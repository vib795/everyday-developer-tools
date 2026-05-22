import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { ColumnExtractorResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function ColumnExtractor() {
  const [text, setText] = useState("");
  const [column, setColumn] = useState(1);
  const [delimiter, setDelimiter] = useState(",");

  const { data, error, pending, run } = useApi(
    (body: { text: string; column_number: number; delimiter: string }) =>
      postJson<ColumnExtractorResponse>("/api/string/columns", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text, column_number: column, delimiter });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Column Extractor" description="Pull a column out of delimited text." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="text">
            Text
          </label>
          <textarea
            id="text"
            rows={6}
            className="input font-mono"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="a,b,c&#10;d,e,f"
          />
        </div>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="label" htmlFor="col">
              Column number (1-based)
            </label>
            <input
              id="col"
              type="number"
              min={1}
              className="input w-32"
              value={column}
              onChange={(e) => setColumn(Math.max(1, Number(e.target.value) || 1))}
            />
          </div>
          <div>
            <label className="label" htmlFor="delim">
              Delimiter
            </label>
            <input
              id="delim"
              className="input w-24 font-mono"
              value={delimiter}
              onChange={(e) => setDelimiter(e.target.value)}
            />
          </div>
          <button type="submit" disabled={pending} className="btn-primary">
            {pending ? "Extracting…" : "Extract"}
          </button>
        </div>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Extracted Columns</h3>
          <CodeBlock value={data.columns.join("\n")} />
        </section>
      )}
    </div>
  );
}
