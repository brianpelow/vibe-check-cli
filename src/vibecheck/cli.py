"""vibe-check CLI."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from vibecheck.collector import GitHubCollector
from vibecheck.analyzer import analyze

app = typer.Typer(name="vibe-check", help="Brutally honest GitHub repo vibe analysis.")
console = Console()

VIBE_COLORS = {
    "chaotic genius": "magenta",
    "enterprise bureaucracy": "blue",
    "solo founder at 2am": "yellow",
    "over-engineered side project": "cyan",
    "quiet professionalism": "green",
    "abandoned dreams": "dim",
    "tutorial graveyard": "red",
    "hype-driven development": "bright_yellow",
    "obsessive perfectionist": "bright_blue",
    "corporate open-source theatre": "blue",
    "passionate amateur": "bright_green",
    "burnout in progress": "red",
}


@app.command()
def main(
    repo: str = typer.Argument(..., help="GitHub repo (org/repo)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show full evidence breakdown"),
    token: str = typer.Option("", "--token", "-t", help="GitHub token"),
) -> None:
    """Check the vibe of any GitHub repo."""
    console.print(f"\n[dim]Scanning[/dim] [cyan]{repo}[/cyan] [dim]for vibes...[/dim]\n")

    collector = GitHubCollector(token=token)
    data = collector.collect(repo)
    report = analyze(data)

    color = VIBE_COLORS.get(report.vibe, "white")

    console.print(Panel.fit(
        f"[{color}]{report.vibe.upper()}[/{color}]\n\n"
        f"[bold]{report.summary}[/bold]\n\n"
        f"[dim italic]{report.roast}[/dim italic]",
        title=f"Vibe Report — {repo}",
        border_style=color,
        padding=(1, 2),
    ))

    console.print(f"  Vibe score: [{color}]{'█' * (report.score // 10)}{'░' * (10 - report.score // 10)}[/{color}] {report.score}/100")
    console.print(f"  Rating: [bold]{report.rating}[/bold]\n")

    if detailed and report.evidence:
        console.print("[bold]Evidence:[/bold]")
        for e in report.evidence:
            if e.strip():
                console.print(f"  [dim]→[/dim] {e.strip()}")
        console.print()


if __name__ == "__main__":
    app()