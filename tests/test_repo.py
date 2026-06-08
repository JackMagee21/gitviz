import pytest
from pathlib import Path

import git

from gitviz.core.repo import open_repo, RepoError


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_open_repo_returns_repo_instance(sample_repo):
    repo = open_repo(str(sample_repo.working_dir))
    assert isinstance(repo, git.Repo)


def test_open_repo_accepts_subdirectory(sample_repo):
    """open_repo walks up to the repo root when given a subdirectory."""
    subdir = Path(sample_repo.working_dir) / "subdir"
    subdir.mkdir()

    repo = open_repo(str(subdir))
    assert isinstance(repo, git.Repo)
    assert Path(repo.working_dir).resolve() == Path(sample_repo.working_dir).resolve()


def test_open_repo_default_dot_inside_repo(sample_repo, monkeypatch):
    monkeypatch.chdir(sample_repo.working_dir)
    repo = open_repo(".")
    assert isinstance(repo, git.Repo)


def test_open_repo_working_dir_is_populated(sample_repo):
    repo = open_repo(str(sample_repo.working_dir))
    assert repo.working_dir is not None
    assert Path(repo.working_dir).exists()


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

def test_open_repo_nonexistent_path_raises_repo_error():
    with pytest.raises(RepoError, match="does not exist"):
        open_repo("/this/path/absolutely/does/not/exist/anywhere")


def test_open_repo_non_git_directory_raises_repo_error(tmp_path):
    with pytest.raises(RepoError, match="No Git repository found"):
        open_repo(str(tmp_path))


def test_open_repo_file_path_raises_repo_error(tmp_path):
    file_path = tmp_path / "not_a_repo.txt"
    file_path.write_text("hello")
    with pytest.raises(RepoError):
        open_repo(str(file_path))


# ---------------------------------------------------------------------------
# Exception chaining tests
# ---------------------------------------------------------------------------

def test_repo_error_chains_original_exception(tmp_path):
    """RepoError must chain the original gitpython exception via __cause__
    so that tracebacks include the root cause when debugging.
    """
    with pytest.raises(RepoError) as exc_info:
        open_repo(str(tmp_path))
    assert exc_info.value.__cause__ is not None


# ---------------------------------------------------------------------------
# RepoError contract tests
# ---------------------------------------------------------------------------

def test_repo_error_is_exception():
    err = RepoError("something went wrong")
    assert isinstance(err, Exception)
    assert str(err) == "something went wrong"


def test_repo_error_message_contains_path():
    bad_path = "/nonexistent/repo"
    with pytest.raises(RepoError) as exc_info:
        open_repo(bad_path)
    assert "nonexistent" in str(exc_info.value)