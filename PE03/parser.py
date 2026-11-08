"""Tokenizer and non-recursive predictive parser for PE03 (Member 2)."""

from file_validation import normalize_symbol
from parse_data import END_MARKER, ParseResult, ParseStep, ParseTable, Production


class Tokenizer:
    """Turn the input field into normalized grammar symbols."""

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Split *text* on whitespace and append the input end marker."""
        tokens = [normalize_symbol(token) for token in text.split()]
        return [token for token in tokens if token] + [END_MARKER]


class PredictiveParser:
    """A table-driven LL(1) parser using an explicit stack."""

    @staticmethod
    def parse(
        productions: list[Production],
        table: ParseTable,
        tokens: list[str] | str,
    ) -> ParseResult:
        """Parse tokens and return every state and the final outcome."""
        input_buffer = (
            Tokenizer.tokenize(tokens)
            if isinstance(tokens, str)
            else PredictiveParser._normalize_tokens(tokens)
        )

        by_id = {production.id: production for production in productions}
        start = by_id.get(1)
        if start is None:
            return ParseResult(
                valid=False,
                error_message="Production 1 is required to determine the start symbol.",
            )

        stack = [start.non_terminal, END_MARKER]
        non_terminals = set(table.non_terminals)
        seen_states: set[tuple[tuple[str, ...], int]] = set()
        position = 0

        # Each row shows the stack and input AFTER an action, together with
        # the action that produced them. The first row is the starting state,
        # so it has no action (this matches the handout's sample output).
        steps = [PredictiveParser._row(stack, input_buffer, position, "")]

        while stack:
            top = stack[0]
            lookahead = input_buffer[position]
            state = (tuple(stack), position)
            if state in seen_states:
                return PredictiveParser._error(
                    steps,
                    "Error: parser detected a non-consuming recursive production.",
                )
            seen_states.add(state)

            if top == END_MARKER:
                if lookahead != END_MARKER:
                    return PredictiveParser._error(
                        steps, f"Error: expected {END_MARKER}, found {lookahead}."
                    )
                stack.pop(0)
                position += 1
                steps.append(PredictiveParser._row(stack, input_buffer, position, "Match $"))
                if position < len(input_buffer):
                    return PredictiveParser._error(
                        steps, "Error: input remains after the end marker."
                    )
                return ParseResult(steps=steps, valid=True)

            if top not in non_terminals:
                if top == lookahead:
                    stack.pop(0)
                    position += 1
                    steps.append(
                        PredictiveParser._row(stack, input_buffer, position, f"Match {top}")
                    )
                    continue
                return PredictiveParser._error(
                    steps, f"Error: expected {top}, found {lookahead}."
                )

            production_id = table.get(top, lookahead)
            if production_id is None:
                return PredictiveParser._error(
                    steps, f"Error: no production for {top} with input {lookahead}."
                )

            production = by_id.get(production_id)
            if production is None:
                return PredictiveParser._error(
                    steps,
                    f"Error: parse table refers to missing production {production_id}.",
                )

            stack.pop(0)
            stack[:0] = production.rhs
            steps.append(
                PredictiveParser._row(stack, input_buffer, position, f"Output {production}")
            )

        if position < len(input_buffer):
            return PredictiveParser._error(
                steps, "Error: input remains after the stack is empty."
            )
        return ParseResult(steps=steps, valid=True)

    @staticmethod
    def _row(
        stack: list[str], input_buffer: list[str], position: int, action: str
    ) -> ParseStep:
        """One solution row: the current stack, the remaining input, and the action."""
        return ParseStep(" ".join(stack), " ".join(input_buffer[position:]), action)

    @staticmethod
    def _normalize_tokens(tokens: list[str]) -> list[str]:
        input_buffer = [normalize_symbol(token) for token in tokens if token]
        if not input_buffer or input_buffer[-1] != END_MARKER:
            input_buffer.append(END_MARKER)
        return input_buffer

    @staticmethod
    def _error(steps: list[ParseStep], message: str) -> ParseResult:
        """Stop parsing: keep the steps so far and add one extra error row.

        The error row has empty stack and input columns, with the message in
        the Action column, as the handout asks.
        """
        steps.append(ParseStep("", "", message))
        return ParseResult(
            steps=steps,
            valid=False,
            error_message=message.removeprefix("Error: ").strip(),
        )