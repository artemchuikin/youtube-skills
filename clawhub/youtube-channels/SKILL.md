---
name: youtube-channels
description: "Reach for this when a YouTube channel is the subject: a pasted @handle or channel URL, a creator's recent uploads, their full catalogue, or a search inside one channel. Also good for keeping an eye on what somebody publishes. Skip it for creating channels or account chores."
version: "1.0.0"
user-invocable: true
compatibility: Requires internet access to reach api.transcriptout.com. No additional runtimes or dependencies needed.
required_environment_variables:
  - name: TRANSCRIPTOUT_API_KEY
    prompt: Your TranscriptOut API key (starts with sk_)
    help: Free account at https://transcriptout.com (100 credits on signup, no card). Create the key in the dashboard.
    required_for: all API requests
metadata: {"openclaw":{"emoji":"📡","requires":{"env":["TRANSCRIPTOUT_API_KEY"]},"primaryEnv":"TRANSCRIPTOUT_API_KEY","homepage":"https://transcriptout.com"},"hermes":{"tags":["youtube","channels","creators","uploads","monitoring","handles"],"category":"media"}}
---

# YouTube Channels

YouTube channel tools via [TranscriptOut.com](https://transcriptout.com).

## Setup

If `$TRANSCRIPTOUT_API_KEY` is not set, read [references/auth-setup.md](references/auth-setup.md) and follow the instructions there to get and store the key.

## Required Header

Every request needs one header:

- **Authorization:** `Bearer $TRANSCRIPTOUT_API_KEY`

Every response is one JSON envelope. Success: `{"ok": true, "request_id": "...", "data": {...}}`. Error: `{"ok": false, "code": "...", "detail": "...", "request_id": "..."}`. Branch on the machine-readable `code`, not on the human text. The remaining credit balance rides in the `X-Credits-Remaining` response header.

## API Reference

Base URL: `https://api.transcriptout.com/v1`. Full reference with the latest parameters and schemas: [transcriptout.com/docs](https://transcriptout.com/docs).

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

## Typical workflow

Start with `channel/latest` when recent uploads are enough. `channel/videos` is for genuine catalogue work.

```bash
# Cheapest first: what did they post lately?
curl -s "https://api.transcriptout.com/v1/channel/latest?name=@handle" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Whole catalogue as IDs when bulk work follows
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@handle&ids_only=true" \
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
