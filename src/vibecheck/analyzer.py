"""Vibe analyzer — classifies repo vibe using LLM or rule-based fallback."""

from __future__ import annotations

import os
from dataclasses import dataclass
from vibecheck.collector import RepoData


VIBES = [
    "chaotic genius",
    "enterprise bureaucracy",
    "solo founder at 2am",
    "over-engineered side project",
    "quiet professionalism",
    "abandoned dreams",
    "tutorial graveyard",
    "hype-driven development",
    "obsessive perfectionist",
    "corporate open-source theatre",
    "passionate amateur",
    "burnout in progress",
]


@dataclass
class VibeReport:
    repo: str
    vibe: str
    score: int
    summary: str
    evidence: list[str]
    roast: str
    rating: str


def analyze(data: RepoData) -> VibeReport:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if api_key:
        return _ai_analyze(data, api_key)
    return _rule_analyze(data)


def _ai_analyze(data: RepoData, api_key: str) -> VibeReport:
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        prompt = f"""You are a brutally honest but funny senior engineer analyzing the vibe of a GitHub repo.

Repo: {data.repo}
Description: {data.description or "none"}
Language: {data.language}
Stars: {data.stars} | Forks: {data.forks} | Open issues: {data.open_issues}
Days since last commit: {data.days_since_last_commit}
Contributors: {data.contributor_count}
Topics: {', '.join(data.topics) or 'none'}

Recent commit messages (last 15):
{chr(10).join(f'- {m}' for m in data.commit_messages[:15])}

PR titles:
{chr(10).join(f'- {t}' for t in data.pr_titles[:8])}

Issue titles:
{chr(10).join(f'- {t}' for t in data.issue_titles[:8])}

README excerpt:
{data.readme_excerpt[:800]}

Commit hour distribution: {data.commit_hours[:20]}

Pick the best vibe from this list: {', '.join(VIBES)}

Respond with EXACTLY this format (no other text):
VIBE: <vibe name>
SCORE: <1-100 where 100 is peak vibe>
SUMMARY: <one punchy sentence describing the overall vibe>
EVIDENCE: <3 specific observations separated by |>
ROAST: <one savage but affectionate roast line about this repo>
RATING: <a made-up rating like "4/5 merge conflicts" or "3/5 abandoned dreams">"""

        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_ai_response(data.repo, response.choices[0].message.content)
    except Exception:
        return _rule_analyze(data)


def _parse_ai_response(repo: str, text: str) -> VibeReport:
    lines = {l.split(":")[0].strip(): ":".join(l.split(":")[1:]).strip()
             for l in text.strip().splitlines() if ":" in l}
    return VibeReport(
        repo=repo,
        vibe=lines.get("VIBE", "chaotic genius"),
        score=int(lines.get("SCORE", "75").strip() or "75"),
        summary=lines.get("SUMMARY", "Vibes detected."),
        evidence=lines.get("EVIDENCE", "||").split("|"),
        roast=lines.get("ROAST", "No notes."),
        rating=lines.get("RATING", "unrated"),
    )


def _rule_analyze(data: RepoData) -> VibeReport:
    """Rule-based vibe detection without LLM."""
    evidence = []
    scores: dict[str, int] = {v: 0 for v in VIBES}

    if data.days_since_last_commit > 365:
        scores["abandoned dreams"] += 40
        evidence.append(f"Last commit was {data.days_since_last_commit} days ago")
    elif data.days_since_last_commit > 90:
        scores["abandoned dreams"] += 20

    night_commits = sum(1 for h in data.commit_hours if h >= 22 or h <= 4)
    if data.commit_hours and night_commits / len(data.commit_hours) > 0.4:
        scores["solo founder at 2am"] += 35
        evidence.append(f"{night_commits}/{len(data.commit_hours)} commits after 10pm")

    bad_msgs = sum(1 for m in data.commit_messages if m.lower() in
                   ["fix", "wip", "update", "changes", "test", "asdf", ".", "misc"])
    if bad_msgs > 5:
        scores["chaotic genius"] += 30
        evidence.append(f"{bad_msgs} commit messages with zero information content")

    if any(t in ["kubernetes", "microservices", "distributed"] for t in data.topics) and data.stars < 50:
        scores["over-engineered side project"] += 35
        evidence.append("Kubernetes topology for a project with fewer stars than my age")

    if data.contributor_count == 1 and data.stars > 100:
        scores["obsessive perfectionist"] += 25
        evidence.append(f"One contributor, {data.stars} stars — someone is very dedicated")

    if not evidence:
        scores["quiet professionalism"] += 30
        evidence.append("Suspiciously well-maintained — no red flags detected")

    top_vibe = max(scores, key=lambda k: scores[k])
    score = min(scores[top_vibe] + 50, 100)

    roasts = {
        "abandoned dreams": "The README has more ambition than the git log.",
        "solo founder at 2am": "The git blame is just one person slowly losing their mind.",
        "chaotic genius": "This code works and nobody knows why, including the author.",
        "over-engineered side project": "A Dockerfile that could run a bank, for a project three people use.",
        "quiet professionalism": "Distressingly normal. Seek help.",
        "obsessive perfectionist": "The kind of repo that makes you feel bad about your own repos.",
    }

    return VibeReport(
        repo=data.repo,
        vibe=top_vibe,
        score=score,
        summary=f"This repo is giving strong '{top_vibe}' energy.",
        evidence=[e for e in evidence if e][:3],
        roast=roasts.get(top_vibe, "Vibes are complicated here."),
        rating=f"{score // 20}/5 {top_vibe.split()[0]} moments",
    )