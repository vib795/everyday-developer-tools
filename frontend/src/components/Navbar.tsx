import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useLocation } from "react-router";
import clsx from "clsx";

import { TOOL_GROUPS, ToolLink } from "../tools";
import { ThemeToggle } from "./ThemeToggle";

interface DropdownProps {
  label: string;
  items: ToolLink[];
}

function Dropdown({ label, items }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const location = useLocation();

  useEffect(() => setOpen(false), [location.pathname]);
  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="rounded px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
        aria-expanded={open}
      >
        {label}
        <span aria-hidden className="ml-1 text-slate-400 dark:text-slate-500">
          ▾
        </span>
      </button>
      {open && (
        <div
          role="menu"
          className="absolute left-0 z-20 mt-1 w-64 rounded-md border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-800 dark:bg-slate-900"
        >
          {items.map((it) => (
            <Link
              key={it.path}
              to={it.path}
              role="menuitem"
              className="block px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              {it.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function Navbar() {
  const [mobile, setMobile] = useState(false);

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2">
        <Link to="/" className="flex items-center gap-2">
          <span className="rounded bg-brand px-2 py-1 text-sm font-semibold text-white">DT</span>
          <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
            Developer Tools
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              clsx(
                "rounded px-3 py-2 text-sm font-medium",
                isActive
                  ? "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100"
                  : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800",
              )
            }
          >
            Home
          </NavLink>
          {TOOL_GROUPS.map((g) =>
            g.items.length > 1 ? (
              <Dropdown key={g.label} label={g.label} items={g.items} />
            ) : (
              <NavLink
                key={g.label}
                to={g.items[0].path}
                className={({ isActive }) =>
                  clsx(
                    "rounded px-3 py-2 text-sm font-medium",
                    isActive
                      ? "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100"
                      : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800",
                  )
                }
              >
                {g.items[0].label}
              </NavLink>
            ),
          )}
        </nav>

        <div className="flex items-center gap-1">
          <ThemeToggle />
          <button
            type="button"
            className="md:hidden btn-ghost"
            onClick={() => setMobile((v) => !v)}
            aria-expanded={mobile}
            aria-label="Toggle menu"
          >
            ☰
          </button>
        </div>
      </div>

      {mobile && (
        <div className="border-t border-slate-200 bg-white md:hidden dark:border-slate-800 dark:bg-slate-900">
          <nav className="space-y-3 px-4 py-3">
            <Link to="/" onClick={() => setMobile(false)} className="block text-sm font-medium">
              Home
            </Link>
            {TOOL_GROUPS.map((g) => (
              <div key={g.label}>
                <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
                  {g.label}
                </p>
                <ul className="mt-1 space-y-1">
                  {g.items.map((it) => (
                    <li key={it.path}>
                      <Link
                        to={it.path}
                        onClick={() => setMobile(false)}
                        className="block rounded px-2 py-1 text-sm text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800"
                      >
                        {it.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
