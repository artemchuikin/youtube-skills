# Copy-paste request examples

The exact requests from SKILL.md as runnable one-liners. Same endpoints, same parameters, same header.

## Quick Examples

```bash
# A transcript with metadata
curl -s "https://api.transcriptout.com/v1/transcript?video=dQw4w9WgXcQ&format=text&video_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# Search
curl -s "https://api.transcriptout.com/v1/search?q=rust+lifetimes&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# A channel's uploads
curl -s "https://api.transcriptout.com/v1/channel/videos?name=@3blue1brown" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"

# A playlist
curl -s "https://api.transcriptout.com/v1/playlist/videos?id=PLAYLIST_URL" \
  -H "Authorization: Bearer $TRANSCRIPTOUT_API_KEY"
```
