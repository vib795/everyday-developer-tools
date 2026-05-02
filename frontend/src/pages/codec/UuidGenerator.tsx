import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { UuidGenerateResponse, UuidInspectResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Version = "v1" | "v3" | "v4" | "v5" | "v7";

export function UuidGenerator() {
  const [version, setVersion] = useState<Version>("v4");
  const [count, setCount] = useState(5);
  const [namespace, setNamespace] = useState("dns");
  const [name, setName] = useState("");
  const [inspectValue, setInspectValue] = useState("");

  const gen = useApi((body: object) =>
    postJson<UuidGenerateResponse>("/api/codec/uuid/generate", body),
  );
  const ins = useApi((body: object) =>
    postJson<UuidInspectResponse>("/api/codec/uuid/inspect", body),
  );

  function onGenerate(e: FormEvent) {
    e.preventDefault();
    const body: Record<string, unknown> = { version, count };
    if (version === "v3" || version === "v5") {
      body.namespace = namespace;
      body.name = name;
    }
    gen.run(body);
  }

  function onInspect(e: FormEvent) {
    e.preventDefault();
    ins.run({ value: inspectValue });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="UUID" description="Generate and inspect UUIDs (v1, v3, v4, v5, v7)." />

      <form onSubmit={onGenerate} className="card space-y-4">
        <h2 className="text-base font-semibold text-slate-700">Generate</h2>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="label" htmlFor="version">Version</label>
            <select
              id="version"
              className="input"
              value={version}
              onChange={(e) => setVersion(e.target.value as Version)}
            >
              <option value="v1">v1 (timestamp + MAC)</option>
              <option value="v3">v3 (md5 namespace)</option>
              <option value="v4">v4 (random)</option>
              <option value="v5">v5 (sha1 namespace)</option>
              <option value="v7">v7 (time-ordered)</option>
            </select>
          </div>
          <div>
            <label className="label" htmlFor="count">Count</label>
            <input
              id="count"
              type="number"
              min={1}
              max={100}
              className="input"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value || "1", 10))}
            />
          </div>
        </div>
        {(version === "v3" || version === "v5") && (
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="ns">Namespace</label>
              <input
                id="ns"
                className="input"
                placeholder="dns / url / oid / x500 or a UUID"
                value={namespace}
                onChange={(e) => setNamespace(e.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="name">Name</label>
              <input
                id="name"
                className="input"
                placeholder="example.com"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          </div>
        )}
        <button type="submit" className="btn-primary" disabled={gen.pending}>
          {gen.pending ? "Generating…" : "Generate"}
        </button>
      </form>
      <ErrorBanner message={gen.error} />
      {gen.data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Generated</h3>
          <CodeBlock value={gen.data.values.join("\n")} />
        </section>
      )}

      <form onSubmit={onInspect} className="card space-y-4">
        <h2 className="text-base font-semibold text-slate-700">Inspect</h2>
        <div>
          <label className="label" htmlFor="inspect">UUID</label>
          <input
            id="inspect"
            className="input font-mono"
            placeholder="550e8400-e29b-41d4-a716-446655440000"
            value={inspectValue}
            onChange={(e) => setInspectValue(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-secondary" disabled={ins.pending}>
          {ins.pending ? "Inspecting…" : "Inspect"}
        </button>
      </form>
      <ErrorBanner message={ins.error} />
      {ins.data && (
        <section className="card text-sm">
          {ins.data.valid ? (
            <dl className="grid grid-cols-[140px_1fr] gap-y-2">
              <dt className="text-slate-500">Version</dt>
              <dd>{ins.data.version}</dd>
              <dt className="text-slate-500">Variant</dt>
              <dd>{ins.data.variant}</dd>
              <dt className="text-slate-500">Hex</dt>
              <dd className="font-mono">{ins.data.hex}</dd>
              <dt className="text-slate-500">URN</dt>
              <dd className="font-mono">{ins.data.urn}</dd>
              {ins.data.timestamp_iso && (
                <>
                  <dt className="text-slate-500">Timestamp</dt>
                  <dd className="font-mono">{ins.data.timestamp_iso}</dd>
                </>
              )}
            </dl>
          ) : (
            <p className="text-rose-700">Invalid UUID: {ins.data.error}</p>
          )}
        </section>
      )}
    </div>
  );
}
