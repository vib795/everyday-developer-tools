import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { SimpleOutput } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function Parser() {
  const [input_json, setInput] = useState("");
  const { data, error, pending, run } = useApi((body: { input_json: string }) =>
    postJson<SimpleOutput>("/api/json/parse", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ input_json });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="JSON Parser" description="Beautify and pretty-print JSON." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="input_json">
            JSON
          </label>
          <textarea
            id="input_json"
            rows={10}
            className="input font-mono"
            value={input_json}
            onChange={(e) => setInput(e.target.value)}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Parsing…" : "Parse / Beautify"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Parsed JSON</h3>
          <CodeBlock value={data.output} showLineNumbers />
        </section>
      )}
    </div>
  );
}
