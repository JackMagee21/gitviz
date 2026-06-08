from dataclasses import dataclass, field
from gitviz.core.commits import CommitInfo


@dataclass
class ContributorStats:
    author: str
    email: str
    commits: int = 0
    insertions: int = 0
    deletions: int = 0
    files_changed: int = 0
    commit_share: float = field(default=0.0, repr=False)

    @property
    def total_changes(self) -> int:
        return self.insertions + self.deletions


def get_contributor_stats(commits: list[CommitInfo]) -> list[ContributorStats]:
    """Aggregate commit data by author, sorted by commit count descending."""
    authors: dict[str, ContributorStats] = {}

    for commit in commits:
        key = commit.email

        if key not in authors:
            authors[key] = ContributorStats(author=commit.author, email=commit.email)

        authors[key].commits += 1
        authors[key].insertions += commit.insertions
        authors[key].deletions += commit.deletions
        authors[key].files_changed += commit.files_changed

    total = sum(s.commits for s in authors.values())
    sorted_stats = sorted(authors.values(), key=lambda c: c.commits, reverse=True)

    if total > 0:
        for s in sorted_stats:
            s.commit_share = round((s.commits / total) * 100, 1)

    return sorted_stats
