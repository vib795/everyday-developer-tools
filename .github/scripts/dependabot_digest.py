#!/usr/bin/env python3
"""Email a prioritized digest of open Dependabot PRs so they can be approved in a
sensible order. Invoked on a schedule by .github/workflows/dependabot-digest.yml.

Standard library only. Sends via Gmail SMTP using an app password, so no
third-party action ever sees the mail credentials. Reads PR data with `gh`,
which the workflow provides via GH_TOKEN.

Required env: MAIL_USERNAME, MAIL_APP_PASSWORD. Optional: MAIL_TO (defaults to
MAIL_USERNAME), REPO (defaults to the wrench.tools repo).
"""
import json
import os
import re
import smtplib
import ssl
import subprocess
import sys
from email.mime.text import MIMEText
from html import escape

REPO = os.environ.get("REPO", "vib795/everyday-developer-tools")


def open_dependabot_prs():
    raw = subprocess.check_output(
        [
            "gh", "pr", "list", "-R", REPO, "--state", "open", "-L", "100",
            "--json", "number,title,url,headRefName,autoMergeRequest",
        ]
    )
    return [p for p in json.loads(raw) if p["headRefName"].startswith("dependabot/")]


def ecosystem(branch):
    parts = branch.split("/")
    return parts[1] if len(parts) > 1 else ""


def is_major_bump(title):
    # "Bump X from 1.2.3 to 4.0.0" / "from v1 to v7" -> compare leading integers.
    m = re.search(r"from\s+v?(\d+)[\w.\-]*\s+to\s+v?(\d+)", title)
    return bool(m) and int(m.group(1)) != int(m.group(2))


def tier(pr):
    """1 = armed/approve-now, 2 = low risk, 3 = backend major, 4 = frontend major."""
    if pr.get("autoMergeRequest"):
        return 1
    eco = ecosystem(pr["headRefName"])
    if eco in ("github_actions", "docker"):
        return 2
    if not is_major_bump(pr["title"]):
        return 2
    if "/frontend" in pr["headRefName"] or eco == "npm_and_yarn":
        return 4
    return 3


TIER_META = {
    1: ("#1a7f37", "Approve now (auto-merge armed — merges + deploys on approval)"),
    2: ("#0969da", "Low risk (CI actions/images or minor/patch — quick review, then approve + merge)"),
    3: ("#bc4c00", "Backend / runtime majors (review + test one at a time)"),
    4: ("#cf222e", "Frontend majors (highest risk — do last, with a click-through)"),
}


def build_html(prs):
    by_tier = {1: [], 2: [], 3: [], 4: []}
    for p in prs:
        by_tier[tier(p)].append(p)

    sections = []
    for t in (1, 2, 3, 4):
        items = sorted(by_tier[t], key=lambda x: x["number"])
        if not items:
            continue
        color, label = TIER_META[t]
        sections.append(f'<h3 style="margin:18px 0 6px;color:{color}">Tier {t} — {label}</h3>')
        sections.append('<table style="border-collapse:collapse;width:100%">')
        for p in items:
            sections.append(
                '<tr>'
                f'<td style="padding:4px 8px;white-space:nowrap"><a href="{escape(p["url"])}">#{p["number"]}</a></td>'
                f'<td style="padding:4px 8px">{escape(p["title"])}</td>'
                '</tr>'
            )
        sections.append("</table>")

    return (
        '<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;'
        'font-size:14px;line-height:1.5;color:#1f2328;max-width:720px">'
        f'<p>There are <strong>{len(prs)} open Dependabot PR(s)</strong> on '
        f'{escape(REPO)}. Recommended approval order below — safest first. Only '
        'auto-merge-armed PRs merge on approval; the rest are approve-and-merge after '
        'review. Comment <code>@claude review this</code> on any PR for a changelog + '
        'test verdict.</p>'
        f'{"".join(sections)}</div>'
    )


def main():
    user = os.environ.get("MAIL_USERNAME")
    password = os.environ.get("MAIL_APP_PASSWORD")
    if not user or not password:
        print("MAIL_USERNAME / MAIL_APP_PASSWORD not set; skipping. Add them as repo secrets.")
        return 0

    prs = open_dependabot_prs()
    if not prs:
        print("No open Dependabot PRs; nothing to send.")
        return 0

    to = os.environ.get("MAIL_TO") or user
    msg = MIMEText(build_html(prs), "html")
    msg["Subject"] = f"Dependabot PRs to approve — {len(prs)} open · wrench.tools"
    msg["From"] = user
    msg["To"] = to

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
    print(f"Sent digest for {len(prs)} PR(s) to {to}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
