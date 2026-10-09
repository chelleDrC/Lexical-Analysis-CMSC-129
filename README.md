# PE02 Lexical Analysis

Lexical analyzer for the IOL custom programming language, with a Tkinter compiler UI.

## Files

```
Lexical-Analysis-CMSC-129/
├── main_window.py             Member A - main window, program entry point
├── lex_data.py                Member B - Token, LexError, Variable, LexResult
├── lex_scanner.py             Member B - lexical analyzer
├── ui_console_panel.py        Member C - console messages
├── ui_editor_panel.py         Member A - editor area
├── ui_token_panel.py          Member B - tokenized code display
├── ui_variable_panel.py       Member D - table of variables
├── build.bat                  Builds the executable
├── CONTRACT.md                Class and method names shared by all members
├── DOCUMENTATION_MemberA.md   Member A documentation section
├── README.md
└── .gitignore
```

All program files stay in one folder, with no subfolders. The PE02 instructions require all program files to sit together with the main program file.

File name prefixes group the files by role:

| Prefix | Role |
|---|---|
| `main_` | Program entry point |
| `ui_` | User interface panels |
| `lex_` | Lexical analysis logic and data |

Files marked **PLACEHOLDER** in their header are stubs. Each member replaces their own file. See [CONTRACT.md](CONTRACT.md).

## Run

```
python main_window.py
```

## Build Executable

```
pip install pyinstaller
build.bat
```

Output: `dist\LexicalAnalyzer.exe`

## Submission

Zip file named with surnames in alphabetical order, separated by underscores, followed by the PE number. Example: `Bonifacio_Rizal_PE02.zip`

Contents:
- Documentation file (combined from each member's documentation section)
- Source code files (`*.py`)
- Executable file (`LexicalAnalyzer.exe`)
