import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { CounterResponse } from "../../api/types";
import { CodeBlock } from "../../components/CodeBlock";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Filter = "Character" | "Word" | "Line" | "Custom Delimiter";

export function Counter() {
  const [text_input, setText] = useState("");
  const [filter, setFilter] = useState<Filter>("Character");
  const [delimiter, setDelimiter] = useState("");

  const { data, error, pending, run } = useApi(
    (body: { text_input: string; filter_option: Filter; custom_delimiter: string }) =>
      postJson<CounterResponse>("/api/string/count", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text_input, filter_option: filter, custom_delimiter: delimiter });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Character / Word Counter" />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="text_input">
            Text
          </label>
          <textarea
            id="text_input"
            rows={6}
            className="input"
            value={text_input}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="label" htmlFor="filter">
              Count by
            </label>
            <select
              id="filter"
              className="input"
              value={filter}
              onChange={(e) => setFilter(e.target.value as Filter)}
            >
              <option>Character</option>
              <option>Word</option>
              <option>Line</option>
              <option>Custom Delimiter</option>
            </select>
          </div>
          {filter === "Custom Delimiter" && (
            <div>
              <label className="label" htmlFor="delim">
                Delimiter
              </label>
              <input
                id="delim"
                className="input font-mono"
                value={delimiter}
                onChange={(e) => setDelimiter(e.target.value)}
              />
            </div>
          )}
          <button type="submit" disabled={pending} className="btn-primary">
            {pending ? "Counting…" : "Count"}
          </button>
        </div>
      </form>

      <ErrorBanner message={error} />

      {data && (
        <section className="card space-y-3">
          <p className="text-lg font-semibold">{data.count.toLocaleString()}</p>
          <CodeBlock value={data.output} />
        </section>
      )}
    </div>
  );
}
