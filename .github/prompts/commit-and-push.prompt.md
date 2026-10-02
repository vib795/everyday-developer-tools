---
description: "Format, scan, verify, commit, and push changes. Runs security checks, formats code, shows a diff for review, then commits and pushes with a conventional commit message."
argument-hint: "Optional: scope or short description of the change (e.g. 'fix auth bug')"
agent: "agent"
tools: ["run_in_terminal", "read_file", "mcp_gitkraken_git_status", "mcp_gitkraken_git_add_or_commit", "mcp_gitkraken_git_push", "vscode_askQuestions"]
---

You are performing a safe, structured commit-and-push workflow. Follow every step below in order. Do not skip any step.

## Step 1 — Show current status

Run `git status` and `git diff --stat HEAD` to get a picture of what has changed. Show the user a concise summary grouped by: **staged**, **unstaged**, **untracked**.

## Step 2 — Format changed files

Format all modified files using the project's standard tooling:

- **Python** (`backend/`): run `uv run --project backend ruff format backend/app/` then `uv run --project backend ruff check backend/app/ --fix`
- **TypeScript/TSX** (`frontend/`): run `cd frontend && npm run lint -- --fix 2>/dev/null || true`

After formatting, stage any files that were changed by the formatter.

## Step 3 — Security and vulnerability scan

Run the pre-commit security hook directly:

```
.github/hooks/scripts/security-check.sh
```

Pipe in the commit payload:
```bash
echo '{"tool_name":"mcp_gitkraken_git_add_or_commit","tool_input":{"action":"commit"}}' \
  | .github/hooks/scripts/security-check.sh
```

If the script exits non-zero or reports **any blocking issue**, stop immediately. Report the findings to the user and do NOT proceed to commit. The user must fix the issues first.

Check specifically for:
- Hardcoded passwords, API keys, tokens, or private keys in staged changes
- HIGH or MEDIUM severity bandit findings
- ruff linting errors (not just warnings)
- TypeScript compile errors

## Step 4 — Show diff for user verification

Run `git diff --staged` and present the full diff to the user in a collapsed code block. Then ask the user to verify:

> "Here are all files staged for commit. Please review and confirm you want to proceed:"
>
> List each staged file with its change type (modified / added / deleted) and line count.
>
> - Are there any files that should NOT be committed?
> - Are there any files missing that should be included?
>
> **Reply 'yes' to proceed, or list files to exclude/add.**

Wait for explicit confirmation before continuing.

## Step 5 — Unstage files the user wants to exclude

If the user asked to exclude files, run `git restore --staged <file>` for each one. Confirm the updated staged list.

## Step 6 — Write a conventional commit message

Analyze the staged diff and write a commit message that follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

<body — what changed and why, wrapped at 72 chars>

<footer — breaking changes or issue refs if applicable>
```

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `ci`

Show the proposed message to the user and ask: "Does this commit message look right? Reply 'yes' or suggest changes."

Wait for confirmation.

## Step 7 — Commit

Run `git commit -m "<confirmed message>"`. Show the commit hash on success.

## Step 8 — Pre-push check

Before pushing, re-run the security check with the push payload:

```bash
echo '{"tool_name":"mcp_gitkraken_git_push","tool_input":{"directory":"."}}' \
  | .github/hooks/scripts/security-check.sh
```

If it fails, report the issue and do NOT push.

## Step 9 — Push

Run `git push`. Show the remote branch and commit SHA on success.

## Step 10 — Summary

Print a final summary:
- Branch pushed to
- Commit SHA and message
- Files committed (with change type)
- Any warnings that were raised (non-blocking) during the process

---

## Hard rules (never violate)

- **Never commit secrets.** If you detect any string that looks like a password, token, private key, or AWS access key in staged changes, block immediately and explain what you found.
- **Never use `--no-verify`.** Do not bypass git hooks.
- **Never force-push** without explicit user instruction (and even then, ask for confirmation).
- **Always wait for user confirmation** at Steps 4 and 6 before proceeding.
