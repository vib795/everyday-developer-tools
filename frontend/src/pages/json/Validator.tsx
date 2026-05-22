import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { JsonValidateResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function Validator() {
  const [json_input, setJsonInput] = useState("");
  const [schema_input, setSchemaInput] = useState("");
  const { data, error, pending, run } = useApi(
    (body: { json_input: string; schema_input: string | null }) =>
      postJson<JsonValidateResponse>("/api/json/validate", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ json_input, schema_input: schema_input.trim() || null });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="JSON Validator" description="Validate JSON, optionally against a schema." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="json_input">
            JSON
          </label>
          <textarea
            id="json_input"
            rows={8}
            className="input font-mono"
            value={json_input}
            onChange={(e) => setJsonInput(e.target.value)}
            placeholder='{"name": "value"}'
          />
        </div>
        <div>
          <label className="label" htmlFor="schema_input">
            Schema (optional)
          </label>
          <textarea
            id="schema_input"
            rows={6}
            className="input font-mono"
            value={schema_input}
            onChange={(e) => setSchemaInput(e.target.value)}
            placeholder='{"type": "object", "required": ["name"]}'
          />
        </div>
        <div className="flex items-center gap-3">
          <button type="submit" disabled={pending} className="btn-primary">
            {pending ? "Validating…" : "Validate"}
          </button>
        </div>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card space-y-3">
          <p
            className={
              data.valid
                ? "rounded bg-emerald-50 dark:bg-emerald-950/40 px-3 py-2 text-sm text-emerald-900 dark:text-emerald-200"
                : "rounded bg-rose-50 dark:bg-rose-950/40 px-3 py-2 text-sm text-rose-900 dark:text-rose-200"
            }
          >
            {data.message}
          </p>
          {data.error_details && <p className="text-xs text-slate-600 dark:text-slate-300">{data.error_details}</p>}
          {data.formatted_json && (
            <div>
              <h3 className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-200">Formatted JSON</h3>
              <CodeBlock value={data.formatted_json} showLineNumbers />
            </div>
          )}
        </section>
      )}
    </div>
  );
}
