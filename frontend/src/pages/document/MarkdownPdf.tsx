import { FormEvent, useState } from "react";

import { ApiError, downloadBlob, postForBlob, postMultipart } from "../../api/client";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";

type Mode = "md_to_pdf" | "pdf_to_md";

export function MarkdownPdf() {
  const [mode, setMode] = useState<Mode>("md_to_pdf");
  const [markdown, setMarkdown] = useState("# Hello\n\n- one\n- two\n");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [extracted, setExtracted] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setExtracted(null);
    setPending(true);
    try {
      if (mode === "md_to_pdf") {
        const { blob, filename } = await postForBlob("/api/document/md-to-pdf", {
          markdown_text: markdown,
        });
        downloadBlob(blob, filename);
      } else {
        if (!pdfFile) {
          setError("Choose a PDF file first.");
          return;
        }
        const fd = new FormData();
        fd.append("pdf_file", pdfFile);
        const result = await postMultipart<{ text: string }>("/api/document/pdf-to-md", fd);
        setExtracted(result.text);
      }
    } catch (err) {
      setError(err instanceof ApiError || err instanceof Error ? err.message : "Conversion failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Markdown ⇄ PDF"
        description="Convert Markdown to a downloadable PDF, or extract text from a PDF."
      />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="m"
              checked={mode === "md_to_pdf"}
              onChange={() => setMode("md_to_pdf")}
            />
            Markdown → PDF
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="m"
              checked={mode === "pdf_to_md"}
              onChange={() => setMode("pdf_to_md")}
            />
            PDF → text
          </label>
        </div>
        {mode === "md_to_pdf" ? (
          <div>
            <label className="label" htmlFor="md">
              Markdown
            </label>
            <textarea
              id="md"
              rows={14}
              className="input font-mono"
              value={markdown}
              onChange={(e) => setMarkdown(e.target.value)}
            />
          </div>
        ) : (
          <div>
            <label className="label" htmlFor="pdf">
              PDF file
            </label>
            <input
              id="pdf"
              type="file"
              accept="application/pdf"
              className="block w-full text-sm"
              onChange={(e) => setPdfFile(e.target.files?.[0] ?? null)}
            />
          </div>
        )}
        <button type="submit" disabled={pending} className="btn-primary">
          {pending ? "Converting…" : mode === "md_to_pdf" ? "Download PDF" : "Extract text"}
        </button>
      </form>

      <ErrorBanner message={error} />

      {extracted !== null && (
        <section className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Extracted text</h3>
          <pre className="code whitespace-pre-wrap">{extracted}</pre>
        </section>
      )}
    </div>
  );
}
