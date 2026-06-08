# gitviz

A fast, zero-config CLI for exploring Git repository history in your terminal.
Understand who is contributing, what is changing, and how active your repository is — without leaving the command line.

```
$ gitviz contributors .

 Contributors — /home/user/my-project
┌───────────────┬─────────┬───────┬───────┬──────┬───────┬──────────────────────┐
│ Author        │ Commits │ Share │     + │    - │ Files │ Activity             │
├───────────────┼─────────┼───────┼───────┼──────┼───────┼──────────────────────┤
│ Alice Chen    │      87 │ 52.1% │ 14203 │ 3812 │   201 │ ████████████████░░░░ │
│ Bob Martínez  │      56 │ 33.5% │  9411 │ 2100 │   134 │ ████████████░░░░░░░░ │
│ Carol Osei    │      24 │ 14.4% │  3204 │  890 │    67 │ █████░░░░░░░░░░░░░░░ │
└───────────────┴─────────┴───────┴───────┴──────┴───────┴──────────────────────┘
Analysed 167 commits across 3 contributor(s).
```

---

## Features

- **`log`** — formatted commit table with author, date, message, and diff stats
- **`contributors`** — per-author breakdown with commit share and inline activity bar
- **`stats`** — high-level repository health summary (total commits, authors, busiest day, top author, commits/day)
- Pure terminal output via [Rich](https://github.com/Textualize/rich) — no browser, no server, no config files
- Works on any local Git repository

---

## Requirements

- Python ≥ 3.10
- Git installed and available on `PATH`

---

## Installation

### Easiest — pipx (recommended for most users)

[pipx](https://pipx.pypa.io) is designed specifically for installing CLI tools. It handles PATH automatically on every platform and keeps gitviz isolated from your other Python projects.

**Windows (PowerShell):**
```powershell
python -m pip install pipx
python -m pipx ensurepath
```
Close and reopen PowerShell, then:
```powershell
pipx install git+https://github.com/your-org/gitviz.git
```

**Mac / Linux:**
```bash
brew install pipx          # or: python3 -m pip install pipx
pipx ensurepath
pipx install git+https://github.com/your-org/gitviz.git
```

That's it. `gitviz` will be available from any directory in any new terminal window.

---

### Windows — automatic install script

If you'd rather not use pipx, run the included PowerShell script which installs the package and fixes PATH for you:

```powershell
git clone https://github.com/your-org/gitviz.git
cd gitviz
.\scripts\install.ps1
```

Then close and reopen PowerShell and run `gitviz --help`.

---

### Mac / Linux — automatic install script

```bash
git clone https://github.com/your-org/gitviz.git
cd gitviz
bash scripts/install.sh
```

Then open a new terminal and run `gitviz --help`.

---

### Manual install (all platforms)

If you prefer to do it yourself:

```bash
git clone https://github.com/your-org/gitviz.git
cd gitviz
pip install .
```

**If `gitviz` is not found after install**, Python's Scripts folder is not on your PATH. Find it with:

```bash
python -m pip show gitviz
# Look at the "Location:" line, e.g.:
# Location: C:\Users\you\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages
# Your Scripts folder is one level up from site-packages, in \Scripts
```

Then add that Scripts folder to your PATH — see [Windows PATH instructions](#adding-python-scripts-to-path-on-windows) below.

---

### Adding Python Scripts to PATH on Windows

1. Press the **Windows key** and search for **"Edit the system environment variables"**
2. Click **"Environment Variables..."**
3. Under **"User variables"**, select **Path** and click **Edit**
4. Click **New** and paste your Scripts folder path (e.g. `C:\Users\you\AppData\Local\Python\pythoncore-3.14-64\Scripts`)
5. Click OK on all windows, then open a new PowerShell window

Or run this one-liner in PowerShell (replace the path with yours from `pip show gitviz`):

```powershell
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\you\AppData\Local\Python\pythoncore-3.14-64\Scripts",
    [EnvironmentVariableTarget]::User
)
```

---

### Dependencies

| Package | Purpose |
|---|---|
| [gitpython](https://gitpython.readthedocs.io) | Reading Git repository data |
| [click](https://click.palletsprojects.com) | CLI argument parsing |
| [rich](https://github.com/Textualize/rich) | Terminal tables, panels, and colour |

---

## Usage

All commands accept a `PATH` argument (defaults to `.`, the current directory). `gitviz` will walk up parent directories to find the repository root, so you can run it from any subdirectory inside a repo.

### `log` — recent commit history

```bash
gitviz log [PATH] [--limit N] [--since DATE] [--until DATE]
```

Shows the most recent commits in a colour-coded table.

| Column | Description |
|---|---|
| SHA | Abbreviated 7-character commit hash |
| Date | Commit date (YYYY-MM-DD) |
| Author | Commit author name |
| Message | First line of the commit message |
| + | Lines inserted |
| - | Lines deleted |

**Options**

| Flag | Default | Description |
|---|---|---|
| `--limit` / `-n` | `20` | Maximum number of commits to display |
| `--since` / `-s` | — | Only show commits after this date (e.g. `"2024-01-01"` or `"6 months ago"`) |
| `--until` / `-u` | — | Only show commits before this date (same format) |

**Example**

```bash
gitviz log ~/projects/my-api -n 50 --since "3 months ago"
```

---

### `contributors` — author breakdown

```bash
gitviz contributors [PATH] [--limit N] [--since DATE] [--until DATE]
```

Aggregates commit history by author, sorted by commit count descending.

| Column | Description |
|---|---|
| Author | Contributor display name |
| Commits | Total commits attributed to this author |
| Share | Percentage of total commits |
| + | Total lines inserted across all commits |
| - | Total lines deleted across all commits |
| Files | Cumulative files changed |
| Activity | Proportional bar chart relative to the top contributor |

> **Note:** Authors are deduplicated by email address, so name changes across commits are handled correctly.

**Options**

| Flag | Default | Description |
|---|---|---|
| `--limit` / `-n` | `500` | Number of commits to analyse |
| `--since` / `-s` | — | Only include commits after this date |
| `--until` / `-u` | — | Only include commits before this date |

**Example**

```bash
gitviz contributors . --since "2024-01-01" --until "2024-12-31"
```

---

### `stats` — repository summary

```bash
gitviz stats [PATH] [--limit N] [--since DATE] [--until DATE]
```

Displays a panel grid of high-level repository metrics.

| Metric | Description |
|---|---|
| Commits | Total commits analysed |
| Authors | Distinct author count (by email) |
| Insertions | Total lines inserted |
| Deletions | Total lines deleted |
| Most Active Day | Day of the week with the most commits |
| Top Author | Author with the most commits |
| Commits/Day | Average daily commit rate over the repo's lifetime |
| First Commit | Date of the earliest commit in the analysed window |
| Latest Commit | Date of the most recent commit |

**Options**

| Flag | Default | Description |
|---|---|---|
| `--limit` / `-n` | `500` | Number of commits to analyse |
| `--since` / `-s` | — | Only include commits after this date |
| `--until` / `-u` | — | Only include commits before this date |

**Example**

```bash
gitviz stats . --since "6 months ago"

```

### Layer responsibilities

```
CLI (cli.py)
  └── calls Core to open the repo and fetch commits
        └── calls Analytics to compute derived statistics
              └── returns plain dataclasses back up to CLI for rendering
```

The CLI layer owns all Rich formatting. The analytics and core layers are pure Python — no I/O, no terminal dependencies — which keeps them easy to test and reuse.

---

## Development

### Running tests

```bash
pip install -e ".[dev]"
pytest
```

Tests use a fully in-memory temporary Git repository created by the `sample_repo` fixture in `conftest.py`. No network access or real repositories are required.

### Running a specific test module

```bash
pytest tests/test_contributors.py -v
```

### Linting and formatting

```bash
ruff check .
ruff format .
```

---

## Performance Notes

gitviz uses a single `git log --numstat` subprocess call to collect all commit data at once, rather than one subprocess per commit. This keeps it fast even on large repositories.

For very large histories (10,000+ commits), use `--since` to limit the date range rather than relying solely on `--limit`.

## Licence

MIT