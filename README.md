# Felix CAT System

Felix is a computer-assisted translation (CAT) tool for Windows, originally created by Ryan Ginstrom. It is also known as a "translation memory" system.

This repository is an **unmodified archive** of the original Felix source code, preserved exactly as released.

## What is Felix?

Felix helps translators work faster and more consistently by storing previously translated segments in a "translation memory." When a new source sentence is similar to one that has been translated before, Felix suggests the previous translation — allowing the translator to reuse, edit, or reject it.

Felix integrates directly with Microsoft Word, Excel, and PowerPoint via COM add-ins.

## Components

### Main application

| Component | Description |
|-----------|-------------|
| Felix | Main CAT application (C++) |
| Word Assist | MS Word COM add-in |
| Excel Assist | MS Excel COM add-in |
| PowerPoint Assist | MS PowerPoint COM add-in |

### Companion tools (in `companion-tools/`)

These are standalone tools Ryan released as separate projects. They are archived here to keep the full Felix ecosystem in one place.

| Tool | Description |
|------|-------------|
| [MemoryServes](companion-tools/memoryserves/) | Network TM server — share a translation memory across a team via CherryPy/HTTP |
| [MemoryServes Exporter](companion-tools/memoryservesexporter/) | Export utility for MemoryServes TM databases |
| [Segmenter](companion-tools/segmenter/) | Multi-format text segmenter — Word, Excel, PPT, HTML, XML, PDF, RTF, CSV (Python) |
| [Terminology Aligner](companion-tools/terminologyaligner/) | Bilingual glossary extraction from parallel texts |
| [Analyze Assist](companion-tools/analyzeassist/) | Pre-translation analysis tool — segment counts, TM leverage, fuzzy band statistics |

All companion tools require **Python 2.7** and the dependencies listed in each tool's README.

## Documentation

The full Felix Manual 1.7.1.1 is available in two forms:

| Format | Location | Use |
|--------|----------|-----|
| HTML (rendered) | [`docs/`](docs/) — via [GitHub Pages](https://arktos-ai-lab.github.io/felix-cat-original/) | Browse in a browser |
| Markdown | [`manual/`](manual/) | Read on GitHub / machine-readable |

The [`docs/index.html`](docs/index.html) is the GitHub Pages entry point with a full table of contents.

Topics covered:
- Getting started and first-time setup
- The Placement feature (auto-insertion of numbers, glossary terms, regex patterns)
- Using Felix from Word, Excel, and PowerPoint
- COM scripting API
- FAQ and troubleshooting

## Build Requirements

Felix was built with **Visual Studio 2013 Community Edition**.

Required libraries:
- [Windows Template Library (WTL)](http://sourceforge.net/projects/wtl/)
- [Boost](http://www.boost.org/)
- [Lua](http://www.lua.org/)
- [LuaBridge](https://github.com/vinniefalco/LuaBridge)
- [Python](https://www.python.org/)

Additional runtime dependencies:
- `SciLexer.dll` from [Scintilla](http://www.scintilla.org/)
- `DbgHelp.dll`
- VS 2010 and VS 2013 redistributable packages
- `MSVCP90.dll` and `MSVCR90.dll` for Python components

## Source Layout

```
src/
├── Felix/              Main application (C++)
├── WordAssist/         Word COM add-in
├── ExcelAssist/        Excel COM add-in
├── PowerPointAssist/   PowerPoint COM add-in
├── common/             Shared third-party libraries
├── python_tools/       Helper scripts
├── manual/             Sphinx RST documentation source (original)
├── settings/           Default configuration
├── setup/              InnoSetup installer scripts
└── Test_*/             Unit tests
docs/
    index.html          GitHub Pages table of contents
    about.html
    getting-started.html
    ... (41 pages total, see index)
manual/
    about.md
    getting-started.md
    ... (41 pages total, Markdown)
```

## License

MIT License — see [LICENSE](LICENSE).

Original copyright: Ryan Ginstrom, 1999–2015.

## Original Project

Felix was originally hosted at [felix-cat.com](http://felix-cat.com/) (now archived).
The original source was published on Bitbucket under the MIT license.

See also: [felix-cat-classic](https://github.com/arktos-ai-lab/felix-cat-classic) — a maintained fork updated for the modern toolchain, by Ernst van Gassen.

## Support Arktos AI Lab

Arktos AI Lab is a one-person operation run by Ernst van Gassen — an independent researcher with one too many interests and not enough hours in the day. Preserving Ryan Ginstrom's work, keeping it accessible, and building on top of it all take genuine time and effort.

If this project has saved you time, helped you rediscover a tool you once loved, or simply made something possible that wasn't before — a small donation is a meaningful way to say thank you and to keep the work going.

[![Donate via PayPal](https://img.shields.io/badge/Donate%20via-PayPal-blue.svg)](https://paypal.me/VanGassen)

Thank you. It genuinely makes a difference.

---
All original credit goes to **Ryan Ginstrom** who designed and built Felix and released it as open source. This repository exists because of his generosity.
