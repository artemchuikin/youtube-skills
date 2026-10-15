# Copy-paste request examples

The exact requests from SKILL.md as runnable one-liners. Same endpoints, same parameters, same header.

## GET /v1/playlist/videos · 1 credit/page

Every video of a playlist, in playlist order.

```bash
# First page (100 videos)
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-playlist"

# Next pages
curl -s "https://api.transcriptout.com/v1/playlist/videos?next_page_token=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-playlist"

# IDs only, 500 per page (feed these into the bulk job)
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID_OR_URL&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-playlist"
```

`id` accepts a `PL...` playlist ID or any URL with `list=`. `limit` goes up to 100, or up to 500 with `ids_only=true`. The response carries `playlist`, `title`, `count`, `videos[]` (or `video_ids[]`), `next_page_token` and `has_more`.

## GET /v1/playlist/search · 1 credit

Find videos inside a playlist by a substring of the title (case-insensitive). YouTube has no native playlist search, so this scans up to 500 playlist items.

```bash
curl -s "https://api.transcriptout.com/v1/playlist/search?id=PL_ID_OR_URL&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-playlist"
```

`truncated: true` in the response means the scan window ended before the playlist did, so there may be more matches.

## Workflow: Playlist → Transcripts

For a whole course or series, do not loop single transcript calls: collect the IDs and submit ONE asynchronous job (1 credit per video, up to 4,000).

```bash
# 1. Collect the playlist's IDs
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PL_ID&ids_only=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-playlist"

# 2. One bulk job for every video
curl -s -X POST "https://api.transcriptout.com/v1/transcripts" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-playlist" \
  -H "Content-Type: application/json" \
  -d '{"videos":["ID1","ID2","..."],"format":"text"}'

# 3. Progress and results
curl -s "https://api.transcriptout.com/v1/transcripts/JOB_ID" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY" \
  -H "X-Client: youtube-skills/youtube-playlist"
```
