import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { JsonSampleResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function SampleGenerator() {
  const [schema_input, setSchemaInput] = useState("");
  const { data, error, pending, run } = useApi((body: { schema_input: string }) =>
    postJson<JsonSampleResponse>("/api/json/sample", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ schema_input });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="JSON Sample Generator"
        description="Generate sample data conforming to a JSON Schema."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="schema_input">
            JSON Schema
          </label>
          <textarea
            id="schema_input"
            rows={10}
            className="input font-mono"
            value={schema_input}
            onChange={(e) => setSchemaInput(e.target.value)}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Generating…" : "Generate sample"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Generated Sample JSON</h3>
          <CodeBlock value={JSON.stringify(data.sample, null, 2)} showLineNumbers />
        </section>
      )}
    </div>
  );
}
