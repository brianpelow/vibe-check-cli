"""GitHub data collector — pulls commits, PRs, issues, and README."""

from __future__ import annotations

import os
import httpx
from dataclasses import dataclass, field


@dataclass
class RepoData:
    """Raw data collected from a GitHub repo."""
    repo: str
    description: str = ""
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    language: str = ""
    commit_messages: list[str] = field(default_factory=list)
    commit_hours: list[int] = field(default_factory=list)
    pr_titles: list[str] = field(default_factory=list)
    issue_titles: list[str] = field(default_factory=list)
    readme_excerpt: str = ""
    contributor_count: int = 0
    days_since_last_commit: int = 0
    topics: list[str] = field(default_factory=list)


class GitHubCollector:
    BASE = "https://api.github.com"

    def __init__(self, token: str = "") -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def collect(self, repo: str) -> RepoData:
        data = RepoData(repo=repo)
        try:
            with httpx.Client(timeout=20, headers=self.headers) as client:
                # Repo metadata
                r = client.get(f"{self.BASE}/repos/{repo}")
                if r.status_code == 200:
                    info = r.json()
                    data.description = info.get("description") or ""
                    data.stars = info.get("stargazers_count", 0)
                    data.forks = info.get("forks_count", 0)
                    data.open_issues = info.get("open_issues_count", 0)
                    data.language = info.get("language") or ""
                    data.topics = info.get("topics", [])

                # Commits
                r = client.get(f"{self.BASE}/repos/{repo}/commits", params={"per_page": 30})
                if r.status_code == 200:
                    commits = r.json()
                    for c in commits:
                        msg = c.get("commit", {}).get("message", "").split("\n")[0][:100]
                        data.commit_messages.append(msg)
                        date_str = c.get("commit", {}).get("author", {}).get("date", "")
                        if date_str:
                            try:
                                from datetime import datetime, timezone
                                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                                data.commit_hours.append(dt.hour)
                            except Exception:
                                pass
                    if commits:
                        from datetime import datetime, timezone
                        last = commits[0].get("commit", {}).get("author", {}).get("date", "")
                        if last:
                            try:
                                dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                                data.days_since_last_commit = (datetime.now(timezone.utc) - dt).days
                            except Exception:
                                pass

                # PRs
                r = client.get(f"{self.BASE}/repos/{repo}/pulls", params={"state": "closed", "per_page": 20})
                if r.status_code == 200:
                    data.pr_titles = [p.get("title", "")[:100] for p in r.json()]

                # Issues
                r = client.get(f"{self.BASE}/repos/{repo}/issues", params={"state": "all", "per_page": 20})
                if r.status_code == 200:
                    data.issue_titles = [i.get("title", "")[:100] for i in r.json() if "pull_request" not in i][:15]

                # README
                r = client.get(f"{self.BASE}/repos/{repo}/readme", headers={**self.headers, "Accept": "application/vnd.github.raw"})
                if r.status_code == 200:
                    data.readme_excerpt = r.text[:1500]

                # Contributors
                r = client.get(f"{self.BASE}/repos/{repo}/contributors", params={"per_page": 10})
                if r.status_code == 200:
                    data.contributor_count = len(r.json())

        except Exception:
            pass
        return data