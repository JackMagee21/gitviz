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
    date: datetime
    files_changed: int
    insertions: int
    deletions: int


_RECORD_SEP = ">>START<<"


def get_commits(
    repo: git.Repo,
    max_count: int = 500,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> list[CommitInfo]:
    """Extract commit data from a repository in a single subprocess call."""
    cmd = [
        "git", "log",
        f"--max-count={max_count}",
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

    if result.returncode != 0:
        if "does not have any commits yet" in result.stderr:
            return []
        result.check_returncode()

    return _parse_numstat_output(result.stdout)


def _parse_numstat_output(raw: str) -> list[CommitInfo]:
    commits: list[CommitInfo] = []
    blocks = raw.split(_RECORD_SEP)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = [l for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        parts = lines[0].split("\x1f")
        if len(parts) < 5:
            continue

        sha, author, email, message, iso_date = parts[:5]
        date = datetime.fromisoformat(iso_date).astimezone(timezone.utc)

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
