import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { RandomStringResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function RandomString() {
  const [length, setLength] = useState(16);
  const { data, error, pending, run } = useApi((body: { length: number }) =>
    postJson<RandomStringResponse>("/api/string/random-string", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ length });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Random String Generator" />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="length">
            Length
          </label>
          <input
            id="length"
            type="number"
            min={1}
            max={4096}
            className="input w-32"
            value={length}
            onChange={(e) => setLength(Math.max(1, Number(e.target.value) || 1))}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Generating…" : "Generate"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Your Random String</h3>
          <CodeBlock value={data.value} />
        </section>
      )}
    </div>
  );
}
