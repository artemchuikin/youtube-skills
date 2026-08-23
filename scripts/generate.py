#!/usr/bin/env python3
"""Generate the 12 TranscriptOut agent skills (skills/ + clawhub/) from one section library.

Every SKILL.md, auth-setup.md and curl-examples.md in this repo is emitted by this script, so the
endpoints, tables and error codes cannot drift apart between the 12 variants. Edit the section
library here and re-run `python3 scripts/generate.py`. Never hand-edit the generated files.

skills/  -> SKILL.md with ```http blocks + references/auth-setup.md + references/curl-examples.md
clawhub/ -> SKILL.md with ```bash blocks + references/auth-setup.md (examples are inline already)
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://api.transcriptout.com/v1"
KEY = "$TRANSCRIPTOUT_API_KEY"


def req(lines, style):
    """lines: list of (comment_or_None, 'GET url') or (comment, 'POST url', body_json_str)."""
    out = []
    if style == "http":
        out.append("```http")
        first = True
        for item in lines:
            comment, request = item[0], item[1]
            body = item[2] if len(item) > 2 else None
            if not first:
                out.append("")
            first = False
            if comment:
                out.append(f"# {comment}")
            out.append(request)
            out.append(f"Authorization: Bearer {KEY}")
            if body:
                out.append("Content-Type: application/json")
                out.append("")
                out.append(body)
        out.append("```")
    else:
        out.append("```bash")
        first = True
        for item in lines:
            comment, request = item[0], item[1]
            body = item[2] if len(item) > 2 else None
            if not first:
                out.append("")
            first = False
            if comment:
                out.append(f"# {comment}")
            method, url = request.split(" ", 1)
            if method == "GET":
                out.append(f'curl -s "{url}" \\')
                out.append(f'  -H "Authorization: Bearer {KEY}"')
            else:
                out.append(f'curl -s -X {method} "{url}" \\')
                out.append(f'  -H "Authorization: Bearer {KEY}" \\')
                if body:
                    out.append('  -H "Content-Type: application/json" \\')
                    out.append(f"  -d '{body}'")
                else:
                    out[-1] = out[-1].rstrip(" \\")
        out.append("```")
    return "\n".join(out)


# ─────────────────────────────── section library ───────────────────────────────

def sec_setup(style):
    return (
        "## Setup\n\n"
        f"If `{KEY}` is not set, read [references/auth-setup.md](references/auth-setup.md) "
        "and follow the instructions there to get and store the key."
    )


def sec_headers(style):
    return (
        "## Required Header\n\n"
        "Every request needs one header:\n\n"
        f"- **Authorization:** `Bearer {KEY}`\n\n"
        "Every response is one JSON envelope. Success: `{\"ok\": true, \"request_id\": \"...\", "
        "\"data\": {...}}`. Error: `{\"ok\": false, \"code\": \"...\", \"detail\": \"...\", "
        "\"request_id\": \"...\"}`. Branch on the machine-readable `code`, not on the human text. "
        "The remaining credit balance rides in the `X-Credits-Remaining` response header."
    )


def sec_apiref(style):
    return (
        "## API Reference\n\n"
        f"Base URL: `{BASE}`. Full reference with the latest parameters and schemas: "
        "[transcriptout.com/docs](https://transcriptout.com/docs)."
    )


TRANSCRIPT_TABLE = """| Param            | Required | Default | Values |
| ---------------- | -------- | ------- | ------ |
| `video`          | yes      | -       | YouTube URL (full/short/shorts) or 11-char video ID |
| `lang`           | no       | `en`    | language code of the track (`en`, `de`, ...) |
| `format`         | no       | `json`  | `json`, `text`, `srt`, `vtt`, `srv3` |
| `kind`           | no       | manual if present | `manual`, `auto` |
| `segment`        | no       | auto tracks: 180 (80 for `srt`/`vtt`). Manual tracks keep the author's lines | 20-5000, max characters per segment |
| `video_metadata` | no       | `false` | `true` adds `data.metadata` (title, channel, duration, views) for the same 1 credit |
| `download`       | no       | `false` | `true` returns the raw file instead of the JSON envelope (`text`/`srt`/`vtt`/`srv3` only) |"""

TRANSCRIPT_RESPONSE = """**Response** for `format=json`. With `format=text`/`srt`/`vtt`/`srv3` the `transcript` field is one string in that format:

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
```"""


def _transcript_body(style, heading, intro):
    r = req([(None, f"GET {BASE}/transcript?video=VIDEO_URL_OR_ID&format=text")], style)
    return (
        f"{heading}\n\n{intro}\n\n{r}\n\n"
        "Accepts full URLs (`youtube.com/watch?v=ID`), short URLs (`youtu.be/ID`), shorts "
        "(`youtube.com/shorts/ID`), or bare video IDs.\n\n"
        "**Default for agents:** use `format=text` unless you need timestamps. Plain text is the "
        "cheapest form to reason over. Use `format=json` to cite or seek to exact moments. Add "
        "`video_metadata=true` when the title/channel is also wanted: same call, same 1 credit.\n\n"
        f"{TRANSCRIPT_TABLE}\n\n"
        "`segment` controls the size of the pieces: 500-1500 characters makes chunks with enough "
        "context for embeddings and retrieval. Left out, an auto-generated track is cut into "
        "~180-character segments and a manual track is returned exactly as its author broke it.\n\n"
        f"{TRANSCRIPT_RESPONSE}"
    )


def sec_transcript(style, heading="## GET /v1/transcript · 1 credit"):
    return _transcript_body(style, heading, "Fetch the transcript of any YouTube video.")


def sec_transcript_subs(style, word):
    r = req([
        ("SRT body inside the JSON envelope",
         f"GET {BASE}/transcript?video=VIDEO_URL_OR_ID&format=srt"),
        ("or the raw .srt file itself",
         f"GET {BASE}/transcript?video=VIDEO_URL_OR_ID&format=srt&download=true"),
    ], style)
    return (
        f"## GET /v1/transcript · 1 credit\n\n"
        f"Fetch the {word} of any YouTube video: timed JSON segments, plain text, or ready-made "
        f"`SRT`/`VTT` files.\n\n{r}\n\n"
        f"{TRANSCRIPT_TABLE}\n\n"
        "With `format=srt` or `format=vtt` the default segmenting for auto-generated tracks is "
        "subtitle-sized (~80 characters per cue). Manual tracks keep the author's own line breaks "
        "in every format. `download=true` returns the bare file instead of the JSON envelope.\n\n"
        f"{TRANSCRIPT_RESPONSE}"
    )


def sec_video_info(style):
    r = req([(None, f"GET {BASE}/video?id=VIDEO_URL_OR_ID")], style)
    return (
        "## GET /v1/video · 1 credit\n\n"
        "Metadata for one video (title, channel, duration, views, thumbnails) plus the list of "
        f"available transcript languages, WITHOUT downloading the subtitles.\n\n{r}\n\n"
        "**Credit hygiene:** if the transcript is wanted anyway, call `/v1/transcript` with "
        "`video_metadata=true` instead. One call and one credit against two."
    )


def sec_search(style):
    r = req([
        ("Videos", f"GET {BASE}/search?q=QUERY&type=video&limit=20"),
        ("Channels", f"GET {BASE}/search?q=QUERY&type=channel&limit=10"),
        ("Next page", f"GET {BASE}/search?next_page_token=TOKEN"),
    ], style)
    return (
        "## GET /v1/search · 1 credit/page\n\n"
        f"Search YouTube for videos or channels.\n\n{r}\n\n"
        "| Param             | Required | Default | Validation |\n"
        "| ----------------- | -------- | ------- | ---------- |\n"
        "| `q`               | yes*     | -       | the query (*or pass `next_page_token`) |\n"
        "| `type`            | no       | `video` | `video`, `channel` |\n"
        "| `limit`           | no       | `20`    | 1-50 |\n"
        "| `next_page_token` | no       | -       | token from a previous page |\n\n"
        "The response carries `next_page_token` and `has_more`. Video entries have `video_id`, "
        "`title`, `channel`, `duration` (`\"M:SS\"`), `view_count`, `published`, `url`, `thumbnails`."
    )


def sec_channel_latest(style):
    r = req([(None, f"GET {BASE}/channel/latest?name=@kurzgesagt")], style)
    return (
        "## GET /v1/channel/latest · 1 credit\n\n"
        "The ~15 most recent videos of a channel, served from its RSS feed: the fastest and "
        f"cheapest way to check what a creator published recently.\n\n{r}\n\n"
        "`name` accepts an `@handle`, a channel name, a `UC...` channel ID or a channel URL. "
        "No resolve step needed: pass the handle directly."
    )


def sec_channel_videos(style):
    r = req([
        ("First page (100 videos)", f"GET {BASE}/channel/videos?name=@3blue1brown"),
        ("Next pages", f"GET {BASE}/channel/videos?next_page_token=TOKEN"),
        ("IDs only, 500 per page (feed these into the bulk job)",
         f"GET {BASE}/channel/videos?name=@3blue1brown&ids_only=true"),
    ], style)
    return (
        "## GET /v1/channel/videos · 1 credit/page\n\n"
        f"Every video from a channel's Videos tab, newest first.\n\n{r}\n\n"
        "Provide `name` on the first call and only `next_page_token` afterwards. `limit` goes up "
        "to 100, or up to 500 with `ids_only=true` (the response is then `video_ids[]` instead of "
        "full video objects). The response carries `next_page_token` and `has_more`."
    )


def sec_channel_search(style):
    r = req([(None, f"GET {BASE}/channel/search?name=@kurzgesagt&q=QUERY&limit=30")], style)
    return (
        "## GET /v1/channel/search · 1 credit/page\n\n"
        "Search inside one channel using YouTube's native relevance search. A result whose title "
        f"lacks the query word is normal: it is relevance, not substring match.\n\n{r}\n\n"
        "| Param             | Required | Default | Validation |\n"
        "| ----------------- | -------- | ------- | ---------- |\n"
        "| `name`            | yes*     | -       | `@handle`, channel name, `UC...` ID or URL (*or `next_page_token`) |\n"
        "| `q`               | yes*     | -       | query to search within the channel |\n"
        "| `limit`           | no       | `30`    | 1-100 |\n"
        "| `next_page_token` | no       | -       | token from a previous page |\n\n"
        "Cheaper and better-ranked than downloading the catalogue and grepping it."
    )


def sec_playlist_videos(style):
    r = req([
        ("First page (100 videos)", f"GET {BASE}/playlist/videos?id=PL_ID_OR_URL"),
        ("Next pages", f"GET {BASE}/playlist/videos?next_page_token=TOKEN"),
        ("IDs only, 500 per page (feed these into the bulk job)",
         f"GET {BASE}/playlist/videos?id=PL_ID_OR_URL&ids_only=true"),
    ], style)
    return (
        "## GET /v1/playlist/videos · 1 credit/page\n\n"
        f"Every video of a playlist, in playlist order.\n\n{r}\n\n"
        "`id` accepts a `PL...` playlist ID or any URL with `list=`. `limit` goes up to 100, or up "
        "to 500 with `ids_only=true`. The response carries `playlist`, `title`, `count`, "
        "`videos[]` (or `video_ids[]`), `next_page_token` and `has_more`."
    )


def sec_playlist_search(style):
    r = req([(None, f"GET {BASE}/playlist/search?id=PL_ID_OR_URL&q=QUERY&limit=30")], style)
    return (
        "## GET /v1/playlist/search · 1 credit\n\n"
        "Find videos inside a playlist by a substring of the title (case-insensitive). YouTube has "
        f"no native playlist search, so this scans up to 500 playlist items.\n\n{r}\n\n"
        "`truncated: true` in the response means the scan window ended before the playlist did, so "
        "there may be more matches."
    )


def sec_batch(style):
    body = '{"videos":["VIDEO_ID_1","VIDEO_ID_2"],"lang":"en","format":"text"}'
    r1 = req([("Submit. Charged 1 credit per unique video, returns 202 immediately",
               f"POST {BASE}/transcripts", body)], style)
    r2 = req([
        ("Progress (free)", f"GET {BASE}/transcripts/JOB_ID"),
        ("Results, readable before the job is done (free)",
         f"GET {BASE}/transcripts/JOB_ID/results?limit=100"),
        ("Cancel. Refunds only videos not started yet (free)",
         f"POST {BASE}/transcripts/JOB_ID/cancel"),
    ], style)
    return (
        "## Bulk transcripts: POST /v1/transcripts · 1 credit per video\n\n"
        "One asynchronous job for up to 4,000 videos. Use it instead of looping over "
        "`/v1/transcript` for more than a handful of videos: same price per video, same options "
        f"(`lang`, `format`, `kind`, `segment`, `video_metadata`), and it paces itself inside the "
        f"account's rate limit instead of bouncing off 429s.\n\n{r1}\n\n"
        "The `202` response carries `job_id`, `status`, `count` and "
        "`credits: {charged, refunded}`. Duplicates collapse BEFORE billing. Add an "
        "`Idempotency-Key` header when a retry is possible: resubmitting the same body with the "
        f"same key returns the SAME job and does not charge twice.\n\n{r2}\n\n"
        "Requires a user key (`sk_...`). Results come in submission order, page by page "
        "(`limit` 1-500, `next_page_token`). Each entry is exactly what `/v1/transcript` returns "
        "for that video, plus its status. Videos that could not be delivered through the "
        "service's fault are refunded automatically."
    )


def sec_costs(style, rows):
    lines = ["## Credit Costs", "", "| Endpoint | Cost |", "| -------- | ---- |"]
    lines += [f"| {a} | {b} |" for a, b in rows]
    lines += ["",
              "Credits are refunded automatically when a call fails before reaching YouTube "
              "(validation, rate limit, service capacity). A definitive \"this video has no "
              "captions\" (404) is an answer and is billed like one."]
    return "\n".join(lines)


COSTS_FULL = [
    ("transcript", "1"), ("video (metadata)", "1"), ("search", "1/page"),
    ("channel/latest", "1"), ("channel/videos", "1/page"), ("channel/search", "1/page"),
    ("playlist/videos", "1/page"), ("playlist/search", "1"),
    ("transcripts (bulk job)", "1 per video"),
    ("job status / results / cancel", "**free**"),
]


def sec_errors(style):
    return (
        "## Errors\n\n"
        "| Code | Meaning | Action |\n"
        "| ---- | ------- | ------ |\n"
        "| 400/422 | Bad parameter | Fix the request. Credit refunded automatically |\n"
        "| 401 | Bad or missing API key | Check the key. It must start with `sk_` |\n"
        "| 402 | Out of credits | [transcriptout.com/billing](https://transcriptout.com/billing) |\n"
        "| 404 | No captions on that language/track, or bad ID | Definitive answer, do not retry. Try another `lang` or `kind=auto`. Billed |\n"
        "| 410 | Video removed | Do not retry |\n"
        "| 451 | Age-restricted or members-only | Do not retry |\n"
        "| 429 | Rate limit (200 req/min per key) | Wait, respect `Retry-After`. Refunded |\n"
        "| 502 | Failed on YouTube's side | One retry is reasonable. Billed |\n"
        "| 503 | Service at capacity | Retry after `Retry-After`. Refunded |\n\n"
        "Every error body carries a machine-readable `code` and a `request_id`. Include the "
        "`request_id` when contacting support."
    )


def sec_tips(style, full=False):
    lines = [
        "## Tips",
        "",
        "- `format=text` is the cheapest form to reason over. Ask for `json` only when timestamps matter.",
        "- Transcript AND title/channel wanted? One call: `video_metadata=true`. Never a separate `/v1/video` first.",
        "- Transcribe last: search and listings are for choosing, and pulling transcripts for a whole results page nobody asked to read is the fastest way to burn a balance.",
    ]
    if full:
        lines += [
            "- More than ~5 transcripts? Submit ONE bulk job with IDs from `ids_only=true` listings.",
            "- `channel/latest` is the cheapest channel question. Reach for it before `channel/videos`.",
            "- Stop paginating once the user has enough: `has_more: true` is an offer, not an obligation.",
        ]
    return "\n".join(lines)


def sec_workflows(style):
    r1 = req([
        ("1. Search", f"GET {BASE}/search?q=rust+async+explained&limit=5"),
        ("2. Transcript of the best hit",
         f"GET {BASE}/transcript?video=VIDEO_ID&format=text&video_metadata=true"),
    ], style)
    r2 = req([
        ("1. Latest uploads (pass the @handle directly)", f"GET {BASE}/channel/latest?name=@kurzgesagt"),
        ("2. Transcript of the newest",
         f"GET {BASE}/transcript?video=VIDEO_ID&format=text&video_metadata=true"),
    ], style)
    r3 = req([
        ("1. Collect IDs, 500 per page", f"GET {BASE}/channel/videos?name=@fireship&ids_only=true"),
        ("2. One job for all of them", f"POST {BASE}/transcripts",
         '{"videos":["ID1","ID2","..."],"format":"text"}'),
        ("3. Read as they land", f"GET {BASE}/transcripts/JOB_ID/results"),
    ], style)
    return (
        "## Typical Workflows\n\n"
        f"**Research:** search, pick the best videos, fetch their transcripts.\n\n{r1}\n\n"
        f"**Channel monitoring:** latest, then transcript.\n\n{r2}\n\n"
        f"**Bulk export:** list IDs, submit one job, read pages.\n\n{r3}"
    )


def sec_workflow_search(style):
    r = req([
        ("1. Search", f"GET {BASE}/search?q=QUERY&limit=5"),
        ("2. Transcript of a chosen result",
         f"GET {BASE}/transcript?video=VIDEO_ID&format=text&video_metadata=true"),
    ], style)
    return ("## Workflow: Search → Transcript\n\n"
            "Results are metadata only: choose from them, then transcribe just the chosen few "
            f"(the transcript endpoint is 1 credit and lives in the `transcript` skill).\n\n{r}")


def sec_workflow_channel(style):
    r = req([
        ("Cheapest first: what did they post lately?", f"GET {BASE}/channel/latest?name=@handle"),
        ("Whole catalogue as IDs when bulk work follows",
         f"GET {BASE}/channel/videos?name=@handle&ids_only=true"),
    ], style)
    return ("## Typical workflow\n\n"
            "Start with `channel/latest` when recent uploads are enough. `channel/videos` is for "
            f"genuine catalogue work.\n\n{r}")


def sec_workflow_playlist(style):
    r = req([
        ("1. Collect the playlist's IDs", f"GET {BASE}/playlist/videos?id=PL_ID&ids_only=true"),
        ("2. One bulk job for every video", f"POST {BASE}/transcripts",
         '{"videos":["ID1","ID2","..."],"format":"text"}'),
        ("3. Progress and results", f"GET {BASE}/transcripts/JOB_ID"),
    ], style)
    return ("## Workflow: Playlist → Transcripts\n\n"
            "For a whole course or series, do not loop single transcript calls: collect the IDs "
            f"and submit ONE asynchronous job (1 credit per video, up to 4,000).\n\n{r}")


def sec_extract_playlist_id(style):
    return (
        "## Extract a playlist reference from a URL\n\n"
        "No extraction needed: `id` accepts the full URL as pasted (`youtube.com/playlist?list=PL...`, "
        "or a watch URL with `list=`). A bare `PL...` ID works too."
    )


def sec_endpoint_summary(style):
    return (
        "## Endpoint Reference\n\n"
        "| Endpoint | What it returns | Cost |\n"
        "| -------- | --------------- | ---- |\n"
        "| `GET /v1/transcript` | transcript of one video (`json`/`text`/`srt`/`vtt`/`srv3`) | 1 |\n"
        "| `GET /v1/video` | title, channel, duration, views + available caption languages | 1 |\n"
        "| `GET /v1/search` | YouTube search, videos or channels | 1/page |\n"
        "| `GET /v1/channel/latest` | ~15 newest uploads of a channel | 1 |\n"
        "| `GET /v1/channel/videos` | full upload history, paginated | 1/page |\n"
        "| `GET /v1/channel/search` | native relevance search inside a channel | 1/page |\n"
        "| `GET /v1/playlist/videos` | playlist contents, paginated | 1/page |\n"
        "| `GET /v1/playlist/search` | title-substring search inside a playlist | 1 |\n"
        "| `POST /v1/transcripts` | asynchronous bulk job, up to 4,000 videos | 1 per video |\n"
        "| `GET /v1/transcripts/{id}` + `/results` | job progress and results | free |\n"
    )


def sec_quick_examples(style):
    r = req([
        ("A transcript with metadata",
         f"GET {BASE}/transcript?video=dQw4w9WgXcQ&format=text&video_metadata=true"),
        ("Search", f"GET {BASE}/search?q=rust+lifetimes&limit=10"),
        ("A channel's uploads", f"GET {BASE}/channel/videos?name=@3blue1brown"),
        ("A playlist", f"GET {BASE}/playlist/videos?id=PLAYLIST_URL"),
    ], style)
    return f"## Quick Examples\n\n{r}"


def sec_why_not_google(style):
    return (
        "## Why Not Google's API?\n\n"
        "- The YouTube Data API does not return transcripts at all. TranscriptOut's core endpoint does.\n"
        "- No Google Cloud project, no OAuth consent screens, no daily quota units: one Bearer key.\n"
        "- Channel and playlist listings cost 1 credit per page instead of burning quota per item.\n"
        "- Search, in-channel search and playlist search come from the same base URL with the same key."
    )


def sec_curl_pointer(style):
    return ("## Copy-paste examples\n\n"
            "Every request in this file as a ready-to-run one-liner: "
            "[references/curl-examples.md](references/curl-examples.md)")


def sec_pricing_line(style):
    return ("Free tier: 100 credits on signup, 200 req/min. Starter ($4.49/mo): 1,000 credits/month, "
            "slider up to 100,000/month. Failed calls that never reached YouTube are refunded.")


# ─────────────────────────────── skill definitions ───────────────────────────────

SKILLS = {
    "youtube-full": dict(
        emoji="▶️", clawmoji="🎯",
        tags=["youtube", "transcripts", "video", "search", "channels", "playlists", "captions"],
        title="YouTube Full",
        intro="Complete YouTube toolkit via [TranscriptOut.com](https://transcriptout.com). Everything in one skill.",
        description=(
            "Reach for this whenever a task touches YouTube, whether or not the word appears: a pasted watch/shorts/channel/playlist link, a bare 11-char video ID or @handle, a creator to look up, a talk to summarize, quote or translate, research where lectures, tutorials and reviews beat written sources, or a product launch to catch on video. One skill for transcripts, video and channel search, channel browsing, in-channel search, playlists and 4,000-video batch jobs. Skip it for uploads, comments and account chores."),
        sections=[sec_setup, sec_headers, sec_apiref,
                  lambda s: sec_transcript(s, "## Transcript · 1 credit"),
                  sec_video_info, sec_search, sec_channel_latest, sec_channel_videos,
                  sec_channel_search, sec_playlist_videos, sec_playlist_search, sec_batch,
                  lambda s: sec_costs(s, COSTS_FULL), sec_errors,
                  lambda s: sec_tips(s, full=True), sec_workflows, sec_pricing_line],
    ),
    "transcript": dict(
        emoji="▶️", clawmoji="📝",
        tags=["youtube", "transcripts", "video", "captions", "summarization", "research", "translation"],
        title="Transcript",
        intro="Fetch video transcripts via [TranscriptOut.com](https://transcriptout.com).",
        description=(
            "Reach for this whenever what was SAID in a YouTube video matters: a pasted link or bare video ID, a summary, quote, translation or fact-check request, notes from a lecture, or research that leans on a specific video. Works even when nobody says the word 'transcript'. Skip it for uploads and account chores."),
        sections=[sec_setup, sec_headers, sec_transcript, sec_errors, sec_tips],
    ),
    "captions": dict(
        emoji="💬", clawmoji="💬",
        tags=["youtube", "captions", "cc", "subtitles", "accessibility", "video"],
        title="Captions",
        intro="Extract closed captions from YouTube videos via [TranscriptOut.com](https://transcriptout.com).",
        description=(
            "Reach for this when caption text from a YouTube video is wanted: reading a video instead of watching it, quoting or translating speech, accessibility (deaf/HoH) needs, content review, language practice, or exporting CC as SRT/VTT files. Timestamped captions from any public video. Skip it for uploading captions or account chores."),
        sections=[sec_setup, sec_headers,
                  lambda s: sec_transcript_subs(s, "closed captions"),
                  sec_tips, sec_errors],
    ),
    "subtitles": dict(
        emoji="📺", clawmoji="📺",
        tags=["youtube", "subtitles", "srt", "vtt", "video", "translation"],
        title="Subtitles",
        intro="Fetch YouTube video subtitles via [TranscriptOut.com](https://transcriptout.com).",
        description=(
            "Reach for this when subtitles are wanted from a YouTube video: following foreign-language content, reading along, translating speech, language practice, or exporting ready SRT/VTT files. Skip it for uploading subtitles or account chores."),
        sections=[sec_setup, sec_headers,
                  lambda s: sec_transcript_subs(s, "subtitles"),
                  sec_tips, sec_errors],
    ),
    "video-transcript": dict(
        emoji="🎞️", clawmoji="🎞️",
        tags=["youtube", "video", "transcript", "video-to-text", "summarization"],
        title="Video Transcript",
        intro="Extract transcripts from videos via [TranscriptOut.com](https://transcriptout.com).",
        description=(
            "Reach for this when a video needs to become text: a pasted YouTube link or ID, a transcribe/summarize/translate request, mining a video for facts, or a bare URL shared with 'what does this say?'. Skip it for uploads and account chores."),
        sections=[sec_setup, sec_headers, sec_transcript, sec_tips, sec_errors],
    ),
    "youtube-search": dict(
        emoji="🔍", clawmoji="🔍",
        tags=["youtube", "search", "video-search", "channels", "research", "discovery"],
        title="YouTube Search",
        intro="Search YouTube and fetch transcripts via [TranscriptOut.com](https://transcriptout.com).",
        description=(
            "Reach for this when the user needs to FIND things on YouTube: videos or channels on a topic, creators covering a subject, tutorials, talks and reviews worth reading, or a channel looked up by name or handle. Also good proactively when researching a topic that video would cover well. Skip it for account chores and text-only research."),
        sections=[sec_setup, sec_headers, sec_apiref, sec_search, sec_channel_search,
                  sec_workflow_search, sec_errors],
    ),
    "youtube-channels": dict(
        emoji="📡", clawmoji="📡",
        tags=["youtube", "channels", "creators", "uploads", "monitoring", "handles"],
        title="YouTube Channels",
        intro="YouTube channel tools via [TranscriptOut.com](https://transcriptout.com).",
        description=(
            "Reach for this when a YouTube channel is the subject: a pasted @handle or channel URL, a creator's recent uploads, their full catalogue, or a search inside one channel. Also good for keeping an eye on what somebody publishes. Skip it for creating channels or account chores."),
        sections=[sec_setup, sec_headers, sec_apiref, sec_channel_latest, sec_channel_videos,
                  sec_channel_search, sec_workflow_channel, sec_errors],
    ),
    "youtube-playlist": dict(
        emoji="🗂️", clawmoji="🗂️",
        tags=["youtube", "playlists", "courses", "series", "bulk", "transcripts"],
        title="YouTube Playlist",
        intro="Browse playlists and fetch transcripts via [TranscriptOut.com](https://transcriptout.com).",
        description=(
            "Reach for this when a YouTube playlist is in play: a pasted playlist link or PL... id, listing a course or series, finding one video inside a long playlist, or turning a whole playlist into transcripts. Skip it for creating playlists or account chores."),
        sections=[sec_setup, sec_headers, sec_apiref, sec_playlist_videos, sec_playlist_search,
                  sec_workflow_playlist, sec_extract_playlist_id, sec_errors],
    ),
    "youtube-data": dict(
        emoji="📊", clawmoji="📊",
        tags=["youtube", "data", "metadata", "api", "channels", "playlists"],
        title="YouTube Data",
        intro=("YouTube data access via [TranscriptOut.com](https://transcriptout.com): a "
               "lightweight alternative to Google's YouTube Data API."),
        description=(
            "Reach for this when structured YouTube data is the goal: video metadata, transcripts for analysis, channel upload history, search results or playlist contents, with no Google Cloud project and no quota units. Triggers on YouTube links, creator names and topic research even when unstated. Skip it for uploads and text-only research."),
        sections=[sec_setup, sec_headers, sec_apiref, sec_video_info,
                  lambda s: sec_transcript(s, "## Transcript data · 1 credit"),
                  sec_search, sec_channel_videos, sec_playlist_videos,
                  lambda s: sec_costs(s, COSTS_FULL), sec_errors],
    ),
    "youtube-api": dict(
        emoji="🧰", clawmoji="🧰",
        tags=["youtube", "api", "rest", "transcripts", "search", "no-quota"],
        title="YouTube API",
        intro=("YouTube API access via [TranscriptOut.com](https://transcriptout.com): no Google "
               "quota needed."),
        description=(
            "Reach for this when YouTube data is needed and Google's Data API is the obstacle: no quota units, no OAuth consent screens, one Bearer key. Covers transcripts (which Google's API does not serve at all), metadata, search, channels and playlists. Triggers on YouTube links, @handles and creator research. Skip it for uploads and account chores."),
        sections=[sec_setup, sec_headers, sec_apiref, sec_endpoint_summary, sec_quick_examples,
                  sec_why_not_google, sec_errors],
    ),
    "transcriptout": dict(
        emoji="🚀", clawmoji="🚀",
        tags=["youtube", "transcripts", "video", "search", "channels", "playlists", "captions"],
        title="TranscriptOut",
        intro=("Full YouTube data toolkit via [TranscriptOut.com](https://transcriptout.com). "
               "Transcripts, search, channels, playlists, bulk jobs: one API key."),
        description=(
            "Reach for this whenever a task touches YouTube, said or unsaid: pasted video/channel/playlist links, IDs and @handles, summaries, quotes, translations, topic research through talks and tutorials, creator monitoring. The full TranscriptOut surface: transcripts in five formats, search, channels, playlists and batch jobs. Skip it for uploads and account chores."),
        sections=[sec_setup, sec_headers, sec_apiref,
                  lambda s: sec_transcript(s, "## Transcript · 1 credit"),
                  sec_video_info, sec_search, sec_channel_latest, sec_channel_videos,
                  sec_channel_search, sec_playlist_videos, sec_playlist_search, sec_batch,
                  lambda s: sec_costs(s, COSTS_FULL), sec_errors,
                  lambda s: sec_tips(s, full=True), sec_pricing_line],
    ),
    "yt": dict(
        emoji="⚡", clawmoji="⚡",
        tags=["youtube", "transcripts", "search", "quick", "video"],
        title="yt",
        intro="Quick YouTube lookup via [TranscriptOut.com](https://transcriptout.com).",
        description=(
            "Reach for this for quick YouTube lookups: a pasted link or video ID, a fast summary, what a channel posted lately, a topic search. Transcripts, search and channel-latest in one small skill. Skip it for uploads and account chores."),
        sections=[sec_setup, sec_headers,
                  lambda s: sec_transcript(s, "## Transcript · 1 credit"),
                  sec_search, sec_channel_latest, sec_errors],
    ),
}

AUTH_SETUP = """# TranscriptOut: Getting and Storing Your API Key

How to get a TranscriptOut API key and store it so it is still there in the next session and the
next shell. Read the whole file before running anything.

---

## Step 0: Understand how to store the key on this system

First decide WHERE the key will live on this machine. The requirement: an environment variable
that every future session sees, non-interactive shells included. What satisfies it differs by
platform and by agent runtime (a shell profile file on one system, a config or secret store owned
by the runtime on another), so check how YOUR environment persists variables instead of guessing.

The variable name you will be storing is `TRANSCRIPTOUT_API_KEY`.

---

## Step 1: Ask the user one question

Ask the user exactly this, in a single message:

> Do you have a TranscriptOut key already? Paste it and I'll wire it up. If not, give me an email
> address and I'll open a free account for you: 100 credits included, no card asked.

- If they paste a key (starts with `sk_`), go straight to **Storing the Key** below.
- If they want a new account, go to **Path B**.

---

## Path A: User already has a key

The user pasted their key. TranscriptOut keys always start with `sk_`. Go straight to
**Storing the Key** at the bottom of this document.

---

## Path B: Create a new account

You do the signup for the user, in two HTTP calls: register (a 6-digit code goes to their inbox),
then verify (the code comes back as an API key). Every response is the standard TranscriptOut
envelope `{"ok": true, "request_id": "...", "data": {...}}`. The fields you need live under
`data`.

### Step B-1: Ask for their email

Ask the user for the email address they want to use.

### Step B-2: Register

Make a POST request to:

```
POST https://api.transcriptout.com/auth/register-cli
Content-Type: application/json

{ "email": "the_user_email" }
```

**Pipe the response into a temporary file and build the next request by reading the token out of
that file. Never echo the token on its own.** Several agent runtimes scrub anything shaped like
`access_token` or a bearer token from tool output before the model sees it, so a printed token
arrives as `[REDACTED]` and the flow dead-ends. File in, file out, one chained command.

The response looks like this:

```json
{
  "ok": true,
  "request_id": "req_...",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "email": "user@example.com",
    "expires_in": 3600
  }
}
```

`data.access_token` is a short-lived session token you will use as the Bearer token in the next
request. It expires together with the code, so proceed promptly.

Possible errors (the envelope carries a machine `code` field):

- `429` with `code: "signup_throttled"`: a code was already sent recently, or too many requests.
  Wait the `Retry-After` seconds and retry.
- `400` with `code: "invalid_email"`: the address is malformed, ask the user to re-check it.
- `501`: CLI signup is not enabled on the server. Fall back to the **Browser path** below.

### Step B-3: Tell the user to check their email

Tell the user a 6-digit code is on its way to their inbox and ask them to read it back to you.

The email is the regular TranscriptOut sign-in email: it carries a sign-in button and, below it,
the 6-digit one-time code. The user needs the code, not the button.

### Step B-4: Verify

Once the user gives you the code, make a POST request to:

```
POST https://api.transcriptout.com/auth/verify-cli
Authorization: Bearer <the access_token from Step B-2>
Content-Type: application/json

{ "otp": "123456" }
```

Same discipline as before: **response into a file, key read out of the file**, because
`sk_`-prefixed values get scrubbed from tool output by the same runtimes.

The response looks like this:

```json
{
  "ok": true,
  "request_id": "req_...",
  "data": {
    "verified": true,
    "user_id": "...",
    "api_key": "sk_...",
    "credits": 100
  }
}
```

Read the `data.api_key` field from the file. This is the key you need to store. Go to
**Storing the Key** below.

Possible errors:

- `400` with `code: "invalid_otp"`: the code is wrong or expired. Ask the user to re-check it.
  If it keeps failing, start Path B again from Step B-2 (a fresh code invalidates the old one).
- `401` with `code: "signup_session_invalid"`: the session token expired or is malformed. Start
  Path B again from Step B-2.
- `409` with `code: "key_limit_reached"`: the account exists and already holds the maximum number
  of keys. Ask the user to revoke unused keys in the dashboard at transcriptout.com/dashboard,
  or to paste one of their existing keys (Path A).
- `429` with `code: "signup_throttled"`: too many verification attempts. Wait, then request a
  fresh code.

Note: an existing account is fine here. The same two steps simply sign the user in and issue a new
key. Possession of the emailed code is the same proof the regular sign-in link relies on.

---

## Browser path (fallback)

If the CLI endpoints answer `501`, or the user prefers doing it themselves:

1. Send them to **https://transcriptout.com/login**, where they sign in with Google or a magic link.
   Signing in for the first time IS the signup and grants the free 100 credits.
2. In the dashboard (**https://transcriptout.com/dashboard**) they create an API key. It starts
   with `sk_` and is shown **once**. Ask them to paste it to you right away.

---

## Storing the Key

You now have a string that starts with `sk_`. This is the `TRANSCRIPTOUT_API_KEY`.

Store it persistently using whatever method is correct for this environment (which you determined
in Step 0). Make sure it will be available in future sessions, including non-interactive shells,
without any manual sourcing step from the user.

Once stored, verify it is accessible in the current session. If the session needs a reload or
restart to pick up the new value, do that or tell the user to do it.

Delete the temporary files this process created.

## Verify the key works

One free call confirms both the key and the balance (`/auth/*` endpoints never spend credits):

```bash
curl -s https://api.transcriptout.com/auth/me \\
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```

A valid key returns your `user_id` and remaining `credits`. A `401` means the key is wrong,
revoked, or the variable did not load into this shell.

---

## Pitfalls seen in the wild

**The `access_token` or `api_key` value shows as `[REDACTED]` or is missing from the response.**
You let the response pass through tool output instead of writing it to a file first. Some agent
runtimes (notably Hermes) redact values matching patterns like `access_token`, `api_key`, or `sk_`
from command output before the model sees them. Always write the raw HTTP response body to a temp
file and read the value from there.

**Hermes agents: env var is set but not available in the next tool call.**
Hermes sandboxes `execute_code` and `terminal` calls. Setting an env var in one call does not
carry over to the next unless the variable is declared in the skill's
`required_environment_variables` frontmatter (these skills declare it). If it still does not
appear, persist the key using the agent's normal environment-secret mechanism so Hermes picks it
up on the next load.

**Claude Code agents: key is saved to shell profile but `$TRANSCRIPTOUT_API_KEY` is still empty.**
Writing to shell startup files only affects new shell sessions. The current session does not
reload profile files automatically. Either source the file explicitly in the current session, or
set the value in whatever config the agent reads at runtime.

**The code was never received.**
Wait up to 2 minutes: transactional email can be slow. Also ask the user to check their spam
folder. After the 60-second cooldown you can retry Step B-2, and a fresh email carries a fresh code.

**register-cli answers `501`.**
CLI signup is switched off on the server. Use the **Browser path** above. It always works.

**The verify step fails with `401`.**
The session token from registration expired (it lives as long as the code, about an hour) or got
mangled in transit. Start over from Step B-2.
"""


def frontmatter(slug, d, claw):
    emoji = d["clawmoji"] if claw else d["emoji"]
    meta = {
        "openclaw": {
            "emoji": emoji,
            "requires": {"env": ["TRANSCRIPTOUT_API_KEY"]},
            "primaryEnv": "TRANSCRIPTOUT_API_KEY",
            "homepage": "https://transcriptout.com",
        },
        "hermes": {"tags": d["tags"], "category": "media"},
    }
    return "\n".join([
        "---",
        f"name: {slug}",
        f'description: "{d["description"]}"',
        'version: "1.0.0"',
        "user-invocable: true",
        "compatibility: Requires internet access to reach api.transcriptout.com. No additional runtimes or dependencies needed.",
        "required_environment_variables:",
        "  - name: TRANSCRIPTOUT_API_KEY",
        "    prompt: Your TranscriptOut API key (starts with sk_)",
        "    help: Free account at https://transcriptout.com (100 credits on signup, no card). Create the key in the dashboard.",
        "    required_for: all API requests",
        f"metadata: {json.dumps(meta, separators=(',', ':'), ensure_ascii=False)}",
        "---",
    ])


def build_skill_md(slug, d, style, claw):
    parts = [frontmatter(slug, d, claw), "", f"# {d['title']}", "", d["intro"], ""]
    body = []
    for fn in d["sections"]:
        body.append(fn(style))
    if not claw:
        body.append(sec_curl_pointer(style))
    parts.append("\n\n".join(body))
    return "\n".join(parts) + "\n"


def build_curl_examples(slug, d):
    """The bash renderings of every request-bearing section in this skill."""
    chunks = [
        "# Copy-paste request examples",
        "",
        "The exact requests from SKILL.md as runnable one-liners. Same endpoints, same "
        "parameters, same header.",
        "",
    ]
    for fn in d["sections"]:
        text = fn("bash")
        if "```bash" not in text:
            continue
        chunks.append(text)
        chunks.append("")
    return "\n".join(chunks).rstrip() + "\n"


def main():
    for sub in ("skills", "clawhub"):
        path = os.path.join(ROOT, sub)
        if os.path.isdir(path):
            shutil.rmtree(path)
    for slug, d in SKILLS.items():
        for sub, style, claw in (("skills", "http", False), ("clawhub", "bash", True)):
            base = os.path.join(ROOT, sub, slug)
            os.makedirs(os.path.join(base, "references"), exist_ok=True)
            with open(os.path.join(base, "SKILL.md"), "w") as f:
                f.write(build_skill_md(slug, d, style, claw))
            with open(os.path.join(base, "references", "auth-setup.md"), "w") as f:
                f.write(AUTH_SETUP)
            if not claw:
                with open(os.path.join(base, "references", "curl-examples.md"), "w") as f:
                    f.write(build_curl_examples(slug, d))
    print("generated", len(SKILLS), "skills into skills/ and clawhub/")


if __name__ == "__main__":
    main()
