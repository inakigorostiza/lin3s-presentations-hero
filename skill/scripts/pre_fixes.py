"""Apply pre-fixes to a freshly-unpacked LIN3S template.

Two changes that prevent visual issues across all decks:

1. slideLayout30.xml: F3F3F3 (grey) -> FFFFFF (white) for the picture-area
   background. This prevents grey letterbox bands on slides where a non-5:4
   image is swapped in, and prevents an empty grey rectangle from showing
   when a picture is removed entirely.

2. slide6.xml (Agenda): widen the title shape from cx=2304300 (sized tight
   to the original Spanish "Índice") to cx=3200000, and reduce the font size
   from 4800 (48pt) to 4000 (40pt). Together these prevent overflow on
   wider words like "Agenda", "Esquema", or "Programme".

Usage:
    python pre_fixes.py /path/to/unpacked/
"""

from pathlib import Path
import sys


def apply_layout30_grey_fix(unpacked_root: Path) -> int:
    """Change the F3F3F3 fill in slideLayout30 to FFFFFF.

    Returns the number of replacements made (typically 1).
    """
    layout = unpacked_root / "ppt" / "slideLayouts" / "slideLayout30.xml"
    if not layout.exists():
        print(f"  WARN: {layout} not found, skipping layout30 fix")
        return 0
    text = layout.read_text(encoding="utf-8")
    count = text.count('<a:srgbClr val="F3F3F3"/>')
    if count == 0:
        print("  layout30: already clean (no F3F3F3 fill found)")
        return 0
    new = text.replace('<a:srgbClr val="F3F3F3"/>', '<a:srgbClr val="FFFFFF"/>')
    layout.write_text(new, encoding="utf-8")
    print(f"  layout30: replaced {count} grey fill(s) with white")
    return count


def apply_agenda_title_fix(unpacked_root: Path) -> bool:
    """Widen the Agenda title shape and reduce its font size.

    Returns True if changes were applied.
    """
    slide = unpacked_root / "ppt" / "slides" / "slide6.xml"
    if not slide.exists():
        print(f"  WARN: {slide} not found, skipping agenda fix")
        return False
    text = slide.read_text(encoding="utf-8")

    old_xfrm = (
        '<a:off x="545450" y="368250"/>\n'
        '            <a:ext cx="2304300" cy="837300"/>'
    )
    new_xfrm = (
        '<a:off x="545450" y="368250"/>\n'
        '            <a:ext cx="3200000" cy="837300"/>'
    )

    changed = False
    if old_xfrm in text:
        text = text.replace(old_xfrm, new_xfrm, 1)
        changed = True
        print("  agenda: widened title shape from cx=2304300 to cx=3200000")
    else:
        print("  agenda: title shape already widened (or template changed)")

    # Reduce font size of the title (handles both Índice and any replacement)
    old_font = '<a:rPr lang="en" sz="4800"/>\n              <a:t>Índice</a:t>'
    new_font = '<a:rPr lang="en" sz="4000"/>\n              <a:t>Índice</a:t>'
    if old_font in text:
        text = text.replace(old_font, new_font, 1)
        changed = True
        print("  agenda: reduced title font from sz=4800 to sz=4000")
    else:
        print("  agenda: title font already reduced (or text changed)")

    if changed:
        slide.write_text(text, encoding="utf-8")
    return changed


def main():
    if len(sys.argv) != 2:
        print("Usage: python pre_fixes.py /path/to/unpacked/")
        sys.exit(1)
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        sys.exit(1)
    print(f"Applying pre-fixes to {root}")
    apply_layout30_grey_fix(root)
    apply_agenda_title_fix(root)
    print("Pre-fixes complete.")


if __name__ == "__main__":
    main()
