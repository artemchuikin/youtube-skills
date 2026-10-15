# Copy-paste request examples

The exact requests from SKILL.md as runnable one-liners. Same endpoints, same parameters, same header.

## GET /v1/transcript · 1 credit

Fetch the subtitles of any YouTube video: timed JSON segments, plain text, or ready-made `SRT`/`VTT` files.

```bash
# SRT body inside the JSON envelope
curl -s "https://api.transcriptout.com/v1/transcript?video=VIDEO_URL_OR_ID&format=srt" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/subtitles"

# or the raw .srt file itself
curl -s "https://api.transcriptout.com/v1/transcript?video=VIDEO_URL_OR_ID&format=srt&download=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/subtitles"
```

| Param            | Required | Default | Values |
| ---------------- | -------- | ------- | ------ |
| `video`          | yes      | -       | YouTube URL (full/short/shorts) or 11-char video ID |
| `lang`           | no       | `en`    | language code of the track (`en`, `de`, ...) |
| `format`         | no       | `json`  | `json`, `text`, `srt`, `vtt`, `srv3` |
| `kind`           | no       | manual if present | `manual`, `auto` |
| `segment`        | no       | auto tracks: 180 (80 for `srt`/`vtt`). Manual tracks keep the author's lines | 20-5000, max characters per segment |
| `video_metadata` | no       | `false` | `true` adds `data.metadata` (title, channel, duration, views) for the same 1 credit |
| `download`       | no       | `false` | `true` returns the raw file instead of the JSON envelope (`text`/`srt`/`vtt`/`srv3` only) |

With `format=srt` or `format=vtt` the default segmenting for auto-generated tracks is subtitle-sized (~80 characters per cue). Manual tracks keep the author's own line breaks in every format. `download=true` returns the bare file instead of the JSON envelope.

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
