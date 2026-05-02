import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { RandomNumberResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function RandomNumber() {
  const [min_val, setMin] = useState(0);
  const [max_val, setMax] = useState(100);

  const { data, error, pending, run } = useApi((body: { min_val: number; max_val: number }) =>
    postJson<RandomNumberResponse>("/api/string/random-number", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ min_val, max_val });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Random Number Generator" />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="label" htmlFor="min">
              Min
            </label>
            <input
              id="min"
              type="number"
              className="input w-32"
              value={min_val}
              onChange={(e) => setMin(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="label" htmlFor="max">
              Max
            </label>
            <input
              id="max"
              type="number"
              className="input w-32"
              value={max_val}
              onChange={(e) => setMax(Number(e.target.value))}
            />
          </div>
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Generating…" : "Generate"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <p className="text-xs uppercase tracking-wide text-slate-500">Your Random Number</p>
          <p className="font-mono text-2xl font-semibold">{data.value}</p>
        </section>
      )}
    </div>
  );
}
