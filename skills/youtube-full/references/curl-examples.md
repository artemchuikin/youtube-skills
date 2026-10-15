# Copy-paste request examples

The exact requests from SKILL.md as runnable one-liners. Same endpoints, same parameters, same header.

## Transcript · 1 credit

Fetch the transcript of any YouTube video.

```bash
curl -s "https://api.transcriptout.com/v1/transcript?video=VIDEO_URL_OR_ID&format=text" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
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
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```

**Credit hygiene:** if the transcript is wanted anyway, call `/v1/transcript` with `video_metadata=true` instead. One call and one credit against two.

## GET /v1/search · 1 credit/page

Search YouTube for videos or channels.

```bash
# Videos
curl -s "https://api.transcriptout.com/v1/search?q=QUERY&type=video&limit=20" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# Channels
curl -s "https://api.transcriptout.com/v1/search?q=QUERY&type=channel&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# Next page
curl -s "https://api.transcriptout.com/v1/search?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
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
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```

`name` accepts an `@handle`, a channel name, a `UC...` channel ID or a channel URL. No resolve step needed: pass the handle directly.

## GET /v1/channel/videos · 1 credit/page

Every video from a channel's Videos tab, newest first.

```bash
# First page (100 videos)
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# Next pages
curl -s "https://api.transcriptout.com/v1/channel/videos?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# IDs only, 500 per page (feed these into the bulk job)
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```

Provide `name` on the first call and only `next_page_token` afterwards. `limit` goes up to 100, or up to 500 with `ids_only=true` (the response is then `video_ids[]` instead of full video objects). The response carries `next_page_token` and `has_more`.

## GET /v1/channel/search · 1 credit/page

Search inside one channel using YouTube's native relevance search. A result whose title lacks the query word is normal: it is relevance, not substring match.

```bash
curl -s "https://api.transcriptout.com/v1/channel/search?name=@kurzgesagt&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
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
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# Next pages
curl -s "https://api.transcriptout.com/v1/playlist/videos?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# IDs only, 500 per page (feed these into the bulk job)
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```

`id` accepts a `PL...` playlist ID or any URL with `list=`. `limit` goes up to 100, or up to 500 with `ids_only=true`. The response carries `playlist`, `title`, `count`, `videos[]` (or `video_ids[]`), `next_page_token` and `has_more`.

## GET /v1/playlist/search · 1 credit

Find videos inside a playlist by a substring of the title (case-insensitive). YouTube has no native playlist search, so this scans up to 500 playlist items.

```bash
curl -s "https://api.transcriptout.com/v1/playlist/search?id=PL_ID_OR_URL&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```

`truncated: true` in the response means the scan window ended before the playlist did, so there may be more matches.

## Bulk transcripts: POST /v1/transcripts · 1 credit per video

One asynchronous job for up to 4,000 videos. Use it instead of looping over `/v1/transcript` for more than a handful of videos: same price per video, same options (`lang`, `format`, `kind`, `segment`, `video_metadata`), and it paces itself inside the account's rate limit instead of bouncing off 429s.

```bash
# Submit. Charged 1 credit per unique video, returns 202 immediately
curl -s -X POST "https://api.transcriptout.com/v1/transcripts" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full" \
  -H "Content-Type: application/json" \
  -d '{"videos":["VIDEO_ID_1","VIDEO_ID_2"],"lang":"en","format":"text"}'
```

The `202` response carries `job_id`, `status`, `count` and `credits: {charged, refunded}`. Duplicates collapse BEFORE billing. Add an `Idempotency-Key` header when a retry is possible: resubmitting the same body with the same key returns the SAME job and does not charge twice.

```bash
# Progress (free)
curl -s "https://api.transcriptout.com/v1/transcripts/JOB_ID" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# Results, readable before the job is done (free)
curl -s "https://api.transcriptout.com/v1/transcripts/JOB_ID/results?limit=100" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# Cancel. Refunds only videos not started yet (free)
curl -s -X POST "https://api.transcriptout.com/v1/transcripts/JOB_ID/cancel" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```

Requires a user key (`sk_...`). Results come in submission order, page by page (`limit` 1-500, `next_page_token`). Each entry is exactly what `/v1/transcript` returns for that video, plus its status. Videos that could not be delivered through the service's fault are refunded automatically.

## Typical Workflows

**Research:** search, pick the best videos, fetch their transcripts.

```bash
# 1. Search
curl -s "https://api.transcriptout.com/v1/search?q=rust+async+explained&limit=5" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# 2. Transcript of the best hit
curl -s "https://api.transcriptout.com/v1/transcript?video=VIDEO_ID&format=text&video_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```

**Channel monitoring:** latest, then transcript.

```bash
# 1. Latest uploads (pass the @handle directly)
curl -s "https://api.transcriptout.com/v1/channel/latest?name=@kurzgesagt" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# 2. Transcript of the newest
curl -s "https://api.transcriptout.com/v1/transcript?video=VIDEO_ID&format=text&video_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```

**Bulk export:** list IDs, submit one job, read pages.

```bash
# 1. Collect IDs, 500 per page
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@fireship&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"

# 2. One job for all of them
curl -s -X POST "https://api.transcriptout.com/v1/transcripts" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full" \
  -H "Content-Type: application/json" \
  -d '{"videos":["ID1","ID2","..."],"format":"text"}'

# 3. Read as they land
curl -s "https://api.transcriptout.com/v1/transcripts/JOB_ID/results" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-full"
```
