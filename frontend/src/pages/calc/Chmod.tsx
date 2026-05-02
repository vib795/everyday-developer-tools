import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { ChmodResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function Chmod() {
  const [value, setValue] = useState("755");
  const { data, error, pending, run } = useApi((body: object) =>
    postJson<ChmodResponse>("/api/calc/chmod", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ value });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="chmod Calculator" description="Convert between numeric (755) and symbolic (rwxr-xr-x) Unix permissions." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="val">Mode</label>
          <input
            id="val"
            className="input font-mono"
            placeholder='e.g. "755" or "rwxr-xr-x"'
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Calculating…" : "Calculate"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && data.error && (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {data.error}
        </div>
      )}
      {data && !data.error && (
        <section className="card text-sm">
          <dl className="grid grid-cols-[100px_1fr] gap-y-2">
            <dt className="text-slate-500">Numeric</dt>
            <dd className="font-mono">{data.numeric}</dd>
            <dt className="text-slate-500">Symbolic</dt>
            <dd className="font-mono">{data.symbolic}</dd>
          </dl>
        </section>
      )}
    </div>
  );
}
