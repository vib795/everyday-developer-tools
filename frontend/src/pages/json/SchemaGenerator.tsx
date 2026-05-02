import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { JsonSchemaResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function SchemaGenerator() {
  const [json_input, setJsonInput] = useState("");
  const [conditionals, setConditionals] = useState("");

  const { data, error, pending, run } = useApi(
    (body: { json_input: string; conditionals: unknown[] | null }) =>
      postJson<JsonSchemaResponse>("/api/json/schema", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    let parsed: unknown[] | null = null;
    try {
      parsed = conditionals.trim() ? (JSON.parse(conditionals) as unknown[]) : null;
    } catch (err) {
      alert("Conditionals must be valid JSON. " + (err as Error).message);
      return;
    }
    run({ json_input, conditionals: parsed });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="JSON Schema Generator"
        description="Generate a draft-04 JSON Schema from a JSON sample."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="json_input">
            JSON input
          </label>
          <textarea
            id="json_input"
            rows={8}
            className="input font-mono"
            value={json_input}
            onChange={(e) => setJsonInput(e.target.value)}
          />
        </div>
        <div>
          <label className="label" htmlFor="conditionals">
            Conditionals (optional, JSON array of <code>{`{path, condition}`}</code>)
          </label>
          <textarea
            id="conditionals"
            rows={4}
            className="input font-mono"
            value={conditionals}
            onChange={(e) => setConditionals(e.target.value)}
            placeholder='[{"path": "address.zip", "condition": {"type": "string"}}]'
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Generating…" : "Generate schema"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Generated JSON Schema</h3>
          <CodeBlock value={JSON.stringify(data.schema, null, 2)} showLineNumbers />
        </section>
      )}
    </div>
  );
}
