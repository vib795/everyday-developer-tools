import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { CronNextRunsResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function CronNext() {
  const [expression, setExpr] = useState("0 9 * * 1-5");
  const [count, setCount] = useState(5);
  const [timezone, setTz] = useState("UTC");

  const { data, error, pending, run } = useApi((body: object) =>
    postJson<CronNextRunsResponse>("/api/calc/cron-next", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ expression, count, timezone });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Cron Next Runs" description="See when a cron expression will fire next." />
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
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="count">How many runs</label>
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
          <div>
            <label className="label" htmlFor="tz">Timezone (IANA)</label>
            <input
              id="tz"
              className="input"
              placeholder="UTC, America/New_York, …"
              value={timezone}
              onChange={(e) => setTz(e.target.value)}
            />
          </div>
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Computing…" : "Show next runs"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && data.error && (
        <div role="alert" className="rounded-md border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 px-4 py-3 text-sm text-rose-900 dark:text-rose-200">
          {data.error}
        </div>
      )}
      {data && !data.error && data.runs.length > 0 && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
            Next {data.runs.length} run{data.runs.length === 1 ? "" : "s"}
          </h3>
          <CodeBlock value={data.runs.join("\n")} />
        </section>
      )}
    </div>
  );
}
