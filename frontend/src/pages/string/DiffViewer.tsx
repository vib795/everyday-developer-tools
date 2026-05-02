import { FormEvent, useState } from "react";
import clsx from "clsx";

import { postJson } from "../../api/client";
import { DiffHunk, DiffResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

const TAG_STYLE: Record<string, string> = {
  equal: "bg-white",
  insert: "bg-emerald-50",
  delete: "bg-rose-50",
  replace: "bg-amber-50",
};

function renderSide(hunks: DiffHunk[], side: "left" | "right") {
  const rows: { lineNumber: number; text: string; tag: string }[] = [];
  for (const h of hunks) {
    const lines = side === "left" ? h.left : h.right;
    const start = side === "left" ? h.left_start : h.right_start;
    const isPad =
      (side === "left" && h.tag === "insert") || (side === "right" && h.tag === "delete");
    if (lines.length === 0 && (h.tag === "insert" || h.tag === "delete")) {
      const otherLen = (side === "left" ? h.right : h.left).length;
      for (let i = 0; i < otherLen; i++) rows.push({ lineNumber: -1, text: "", tag: h.tag });
      continue;
    }
    lines.forEach((text, i) =>
      rows.push({ lineNumber: isPad ? -1 : start + i + 1, text, tag: h.tag }),
    );
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

  const left = data ? renderSide(data.hunks, "left") : [];
  const right = data ? renderSide(data.hunks, "right") : [];
  const rowCount = Math.max(left.length, right.length);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Diff Viewer"
        description="Compare two pieces of text side-by-side."
      />
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
          <div className="grid grid-cols-2 divide-x divide-slate-200 font-mono text-xs">
            <div className="bg-slate-50 px-3 py-2 text-[11px] font-semibold uppercase text-slate-500">
              Text 1
            </div>
            <div className="bg-slate-50 px-3 py-2 text-[11px] font-semibold uppercase text-slate-500">
              Text 2
            </div>
            {Array.from({ length: rowCount }).map((_, i) => {
              const l = left[i] ?? { lineNumber: -1, text: "", tag: "equal" };
              const r = right[i] ?? { lineNumber: -1, text: "", tag: "equal" };
              return (
                <Row key={`row-${i}`} l={l} r={r} />
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}

interface Row {
  lineNumber: number;
  text: string;
  tag: string;
}
function Row({ l, r }: { l: Row; r: Row }) {
  return (
    <>
      <div className={clsx("flex gap-3 px-3 py-1", TAG_STYLE[l.tag])}>
        <span className="w-8 select-none text-right text-slate-400">
          {l.lineNumber > 0 ? l.lineNumber : ""}
        </span>
        <span className="whitespace-pre-wrap break-all">{l.text}</span>
      </div>
      <div className={clsx("flex gap-3 px-3 py-1", TAG_STYLE[r.tag])}>
        <span className="w-8 select-none text-right text-slate-400">
          {r.lineNumber > 0 ? r.lineNumber : ""}
        </span>
        <span className="whitespace-pre-wrap break-all">{r.text}</span>
      </div>
    </>
  );
}
