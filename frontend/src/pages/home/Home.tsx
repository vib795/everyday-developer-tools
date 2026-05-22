import { Link } from "react-router-dom";

import { TOOL_GROUPS } from "../../tools";

export function Home() {
  return (
    <div>
      <section className="mb-10 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Developer Tools</h1>
        <p className="mt-3 text-base text-slate-600 dark:text-slate-300">
          A small suite of practical tools for everyday development. Pick one below to get started.
        </p>
      </section>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {TOOL_GROUPS.map((group) => (
          <section key={group.label} className="card">
            <h2 className="text-base font-semibold text-slate-900 dark:text-slate-100">{group.label}</h2>
            <ul className="mt-3 space-y-2">
              {group.items.map((item) => (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className="group flex flex-col rounded p-2 hover:bg-slate-50 dark:hover:bg-slate-800"
                  >
                    <span className="text-sm font-medium text-slate-800 dark:text-slate-100 group-hover:text-brand">
                      {item.label}
                    </span>
                    {item.description && (
                      <span className="text-xs text-slate-500 dark:text-slate-400">{item.description}</span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
