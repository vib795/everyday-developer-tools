from typing import Literal

from typing_extensions import TypedDict


class DiffHunk(TypedDict):
    tag: Literal["equal", "replace", "delete", "insert"]
    left: list[str]
    right: list[str]
    left_start: int
    right_start: int


def _myers_ops(a: list[str], b: list[str]) -> list[str]:
    """Shortest edit script between ``a`` and ``b`` as a forward list of
    per-line operations ("equal" | "delete" | "insert").

    Implements the greedy O(ND) algorithm from Eugene W. Myers, "An O(ND)
    Difference Algorithm and Its Variations" (1986). "delete" consumes one
    line of ``a``; "insert" consumes one line of ``b``; "equal" consumes one
    of each. The kept ("equal") lines form a longest common subsequence, so
    the script is of minimum length.
    """
    n, m = len(a), len(b)
    if n == 0 and m == 0:
        return []

    # Forward pass. For each edit distance d, v maps a diagonal k (= x - y) to
    # the furthest x reachable with d edits. trace[d] snapshots v before the
    # round so the path can be recovered afterwards. v[1] = 0 seeds the origin.
    v: dict[int, int] = {1: 0}
    trace: list[dict[int, int]] = []
    for d in range(n + m + 1):
        trace.append(dict(v))
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[k - 1] < v[k + 1]):
                x = v[k + 1]  # move down  -> insert b[y]
            else:
                x = v[k - 1] + 1  # move right -> delete a[x]
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x, y = x + 1, y + 1  # follow the diagonal "snake" of equal lines
            v[k] = x
            if x >= n and y >= m:
                return _backtrack(trace, a, b)
    return _backtrack(trace, a, b)  # pragma: no cover - reached only if unbounded


def _backtrack(trace: list[dict[int, int]], a: list[str], b: list[str]) -> list[str]:
    """Walk the recorded furthest-reaching paths backwards, emitting one op per
    move: diagonal -> "equal", down -> "insert", right -> "delete"."""
    ops: list[str] = []
    x, y = len(a), len(b)
    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        if k == -d or (k != d and v[k - 1] < v[k + 1]):
            prev_k = k + 1
        else:
            prev_k = k - 1
        prev_x = v[prev_k]
        prev_y = prev_x - prev_k
        while x > prev_x and y > prev_y:
            ops.append("equal")
            x, y = x - 1, y - 1
        if d > 0:
            ops.append("insert" if x == prev_x else "delete")
        x, y = prev_x, prev_y
    ops.reverse()
    return ops


def structured_diff(text1: str, text2: str) -> list[DiffHunk]:
    a = text1.splitlines()
    b = text2.splitlines()
    ops = _myers_ops(a, b)

    hunks: list[DiffHunk] = []
    ia = ib = 0
    i = 0
    while i < len(ops):
        left_start, right_start = ia, ib
        left: list[str] = []
        right: list[str] = []
        if ops[i] == "equal":
            while i < len(ops) and ops[i] == "equal":
                left.append(a[ia])
                right.append(b[ib])
                ia, ib, i = ia + 1, ib + 1, i + 1
            tag: Literal["equal", "replace", "delete", "insert"] = "equal"
        else:
            # Coalesce a run of deletes/inserts into one hunk. A run with both
            # sides is a "replace" so the UI can align the changed lines.
            while i < len(ops) and ops[i] != "equal":
                if ops[i] == "delete":
                    left.append(a[ia])
                    ia += 1
                else:
                    right.append(b[ib])
                    ib += 1
                i += 1
            if left and right:
                tag = "replace"
            elif left:
                tag = "delete"
            else:
                tag = "insert"
        hunks.append(
            DiffHunk(
                tag=tag,
                left=left,
                right=right,
                left_start=left_start,
                right_start=right_start,
            )
        )
    return hunks
