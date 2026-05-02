import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { TimeConvertResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function TimeConverter() {
  const [time_input, setInput] = useState("");
  const { data, error, pending, run } = useApi((body: { time_input: string }) =>
    postJson<TimeConvertResponse>("/api/time/convert", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ time_input });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Time Converter"
        description="Accepts ISO-8601, epoch seconds/ms, or 'YYYY-MM-DD HH:MM:SS'."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="t">
            Input
          </label>
          <input
            id="t"
            className="input font-mono"
            value={time_input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="2024-01-01T12:00:00Z or 1700000000"
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Converting…" : "Convert"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <dl className="space-y-3">
            {Object.entries(data.output).map(([k, v]) => (
              <div key={k} className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:gap-3">
                <dt className="w-56 shrink-0 text-xs uppercase tracking-wide text-slate-500">
                  {k}
                </dt>
                <dd className="font-mono text-sm text-slate-800">
                  {Array.isArray(v) ? (
                    <ul className="space-y-1">
                      {v.map((line) => (
                        <li key={line}>{line}</li>
                      ))}
                    </ul>
                  ) : (
                    v
                  )}
                </dd>
              </div>
            ))}
          </dl>
        </section>
      )}
    </div>
  );
}
