import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { CidrResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function Cidr() {
  const [cidr, setCidr] = useState("10.0.0.0/24");
  const { data, error, pending, run } = useApi((body: object) =>
    postJson<CidrResponse>("/api/calc/cidr", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ cidr });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="CIDR Calculator" description="Subnet, range, and host count from a CIDR block." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="cidr">CIDR</label>
          <input
            id="cidr"
            className="input font-mono"
            placeholder="10.0.0.0/24 or 2001:db8::/64"
            value={cidr}
            onChange={(e) => setCidr(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Calculating…" : "Calculate"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && data.error && (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {data.error}
        </div>
      )}
      {data && !data.error && (
        <section className="card text-sm">
          <dl className="grid grid-cols-[140px_1fr] gap-y-2">
            <dt className="text-slate-500">IP version</dt><dd>{data.version}</dd>
            <dt className="text-slate-500">Prefix length</dt><dd>/{data.prefix}</dd>
            <dt className="text-slate-500">Network</dt><dd className="font-mono">{data.network}</dd>
            <dt className="text-slate-500">Netmask</dt><dd className="font-mono">{data.netmask}</dd>
            {data.broadcast && (
              <>
                <dt className="text-slate-500">Broadcast</dt>
                <dd className="font-mono">{data.broadcast}</dd>
              </>
            )}
            {data.first_host && (
              <>
                <dt className="text-slate-500">First host</dt>
                <dd className="font-mono">{data.first_host}</dd>
              </>
            )}
            {data.last_host && (
              <>
                <dt className="text-slate-500">Last host</dt>
                <dd className="font-mono">{data.last_host}</dd>
              </>
            )}
            <dt className="text-slate-500"># hosts</dt>
            <dd className="font-mono">{data.num_hosts.toLocaleString()}</dd>
          </dl>
        </section>
      )}
    </div>
  );
}
