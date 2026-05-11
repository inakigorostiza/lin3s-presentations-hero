# Installation

## What you need

- A Claude environment that supports skills (Claude.ai with skills enabled, Claude Code, or any API client that loads skill folders)
- About 11 MB of disk space (mostly for the LIN3S template asset)

## Option 1: Install the packaged `.skill` file (easiest)

1. Go to the [Releases page](../../releases) and download the most recent `lin3s-presentations-hero.skill` file.
2. In your Claude environment, add the skill:
   - **Claude.ai** — open Settings → Capabilities → Skills → Upload skill. Select the `.skill` file.
   - **Claude Code** — copy the `.skill` file into your skills directory (typically `~/.claude/skills/`), or use whatever installation flow your Claude Code version provides.
   - **Claude API / SDK** — unzip the `.skill` file (it's a regular zip archive) and load the resulting folder via your skill-loading mechanism.
3. Open a new Claude conversation. Ask Claude to turn a document into a presentation. The skill should auto-trigger.

## Option 2: Install from source

1. Clone this repository:
   ```bash
   git clone https://github.com/USER/lin3s-presentations-hero.git
   cd lin3s-presentations-hero
   ```
2. Either:
   - Point your Claude environment directly at the `skill/` folder, or
   - Run `bash scripts/build.sh` to produce a fresh `.skill` file you can install via Option 1.

## Verify it works

After installation, start a new Claude conversation. Upload any short `.docx` or `.pdf` document and ask:

> Turn this document into a slide deck.

Claude should:
1. Read your document
2. Plan a slide structure (asking clarifying questions if the structure is ambiguous)
3. Build the deck using the LIN3S template
4. Hand you a `.pptx` file

If Claude doesn't reach for the skill, prompt more directly:

> Use the LIN3S Presentations Hero skill to make a slide deck from this document.

## Troubleshooting

**The skill isn't triggering.** Check that the skill is listed in Claude's available skills. If it is, your prompt may not be matching the trigger description — try a more direct phrasing like "make slides from this document" or naming the skill explicitly.

**Claude builds slides but they don't look like the LIN3S template.** The template asset may not have unpacked correctly. Verify `skill/assets/LIN3S_TEMPLATE.pptx` exists and is around 10 MB in size.

**Something else goes wrong during the build.** Open an issue with:
- Your input document (or a description of it)
- The exact prompt you used
- What Claude did vs. what you expected
- Any error messages

## Using your own template

The skill is wired to the specific shape coordinates and placeholder text of the LIN3S Design Week 2020 template. To adapt it to a different template:

1. Replace `skill/assets/LIN3S_TEMPLATE.pptx` with your template
2. Re-derive the placeholder strings in `skill/scripts/helpers.py` (the `LONG_INTRO`, `LONG_TRUCK_*`, `HEADER_OLD`, etc. constants) from your template's stock content
3. Update `skill/references/slide_taxonomy.md` to reflect your template's slide layouts
4. Update the pre-fixes in `skill/scripts/pre_fixes.py` for any layout-specific issues in your template

This is more work than installation, but the structure is reusable.
