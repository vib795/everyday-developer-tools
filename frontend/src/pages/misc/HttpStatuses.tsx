import { useEffect, useMemo, useState } from "react";

import { getJson } from "../../api/client";
import { HttpStatusListResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";

function bandColor(code: number): string {
  if (code < 200) return "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200";
  if (code < 300) return "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-200";
  if (code < 400) return "bg-sky-100 dark:bg-sky-950/60 text-sky-800 dark:text-sky-200";
  if (code < 500) return "bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-200";
  return "bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-200";
}

export function HttpStatuses() {
  const [data, setData] = useState<HttpStatusListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");

  useEffect(() => {
    getJson<HttpStatusListResponse>("/api/misc/http-statuses")
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "load failed"));
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    const needle = q.trim().toLowerCase();
    if (!needle) return data.statuses;
    return data.statuses.filter(
      (s) =>
        String(s.code).includes(needle) ||
        s.name.toLowerCase().includes(needle) ||
        s.description.toLowerCase().includes(needle),
    );
  }, [data, q]);

  return (
    <div className="space-y-6">
      <PageHeader title="HTTP Status Codes" description="Searchable reference of common HTTP status codes." />
      <input
        className="input"
        placeholder="Search by code, name, or description…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      <ErrorBanner message={error} />
      {data && (
        <ul className="space-y-2">
          {filtered.map((s) => (
            <li key={s.code} className="card flex items-start gap-4">
              <span className={`rounded px-2 py-1 text-sm font-mono ${bandColor(s.code)}`}>{s.code}</span>
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{s.name}</p>
                <p className="text-sm text-slate-600 dark:text-slate-300">{s.description}</p>
              </div>
            </li>
          ))}
          {filtered.length === 0 && <p className="text-sm text-slate-500 dark:text-slate-400">No matches.</p>}
        </ul>
      )}
    </div>
  );
}
