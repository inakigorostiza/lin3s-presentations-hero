# Slide Taxonomy

Each numbered "source slide" below is a slide that lives inside the LIN3S template (visible in `unpacked/ppt/slides/` after unpacking). When you duplicate a slide for the deck, you're duplicating one of these source slides. This reference tells you which source slide fits which content type.

## Source slide directory

| Source slide | Layout | Best for |
|---|---|---|
| `slide1` | Dark title slide with portrait background image and topic callouts | Cover / Title slide (always exactly one per deck) |
| `slide6` | Index/Agenda with title left + 6 numbered slots right | Agenda (always exactly one per deck) |
| `slide10` | Quote slide with a sneaker image in the middle | Big-statement quote, Decision Rule, problem/solution comparison (after removing image and adding cards via `problem_solution_cards()`) |
| `slide11` | 3-column body with **bold header per column** | 3-way comparison where each column needs a clear name (e.g. "General purpose / Explore / Plan") |
| `slide13` | 3-column body with **small intro column left + 2 wider content columns right** | A framing statement + two parallel elaborations (e.g. "Choose based on X. Sub-option A handles… / Sub-option B handles…") |
| `slide14` | Text body on left + picture placeholder on right (5:4 ratio) | Title + 2-paragraph explanation alongside a supporting image or right-side code block |
| `slide15` | Simple text body left + small picture placeholder right | Simpler title + 2-paragraph explanation; works for definitions, limitations, or full-width text (remove the picture) |
| `slide16` | Section divider: image left + dark right panel with section title and `01 ― 04` indicator | Every section divider in the deck |
| `slide17` | Title + picture placeholder + body text (different proportions to slide14) | Wide diagrams or images that need more horizontal room |
| `slide47` | Dark "Thank You" closer with topic callouts and link/contact list | Final slide (always exactly one per deck) |

## How many duplicates do I need?

After planning your deck (Step 2 of the workflow), count how many slides of each type you have. Then:

```
duplicates_needed = uses_in_deck - 1
```

Because the original source slide is already there. So if your deck uses `slide11` (3-col-with-headers) four times, you need to duplicate it 3 times.

### Example calculation

For a 23-slide Agent Teams deck with 5 sections:

| Source slide | Uses | Duplicates |
|---|---|---|
| `slide1` Title | 1 | 0 |
| `slide6` Agenda | 1 | 0 |
| `slide16` Section divider | 5 | 4 |
| `slide14` Image+text | 3 | 2 |
| `slide15` Simple text | 2 | 1 |
| `slide13` 3-col body | 4 | 3 |
| `slide11` 3-col headers | 6 | 5 |
| `slide10` Quote | 1 | 0 |
| `slide47` Thank You | 1 | 0 |
| **Total slides** | **24** | **15 duplicates** |

## Duplication mechanics

Use the `add_slide.py` helper for each duplicate:

```bash
python /mnt/skills/public/pptx/scripts/add_slide.py /home/claude/unpacked/ slide16.xml
```

It reports back the new filename and `rId` for each duplicate. Capture those — you'll need them when rebuilding `sldIdLst` in Step 5.

## How source slides map to common content patterns

When you're planning what goes on each slide, this is the mental model:

- **Multi-step process or workflow with named stages** → `slide11` (3-col headers). Each column header names a stage, the body explains.
- **Comparison table** (subagents vs agent teams, before vs after) → `slide13` if there's a framing question to introduce, or two columns of `slide11` if not.
- **Definition / opening explanation for a section** → `slide15` (remove picture for full-width text) or `slide14` if you have a supporting image.
- **Code example, command sequence, or configuration block** → `slide14` (remove picture, replace with `codebox()` on the right side).
- **Diagram, screenshot, or illustration paired with text** → `slide14` (or `slide17` for wide diagrams) with `fix_image()` applied.
- **Big quote, principle, or rule** → `slide10`. If the slide feels empty after removing the original image, use `problem_solution_cards()` to fill it.
- **Decision rule with two outcomes** → `slide10` + `problem_solution_cards()` for a YES/NO or Do/Don't comparison.
- **Section transition** → `slide16` duplicate.

## What about long lists?

The template doesn't have a "bulleted list" layout. For a list of 4+ items, choose:

1. **If the items are roughly equal weight and 3-5 in count**: use `slide11` (3 columns) or `slide13` (intro + 2 columns) and group items if you have more than fit cleanly.
2. **If the items are 6+ in count**: consider splitting across two slides, or moving the content to two of `slide13`'s columns as bullet-style paragraphs (the body cells accept multi-line content).
3. **If you really need a one-shot list**: build a single text shape from scratch on a duplicated `slide15` and remove the picture. This is more XML work — only do it when the other options actually don't fit.

The template's strength is comparison and structure, not enumeration. Lean into that.
