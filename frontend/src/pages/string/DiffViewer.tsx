import { FormEvent, useState } from "react";
import clsx from "clsx";

import { postJson } from "../../api/client";
import { DiffHunk, DiffResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type CellKind = "equal" | "add" | "del" | "empty";

/** A run of text within a line, flagged if it differs from the paired line. */
interface Segment {
  text: string;
  changed: boolean;
}

/** One half of a rendered row. "empty" means this side has no counterpart line. */
interface Cell {
  lineNumber: number;
  segments: Segment[];
  kind: CellKind;
}

interface RowPair {
  left: Cell;
  right: Cell;
}

const ROW_BG: Record<CellKind, string> = {
  equal: "bg-white dark:bg-slate-900",
  add: "bg-emerald-50 dark:bg-emerald-950/40",
  del: "bg-rose-50 dark:bg-rose-950/40",
  empty: "bg-slate-50 dark:bg-slate-900/60",
};

/** Deeper shade marking the words that actually changed inside a replaced line. */
const WORD_BG: Record<CellKind, string> = {
  equal: "",
  add: "bg-emerald-200 dark:bg-emerald-700/50",
  del: "bg-rose-200 dark:bg-rose-700/50",
  empty: "",
};

const MARKER: Record<CellKind, string> = {
  equal: "",
  add: "+",
  del: "-",
  empty: "",
};

const MARKER_COLOR: Record<CellKind, string> = {
  equal: "",
  add: "text-emerald-600 dark:text-emerald-400",
  del: "text-rose-600 dark:text-rose-400",
  empty: "",
};

const EMPTY_CELL: Cell = { lineNumber: -1, segments: [], kind: "empty" };

// Words, whitespace runs, and single punctuation marks. Joining the matches back
// together reproduces the line exactly, so segments never lose characters.
const TOKEN_RE = /[A-Za-z0-9_]+|\s+|[^A-Za-z0-9_\s]/g;

// Past this many tokens the O(n*m) LCS table costs more than the highlight is
// worth; such a pair still renders as a full-line change, just without the
// word-level shading.
const WORD_DIFF_LIMIT = 400;

function segment(text: string, changed: boolean): Segment[] {
  return text === "" ? [] : [{ text, changed }];
}

/** Append to `out`, merging into the previous run when the flag matches. */
function push(out: Segment[], text: string, changed: boolean) {
  const last = out[out.length - 1];
  if (last && last.changed === changed) last.text += text;
  else out.push({ text, changed });
}

/**
 * Split a replaced line pair into segments, flagging the tokens outside their
 * longest common subsequence — the intra-line highlight GitHub shows on a
 * side-by-side review.
 */
function wordDiff(oldLine: string, newLine: string): [Segment[], Segment[]] {
  const a = oldLine.match(TOKEN_RE) ?? [];
  const b = newLine.match(TOKEN_RE) ?? [];
  if (a.length > WORD_DIFF_LIMIT || b.length > WORD_DIFF_LIMIT) {
    return [segment(oldLine, true), segment(newLine, true)];
  }

  // lcs[i][j] = length of the longest common subsequence of a[i:] and b[j:].
  const lcs: number[][] = Array.from({ length: a.length + 1 }, () =>
    new Array<number>(b.length + 1).fill(0),
  );
  for (let i = a.length - 1; i >= 0; i--) {
    for (let j = b.length - 1; j >= 0; j--) {
      lcs[i][j] =
        a[i] === b[j] ? lcs[i + 1][j + 1] + 1 : Math.max(lcs[i + 1][j], lcs[i][j + 1]);
    }
  }

  const left: Segment[] = [];
  const right: Segment[] = [];
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) {
      push(left, a[i], false);
      push(right, b[j], false);
      i++;
      j++;
    } else if (lcs[i + 1][j] >= lcs[i][j + 1]) {
      push(left, a[i], true);
      i++;
    } else {
      push(right, b[j], true);
      j++;
    }
  }
  while (i < a.length) push(left, a[i++], true);
  while (j < b.length) push(right, b[j++], true);
  return [left, right];
}

/**
 * Flatten hunks into aligned row pairs. Every hunk contributes the same number
 * of rows to both columns — the short side gets blank filler — so the two
 * columns stay in step for the whole document.
 */
function buildRows(hunks: DiffHunk[]): RowPair[] {
  const rows: RowPair[] = [];
  for (const h of hunks) {
    if (h.tag === "equal") {
      h.left.forEach((text, i) => {
        rows.push({
          left: { lineNumber: h.left_start + i + 1, segments: segment(text, false), kind: "equal" },
          right: {
            lineNumber: h.right_start + i + 1,
            segments: segment(h.right[i], false),
            kind: "equal",
          },
        });
      });
      continue;
    }

    for (let i = 0; i < Math.max(h.left.length, h.right.length); i++) {
      const oldText: string | undefined = h.left[i];
      const newText: string | undefined = h.right[i];
      if (oldText !== undefined && newText !== undefined) {
        const [leftSegments, rightSegments] = wordDiff(oldText, newText);
        rows.push({
          left: { lineNumber: h.left_start + i + 1, segments: leftSegments, kind: "del" },
          right: { lineNumber: h.right_start + i + 1, segments: rightSegments, kind: "add" },
        });
      } else if (oldText !== undefined) {
        rows.push({
          left: { lineNumber: h.left_start + i + 1, segments: segment(oldText, false), kind: "del" },
          right: EMPTY_CELL,
        });
      } else if (newText !== undefined) {
        rows.push({
          left: EMPTY_CELL,
          right: {
            lineNumber: h.right_start + i + 1,
            segments: segment(newText, false),
            kind: "add",
          },
        });
      }
    }
  }
  return rows;
}

export function DiffViewer() {
  const [text1, setText1] = useState("");
  const [text2, setText2] = useState("");
  const { data, error, pending, run } = useApi((body: { text1: string; text2: string }) =>
    postJson<DiffResponse>("/api/string/diff", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text1, text2 });
  }

  const rows = data ? buildRows(data.hunks) : [];

  return (
    <div className="space-y-6">
      <PageHeader title="Diff Viewer" description="Compare two pieces of text side-by-side." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label" htmlFor="text1">
              Text 1
            </label>
            <textarea
              id="text1"
              rows={8}
              className="input font-mono"
              value={text1}
              onChange={(e) => setText1(e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="text2">
              Text 2
            </label>
            <textarea
              id="text2"
              rows={8}
              className="input font-mono"
              value={text2}
              onChange={(e) => setText2(e.target.value)}
            />
          </div>
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Diffing…" : "Compare"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card overflow-hidden p-0">
          <div className="grid grid-cols-2 divide-x divide-slate-200 dark:divide-slate-800 font-mono text-xs">
            <div className="bg-slate-50 dark:bg-slate-800 px-3 py-2 text-[11px] font-semibold uppercase text-slate-500 dark:text-slate-400">
              Text 1
            </div>
            <div className="bg-slate-50 dark:bg-slate-800 px-3 py-2 text-[11px] font-semibold uppercase text-slate-500 dark:text-slate-400">
              Text 2
            </div>
            {rows.map((row, i) => (
              <Row key={`row-${i}`} row={row} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function Row({ row }: { row: RowPair }) {
  return (
    <>
      <Side cell={row.left} />
      <Side cell={row.right} />
    </>
  );
}

function Side({ cell }: { cell: Cell }) {
  return (
    <div className={clsx("flex gap-2 px-3 py-1", ROW_BG[cell.kind])}>
      <span className="w-8 shrink-0 select-none text-right text-slate-400 dark:text-slate-500">
        {cell.lineNumber > 0 ? cell.lineNumber : ""}
      </span>
      <span
        className={clsx(
          "w-3 shrink-0 select-none text-center font-semibold",
          MARKER_COLOR[cell.kind],
        )}
      >
        {MARKER[cell.kind]}
      </span>
      <span className="whitespace-pre-wrap break-all">
        {cell.segments.map((s, i) =>
          s.changed ? (
            <mark key={i} className={clsx("rounded-sm text-inherit", WORD_BG[cell.kind])}>
              {s.text}
            </mark>
          ) : (
            <span key={i}>{s.text}</span>
          ),
        )}
      </span>
    </div>
  );
}
