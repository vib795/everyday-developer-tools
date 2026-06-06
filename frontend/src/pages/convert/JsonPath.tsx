import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { JsonPathResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

const SAMPLE = `{
  "users": [
    {"name": "alice", "age": 30, "tags": ["admin"]},
    {"name": "bob", "age": 25, "tags": ["user"]}
  ]
}`;

export function JsonPath() {
  const [json_text, setJson] = useState(SAMPLE);
  const [expression, setExpr] = useState("$.users[*].name");

  const { data, error, pending, run } = useApi((body: object) =>
    postJson<JsonPathResponse>("/api/convert/jsonpath", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ json_text, expression });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="JSONPath" description="Evaluate a JSONPath expression against a JSON document." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="expr">Expression</label>
          <input
            id="expr"
            className="input font-mono"
            value={expression}
            onChange={(e) => setExpr(e.target.value)}
          />
        </div>
        <div>
          <label className="label" htmlFor="doc">JSON</label>
          <textarea
            id="doc"
            rows={10}
            className="input font-mono"
            value={json_text}
            onChange={(e) => setJson(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Evaluating…" : "Evaluate"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && data.error && (
        <div role="alert" className="rounded-md border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 px-4 py-3 text-sm text-rose-900 dark:text-rose-200">
          {data.error}
        </div>
      )}
      {data && !data.error && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
            Matches ({data.matches.length})
          </h3>
          <CodeBlock value={JSON.stringify(data.matches, null, 2)} />
        </section>
      )}
    </div>
  );
}
