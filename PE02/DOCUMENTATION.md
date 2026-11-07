# CMSC 129: Principles of Compiler Design
## Programming Exercise 02: Lexical Analysis
### Group Documentation Report

---

## 1. Program Description

The **IOL Lexical Analyzer** is a partial implementation of a compiler front-end for the custom programming language **IOL** (Integer-Oriented Language). Built using Python and the standard Tkinter graphical interface library, the system provides an integrated compiler user interface (UI) capable of reading, writing, editing, scanning, tokenizing, and analyzing IOL source code.

The lexical analyzer processes IOL source code character by character from left to right, isolating lexemes and categorizing them into official token types:
- **Keywords**: Exact reserved words in IOL (`IOL`, `LOI`, `INT`, `STR`, `INTO`, `IS`, `BEG`, `PRINT`, `NEWLN`, `ADD`, `SUB`, `MULT`, `DIV`, `MOD`).
- **Identifiers (`IDENT`)**: Variable names consisting of a letter followed by zero or more letters or digits.
- **Integer Literals (`INT_LIT`)**: Sequences of one or more decimal digits.
- **Error Lexemes (`ERR_LEX`)**: Invalid words, malformed identifiers (such as digits followed by letters), or unsupported characters.

### Key Outputs:
1. **Token Stream Output (`.tkn` file)**: Converts the entire source program into its tokenized representation where each lexeme is replaced by its token name, preserving line numbering and empty lines.
2. **Compiler Console Output**: Real-time feedback displaying either a success notification or detailed error diagnostics highlighting unknown words and their exact line numbers.
3. **Table of Variables Used**: A structured graphical table populated with all declared identifiers and their corresponding data types (`INT` or `STR`), guaranteed without duplicate rows.
4. **Tokenized Code Panel**: An on-screen inspector showing token details line by line upon user request.

---

## 2. Parts, Modules, and Functions

All program source code files are structured in a flat directory layout alongside the main program entry point, adhering strictly to the structured programming and project architectural guidelines.

```
Lexical-Analysis-CMSC-129/
├── main_window.py          # Program entry point and central coordinator (Member A)
├── ui_editor_panel.py      # Source code editor panel with scrolling (Member A)
├── lex_data.py             # Data classes for tokens, errors, and variables (Member B)
├── lex_scanner.py          # Lexical scanner and tokenizer (Member B)
├── ui_token_panel.py       # Tokenized code display panel (Member B)
├── ui_console_panel.py     # Compiler console status and error panel (Member C)
├── ui_variable_panel.py    # Table of variables panel with deduplication (Member D)
├── test_lex_scanner.py     # Unit test suite for scanner and console
└── test_ui_variable_panel.py # Unit test suite for variable table panel
```

### 2.1 Main Window (`main_window.py`) — Member A
Coordinates UI panels, file input/output, and routes compiler actions.

| Function | Parameters | Return Type | Description |
|---|---|---|---|
| `main()` | None | `None` | Starts the application by instantiating the Tk root window and `MainWindow`. |
| `__init__(root)` | `root: tk.Tk` | `None` | Sets up window geometry, title, scanner instance, panels, and layout. |
| `create_toolbar()` | None | `None` | Creates buttons: Open File, New File, Compile Code, Show Tokenized Code. |
| `create_status_bar()` | None | `None` | Builds the bottom status bar displaying operational status and file paths. |
| `create_main_area()` | None | `None` | Configures resizable paned windows (`ttk.PanedWindow`) for editor, outputs, and console. |
| `open_file()` | None | `None` | Prompts user for an `.iol` file, reads content, loads into the editor, and updates window title. |
| `new_file()` | None | `None` | Prompts to save existing edits, clears editor, and resets compile state. |
| `compile_code()` | None | `None` | Extracts editor text, executes `scanner.analyze()`, updates console and variable table, clears tokens, and saves `.tkn` file. |
| `show_tokenized_code()` | None | `None` | Displays generated token list in `TokenPanel` if code has been compiled. |
| `read_file(path)` | `path: str` | `str` | Reads entire contents of a text file using UTF-8 encoding. |
| `write_file(path, text)`| `path: str, text: str` | `None` | Writes text content to disk, overwriting existing file. |
| `save_file()` | None | `bool` | Opens save dialog to save current editor content to an `.iol` file. |
| `write_token_file(tokens)` | `tokens: list[Token]` | `None` | Writes token stream to `<name>.tkn` in the same directory as source file (or `untitled.tkn`). |
| `build_token_stream(tokens)` | `tokens: list[Token]` | `str` | Formats tokens into line-preserved token strings matching original source line numbers. |
| `show_error(message)` | `message: str` | `None` | Displays an error dialog using `tkinter.messagebox`. |
| `set_status(message)` | `message: str` | `None` | Updates status bar label with notification text. |

### 2.2 Editor Panel (`ui_editor_panel.py`) — Member A
Provides a text editor widget with line-based editing and vertical scrolling.

| Function | Parameters | Return Type | Description |
|---|---|---|---|
| `__init__(parent)` | `parent: Widget` | `None` | Creates a `tk.LabelFrame` containing a monospaced text widget and vertical scrollbar. |
| `get_text()` | None | `str` | Retrieves current text from the editor without trailing newline. |
| `set_text(content)` | `content: str` | `None` | Overwrites editor text with `content` and moves view to the top. |
| `clear()` | None | `None` | Clears all text from the editor area. |

### 2.3 Lexical Data Models (`lex_data.py`) — Member B
Provides standard data classes shared across scanner and UI panels.

| Class | Attributes | Description |
|---|---|---|
| `Token` | `type: str`, `lexeme: str`, `line: int` | Represents an individual recognized token with its type, source text, and 1-based line number. |
| `LexError` | `lexeme: str`, `line: int` | Represents an invalid or unknown lexeme and the line where it occurred. |
| `Variable` | `name: str`, `type: str` | Represents a declared variable identifier and its data type (`INT` or `STR`). |
| `LexResult` | `tokens: list`, `errors: list`, `variables: list` | Aggregates all tokens, errors, and variables produced from a single compilation run. |

### 2.4 Lexical Scanner (`lex_scanner.py`) — Member B & C
Performs character-by-character lexical analysis, identifies tokens, detects invalid lexemes, and extracts variable declarations.

| Function | Parameters | Return Type | Description |
|---|---|---|---|
| `analyze(source_code)` | `source_code: str` | `LexResult` | Scans source text line by line and character by character, returning tokens, errors, and variables. |
| `_consume_invalid_lexeme(line, pos)` | `line: str, pos: int` | `int` | Advances position past non-whitespace characters for malformed lexemes. |
| `_record_error(tokens, errors, lexeme, line)` | `tokens, errors, lexeme: str, line: int` | `None` | Appends an `ERR_LEX` token to tokens and a `LexError` to the error collection. |
| `_collect_variables(tokens)` | `tokens: list[Token]` | `list[Variable]` | Parses declaration sequences (`INT <name>`, `STR <name>`) and records variables without duplicates. |

### 2.5 Token Display Panel (`ui_token_panel.py`) — Member B
Displays tokenized output line by line.

| Function | Parameters | Return Type | Description |
|---|---|---|---|
| `__init__(parent)` | `parent: Widget` | `None` | Initializes `tk.LabelFrame` holding read-only text view for tokens. |
| `show_tokens(tokens)` | `tokens: list[Token]` | `None` | Replaces panel content with formatted lines: `<line>: <token_type> <lexeme>`. |

### 2.6 Console Panel (`ui_console_panel.py`) — Member C
Displays lexical analysis status, success notifications, and error reports.

| Function | Parameters | Return Type | Description |
|---|---|---|---|
| `__init__(parent)` | `parent: Widget` | `None` | Creates `LabelFrame` console with color tags (`#1b7f3a` for success, `#b00020` for errors). |
| `show_result(errors)` | `errors: list[LexError]` | `None` | Replaces console content with success message or detailed list of errors. |
| `build_messages(errors)` | `errors: list[LexError]` | `list[str]` | Static method that constructs display messages describing detected errors. |

### 2.7 Table of Variables Panel (`ui_variable_panel.py`) — Member D
Displays declared variables (name and type) in a structured table with duplicate suppression and scrolling.

| Function | Parameters | Return Type | Description |
|---|---|---|---|
| `__init__(parent)` | `parent: Widget` | `None` | Sets up `tk.LabelFrame`, `ttk.Treeview` with columns "Variable Name" and "Data Type", and vertical scrollbar. |
| `show_variables(variables)` | `variables: list[Variable]` | `None` | Clears table, extracts variable names and types, filters duplicates, and inserts unique rows into Treeview. |
| `clear()` | None | `None` | Removes all rows from the Treeview table. |
| `get_variables()` | None | `list[tuple[str, str]]` | Returns list of `(name, type)` tuples currently displayed in the table. |
| `count()` | None | `int` | Returns count of rows currently in the table. |

---

## 3. Control Flow of the Program

### 3.1 Overall Application Lifecycle
```text
[ Program Launch ]
       │
       ▼
  main() -> MainWindow(root) -> root.mainloop()
       │
       ▼
[ Idle State: Waiting for User Interaction ]
   ├─► Click "Open File"
   │     └─► File dialog -> load .iol file into EditorPanel -> reset compile state
   │
   ├─► Click "New File"
   │     └─► Prompt unsaved changes -> clear EditorPanel -> reset state
   │
   ├─► Click "Compile Code"
   │     └─► Execute Lexical Analysis workflow (see Section 3.2)
   │
   ├─► Click "Show Tokenized Code"
   │     └─► If compiled: display tokens in TokenPanel
   │         Else: show info dialog "Compile the code first."
   │
   └─► Close Window -> Program Terminate
```

### 3.2 Compilation and Lexical Analysis Flow
When the user clicks **Compile Code**:
```text
1. User clicks 'Compile Code'
       │
       ▼
2. MainWindow.compile_code()
       │  reads editor text from EditorPanel.get_text()
       │  (if empty, displays warning dialog and aborts)
       ▼
3. Scanner.analyze(source_code)
       │
       ├─► Split source into lines (1-indexed)
       ├─► Left-to-right character scanning:
       │     ├─ Whitespace: skip
       │     ├─ Alpha: scan word -> Keyword or IDENT (or ERR_LEX if invalid tail)
       │     ├─ Digit: scan integer -> INT_LIT (or ERR_LEX if followed by letters)
       │     └─ Other symbols: scan invalid sequence -> ERR_LEX
       │
       ├─► Collect errors -> list of LexError(lexeme, line)
       ├─► Collect variables -> parse declarations (INT/STR <name>), deduplicate
       └─► Return LexResult(tokens, errors, variables)
       ▼
4. ConsolePanel.show_result(result.errors)
       ├─ If errors empty: display green "Lexical analysis successful."
       └─ If errors exist: display red "Lexical analysis failed" with error lines
       ▼
5. VariablePanel.show_variables(result.variables)
       ├─ Clear previous rows in Treeview
       ├─ Filter incoming variables to guarantee no duplicate identifiers
       └─ Insert unique (name, type) entries into Table of Variables
       ▼
6. TokenPanel.show_tokens([])
       └─ Clear displayed tokens until user explicitly requests display
       ▼
7. MainWindow.write_token_file(result.tokens)
       ├─ Build token stream matching original line structure
       └─ Save to <filename>.tkn (or untitled.tkn) and update status bar
```

---

## 4. Work Distribution to Members

| Member Name | Role & Identifier | Assigned Feature / Responsibilities | Modules / Files Implemented |
|---|---|---|---|
| **Richelle De Arce** | **Member A**:<br>Editor and Flow | **Program Flow & File Handling**<br>• Main window GUI layout, resizable paned windows, toolbar, status bar<br>• File operations: Open File, New File, Save File<br>• Compiler trigger: connecting Compile button to Scanner, distributing results to panels<br>• Token stream file generation (`.tkn` file output)<br>• Editor panel with scrolling | • `main_window.py`<br>• `ui_editor_panel.py`<br>• `DOCUMENTATION_MemberA.md` |
| **Johnric Apolinario** | **Member B**:<br>Tokenizer | **Token Generation & Output**<br>• Lexical scanner core character scanning and line tracking<br>• Keyword recognition (`IOL`, `LOI`, `INT`, `STR`, `PRINT`, etc.)<br>• Identifier (`IDENT`) and integer literal (`INT_LIT`) recognition<br>• Token data classes (`Token`, `LexError`, `Variable`, `LexResult`)<br>• Tokenized code UI display panel | • `lex_scanner.py`<br>• `lex_data.py`<br>• `ui_token_panel.py`<br>• `sample.iol`<br>• `test_lex_scanner.py`<br>• `DOCUMENTATION_MemberB.md` |
| **John Andrei Manalo** | **Member C**:<br>Errors | **Lexical Error Detection**<br>• Detection of invalid lexemes (`ERR_LEX`) during scanning<br>• Tracking malformed words and exact line numbers<br>• Compiler UI console panel with color-coded success/error feedback<br>• Diagnostic error message formatting<br>• Error detection test cases | • `ui_console_panel.py`<br>• Error handling in `lex_scanner.py`<br>• Error tests in `test_lex_scanner.py`<br>• `DOCUMENTATION_MemberC.md` |
| **Mark Jaily Pena** | **Member D**:<br>Variables and Docs | **Table of Variables, Docs & Packaging**<br>• Table of variables UI panel (`VariablePanel`) with vertical scrolling<br>• Treeview table formatting with name and type columns<br>• Identifier collection with duplicate suppression (no duplicate rows)<br>• Variable panel unit test suite (`test_ui_variable_panel.py`)<br>• Comprehensive documentation compilation (`DOCUMENTATION.md`)<br>• Packaging and executable build | • `ui_variable_panel.py`<br>• `test_ui_variable_panel.py`<br>• `DOCUMENTATION.md`<br>• `DOCUMENTATION_MemberD.md` |

---

## 5. Language Specification & Token Definition

### 5.1 Official Keywords
```text
IOL   LOI   INT   STR   INTO   IS   BEG   PRINT   NEWLN   ADD   SUB   MULT   DIV   MOD
```
*Note: IOL is strictly case-sensitive. Words in lowercase (such as `int` or `print`) are treated as identifiers (`IDENT`), not keywords.*

### 5.2 Token Mapping Rules
| Pattern / Lexeme | Token Name | Example |
|---|---|---|
| Reserved keywords | Exact keyword name | `INT` -> `INT`, `PRINT` -> `PRINT` |
| Letter followed by alphanumeric characters | `IDENT` | `num`, `count1`, `message` |
| One or more numeric digits | `INT_LIT` | `0`, `3`, `42` |
| Digits starting identifier, invalid characters, symbols | `ERR_LEX` | `2name`, `bad$`, `@`, `+`, `=` |

### 5.3 Token Stream Format (`.tkn`)
In the generated `.tkn` file, each lexeme from the original code is replaced by its token name, retaining the exact line numbers:
```text
Source Code (.iol):                 Token Stream (.tkn):
IOL                                 IOL
INT num IS 3                        INT IDENT IS INT_LIT
PRINT num                           PRINT IDENT
LOI                                 LOI
```

---

## 6. Build, Execution, and Packaging Guide

### 6.1 Running the Program Directly
Requirements: Python 3.8+ (standard library only; Tkinter is built-in).
```bash
python main_window.py
```

### 6.2 Running Automated Unit Tests
```bash
# Run all tests across the project
python -m unittest discover

# Or run individual test modules
python test_lex_scanner.py
python test_ui_variable_panel.py
```

### 6.3 Building the Standalone Executable
Using PyInstaller:
- **Windows**:
  ```cmd
  build.bat
  ```
  Generates `dist\LexicalAnalyzer.exe`.
- **Linux**:
  ```bash
  pyinstaller --onefile --windowed --name LexicalAnalyzer main_window.py
  ```
  Generates `dist/LexicalAnalyzer`.

### 6.4 Creating the Submission Archive
Compress the required files into an archive named in alphabetical order of surnames:
**`Apolinario_DeArce_Manalo_Pena_PE02.zip`**
- Archive contents:
  1. Documentation file (`DOCUMENTATION.md` or PDF/DOCX)
  2. Complete source code files (`*.py`, `sample.iol`, `build.bat`, `CONTRACT.md`)
  3. Standalone executable file in `dist/`
