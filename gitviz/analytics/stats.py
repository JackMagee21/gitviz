from dataclasses import dataclass
from collections import Counter
from datetime import datetime
from gitviz.core.commits import CommitInfo
from gitviz.analytics.contributors import get_contributor_stats


@dataclass
class RepoStats:
    total_commits: int
    total_authors: int
    total_insertions: int
    total_deletions: int
    most_active_day: str
    most_active_author: str
    first_commit: datetime
    latest_commit: datetime
    avg_commits_per_day: float


def get_repo_stats(commits: list[CommitInfo]) -> RepoStats:
    """Compute high-level repository statistics from a list of commits."""
    if not commits:
        raise ValueError("No commits to analyse.")

    contributor_stats = get_contributor_stats(commits)
    total_authors = len(contributor_stats)
    most_active_author = contributor_stats[0].author if contributor_stats else "-"

    total_insertions = sum(c.insertions for c in commits)
    total_deletions = sum(c.deletions for c in commits)

    day_counts = Counter(c.date.strftime("%A") for c in commits)
    most_active_day = day_counts.most_common(1)[0][0]

    dates = [c.date for c in commits]
    first_commit = min(dates)
    latest_commit = max(dates)

    delta_days = (latest_commit - first_commit).days or 1
    avg_commits_per_day = round(len(commits) / delta_days, 2)

    return RepoStats(
        total_commits=len(commits),
        total_authors=total_authors,
        total_insertions=total_insertions,
        total_deletions=total_deletions,
        most_active_day=most_active_day,
        most_active_author=most_active_author,
        first_commit=first_commit,
        latest_commit=latest_commit,
        avg_commits_per_day=avg_commits_per_day,
    )
