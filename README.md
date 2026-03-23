# Felix CAT System

Felix is a computer-assisted translation (CAT) tool for Windows, originally created by Ryan Ginstrom. It is also known as a "translation memory" system.

This repository is an **unmodified archive** of the original Felix source code, preserved exactly as released.

## What is Felix?

Felix helps translators work faster and more consistently by storing previously translated segments in a "translation memory." When a new source sentence is similar to one that has been translated before, Felix suggests the previous translation — allowing the translator to reuse, edit, or reject it.

Felix integrates directly with Microsoft Word, Excel, and PowerPoint via COM add-ins.

## Components

| Component | Description |
|-----------|-------------|
| Felix | Main CAT application (C++) |
| Word Assist | MS Word COM add-in |
| Excel Assist | MS Excel COM add-in |
| PowerPoint Assist | MS PowerPoint COM add-in |

## Documentation

The full Felix Manual 1.7.1.1 is available in two forms:

| Format | Location | Use |
|--------|----------|-----|
| HTML (rendered) | [`docs/`](docs/) — via [GitHub Pages](https://your-org.github.io/felix-original/) | Browse in a browser |
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

See also: [felix-classic](https://github.com/your-org/felix-classic) — a maintained fork updated for the modern toolchain.
