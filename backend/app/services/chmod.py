"""chmod calculator: convert between numeric (e.g. "755") and symbolic ("rwxr-xr-x")."""
from __future__ import annotations

_BIT_NAMES = "rwx"


def numeric_to_symbolic(value: str) -> str:
    s = value.strip()
    if len(s) not in (3, 4):
        raise ValueError("Numeric mode must be 3 or 4 octal digits")
    if len(s) == 3:
        s = "0" + s
    try:
        digits = [int(c) for c in s]
    except ValueError as e:
        raise ValueError(f"Invalid octal digit: {e}") from e
    for d in digits:
        if d < 0 or d > 7:
            raise ValueError("Each digit must be 0-7")

    setuid, setgid, sticky = bool(digits[0] & 4), bool(digits[0] & 2), bool(digits[0] & 1)
    out: list[str] = []
    for i, perm in enumerate(digits[1:]):
        chars = [
            _BIT_NAMES[0] if perm & 4 else "-",
            _BIT_NAMES[1] if perm & 2 else "-",
            _BIT_NAMES[2] if perm & 1 else "-",
        ]
        if i == 0 and setuid:
            chars[2] = "s" if perm & 1 else "S"
        elif i == 1 and setgid:
            chars[2] = "s" if perm & 1 else "S"
        elif i == 2 and sticky:
            chars[2] = "t" if perm & 1 else "T"
        out.extend(chars)
    return "".join(out)


def symbolic_to_numeric(value: str) -> str:
    s = value.strip()
    if len(s) != 9:
        raise ValueError("Symbolic mode must be 9 chars (rwxrwxrwx)")
    setuid = setgid = sticky = False
    triplets: list[int] = []
    for i in range(3):
        chunk = s[i * 3 : i * 3 + 3]
        bits = 0
        if chunk[0] == "r":
            bits |= 4
        elif chunk[0] != "-":
            raise ValueError(f"Bad char at pos {i*3}: {chunk[0]!r}")
        if chunk[1] == "w":
            bits |= 2
        elif chunk[1] != "-":
            raise ValueError(f"Bad char at pos {i*3 + 1}: {chunk[1]!r}")
        c2 = chunk[2]
        if c2 in ("x", "s", "t"):
            bits |= 1
        elif c2 not in ("-", "S", "T"):
            raise ValueError(f"Bad char at pos {i*3 + 2}: {c2!r}")
        if i == 0 and c2 in ("s", "S"):
            setuid = True
        elif i == 1 and c2 in ("s", "S"):
            setgid = True
        elif i == 2 and c2 in ("t", "T"):
            sticky = True
        triplets.append(bits)
    special = (4 if setuid else 0) | (2 if setgid else 0) | (1 if sticky else 0)
    return f"{special}{triplets[0]}{triplets[1]}{triplets[2]}"


def chmod_calc(value: str) -> tuple[str, str]:
    """Return (numeric, symbolic) for either input form."""
    s = value.strip()
    if all(c in "01234567" for c in s) and 3 <= len(s) <= 4:
        sym = numeric_to_symbolic(s)
        num = s if len(s) == 4 else "0" + s
        return num, sym
    if len(s) == 9:
        num = symbolic_to_numeric(s)
        sym = numeric_to_symbolic(num)
        return num, sym
    raise ValueError("Use numeric (e.g. 755) or symbolic (e.g. rwxr-xr-x) mode")
