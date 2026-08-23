---
name: transcriptout
description: "Reach for this whenever a task touches YouTube, said or unsaid: pasted video/channel/playlist links, IDs and @handles, summaries, quotes, translations, topic research through talks and tutorials, creator monitoring. The full TranscriptOut surface: transcripts in five formats, search, channels, playlists and batch jobs. Skip it for uploads and account chores."
version: "1.0.0"
user-invocable: true
compatibility: Requires internet access to reach api.transcriptout.com. No additional runtimes or dependencies needed.
required_environment_variables:
  - name: TRANSCRIPTOUT_API_KEY
    prompt: Your TranscriptOut API key (starts with sk_)
    help: Free account at https://transcriptout.com (100 credits on signup, no card). Create the key in the dashboard.
    required_for: all API requests
metadata: {"openclaw":{"emoji":"🚀","requires":{"env":["TRANSCRIPTOUT_API_KEY"]},"primaryEnv":"TRANSCRIPTOUT_API_KEY","homepage":"https://transcriptout.com"},"hermes":{"tags":["youtube","transcripts","video","search","channels","playlists","captions"],"category":"media"}}
---

# TranscriptOut

Full YouTube data toolkit via [TranscriptOut.com](https://transcriptout.com). Transcripts, search, channels, playlists, bulk jobs: one API key.

## Setup

If `$TRANSCRIPTOUT_API_KEY` is not set, read [references/auth-setup.md](references/auth-setup.md) and follow the instructions there to get and store the key.

## Required Header

Every request needs one header:

- **Authorization:** `Bearer $TRANSCRIPTOUT_API_KEY`

Every response is one JSON envelope. Success: `{"ok": true, "request_id": "...", "data": {...}}`. Error: `{"ok": false, "code": "...", "detail": "...", "request_id": "..."}`. Branch on the machine-readable `code`, not on the human text. The remaining credit balance rides in the `X-Credits-Remaining` response header.

## API Reference

Base URL: `https://api.transcriptout.com/v1`. Full reference with the latest parameters and schemas: [transcriptout.com/docs](https://transcriptout.com/docs).

## Transcript · 1 credit

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

## GET /v1/video · 1 credit

Metadata for one video (title, channel, duration, views, thumbnails) plus the list of available transcript languages, WITHOUT downloading the subtitles.

```bash
curl -s "https://api.transcriptout.com/v1/video?id=VIDEO_URL_OR_ID" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

**Credit hygiene:** if the transcript is wanted anyway, call `/v1/transcript` with `video_metadata=true` instead. One call and one credit against two.

## GET /v1/search · 1 credit/page

Search YouTube for videos or channels.

```bash
# Videos
curl -s "https://api.transcriptout.com/v1/search?q=QUERY&type=video&limit=20" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Channels
curl -s "https://api.transcriptout.com/v1/search?q=QUERY&type=channel&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Next page
curl -s "https://api.transcriptout.com/v1/search?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

| Param             | Required | Default | Validation |
| ----------------- | -------- | ------- | ---------- |
| `q`               | yes*     | -       | the query (*or pass `next_page_token`) |
| `type`            | no       | `video` | `video`, `channel` |
| `limit`           | no       | `20`    | 1-50 |
| `next_page_token` | no       | -       | token from a previous page |

The response carries `next_page_token` and `has_more`. Video entries have `video_id`, `title`, `channel`, `duration` (`"M:SS"`), `view_count`, `published`, `url`, `thumbnails`.

## GET /v1/channel/latest · 1 credit

The ~15 most recent videos of a channel, served from its RSS feed: the fastest and cheapest way to check what a creator published recently.

```bash
curl -s "https://api.transcriptout.com/v1/channel/latest?name=@kurzgesagt" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

`name` accepts an `@handle`, a channel name, a `UC...` channel ID or a channel URL. No resolve step needed: pass the handle directly.

## GET /v1/channel/videos · 1 credit/page

Every video from a channel's Videos tab, newest first.

```bash
# First page (100 videos)
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Next pages
curl -s "https://api.transcriptout.com/v1/channel/videos?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# IDs only, 500 per page (feed these into the bulk job)
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

Provide `name` on the first call and only `next_page_token` afterwards. `limit` goes up to 100, or up to 500 with `ids_only=true` (the response is then `video_ids[]` instead of full video objects). The response carries `next_page_token` and `has_more`.

## GET /v1/channel/search · 1 credit/page

Search inside one channel using YouTube's native relevance search. A result whose title lacks the query word is normal: it is relevance, not substring match.

```bash
curl -s "https://api.transcriptout.com/v1/channel/search?name=@kurzgesagt&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

| Param             | Required | Default | Validation |
| ----------------- | -------- | ------- | ---------- |
| `name`            | yes*     | -       | `@handle`, channel name, `UC...` ID or URL (*or `next_page_token`) |
| `q`               | yes*     | -       | query to search within the channel |
| `limit`           | no       | `30`    | 1-100 |
| `next_page_token` | no       | -       | token from a previous page |

Cheaper and better-ranked than downloading the catalogue and grepping it.

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

## Bulk transcripts: POST /v1/transcripts · 1 credit per video

One asynchronous job for up to 4,000 videos. Use it instead of looping over `/v1/transcript` for more than a handful of videos: same price per video, same options (`lang`, `format`, `kind`, `segment`, `video_metadata`), and it paces itself inside the account's rate limit instead of bouncing off 429s.

```bash
# Submit. Charged 1 credit per unique video, returns 202 immediately
curl -s -X POST "https://api.transcriptout.com/v1/transcripts" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"videos":["VIDEO_ID_1","VIDEO_ID_2"],"lang":"en","format":"text"}'
```

The `202` response carries `job_id`, `status`, `count` and `credits: {charged, refunded}`. Duplicates collapse BEFORE billing. Add an `Idempotency-Key` header when a retry is possible: resubmitting the same body with the same key returns the SAME job and does not charge twice.

```bash
# Progress (free)
curl -s "https://api.transcriptout.com/v1/transcripts/JOB_ID" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Results, readable before the job is done (free)
curl -s "https://api.transcriptout.com/v1/transcripts/JOB_ID/results?limit=100" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Cancel. Refunds only videos not started yet (free)
curl -s -X POST "https://api.transcriptout.com/v1/transcripts/JOB_ID/cancel" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

Requires a user key (`sk_...`). Results come in submission order, page by page (`limit` 1-500, `next_page_token`). Each entry is exactly what `/v1/transcript` returns for that video, plus its status. Videos that could not be delivered through the service's fault are refunded automatically.

## Credit Costs

| Endpoint | Cost |
| -------- | ---- |
| transcript | 1 |
| video (metadata) | 1 |
| search | 1/page |
| channel/latest | 1 |
| channel/videos | 1/page |
| channel/search | 1/page |
| playlist/videos | 1/page |
| playlist/search | 1 |
| transcripts (bulk job) | 1 per video |
| job status / results / cancel | **free** |

Credits are refunded automatically when a call fails before reaching YouTube (validation, rate limit, service capacity). A definitive "this video has no captions" (404) is an answer and is billed like one.

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
- More than ~5 transcripts? Submit ONE bulk job with IDs from `ids_only=true` listings.
- `channel/latest` is the cheapest channel question. Reach for it before `channel/videos`.
- Stop paginating once the user has enough: `has_more: true` is an offer, not an obligation.

Free tier: 100 credits on signup, 200 req/min. Starter ($4.49/mo): 1,000 credits/month, slider up to 100,000/month. Failed calls that never reached YouTube are refunded.
