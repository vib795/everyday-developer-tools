import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { HashResponse, HmacResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

const ALGOS = ["md5", "sha1", "sha256", "sha384", "sha512"] as const;
type Algo = (typeof ALGOS)[number];

export function HashTool() {
  const [text, setText] = useState("");
  const [algos, setAlgos] = useState<Algo[]>(["sha256"]);
  const [hmacSecret, setHmacSecret] = useState("");
  const [hmacAlgo, setHmacAlgo] = useState<Algo>("sha256");

  const hash = useApi((body: object) => postJson<HashResponse>("/api/codec/hash", body));
  const hmac = useApi((body: object) => postJson<HmacResponse>("/api/codec/hmac", body));

  function toggle(a: Algo) {
    setAlgos((prev) => (prev.includes(a) ? prev.filter((x) => x !== a) : [...prev, a]));
  }

  function onHash(e: FormEvent) {
    e.preventDefault();
    if (algos.length === 0) return;
    hash.run({ text, algorithms: algos });
  }

  function onHmac(e: FormEvent) {
    e.preventDefault();
    hmac.run({ text, secret: hmacSecret, algorithm: hmacAlgo });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Hash & HMAC" description="MD5, SHA-1/256/384/512 digests and HMAC." />

      <form onSubmit={onHash} className="card space-y-4">
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
        <div>
          <p className="label">Algorithms</p>
          <div className="flex flex-wrap gap-3 text-sm">
            {ALGOS.map((a) => (
              <label key={a} className="flex items-center gap-2">
                <input type="checkbox" checked={algos.includes(a)} onChange={() => toggle(a)} />
                {a}
              </label>
            ))}
          </div>
        </div>
        <button type="submit" className="btn-primary" disabled={hash.pending}>
          {hash.pending ? "Hashing…" : "Hash"}
        </button>
      </form>
      <ErrorBanner message={hash.error} />
      {hash.data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Digests</h3>
          <CodeBlock
            value={Object.entries(hash.data.digests)
              .map(([k, v]) => `${k}: ${v}`)
              .join("\n")}
          />
        </section>
      )}

      <form onSubmit={onHmac} className="card space-y-4">
        <h2 className="text-base font-semibold text-slate-700">HMAC</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="secret">Secret</label>
            <input
              id="secret"
              type="password"
              className="input font-mono"
              value={hmacSecret}
              onChange={(e) => setHmacSecret(e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="hmacAlgo">Algorithm</label>
            <select
              id="hmacAlgo"
              className="input"
              value={hmacAlgo}
              onChange={(e) => setHmacAlgo(e.target.value as Algo)}
            >
              {ALGOS.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>
        </div>
        <button type="submit" className="btn-secondary" disabled={hmac.pending}>
          {hmac.pending ? "Computing…" : "Compute HMAC"}
        </button>
      </form>
      <ErrorBanner message={hmac.error} />
      {hmac.data && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">HMAC digest</h3>
          <CodeBlock value={hmac.data.digest} />
        </section>
      )}
    </div>
  );
}
