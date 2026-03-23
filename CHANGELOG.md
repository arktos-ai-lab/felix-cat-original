# Changelog — Felix CAT Original

## v1.7.3 (2015) — Final original release

Last version published by Ryan Ginstrom before the project went inactive.

### Features at v1.7.3
- Translation memory with fuzzy and exact matching
- Placement feature — auto-insertion of numbers, glossary terms, and regex-defined patterns
- Microsoft Word add-in (Word Assist) — translation and review modes
- Microsoft Excel add-in (Excel Assist) — translation and review modes
- Microsoft PowerPoint add-in (PowerPoint Assist)
- COM scripting API — scriptable from VBA in Word, Excel, PowerPoint
- MemoryServes — networked shared translation memory server (Python/CherryPy)
- Multi-format segmenter — Word, Excel, PPT, HTML, XML, PDF, RTF, CSV (Python)
- Terminology Aligner — bilingual glossary extraction (Python)
- Rule Manager — custom Placement rules via regex
- Lua scripting support
- Japanese and English UI

### Known compatibility issues
- Built with Visual Studio 2013; requires VS2013 redistributable
- Python components require Python 2.7
- COM add-ins are 32-bit; may have issues with 64-bit Office 365

For a version that works with modern Windows and Office, see
[Felix Classic](https://github.com/arktos-ai-lab/felix-cat-classic).

---
Original project by Ryan Ginstrom. MIT licensed.
Archived and maintained by Ernst van Gassen.
