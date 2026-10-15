# Copy-paste request examples

The exact requests from SKILL.md as runnable one-liners. Same endpoints, same parameters, same header.

## GET /v1/channel/latest · 1 credit

The ~15 most recent videos of a channel, served from its RSS feed: the fastest and cheapest way to check what a creator published recently.

```bash
curl -s "https://api.transcriptout.com/v1/channel/latest?name=@kurzgesagt" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-channels"
```

`name` accepts an `@handle`, a channel name, a `UC...` channel ID or a channel URL. No resolve step needed: pass the handle directly.

## GET /v1/channel/videos · 1 credit/page

Every video from a channel's Videos tab, newest first.

```bash
# First page (100 videos)
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-channels"

# Next pages
curl -s "https://api.transcriptout.com/v1/channel/videos?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-channels"

# IDs only, 500 per page (feed these into the bulk job)
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-channels"
```

Provide `name` on the first call and only `next_page_token` afterwards. `limit` goes up to 100, or up to 500 with `ids_only=true` (the response is then `video_ids[]` instead of full video objects). The response carries `next_page_token` and `has_more`.

## GET /v1/channel/search · 1 credit/page

Search inside one channel using YouTube's native relevance search. A result whose title lacks the query word is normal: it is relevance, not substring match.

```bash
curl -s "https://api.transcriptout.com/v1/channel/search?name=@kurzgesagt&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-channels"
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
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-channels"

# Whole catalogue as IDs when bulk work follows
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@handle&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-channels"
```
