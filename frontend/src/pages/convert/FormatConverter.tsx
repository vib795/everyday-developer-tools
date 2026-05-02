import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { FormatConvertResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

const FORMATS = ["json", "yaml", "toml", "xml", "csv"] as const;
type Format = (typeof FORMATS)[number];

export function FormatConverter() {
  const [text, setText] = useState('{"name": "alice", "age": 30}');
  const [source, setSource] = useState<Format>("json");
  const [target, setTarget] = useState<Format>("yaml");

  const { data, error, pending, run } = useApi((body: object) =>
    postJson<FormatConvertResponse>("/api/convert/format", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text, source, target });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Format Converter"
        description="Convert between JSON, YAML, TOML, XML, and CSV."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="src">Source</label>
            <select
              id="src"
              className="input"
              value={source}
              onChange={(e) => setSource(e.target.value as Format)}
            >
              {FORMATS.map((f) => (
                <option key={f} value={f}>{f.toUpperCase()}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="tgt">Target</label>
            <select
              id="tgt"
              className="input"
              value={target}
              onChange={(e) => setTarget(e.target.value as Format)}
            >
              {FORMATS.map((f) => (
                <option key={f} value={f}>{f.toUpperCase()}</option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <label className="label" htmlFor="text">Input</label>
          <textarea
            id="text"
            rows={8}
            className="input font-mono"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={pending || source === target}>
          {pending ? "Converting…" : "Convert"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && data.error && (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {data.error}
        </div>
      )}
      {data && !data.error && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Output</h3>
          <CodeBlock value={data.output} />
        </section>
      )}
    </div>
  );
}
