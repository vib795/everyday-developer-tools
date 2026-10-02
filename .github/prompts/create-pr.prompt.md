---
description: "Create a pull request from the current branch. Generates a PR title and description from the diff, asks for confirmation, then opens the PR via the GitHub CLI."
argument-hint: "Optional: target base branch (default: main) or extra context for the PR description"
agent: "agent"
tools: ["run_in_terminal", "vscode_askQuestions"]
---

You are creating a GitHub pull request from the current branch. Follow every step in order.

## Step 1 — Pre-flight checks

1. Verify `gh` is available: `gh --version`. If not found, stop and tell the user to install the GitHub CLI (`brew install gh`).
2. Verify the user is authenticated: `gh auth status`. If not, stop and prompt them to run `gh auth login`.
3. Get the current branch: `git branch --show-current`. If it is `main`, `master`, `develop`, or `trunk`, stop and warn the user they are about to open a PR from a primary branch — ask if they really want to continue.
4. Determine the base branch:
   - Use any branch the user provided as an argument.
   - Otherwise check `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
   - Show the user: "Base branch: `<base>` — reply with a different branch name to change it, or press Enter to continue."

## Step 2 — Gather diff context

Run the following and collect the output for analysis:
```bash
git log <base>..HEAD --oneline
git diff <base>..HEAD --stat
git diff <base>..HEAD
```

Summarise what changed: number of commits, files modified/added/deleted, key functional areas touched.

## Step 3 — Check for unpushed commits

Run `git status -sb`. If the branch has commits not yet pushed to the remote, warn:

> "Your branch has unpushed commits. Consider running `/commit-and-push` first, or I can push the current branch now."

Ask whether to push first or continue creating the PR against what is already on the remote.

## Step 4 — Generate PR title and description

Using the diff summary from Step 2, write a PR title and body that follow this structure:

**Title** — one line, ≤ 72 chars, using Conventional Commits style:
```
<type>(<scope>): <short summary>
```

**Body** — markdown, structured as:

```markdown
## Summary
<!-- What this PR does and why -->

## Changes
<!-- Bullet list of key changes grouped by area -->

## Testing
<!-- How the change was tested: unit tests, manual steps, etc. -->

## Notes
<!-- Breaking changes, migration steps, follow-up tasks, or "None" -->
```

Fill in all sections from the diff. Do not leave template placeholders.

Show the full proposed title and body to the user and ask:

> "Does this PR description look right? Reply 'yes' to proceed, or tell me what to change."

Wait for confirmation before continuing.

## Step 5 — Security review of PR content

Before opening the PR, scan the diff one final time for:
- Hardcoded secrets, tokens, API keys, or private key material
- Files that should not be public (`.env`, `*.pem`, `*.key`, credentials files)

If any are found, stop immediately. Do NOT open the PR. Report the exact file and line, and instruct the user to remove the secret and re-push before creating the PR.

## Step 6 — Open the PR

Run:
```bash
gh pr create \
  --base <base> \
  --title "<confirmed title>" \
  --body "<confirmed body>" \
  --draft
```

Open as a **draft** by default (safer — lets the user promote it when ready). If the user explicitly asked for a ready-for-review PR, omit `--draft`.

## Step 7 — Summary

Print:
- PR URL (from `gh pr create` output)
- Title
- Base ← Head
- Draft status
- Next suggested action: "Mark ready with `gh pr ready <number>` or promote it in the GitHub UI."

---

## Hard rules (never violate)

- **Never open a PR that contains secrets.** Always run Step 5 before Step 6.
- **Always show the full PR description and wait for confirmation** before calling `gh pr create`.
- **Default to draft PRs.** Only create a ready-for-review PR if the user explicitly requests it.
- **Never force-push** to prepare the branch without explicit user instruction.
