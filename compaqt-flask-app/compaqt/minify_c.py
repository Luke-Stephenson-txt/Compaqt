from enum import Enum

class State(Enum):
    NORMAL = 0
    LINE_COMMENT = 1
    BLOCK_COMMENT = 2
    STRING = 3
    CHAR = 4
    PREPROCESSOR = 5

OPERATORS = sorted([
    ">>=", "<<=", "++", "--", "->", "==", "!=", "<=", ">=",
    "&&", "||", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=",
    "<<", ">>",
    "+", "-", "*", "/", "%", "=",
    "<", ">", "!", "~",
    "&", "|", "^",
    "?", ":", ",", ";",
    "(", ")", "[", "]", "{", "}"
], key=len, reverse=True)

def is_ident_char(c):
    return c.isalnum() or c == "_"

def minify_c(code: str) -> str:
    """Minify C code by removing comments and unnecessary whitespace."""
    out = []
    i = 0
    n = len(code)
    state = State.NORMAL
    at_line_start = True

    while i < n:
        c = code[i]

        if state == State.NORMAL:
            # Preprocessor
            if at_line_start and c == "#":
                state = State.PREPROCESSOR
                out.append(c)
                i += 1
                at_line_start = False
                continue

            # Comments
            if c == "/" and i + 1 < n:
                if code[i + 1] == "/":
                    state = State.LINE_COMMENT
                    i += 2
                    continue
                elif code[i + 1] == "*":
                    state = State.BLOCK_COMMENT
                    i += 2
                    continue

            # Strings / chars
            if c == '"':
                state = State.STRING
                out.append(c)
                i += 1
                continue

            if c == "'":
                state = State.CHAR
                out.append(c)
                i += 1
                continue

            # Whitespace & newline handling
            if c.isspace():
                if out:
                    prev = out[-1]
                    nextc = code[i + 1] if i + 1 < n else ""

                    if is_ident_char(prev) and is_ident_char(nextc):
                        out.append(" ")

                if c == "\n":
                    at_line_start = True
                i += 1
                continue

            # Operators (greedy)
            matched = False
            for op in OPERATORS:
                if code.startswith(op, i):
                    out.append(op)
                    i += len(op)
                    matched = True
                    break

            if matched:
                at_line_start = False
                continue

            # Normal character
            out.append(c)
            at_line_start = False
            i += 1

        elif state == State.LINE_COMMENT:
            if c == "\n":
                state = State.NORMAL
                at_line_start = True
            i += 1

        elif state == State.BLOCK_COMMENT:
            if c == "*" and i + 1 < n and code[i + 1] == "/":
                state = State.NORMAL
                i += 2
            else:
                i += 1

        elif state == State.STRING:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(code[i + 1])
                i += 2
            elif c == '"':
                state = State.NORMAL
                i += 1
            else:
                i += 1

        elif state == State.CHAR:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(code[i + 1])
                i += 2
            elif c == "'":
                state = State.NORMAL
                i += 1
            else:
                i += 1

        elif state == State.PREPROCESSOR:
            out.append(c)
            if c == "\n":
                state = State.NORMAL
                at_line_start = True
            i += 1

    return "".join(out)
