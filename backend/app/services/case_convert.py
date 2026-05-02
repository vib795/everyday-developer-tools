import re

_TOKENIZE = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")


def tokens(text: str) -> list[str]:
    """Split mixed-case / delimited identifiers into lowercase word tokens."""
    cleaned = text.replace("-", " ").replace("_", " ").replace(".", " ").replace("/", " ")
    parts = _TOKENIZE.findall(cleaned)
    return [p.lower() for p in parts if p]


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
        return (words[0].capitalize() + (" " + " ".join(words[1:]) if len(words) > 1 else ""))
    if style == "lower":
        return " ".join(words)
    if style == "upper":
        return " ".join(w.upper() for w in words)
    if style == "dot":
        return ".".join(words)
    if style == "path":
        return "/".join(words)
    raise ValueError(f"unknown case style: {style}")
