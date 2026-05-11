# Known Pitfalls

Every gotcha encountered across the four decks built so far, with the diagnostic and fix for each. Read this when something looks wrong in visual QA.

## Smart quotes don't match

**Symptom:** `text.replace()` calls for paragraphs containing `'`, `'`, `"`, `"`, `—`, or `–` don't match the on-disk content. The replacement silently does nothing.

**Cause:** `unpack.py` converts smart quotes to XML entity form (`&#x2019;` etc.) when it writes slide XML to disk. If your Python source code contains raw Unicode `'`, the string literal you're searching for doesn't match what's actually in the file.

**Fix:** Use entity form in all replacement search strings, or run user-facing content strings through `helpers.smart_quote_entities()` before splicing them into slide XML.

```python
# WRONG — won't match
text.replace("It's a thing", "It's another thing")

# RIGHT
text.replace("It&#x2019;s a thing", "It&#x2019;s another thing")
```

The most common entities to remember:
- `'` → `&#x2018;`
- `'` → `&#x2019;`
- `"` → `&#x201C;`
- `"` → `&#x201D;`
- `—` (em dash) → `&#x2014;`
- `–` (en dash) → `&#x2013;`
- `―` (horizontal bar, used in section indicators like `01 ― 04`) → `&#x2015;`

## Duplicate placeholder text across columns

**Symptom:** Replacing a paragraph in a 3-column slide accidentally hits the wrong column. Or only one of three columns gets updated when you wanted all three.

**Cause:** `slide11` and `slide13` contain the **exact same** placeholder paragraphs in all 3 columns. There are 3 instances of "I want to talk about to things..." and 3 instances of "I have a truck..." in the same slide file.

**Fix:** Always use `count=1` and call `.replace()` once per column in left-to-right order. The helpers in `helpers.py` handle this correctly:

```python
# WRONG — replaces all 3 occurrences with the same text
text = text.replace(LONG_INTRO, "<a:t>New text for column A</a:t>")

# RIGHT — sequential left-to-right replacement
text = text.replace(LONG_INTRO, "<a:t>Column A text</a:t>", 1)
text = text.replace(LONG_INTRO, "<a:t>Column B text</a:t>", 1)
text = text.replace(LONG_INTRO, "<a:t>Column C text</a:t>", 1)
```

## The truck paragraph has two variants

**Symptom:** Your 3-col edit script replaces the first occurrence fine, then fails to find the second or third.

**Cause:** The "I have a truck..." paragraph exists in two forms in `slide11`:
- The **first** occurrence ends with `...keep my truck).</a:t>` (no trailing space before `</a:t>`)
- The **second and third** occurrences end with `...keep my truck). </a:t>` (one trailing space)

**Fix:** `helpers.py` exports both as `LONG_TRUCK_NS` (no space) and `LONG_TRUCK_SP` (with space). The `edit_3col_headers` helper uses the right one in the right position automatically. If you're doing custom edits, mirror that pattern.

## Image cropping cuts off content

**Symptom:** Swapping a docx image into a `slide14` picture placeholder produces an image with content cut off at top/bottom edges, or labels missing on the sides.

**Cause:** The template's `<a:srcRect>` element applies a fixed crop tuned for the original placeholder image (a watch product photo with lots of background). Swapping in a 16:9 docx image with a tight composition makes the crop cut off real content.

**Fix:** Always call `fix_image(slide_name)` after `edit_rels()` for any slide where you swapped in an image. It strips the `srcRect` and resizes the picture placeholder to 16:9 centered.

```python
edit_rels("slide14", "image16.jpg", "my_diagram.png")
fix_image("slide14")  # ← Don't forget this
```

## Grey letterbox bands around images

**Symptom:** After swapping in a 16:9 image, visible grey bands appear above and below the image.

**Cause:** `slideLayout30.xml` has an `F3F3F3` (light grey) fill on the picture-area background rectangle. When the image is resized to 16:9 inside a 5:4 placeholder, the grey background shows in the letterbox area.

**Fix:** Run `pre_fixes.py` on the unpacked deck right after unpacking. It changes the grey fill to white, which blends with the slide background.

```bash
python scripts/pre_fixes.py /home/claude/unpacked/
```

If you forget this and only discover the issue during QA: edit `slideLayout30.xml` directly to swap `F3F3F3` for `FFFFFF`, then repack. The fix is non-destructive — only one shape changes color.

## Empty grey rectangle on a "no image" slide

**Symptom:** You used `remove_pic()` to take an image off a `slide14` or `slide15`, but a grey rectangle still shows where the image used to be.

**Cause:** Same as above — the layout's grey background rectangle is still painted.

**Fix:** Same as above — run `pre_fixes.py` (or change `F3F3F3` to `FFFFFF` in `slideLayout30.xml`).

## Agenda title wraps to two lines

**Symptom:** The "Agenda" text on `slide6` breaks to two lines like `Agend / a`.

**Cause:** The title shape is sized tight to the original Spanish word "Índice" (which has a narrow `Í`). Wider 6+ character words like "Agenda" don't fit.

**Fix:** `pre_fixes.py` widens the title shape from `cx=2304300` to `cx=3200000` and reduces the font from 48pt to 40pt. Run it before editing the agenda text.

## Title overflow on short titles

**Symptom:** Other slide titles also wrap when the new title is wider than the original placeholder text.

**Cause:** Some slide titles are sized just barely wide enough for the original placeholder text. Most are forgiving, but unusually wide replacement titles can overflow.

**Diagnostic:** Render the slide and `view` the JPEG. If the title wraps where it shouldn't, find the title shape's `<a:xfrm>` in the slide XML and widen the `cx` value.

**Fix:** Increase the title's `cx` (width) by 1-2 million EMU, or reduce the font `sz`. Both are cheap.

## Footer brand mark on every slide

**Observation:** The "LIN3S" wordmark appears in the bottom-left of every content slide. This comes from the slide master, not the individual slides.

**Why:** It's part of the LIN3S Design Week 2020 template branding.

**To remove for non-LIN3S decks:** Edit `ppt/slideMasters/slideMaster1.xml` and remove the shape containing the "LIN3S" text. This affects every slide that uses the master, so do it once at unpack time.

```python
# Quick check: search the master for the LIN3S text shape
grep -n "LIN3S" /home/claude/unpacked/ppt/slideMasters/slideMaster1.xml
```

## Slide order doesn't reflect duplicated slides

**Symptom:** You duplicated several slides with `add_slide.py`, but the final deck only shows the original slides — the duplicates don't appear.

**Cause:** `add_slide.py` creates the new slide file and adds it to the relationships, but doesn't update `ppt/presentation.xml`'s `<p:sldIdLst>` element. The deck still uses the original slide order until you rebuild it.

**Fix:** After all duplications, manually rebuild the `sldIdLst` element in `presentation.xml`. Each duplicate reports its `rId` after creation — capture all of those and assemble the new list in the deck order you want.

```python
new_lst = """  <p:sldIdLst>
    <p:sldId id="256" r:id="rId7"/>    <!-- slide1 Title -->
    <p:sldId id="261" r:id="rId12"/>   <!-- slide6 Agenda -->
    <p:sldId id="271" r:id="rId22"/>   <!-- slide16 Section 1 divider -->
    <p:sldId id="303" r:id="rId58"/>   <!-- slide48 Section 2 divider (duplicate) -->
    ...
  </p:sldIdLst>"""

import re
text = re.sub(r"  <p:sldIdLst>.*?</p:sldIdLst>", new_lst, text, count=1, flags=re.DOTALL)
```

The `id` values just need to be unique integers (256-301 are used by the original template; pick 302+ for duplicates).

## "Slide order" but slides are in directory

**Symptom:** Final deck still shows the 47 original template slides plus your duplicates — way more than you wanted.

**Cause:** The unused source slides aren't in your final `sldIdLst` but their `.xml` files are still in the directory. `pack.py` packages them but PowerPoint shouldn't display them. Verify your `sldIdLst` only contains the slides you actually want shown.

**Defensive measure:** Run `clean.py` after editing but before packing — it removes orphaned slides and unreferenced media:

```bash
python /mnt/skills/public/pptx/scripts/clean.py /home/claude/unpacked/
```

## Trailing whitespace causes pack repair

**Symptom:** `pack.py` reports messages like "Auto-repaired: Added xml:space='preserve' to a:t: 'something '".

**Cause:** Text with leading/trailing whitespace inside `<a:t>` elements needs `xml:space="preserve"` to render correctly.

**Fix:** This is auto-repaired by `pack.py` — it's a notification, not an error. Safe to ignore unless you see "VALIDATION FAILED" messages alongside.

## A slide goes blank when packed

**Symptom:** A slide that looked fine in the unpacked XML renders as blank or partial in the final `.pptx`.

**Cause:** Usually malformed XML — an unclosed tag, a mismatched namespace prefix, or a string literal that didn't get its smart quotes converted.

**Diagnostic:** Open the slide's XML and look for unmatched brackets, unclosed tags, or `'` characters in `<a:t>` content (they should be `&#x2019;`).

**Fix:** Repair the XML and repack. The `pack.py` validation step catches most malformed XML — if it passes validation but the rendered output is broken, the issue is usually content, not structure.

## Quick QA checklist

After packing and before delivery, run this mental checklist:

- [ ] Title slide shows correct text, no original "Myspace" content
- [ ] Agenda title fits on one line (no `Agend / a` wrap)
- [ ] Every section divider has the right `NN ― TT` indicator
- [ ] Section divider titles fit on one or two lines (not three)
- [ ] All swapped images display fully (no cropping of labels or content)
- [ ] No grey rectangles where images were removed
- [ ] Code blocks fit inside the right-side panel without line-wrapping mid-token
- [ ] Footer text reads correctly on every slide (your deck title, not "Myspace")
- [ ] Thank You slide shows your contact/resource links, not LIN3S originals
- [ ] `verify.py` reports CLEAN

If all 10 pass, the deck is ready to ship.
