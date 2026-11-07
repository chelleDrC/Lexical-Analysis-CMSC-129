# Member 2: Tokenizer and Predictive Parser

## `parser.py`

`Tokenizer.tokenize(text)` splits the input field on any whitespace, normalizes
curly apostrophes with the shared `normalize_symbol` helper, removes empty
tokens, and appends the end marker `$`.

`PredictiveParser.parse(productions, table, tokens)` implements the
non-recursive, table-driven LL(1) algorithm. The stack is represented with its
top on the left, matching the required solution-table format. It starts with
the start symbol (the non-terminal of production 1) and `$`.

For each step:

1. A matching terminal is popped and records `Match x`.
2. A non-terminal looks up the current input symbol in the parse table,
   records `Output A > rhs`, and pushes the production's RHS in reverse
   order.
3. An empty production is popped without pushing symbols.
4. A blank table cell or terminal mismatch stops parsing and appends an
   `Error:` row.

The final `$` match is recorded. `ParseResult.valid` is `True` only after that
match; otherwise `error_message` contains the reason parsing stopped.