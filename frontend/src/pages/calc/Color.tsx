import { FormEvent, useState } from "react";

import { postJson } from "../../api/client";
import { ColorConvertResponse, ContrastResponse } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { PageHeader } from "../../components/PageHeader";
import { useApi } from "../../hooks/useApi";

export function Color() {
  const [color, setColor] = useState("#6225e6");
  const [fg, setFg] = useState("#000000");
  const [bg, setBg] = useState("#ffffff");

  const conv = useApi((body: object) =>
    postJson<ColorConvertResponse>("/api/calc/color", body),
  );
  const contrast = useApi((body: object) =>
    postJson<ContrastResponse>("/api/calc/contrast", body),
  );

  function onConvert(e: FormEvent) {
    e.preventDefault();
    conv.run({ color });
  }
  function onContrast(e: FormEvent) {
    e.preventDefault();
    contrast.run({ foreground: fg, background: bg });
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Color" description="Convert color formats and check WCAG contrast." />

      <form onSubmit={onConvert} className="card space-y-4">
        <h2 className="text-base font-semibold text-slate-700">Convert</h2>
        <div className="flex items-end gap-3">
          <div className="flex-1">
            <label className="label" htmlFor="color">Color (hex / rgb / hsl)</label>
            <input
              id="color"
              className="input font-mono"
              value={color}
              onChange={(e) => setColor(e.target.value)}
            />
          </div>
          <div
            aria-hidden
            className="h-10 w-16 rounded border border-slate-200"
            style={{ background: color }}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={conv.pending}>
          {conv.pending ? "Converting…" : "Convert"}
        </button>
      </form>
      <ErrorBanner message={conv.error} />
      {conv.data && conv.data.error && (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {conv.data.error}
        </div>
      )}
      {conv.data && !conv.data.error && (
        <section className="card text-sm">
          <dl className="grid grid-cols-[80px_1fr] gap-y-2">
            <dt className="text-slate-500">HEX</dt><dd className="font-mono">{conv.data.hex}</dd>
            <dt className="text-slate-500">RGB</dt><dd className="font-mono">{conv.data.rgb}</dd>
            <dt className="text-slate-500">HSL</dt><dd className="font-mono">{conv.data.hsl}</dd>
            <dt className="text-slate-500">OKLCH</dt><dd className="font-mono">{conv.data.oklch}</dd>
          </dl>
        </section>
      )}

      <form onSubmit={onContrast} className="card space-y-4">
        <h2 className="text-base font-semibold text-slate-700">Contrast (WCAG)</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="fg">Foreground</label>
            <div className="flex items-center gap-2">
              <input
                id="fg"
                className="input font-mono flex-1"
                value={fg}
                onChange={(e) => setFg(e.target.value)}
              />
              <div aria-hidden className="h-9 w-9 rounded border border-slate-200" style={{ background: fg }} />
            </div>
          </div>
          <div>
            <label className="label" htmlFor="bg">Background</label>
            <div className="flex items-center gap-2">
              <input
                id="bg"
                className="input font-mono flex-1"
                value={bg}
                onChange={(e) => setBg(e.target.value)}
              />
              <div aria-hidden className="h-9 w-9 rounded border border-slate-200" style={{ background: bg }} />
            </div>
          </div>
        </div>
        <div className="rounded border border-slate-200 px-4 py-3" style={{ color: fg, background: bg }}>
          The quick brown fox jumps over the lazy dog.
        </div>
        <button type="submit" className="btn-secondary" disabled={contrast.pending}>
          {contrast.pending ? "Computing…" : "Check contrast"}
        </button>
      </form>
      <ErrorBanner message={contrast.error} />
      {contrast.data && contrast.data.error && (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {contrast.data.error}
        </div>
      )}
      {contrast.data && !contrast.data.error && (
        <section className="card text-sm">
          <p className="mb-3">
            Ratio: <span className="font-mono text-base">{contrast.data.ratio}:1</span>
          </p>
          <table className="w-full">
            <thead className="text-left text-slate-500">
              <tr>
                <th className="py-1 font-medium">Level</th>
                <th className="py-1 font-medium">Normal text</th>
                <th className="py-1 font-medium">Large text</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-slate-200">
                <td className="py-1">AA (4.5 / 3.0)</td>
                <td className={contrast.data.aa_normal ? "text-emerald-700" : "text-rose-700"}>
                  {contrast.data.aa_normal ? "pass" : "fail"}
                </td>
                <td className={contrast.data.aa_large ? "text-emerald-700" : "text-rose-700"}>
                  {contrast.data.aa_large ? "pass" : "fail"}
                </td>
              </tr>
              <tr className="border-t border-slate-200">
                <td className="py-1">AAA (7.0 / 4.5)</td>
                <td className={contrast.data.aaa_normal ? "text-emerald-700" : "text-rose-700"}>
                  {contrast.data.aaa_normal ? "pass" : "fail"}
                </td>
                <td className={contrast.data.aaa_large ? "text-emerald-700" : "text-rose-700"}>
                  {contrast.data.aaa_large ? "pass" : "fail"}
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
