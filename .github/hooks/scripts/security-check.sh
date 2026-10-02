#!/usr/bin/env bash
# .github/hooks/scripts/security-check.sh
#
# PreToolUse hook: runs security and quality checks before git commit/push.
# Blocks the operation and reports issues if checks fail.
#
# Triggered by: run_in_terminal (git commit/push), mcp_gitkraken_git_add_or_commit, mcp_gitkraken_git_push
# Exit 0  → allow
# Exit 2  → block (hard error shown to agent)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"

# ── Parse stdin ──────────────────────────────────────────────────────────────
INPUT="$(cat)"
TOOL_NAME=""
IS_COMMIT_OR_PUSH=false

if command -v jq &>/dev/null; then
  TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null || true)"
  ACTION="$(echo "$INPUT"    | jq -r '.tool_input.action  // ""' 2>/dev/null || true)"
  CMD="$(echo "$INPUT"       | jq -r '.tool_input.command // ""' 2>/dev/null || true)"
else
  # Fallback: grep-based extraction
  TOOL_NAME="$(echo "$INPUT" | grep -o '"tool_name"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"//' | tr -d '"' || true)"
  ACTION="$(echo "$INPUT"    | grep -o '"action"[[:space:]]*:[[:space:]]*"[^"]*"'    | sed 's/.*: *"//' | tr -d '"' || true)"
  CMD="$(echo "$INPUT"       | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"'   | sed 's/.*: *"//' | tr -d '"' || true)"
fi

# Determine if this is a commit or push operation
case "$TOOL_NAME" in
  mcp_gitkraken_git_push)
    IS_COMMIT_OR_PUSH=true
    OP="push"
    ;;
  mcp_gitkraken_git_add_or_commit)
    if [[ "$ACTION" == "commit" ]]; then
      IS_COMMIT_OR_PUSH=true
      OP="commit"
    fi
    ;;
  run_in_terminal)
    if echo "$CMD" | grep -qE 'git (commit|push)'; then
      IS_COMMIT_OR_PUSH=true
      OP="$(echo "$CMD" | grep -oE 'git (commit|push)' | awk '{print $2}' | head -1)"
    fi
    ;;
esac

# Not a commit/push — allow immediately
if [[ "$IS_COMMIT_OR_PUSH" != "true" ]]; then
  exit 0
fi

# ── Run checks ───────────────────────────────────────────────────────────────
ERRORS=()
WARNINGS=()

echo "🔍 Running pre-${OP} security checks..." >&2

cd "$REPO_ROOT"

# 1. Python linting (ruff)
if [[ -d "backend" ]]; then
  echo "  [1/4] ruff check (Python linting)..." >&2
  if command -v uv &>/dev/null; then
    if ! uv run --project backend ruff check backend/app/ --quiet 2>&1; then
      RUFF_OUT="$(uv run --project backend ruff check backend/app/ 2>&1 || true)"
      ERRORS+=("ruff: Python linting errors found\n${RUFF_OUT}")
    fi
  elif command -v ruff &>/dev/null; then
    if ! ruff check backend/app/ --quiet 2>&1; then
      RUFF_OUT="$(ruff check backend/app/ 2>&1 || true)"
      ERRORS+=("ruff: Python linting errors found\n${RUFF_OUT}")
    fi
  else
    WARNINGS+=("ruff not found — skipping Python linting")
  fi
fi

# 2. Python security scan (bandit)
if [[ -d "backend" ]]; then
  echo "  [2/4] bandit (Python security scan)..." >&2
  if command -v bandit &>/dev/null; then
    BANDIT_OUT="$(bandit -r backend/app -ll -q 2>&1 || true)"
    if echo "$BANDIT_OUT" | grep -qE 'Issue \['; then
      ERRORS+=("bandit: Security issues found\n${BANDIT_OUT}")
    fi
  elif command -v uv &>/dev/null && uv run --project backend python -c "import bandit" 2>/dev/null; then
    BANDIT_OUT="$(uv run --project backend bandit -r backend/app -ll -q 2>&1 || true)"
    if echo "$BANDIT_OUT" | grep -qE 'Issue \['; then
      ERRORS+=("bandit: Security issues found\n${BANDIT_OUT}")
    fi
  else
    WARNINGS+=("bandit not found — skipping Python security scan (install with: uv add --dev bandit)")
  fi
fi

# 3. Hardcoded secret detection (git grep on staged/tracked changes)
echo "  [3/4] Secret detection (staged changes)..." >&2
SECRET_PATTERNS=(
  'password\s*=\s*["\x27][^"\x27]{4,}'
  'secret\s*=\s*["\x27][^"\x27]{4,}'
  'api_key\s*=\s*["\x27][^"\x27]{4,}'
  'token\s*=\s*["\x27][^"\x27]{4,}'
  'private_key\s*=\s*["\x27][^"\x27]{4,}'
  'BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY'
  'AKIA[0-9A-Z]{16}'
)

SECRET_HITS=""
if git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  for pattern in "${SECRET_PATTERNS[@]}"; do
    HITS="$(git diff --staged -U0 2>/dev/null | grep '^\+' | grep -iE "$pattern" || true)"
    if [[ -n "$HITS" ]]; then
      SECRET_HITS+="$HITS\n"
    fi
  done
fi

if [[ -n "$SECRET_HITS" ]]; then
  ERRORS+=("secrets: Possible hardcoded credentials in staged changes\n${SECRET_HITS}")
fi

# 4. Frontend TypeScript check (npm run lint)
if [[ -d "frontend" ]]; then
  echo "  [4/4] TypeScript check (npm run lint)..." >&2
  if command -v npm &>/dev/null && [[ -f "frontend/package.json" ]]; then
    TS_OUT="$(cd frontend && npm run lint --silent 2>&1 || true)"
    if echo "$TS_OUT" | grep -qE 'error TS|error:'; then
      ERRORS+=("tsc: TypeScript errors found\n${TS_OUT}")
    fi
  else
    WARNINGS+=("npm not found — skipping TypeScript check")
  fi
fi

# ── Report ───────────────────────────────────────────────────────────────────
if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo "" >&2
  echo "⚠️  Warnings (non-blocking):" >&2
  for w in "${WARNINGS[@]}"; do
    echo "   • $w" >&2
  done
fi

if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo "" >&2
  echo "❌ Pre-${OP} checks FAILED — operation blocked:" >&2
  for err in "${ERRORS[@]}"; do
    echo "" >&2
    printf "   %b\n" "$err" >&2
  done
  echo "" >&2
  echo "Fix the issues above before committing/pushing." >&2

  printf '%s' "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Pre-${OP} security checks failed. Fix issues reported in the terminal before proceeding.\"}}"
  exit 2
fi

echo "" >&2
echo "✅ All pre-${OP} checks passed." >&2
exit 0
