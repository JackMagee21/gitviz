from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import subprocess
import git


@dataclass
class CommitInfo:
    sha: str
    author: str
    email: str
    message: str
    date: datetime          # always UTC-aware
    files_changed: int
    insertions: int
    deletions: int


# Sentinel placed at the START of each record's format line so that splitting
# on it yields one block per commit with header + numstat together.
_RECORD_SEP = ">>START<<"


def get_commits(
    repo: git.Repo,
    max_count: int = 500,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> list[CommitInfo]:
    """Extract commit data from a repository in a single subprocess call.

    Uses ``git log --numstat`` to collect diff stats for all commits at once,
    avoiding the O(n) subprocess-per-commit cost of gitpython's
    ``commit.stats`` API.

    Args:
        repo:      An open git.Repo instance.
        max_count: Maximum number of commits to return.
        since:     Only include commits after this date (git date string,
                   e.g. ``"2024-01-01"`` or ``"6 months ago"``).
        until:     Only include commits before this date (same format).

    Returns:
        List of CommitInfo, most recent first. Empty list if no commits exist.
    """
    cmd = [
        "git", "log",
        f"--max-count={max_count}",
        # Sentinel goes at the START of the format so splitting yields
        # one block per commit: [empty, commit1_block, commit2_block, ...]
        f"--format={_RECORD_SEP}%n%H\x1f%an\x1f%ae\x1f%s\x1f%cI",
        "--numstat",
    ]

    if since:
        cmd.append(f"--after={since}")
    if until:
        cmd.append(f"--before={until}")

    result = subprocess.run(
        cmd,
        cwd=repo.working_dir,
        capture_output=True,
        text=True,
    )

    # git exits 128 with "does not have any commits yet" on a fresh repo.
    # Treat that as an empty result rather than an error.
    if result.returncode != 0:
        if "does not have any commits yet" in result.stderr:
            return []
        result.check_returncode()   # re-raise for genuine errors

    return _parse_numstat_output(result.stdout)


def _parse_numstat_output(raw: str) -> list[CommitInfo]:
    """Parse the combined --format / --numstat output into CommitInfo objects.

    Output shape (sentinel at the start of each record):

        >>START<<
        <sha>\x1f<author>\x1f<email>\x1f<subject>\x1f<iso-date>

        <ins>\t<del>\t<filename>   (zero or more numstat lines)

        >>START<<
        ...
    """
    commits: list[CommitInfo] = []

    # Split on the sentinel; block[0] is always empty (before first sentinel).
    blocks = raw.split(_RECORD_SEP)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = [l for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        # First line is the header.
        parts = lines[0].split("\x1f")
        if len(parts) < 5:
            continue

        sha, author, email, message, iso_date = parts[:5]

        # Parse ISO 8601 date; git --format=%cI always includes timezone offset.
        date = datetime.fromisoformat(iso_date).astimezone(timezone.utc)

        # Remaining lines are numstat rows: "<ins>\t<del>\t<path>"
        # Binary files show "-\t-\t<path>"; we treat those as 0.
        insertions = 0
        deletions = 0
        files_changed = 0

        for line in lines[1:]:
            stat_parts = line.split("\t", 2)
            if len(stat_parts) < 3:
                continue
            ins_raw, del_raw, _ = stat_parts
            files_changed += 1
            insertions += int(ins_raw) if ins_raw.isdigit() else 0
            deletions += int(del_raw) if del_raw.isdigit() else 0

        commits.append(CommitInfo(
            sha=sha[:7],
            author=author,
            email=email,
            message=message,
            date=date,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
        ))

    return commits