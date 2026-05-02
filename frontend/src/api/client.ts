export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

function readableDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        if (d && typeof d === "object" && "msg" in d) return String((d as { msg: unknown }).msg);
        return JSON.stringify(d);
      })
      .join("; ");
  }
  if (detail && typeof detail === "object") return JSON.stringify(detail);
  return "Request failed";
}

async function handle(res: Response): Promise<Response> {
  if (res.ok) return res;
  let detail: unknown = res.statusText;
  try {
    const body = await res.clone().json();
    detail = body?.detail ?? body;
  } catch {
    /* ignore */
  }
  throw new ApiError(res.status, readableDetail(detail), detail);
}

export async function postJson<TResp>(path: string, body: unknown): Promise<TResp> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  await handle(res);
  return (await res.json()) as TResp;
}

export async function getJson<TResp>(path: string): Promise<TResp> {
  const res = await fetch(path);
  await handle(res);
  return (await res.json()) as TResp;
}

export async function postForBlob(
  path: string,
  body: unknown,
): Promise<{ blob: Blob; filename: string }> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  await handle(res);
  const cd = res.headers.get("content-disposition") ?? "";
  const match = /filename="?([^"]+)"?/.exec(cd);
  return { blob: await res.blob(), filename: match?.[1] ?? "download" };
}

export async function postMultipart<TResp>(path: string, formData: FormData): Promise<TResp> {
  const res = await fetch(path, { method: "POST", body: formData });
  await handle(res);
  return (await res.json()) as TResp;
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
