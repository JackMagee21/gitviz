import pytest
from gitviz.core.commits import get_commits
from gitviz.analytics.contributors import get_contributor_stats


# ---------------------------------------------------------------------------
# Single-author repo
# ---------------------------------------------------------------------------

def test_contributor_count(sample_repo):
    commits = get_commits(sample_repo)
    stats = get_contributor_stats(commits)
    assert len(stats) == 1


def test_contributor_commit_count(sample_repo):
    commits = get_commits(sample_repo)
    stats = get_contributor_stats(commits)
    assert stats[0].commits == 3


def test_contributor_name(sample_repo):
    commits = get_commits(sample_repo)
    stats = get_contributor_stats(commits)
    assert stats[0].author == "Test User"


def test_sorted_by_commits_descending(sample_repo):
    commits = get_commits(sample_repo)
    stats = get_contributor_stats(commits)
    counts = [s.commits for s in stats]
    assert counts == sorted(counts, reverse=True)


def test_commit_share_sums_to_100(sample_repo):
    """commit_share on ContributorStats replaces the old contribution_percentage function."""
    commits = get_commits(sample_repo)
    stats = get_contributor_stats(commits)
    total = sum(s.commit_share for s in stats)
    assert abs(total - 100.0) < 0.2   # allow for rounding across many authors


def test_commit_share_empty_list():
    stats = get_contributor_stats([])
    assert stats == []


def test_total_changes_property(sample_repo):
    commits = get_commits(sample_repo)
    stats = get_contributor_stats(commits)
    for s in stats:
        assert s.total_changes == s.insertions + s.deletions


# ---------------------------------------------------------------------------
# Multi-author repo
# ---------------------------------------------------------------------------

def test_multi_author_count(multi_author_repo):
    commits = get_commits(multi_author_repo)
    stats = get_contributor_stats(commits)
    assert len(stats) == 2


def test_multi_author_deduplication_by_email(multi_author_repo):
    """Alice commits twice under the same email — must appear as one contributor."""
    commits = get_commits(multi_author_repo)
    stats = get_contributor_stats(commits)
    alice = next((s for s in stats if s.email == "alice@example.com"), None)
    assert alice is not None
    assert alice.commits == 2


def test_multi_author_sorted_order(multi_author_repo):
    commits = get_commits(multi_author_repo)
    stats = get_contributor_stats(commits)
    # Alice has 2 commits, Bob has 1 — Alice should be first.
    assert stats[0].email == "alice@example.com"
    assert stats[1].email == "bob@example.com"


def test_multi_author_shares_sum_to_100(multi_author_repo):
    commits = get_commits(multi_author_repo)
    stats = get_contributor_stats(commits)
    total = sum(s.commit_share for s in stats)
    assert abs(total - 100.0) < 0.2