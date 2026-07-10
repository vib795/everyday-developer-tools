import { useEffect, useState } from "react";

import { postJson } from "../../api/client";
import { MarkdownPreviewResponse } from "../../api/types";
import { PageHeader } from "../../components/PageHeader";

const SAMPLE = `# Hello

A live **Markdown** preview.

- one
- two

\`\`\`js
console.log("hi");
\`\`\`
`;

export function MarkdownPreview() {
  const [text, setText] = useState(SAMPLE);
  const [html, setHtml] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const t = setTimeout(async () => {
      try {
        const resp = await postJson<MarkdownPreviewResponse>("/api/calc/markdown", { text });
        if (!cancelled) {
          setHtml(resp.html);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "preview failed");
      }
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [text]);

  return (
    <div className="space-y-6">
      <PageHeader title="Markdown Preview" description="Live side-by-side preview of Markdown." />
      <div className="grid gap-4 lg:grid-cols-2">
        <textarea
          className="input font-mono min-h-[400px]"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <div className="card prose prose-sm dark:prose-invert max-w-none overflow-auto">
          {error && (
            <div role="alert" className="rounded-md border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 px-4 py-3 text-sm text-rose-900 dark:text-rose-200">
              {error}
            </div>
          )}
          <div dangerouslySetInnerHTML={{ __html: html }} />
        </div>
      </div>
    </div>
  );
}
