"""Reusable helpers for editing LIN3S template slide XML.

Import into your build script:

    import sys
    sys.path.insert(0, '<skill_path>/scripts')
    from helpers import (
        read, write, edit_rels, fix_image, remove_pic,
        codebox, edit_3col_headers, edit_3col_body, problem_solution_cards,
        LONG_INTRO, LONG_TRUCK_NS, LONG_TRUCK_SP, HEADER_OLD, FOOTER_OLD,
        smart_quote_entities,
    )

All read/write operations target paths relative to the `BASE` you set.
Set it at the top of your build script:

    helpers.BASE = Path("unpacked/ppt/slides")
"""

from pathlib import Path
import re

# Set this from your build script BEFORE using any read/write helpers.
BASE: Path = Path("unpacked/ppt/slides")

# ============================================================================
# Template placeholder strings (after unpack.py converts smart quotes to entities)
# ============================================================================
# slide11 (3-col with headers) puts this in each column header:
HEADER_OLD = "<a:t>Welcome To Classifieds Free Ads Free Advertisement</a:t>"

# slide11 / slide13 / slide14 main intro paragraph (the "love" one):
LONG_INTRO = (
    '<a:t>I want to talk about to things that are quite important to me. '
    "There are love and one my personal inadequacies. The thing is that "
    "I&#x2019;m quite fond of love, I think that it&#x2019;s a pretty all "
    "right deal. However, I&#x2019;m going to have to admit that my "
    "emotional baggage has built up walls that not even a shock and awe "
    "campaign could bring down. But I do love. And in fact I even love "
    "unconditionally. </a:t>"
)

# slide11 / slide13 "truck" paragraph — exists in TWO variants. The first
# occurrence in a slide11 layout has NO trailing space; subsequent
# occurrences have one. Match them in order:
LONG_TRUCK_NS = (
    '<a:t>I have a truck. It&#x2019;s kind of a small truck, but I&#x2019;m '
    "comfortable with myself so that&#x2019;s okay. I think that I love it. "
    "I had a friend about a year ago ask me if I could have any car in the "
    "world what would I have. And aside from pointing out that my friend "
    "and I have clearly ran out of things to discuss and should probably go "
    "our separate ways, my answer told me that I love my truck (obviously "
    "I said I would keep my truck).</a:t>"
)
LONG_TRUCK_SP = LONG_TRUCK_NS[:-6] + " </a:t>"  # same but with trailing space

# Most-common footer line (the "Ugly Myspace..." subtitle on many slides):
FOOTER_OLD = "<a:t>An Ugly Myspace Profile Will Sure Ruin Your Reputation</a:t>"
FOOTER_OLD_DOT = "<a:t>An Ugly Myspace Profile Will Sure Ruin Your Reputation.</a:t>"


# ============================================================================
# File I/O helpers
# ============================================================================

def read(slide_name: str) -> str:
    """Read a slide's XML by name (e.g. 'slide14')."""
    return (BASE / f"{slide_name}.xml").read_text(encoding="utf-8")


def write(slide_name: str, text: str) -> None:
    """Write a slide's XML by name."""
    (BASE / f"{slide_name}.xml").write_text(text, encoding="utf-8")


def edit_rels(slide_name: str, old_target: str, new_target: str) -> None:
    """Update a relationship target in slide<N>.xml.rels.

    Use this to repoint a slide's image reference, e.g.:
        edit_rels("slide14", "image16.jpg", "my_diagram.png")
    """
    rels_path = BASE / "_rels" / f"{slide_name}.xml.rels"
    text = rels_path.read_text(encoding="utf-8")
    rels_path.write_text(text.replace(old_target, new_target), encoding="utf-8")


# ============================================================================
# Image helpers
# ============================================================================

def fix_image(slide_name: str) -> None:
    """Strip srcRect crop and resize picture placeholder to 16:9, centered.

    Apply this to every slide where you swap in a non-5:4 image (typically
    16:9 docx images). Without it, the template's original srcRect crops
    the new image awkwardly, often cutting off labels or essential content.
    """
    path = BASE / f"{slide_name}.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<a:srcRect[^/]*/>\s*', '', text)
    for pic in re.findall(r"(<p:pic>.*?</p:pic>)", text, re.DOTALL):
        m = re.search(
            r'<a:xfrm>\s*<a:off x="(\d+)" y="(\d+)"/>\s*'
            r'<a:ext cx="(\d+)" cy="(\d+)"/>\s*</a:xfrm>',
            pic,
        )
        if not m:
            continue
        x, y, cx, cy = (int(g) for g in m.groups())
        new_cy = round(cx * 9 / 16)
        new_y = y + (cy - new_cy) // 2
        new_xfrm = (
            f'<a:xfrm>\n            <a:off x="{x}" y="{new_y}"/>\n'
            f'            <a:ext cx="{cx}" cy="{new_cy}"/>\n          </a:xfrm>'
        )
        text = text.replace(pic, pic.replace(m.group(0), new_xfrm), 1)
    path.write_text(text, encoding="utf-8")


def remove_pic(slide_name: str) -> None:
    """Remove the first <p:pic> element from a slide.

    Use when replacing an image with text content (definitions, quotes)
    or a code block via codebox().
    """
    path = BASE / f"{slide_name}.xml"
    text = re.sub(
        r"<p:pic>.*?</p:pic>\s*",
        "",
        path.read_text(encoding="utf-8"),
        count=1,
        flags=re.DOTALL,
    )
    path.write_text(text, encoding="utf-8")


# ============================================================================
# Content helpers — codebox
# ============================================================================

def codebox(x: int, y: int, cx: int, cy: int, lines, font_sz: str = "900") -> str:
    """Build a light-grey code-style text shape for the right-side area.

    `lines` is a list of `(text, is_bold)` tuples. Bold lines use the slide's
    default sans-serif font and serve as section labels (e.g. "settings.json").
    Non-bold lines use Courier New for code/monospace display.

    Standard right-side coordinates (matches the slide14 picture placeholder):
        x=4688750, y=1068400, cx=3909900, cy=3260448

    Use font_sz="800" or "900" depending on content density.

    The returned XML string should be substituted into the slide via:
        text = re.sub(r"<p:pic>.*?</p:pic>", codebox(...), text, count=1,
                      flags=re.DOTALL)
    """
    paras = []
    for text, bold in lines:
        if bold:
            rpr = f'<a:rPr lang="en" sz="{font_sz}" b="1"/>'
        else:
            rpr = (
                f'<a:rPr lang="en" sz="{font_sz}">'
                f'<a:latin typeface="Courier New"/></a:rPr>'
            )
        paras.append(
            f"          <a:p>\n"
            f'            <a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l">'
            f'<a:spcBef><a:spcPts val="0"/></a:spcBef>'
            f'<a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr>\n'
            f"            <a:r>{rpr}<a:t>{text}</a:t></a:r>\n"
            f"          </a:p>"
        )
    body = "\n".join(paras)
    return f'''      <p:sp>
        <p:nvSpPr><p:cNvPr id="9001" name="code"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="F4F4F4"/></a:solidFill>
          <a:ln><a:noFill/></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr anchorCtr="0" anchor="t" bIns="200000" lIns="200000" spcFirstLastPara="1" rIns="200000" wrap="square" tIns="200000"><a:noAutofit/></a:bodyPr>
          <a:lstStyle/>
{body}
        </p:txBody>
      </p:sp>'''


# ============================================================================
# Multi-column slide helpers
# ============================================================================

def edit_3col_headers(slide_name: str, title: str, headers, intros, details,
                       footer_new: str) -> None:
    """Edit a slide11-style 3-column-with-bold-headers slide.

    Args:
        slide_name: e.g. 'slide11'
        title: the slide title text (without <a:t> tags)
        headers: list of 3 header strings
        intros: list of 3 intro paragraph strings
        details: list of 3 detail paragraph strings
        footer_new: the new footer text (the deck's running title)

    All input strings should NOT include <a:t> tags — they're added here.
    Smart quotes must use entity form (e.g. &#x2019; for ').
    """
    text = read(slide_name)
    text = text.replace(
        "<a:t>Effective Forms Advertising</a:t>",
        f"<a:t>{title}</a:t>",
        1,
    )
    text = text.replace(FOOTER_OLD, footer_new, 1)
    for h in headers:
        text = text.replace(HEADER_OLD, f"<a:t>{h}</a:t>", 1)
    for intro in intros:
        text = text.replace(LONG_INTRO, f"<a:t>{intro}</a:t>", 1)
    # First detail uses no-space variant; rest use space variant
    text = text.replace(LONG_TRUCK_NS, f"<a:t>{details[0]}</a:t>", 1)
    text = text.replace(LONG_TRUCK_SP, f"<a:t>{details[1]}</a:t>", 1)
    text = text.replace(LONG_TRUCK_SP, f"<a:t>{details[2]}</a:t>", 1)
    write(slide_name, text)


def edit_3col_body(slide_name: str, title: str,
                    intro_a: str, intro_b: str,
                    mid_a: str, mid_b: str,
                    right_a: str, right_b: str,
                    footer_new: str) -> None:
    """Edit a slide13-style 3-column body slide.

    Layout: a narrow intro column on the left (2 short paragraphs), then two
    wider content columns on the right (2 paragraphs each).

    Args:
        slide_name: e.g. 'slide13'
        title: slide title text
        intro_a, intro_b: paragraphs for the left intro column
        mid_a, mid_b: paragraphs for the middle column
        right_a, right_b: paragraphs for the right column
        footer_new: the new footer text
    """
    text = read(slide_name)
    text = text.replace(
        "<a:t>Effective Forms Advertising</a:t>",
        f"<a:t>{title}</a:t>",
        1,
    )
    text = text.replace(FOOTER_OLD, footer_new, 1)
    text = text.replace(
        "<a:t>I want to talk about to things that are quite important to me. </a:t>",
        f"<a:t>{intro_a}</a:t>",
        1,
    )
    text = text.replace(
        "<a:t>There are love and one my personal inadequacies. The thing is "
        "that I&#x2019;m quite fond of love, I think that it&#x2019;s a "
        "pretty all right deal. </a:t>",
        f"<a:t>{intro_b}</a:t>",
        1,
    )
    text = text.replace(LONG_INTRO, f"<a:t>{mid_a}</a:t>", 1)
    text = text.replace(LONG_TRUCK_SP, f"<a:t>{mid_b}</a:t>", 1)
    text = text.replace(LONG_INTRO, f"<a:t>{right_a}</a:t>", 1)
    text = text.replace(LONG_TRUCK_SP, f"<a:t>{right_b}</a:t>", 1)
    write(slide_name, text)


# ============================================================================
# Quote slide helper — problem/solution or yes/no comparison cards
# ============================================================================

def problem_solution_cards(slide_name: str,
                            left_header: str, left_body: str, left_tag: str,
                            right_header: str, right_body: str, right_tag: str
                            ) -> None:
    """Replace slide10-style quote slide's empty middle with two contrast cards.

    Left card: light grey (F4F4F4) background, dark text.
    Right card: dark (1A1A1A) background, white text.

    Card dimensions: 3,700,000 × 2,900,000 EMU, positioned at y=1,300,000.
    Left x=545,450; right x=4,898,550. Gap between cards: ~498,550 EMU.

    Each card has:
        - Bold header (24pt)
        - Body paragraph (12pt regular)
        - Italic tag/example paragraph (12pt italic)

    Args:
        slide_name: e.g. 'slide10'
        left_header / left_body / left_tag: content for the light card
        right_header / right_body / right_tag: content for the dark card

    Use cases: "Problem / Solution: Tool Use", "YES keep / NO delegate",
    "Don't do X / Do Y", etc.
    """
    path = BASE / f"{slide_name}.xml"
    text = path.read_text(encoding="utf-8")

    # Remove any picture from the slide
    text = re.sub(r"<p:pic>.*?</p:pic>\s*", "", text, count=1, flags=re.DOTALL)

    # Remove the bottom subtitle shape (it was sized for footer-style text)
    text = re.sub(
        r'<p:sp>\s*<p:nvSpPr>\s*<p:cNvPr id="706"[^>]*/>.*?</p:sp>',
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )

    left_card = f'''      <p:sp>
        <p:nvSpPr><p:cNvPr id="9101" name="left card"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="545450" y="1300000"/><a:ext cx="3700000" cy="2900000"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="F4F4F4"/></a:solidFill>
          <a:ln><a:noFill/></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr anchorCtr="0" anchor="t" bIns="280000" lIns="280000" spcFirstLastPara="1" rIns="280000" wrap="square" tIns="280000"><a:noAutofit/></a:bodyPr>
          <a:lstStyle/>
          <a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="600"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en" sz="2400" b="1"/><a:t>{left_header}</a:t></a:r></a:p>
          <a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="600"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en" sz="1200"/><a:t>{left_body}</a:t></a:r></a:p>
          <a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en" sz="1200" i="1"/><a:t>{left_tag}</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>'''

    right_card = f'''      <p:sp>
        <p:nvSpPr><p:cNvPr id="9102" name="right card"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="4898550" y="1300000"/><a:ext cx="3700000" cy="2900000"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="1A1A1A"/></a:solidFill>
          <a:ln><a:noFill/></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr anchorCtr="0" anchor="t" bIns="280000" lIns="280000" spcFirstLastPara="1" rIns="280000" wrap="square" tIns="280000"><a:noAutofit/></a:bodyPr>
          <a:lstStyle/>
          <a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="600"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en" sz="2400" b="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{right_header}</a:t></a:r></a:p>
          <a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="600"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en" sz="1200"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{right_body}</a:t></a:r></a:p>
          <a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en" sz="1200" i="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{right_tag}</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>'''

    text = text.replace(
        "      </p:spTree>",
        left_card + "\n" + right_card + "\n      </p:spTree>",
        1,
    )
    path.write_text(text, encoding="utf-8")


# ============================================================================
# Smart quote utility
# ============================================================================

def smart_quote_entities(text: str) -> str:
    """Convert raw Unicode smart quotes to XML entity form.

    The unpack.py tool converts smart quotes in the original template to
    entity form (e.g. &#x2019;) on disk. If you build replacement strings
    with raw Unicode characters (' " etc.), the matches will fail. Pass
    user-facing content strings through this helper before splicing them
    into slide XML.
    """
    return (
        text
        .replace("\u2018", "&#x2018;")  # '
        .replace("\u2019", "&#x2019;")  # '
        .replace("\u201C", "&#x201C;")  # "
        .replace("\u201D", "&#x201D;")  # "
        .replace("\u2014", "&#x2014;")  # —
        .replace("\u2013", "&#x2013;")  # –
        .replace("\u2015", "&#x2015;")  # ― (used in section indicators)
    )
