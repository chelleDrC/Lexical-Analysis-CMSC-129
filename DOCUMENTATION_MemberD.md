# Member D: Variables, Documentation, and Packaging

**Member:** Mark Jaily Pena  
**Role:** Variables and Docs feat — Table of variables panel, identifier collection with duplicate suppression, documentation compilation, and release packaging.

---

## 1. Description

Member D is responsible for:
1. **Table of Variables UI Panel (`VariablePanel` in `ui_variable_panel.py`)**: A dedicated graphical table that displays all unique variables recognized during lexical analysis alongside their data types (e.g., `INT` or `STR`).
2. **Identifier Collection and Deduplication**: Ensuring each identifier is recorded with its corresponding type, strictly preventing duplicate rows in the variable table even when variables are referenced multiple times.
3. **Documentation Compilation**: Compiling the unified program documentation covering all team modules, control flow, and work distribution.
4. **Project Packaging**: Managing the creation of the standalone executable (`LexicalAnalyzer.exe` / `LexicalAnalyzer`) and building the official submission ZIP archive (`Apolinario_DeArce_Manalo_Pena_PE02.zip`).

---

## 2. Table of Variables Panel (`ui_variable_panel.py`)

The `VariablePanel` class inherits from `tk.LabelFrame` and is positioned in the lower-right quadrant of the main compiler UI.

### Key Features:
- **`ttk.Treeview` Table**: Formats variables into clean, styled columns:
  - **Variable Name**: Left-aligned column displaying identifier names.
  - **Data Type**: Centered column displaying the variable type (`INT`, `STR`).
- **Vertical Scrollbar (`ttk.Scrollbar`)**: Allows smooth scrolling when large numbers of variables are declared in source files.
- **Duplicate Prevention**: Filters incoming variables against an internal `seen_names` set so that each identifier appears exactly once.
- **Dynamic Content Replacement**: Empties prior results upon each compilation run to guarantee fresh, synchronized state.

### `VariablePanel` Functions

| Function | Parameters | Return Type | Description |
|---|---|---|---|
| `__init__(parent)` | `parent`: Parent widget (`ttk.PanedWindow`) | `None` | Initializes the LabelFrame container, Treeview with columns `("name", "type")`, headings, and vertical scrollbar. |
| `show_variables(variables)` | `variables`: List of `Variable` objects or `(name, type)` tuples | `None` | Clears existing table rows, iterates through incoming variables, deduplicates by identifier name, and populates unique rows into the Treeview. |
| `clear()` | None | `None` | Removes all rows from the Treeview table. |
| `get_variables()` | None | `list[tuple[str, str]]` | Returns a list of `(name, type)` tuples currently rendered in the table (used for testing and inspection). |
| `count()` | None | `int` | Returns the number of unique variable entries currently shown in the table. |

---

## 3. Data Structure: `Variable` (`lex_data.py`)

```python
class Variable:
    """A declared variable: its name and data type."""

    def __init__(self, name, type):
        self.name = name  # Identifier string (e.g. "num")
        self.type = type  # Keyword type name (e.g. "INT" or "STR")
```

---

## 4. Deduplication Logic

In accordance with the program specification:
> *"Collects each identifier with its type into the variable table (no duplicates)."*

Deduplication occurs at two layers for maximum robustness:
1. **Scanner Layer (`lex_scanner.py`)**: `_collect_variables()` tracks declared variable names in `declared_names = set()` when scanning declarations like `INT x` and `STR msg`.
2. **UI Panel Layer (`ui_variable_panel.py`)**: `VariablePanel.show_variables()` maintains `seen_names = set()`. If multiple entries or subsequent uses share the same identifier name, subsequent occurrences are omitted from the Treeview.

```python
seen_names = set()
for variable in variables:
    var_name = variable.name
    var_type = variable.type
    if var_name and var_name not in seen_names:
        seen_names.add(var_name)
        self.table.insert("", tk.END, values=(var_name, var_type))
```

---

## 5. Control Flow Integration

```text
User clicks 'Compile Code' (main_window.py)
  │
  ▼
MainWindow.compile_code()
  │
  ├─► Scanner.analyze(source_code)
  │     └─► Collects tokens, errors, and variables
  │
  ├─► ConsolePanel.show_result(result.errors)
  │
  ├─► VariablePanel.show_variables(result.variables)
  │     ├─► Clear previous table rows
  │     ├─► Filter duplicates by identifier name
  │     └─► Insert unique (name, type) rows into Treeview
  │
  ├─► TokenPanel.show_tokens([]) (cleared until requested)
  └─► MainWindow.write_token_file(result.tokens)
```

---

## 6. Unit Testing (`test_ui_variable_panel.py`)

A comprehensive test suite was implemented in `test_ui_variable_panel.py`:

| Test Method | Objective | Result |
|---|---|---|
| `test_initial_state_is_empty` | Verifies that a newly created table has 0 rows. | Passed |
| `test_show_variables_displays_entries` | Verifies correct population of multiple `Variable` objects. | Passed |
| `test_show_variables_deduplicates_identifiers` | Validates that duplicate variable names are excluded. | Passed |
| `test_show_variables_replaces_old_content` | Confirms old table data is wiped before displaying new data. | Passed |
| `test_show_variables_with_empty_list_clears_table` | Ensures passing an empty list resets the table. | Passed |
| `test_clear_method_removes_all_rows` | Confirms explicit `clear()` removes all entries. | Passed |

---

## 7. Packaging & Distribution

### Building the Standalone Executable
- **Windows**: Run `build.bat`
  ```cmd
  pyinstaller --onefile --windowed --name LexicalAnalyzer main_window.py
  ```
  Produces `dist\LexicalAnalyzer.exe`.
- **Linux**:
  ```bash
  pyinstaller --onefile --windowed --name LexicalAnalyzer main_window.py
  ```
  Produces `dist/LexicalAnalyzer`.

### Creating the Submission ZIP Archive
Create the submission ZIP archive named according to the group members' surnames:
**`Apolinario_DeArce_Manalo_Pena_PE02.zip`**

Contains:
- Master documentation (`DOCUMENTATION.md` or PDF/DOCX)
- Program source code files (`main_window.py`, `lex_scanner.py`, `lex_data.py`, `ui_*.py`, etc.)
- Program executable (`dist/LexicalAnalyzer.exe` or `dist/LexicalAnalyzer`)
- Sample input file (`sample.iol`) and test suites
