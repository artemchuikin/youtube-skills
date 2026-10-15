# YouTube Skills for AI Agents 🎬

> Drop-in skills that let a coding or chat agent pull YouTube transcripts, run searches, walk
> channels and export whole playlists.

An [Agent Skill](https://skills.sh) is a folder of instructions an agent loads when the task
matches. The 12 skills in this repo cover YouTube end to end. Each one names its endpoint, shows
the exact request, lists every parameter with defaults and limits, and maps every error code to a
recovery, so the agent makes the right call on the first try instead of guessing. No yt-dlp, no
headless browser, no Google Cloud project. One HTTPS request per answer.

Works with Claude Code, Cursor, Antigravity, Cline, Codex, OpenClaw, Hermes Agent, and anything
else that reads the Agent Skills format.

Made by [TranscriptOut](https://transcriptout.com/?utm_source=youtube-skills&utm_medium=readme) · [API docs](https://transcriptout.com/docs?utm_source=youtube-skills&utm_medium=readme) · [MCP server](https://github.com/artemchuikin/youtube-mcp)

---

## ⚡ Quick start

```bash
npx skills add artemchuikin/youtube-skills --skill youtube-full
```

Then ask the agent something it previously had to refuse.

```txt
What does this talk actually claim? https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

The first run also takes care of the API key, without leaving the chat. The agent asks for your
email, a 6-digit code arrives in your inbox, you read it back, and a fresh `sk_` key lands in your
shell or agent config. The account behind it is free, starts with 100 credits and never asks for a
card.

<details>
<summary><strong>Other install paths</strong></summary>

**Hermes Agent**

```bash
hermes skills install skills-sh/artemchuikin/youtube-skills/skills/youtube-full
```

**All 12 skills at once**

```bash
npx skills add artemchuikin/youtube-skills
```

**Manual (git clone)**

```bash
git clone https://github.com/artemchuikin/youtube-skills.git
cp -r youtube-skills/skills/youtube-full ~/.claude/skills/
```

**OpenClaw (ClawdBot/Moltbot).** Copy a folder from `clawhub/` into your skills directory. The
`clawhub/` tree carries the same 12 skills with bash-style examples.

**No terminal at all.** Paste this into the agent and let it do the work.

```txt
Install the youtube skills from this GitHub repo: https://github.com/artemchuikin/youtube-skills
I want to get YouTube transcripts, search YouTube, and browse channel videos from my agent.
Set everything up for me.
```

Installing skills and creating the API key are both things these skills teach the agent to do.

</details>

---

## 💬 What you can ask

Every row is something you can say to the agent word for word. The skill turns it into the
right API call.

| Ask for | For example |
|---------|-------------|
| **A transcript** | "What does this video actually say? [URL]" |
| **A summary or quote** | "Pull the three strongest quotes from this talk" |
| **Subtitles as files** | "Export this video's subtitles as SRT" |
| **A YouTube search** | "Find recent talks about Rust async and pick the best three" |
| **A channel's news** | "Anything new on @kurzgesagt this week?" |
| **A channel's catalogue** | "List everything @3blue1brown has ever uploaded" |
| **Search inside a channel** | "Find every Fireship video that mentions Postgres" |
| **A whole playlist** | "Turn this lecture course into study notes" |
| **A bulk export** | "Queue transcripts for all 800 videos on this channel" |
| **RAG-ready chunks** | "Fetch this playlist's transcripts in ~1000-character segments for my index" |

---

## 🧰 Which skill to install

`youtube-full` is the right answer for most people. One skill, the whole surface. The narrower
ones exist because a skill is context the agent has to carry, and a workflow that only ever needs
transcripts should not pay for playlist documentation.

| Skill | What it does | Install |
|-------|--------------|---------|
| **youtube-full** | Everything. Transcripts, search, channels, playlists, bulk jobs | `--skill youtube-full` |
| **transcript** | Video transcripts with timestamps | `--skill transcript` |
| **youtube-search** | Search YouTube for videos and channels | `--skill youtube-search` |
| **youtube-channels** | Uploads, latest videos, search within a channel | `--skill youtube-channels` |
| **youtube-playlist** | Every video of a playlist | `--skill youtube-playlist` |

```bash
# one skill
npx skills add artemchuikin/youtube-skills --skill transcript

# several at once
npx skills add artemchuikin/youtube-skills --skill transcript --skill youtube-search
```

<details>
<summary><strong>All 12 skills</strong></summary>

Beyond the core five, the rest are vocabulary variants of the same capabilities. People say
"captions", "subtitles", "video to text" or "youtube api" for overlapping things, and an agent
picks a skill by matching your words against skill descriptions, so each phrasing has a skill that
answers to it.

| Skill | Description |
|-------|-------------|
| **youtube-full** | Complete toolkit. Transcripts + search + channels + playlists + bulk jobs |
| **transcript** | Extract the transcript of any YouTube video, with timestamps |
| **captions** | Closed captions / CC, including SRT and VTT files |
| **subtitles** | Subtitles from YouTube videos, including SRT and VTT files |
| **youtube-search** | Search YouTube for videos and channels |
| **youtube-channels** | Channel uploads, latest videos, in-channel search |
| **youtube-playlist** | All videos of a YouTube playlist |
| **youtube-data** | Video and channel data without Google's API quotas |
| **youtube-api** | YouTube API access for agents, no Google Cloud project |
| **transcriptout** | The full API surface in one skill |
| **video-transcript** | Convert YouTube videos to text |
| **yt** | Quick lookups. Transcript, search, channel latest |

</details>

---

## 💳 What calls cost

The unit is a credit, and one credit is one answered request.

| Request | Cost |
|---------|------|
| transcript of one video (any of 5 formats) | 1 |
| video metadata + available caption languages | 1 |
| YouTube search | 1 per page |
| channel latest (~15 newest videos) | 1 |
| channel videos | 1 per page (100 videos, or 500 IDs) |
| search within a channel | 1 per page |
| playlist videos | 1 per page (100 videos, or 500 IDs) |
| search within a playlist | 1 |
| bulk job submit | 1 per video |
| bulk job progress, results, cancel | free |

A call that dies before reaching YouTube (bad parameter, rate limit, service busy) refunds itself
automatically. A confirmed "this video has no captions" costs the credit, because the lookup
really happened. The rate limit is 200 requests per minute per key on every plan.

| Plan | Price | Credits | 
|------|-------|---------|
| **Free** | $0 | 100 on signup, one-time |
| **Starter** | $4.49/month | 1,000/month |
| **Starter Annual** | $45.29/year (~$3.77/mo) | 1,000/month |
| **Scale** | slider up to $198.99/mo | up to 100,000/month |

Subscription volume is a slider from 1,000 to 100,000 credits per month in steps of 1,000, and the
per-1,000 rate falls as the volume grows. [Full pricing →](https://transcriptout.com/?utm_source=youtube-skills&utm_medium=readme#pricing)

---

## 📦 Built for bulk work

Bulk export is one job, not a loop. The agent collects video IDs cheaply (`ids_only=true` returns
up to 500 per page), submits them all in a single `POST /v1/transcripts` (up to 4,000 videos), and
reads results page by page while the job is still running. Duplicates are dropped before billing,
an `Idempotency-Key` makes retries free, the job paces itself inside the rate limit instead of
tripping 429s, and any video the service fails to deliver is refunded on its own. A full channel
archive that used to be an evening of scripting is three prompts.

## 🧠 Chunks sized for retrieval

Transcripts arrive pre-chunked if you ask. The `segment` parameter (20 to 5,000 characters)
controls how the text is cut, and 500 to 1,500 gives retrieval-sized pieces with real context. Cut
points come from per-word timestamps in YouTube's raw srv3 data, so each chunk's `start` is the
moment the words are actually spoken rather than an interpolation. `segment=1000&format=json` goes
straight into an embedding pipeline with no re-chunking step.

---

## 🔑 Setting up the key by hand

The in-chat flow above is optional. The manual way takes two minutes.

1. Sign in at [transcriptout.com](https://transcriptout.com/?utm_source=youtube-skills&utm_medium=readme) with Google or a magic link. The
   first sign-in is the signup and grants the free credits.
2. Create an API key in the [dashboard](https://transcriptout.com/dashboard?utm_source=youtube-skills&utm_medium=readme). It starts with `sk_`
   and is shown once.
3. Export it where the agent can see it.

```bash
export TRANSCRIPTOUT_API_KEY="sk_your_key_here"
```

Or hand it to the agent and let it persist the value.

> "My TranscriptOut key is `sk_...`, store it so it persists across sessions."

<details>
<summary><strong>Where does the key get saved?</strong></summary>

The storage location depends on which runtime the agent lives in.

| Location | File |
|----------|------|
| **OpenClaw/Moltbot** | `~/.openclaw/openclaw.json` or `~/.clawdbot/moltbot.json` |
| **Hermes Agent** | Hermes secret store (`TRANSCRIPTOUT_API_KEY` declared via `required_environment_variables` in skill frontmatter) |
| **macOS shell** | `~/.zshenv`, `~/.zprofile` |
| **Linux shell** | `~/.profile`, `~/.bashrc`, `~/.zshenv` |
| **Fish shell** | `~/.config/fish/config.fish` |
| **Fallback** | `~/.transcriptout` (mode 600) |

The agent picks it up automatically after saving.

</details>

---

## ❓ FAQ

### Can I bulk download YouTube transcripts?

Yes, and there is a purpose-built endpoint for it. Install `youtube-full` and ask for transcripts
of a playlist or channel. The agent gathers the IDs and submits one batch job for up to 4,000
videos, then reads results as they land. Same price per video as single calls.

### Do I need a Google YouTube Data API key?

No. These skills replace the Data API for transcripts, search, and channel and playlist listings,
without a Google Cloud project, quota units or OAuth screens. Google's API also does not return
transcripts, which tends to be the whole point.

### Do I need an API key at all?

Yes, but getting one is part of the first run. The agent registers your email, you read a 6-digit
code off your inbox, and the key is stored for you. 100 free credits, no card.

### Which skill should I install?

`youtube-full`, unless you know you want less. The narrow ones are listed under
[Which skill to install](#-which-skill-to-install).

### What API is underneath?

[TranscriptOut](https://transcriptout.com/?utm_source=youtube-skills&utm_medium=readme), a hosted YouTube data API. The full reference lives at
[transcriptout.com/docs](https://transcriptout.com/docs?utm_source=youtube-skills&utm_medium=readme), and the same backend is available as a
remote [MCP server](https://github.com/artemchuikin/youtube-mcp) if your client speaks MCP
natively.
For code outside an agent there are client libraries,
[`pip install transcriptout`](https://github.com/artemchuikin/youtube-transcript-python) and
[`npm i transcriptout`](https://github.com/artemchuikin/youtube-transcript-js), drop-in
replacements for youtube-transcript-api and youtube-transcript.

### Live streams?

Transcripts appear after a stream ends and captions are processed, not while it runs.

---

## 🧯 Troubleshooting

Every error response carries a machine-readable `code` and a `request_id`, and agents tend to
relay them word for word, so this table is keyed by what you will actually see.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `401 Unauthorized` | Key missing, mistyped, or not loaded into the environment | Confirm `TRANSCRIPTOUT_API_KEY` is set in the shell the agent runs in and starts with `sk_` |
| `402 Payment Required` | The account is out of credits | Check the balance at [transcriptout.com/billing](https://transcriptout.com/billing?utm_source=youtube-skills&utm_medium=readme) |
| `404 Not Found` | No captions on the requested language or track, or a wrong ID | A definitive answer, retrying won't change it. Try another `lang`, or `kind=auto` |
| `410 Gone` | The video was removed | Nothing to fetch |
| `451` | Age-restricted or members-only video | Nothing to fetch without an account, which the API deliberately does not use |
| `422 / 400` | A malformed parameter | Channels accept `@handle`, a name, a URL or a `UC` ID. Playlists take a `PL...` ID or URL. The credit refunds itself |
| `429 Too Many Requests` | Rate limit reached (200 req/min per key) | Wait out the `Retry-After` header. The credit refunds itself |
| `503` | Temporary capacity pressure on cold fetches | Retry after `Retry-After`. The credit refunds itself |

And three situations that are not errors at all.

- **The key is saved but the agent cannot see it.** Shell profiles only load into new shells, and
  the session that wrote the key does not reread its own profile. Restart the agent, or check that
  the file written matches the shell the agent actually runs (see the table above).
- **The transcript came back in an unexpected language.** Many videos only carry captions in their
  original language. Ask for `lang=<code>` explicitly, or let the agent translate. The metadata
  endpoint lists which languages a video actually has.
- **A fresh upload has no transcript yet.** Captions take YouTube some time to process after
  publishing. Come back in a while.

---

## 🗂️ Repository layout

```text
skills/     the 12 skills with HTTP-style examples (Claude Code, Cursor, Codex, Hermes, ...)
clawhub/    the same 12 with bash examples, for OpenClaw
scripts/    generate.py, the single source every skill file is emitted from
assets/     icons
```

The skill files are generated. Edit `scripts/generate.py` and re-run it rather than touching
`skills/` or `clawhub/` by hand. The endpoints and error tables stay consistent across all 12
because they come from one section library.

## 🤝 Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT. These skills call the TranscriptOut API, an independent product that is not affiliated with
or endorsed by YouTube or Google.
