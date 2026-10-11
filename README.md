# PE02 Lexical Analysis

Lexical analyzer for the official IOL (Integer-Oriented Language) custom programming language, featuring a Tkinter compiler graphical user interface.

## Group Members & Work Distribution

| Member | Identifier | Role & Feature | Documentation |
|---|---|---|---|
| **Richelle De Arce** | Member A | **Editor and Flow**: Window layout, toolbar buttons, editor area, file I/O, compile pipeline trigger, token file writing | [`DOCUMENTATION_MemberA.md`](DOCUMENTATION_MemberA.md) |
| **Johnric Apolinario** | Member B | **Tokenizer**: Scanner character scanning, line tracking, keyword and literal recognition, token data structures, token panel | [`DOCUMENTATION_MemberB.md`](DOCUMENTATION_MemberB.md) |
| **John Andrei Manalo** | Member C | **Errors**: Lexical error detection (`ERR_LEX`), line number reporting, compiler console color-coded output and diagnostics | [`DOCUMENTATION_MemberC.md`](DOCUMENTATION_MemberC.md) |
| **Mark Jaily Pena** | Member D | **Variables and Docs**: Table of variables panel with deduplication and scrolling, unit testing, master documentation, packaging | [`DOCUMENTATION_MemberD.md`](DOCUMENTATION_MemberD.md) |

Comprehensive consolidated project documentation is available in [`DOCUMENTATION.md`](DOCUMENTATION.md).

---

## File Structure

All program files sit together in the root project folder alongside the main program file (as required by PE02 instructions).

```
Lexical-Analysis-CMSC-129/
├── main_window.py             Member A - main window, program entry point
├── ui_editor_panel.py         Member A - editor area
├── lex_data.py                Member B - Token, LexError, Variable, LexResult
├── lex_scanner.py             Member B & C - lexical analyzer and error scanner
├── ui_token_panel.py          Member B - tokenized code display
├── ui_console_panel.py        Member C - console messages
├── ui_variable_panel.py       Member D - table of variables with deduplication
├── build.bat                  Builds the Windows executable
├── CONTRACT.md                Class and method interface contract
├── DOCUMENTATION.md           Full group documentation report
├── DOCUMENTATION_MemberA.md   Member A documentation section
├── DOCUMENTATION_MemberB.md   Member B documentation section
├── DOCUMENTATION_MemberC.md   Member C documentation section
├── DOCUMENTATION_MemberD.md   Member D documentation section
├── test_lex_scanner.py        Unit tests for scanner and console
├── test_ui_variable_panel.py  Unit tests for variable panel
├── sample.iol                 Sample IOL source code file
├── README.md
└── .gitignore
```

---

## Running the Application

Requires Python 3.8+ (standard library only; Tkinter is built-in):

```bash
python main_window.py
```

---

## Running Automated Tests

Run the full test suite covering the scanner, error reporting, and table of variables:

```bash
python -m unittest discover
```

---

## Building the Executable

Using PyInstaller:

- **Windows**:
  ```cmd
  build.bat
  ```
  Output: `dist\LexicalAnalyzer.exe`

- **Linux**:
  ```bash
  pyinstaller --onefile --windowed --name LexicalAnalyzer main_window.py
  ```
  Output: `dist/LexicalAnalyzer`

---

## Submission Archive

Zip the files named in alphabetical order of group members' surnames:
**`Apolinario_DeArce_Manalo_Pena_PE02.zip`**

Contains:
1. Documentation file (`DOCUMENTATION.md` or PDF/DOCX)
2. Program source code files (`*.py`, `sample.iol`, etc.)
3. Executable file (`dist/LexicalAnalyzer.exe` or `dist/LexicalAnalyzer`)
