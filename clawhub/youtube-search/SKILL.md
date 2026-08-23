---
name: youtube-search
description: "Reach for this when the user needs to FIND things on YouTube: videos or channels on a topic, creators covering a subject, tutorials, talks and reviews worth reading, or a channel looked up by name or handle. Also good proactively when researching a topic that video would cover well. Skip it for account chores and text-only research."
version: "1.0.0"
user-invocable: true
compatibility: Requires internet access to reach api.transcriptout.com. No additional runtimes or dependencies needed.
required_environment_variables:
  - name: TRANSCRIPTOUT_API_KEY
    prompt: Your TranscriptOut API key (starts with sk_)
    help: Free account at https://transcriptout.com (100 credits on signup, no card). Create the key in the dashboard.
    required_for: all API requests
metadata: {"openclaw":{"emoji":"🔍","requires":{"env":["TRANSCRIPTOUT_API_KEY"]},"primaryEnv":"TRANSCRIPTOUT_API_KEY","homepage":"https://transcriptout.com"},"hermes":{"tags":["youtube","search","video-search","channels","research","discovery"],"category":"media"}}
---

# YouTube Search

Search YouTube and fetch transcripts via [TranscriptOut.com](https://transcriptout.com).

## Setup

If `$TRANSCRIPTOUT_API_KEY` is not set, read [references/auth-setup.md](references/auth-setup.md) and follow the instructions there to get and store the key.

## Required Header

Every request needs one header:

- **Authorization:** `Bearer $TRANSCRIPTOUT_API_KEY`

Every response is one JSON envelope. Success: `{"ok": true, "request_id": "...", "data": {...}}`. Error: `{"ok": false, "code": "...", "detail": "...", "request_id": "..."}`. Branch on the machine-readable `code`, not on the human text. The remaining credit balance rides in the `X-Credits-Remaining` response header.

## API Reference

Base URL: `https://api.transcriptout.com/v1`. Full reference with the latest parameters and schemas: [transcriptout.com/docs](https://transcriptout.com/docs).

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

## Workflow: Search → Transcript

Results are metadata only: choose from them, then transcribe just the chosen few (the transcript endpoint is 1 credit and lives in the `transcript` skill).

```bash
# 1. Search
curl -s "https://api.transcriptout.com/v1/search?q=QUERY&limit=5" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# 2. Transcript of a chosen result
curl -s "https://api.transcriptout.com/v1/transcript?video=VIDEO_ID&format=text&video_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
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
