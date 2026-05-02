import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { Base64Response } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Op = "encode" | "decode";

export function Base64Page() {
  const [input_text, setInput] = useState("");
  const [operation, setOp] = useState<Op>("encode");
  const { data, error, pending, run } = useApi(
    (body: { input_text: string; operation: Op }) =>
      postJson<Base64Response>("/api/encoding/base64", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ input_text, operation });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Base64" description="Encode or decode UTF-8 text." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="op"
              checked={operation === "encode"}
              onChange={() => setOp("encode")}
            />
            Encode
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="op"
              checked={operation === "decode"}
              onChange={() => setOp("decode")}
            />
            Decode
          </label>
        </div>
        <div>
          <label className="label" htmlFor="input_text">
            Input
          </label>
          <textarea
            id="input_text"
            rows={6}
            className="input font-mono"
            value={input_text}
            onChange={(e) => setInput(e.target.value)}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Working…" : operation === "encode" ? "Encode" : "Decode"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Output</h3>
          <CodeBlock value={data.output} />
        </section>
      )}
    </div>
  );
}
