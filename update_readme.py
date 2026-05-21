#!/usr/bin/env python3
"""Auto-update README.md projects table from GitHub public API."""

import json
import os
import re
import urllib.request

USERNAME = "qzwtrp"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "qzwtrp-profile-update",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"GitHub API error {e.code}: {body}") from e


def fetch_repos():
    repos = api(f"/users/{USERNAME}/repos?per_page=100\u0026type=owner")
    filtered = [
        r for r in repos
        if not r["fork"]
        and not r.get("private", False)
    ]
    filtered.sort(key=lambda r: r["pushed_at"], reverse=True)
    return filtered


def build_projects_table(repos):
    lines = ["| project | description | tech |", "|---------|-------------|------|"]
    for r in repos[:10]:
        name = r["name"]
        desc = (r["description"] or "no description").replace("|", chr(92) + "|")
        lang = r["language"] or "—"
        url = r["html_url"]
        lines.append(f"| [`{name}`]({url}) | {desc} | {lang} |")
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"> last sync: {ts}")
    NL = chr(10)
    return NL.join(lines)


def update_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    repos = fetch_repos()
    table = build_projects_table(repos)

    NL = chr(10)
    pattern = re.compile(
        r"(### \U0001f6e0\ufe0f projects" + NL + NL + ")[\s\S]*?(" + NL + "---)",
        re.MULTILINE,
    )

    if pattern.search(content):
        content = pattern.sub(r"\1" + table + r"\2", content)
        print(f"Updated projects table with {len(repos[:10])} public repos")
    else:
        print("WARNING: Could not find projects section in README")
        return

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    update_readme()
