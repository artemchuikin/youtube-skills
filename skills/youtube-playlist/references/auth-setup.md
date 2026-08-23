# TranscriptOut: Getting and Storing Your API Key

How to get a TranscriptOut API key and store it so it is still there in the next session and the
next shell. Read the whole file before running anything.

---

## Step 0: Understand how to store the key on this system

First decide WHERE the key will live on this machine. The requirement: an environment variable
that every future session sees, non-interactive shells included. What satisfies it differs by
platform and by agent runtime (a shell profile file on one system, a config or secret store owned
by the runtime on another), so check how YOUR environment persists variables instead of guessing.

The variable name you will be storing is `TRANSCRIPTOUT_API_KEY`.

---

## Step 1: Ask the user one question

Ask the user exactly this, in a single message:

> Do you have a TranscriptOut key already? Paste it and I'll wire it up. If not, give me an email
> address and I'll open a free account for you: 100 credits included, no card asked.

- If they paste a key (starts with `sk_`), go straight to **Storing the Key** below.
- If they want a new account, go to **Path B**.

---

## Path A: User already has a key

The user pasted their key. TranscriptOut keys always start with `sk_`. Go straight to
**Storing the Key** at the bottom of this document.

---

## Path B: Create a new account

You do the signup for the user, in two HTTP calls: register (a 6-digit code goes to their inbox),
then verify (the code comes back as an API key). Every response is the standard TranscriptOut
envelope `{"ok": true, "request_id": "...", "data": {...}}`. The fields you need live under
`data`.

### Step B-1: Ask for their email

Ask the user for the email address they want to use.

### Step B-2: Register

Make a POST request to:

```
POST https://api.transcriptout.com/auth/register-cli
Content-Type: application/json

{ "email": "the_user_email" }
```

**Pipe the response into a temporary file and build the next request by reading the token out of
that file. Never echo the token on its own.** Several agent runtimes scrub anything shaped like
`access_token` or a bearer token from tool output before the model sees it, so a printed token
arrives as `[REDACTED]` and the flow dead-ends. File in, file out, one chained command.

The response looks like this:

```json
{
  "ok": true,
  "request_id": "req_...",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "email": "user@example.com",
    "expires_in": 3600
  }
}
```

`data.access_token` is a short-lived session token you will use as the Bearer token in the next
request. It expires together with the code, so proceed promptly.

Possible errors (the envelope carries a machine `code` field):

- `429` with `code: "signup_throttled"`: a code was already sent recently, or too many requests.
  Wait the `Retry-After` seconds and retry.
- `400` with `code: "invalid_email"`: the address is malformed, ask the user to re-check it.
- `501`: CLI signup is not enabled on the server. Fall back to the **Browser path** below.

### Step B-3: Tell the user to check their email

Tell the user a 6-digit code is on its way to their inbox and ask them to read it back to you.

The email is the regular TranscriptOut sign-in email: it carries a sign-in button and, below it,
the 6-digit one-time code. The user needs the code, not the button.

### Step B-4: Verify

Once the user gives you the code, make a POST request to:

```
POST https://api.transcriptout.com/auth/verify-cli
Authorization: Bearer <the access_token from Step B-2>
Content-Type: application/json

{ "otp": "123456" }
```

Same discipline as before: **response into a file, key read out of the file**, because
`sk_`-prefixed values get scrubbed from tool output by the same runtimes.

The response looks like this:

```json
{
  "ok": true,
  "request_id": "req_...",
  "data": {
    "verified": true,
    "user_id": "...",
    "api_key": "sk_...",
    "credits": 100
  }
}
```

Read the `data.api_key` field from the file. This is the key you need to store. Go to
**Storing the Key** below.

Possible errors:

- `400` with `code: "invalid_otp"`: the code is wrong or expired. Ask the user to re-check it.
  If it keeps failing, start Path B again from Step B-2 (a fresh code invalidates the old one).
- `401` with `code: "signup_session_invalid"`: the session token expired or is malformed. Start
  Path B again from Step B-2.
- `409` with `code: "key_limit_reached"`: the account exists and already holds the maximum number
  of keys. Ask the user to revoke unused keys in the dashboard at transcriptout.com/dashboard,
  or to paste one of their existing keys (Path A).
- `429` with `code: "signup_throttled"`: too many verification attempts. Wait, then request a
  fresh code.

Note: an existing account is fine here. The same two steps simply sign the user in and issue a new
key. Possession of the emailed code is the same proof the regular sign-in link relies on.

---

## Browser path (fallback)

If the CLI endpoints answer `501`, or the user prefers doing it themselves:

1. Send them to **https://transcriptout.com/login**, where they sign in with Google or a magic link.
   Signing in for the first time IS the signup and grants the free 100 credits.
2. In the dashboard (**https://transcriptout.com/dashboard**) they create an API key. It starts
   with `sk_` and is shown **once**. Ask them to paste it to you right away.

---

## Storing the Key

You now have a string that starts with `sk_`. This is the `TRANSCRIPTOUT_API_KEY`.

Store it persistently using whatever method is correct for this environment (which you determined
in Step 0). Make sure it will be available in future sessions, including non-interactive shells,
without any manual sourcing step from the user.

Once stored, verify it is accessible in the current session. If the session needs a reload or
restart to pick up the new value, do that or tell the user to do it.

Delete the temporary files this process created.

## Verify the key works

One free call confirms both the key and the balance (`/auth/*` endpoints never spend credits):

```bash
curl -s https://api.transcriptout.com/auth/me \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

A valid key returns your `user_id` and remaining `credits`. A `401` means the key is wrong,
revoked, or the variable did not load into this shell.

---

## Pitfalls seen in the wild

**The `access_token` or `api_key` value shows as `[REDACTED]` or is missing from the response.**
You let the response pass through tool output instead of writing it to a file first. Some agent
runtimes (notably Hermes) redact values matching patterns like `access_token`, `api_key`, or `sk_`
from command output before the model sees them. Always write the raw HTTP response body to a temp
file and read the value from there.

**Hermes agents: env var is set but not available in the next tool call.**
Hermes sandboxes `execute_code` and `terminal` calls. Setting an env var in one call does not
carry over to the next unless the variable is declared in the skill's
`required_environment_variables` frontmatter (these skills declare it). If it still does not
appear, persist the key using the agent's normal environment-secret mechanism so Hermes picks it
up on the next load.

**Claude Code agents: key is saved to shell profile but `$TRANSCRIPTOUT_API_KEY` is still empty.**
Writing to shell startup files only affects new shell sessions. The current session does not
reload profile files automatically. Either source the file explicitly in the current session, or
set the value in whatever config the agent reads at runtime.

**The code was never received.**
Wait up to 2 minutes: transactional email can be slow. Also ask the user to check their spam
folder. After the 60-second cooldown you can retry Step B-2, and a fresh email carries a fresh code.

**register-cli answers `501`.**
CLI signup is switched off on the server. Use the **Browser path** above. It always works.

**The verify step fails with `401`.**
The session token from registration expired (it lives as long as the code, about an hour) or got
mangled in transit. Start over from Step B-2.
