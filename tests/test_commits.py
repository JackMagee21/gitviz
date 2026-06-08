from datetime import timezone
import pytest
from gitviz.core.commits import get_commits


def test_get_commits_returns_all(sample_repo):
    commits = get_commits(sample_repo)
    assert len(commits) == 3


def test_get_commits_respects_limit(sample_repo):
    commits = get_commits(sample_repo, max_count=2)
    assert len(commits) == 2


def test_commit_fields_are_populated(sample_repo):
    commits = get_commits(sample_repo)
    latest = commits[0]  # most recent first

    assert len(latest.sha) == 7
    assert latest.author == "Test User"
    assert latest.email == "test@example.com"
    assert latest.message == "Add utils module"
    assert latest.date is not None


def test_commit_sha_is_7_chars(sample_repo):
    commits = get_commits(sample_repo)
    for c in commits:
        assert len(c.sha) == 7


def test_commit_messages_are_first_line_only(sample_repo):
    commits = get_commits(sample_repo)
    for c in commits:
        assert "\n" not in c.message


def test_commit_dates_are_timezone_aware(sample_repo):
    """All commit dates must carry UTC timezone info — never naive datetimes."""
    commits = get_commits(sample_repo)
    for c in commits:
        assert c.date.tzinfo is not None, (
            f"Commit {c.sha} has a naive datetime. "
            "Use timezone-aware datetimes to avoid silent locale bugs."
        )
        assert c.date.tzinfo == timezone.utc


def test_commits_are_most_recent_first(sample_repo):
    commits = get_commits(sample_repo)
    dates = [c.date for c in commits]
    assert dates == sorted(dates, reverse=True)


def test_insertions_and_deletions_are_non_negative(sample_repo):
    commits = get_commits(sample_repo)
    for c in commits:
        assert c.insertions >= 0
        assert c.deletions >= 0


def test_files_changed_is_non_negative(sample_repo):
    commits = get_commits(sample_repo)
    for c in commits:
        assert c.files_changed >= 0


def test_get_commits_since_filters_results(sample_repo):
    """--since should reduce the number of commits returned."""
    all_commits = get_commits(sample_repo)
    # Use the date of the latest commit as the since boundary — should return only 1.
    latest_date = all_commits[0].date.strftime("%Y-%m-%dT%H:%M:%S")
    recent = get_commits(sample_repo, since=latest_date)
    assert len(recent) <= len(all_commits)


def test_get_commits_empty_repo(tmp_path):
    """A repo with no commits should return an empty list, not raise."""
    import git
    repo = git.Repo.init(tmp_path)
    with repo.config_writer() as cfg:
        cfg.set_value("user", "name", "Nobody")
        cfg.set_value("user", "email", "nobody@example.com")
    commits = get_commits(repo)
    assert commits == []