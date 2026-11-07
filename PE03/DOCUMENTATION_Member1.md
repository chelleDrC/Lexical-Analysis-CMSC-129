# Member 1: File Loading and Validation

## Program Description

The program is a non-recursive predictive parser (table-driven LL(1) parser) with a graphical interface. The user loads two files with the single Load button:

- a productions file (`.prod`) that lists the grammar's productions, and
- a parse table file (`.ptbl`) that gives the production to use for each non-terminal and input symbol.

Both files must have the same name, for example `rules.prod` and `rules.ptbl`. The user then types a sequence of tokens in the INPUT field, separated by any whitespace, and clicks Parse. The parser pushes `$` and the start symbol (the non-terminal of production 1) on a stack, appends `$` to the input, and runs the table-driven algorithm. Each step is shown in a table with three columns: the stack, the remaining input, and the action (`Output A > rhs` or `Match x`).

The result is VALID if the input is accepted by the grammar and INVALID otherwise. The steps are saved to `outname_prodname.prsd` in the same folder as the input files, where `outname` is asked from the user. For an invalid input, the file holds the steps up to the point where parsing stops, followed by one row with the error in the Action column. All three file types (`.prod`, `.ptbl`, `.prsd`) use CSV format.

## Module Description

The file loading module reads the `.prod` and `.ptbl` files, checks that they are correct, and turns them into the shared data classes that the parser (Member 2) and the controller (Member 4) use. The module has no GUI code. Every problem is reported by raising `LoadError` with a message that can be shown to the user as is, for example:

```
rules.prod, line 4: missing columns. Expected 3 columns (number, non-terminal, production), found 2.
```

| File | Contents |
|---|---|
| `parse_data.py` | Shared data classes: `Production`, `ParseTable`, `ParseStep`, `ParseResult`. Constants `EMPTY_SYMBOL` (`e`) and `END_MARKER` (`$`). |
| `csv_reader.py` | `CsvReader`: reads a file and splits it into CSV rows. |
| `production_loader.py` | `ProductionLoader`: reads a `.prod` file into a list of `Production`. |
| `parse_table_loader.py` | `ParseTableLoader`: reads a `.ptbl` file into a `ParseTable`. |
| `file_validation.py` | `LoadError`, apostrophe normalization, extension checks, the file name match check, and the check that the two files agree. |
| `rules.prod`, `rules.ptbl` | Sample grammar from the handout. |
| `test_loaders.py` | Unit tests for this module. |

### Data Classes (`parse_data.py`)

| Class | Fields and methods | Description |
|---|---|---|
| `Production` | `id`, `non_terminal`, `rhs` | One production. `rhs` is a list of symbols. The empty production `e` is stored as `[]`. |
| | `is_empty` | `True` when `rhs` is empty. |
| | `rhs_text` | Right-hand side as text, `e` for the empty production. |
| | `str(p)` | `"E' > + T E'"`, the text used in the `Output` action. |
| `ParseTable` | `terminals` | Column labels in file order, including `$`. |
| | `non_terminals` | Row labels in file order. |
| | `table` | `table[non_terminal][terminal]` is a production number. Blank cells are not stored. |
| | `get(nt, t)` | Production number, or `None` for a blank cell or an unknown symbol. |
| | `cell_text(nt, t)` | Production number as text, or `""` for a blank cell. Used by the GUI. |
| `ParseStep` | `stack`, `input`, `action` | One row of the solution (filled by Member 2). |
| `ParseResult` | `steps`, `valid`, `error_message` | Result of a parse (filled by Member 2). |

### `CsvReader`

| Function | Description |
|---|---|
| `read_text(path)` | Reads the file. Tries UTF-8 (removing the byte order mark that Excel or Notepad may add) and then Windows-1252, so curly apostrophes saved by Excel are read correctly. Raises `LoadError` if the file is missing, is a folder, cannot be opened, or is not a text file. |
| `read_rows(path)` | Returns `(line_number, cells)` for every row that is not blank. Rows that are empty or only commas are skipped. Uses Python's `csv` module in strict mode, so quoted cells such as `"id , L"` work and an unclosed quote is reported as malformed CSV. Raises `LoadError` for an empty file. |

### `ProductionLoader`

| Function | Description |
|---|---|
| `load(path)` | Checks the `.prod` extension, reads the rows, and returns a list of `Production` in file order. Raises `LoadError` if a production number is used twice or there is no production 1. |
| `start_symbol(productions)` | The non-terminal of production 1, which is the start symbol. |
| `parse_row(cells, where)` | Turns one row into a `Production`. `where` is the file name and line number used in error messages. |

Rules for each row:

- Exactly three columns: number, non-terminal, production. Extra empty columns at the end (trailing commas) are ignored. Fewer columns is "missing columns". More non-empty columns is "too many columns".
- The number must be a whole number of 1 or higher.
- The non-terminal must be one symbol.
- The production is split on whitespace (one or more spaces or tabs). It must not be blank. `e` means empty and must be the only symbol.
- All symbols have their apostrophes normalized.

### `ParseTableLoader`

| Function | Description |
|---|---|
| `load(path)` | Checks the `.ptbl` extension, reads the header and rows, and returns a `ParseTable`. Raises `LoadError` if a non-terminal has two rows or there are no rows. |
| `parse_header(cells, where)` | Returns the list of terminals from the first row. |
| `parse_row(cells, terminals, where)` | Returns the non-terminal and its filled cells for one row. |

Rules:

- The top-left cell is ignored. It is normally empty.
- Empty cells at the end of the header or a row (trailing commas) are ignored.
- The header must list at least one terminal, with no empty name in the middle, no duplicates, and must include `$`.
- Each row starts with a non-terminal. A row with fewer cells than the header has blank cells at the end. A row with more non-empty cells than the header is "too many columns".
- Each cell is a production number of 1 or higher, or blank.
- All symbols have their apostrophes normalized.

### `file_validation.py`

| Function | Description |
|---|---|
| `LoadError` | Exception for any file problem. `str(error)` is the message to show. |
| `normalize_symbol(text)` | Strips spaces and turns `’`, `‘`, `′`, `´`, and `` ` `` into `'`. The handout's sample mixes `E'` and `E’`; without this, table lookups fail. Member 2's Tokenizer should use it on input tokens too. |
| `file_type(path)` | Returns `".prod"` or `".ptbl"` from the extension (any case). Raises `LoadError` for other files. Used by the single Load button. |
| `check_extension(path, expected)` | Raises `LoadError` if the extension is not `expected`. |
| `base_name(path)` | File name without folder and extension. |
| `names_match(prod_path, ptbl_path)` | `True` when the names match, ignoring case (Windows file names are not case sensitive). The folders may differ. |
| `check_matching_names(prod_path, ptbl_path)` | Raises `LoadError` when the names differ, e.g. `a.prod` and `b.ptbl`. |
| `check_compatible(productions, table)` | Raises `LoadError` when a table cell names a production that does not exist or belongs to another non-terminal, a non-terminal has no table row, a production uses `$`, or a production uses a symbol that is neither a non-terminal nor a table terminal. |
| `check_pair(prod_path, productions, ptbl_path, table)` | `check_matching_names` and then `check_compatible`. |

## Interface for Members 2, 3, and 4

```python
from file_validation import LoadError, file_type, check_pair, normalize_symbol, PROD_EXT
from production_loader import ProductionLoader
from parse_table_loader import ParseTableLoader

try:
    if file_type(path) == PROD_EXT:
        productions = ProductionLoader.load(path)   # list[Production]
    else:
        table = ParseTableLoader.load(path)         # ParseTable
except LoadError as e:
    show_message(str(e))   # keep the previously loaded file

# Before enabling Parse, once both files are loaded:
try:
    check_pair(prod_path, productions, ptbl_path, table)
except LoadError as e:
    show_message(str(e))   # do not enable Parse
```

- Member 2: get the start symbol with `ProductionLoader.start_symbol(productions)`. Look up a production by number with `{p.id: p for p in productions}`. Use `str(production)` for the `Output` action and `table.get(nt, t)` for the lookup.
- Member 3: draw the parse table with `table.terminals` as the column headers, `table.non_terminals` as the rows, and `table.cell_text(nt, t)` for each cell. Draw the productions with `p.id`, `p.non_terminal`, and `p.rhs_text`.
- Member 4: a failed load raises `LoadError` before anything is returned, so the old file stays loaded as long as the result is only assigned on success.

## Notes on the Handout's Sample

- The sample writes `7,F,(E)` with no spaces. Since symbols are separated by spaces, `(E)` would be read as one symbol, and `check_compatible` rejects it because `(E)` is not a terminal. The shipped `rules.prod` uses `7,F,( E )`.
- The sample mixes `E'` and `E’`. Both are read as `E'`.

## Testing

Run from the PE03 folder:

```bash
python -m unittest test_loaders -v
```

64 tests, all passing.

| Area | Cases |
|---|---|
| Mismatched file names | `a.prod` with `b.ptbl` is rejected; `rules.prod` with `Rules.ptbl` in another folder is accepted; names with dots. |
| Malformed files | No production 1, empty file, blank-only file, binary file, unclosed quote, text after a closing quote, non-number production number or cell, number 0, duplicate production number, duplicate table row, duplicate terminal, missing `$`, empty non-terminal, non-terminal with a space, blank production, `e` mixed with other symbols, missing file, folder instead of file. |
| Bad extension | `.txt` or `.csv` file; a `.ptbl` given to the production loader and the reverse. |
| Missing columns | Production row with 2 columns; production row with 4 columns; header with no terminals; header with a gap; table row with too many cells. |
| Apostrophes | `’`, `‘`, and `′` in both files, in UTF-8 and in Windows-1252; the sample's mixed `E'` and `E’` loads as a compatible pair. |
| Format details | Empty top-left cell, text in the top-left cell, trailing commas, short table rows, spaces around cells, tabs and repeated spaces in a production, Windows line endings, byte order mark, quoted comma terminal. |
| Pair check | Sample pair accepted; unknown production number in a cell; production of the wrong non-terminal; missing table row; production symbol not in the table; `(E)` without spaces. |
