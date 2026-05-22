import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { RegexGenerateResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function RegexGenerator() {
  const [text_input, setText] = useState("");
  const { data, error, pending, run } = useApi((body: { text_input: string }) =>
    postJson<RegexGenerateResponse>("/api/regex/generate", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text_input });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Regex Generator"
        description="Suggest a regex pattern for an input. Detects common formats."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="text_input">
            Sample text
          </label>
          <input
            id="text_input"
            className="input font-mono"
            value={text_input}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g. foo@bar.com or 2024-01-01"
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Generating…" : "Generate pattern"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Pattern</h3>
          <CodeBlock value={data.pattern} />
        </section>
      )}
    </div>
  );
}
