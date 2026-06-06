import { CopyButton } from "./CopyButton";

interface Props {
  value: string;
  language?: string;
  showLineNumbers?: boolean;
  copyable?: boolean;
}

export function CodeBlock({ value, showLineNumbers = false, copyable = true }: Props) {
  const lines = value.split("\n");
  return (
    <div className="relative">
      {copyable && (
        <div className="absolute right-2 top-2 z-10">
          <CopyButton value={value} />
        </div>
      )}
      <pre className="code overflow-x-auto">
        {showLineNumbers ? (
          <div className="flex">
            <div
              aria-hidden
              className="select-none border-r border-slate-200 pr-3 text-right text-slate-400 dark:border-slate-800 dark:text-slate-500"
            >
              {lines.map((_, i) => (
                <div key={i}>{i + 1}</div>
              ))}
            </div>
            <div className="pl-3">
              {lines.map((line, i) => (
                <div key={i}>{line || " "}</div>
              ))}
            </div>
          </div>
        ) : (
          <code>{value}</code>
        )}
      </pre>
    </div>
  );
}
