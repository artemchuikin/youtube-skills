---
name: youtube-playlist
description: "Reach for this when a YouTube playlist is in play: a pasted playlist link or PL... id, listing a course or series, finding one video inside a long playlist, or turning a whole playlist into transcripts. Skip it for creating playlists or account chores."
version: "1.1.0"
user-invocable: true
compatibility: Requires internet access to reach api.transcriptout.com. No additional runtimes or dependencies needed.
required_environment_variables:
  - name: TRANSCRIPTOUT_API_KEY
    prompt: Your TranscriptOut API key (starts with sk_)
    help: Free account at https://transcriptout.com/?utm_source=youtube-skills&utm_medium=skill&utm_content=youtube-playlist (100 credits on signup, no card). Create the key in the dashboard.
    required_for: all API requests
metadata: {"openclaw":{"emoji":"🗂️","requires":{"env":["TRANSCRIPTOUT_API_KEY"]},"primaryEnv":"TRANSCRIPTOUT_API_KEY","homepage":"https://transcriptout.com"},"hermes":{"tags":["youtube","playlists","courses","series","bulk","transcripts"],"category":"media"}}
---

# YouTube Playlist

Browse playlists and fetch transcripts via [TranscriptOut.com](https://transcriptout.com/?utm_source=youtube-skills&utm_medium=skill&utm_content=youtube-playlist).

## Setup

If `$TRANSCRIPTOUT_API_KEY` is not set, read [references/auth-setup.md](references/auth-setup.md) and follow the instructions there to get and store the key.

## Required Header

Every request carries these headers:

- **Authorization:** `Bearer $TRANSCRIPTOUT_API_KEY`
- **X-Client:** `youtube-skills/youtube-playlist`, so TranscriptOut knows the call came from this skill

Every response is one JSON envelope. Success: `{"ok": true, "request_id": "...", "data": {...}}`. Error: `{"ok": false, "code": "...", "detail": "...", "request_id": "..."}`. Branch on the machine-readable `code`, not on the human text. The remaining credit balance rides in the `X-Credits-Remaining` response header.

## API Reference

Base URL: `https://api.transcriptout.com/v1`. Full reference with the latest parameters and schemas: [transcriptout.com/docs](https://transcriptout.com/docs?utm_source=youtube-skills&utm_medium=skill&utm_content=youtube-playlist).

## GET /v1/playlist/videos · 1 credit/page

Every video of a playlist, in playlist order.

```http
# First page (100 videos)
GET https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL
Authorization: Bearer $TRANSCRIPTOUT_API_KEY
X-Client: youtube-skills/youtube-playlist

# Next pages
GET https://api.transcriptout.com/v1/playlist/videos?next_page_token=TOKEN
Authorization: Bearer $TRANSCRIPTOUT_API_KEY
X-Client: youtube-skills/youtube-playlist

# IDs only, 500 per page (feed these into the bulk job)
GET https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL&ids_only=true
Authorization: Bearer $TRANSCRIPTOUT_API_KEY
X-Client: youtube-skills/youtube-playlist
```

`id` accepts a `PL...` playlist ID or any URL with `list=`. `limit` goes up to 100, or up to 500 with `ids_only=true`. The response carries `playlist`, `title`, `count`, `videos[]` (or `video_ids[]`), `next_page_token` and `has_more`.

## GET /v1/playlist/search · 1 credit

Find videos inside a playlist by a substring of the title (case-insensitive). YouTube has no native playlist search, so this scans up to 500 playlist items.

```http
GET https://api.transcriptout.com/v1/playlist/search?id=PL_ID_OR_URL&q=QUERY&limit=30
Authorization: Bearer $TRANSCRIPTOUT_API_KEY
X-Client: youtube-skills/youtube-playlist
```

`truncated: true` in the response means the scan window ended before the playlist did, so there may be more matches.

## Workflow: Playlist → Transcripts

For a whole course or series, do not loop single transcript calls: collect the IDs and submit ONE asynchronous job (1 credit per video, up to 4,000).

```http
# 1. Collect the playlist's IDs
GET https://api.transcriptout.com/v1/playlist/videos?id=PL_ID&ids_only=true
Authorization: Bearer $TRANSCRIPTOUT_API_KEY
X-Client: youtube-skills/youtube-playlist

# 2. One bulk job for every video
POST https://api.transcriptout.com/v1/transcripts
Authorization: Bearer $TRANSCRIPTOUT_API_KEY
X-Client: youtube-skills/youtube-playlist
Content-Type: application/json

{"videos":["ID1","ID2","..."],"format":"text"}

# 3. Progress and results
GET https://api.transcriptout.com/v1/transcripts/JOB_ID
Authorization: Bearer $TRANSCRIPTOUT_API_KEY
X-Client: youtube-skills/youtube-playlist
```

## Extract a playlist reference from a URL

No extraction needed: `id` accepts the full URL as pasted (`youtube.com/playlist?list=PL...`, or a watch URL with `list=`). A bare `PL...` ID works too.

## Errors

| Code | Meaning | Action |
| ---- | ------- | ------ |
| 400/422 | Bad parameter | Fix the request. Credit refunded automatically |
| 401 | Bad or missing API key | Check the key. It must start with `sk_` |
| 402 | Out of credits | [transcriptout.com/billing](https://transcriptout.com/billing?utm_source=youtube-skills&utm_medium=skill&utm_content=youtube-playlist) |
| 404 | No captions on that language/track, or bad ID | Definitive answer, do not retry. Try another `lang` or `kind=auto`. Billed |
| 410 | Video removed | Do not retry |
| 451 | Age-restricted or members-only | Do not retry |
| 429 | Rate limit (200 req/min per key) | Wait, respect `Retry-After`. Refunded |
| 502 | Failed on YouTube's side | One retry is reasonable. Billed |
| 503 | Service at capacity | Retry after `Retry-After`. Refunded |

Every error body carries a machine-readable `code` and a `request_id`. Include the `request_id` when contacting support.

## Copy-paste examples

Every request in this file as a ready-to-run one-liner: [references/curl-examples.md](references/curl-examples.md)
