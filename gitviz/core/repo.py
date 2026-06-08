from pathlib import Path
import git


class RepoError(Exception):
    pass


def open_repo(path: str) -> git.Repo:
    """Open a Git repository at the given path.

    Walks up parent directories to find the repository root, so callers
    may pass any subdirectory within a repo.

    Raises:
        RepoError: if the path does not exist, or no Git repository is found.
    """
    resolved = Path(path).resolve()

    if not resolved.exists():
        raise RepoError(f"Path does not exist: {resolved}")

    try:
        repo = git.Repo(resolved, search_parent_directories=True)
    except git.InvalidGitRepositoryError as e:
        raise RepoError(f"No Git repository found at: {resolved}") from e
    except git.NoSuchPathError as e:
        raise RepoError(f"Path not found: {resolved}") from e

    return repo