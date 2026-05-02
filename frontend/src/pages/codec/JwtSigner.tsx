import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { JwtSignResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Algo = "HS256" | "HS384" | "HS512";

export function JwtSigner() {
  const [payload, setPayload] = useState('{\n  "sub": "user-123",\n  "iat": 0\n}');
  const [secret, setSecret] = useState("");
  const [algorithm, setAlgo] = useState<Algo>("HS256");

  const { data, error, pending, run } = useApi((body: object) =>
    postJson<JwtSignResponse>("/api/codec/jwt/sign", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ payload, secret, algorithm });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="JWT Signer" description="Sign a payload with HS256/384/512." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="payload">Payload (JSON)</label>
          <textarea
            id="payload"
            rows={8}
            className="input font-mono"
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="secret">Secret</label>
            <input
              id="secret"
              type="password"
              className="input font-mono"
              value={secret}
              onChange={(e) => setSecret(e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="algo">Algorithm</label>
            <select
              id="algo"
              className="input"
              value={algorithm}
              onChange={(e) => setAlgo(e.target.value as Algo)}
            >
              <option value="HS256">HS256</option>
              <option value="HS384">HS384</option>
              <option value="HS512">HS512</option>
            </select>
          </div>
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Signing…" : "Sign"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && data.error && (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {data.error}
        </div>
      )}
      {data && data.token && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Signed token</h3>
          <CodeBlock value={data.token} />
        </section>
      )}
    </div>
  );
}
