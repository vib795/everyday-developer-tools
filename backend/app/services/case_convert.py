def tokens(text: str) -> list[str]:
    """Split mixed-case / delimited identifiers into lowercase word tokens."""
    words: list[str] = []
    run: list[str] = []
    kind = ""  # "upper" | "lower" | "digit"

    def flush() -> None:
        if run:
            words.append("".join(run).lower())
            run.clear()

    for ch in text:
        if not ch.isascii():
            new = ""
        elif ch.isupper():
            new = "upper"
        elif ch.islower():
            new = "lower"
        elif ch.isdigit():
            new = "digit"
        else:
            new = ""
        if not new:
            flush()
            kind = ""
            continue
        if new == "lower" and kind == "upper":
            # a capital starting a word continues the run ("Hello"); an acronym
            # keeps its last capital for the next word: "HTTPServer" -> "HTTP", "Server"
            if len(run) > 1:
                last = run.pop()
                flush()
                run.append(last)
        elif new != kind:
            flush()
        run.append(ch)
        kind = new
    flush()
    return words


def to_case(text: str, style: str) -> str:
    words = tokens(text)
    if not words:
        return ""
    if style == "camel":
        return words[0] + "".join(w.capitalize() for w in words[1:])
    if style == "pascal":
        return "".join(w.capitalize() for w in words)
    if style == "snake":
        return "_".join(words)
    if style == "kebab":
        return "-".join(words)
    if style == "constant":
        return "_".join(w.upper() for w in words)
    if style == "title":
        return " ".join(w.capitalize() for w in words)
    if style == "sentence":
        return words[0].capitalize() + (" " + " ".join(words[1:]) if len(words) > 1 else "")
    if style == "lower":
        return " ".join(words)
    if style == "upper":
        return " ".join(w.upper() for w in words)
    if style == "dot":
        return ".".join(words)
    if style == "path":
        return "/".join(words)
    raise ValueError(f"unknown case style: {style}")
