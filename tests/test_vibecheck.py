"""Tests for vibe-check-cli."""

from vibecheck.collector import RepoData
from vibecheck.analyzer import analyze, _rule_analyze, VibeReport


def make_repo(**kwargs) -> RepoData:
    defaults = dict(
        repo="test/repo", description="A test repo", stars=10, forks=2,
        open_issues=3, language="Python", commit_messages=[], commit_hours=[],
        pr_titles=[], issue_titles=[], readme_excerpt="", contributor_count=1,
        days_since_last_commit=5, topics=[],
    )
    defaults.update(kwargs)
    return RepoData(**defaults)


def test_analyze_returns_vibe_report() -> None:
    data = make_repo()
    report = analyze(data)
    assert isinstance(report, VibeReport)
    assert report.vibe != ""
    assert 0 <= report.score <= 100


def test_abandoned_repo_detected() -> None:
    data = make_repo(days_since_last_commit=500)
    report = _rule_analyze(data)
    assert report.vibe == "abandoned dreams"
    assert report.score > 0


def test_night_owl_commits_detected() -> None:
    data = make_repo(commit_hours=[23, 0, 1, 2, 23, 0, 1, 23, 0, 2])
    report = _rule_analyze(data)
    assert report.vibe == "solo founder at 2am"


def test_bad_commit_messages_detected() -> None:
    data = make_repo(commit_messages=["fix", "wip", "update", "changes", "test", "fix", "wip"])
    report = _rule_analyze(data)
    assert report.vibe == "chaotic genius"


def test_over_engineered_detected() -> None:
    data = make_repo(topics=["kubernetes", "microservices"], stars=10)
    report = _rule_analyze(data)
    assert report.vibe == "over-engineered side project"


def test_report_has_roast() -> None:
    data = make_repo()
    report = _rule_analyze(data)
    assert len(report.roast) > 0


def test_report_has_rating() -> None:
    data = make_repo()
    report = _rule_analyze(data)
    assert len(report.rating) > 0


def test_score_never_exceeds_100() -> None:
    data = make_repo(
        days_since_last_commit=600,
        commit_hours=[23, 0, 1, 2, 23],
        commit_messages=["fix", "wip", "update", "changes", "test", "fix", "wip"],
        topics=["kubernetes"],
        stars=5,
    )
    report = _rule_analyze(data)
    assert report.score <= 100