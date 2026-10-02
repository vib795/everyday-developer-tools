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
            Secret Key <span className="font-normal text-slate-500">(optional)</span>
          </label>
          <input
            id="secret"
            className="input font-mono"
            value={secret_key}
            onChange={(e) => setSecret(e.target.value)}
          />
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Leave blank to inspect the payload without verifying the signature.
          </p>
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Decoding…" : "Decode"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          {data.error ? (
            <p className="rounded bg-rose-50 dark:bg-rose-950/40 px-3 py-2 text-sm text-rose-900 dark:text-rose-200">{data.error}</p>
          ) : (
            <>
              <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Decoded JWT</h3>
              {data.signature_verified ? (
                <p className="mb-2 rounded bg-emerald-50 dark:bg-emerald-950/40 px-3 py-2 text-sm text-emerald-900 dark:text-emerald-200">
                  Signature verified with the supplied secret.
                </p>
              ) : (
                <p className="mb-2 rounded bg-amber-50 dark:bg-amber-950/40 px-3 py-2 text-sm text-amber-900 dark:text-amber-200">
                  Signature <strong>not verified</strong> — no secret was supplied. Treat this
                  payload as untrusted; anyone can craft a token with these contents.
                </p>
              )}
              <CodeBlock value={JSON.stringify(data.decoded, null, 2)} />
            </>
          )}
        </section>
      )}
    </div>
  );
}
