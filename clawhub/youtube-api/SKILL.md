---
name: youtube-api
description: "Reach for this when YouTube data is needed and Google's Data API is the obstacle: no quota units, no OAuth consent screens, one Bearer key. Covers transcripts (which Google's API does not serve at all), metadata, search, channels and playlists. Triggers on YouTube links, @handles and creator research. Skip it for uploads and account chores."
version: "1.0.0"
user-invocable: true
compatibility: Requires internet access to reach api.transcriptout.com. No additional runtimes or dependencies needed.
required_environment_variables:
  - name: TRANSCRIPTOUT_API_KEY
    prompt: Your TranscriptOut API key (starts with sk_)
    help: Free account at https://transcriptout.com (100 credits on signup, no card). Create the key in the dashboard.
    required_for: all API requests
metadata: {"openclaw":{"emoji":"🧰","requires":{"env":["TRANSCRIPTOUT_API_KEY"]},"primaryEnv":"TRANSCRIPTOUT_API_KEY","homepage":"https://transcriptout.com"},"hermes":{"tags":["youtube","api","rest","transcripts","search","no-quota"],"category":"media"}}
---

# YouTube API

YouTube API access via [TranscriptOut.com](https://transcriptout.com): no Google quota needed.

## Setup

If `$TRANSCRIPTOUT_API_KEY` is not set, read [references/auth-setup.md](references/auth-setup.md) and follow the instructions there to get and store the key.

## Required Header

Every request needs one header:

- **Authorization:** `Bearer $TRANSCRIPTOUT_API_KEY`

Every response is one JSON envelope. Success: `{"ok": true, "request_id": "...", "data": {...}}`. Error: `{"ok": false, "code": "...", "detail": "...", "request_id": "..."}`. Branch on the machine-readable `code`, not on the human text. The remaining credit balance rides in the `X-Credits-Remaining` response header.

## API Reference

Base URL: `https://api.transcriptout.com/v1`. Full reference with the latest parameters and schemas: [transcriptout.com/docs](https://transcriptout.com/docs).

## Endpoint Reference

| Endpoint | What it returns | Cost |
| -------- | --------------- | ---- |
| `GET /v1/transcript` | transcript of one video (`json`/`text`/`srt`/`vtt`/`srv3`) | 1 |
| `GET /v1/video` | title, channel, duration, views + available caption languages | 1 |
| `GET /v1/search` | YouTube search, videos or channels | 1/page |
| `GET /v1/channel/latest` | ~15 newest uploads of a channel | 1 |
| `GET /v1/channel/videos` | full upload history, paginated | 1/page |
| `GET /v1/channel/search` | native relevance search inside a channel | 1/page |
| `GET /v1/playlist/videos` | playlist contents, paginated | 1/page |
| `GET /v1/playlist/search` | title-substring search inside a playlist | 1 |
| `POST /v1/transcripts` | asynchronous bulk job, up to 4,000 videos | 1 per video |
| `GET /v1/transcripts/{id}` + `/results` | job progress and results | free |


## Quick Examples

```bash
# A transcript with metadata
curl -s "https://api.transcriptout.com/v1/transcript?video=dQw4w9WgXcQ&format=text&video_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Search
curl -s "https://api.transcriptout.com/v1/search?q=rust+lifetimes&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# A channel's uploads
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# A playlist
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PLAYLIST_URL" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

## Why Not Google's API?

- The YouTube Data API does not return transcripts at all. TranscriptOut's core endpoint does.
- No Google Cloud project, no OAuth consent screens, no daily quota units: one Bearer key.
- Channel and playlist listings cost 1 credit per page instead of burning quota per item.
- Search, in-channel search and playlist search come from the same base URL with the same key.

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
