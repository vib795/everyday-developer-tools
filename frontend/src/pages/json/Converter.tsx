import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { SimpleOutput } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Direction = "to_json" | "to_string";

export function Converter() {
  const [input_data, setInput] = useState("");
  const [direction, setDirection] = useState<Direction>("to_json");

  const { data, error, pending, run } = useApi(
    (body: { input_data: string; conversion_type: Direction }) =>
      postJson<SimpleOutput>("/api/json/convert", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ input_data, conversion_type: direction });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="JSON ⇄ String Converter"
        description="Convert a JSON object to an escaped string, or back."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="dir"
              checked={direction === "to_json"}
              onChange={() => setDirection("to_json")}
            />
            String → JSON
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="dir"
              checked={direction === "to_string"}
              onChange={() => setDirection("to_string")}
            />
            JSON → String
          </label>
        </div>
        <div>
          <label className="label" htmlFor="input_data">
            Input
          </label>
          <textarea
            id="input_data"
            rows={10}
            className="input font-mono"
            value={input_data}
            onChange={(e) => setInput(e.target.value)}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Converting…" : "Convert"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Output</h3>
          <CodeBlock value={data.output} showLineNumbers />
        </section>
      )}
    </div>
  );
}
