import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { CleanTextResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function CleanText() {
  const [text, setText] = useState("");
  const { data, error, pending, run } = useApi((body: { text: string }) =>
    postJson<CleanTextResponse>("/api/string/clean", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Clean Text"
        description="Collapse whitespace and capitalize sentences."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
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
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Cleaned Text</h3>
          <CodeBlock value={data.cleaned} />
        </section>
      )}
    </div>
  );
}
