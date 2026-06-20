# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes in this repo (FastAPI backend in `backend/app/`, Vite + React/TS SPA in `frontend/src/`, K8s manifests in `k8s/`).

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State the placement decision out loud. "Adding this as a new endpoint on `routers/json_tools.py`, a schema in `schemas/json_tools.py`, and a pure function in `services/`." If you're not sure where it goes, ask.
- If multiple interpretations exist, present them. A new "convert" tool could be another endpoint on `routers/convert.py` or a new module under `routers/codec.py` — don't pick silently.
- If a simpler approach exists, say so. A pure function in `services/` reused by an existing route often beats a new endpoint. A tailwind class often beats a new component.
- If something is unclear, stop. Common ambiguities here: which deploy topology (combined `Dockerfile`, split `Dockerfile.dev`, or split K8s), whether the SPA needs a route entry in `frontend/src/tools.ts`, whether a change should also touch the slowapi rate-limit settings in `backend/app/config.py`.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked. If the task is one tool, don't also tweak adjacent routers or pages "while I'm here."
- No abstractions for single-use code. A service function called by one router is a function, not a class hierarchy.
- No "flexibility" or "configurability" that wasn't requested. Don't add new fields to `Settings` in `backend/app/config.py` for hypothetical env vars; don't add new ConfigMap keys in `k8s/10-configmap.yaml` that nothing reads.
- No error handling for impossible scenarios. Pydantic schemas in `schemas/` already validate router inputs — don't re-validate the same shapes inside `services/`.
- If a route handler grows past ~30 lines, the work probably belongs in `services/` and the handler should call it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent routers, schemas, services, components, or formatting.
- Don't refactor patterns that aren't broken. The repo's convention is one module per tool group across `routers/`, `schemas/`, and `services/`, mirrored by `frontend/src/pages/<area>/`. Match it.
- Match existing style. Run `uv run ruff format .` from `backend/` for Python; mirror the style of neighboring `.tsx` files for TypeScript.
- If you notice unrelated dead code (a stray export in `services/`, a stale entry in `frontend/src/tools.ts`), mention it — don't delete it.

When your changes create orphans:
- Remove imports and helpers your edits left unused.
- Don't remove pre-existing dead code unless asked.

Don't auto-bump dependencies in `backend/pyproject.toml` or `frontend/package.json` beyond what the task requires. (The frontend peer-dep tree is currently clean — `vite@8` and `@vitejs/plugin-react@6` are compatible, so `npm ci` / `npm install` resolve without `--legacy-peer-deps`. Treat dep bumps as their own task.)

The test: every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → write a `pytest` case in `backend/tests/test_<area>_router.py` for the invalid input, then make it pass.
- "Fix the bug" → reproduce it first in `tests/test_<area>_router.py` (or `tests/test_services.py` for pure logic), then fix.
- "Refactor X" → `cd backend && uv run pytest` passes before and after.
- Frontend changes have no automated test layer yet. Verify by running `npm run dev` (proxies `/api` → `:8000`), clicking through the affected page, and confirming `npm run lint` (which is `tsc --noEmit`) is clean.
- K8s changes → `kubectl apply -f k8s/`, then `kubectl rollout status deploy/<name> -n devtools` and `kubectl get pods -n devtools` show Ready.

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
