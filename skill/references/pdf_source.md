# PDF Source Documents

The skill is built around `.docx` sources, but works equally well with `.pdf` once you extract text and images. This reference documents the differences.

## Text extraction

For text-based PDFs (born-digital, not scanned), use the `pdf-reading` skill's text extraction:

```bash
# Read /mnt/skills/public/pdf-reading/SKILL.md first for the full toolkit.
# Quick approach for text-heavy PDFs:
python -c "
import sys
from pypdf import PdfReader
reader = PdfReader('/mnt/user-data/uploads/source.pdf')
for i, page in enumerate(reader.pages, start=1):
    print(f'--- Page {i} ---')
    print(page.extract_text())
"
```

For scanned PDFs, you'll need OCR. See `pdf-reading/SKILL.md` for the recommended approach.

## Image extraction

PDFs store embedded images differently from `.docx` files. Use `pdfimages` (from poppler-utils) or `pymupdf`:

```bash
# Extract all embedded images
mkdir -p /home/claude/pdf_images
pdfimages -all /mnt/user-data/uploads/source.pdf /home/claude/pdf_images/img
ls /home/claude/pdf_images/
```

For more control (preserve aspect ratio, get rendered-page snapshots instead of raw embedded images):

```python
import fitz  # pymupdf
doc = fitz.open("/mnt/user-data/uploads/source.pdf")
for page_num, page in enumerate(doc):
    for img_idx, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        pix.save(f"/home/claude/pdf_images/p{page_num+1}_i{img_idx+1}.png")
```

## Diagrams in PDFs

PDFs often contain diagrams that are **rendered to vector graphics** rather than stored as raster images. These won't extract via `pdfimages` because there's no embedded image to extract — the diagram is drawn with vector primitives at render time.

For those, rasterize the relevant page(s) instead:

```bash
# Rasterize page 3 at 200 DPI as a high-quality image for the slide deck
pdftoppm -png -r 200 -f 3 -l 3 /mnt/user-data/uploads/source.pdf /home/claude/pdf_images/page3
```

The output `page3-3.png` will be a 1700x2200ish image — good enough to use as a slide image. Crop it to the diagram if needed.

## Workflow adjustments

When sourcing from PDF, the workflow has two small changes:

**Step 1 (Read the document):** Use `pdf-reading` skill helpers instead of `extract-text`. Read every page's text content into a planning document before building the deck.

**Step 2 (Plan):** The section structure is often less explicit in PDFs than in `.docx` files (PDFs lack heading semantics). You may need to infer sections from page breaks, large headings, or document outline / bookmarks.

```python
# Get the PDF outline (table of contents) if present
import fitz
doc = fitz.open("/mnt/user-data/uploads/source.pdf")
toc = doc.get_toc()
for level, title, page in toc:
    print(f"{'  ' * (level-1)}{title} (p.{page})")
```

A PDF outline with 5-7 top-level entries is a strong signal for sectioning the deck. If there's no outline, fall back to scanning for headings (large or bold text near the top of each section).

**Everything else (Steps 3-9 of the main workflow):** identical to the `.docx` workflow.
