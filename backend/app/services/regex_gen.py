import re

EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
PHONE = r"^\+?1?\d{10,15}$"
DATE = r"^\d{4}-\d{2}-\d{2}$"
SSN = r"^\d{3}-\d{2}-\d{4}$"


def detect_pattern(text_input: str) -> str:
    if re.match(EMAIL, text_input):
        return r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
    if re.match(PHONE, text_input):
        return r"\+?1?\d{10,15}"
    if re.match(DATE, text_input):
        return r"\d{4}-\d{2}-\d{2}"
    if re.match(SSN, text_input):
        return r"\d{3}-\d{2}-\d{4}"
    return generate_basic_pattern(text_input)


def generate_basic_pattern(text_input: str) -> str:
    char_types = {"lower": False, "upper": False, "digit": False, "special": set()}
    for char in text_input:
        if char.islower():
            char_types["lower"] = True
        elif char.isupper():
            char_types["upper"] = True
        elif char.isdigit():
            char_types["digit"] = True
        else:
            char_types["special"].add(re.escape(char))

    parts: list[str] = []
    if char_types["lower"]:
        parts.append("a-z")
    if char_types["upper"]:
        parts.append("A-Z")
    if char_types["digit"]:
        parts.append("0-9")
    if char_types["special"]:
        parts.append("".join(sorted(char_types["special"])))

    return f"[{''.join(parts)}]{{{len(text_input)}}}"
