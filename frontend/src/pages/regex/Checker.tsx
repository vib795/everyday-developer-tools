import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { RegexCheckResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function RegexChecker() {
  const [regex, setRegex] = useState("");
  const [str, setStr] = useState("");
  const { data, error, pending, run } = useApi((body: { regex: string; string: string }) =>
    postJson<RegexCheckResponse>("/api/regex/check", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ regex, string: str });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Regex Checker"
        description="Test whether a regex matches a string. Limited to 1s of execution to avoid ReDoS."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="regex">
            Regex
          </label>
          <input
            id="regex"
            className="input font-mono"
            value={regex}
            onChange={(e) => setRegex(e.target.value)}
          />
        </div>
        <div>
          <label className="label" htmlFor="str">
            Test string
          </label>
          <input
            id="str"
            className="input font-mono"
            value={str}
            onChange={(e) => setStr(e.target.value)}
          />
        </div>
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Checking…" : "Check"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card">
          <p
            className={
              data.match === true
                ? "rounded bg-emerald-50 px-3 py-2 text-sm text-emerald-900"
                : data.match === false
                  ? "rounded bg-amber-50 px-3 py-2 text-sm text-amber-900"
                  : "rounded bg-rose-50 px-3 py-2 text-sm text-rose-900"
            }
          >
            {data.message}
          </p>
        </section>
      )}
    </div>
  );
}
