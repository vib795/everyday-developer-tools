import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { TextStats } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

const ROWS: { key: keyof TextStats; label: string; format?: (v: number) => string }[] = [
  { key: "num_chars", label: "Characters" },
  { key: "num_chars_no_space", label: "Characters (no spaces)" },
  { key: "num_words", label: "Words" },
  { key: "num_unique_words", label: "Unique words" },
  {
    key: "percent_unique_words",
    label: "% unique words",
    format: (v) => `${v.toFixed(1)}%`,
  },
  { key: "num_lines", label: "Lines" },
  { key: "num_sentences", label: "Sentences" },
  { key: "length_shortest_word", label: "Shortest word length" },
  { key: "length_longest_word", label: "Longest word length" },
  { key: "avg_word_length", label: "Avg word length", format: (v) => v.toFixed(2) },
];

export function TextStatistics() {
  const [text, setText] = useState("");
  const { data, error, pending, run } = useApi((body: { text: string }) =>
    postJson<TextStats>("/api/string/stats", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Text Statistics" />
      <form onSubmit={onSubmit} className="card space-y-4">
        <textarea
          rows={8}
          className="input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste text here…"
        />
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Calculating…" : "Calculate"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Text Statistics</h3>
          <dl className="grid gap-3 sm:grid-cols-2">
            {ROWS.map((row) => (
              <div key={row.key} className="rounded border border-slate-200 p-3">
                <dt className="text-xs uppercase tracking-wide text-slate-500">{row.label}</dt>
                <dd className="text-base font-semibold text-slate-900">
                  {row.format ? row.format(data[row.key] as number) : data[row.key]}
                </dd>
              </div>
            ))}
          </dl>
        </section>
      )}
    </div>
  );
}
