import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { QrCodeResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

type Ec = "L" | "M" | "Q" | "H";

export function QrCode() {
  const [text, setText] = useState("https://example.com");
  const [errorCorrection, setEc] = useState<Ec>("M");
  const [boxSize, setBoxSize] = useState(8);

  const { data, error, pending, run } = useApi((body: object) =>
    postJson<QrCodeResponse>("/api/misc/qr", body),
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run({ text, error_correction: errorCorrection, box_size: boxSize, border: 4 });
  }

  function downloadSvg() {
    if (!data?.svg) return;
    const blob = new Blob([data.svg], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "qr-code.svg";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-6">
      <PageHeader title="QR Code Generator" description="Encode text or a URL into a QR code (SVG)." />
      <form onSubmit={onSubmit} className="card space-y-4">
        <div>
          <label className="label" htmlFor="text">Text or URL</label>
          <textarea
            id="text"
            rows={3}
            className="input font-mono"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="ec">Error correction</label>
            <select
              id="ec"
              className="input"
              value={errorCorrection}
              onChange={(e) => setEc(e.target.value as Ec)}
            >
              <option value="L">L — ~7%</option>
              <option value="M">M — ~15%</option>
              <option value="Q">Q — ~25%</option>
              <option value="H">H — ~30%</option>
            </select>
          </div>
          <div>
            <label className="label" htmlFor="box">Box size (px)</label>
            <input
              id="box"
              type="number"
              min={1}
              max={40}
              className="input"
              value={boxSize}
              onChange={(e) => setBoxSize(parseInt(e.target.value || "8", 10))}
            />
          </div>
        </div>
        <button type="submit" className="btn-primary" disabled={pending}>
          {pending ? "Generating…" : "Generate"}
        </button>
      </form>
      <ErrorBanner message={error} />
      {data && data.error && (
        <div role="alert" className="rounded-md border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 px-4 py-3 text-sm text-rose-900 dark:text-rose-200">
          {data.error}
        </div>
      )}
      {data && data.svg && (
        <section className="card flex flex-col items-center gap-4">
          <div className="bg-white dark:bg-slate-900 p-4" dangerouslySetInnerHTML={{ __html: data.svg }} />
          <button type="button" onClick={downloadSvg} className="btn-secondary">
            Download SVG
          </button>
        </section>
      )}
    </div>
  );
}
