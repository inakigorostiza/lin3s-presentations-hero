# Content Patterns

Concrete recipes for the most common content layouts. Each pattern shows what it looks like, when to use it, and the exact helper call.

## Pattern 1: Title slide

**When:** Always the first slide of the deck.
**Source:** `slide1` (do not duplicate; use the original).
**Recipe:**

```python
text = read("slide1")
# The original "An Ugly Myspace Profile Will Sure Ruin Your Reputation" title
# is split across multiple <a:r> runs. Replace the first run group with your
# title and clear the rest:
text = text.replace(
    '<a:r>\n              <a:rPr lang="en"/>\n              <a:t>A</a:t>\n            </a:r>\n            <a:r>\n              <a:rPr lang="en"/>\n              <a:t>n Ugly Myspace </a:t>\n            </a:r>',
    '<a:r>\n              <a:rPr lang="en"/>\n              <a:t>Your Title</a:t>\n            </a:r>', 1)
text = text.replace('<a:t>Profile Will Sure Ruin Your Reputation</a:t>', '<a:t>Subline</a:t>', 1)
text = text.replace('<a:t>Design Week 2020</a:t>', '<a:t>Your Brand Line</a:t>', 1)
text = text.replace('<a:t>Paula Soto</a:t>', '<a:t>Topic A</a:t>', 1)
text = text.replace('<a:t>Ainize Medrano</a:t>', '<a:t>Topic B</a:t>', 1)
text = text.replace('<a:t>Title</a:t>', '<a:t>Subtitle line under the title</a:t>', 1)
text = text.replace('<a:t>Speakers</a:t>', '<a:t>Topics</a:t>', 1)
write("slide1", text)
```

## Pattern 2: Agenda slide

**When:** Always the second slide of the deck.
**Source:** `slide6` (do not duplicate).
**Recipe:**

```python
text = read("slide6")
text = text.replace(FOOTER_OLD, footer_new, 1)
text = text.replace("<a:t>An Ugly Myspace Profile Will Sure Ruin Your Reputation.</a:t>",
                    f"<a:t>{deck_title}.</a:t>", 1)
text = text.replace("<a:t>Introduction</a:t>", "<a:t>Section 1 Title</a:t>", 1)
text = text.replace("<a:t>Our award winning analytic process</a:t>", "<a:t>Section 2 Title</a:t>", 1)
text = text.replace("<a:t>A sprint based methodology</a:t>", "<a:t>Section 3 Title</a:t>", 1)
text = text.replace("<a:t>How to transform </a:t>", "<a:t>Section 4 Title </a:t>", 1)
text = text.replace("<a:t>your business</a:t>", "<a:t>(continued)</a:t>", 1)
text = text.replace("<a:t>Final thoughts and considerations</a:t>", "<a:t>Section 5 Title</a:t>", 1)
text = text.replace("<a:t>Q&amp;A Session with </a:t>", "<a:t>Section 6 Title</a:t>", 1)
text = text.replace("<a:t>John Pax</a:t>", "<a:t></a:t>", 1)
write("slide6", text)
```

The 4th agenda item is split across two `<a:t>` elements ("How to transform" + "your business"). To put a longer section title in slot 4, use both replacements together; for a shorter title, clear the second one with `<a:t></a:t>`.

If your deck has more than 6 sections, combine related sections into a single agenda slot but keep them as separate section dividers later in the deck.

## Pattern 3: Section divider

**When:** Between major sections of the deck.
**Source:** `slide16` (duplicate as `slide48`, `slide49`, etc.)
**Recipe:**

```python
for slide_name, title, indicator in [
    ("slide16", "What Are Agent Teams?", "01 \u2015 05"),  # \u2015 is the ―
    ("slide48", "Setting Up Your First Team", "02 \u2015 05"),
    ...
]:
    text = read(slide_name)
    text = text.replace("<a:t>Effective Forms Advertising</a:t>", f"<a:t>{title}</a:t>", 1)
    text = text.replace("<a:t>04 \u2015 06</a:t>", f"<a:t>{indicator}</a:t>", 1)
    text = text.replace(FOOTER_OLD, footer_new, 1)
    write(slide_name, text)
```

The horizontal-bar character `―` is `\u2015` in Python source and `&#x2015;` in the on-disk XML. Both work when passed through `.replace()` because Python encodes the source as the entity-rendered byte stream.

## Pattern 4: Image-on-right + 2 paragraphs

**When:** Definition slides, conceptual explanations with a supporting visual.
**Source:** `slide14` (or duplicate).
**Recipe:**

```python
edit_rels("slide14", "image16.jpg", "your_image.png")
fix_image("slide14")  # strips srcRect, resizes to 16:9 centered
text = read("slide14")
text = text.replace("<a:t>Effective Forms Advertising</a:t>", "<a:t>Slide Title</a:t>", 1)
text = text.replace(FOOTER_OLD, footer_new, 1)
text = text.replace(
    "<a:t>Freelance Design Tricks How To Get Away With Murder In The Workplace</a:t>",
    "<a:t>Subtitle (bold)</a:t>", 1)
text = text.replace(
    "<a:t>Generated effective advertising campaigns in the form of audio visual media that includes the television and radios and the print media that cover the newspaper and campaign materials like the posters, brochures, business cards, flyers and many more.</a:t>",
    "<a:t>First paragraph text.</a:t>", 1)
text = text.replace(
    "<a:t>Taking part with the flyers \u2013 they are tiny form or a single sheet promotional tool that easily spreads by hand. They are simply characterized as a simple yet compelling promotional material that helps businesses to easily reach out for their targeted audience. </a:t>",
    "<a:t>Second paragraph text.</a:t>", 1)
write("slide14", text)
```

## Pattern 5: Code block on right

**When:** Showing commands, configuration, code examples, prompts.
**Source:** `slide14` (or duplicate). Replace the picture with a `codebox()`.

```python
from helpers import codebox

text = read("slide54")
code = codebox(
    4688750, 1068400, 3909900, 3260448,  # standard right-side picture coords
    [("settings.json", True),             # bold label
     ("", False),                          # blank line
     ("{", False),
     ("  \"env\": {", False),
     ("    \"FLAG_NAME\": \"1\"", False),
     ("  }", False),
     ("}", False)],
    font_sz="900",
)
text = re.sub(r"<p:pic>.*?</p:pic>", code, text, count=1, flags=re.DOTALL)
# Then edit title and body paragraphs as in Pattern 4
write("slide54", text)
```

**Line-length budget:** at `font_sz="900"`, fit about 30 characters per line. At `font_sz="800"`, fit about 35. Pre-wrap long lines manually (don't rely on auto-wrap inside the code box).

## Pattern 6: 3-column comparison with bold headers

**When:** Comparing 3 distinct options, modes, or categories.
**Source:** `slide11` (or duplicate).

```python
from helpers import edit_3col_headers

edit_3col_headers(
    "slide11",
    title="Comparison Title",
    headers=["Option A", "Option B", "Option C"],
    intros=["Intro paragraph for column A.",
            "Intro paragraph for column B.",
            "Intro paragraph for column C."],
    details=["Follow-up detail for A.",
             "Follow-up detail for B.",
             "Follow-up detail for C."],
    footer_new=footer_new,
)
```

## Pattern 7: 3-column body with intro

**When:** A framing statement on the left, two parallel content blocks on the right. Good for "Here's the principle. Here's case A. Here's case B."
**Source:** `slide13` (or duplicate).

```python
from helpers import edit_3col_body

edit_3col_body(
    "slide13",
    title="Slide Title",
    intro_a="Short framing statement (top of left column).",
    intro_b="Slightly longer subsidiary statement (bottom of left column).",
    mid_a="First paragraph of middle column.",
    mid_b="Second paragraph of middle column.",
    right_a="First paragraph of right column.",
    right_b="Second paragraph of right column.",
    footer_new=footer_new,
)
```

## Pattern 8: Problem / Solution comparison cards

**When:** A pointed question or decision rule slide that needs to show two contrasting outcomes side by side.
**Source:** `slide10` (the original quote slide).

```python
from helpers import problem_solution_cards

# First, set up the slide's title and footer manually:
text = read("slide10")
text = text.replace("<a:t>Don&#x2019;t be afraid of white spaces.</a:t>",
                    "<a:t>Does the intermediate work matter?</a:t>", 1)
write("slide10", text)

# Then add the two cards (this also removes the original picture and footer text):
problem_solution_cards(
    "slide10",
    left_header="YES &#x2014; Keep in main thread",
    left_body="You need to see and react to what's happening along the way.",
    left_tag="Example: bug fixing, where the fix depends on what the debug step found.",
    right_header="NO &#x2014; Delegate to a subagent",
    right_body="You just need the final result. The journey doesn't matter.",
    right_tag="Example: investigating how authentication works in an unfamiliar codebase.",
)
```

The light-grey left card sits next to the dark right card, reinforcing the binary nature of the comparison.

## Pattern 9: Full-width text (no image)

**When:** A pure-text slide with no picture — definitions, limitations summaries.
**Source:** `slide15` (or duplicate). Remove the picture with `remove_pic()`.

```python
from helpers import remove_pic, read, write, FOOTER_OLD

remove_pic("slide15")
text = read("slide15")
text = text.replace("<a:t>Effective Forms Advertising</a:t>", "<a:t>Slide Title</a:t>", 1)
text = text.replace(FOOTER_OLD, footer_new, 1)
text = text.replace(
    "<a:t>Taking part with the flyers \u2013 they are tiny form or a single sheet promotional tool that easily spreads by hand. </a:t>",
    "<a:t>First paragraph.</a:t>", 1)
text = text.replace(
    "<a:t>They are simply characterized as a simple yet compelling promotional material that helps businesses to easily reach out for their targeted audience. </a:t>",
    "<a:t>Second paragraph.</a:t>", 1)
write("slide15", text)
```

With the layout30 pre-fix applied, the right side will be white (matching the slide background) instead of grey.

## Pattern 10: Thank You slide

**When:** Always the last slide of the deck.
**Source:** `slide47` (do not duplicate).

```python
text = read("slide47")
text = text.replace("<a:t>Contacta con nosotros:</a:t>", "<a:t>Get started:</a:t>", 1)
text = text.replace("<a:t>Ainize@lin3s.com</a:t>", "<a:t>code.claude.com/docs</a:t>", 1)
text = text.replace("<a:t>Paula@lin3s.com</a:t>", "<a:t>claude.ai/install.sh</a:t>", 1)
text = text.replace("<a:t>Follow Lin3s:</a:t>", "<a:t>Learn more:</a:t>", 1)
text = text.replace("<a:t>Twitter</a:t>", "<a:t>Link or resource 1</a:t>", 1)
text = text.replace("<a:t>Instagram</a:t>", "<a:t>Link or resource 2</a:t>", 1)
text = text.replace("<a:t>Facebook</a:t>", "<a:t>Link or resource 3</a:t>", 1)
text = text.replace("<a:t>Design Week 2020</a:t>", "<a:t>Brand line</a:t>", 1)
text = text.replace("<a:t>Paula Soto</a:t>", "<a:t>Topic A</a:t>", 1)
text = text.replace("<a:t>Ainize Medrano</a:t>", "<a:t>Topic B</a:t>", 1)
text = text.replace("<a:t>Speaker</a:t>", "<a:t>Topics</a:t>", 1)
write("slide47", text)
```

## Slide assembly cheat-sheet

For a typical 20-slide deck, the order looks like:

```
1.  Title                       → slide1
2.  Agenda                      → slide6
3.  Section 1 divider           → slide16
4.  Definition / overview       → slide14 or slide15 (Pattern 4 or 9)
5.  Concept explanation         → slide14 with image (Pattern 4)
6.  3-column comparison         → slide11 (Pattern 6)
7.  Section 2 divider           → slide16 dup
8.  Setup / code example        → slide14 dup with codebox (Pattern 5)
9.  ... (continues)
20. Thank You                   → slide47
```

The exact mix depends on content. Lean on `slide11` (3-col with headers) for any list of 3-5 named items, `slide14` for visuals or code, `slide15` for prose, and `slide10` for big statements or decision rules.
