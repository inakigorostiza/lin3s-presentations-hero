---
name: lin3s-presentations-hero
description: Build polished PowerPoint presentations from .docx or .pdf source documents using the LIN3S Design Week 2020 template. Use this skill whenever the user wants to turn a document into a slide deck, create a .pptx from written content, or asks to make a presentation from a report, article, course material, training content, or technical documentation. Trigger even if they say "turn this doc into slides", "make a deck from this", or just upload a .docx/.pdf alongside a presentation request. Handles template setup, slide layout selection, image swapping, code-block formatting, section dividers, and visual QA end to end. Output is a professionally-formatted .pptx the user can open directly in PowerPoint or import into Google Slides.
---

# LIN3S Presentations Hero

Turn a source document into a polished slide deck built on the LIN3S Design Week 2020 template. Output is a real `.pptx` file dropped in `/mnt/user-data/outputs/`, ready for the user to open in PowerPoint or import slide-by-slide into Google Slides.

## When to use this skill

The user has a `.docx` or `.pdf` (or sometimes raw text) and wants slides out of it. Common cues: "make a presentation from this", "turn this into a deck", "create slides for the attached doc", or simply uploading a document alongside a request like "I want to teach this material". Use this skill for any deck built on the LIN3S template — including educational content, technical guides, reports, training materials.

## Working directory and assets

Work in `/home/claude/`. The template lives at `assets/LIN3S_TEMPLATE.pptx` relative to this skill folder. Always copy it to the working directory first — don't edit the asset.

```bash
cp <skill_path>/assets/LIN3S_TEMPLATE.pptx /home/claude/template.pptx
```

## End-to-end workflow

The workflow has nine steps. Each step has been validated across multiple deck builds. Don't skip steps — they're ordered for a reason.

### Step 1 — Read the source document

```bash
# For .docx files
extract-text /mnt/user-data/uploads/<file>.docx

# Unpack to inspect embedded images
python /mnt/skills/public/docx/scripts/office/unpack.py /mnt/user-data/uploads/<file>.docx /home/claude/source_unpacked/
ls /home/claude/source_unpacked/word/media/
```

For `.pdf` source documents, follow `references/pdf_source.md`.

Read every embedded image with the `view` tool before planning. Visual content drives slide structure as much as the text does.

### Step 2 — Plan the slide structure

A typical deck is **18–25 slides** organized around the source document's natural sections. Use this template as a starting point:

1. Title
2. Agenda
3. Section 1 divider
4. Content slides for section 1 (typically 2–4 slides)
5. Section 2 divider
6. ... etc
7. Optional: Key Takeaways or Decision Rule slide
8. Thank You

Map each content slide to a source template slide using `references/slide_taxonomy.md`. The taxonomy tells Claude which template slide handles which content type (3-column comparison, image+text, code block on right, quote, etc.).

**Section count handling.** The agenda template has exactly 6 numbered slots. For decks with more than 6 sections, combine related sections into one agenda slot but keep them as separate section dividers in the deck body. For fewer than 6 sections, leave trailing agenda slots empty.

### Step 3 — Unpack and apply pre-fixes

```bash
cp <skill_path>/assets/LIN3S_TEMPLATE.pptx /home/claude/template.pptx
python /mnt/skills/public/pptx/scripts/office/unpack.py /home/claude/template.pptx /home/claude/unpacked/
python <skill_path>/scripts/pre_fixes.py /home/claude/unpacked/
```

`pre_fixes.py` applies two changes that prevent visual issues later:
- `slideLayout30.xml`: changes the picture-area background from `F3F3F3` (grey) to `FFFFFF` (white). Prevents grey letterbox bands when swapping in non-5:4 images, and prevents a grey rectangle from showing when removing pictures entirely.
- Agenda title widening: the title shape on `slide6.xml` is sized tight to "Índice" (the original Spanish word). Wider words like "Agenda" overflow to two lines without this fix.

### Step 4 — Duplicate template slides

The template has one of each slide type. For a 20-slide deck, you'll need multiple copies of the same source slides. Use the `add_slide.py` helper:

```bash
python /mnt/skills/public/pptx/scripts/add_slide.py /home/claude/unpacked/ slide16.xml  # one duplicate
```

Count how many of each source slide type you need, then run the helper that many times. See `references/slide_taxonomy.md` for the count formula.

### Step 5 — Rebuild the slide order in presentation.xml

After duplicating, the new slides exist as files but aren't in the deck's slide order. Edit `ppt/presentation.xml` to replace the `<p:sldIdLst>` with the new order. Each slide gets:
- An `id` (any unique integer; the original template uses 256-301, and duplicates get auto-assigned 302+)
- An `r:id` (the relationship ID from `ppt/_rels/presentation.xml.rels`, which `add_slide.py` reports after each duplicate)

```python
new_lst = """  <p:sldIdLst>
    <p:sldId id="256" r:id="rId7"/>   <!-- slide1 Title -->
    <p:sldId id="261" r:id="rId12"/>  <!-- slide6 Agenda -->
    ... (etc, in the order they should appear)
  </p:sldIdLst>"""

import re
t = re.sub(r"  <p:sldIdLst>.*?</p:sldIdLst>", new_lst, t, count=1, flags=re.DOTALL)
```

### Step 6 — Copy images into the template's media folder

```bash
cp /home/claude/source_unpacked/word/media/image1.png /home/claude/unpacked/ppt/media/<descriptive_name>.png
```

Name images by what they show (`flow_diagram.png`, `claude_md_locations.png`), not by their source filename — it makes the edit code much more readable.

### Step 7 — Edit slides in batched Python scripts

**Do not edit slides with one-off `str_replace` calls.** That worked for the first deck but scales badly. Use the helpers in `scripts/helpers.py`:

- `edit_3col_headers(slide, title, headers, intros, details)` — slide11-style: 3 columns each with a bold header
- `edit_3col_body(slide, title, intro_a, intro_b, mid_a, mid_b, right_a, right_b)` — slide13-style: small intro left + 2 wider columns
- `fix_image(slide)` — strip `srcRect` and resize the picture placeholder to 16:9, centered. Apply to every slide where you swap in a docx image
- `remove_pic(slide)` — drop the picture element entirely (use when replacing with text or a code block)
- `codebox(x, y, cx, cy, lines, font_sz)` — build a light-grey code panel for right-side code blocks. Each line is `(text, is_bold)`
- `problem_solution_cards(slide)` — replace a slide10-style quote slide's empty middle with two contrasting cards (light grey "problem" / dark "solution")

Write all edits for the deck in a single Python script. Each helper takes a slide filename and updates the XML in place. Run the whole script once.

Reference `references/patterns.md` for content-layout pairings: which template slide best fits a 3-column comparison, a code example, a definition, a quote, etc.

### Step 8 — Clean, pack, render, QA

```bash
python /mnt/skills/public/pptx/scripts/clean.py /home/claude/unpacked/
python /mnt/skills/public/pptx/scripts/office/pack.py /home/claude/unpacked/ /home/claude/<DeckName>.pptx --original /home/claude/template.pptx

# Render to images for visual QA
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf /home/claude/<DeckName>.pptx
pdftoppm -jpeg -r 100 /home/claude/<DeckName>.pdf /home/claude/slide
```

Then `view` each generated `.jpg` and check for:
- Title overflow (wrapping mid-word, getting cut off)
- Grey rectangles where images were removed or letterboxed
- Image cropping cutting off labels or essential content
- Leftover template placeholder text (the verify script catches most of this — run it before packing)

```bash
python <skill_path>/scripts/verify.py /home/claude/unpacked/
```

### Step 9 — Deliver

Copy the final `.pptx` to outputs and call `present_files`:

```bash
cp /home/claude/<DeckName>.pptx /mnt/user-data/outputs/<DeckName>.pptx
```

Then `present_files` with the filepath.

Tell the user the deck can be imported into Google Slides via *File → Import slides → Upload → All slides*.

## Sub-references

The following files contain the depth Claude needs for specific situations. Read them when relevant — don't try to inline their contents.

- `references/slide_taxonomy.md` — Map of every source template slide (slide1, slide6, slide10, slide11, etc.) to the content type it handles best. Read before planning the deck.
- `references/patterns.md` — Reusable content/layout patterns: problem/solution cards, yes/no decision splits, 3-col comparisons, code-on-right, image+text. Read while editing slide XML.
- `references/pitfalls.md` — Known gotchas: smart-quote XML entities, duplicate placeholder text across multi-column layouts, srcRect crops on swapped images, footer mark on master slide. Read when something looks wrong in QA.
- `references/pdf_source.md` — How to extract text and images from `.pdf` source documents instead of `.docx`.

## Hard-won lessons distilled

These are the things that will save the most time across builds:

1. **One Python script per deck, not many `str_replace` calls.** Compose all edits in one file, run once. Edit failures become loud and locatable.
2. **Apply pre-fixes at unpack time, not after rendering.** The layout30 grey fix and agenda title widening are deterministic — do them up front and the first render is correct.
3. **Read all source images before planning slides.** Visual content is often as important as the text for deciding section structure.
4. **Use the helpers, even for "simple" edits.** Reaching for raw XML in the middle of a script always costs more time than expected. If something isn't covered by a helper, add one rather than going freestyle.
5. **Visual QA matters.** Render to PDF, then JPEG, then `view`. Some issues (image cropping, title wrapping, dark-on-dark text) only show up visually.
6. **Smart quotes are XML entities.** `unpack.py` converts `'` to `&#x2019;` on disk. All replacements must use the entity form, not raw Unicode.
