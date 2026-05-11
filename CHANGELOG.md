# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Pending
- Confirmation from LIN3S on bundling the template
- Spanish translation of documentation
- Video walkthrough of the skill in action

## [0.1.0] — 2026-05-11

### Added
- Initial release. Distilled from four educational decks built on the LIN3S
  Design Week 2020 template.
- `skill/SKILL.md` — nine-step workflow blueprint for turning `.docx` or `.pdf`
  source documents into finished `.pptx` decks.
- `skill/scripts/helpers.py` — reusable helpers covering 3-column slides,
  image+text slides, code blocks, problem/solution cards, full-width text,
  smart-quote conversion, and image cropping/resizing.
- `skill/scripts/pre_fixes.py` — applies two pre-fixes at unpack time
  (layout30 grey→white background, agenda title widening).
- `skill/scripts/verify.py` — scans an unpacked deck for leftover template
  placeholder text before packing.
- `skill/references/slide_taxonomy.md` — maps each source template slide
  (slide1, slide6, slide10, slide11, slide13, slide14, slide15, slide16,
  slide17, slide47) to the content type it handles best.
- `skill/references/patterns.md` — 10 layout recipes with concrete code.
- `skill/references/pitfalls.md` — every gotcha encountered during the
  build of the four example decks, with diagnostic and fix for each.
- `skill/references/pdf_source.md` — handling `.pdf` inputs alongside `.docx`.
- `skill/assets/LIN3S_TEMPLATE.pptx` — the template itself (pending LIN3S
  permission to redistribute).
- Four example decks in `examples/` produced with this skill.
- `docs/installation.md` — how end users install the skill.
- `scripts/build.sh` — reproducible packaging.

[Unreleased]: https://github.com/USER/lin3s-presentations-hero/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/USER/lin3s-presentations-hero/releases/tag/v0.1.0
