---
name: youtube-playlist
description: "Reach for this when a YouTube playlist is in play: a pasted playlist link or PL... id, listing a course or series, finding one video inside a long playlist, or turning a whole playlist into transcripts. Skip it for creating playlists or account chores."
version: "1.0.0"
user-invocable: true
compatibility: Requires internet access to reach api.transcriptout.com. No additional runtimes or dependencies needed.
required_environment_variables:
  - name: TRANSCRIPTOUT_API_KEY
    prompt: Your TranscriptOut API key (starts with sk_)
    help: Free account at https://transcriptout.com (100 credits on signup, no card). Create the key in the dashboard.
    required_for: all API requests
metadata: {"openclaw":{"emoji":"🗂️","requires":{"env":["TRANSCRIPTOUT_API_KEY"]},"primaryEnv":"TRANSCRIPTOUT_API_KEY","homepage":"https://transcriptout.com"},"hermes":{"tags":["youtube","playlists","courses","series","bulk","transcripts"],"category":"media"}}
---

# YouTube Playlist

Browse playlists and fetch transcripts via [TranscriptOut.com](https://transcriptout.com).

## Setup

If `$TRANSCRIPTOUT_API_KEY` is not set, read [references/auth-setup.md](references/auth-setup.md) and follow the instructions there to get and store the key.

## Required Header

Every request needs one header:

- **Authorization:** `Bearer $TRANSCRIPTOUT_API_KEY`

Every response is one JSON envelope. Success: `{"ok": true, "request_id": "...", "data": {...}}`. Error: `{"ok": false, "code": "...", "detail": "...", "request_id": "..."}`. Branch on the machine-readable `code`, not on the human text. The remaining credit balance rides in the `X-Credits-Remaining` response header.

## API Reference

Base URL: `https://api.transcriptout.com/v1`. Full reference with the latest parameters and schemas: [transcriptout.com/docs](https://transcriptout.com/docs).

## GET /v1/playlist/videos · 1 credit/page

Every video of a playlist, in playlist order.

```bash
# First page (100 videos)
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Next pages
curl -s "https://api.transcriptout.com/v1/playlist/videos?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# IDs only, 500 per page (feed these into the bulk job)
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

`id` accepts a `PL...` playlist ID or any URL with `list=`. `limit` goes up to 100, or up to 500 with `ids_only=true`. The response carries `playlist`, `title`, `count`, `videos[]` (or `video_ids[]`), `next_page_token` and `has_more`.

## GET /v1/playlist/search · 1 credit

Find videos inside a playlist by a substring of the title (case-insensitive). YouTube has no native playlist search, so this scans up to 500 playlist items.

```bash
curl -s "https://api.transcriptout.com/v1/playlist/search?id=PL_ID_OR_URL&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

`truncated: true` in the response means the scan window ended before the playlist did, so there may be more matches.

## Workflow: Playlist → Transcripts

For a whole course or series, do not loop single transcript calls: collect the IDs and submit ONE asynchronous job (1 credit per video, up to 4,000).

```bash
# 1. Collect the playlist's IDs
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# 2. One bulk job for every video
curl -s -X POST "https://api.transcriptout.com/v1/transcripts" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"videos":["ID1","ID2","..."],"format":"text"}'

# 3. Progress and results
curl -s "https://api.transcriptout.com/v1/transcripts/JOB_ID" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

## Extract a playlist reference from a URL

No extraction needed: `id` accepts the full URL as pasted (`youtube.com/playlist?list=PL...`, or a watch URL with `list=`). A bare `PL...` ID works too.

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
