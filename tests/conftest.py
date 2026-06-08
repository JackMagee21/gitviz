import pytest
import git
from pathlib import Path


@pytest.fixture
def sample_repo(tmp_path: Path) -> git.Repo:
    """Creates a temporary Git repo with a few commits for testing.

    All commits are by a single author ("Test User") so contributor tests
    can assert on exact counts without accounting for noise.
    """
    repo = git.Repo.init(tmp_path)

    # Required for git to work in CI / clean environments, and also for the
    # subprocess-based get_commits() which reads the git config directly.
    with repo.config_writer() as cfg:
        cfg.set_value("user", "name", "Test User")
        cfg.set_value("user", "email", "test@example.com")

    # Commit 1
    file1 = tmp_path / "hello.py"
    file1.write_text("print('hello')\n")
    repo.index.add(["hello.py"])
    repo.index.commit("Initial commit")

    # Commit 2
    file1.write_text("print('hello world')\n")
    repo.index.add(["hello.py"])
    repo.index.commit("Update hello message")

    # Commit 3 — add a second file
    file2 = tmp_path / "utils.py"
    file2.write_text("def add(a, b):\n    return a + b\n")
    repo.index.add(["utils.py"])
    repo.index.commit("Add utils module")

    return repo


@pytest.fixture
def multi_author_repo(tmp_path: Path) -> git.Repo:
    """Creates a repo with commits from two distinct authors.

    Author A: 2 commits
    Author B: 1 commit

    Useful for testing contributor deduplication and percentage calculations.
    """
    repo = git.Repo.init(tmp_path)

    def commit_as(name: str, email: str, filename: str, content: str, message: str):
        with repo.config_writer() as cfg:
            cfg.set_value("user", "name", name)
            cfg.set_value("user", "email", email)
        f = tmp_path / filename
        f.write_text(content)
        repo.index.add([filename])
        repo.index.commit(message)

    commit_as("Alice", "alice@example.com", "a1.py", "x = 1\n",       "Alice first commit")
    commit_as("Bob",   "bob@example.com",   "b1.py", "y = 2\n",       "Bob first commit")
    commit_as("Alice", "alice@example.com", "a2.py", "z = 3\n",       "Alice second commit")

    return repo