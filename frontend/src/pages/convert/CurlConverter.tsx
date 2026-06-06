import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { CurlConvertResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

const SAMPLE = `curl -X POST https://api.example.com/users \\
  -H "Content-Type: application/json" \\
  -d '{"name":"alice","age":30}'`;

export function CurlConverter() {
  const [curl, setCurl] = useState(SAMPLE);
  const { data, error, pending, run } = useApi((body: object) =>
    postJson<CurlConvertResponse>("/api/convert/curl", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ curl });
  }

  const langs: { key: keyof typeof data extends never ? string : string; label: string }[] = [
    { key: "fetch", label: "fetch (JS)" },
    { key: "axios", label: "axios" },
    { key: "requests", label: "requests (Python)" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="cURL Converter" description="Translate a curl command to fetch, axios, or Python requests." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="curl">curl command</label>
          <textarea
            id="curl"
            rows={8}
            className="input font-mono"
            value={curl}
            onChange={(e) => setCurl(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Converting…" : "Convert"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && data.error && (
        <div role="alert" className="rounded-md border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 px-4 py-3 text-sm text-rose-900 dark:text-rose-200">
          {data.error}
        </div>
      )}
      {data && !data.error && (
        <div className="space-y-4">
          {langs.map(({ key, label }) => (
            <section key={key} className="card">
              <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">{label}</h3>
              <CodeBlock value={data.outputs[key] || ""} />
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
