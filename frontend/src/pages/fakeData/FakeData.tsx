import { FormEvent, useEffect, useState } from "react";

import {
  ApiError,
  downloadBlob,
  getJson,
  postForBlob,
  postJson,
} from "../../api/client";
import { FakePreviewResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";

interface Field {
  name: string;
  type: string;
}

const DEFAULT_FIELDS: Field[] = [
  { name: "name", type: "name" },
  { name: "email", type: "email" },
  { name: "phone", type: "phone" },
];

export function FakeData() {
  const [fields, setFields] = useState<Field[]>(DEFAULT_FIELDS);
  const [num, setNum] = useState(10);
  const [types, setTypes] = useState<string[]>([]);
  const [preview, setPreview] = useState<FakePreviewResponse["records"] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    getJson<{ types: string[] }>("/api/fake-data/types")
      .then((r) => setTypes(r.types.sort()))
      .catch(() => setTypes([]));
  }, []);

  function update(i: number, patch: Partial<Field>) {
    setFields((prev) => prev.map((f, idx) => (idx === i ? { ...f, ...patch } : f)));
  }
  function addField() {
    setFields((prev) => [...prev, { name: `field_${prev.length + 1}`, type: "name" }]);
  }
  function removeField(i: number) {
    setFields((prev) => prev.filter((_, idx) => idx !== i));
  }

  async function generate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setPending(true);
    try {
      const body = {
        field_names: fields.map((f) => f.name),
        field_types: fields.map((f) => f.type),
        num_records: num,
      };
      const r = await postJson<FakePreviewResponse>("/api/fake-data/preview", body);
      setPreview(r.records);
    } catch (err) {
      setError(err instanceof ApiError || err instanceof Error ? err.message : "Failed");
    } finally {
      setPending(false);
    }
  }

  async function exportData(format: "json" | "csv") {
    setError(null);
    try {
      const body = {
        field_names: fields.map((f) => f.name),
        field_types: fields.map((f) => f.type),
        num_records: num,
        format,
      };
      const { blob, filename } = await postForBlob("/api/fake-data/export", body);
      downloadBlob(blob, filename);
    } catch (err) {
      setError(err instanceof ApiError || err instanceof Error ? err.message : "Failed");
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Fake Data Generator"
        description="Build a synthetic dataset of up to 1000 records and export it."
      />
      <form onSubmit={generate} className="card space-y-4">
        <div className="space-y-2">
          {fields.map((f, i) => (
            <div key={i} className="grid gap-2 sm:grid-cols-[1fr,1fr,auto]">
              <input
                className="input"
                value={f.name}
                onChange={(e) => update(i, { name: e.target.value })}
                placeholder="Field name"
              />
              <select
                className="input"
                value={f.type}
                onChange={(e) => update(i, { type: e.target.value })}
              >
                {types.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="btn-ghost text-rose-600 dark:text-rose-400"
                onClick={() => removeField(i)}
                disabled={fields.length === 1}
              >
                Remove
              </button>
            </div>
          ))}
          <button type="button" className="btn-secondary" onClick={addField}>
            + Add field
          </button>
        </div>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="label" htmlFor="num">
              Number of records
            </label>
            <input
              id="num"
              type="number"
              min={1}
              max={1000}
              className="input w-32"
              value={num}
              onChange={(e) => setNum(Math.max(1, Math.min(1000, Number(e.target.value) || 1)))}
            />
          </div>
          <button type="submit" disabled={pending} className="btn-primary">
            {pending ? "Generating…" : "Preview"}
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => exportData("json")}
            disabled={pending}
          >
            Download JSON
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => exportData("csv")}
            disabled={pending}
          >
            Download CSV
          </button>
        </div>
      </form>

      <ErrorBanner message={error} />

      {preview && preview.length > 0 && (
        <section className="card overflow-x-auto p-0">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800 text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800">
              <tr>
                {Object.keys(preview[0]).map((k) => (
                  <th
                    key={k}
                    className="px-3 py-2 text-left font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300"
                  >
                    {k}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {preview.map((row, i) => (
                <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800">
                  {Object.keys(preview[0]).map((k) => (
                    <td key={k} className="px-3 py-1 font-mono text-slate-800 dark:text-slate-100">
                      {String(row[k] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
