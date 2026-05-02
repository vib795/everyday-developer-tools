interface Props {
  message?: string | null;
}

export function ErrorBanner({ message }: Props) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900"
    >
      {message}
    </div>
  );
}
