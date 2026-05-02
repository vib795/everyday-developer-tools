import difflib
from typing import Literal

from typing_extensions import TypedDict


class DiffHunk(TypedDict):
    tag: Literal["equal", "replace", "delete", "insert"]
    left: list[str]
    right: list[str]
    left_start: int
    right_start: int


def structured_diff(text1: str, text2: str) -> list[DiffHunk]:
    a = text1.splitlines()
    b = text2.splitlines()
    matcher = difflib.SequenceMatcher(a=a, b=b)
    out: list[DiffHunk] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        out.append(
            DiffHunk(
                tag=tag,  # type: ignore[arg-type]
                left=a[i1:i2],
                right=b[j1:j2],
                left_start=i1,
                right_start=j1,
            )
        )
    return out


def html_diff(text1: str, text2: str) -> str:
    return difflib.HtmlDiff().make_file(
        text1.splitlines(), text2.splitlines(), fromdesc="Text 1", todesc="Text 2"
    )
