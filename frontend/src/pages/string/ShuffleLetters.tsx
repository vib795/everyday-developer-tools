import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { ShuffleResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function ShuffleLetters() {
  const [text, setText] = useState("");
  const { data, error, pending, run } = useApi((body: { text: string }) =>
    postJson<ShuffleResponse>("/api/string/shuffle", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Shuffle Letters" />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="text">
            Text
          </label>
          <input
            id="text"
            className="input"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Shuffling…" : "Shuffle"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Shuffled Text</h3>
          <CodeBlock value={data.value} />
        </section>
      )}
    </div>
  );
}
