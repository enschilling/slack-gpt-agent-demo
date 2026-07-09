from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from config import settings


API_BASE = "https://api.github.com"


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def _configured_repos(repo: str | None = None) -> list[str]:
    if repo:
        return [repo]
    return list(settings.github_repos)


def _get_json(path: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(f"{API_BASE}{path}", headers=_headers(), params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def summarize_github_activity(days: int = 7, repo: str | None = None) -> dict[str, Any]:
    if not settings.github_owner:
        return {"configured": False, "message": "Set GITHUB_OWNER before using GitHub tools."}

    repos = _configured_repos(repo)
    if not repos:
        return {"configured": False, "message": "Set GITHUB_REPOS to one or more comma-separated repositories."}

    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    summaries = []

    for repo_name in repos:
        full_name = f"{settings.github_owner}/{repo_name}"
        commits = _get_json(f"/repos/{full_name}/commits", {"since": since, "per_page": 20})
        pulls = _get_json(f"/repos/{full_name}/pulls", {"state": "all", "per_page": 20})
        issues = _get_json(
            f"/repos/{full_name}/issues",
            {"state": "open", "since": since, "per_page": 20},
        )

        open_issues = [item for item in issues if "pull_request" not in item]
        recent_prs = [
            {
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "updated_at": pr["updated_at"],
                "url": pr["html_url"],
            }
            for pr in pulls[:5]
        ]

        summaries.append(
            {
                "repo": full_name,
                "days": days,
                "commit_count_sample": len(commits),
                "recent_commits": [
                    {
                        "sha": commit["sha"][:7],
                        "message": commit["commit"]["message"].splitlines()[0],
                        "author": commit["commit"]["author"]["name"],
                        "url": commit["html_url"],
                    }
                    for commit in commits[:5]
                ],
                "recent_pull_requests": recent_prs,
                "open_issue_count_sample": len(open_issues),
                "recent_open_issues": [
                    {
                        "number": issue["number"],
                        "title": issue["title"],
                        "url": issue["html_url"],
                    }
                    for issue in open_issues[:5]
                ],
            }
        )

    return {"configured": True, "repositories": summaries}


def create_github_issue(repo: str, title: str, body: str) -> dict[str, Any]:
    if not settings.github_owner:
        return {"created": False, "message": "Set GITHUB_OWNER before creating issues."}
    if not settings.github_token:
        return {"created": False, "message": "Set GITHUB_TOKEN with repo issue permissions before creating issues."}

    full_name = f"{settings.github_owner}/{repo}"
    response = requests.post(
        f"{API_BASE}/repos/{full_name}/issues",
        headers=_headers(),
        json={"title": title, "body": body},
        timeout=20,
    )
    response.raise_for_status()
    issue = response.json()
    return {
        "created": True,
        "repo": full_name,
        "number": issue["number"],
        "title": issue["title"],
        "url": issue["html_url"],
    }
