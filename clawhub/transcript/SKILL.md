---
name: transcript
description: "Reach for this whenever what was SAID in a YouTube video matters: a pasted link or bare video ID, a summary, quote, translation or fact-check request, notes from a lecture, or research that leans on a specific video. Works even when nobody says the word 'transcript'. Skip it for uploads and account chores."
version: "1.0.0"
user-invocable: true
compatibility: Requires internet access to reach api.transcriptout.com. No additional runtimes or dependencies needed.
required_environment_variables:
  - name: TRANSCRIPTOUT_API_KEY
    prompt: Your TranscriptOut API key (starts with sk_)
    help: Free account at https://transcriptout.com (100 credits on signup, no card). Create the key in the dashboard.
    required_for: all API requests
metadata: {"openclaw":{"emoji":"📝","requires":{"env":["TRANSCRIPTOUT_API_KEY"]},"primaryEnv":"TRANSCRIPTOUT_API_KEY","homepage":"https://transcriptout.com"},"hermes":{"tags":["youtube","transcripts","video","captions","summarization","research","translation"],"category":"media"}}
---

# Transcript

Fetch video transcripts via [TranscriptOut.com](https://transcriptout.com).

## Setup

If `$TRANSCRIPTOUT_API_KEY` is not set, read [references/auth-setup.md](references/auth-setup.md) and follow the instructions there to get and store the key.

## Required Header

Every request needs one header:

- **Authorization:** `Bearer $TRANSCRIPTOUT_API_KEY`

Every response is one JSON envelope. Success: `{"ok": true, "request_id": "...", "data": {...}}`. Error: `{"ok": false, "code": "...", "detail": "...", "request_id": "..."}`. Branch on the machine-readable `code`, not on the human text. The remaining credit balance rides in the `X-Credits-Remaining` response header.

## GET /v1/transcript · 1 credit

Fetch the transcript of any YouTube video.

```bash
curl -s "https://api.transcriptout.com/v1/transcript?video=VIDEO_URL_OR_ID&format=text" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

Accepts full URLs (`youtube.com/watch?v=ID`), short URLs (`youtu.be/ID`), shorts (`youtube.com/shorts/ID`), or bare video IDs.

**Default for agents:** use `format=text` unless you need timestamps. Plain text is the cheapest form to reason over. Use `format=json` to cite or seek to exact moments. Add `video_metadata=true` when the title/channel is also wanted: same call, same 1 credit.

| Param            | Required | Default | Values |
| ---------------- | -------- | ------- | ------ |
| `video`          | yes      | -       | YouTube URL (full/short/shorts) or 11-char video ID |
| `lang`           | no       | `en`    | language code of the track (`en`, `de`, ...) |
| `format`         | no       | `json`  | `json`, `text`, `srt`, `vtt`, `srv3` |
| `kind`           | no       | manual if present | `manual`, `auto` |
| `segment`        | no       | auto tracks: 180 (80 for `srt`/`vtt`). Manual tracks keep the author's lines | 20-5000, max characters per segment |
| `video_metadata` | no       | `false` | `true` adds `data.metadata` (title, channel, duration, views) for the same 1 credit |
| `download`       | no       | `false` | `true` returns the raw file instead of the JSON envelope (`text`/`srt`/`vtt`/`srv3` only) |

`segment` controls the size of the pieces: 500-1500 characters makes chunks with enough context for embeddings and retrieval. Left out, an auto-generated track is cut into ~180-character segments and a manual track is returned exactly as its author broke it.

**Response** for `format=json`. With `format=text`/`srt`/`vtt`/`srv3` the `transcript` field is one string in that format:

```json
{
  "ok": true,
  "request_id": "req_...",
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "language": "en",
    "kind": "manual",
    "transcript": [
      { "text": "Never gonna give you up", "start": 18.0, "duration": 4.12 },
      { "text": "Never gonna let you down", "start": 22.12, "duration": 3.85 }
    ],
    "available_langs": [
      { "code": "en", "kind": "manual", "name": "English" },
      { "code": "en", "kind": "auto", "name": "English (auto-generated)" }
    ]
  }
}
```

## Errors

| Code | Meaning | Action |
| ---- | ------- | ------ |
| 400/422 | Bad parameter | Fix the request. Credit refunded automatically |
| 401 | Bad or missing API key | Check the key. It must start with `sk_` |
| 402 | Out of credits | [transcriptout.com/billing](https://transcriptout.com/billing) |
| 404 | No captions on that language/track, or bad ID | Definitive answer, do not retry. Try another `lang` or `kind=auto`. Billed |
| 410 | Video removed | Do not retry |
| 451 | Age-restricted or members-only | Do not retry |
| 429 | Rate limit (200 req/min per key) | Wait, respect `Retry-After`. Refunded |
| 502 | Failed on YouTube's side | One retry is reasonable. Billed |
| 503 | Service at capacity | Retry after `Retry-After`. Refunded |

Every error body carries a machine-readable `code` and a `request_id`. Include the `request_id` when contacting support.

## Tips

- `format=text` is the cheapest form to reason over. Ask for `json` only when timestamps matter.
- Transcript AND title/channel wanted? One call: `video_metadata=true`. Never a separate `/v1/video` first.
- Transcribe last: search and listings are for choosing, and pulling transcripts for a whole results page nobody asked to read is the fastest way to burn a balance.
