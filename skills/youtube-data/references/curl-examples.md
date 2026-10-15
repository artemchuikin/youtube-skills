# Copy-paste request examples

The exact requests from SKILL.md as runnable one-liners. Same endpoints, same parameters, same header.

## GET /v1/video · 1 credit

Metadata for one video (title, channel, duration, views, thumbnails) plus the list of available transcript languages, WITHOUT downloading the subtitles.

```bash
curl -s "https://api.transcriptout.com/v1/video?id=VIDEO_URL_OR_ID" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"
```

**Credit hygiene:** if the transcript is wanted anyway, call `/v1/transcript` with `video_metadata=true` instead. One call and one credit against two.

## Transcript data · 1 credit

Fetch the transcript of any YouTube video.

```bash
curl -s "https://api.transcriptout.com/v1/transcript?video=VIDEO_URL_OR_ID&format=text" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"
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

## GET /v1/search · 1 credit/page

Search YouTube for videos or channels.

```bash
# Videos
curl -s "https://api.transcriptout.com/v1/search?q=QUERY&type=video&limit=20" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"

# Channels
curl -s "https://api.transcriptout.com/v1/search?q=QUERY&type=channel&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"

# Next page
curl -s "https://api.transcriptout.com/v1/search?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"
```

| Param             | Required | Default | Validation |
| ----------------- | -------- | ------- | ---------- |
| `q`               | yes*     | -       | the query (*or pass `next_page_token`) |
| `type`            | no       | `video` | `video`, `channel` |
| `limit`           | no       | `20`    | 1-50 |
| `next_page_token` | no       | -       | token from a previous page |

The response carries `next_page_token` and `has_more`. Video entries have `video_id`, `title`, `channel`, `duration` (`"M:SS"`), `view_count`, `published`, `url`, `thumbnails`.

## GET /v1/channel/videos · 1 credit/page

Every video from a channel's Videos tab, newest first.

```bash
# First page (100 videos)
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"

# Next pages
curl -s "https://api.transcriptout.com/v1/channel/videos?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"

# IDs only, 500 per page (feed these into the bulk job)
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"
```

Provide `name` on the first call and only `next_page_token` afterwards. `limit` goes up to 100, or up to 500 with `ids_only=true` (the response is then `video_ids[]` instead of full video objects). The response carries `next_page_token` and `has_more`.

## GET /v1/playlist/videos · 1 credit/page

Every video of a playlist, in playlist order.

```bash
# First page (100 videos)
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"

# Next pages
curl -s "https://api.transcriptout.com/v1/playlist/videos?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"

# IDs only, 500 per page (feed these into the bulk job)
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-data"
```

`id` accepts a `PL...` playlist ID or any URL with `list=`. `limit` goes up to 100, or up to 500 with `ids_only=true`. The response carries `playlist`, `title`, `count`, `videos[]` (or `video_ids[]`), `next_page_token` and `has_more`.
