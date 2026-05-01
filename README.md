# vibe-check-cli

> Analyzes the vibe of any GitHub repo and delivers a brutally honest vibe report.

![CI](https://github.com/brianpelow/vibe-check-cli/actions/workflows/ci.yml/badge.svg)

## What it does

Scans a GitHub repo — commit messages, PR titles, issue titles, README tone,
contributor patterns — and classifies the overall vibe using an LLM.

## Example vibes

- **"chaotic genius"** — brilliant code, zero docs, commit messages like "fix" and "asdfgh"
- **"enterprise bureaucracy"** — 47 approvers required, every PR has a JIRA ticket
- **"solo founder at 2am"** — commit timestamps cluster around midnight, increasingly desperate messages
- **"over-engineered side project"** — Kubernetes for a todo app, 12 abstraction layers
- **"quiet professionalism"** — consistent commits, good docs, nobody is suffering
- **"abandoned dreams"** — last commit 3 years ago, ambitious README, empty src/

## Usage

```bash
pip install vibe-check-cli

vibe-check brianpelow/IncidentPilot
vibe-check torvalds/linux
vibe-check --detailed brianpelow/orbit-platform
```

## Setup

```bash
export GITHUB_TOKEN=your_token    # optional, raises rate limit
export OPENROUTER_API_KEY=your_key  # for AI vibe analysis
```

## License

Apache 2.0
