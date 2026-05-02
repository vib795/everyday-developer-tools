import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { JwtResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function JwtViewer() {
  const [jwt_token, setToken] = useState("");
  const [secret_key, setSecret] = useState("");
  const { data, error, pending, run } = useApi(
    (body: { jwt_token: string; secret_key: string }) =>
      postJson<JwtResponse>("/api/encoding/jwt", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ jwt_token, secret_key });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="JWT Viewer" description="Decode an HS256 JWT." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="token">
            JWT Token
          </label>
          <textarea
            id="token"
            rows={4}
            className="input font-mono"
            value={jwt_token}
            onChange={(e) => setToken(e.target.value)}
          />
        </div>
        <div>
          <label className="label" htmlFor="secret">
            Secret Key
          </label>
          <input
            id="secret"
            className="input font-mono"
            value={secret_key}
            onChange={(e) => setSecret(e.target.value)}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Decoding…" : "Decode"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          {data.error ? (
            <p className="rounded bg-rose-50 px-3 py-2 text-sm text-rose-900">{data.error}</p>
          ) : (
            <>
              <h3 className="mb-2 text-sm font-semibold text-slate-700">Decoded JWT</h3>
              <CodeBlock value={JSON.stringify(data.decoded, null, 2)} />
            </>
          )}
        </section>
      )}
    </div>
  );
}
