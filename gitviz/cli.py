import click
from importlib.metadata import version, PackageNotFoundError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

from gitviz.core.repo import open_repo, RepoError
from gitviz.core.commits import get_commits
from gitviz.analytics.contributors import get_contributor_stats
from gitviz.analytics.stats import get_repo_stats

console = Console()


def _get_version() -> str:
    try:
        return version("gitviz")
    except PackageNotFoundError:
        return "unknown"


@click.group()
@click.version_option(version=_get_version(), prog_name="gitviz")
def main():
    """Git Visualizer - analyse and visualise your Git history."""
    pass


_since_option = click.option(
    "--since", "-s",
    default=None,
    metavar="DATE",
    help="Only include commits after this date (e.g. 2024-01-01 or 6 months ago).",
)
_until_option = click.option(
    "--until", "-u",
    default=None,
    metavar="DATE",
    help="Only include commits before this date (same format as --since).",
)


@main.command()
@click.argument("path", default=".")
@click.option("--limit", "-n", default=20, help="Number of commits to show.")
@_since_option
@_until_option
def log(path, limit, since, until):
    """Show recent commits in a formatted table."""
    try:
        repo = open_repo(path)
    except RepoError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    commits = get_commits(repo, max_count=limit, since=since, until=until)

    if not commits:
        console.print("[yellow]No commits found.[/yellow]")
        return

    table = Table(title=f"Recent Commits - {repo.working_dir}", show_lines=False)
    table.add_column("SHA",     style="cyan",  no_wrap=True)
    table.add_column("Date",    style="dim",   no_wrap=True)
    table.add_column("Author",  style="green", no_wrap=True)
    table.add_column("Message", style="white")
    table.add_column("+",       style="green", justify="right", no_wrap=True)
    table.add_column("-",       style="red",   justify="right", no_wrap=True)

    for c in commits:
        table.add_row(
            c.sha,
            c.date.strftime("%Y-%m-%d"),
            c.author,
            c.message,
            str(c.insertions),
            str(c.deletions),
        )

    console.print(table)


@main.command()
@click.argument("path", default=".")
@click.option("--limit", "-n", default=500, help="Number of commits to analyse.")
@_since_option
@_until_option
def contributors(path, limit, since, until):
    """Show contributor breakdown - commits, lines changed, and share."""
    try:
        repo = open_repo(path)
    except RepoError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    commits = get_commits(repo, max_count=limit, since=since, until=until)

    if not commits:
        console.print("[yellow]No commits found.[/yellow]")
        return

    stats = get_contributor_stats(commits)

    table = Table(title=f"Contributors - {repo.working_dir}", show_lines=False)
    table.add_column("Author",   style="green",  no_wrap=True)
    table.add_column("Commits",  style="cyan",   justify="right", no_wrap=True)
    table.add_column("Share",    style="yellow", justify="right", no_wrap=True)
    table.add_column("+",        style="green",  justify="right", no_wrap=True)
    table.add_column("-",        style="red",    justify="right", no_wrap=True)
    table.add_column("Files",    style="dim",    justify="right", no_wrap=True)
    table.add_column("Activity", no_wrap=True)

    max_commits = stats[0].commits if stats else 1

    for c in stats:
        bar_len = int((c.commits / max_commits) * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)

        table.add_row(
            c.author,
            str(c.commits),
            f"{c.commit_share}%",
            str(c.insertions),
            str(c.deletions),
            str(c.files_changed),
            f"[cyan]{bar}[/cyan]",
        )

    console.print(table)
    console.print(f"[dim]Analysed {len(commits)} commits across {len(stats)} contributor(s).[/dim]")


@main.command()
@click.argument("path", default=".")
@click.option("--limit", "-n", default=500, help="Number of commits to analyse.")
@_since_option
@_until_option
def stats(path, limit, since, until):
    """Show a high-level summary of repository health."""
    try:
        repo = open_repo(path)
    except RepoError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    commits = get_commits(repo, max_count=limit, since=since, until=until)

    if not commits:
        console.print("[yellow]No commits found.[/yellow]")
        return

    s = get_repo_stats(commits)

    panels = [
        Panel(f"[cyan]{s.total_commits}[/cyan]",         title="Commits",         expand=True),
        Panel(f"[cyan]{s.total_authors}[/cyan]",          title="Authors",         expand=True),
        Panel(f"[green]+{s.total_insertions}[/green]",    title="Insertions",      expand=True),
        Panel(f"[red]-{s.total_deletions}[/red]",         title="Deletions",       expand=True),
        Panel(f"[yellow]{s.most_active_day}[/yellow]",    title="Most Active Day", expand=True),
        Panel(f"[yellow]{s.most_active_author}[/yellow]", title="Top Author",      expand=True),
        Panel(f"[cyan]{s.avg_commits_per_day}[/cyan]",    title="Commits/Day",     expand=True),
        Panel(f"[dim]{s.first_commit.strftime('%Y-%m-%d')}[/dim]", title="First Commit",  expand=True),
        Panel(f"[dim]{s.latest_commit.strftime('%Y-%m-%d')}[/dim]", title="Latest Commit", expand=True),
    ]

    console.print()
    console.print(f"[bold]Repository Stats - {repo.working_dir}[/bold]")
    console.print()
    console.print(Columns(panels))
    console.print()
    console.print(f"[dim]Based on the last {len(commits)} commits.[/dim]")
