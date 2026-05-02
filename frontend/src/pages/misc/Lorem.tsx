import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { LoremResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Units = "paragraphs" | "sentences" | "words";

export function Lorem() {
  const [units, setUnits] = useState<Units>("paragraphs");
  const [count, setCount] = useState(3);
  const [startWithLorem, setStart] = useState(true);

  const { data, error, pending, run } = useApi((body: object) =>
    postJson<LoremResponse>("/api/misc/lorem", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ units, count, start_with_lorem: startWithLorem });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Lorem Ipsum" description="Filler text for layouts and prototypes." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="label" htmlFor="units">Units</label>
            <select
              id="units"
              className="input"
              value={units}
              onChange={(e) => setUnits(e.target.value as Units)}
            >
              <option value="paragraphs">Paragraphs</option>
              <option value="sentences">Sentences</option>
              <option value="words">Words</option>
            </select>
          </div>
          <div>
            <label className="label" htmlFor="count">Count</label>
            <input
              id="count"
              type="number"
              min={1}
              max={50}
              className="input"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value || "1", 10))}
            />
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={startWithLorem} onChange={(e) => setStart(e.target.checked)} />
              Start with “Lorem ipsum”
            </label>
          </div>
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Generating…" : "Generate"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Output</h3>
          <CodeBlock value={data.text} />
        </section>
      )}
    </div>
  );
}
