"""Scan an unpacked deck for leftover LIN3S template placeholder text.

Run this BEFORE packing the final .pptx. Catches the most common mistake:
forgetting to replace one of the original template's stock content strings
in a slide that was duplicated and partially edited.

Usage:
    python verify.py /path/to/unpacked/
    python verify.py /path/to/unpacked/ --slides slide1,slide6,slide16,...

Without --slides, scans every slide in ppt/slides/. With --slides, scans only
the listed slides (useful when you have duplicated source slides still sitting
in the directory that aren't part of the final deck order).
"""

from pathlib import Path
import re
import sys


# Stock template phrases that almost never belong in a real deck.
PATTERNS = [
    (r"Ugly Myspace", "Original slide title placeholder"),
    (r"Effective Forms Advertising", "Stock content title"),
    (r"Welcome To Classifieds", "Stock 3-col header"),
    (r"Freelance Design Tricks", "Stock subhead"),
    (r"I want to talk about to things", "Stock 'love' intro paragraph"),
    (r"I have a truck", "Stock 'truck' detail paragraph"),
    (r"audio visual media", "Stock body paragraph"),
    (r"Taking part with", "Stock flyers paragraph"),
    (r"\bÍndice\b", "Original Spanish agenda title"),
    (r"Design Week 2020", "Template event branding"),
    (r"\bPaula Soto\b", "Original speaker name"),
    (r"Ainize Medrano", "Original speaker name"),
    (r"Contacta con nosotros", "Original Spanish contact text"),
    (r"lin3s\.com", "Original contact emails"),
    (r"Choose great looking images", "Stock title"),
    (r"Don.t be afraid of white spaces", "Stock quote"),
]


def scan_slide(slide_path: Path):
    """Return list of (pattern_label, line_number, line_snippet) hits."""
    text = slide_path.read_text(encoding="utf-8")
    hits = []
    for pattern, label in PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            line_num = text[:m.start()].count("\n") + 1
            line = text.splitlines()[line_num - 1].strip()[:120]
            hits.append((label, line_num, line))
    return hits


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify.py /path/to/unpacked/ [--slides slide1,slide6,...]")
        sys.exit(1)

    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        sys.exit(1)

    slides_dir = root / "ppt" / "slides"

    # Determine which slides to scan
    if "--slides" in sys.argv:
        idx = sys.argv.index("--slides")
        names = sys.argv[idx + 1].split(",")
        slide_paths = [slides_dir / f"{n}.xml" for n in names]
    else:
        slide_paths = sorted(slides_dir.glob("slide*.xml"))

    total_hits = 0
    for slide_path in slide_paths:
        if not slide_path.exists():
            print(f"  SKIP: {slide_path.name} (not found)")
            continue
        hits = scan_slide(slide_path)
        if hits:
            print(f"\n{slide_path.name}:")
            for label, line_num, snippet in hits:
                print(f"  line {line_num}: {label}")
                print(f"    > {snippet}")
                total_hits += 1

    print()
    if total_hits == 0:
        print(f"CLEAN: scanned {len(slide_paths)} slide(s), no leftover placeholders")
    else:
        print(f"FOUND {total_hits} leftover placeholder(s) across {len(slide_paths)} slide(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
