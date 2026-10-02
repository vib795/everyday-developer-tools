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
# True when the pending commit will stage content beyond the current index
# (`git commit -a`), which the index-only secret scan would otherwise miss.
COMMIT_ALL=false

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
      # This tool does not expose whether it stages everything, so assume the
      # wider scope rather than scanning less than what gets committed.
      COMMIT_ALL=true
    fi
    ;;
  run_in_terminal)
    # Walk the command token by token rather than matching "git (commit|push)".
    # Git accepts global options before the subcommand, so `git -C . commit`,
    # `git -c user.name=x push` and `git --git-dir=.git commit` all failed the
    # old regex and silently skipped every check below.
    _TOKENS=()
    if [[ -n "${CMD:-}" ]]; then
      read -ra _TOKENS <<< "$CMD" || true
    fi
    _i=0
    while [[ $_i -lt ${#_TOKENS[@]} ]]; do
      case "${_TOKENS[$_i]}" in
        git|*/git)
          _j=$(( _i + 1 ))
          while [[ $_j -lt ${#_TOKENS[@]} ]]; do
            case "${_TOKENS[$_j]}" in
              # Global options that consume the next token as their value.
              -C|-c|--git-dir|--work-tree|--namespace|--exec-path|--super-prefix)
                _j=$(( _j + 2 )) ;;
              # Any other option belongs to git itself; step over it.
              -*)
                _j=$(( _j + 1 )) ;;
              commit)
                IS_COMMIT_OR_PUSH=true
                OP="commit"
                # -a/--all (and bundles like -am) stage content the index does
                # not hold yet. Order matters: --all/--include first, then a
                # catch-all for every other long option so that --amend is not
                # mistaken for -a, then short bundles containing an "a".
                for _f in "${_TOKENS[@]:$_j}"; do
                  case "$_f" in
                    --all|--include) COMMIT_ALL=true ;;
                    --*)             : ;;
                    -*a*)            COMMIT_ALL=true ;;
                  esac
                done
                break ;;
              push)
                IS_COMMIT_OR_PUSH=true
                OP="push"
                break ;;
              *)
                break ;;
            esac
          done
          ;;
      esac
      if [[ "$IS_COMMIT_OR_PUSH" == "true" ]]; then
        break
      fi
      _i=$(( _i + 1 ))
    done
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
  # Trust bandit's exit status, not its prose. The text formatter prints
  # "Issue: [" with a colon, so the old 'Issue \[' match never fired and every
  # finding was reported as a clean scan. bandit exits 1 when it reports
  # findings and 2 on a usage error; both deserve a block.
  if command -v bandit &>/dev/null; then
    BANDIT_RC=0
    BANDIT_OUT="$(bandit -r backend/app -ll -q 2>&1)" || BANDIT_RC=$?
    if [[ $BANDIT_RC -ne 0 ]]; then
      ERRORS+=("bandit: Security issues found (exit ${BANDIT_RC})\n${BANDIT_OUT}")
    fi
  elif command -v uv &>/dev/null && uv run --project backend python -c "import bandit" 2>/dev/null; then
    BANDIT_RC=0
    BANDIT_OUT="$(uv run --project backend bandit -r backend/app -ll -q 2>&1)" || BANDIT_RC=$?
    if [[ $BANDIT_RC -ne 0 ]]; then
      ERRORS+=("bandit: Security issues found (exit ${BANDIT_RC})\n${BANDIT_OUT}")
    fi
  else
    WARNINGS+=("bandit not found — skipping Python security scan (install with: uv add --dev bandit)")
  fi
fi

# 3. Hardcoded secret detection (git grep on staged/tracked changes)
echo "  [3/4] Secret detection (staged changes)..." >&2
# Portable ERE only. These previously used \s and \x27, which are PCRE/GNU
# extensions: BSD grep (the default on macOS) does not understand either, so
# the five quoted-value patterns matched nothing at all there.
SECRET_PATTERNS=(
  "password[[:space:]]*=[[:space:]]*[\"'][^\"']{4,}"
  "secret[[:space:]]*=[[:space:]]*[\"'][^\"']{4,}"
  "api_key[[:space:]]*=[[:space:]]*[\"'][^\"']{4,}"
  "token[[:space:]]*=[[:space:]]*[\"'][^\"']{4,}"
  "private_key[[:space:]]*=[[:space:]]*[\"'][^\"']{4,}"
  'BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY'
  'AKIA[0-9A-Z]{16}'
)

SECRET_HITS=""
SCOPE_LABEL="staged changes"
if git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  # Scan what the commit will actually contain. `git commit -a` stages tracked
  # modifications *after* this hook runs, so the index alone understates it.
  if [[ "$COMMIT_ALL" == "true" ]]; then
    DIFF_SCOPE="HEAD"
    SCOPE_LABEL="staged changes plus tracked working-tree edits (git commit -a)"
  else
    DIFF_SCOPE="--staged"
  fi

  # Report file names and match counts only. The matching line *is* the
  # credential, and this hook's stderr is fed back to the agent, so printing
  # it would disclose the very value the check exists to catch.
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    for pattern in "${SECRET_PATTERNS[@]}"; do
      COUNT="$(git diff "$DIFF_SCOPE" -U0 -- "$file" 2>/dev/null \
                 | grep '^+' | grep -v '^+++' | grep -icE "$pattern" || true)"
      if [[ "${COUNT:-0}" -gt 0 ]]; then
        SECRET_HITS+="   ${file}: ${COUNT} added line(s) match /${pattern}/\n"
      fi
    done
  done < <(git diff "$DIFF_SCOPE" --name-only 2>/dev/null || true)
fi

if [[ -n "$SECRET_HITS" ]]; then
  ERRORS+=("secrets: Possible hardcoded credentials in ${SCOPE_LABEL} — values redacted, inspect the files yourself\n${SECRET_HITS}")
fi

# 4. Frontend TypeScript check (npm run lint)
if [[ -d "frontend" ]]; then
  echo "  [4/4] TypeScript check (npm run lint)..." >&2
  if command -v npm &>/dev/null && [[ -f "frontend/package.json" ]]; then
    # Use the exit status. `|| true` discarded it, and the grep for
    # "error TS"/"error:" misses any linter that fails without printing those
    # exact strings -- so this gate reported success unconditionally.
    TS_RC=0
    TS_OUT="$(cd frontend && npm run lint --silent 2>&1)" || TS_RC=$?
    if [[ $TS_RC -ne 0 ]]; then
      ERRORS+=("tsc: lint failed (exit ${TS_RC})\n${TS_OUT}")
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
