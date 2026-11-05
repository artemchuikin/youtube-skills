# TranscriptOut: Getting and Storing Your API Key

How to get a TranscriptOut API key and store it so it is still there in the next session and the
next shell. Read the whole file before running anything.

---

## Rules for handling the key

The key (`sk_...`) spends the user's credits. Treat it, the short-lived sign-up token and the
emailed code as secrets.

- **Never print them.** Not in chat, not in tool output, not in logs. The commands below keep them
  inside files and shell variables and print only a status line.
- **If a value shows up as `[REDACTED]`, the runtime is protecting it on purpose.** Do not try to
  recover it or route around the redaction. Nothing in this guide needs a secret printed.
- **Never repeat the key back to the user**, and never write it into a project directory, a git
  repository or a shell profile.
- **Send it only to `api.transcriptout.com`.** No other host, tool or service has any use for it.

---

## Step 0: Find out how this runtime stores secrets

The skill needs `TRANSCRIPTOUT_API_KEY` in the environment of every future session. Check, in
this order:

1. **The runtime has its own secret prompt.** Hermes and OpenClaw read
   `required_environment_variables` from the skill frontmatter and can ask the user for the value
   in their own interface. If yours does, use it: the user types the key there, never in chat.
2. **No secret prompt.** Keep the key in a file only the user can read,
   `~/.config/transcriptout/key` (folder mode 700, file mode 600), and load it from there. The
   shell profile then carries a line that reads the file, never the key itself.

The variable name is always `TRANSCRIPTOUT_API_KEY`.

---

## Step 1: Ask the user one question

Ask the user exactly this, in a single message:

> Do you already have a TranscriptOut key? If so, I'll show you where to put it so it never has
> to go through this chat. If not, give me an email address and I'll open a free account for
> you: 100 credits included, no card asked.

- They have a key: go to **Path A**.
- They want a new account: go to **Path B**.

---

## Path A: User already has a key (preferred)

The key should reach its storage without passing through the conversation.

- **Runtime with a secret prompt:** ask the user to enter it there under `TRANSCRIPTOUT_API_KEY`.
- **Otherwise:** ask the user to run this in their own terminal. It reads the key without echoing
  it and writes the private file:

```bash
mkdir -p ~/.config/transcriptout && chmod 700 ~/.config/transcriptout && (umask 077; printf 'TranscriptOut key: '; stty -echo; IFS= read -r k; stty echo; echo; printf '%s' "$k" > ~/.config/transcriptout/key)
```

Then continue with **Load the key** below.

If the user pastes the key into the chat anyway, store it with the same file method, do not repeat
it, and mention once that it now sits in the chat history: they can create a fresh key and delete
this one in the dashboard at https://transcriptout.com/dashboard?utm_source=youtube-skills&utm_medium=clawhub&utm_content=youtube-data if that matters to them.

---

## Path B: Create a new account

You do the signup for the user, in two HTTP calls: register (a 6-digit code goes to their inbox),
then verify (the code comes back as an API key). Every response is the standard TranscriptOut
envelope `{"ok": true, "request_id": "...", "data": {...}}`.

Both secrets this produces, the sign-up token and the key, go straight from the response into a
private file and are never printed. Shell variables do not survive between tool calls in many
runtimes, so the token waits in a file for the second step and is deleted after it.

### Step B-1: Ask for their email

Ask the user for the email address they want to use.

### Step B-2: Register

Run this as one command, with the user's address in place of `USER_EMAIL`:

```bash
mkdir -p ~/.config/transcriptout && chmod 700 ~/.config/transcriptout && (umask 077; curl -s -X POST https://api.transcriptout.com/auth/register-cli -H "Content-Type: application/json" -H "X-Client: youtube-skills-clawhub/youtube-data" -d '{"email":"USER_EMAIL","source":"youtube-skills-clawhub/youtube-data"}' -o ~/.config/transcriptout/signup.json); grep -o '"ok":[a-z]*\|"code":"[^"]*"' ~/.config/transcriptout/signup.json
```

It prints only `"ok":true`, or `"ok":false` with an error `code`. The response itself holds
`data.access_token`, a short-lived token for the next step, and stays in the file.

Possible errors:

- `signup_throttled`: a code was already sent recently, or too many requests. Wait a minute and
  retry.
- `invalid_email`: the address is malformed, ask the user to re-check it.
- HTTP `501`: CLI signup is not enabled on the server. Use the **Browser path** below.

### Step B-3: Ask for the code

Tell the user a 6-digit code is on its way to their inbox and ask them to give it to you.

The email is the regular TranscriptOut sign-in email: a sign-in button and, below it, the 6-digit
code. The user needs the code, not the button. Tell them it is single use and only good for this
one step. Use it once in the next command, and do not repeat it or write it anywhere else.

### Step B-4: Verify and store the key

Run this as one command, with the code in place of `CODE`:

```bash
d=~/.config/transcriptout; t=$(sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p' "$d/signup.json"); (umask 077; curl -s -X POST https://api.transcriptout.com/auth/verify-cli -H "Authorization: Bearer $t" -H "Content-Type: application/json" -H "X-Client: youtube-skills-clawhub/youtube-data" -d '{"otp":"CODE","source":"youtube-skills-clawhub/youtube-data"}' -o "$d/verify.json"); k=$(sed -n 's/.*"api_key":"\([^"]*\)".*/\1/p' "$d/verify.json"); if [ -n "$k" ]; then (umask 077; printf '%s' "$k" > "$d/key"); rm -f "$d/signup.json"; echo stored; fi; grep -o '"code":"[^"]*"\|"credits":[0-9]*' "$d/verify.json"; rm -f "$d/verify.json"
```

It prints `stored` and the credit balance on success, or an error `code`. The key goes from the
response into `~/.config/transcriptout/key` without being printed. Continue with **Load the key**.

Possible errors:

- `invalid_otp`: the code is wrong or expired. Ask the user to re-check it. If it keeps failing,
  start again from Step B-2 (a fresh code invalidates the old one).
- `signup_session_invalid`: the sign-up token expired. Start again from Step B-2.
- `key_limit_reached`: the account already holds the maximum number of keys. Ask the user to
  delete unused keys in the dashboard at https://transcriptout.com/dashboard?utm_source=youtube-skills&utm_medium=clawhub&utm_content=youtube-data, then retry, or use
  **Path A** with one of their existing keys.
- `signup_throttled`: too many verification attempts. Wait, then request a fresh code.

Note: an existing account is fine here. The same two steps sign the user in and issue a new key.
Possession of the emailed code is the same proof the regular sign-in link relies on.

---

## Browser path (fallback)

If the CLI endpoints answer `501`, or the user prefers doing it themselves:

1. Send them to **https://transcriptout.com/login?utm_source=youtube-skills&utm_medium=clawhub&utm_content=youtube-data**, where they sign in with Google or a magic link.
   Signing in for the first time IS the signup and grants the free 100 credits.
2. In the dashboard (**https://transcriptout.com/dashboard?utm_source=youtube-skills&utm_medium=clawhub&utm_content=youtube-data**) they create an API key. It starts
   with `sk_` and is shown **once**.
3. Continue with **Path A**, so the key goes into storage rather than into the chat.

---

## Load the key

Skip this if the runtime's own secret prompt holds the key.

Otherwise make every new shell read the file. Add this one line to the shell profile this system
uses (for example `~/.zshenv` on macOS, `~/.profile` or `~/.bashrc` on Linux). The line holds a
path, not the key:

```bash
export TRANSCRIPTOUT_API_KEY="$(cat ~/.config/transcriptout/key 2>/dev/null)"
```

In the current session, run the same line once so the variable is set now. If the runtime does not
read shell profiles, set `TRANSCRIPTOUT_API_KEY` through its own configuration, still pointing at
the file where it can.

## Verify the key works

One free call confirms both the key and the balance (`/auth/*` endpoints never spend credits). It
prints the account id and the credits, never the key:

```bash
curl -s https://api.transcriptout.com/auth/me \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills-clawhub/youtube-data"
```

A `401` means the key is wrong, revoked, or the variable did not load into this shell.

---

## Pitfalls seen in the wild

**A value shows as `[REDACTED]`.**
The runtime is hiding a secret, as it should. The commands above never need one printed: they read
values from files inside the same command. If a step still dead-ends, start that step again rather
than trying to reveal the value.

**Hermes agents: env var is set but not available in the next tool call.**
Hermes sandboxes `execute_code` and `terminal` calls. A variable set in one call does not carry
over to the next unless it is declared in the skill's `required_environment_variables` frontmatter
(these skills declare it). Let Hermes prompt the user for it and keep it in its own secret store.

**Claude Code agents: the profile line is in place but `$TRANSCRIPTOUT_API_KEY` is still empty.**
Profile files only affect new shells. Run the `export` line once in the current session, or set the
variable in whatever configuration the agent reads at start.

**The code was never received.**
Wait up to 2 minutes: transactional email can be slow. Also ask the user to check their spam
folder. After the 60-second cooldown you can retry Step B-2, and a fresh email carries a fresh code.

**register-cli answers `501`.**
CLI signup is switched off on the server. Use the **Browser path** above. It always works.

**The verify step fails with `signup_session_invalid`.**
The sign-up token from registration expired (it lives as long as the code, about an hour). Start
over from Step B-2.
