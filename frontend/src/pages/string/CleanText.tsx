import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { CleanTextResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Mode = "preserve" | "collapse";

export function CleanText() {
  const [text, setText] = useState("");
  const [mode, setMode] = useState<Mode>("preserve");
  const { data, error, pending, run } = useApi(
    (body: { text: string; collapse_spaces: boolean }) =>
      postJson<CleanTextResponse>("/api/string/clean", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text, collapse_spaces: mode === "collapse" });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Clean Text"
        description="Strip leading/trailing whitespace, hidden characters, and control codes. Case and internal whitespace are preserved."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="mode"
              checked={mode === "preserve"}
              onChange={() => setMode("preserve")}
            />
            Preserve internal whitespace
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="mode"
              checked={mode === "collapse"}
              onChange={() => setMode("collapse")}
            />
            Collapse runs of spaces (keep newlines)
          </label>
        </div>
        <div>
          <label className="label" htmlFor="text">
            Text
          </label>
          <textarea
            id="text"
            rows={6}
            className="input"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Cleaning…" : "Clean"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Cleaned Text</h3>
          <CodeBlock value={data.cleaned} />
        </section>
      )}
    </div>
  );
}
