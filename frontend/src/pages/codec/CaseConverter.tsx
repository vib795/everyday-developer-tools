import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { CaseConvertResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

const STYLES = [
  { value: "camel", label: "camelCase" },
  { value: "pascal", label: "PascalCase" },
  { value: "snake", label: "snake_case" },
  { value: "kebab", label: "kebab-case" },
  { value: "constant", label: "CONSTANT_CASE" },
  { value: "title", label: "Title Case" },
  { value: "sentence", label: "Sentence case" },
  { value: "lower", label: "lower case" },
  { value: "upper", label: "UPPER CASE" },
  { value: "dot", label: "dot.case" },
  { value: "path", label: "path/case" },
] as const;

type Style = (typeof STYLES)[number]["value"];

export function CaseConverter() {
  const [text, setText] = useState("");
  const [style, setStyle] = useState<Style>("camel");

  const { data, error, pending, run } = useApi((body: object) =>
    postJson<CaseConvertResponse>("/api/codec/case", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text, style });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Case Converter" description="Convert between camelCase, snake_case, kebab-case, and friends." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="text">Input</label>
          <textarea
            id="text"
            rows={3}
            className="input font-mono"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <div>
          <label className="label" htmlFor="style">Target style</label>
          <select
            id="style"
            className="input"
            value={style}
            onChange={(e) => setStyle(e.target.value as Style)}
          >
            {STYLES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Converting…" : "Convert"}
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
