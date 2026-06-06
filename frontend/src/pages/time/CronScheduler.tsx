import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { CronResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

interface State {
  minute: string;
  hour: string;
  day_of_month: string;
  month: string;
  day_of_week: string;
}

const FIELDS: { key: keyof State; label: string; help: string }[] = [
  { key: "minute", label: "Minute", help: "0–59" },
  { key: "hour", label: "Hour", help: "0–23" },
  { key: "day_of_month", label: "Day of month", help: "1–31" },
  { key: "month", label: "Month", help: "1–12 or JAN-DEC" },
  { key: "day_of_week", label: "Day of week", help: "0–6 or SUN-SAT" },
];

export function CronScheduler() {
  const [state, setState] = useState<State>({
    minute: "*",
    hour: "*",
    day_of_month: "*",
    month: "*",
    day_of_week: "*",
  });

  const { data, error, pending, run } = useApi((body: State) =>
    postJson<CronResponse>("/api/time/cron", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run(state);
  }

  return (
    <div className="space-y-6">
      <PageHeader title="CRON Scheduler" description="Build a CRON expression visually." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          {FIELDS.map((f) => (
            <div key={f.key}>
              <label className="label" htmlFor={f.key}>
                {f.label} <span className="text-xs text-slate-500 dark:text-slate-400">({f.help})</span>
              </label>
              <input
                id={f.key}
                className="input font-mono"
                value={state[f.key]}
                onChange={(e) => setState({ ...state, [f.key]: e.target.value })}
              />
            </div>
          ))}
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Generating…" : "Generate expression"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">CRON Expression</h3>
          <CodeBlock value={data.expression} />
        </section>
      )}
    </div>
  );
}
