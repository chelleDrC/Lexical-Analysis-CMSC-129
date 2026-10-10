# Member B: Lexical Analyzer (Scanner)

## Description

`Scanner` in `lex_scanner.py` performs lexical analysis for the official
Integer-Oriented Language (IOL). It scans source code from left to right,
identifies lexemes, and returns a `LexResult` containing tokens, lexical
errors, and declared variables.

IOL is case-sensitive. An identifier starts with a letter and continues with
letters or digits. Integer literals contain one or more digits. Operations
use words such as `ADD`, `SUB`, `MULT`, `DIV`, and `MOD`.

## Responsibilities

1. Scan source code character by character.
2. Recognize official IOL keywords.
3. Recognize identifiers and integer literals.
4. Report invalid lexemes as `ERR_LEX` with their line numbers.
5. Collect declarations of the form `INT name` and `STR name`.
6. Return the result through the shared `LexResult` contract.

Syntax and semantic checks, such as validating statement structure or
checking whether a variable was declared before use, belong to later compiler
phases.

## Official Token Categories

| Lexeme or pattern | Token |
|---|---|
| `IOL`, `LOI`, `INT`, `STR`, `INTO`, `IS`, `BEG`, `PRINT`, `NEWLN` | The keyword itself |
| `ADD`, `SUB`, `MULT`, `DIV`, `MOD` | The keyword itself |
| Letter followed by zero or more letters/digits | `IDENT` |
| One or more digits | `INT_LIT` |
| Invalid or unsupported lexeme | `ERR_LEX` |

The official IOL keyword set is:

```text
IOL LOI INT STR INTO IS BEG PRINT NEWLN ADD SUB MULT DIV MOD
```

## Data Structures

### Token

A `Token` contains:

- `type`: token name
- `lexeme`: original source text
- `line`: one-based source line number

### LexError

A `LexError` contains the invalid lexeme and its one-based line number.

### Variable

A `Variable` contains the declared variable name and type (`INT` or `STR`).

### LexResult

A `LexResult` contains the token list, error list, and variable list returned
by one scanner run.

## Scanner Algorithm

1. Split the source into lines.
2. Scan each line from left to right.
3. Skip whitespace.
4. If the next character is a letter, read the complete sequence of letters
   and digits. Classify it as an official keyword or `IDENT`.
5. If the next character is a digit, read the complete integer literal and
   classify it as `INT_LIT`.
6. If a digit is immediately followed by letters, report the whole sequence
   as an invalid lexeme because identifiers must begin with a letter.
7. Report unsupported non-whitespace sequences as `ERR_LEX`.
8. Collect declarations following `INT` or `STR`.
9. Return `LexResult`.

## Example

Source code:

```text
IOL
INT x IS 5
PRINT x
LOI
```

Tokenized output:

```text
IOL
INT IDENT IS INT_LIT
PRINT IDENT
LOI
```

## Error Handling

For this source:

```text
IOL
INT 2name
PRINT @
LOI
```

The scanner creates `ERR_LEX` tokens for `2name` and `@`, and records their
source lines in `LexError` objects. The console panel can then display those
errors.

## Variable Collection

For this source:

```text
INT num IS 3
STR message
```

the scanner returns:

```text
[("num", "INT"), ("message", "STR")]
```

The variable panel displays these values. The scanner does not execute input,
output, or arithmetic operations.

## Control Flow

```text
MainWindow.compile_code()
  -> Scanner.analyze(source_code)
  -> LexResult(tokens, errors, variables)
  -> ConsolePanel.show_result(errors)
  -> VariablePanel.show_variables(variables)
  -> write token types to the .tkn file
```

## Member B Contribution

Member B implements the lexical-analysis phase and tokenized-code output for
the IOL compiler project.
