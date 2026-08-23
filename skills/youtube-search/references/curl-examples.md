# Copy-paste request examples

The exact requests from SKILL.md as runnable one-liners. Same endpoints, same parameters, same header.

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
