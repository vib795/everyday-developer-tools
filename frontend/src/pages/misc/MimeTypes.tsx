import { useEffect, useMemo, useState } from "react";

import { getJson } from "../../api/client";
import { MimeTypeListResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";

export function MimeTypes() {
  const [data, setData] = useState<MimeTypeListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");

  useEffect(() => {
    getJson<MimeTypeListResponse>("/api/misc/mime-types")
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "load failed"));
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    const needle = q.trim().toLowerCase();
    if (!needle) return data.mime_types;
    return data.mime_types.filter(
      (m) =>
        m.type.toLowerCase().includes(needle) ||
        m.extensions.some((e) => e.toLowerCase().includes(needle)) ||
        m.description.toLowerCase().includes(needle),
    );
  }, [data, q]);

  return (
    <div className="space-y-6">
      <PageHeader title="MIME Types" description="Common Content-Type / file-extension reference." />
      <input
        className="input"
        placeholder="Search by type, extension, or description…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      <ErrorBanner message={error} />
      {data && (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 dark:text-slate-400">
              <th className="py-1 pr-4 font-medium">Type</th>
              <th className="py-1 pr-4 font-medium">Extensions</th>
              <th className="py-1 font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((m) => (
              <tr key={m.type} className="border-t border-slate-200 dark:border-slate-800">
                <td className="py-1 pr-4 font-mono">{m.type}</td>
                <td className="py-1 pr-4 font-mono text-slate-600 dark:text-slate-300">
                  {m.extensions.map((e) => `.${e}`).join(", ") || "—"}
                </td>
                <td className="py-1 text-slate-700 dark:text-slate-200">{m.description}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={3} className="py-2 text-slate-500 dark:text-slate-400">No matches.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
