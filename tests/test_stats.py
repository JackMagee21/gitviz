import pytest
from gitviz.core.commits import get_commits
from gitviz.analytics.stats import get_repo_stats


def test_total_commits(sample_repo):
    commits = get_commits(sample_repo)
    s = get_repo_stats(commits)
    assert s.total_commits == 3


def test_total_authors(sample_repo):
    commits = get_commits(sample_repo)
    s = get_repo_stats(commits)
    assert s.total_authors == 1


def test_total_authors_multi(multi_author_repo):
    """Author count uses email deduplication — consistent with contributors module."""
    commits = get_commits(multi_author_repo)
    s = get_repo_stats(commits)
    assert s.total_authors == 2


def test_most_active_author(sample_repo):
    commits = get_commits(sample_repo)
    s = get_repo_stats(commits)
    assert s.most_active_author == "Test User"


def test_most_active_author_multi(multi_author_repo):
    """Alice has 2 commits vs Bob's 1, so Alice should be the top author."""
    commits = get_commits(multi_author_repo)
    s = get_repo_stats(commits)
    assert s.most_active_author == "Alice"


def test_first_and_latest_commit_order(sample_repo):
    commits = get_commits(sample_repo)
    s = get_repo_stats(commits)
    assert s.first_commit <= s.latest_commit


def test_commit_dates_are_timezone_aware(sample_repo):
    """first_commit and latest_commit must be timezone-aware."""
    commits = get_commits(sample_repo)
    s = get_repo_stats(commits)
    assert s.first_commit.tzinfo is not None
    assert s.latest_commit.tzinfo is not None


def test_insertions_and_deletions_are_non_negative(sample_repo):
    commits = get_commits(sample_repo)
    s = get_repo_stats(commits)
    assert s.total_insertions >= 0
    assert s.total_deletions >= 0


def test_avg_commits_per_day_is_positive(sample_repo):
    commits = get_commits(sample_repo)
    s = get_repo_stats(commits)
    assert s.avg_commits_per_day > 0


def test_empty_commits_raises():
    with pytest.raises(ValueError, match="No commits"):
        get_repo_stats([])