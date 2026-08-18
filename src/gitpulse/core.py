"""gitpulse core — inspect recent git commit history from a local repository."""
from __future__ import annotations

import csv
import io
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Item:
    """One commit from a git repository."""

    title: str        # commit subject
    url: str          # empty for local repos
    author: str = ""  # author name
    score: int = 0    # unused (kept for formatter compatibility)
    comments: int = 0 # unused (kept for formatter compatibility)
    created_at: Optional[datetime] = None
    body: str = ""    # short commit hash (first 8 chars)

    def _created_iso(self) -> str:
        return self.created_at.isoformat() if self.created_at else ""


# --------------------------------------------------------------------------- #
# fetch — reads git log via subprocess
# --------------------------------------------------------------------------- #
def fetch(path: Optional[str] = None, limit: int = 10) -> list[Item]:
    """Fetch the last `limit` commits from the git repo at `path`.

    Args:
        path: Path to a local git repository. Defaults to current directory.
        limit: Maximum number of commits to return.

    Returns:
        A list of Item objects, newest commit first.

    Raises:
        RuntimeError: If git is not found or the path is not a git repository.
    """
    repo_path = path or "."

    # Use NUL byte as field separator to handle pipes/special chars in messages
    fmt = "%H%x00%an%x00%ai%x00%s"

    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", f"--pretty=format:{fmt}", f"-{limit}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError as e:
        raise RuntimeError("git not found — is git installed and on PATH?") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"git command timed out after 15s") from e

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"git log failed: {stderr or 'unknown error'}")

    items: list[Item] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x00", 3)
        if len(parts) < 4:
            continue
        sha, author, date_str, subject = parts

        dt: Optional[datetime] = None
        try:
            dt = datetime.fromisoformat(date_str.strip())
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass

        items.append(Item(
            title=subject.strip(),
            url="",
            author=author.strip(),
            score=0,
            comments=0,
            created_at=dt,
            body=sha.strip()[:8],
        ))

    return items


# --------------------------------------------------------------------------- #
# formatters — tested by tests/test_formatter.py. Do not rewrite.
# --------------------------------------------------------------------------- #
def to_text(items: list[Item], source: str = "gitpulse") -> str:
    if not items:
        return f"# {source}\n\nNo items found."
    lines = [f"# {source}", ""]
    for i, it in enumerate(items, 1):
        meta = []
        if it.author:
            meta.append(f"by {it.author}")
        if it.created_at:
            meta.append(it.created_at.strftime("%Y-%m-%d"))
        if it.body:
            meta.append(it.body)
        suffix = f"  ({' · '.join(meta)})" if meta else ""
        lines.append(f"{i}. **{it.title}**{suffix}")
        if it.url:
            lines.append(f"   {it.url}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def to_json(items: list[Item], source: str = "gitpulse") -> str:
    payload = {
        "source": source,
        "count": len(items),
        "items": [
            {**asdict(it), "created_at": it._created_iso()} for it in items
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def to_table(items: list[Item], source: str = "gitpulse") -> str:
    if not items:
        return "No items found."
    header = "| # | Subject | Author | Date | Hash |"
    sep = "|---|---------|--------|------|------|"
    rows = [header, sep]
    for i, it in enumerate(items, 1):
        title = it.title.replace("|", "\\|")
        date = it.created_at.strftime("%Y-%m-%d") if it.created_at else ""
        rows.append(
            f"| {i} | {title} | {it.author} | {date} | {it.body} |"
        )
    return "\n".join(rows)


def to_csv(items: list[Item], source: str = "gitpulse") -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["title", "author", "created_at", "hash"])
    for it in items:
        w.writerow([it.title, it.author, it._created_iso(), it.body])
    return buf.getvalue()
