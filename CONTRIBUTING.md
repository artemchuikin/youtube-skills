# Contributing

PRs welcome! Here's what helps:

## Adding a New Skill

The skill files are GENERATED: every `SKILL.md`, `auth-setup.md` and `curl-examples.md` comes out
of `scripts/generate.py`, so the endpoints and error tables cannot drift apart between variants.

1. Add the skill definition (name, description, emoji, section list) to `SKILLS` in
   `scripts/generate.py`
2. Run `python3 scripts/generate.py`
3. Submit a PR with both the script change and the regenerated files

Never hand-edit files under `skills/` or `clawhub/`; the next generator run would overwrite them.

## Improving Existing Skills

- Better trigger phrases in descriptions
- Clearer examples
- Fixes to endpoint parameters (check them against [transcriptout.com/docs](https://transcriptout.com/docs))

## Quality Checklist

- [ ] SKILL.md has proper frontmatter
- [ ] Description includes when-to-use phrases
- [ ] references/auth-setup.md is present
- [ ] Tested with `npx skills add` locally

## Questions?

Open an issue or reach out at [transcriptout.com](https://transcriptout.com).
