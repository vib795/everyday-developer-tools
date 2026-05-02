import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { QueryStringResponse, UrlCodecResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Op = "encode" | "decode";

export function UrlCodec() {
  const [text, setText] = useState("");
  const [operation, setOp] = useState<Op>("encode");
  const [component, setComponent] = useState(true);
  const [qsInput, setQsInput] = useState("");

  const codec = useApi((body: object) =>
    postJson<UrlCodecResponse>("/api/codec/url", body),
  );
  const parse = useApi((body: object) =>
    postJson<QueryStringResponse>("/api/codec/url/parse", body),
  );

  function onCodec(e: FormEvent) {
    e.preventDefault();
    codec.run({ text, operation, component });
  }

  function onParse(e: FormEvent) {
    e.preventDefault();
    parse.run({ text: qsInput });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="URL Codec" description="Encode/decode URLs and parse query strings." />

      <form onSubmit={onCodec} className="card space-y-4">
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input type="radio" name="op" checked={operation === "encode"} onChange={() => setOp("encode")} />
            Encode
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input type="radio" name="op" checked={operation === "decode"} onChange={() => setOp("decode")} />
            Decode
          </label>
          {operation === "encode" && (
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={component} onChange={(e) => setComponent(e.target.checked)} />
              Component-style (encodeURIComponent)
            </label>
          )}
        </div>
        <div>
          <label className="label" htmlFor="text">Input</label>
          <textarea
            id="text"
            rows={4}
            className="input font-mono"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={codec.pending}>
          {codec.pending ? "Working…" : operation === "encode" ? "Encode" : "Decode"}
        </button>
      </form>
      <ErrorBanner message={codec.error} />
      {codec.data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Output</h3>
          <CodeBlock value={codec.data.output} />
        </section>
      )}

      <form onSubmit={onParse} className="card space-y-4">
        <h2 className="text-base font-semibold text-slate-700">Query-string parser</h2>
        <div>
          <label className="label" htmlFor="qs">URL or query string</label>
          <input
            id="qs"
            className="input font-mono"
            placeholder="https://example.com/path?a=1&b=2"
            value={qsInput}
            onChange={(e) => setQsInput(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-secondary" disabled={parse.pending}>
          {parse.pending ? "Parsing…" : "Parse"}
        </button>
      </form>
      <ErrorBanner message={parse.error} />
      {parse.data && (
        <section className="card">
          {parse.data.base && (
            <p className="mb-2 text-xs text-slate-500">
              Base: <span className="font-mono text-slate-700">{parse.data.base}</span>
            </p>
          )}
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="py-1 pr-4 font-medium">Key</th>
                <th className="py-1 font-medium">Value</th>
              </tr>
            </thead>
            <tbody>
              {parse.data.params.map((p, i) => (
                <tr key={i} className="border-t border-slate-200">
                  <td className="py-1 pr-4 font-mono">{p.key}</td>
                  <td className="py-1 font-mono">{p.value}</td>
                </tr>
              ))}
              {parse.data.params.length === 0 && (
                <tr>
                  <td colSpan={2} className="py-2 text-slate-500">No parameters.</td>
                </tr>
              )}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
