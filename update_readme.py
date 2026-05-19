#!/usr/bin/env python3
"""Auto-update README.md projects table from GitHub API."""

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
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_repos():
    # /user/repos returns both public and private repos for the authenticated user
    repos = api("/user/repos?per_page=100&sort=pushed")
    filtered = [r for r in repos if r["name"] != USERNAME and not r["fork"]]
    filtered.sort(key=lambda r: r["pushed_at"], reverse=True)
    return filtered


def build_projects_table(repos):
    lines = ["| project | description | tech |", "|---------|-------------|------|"]
    for r in repos[:10]:
        name = r["name"]
        desc = (r["description"] or "no description").replace("|", "\\|")
        lang = r["language"] or "—"
        url = r["html_url"]
        lines.append(f"| [`{name}`]({url}) | {desc} | {lang} |")
    return "\n".join(lines)


def update_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    repos = fetch_repos()
    table = build_projects_table(repos)

    pattern = re.compile(
        r"(### \U0001f6e0\ufe0f projects\n\n)[\s\S]*?(\n---)",
        re.MULTILINE,
    )

    if pattern.search(content):
        content = pattern.sub(r"\1" + table + r"\2", content)
        print(f"Updated projects table with {len(repos[:10])} repos")
    else:
        print("WARNING: Could not find projects section in README")
        return

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    update_readme()
