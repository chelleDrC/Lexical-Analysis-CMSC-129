# Member C: Lexical Error Detection and Console

## Description

Member C is responsible for detecting invalid lexemes during lexical analysis, reporting their line numbers, and displaying appropriate messages in the compiler UI console panel (`ConsolePanel` in `ui_console_panel.py`).

## Responsibilities

1. Detect invalid or unsupported lexemes during scanning and classify them as `ERR_LEX`.
2. Record line numbers and unknown words using `LexError` objects.
3. Provide user-friendly feedback in the built-in compiler console.
4. Distinguish between successful analysis (green message) and lexical failure (red error list).

## Components

| Component | File | Description |
|---|---|---|
| `ConsolePanel` | `ui_console_panel.py` | Tkinter `LabelFrame` console displaying compilation status and error diagnostics. |
| Error detection logic | `lex_scanner.py` | Scanner routines (`_record_error`, `_consume_invalid_lexeme`) that flag invalid characters and words. |
| `LexError` | `lex_data.py` | Data structure holding `lexeme` and `line`. |

## Console Messages

### Success Message
When no lexical errors are present in the source code:
```text
Lexical analysis successful. No lexical errors found.
```
Displayed in green text in the console panel.

### Error Messages
When one or more lexical errors are detected:
```text
Lexical analysis failed. Found 2 lexical error(s):
ERR_LEX: unknown word '2name' at line 2
ERR_LEX: unknown word '@' at line 3
```
The header is displayed in bold red, and each error line is listed in red with its exact line number and unknown word.

## ConsolePanel Functions

| Function | Description |
|---|---|
| `__init__(parent)` | Initializes the console text box with colored tags (`success` in green, `error` in red, `heading` in bold). |
| `show_result(errors)` | Clears the console and displays either the success message or the formatted list of lexical errors. |
| `build_messages(errors)` | Static helper method that generates user-facing message strings from a list of `LexError` objects. |

## Error Detection Criteria

The scanner flags a lexeme as `ERR_LEX` if:
1. An identifier starts with a digit (e.g., `2name`, `123abc`).
2. An identifier or literal contains illegal symbols (e.g., `num$`, `3#`, `abc_def`).
3. An unsupported non-alphanumeric symbol is encountered (e.g., `@`, `+`, `=`, `"hello"`).
