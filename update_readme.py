#!/usr/bin/env python3
"""Auto-update README.md projects table from GitHub GraphQL API."""

import json
import os
import re
import urllib.request

USERNAME = "qzwtrp"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def graphql(query, variables=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "qzwtrp-profile-update",
        "Content-Type": "application/json",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_repos():
    query = """
    {
      viewer {
        repositories(first: 100, ownerAffiliations: [OWNER], orderBy: {field: PUSHED_AT, direction: DESC}) {
          nodes {
            name
            description
            pushedAt
            isPrivate
            primaryLanguage { name }
            isArchived
            nameWithOwner
            url
          }
        }
      }
    }
    """
    data = graphql(query)
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")

    repos = data["data"]["viewer"]["repositories"]["nodes"]
    filtered = [r for r in repos if r["name"] != USERNAME and not r.get("isArchived", False)]
    return filtered


def build_projects_table(repos):
    lines = ["| project | description | tech |", "|---------|-------------|------|"]
    for r in repos[:10]:
        name = r["name"]
        desc = (r["description"] or "no description").replace("|", "\\|")
        lang = r["primaryLanguage"]["name"] if r.get("primaryLanguage") else "—"
        url = r["url"]
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
