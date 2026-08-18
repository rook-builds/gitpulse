"""Tests for gitpulse.core.fetch() — mocks subprocess so no real git repo needed."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from gitpulse.core import Item, fetch


def _make_git_output(*commits):
    """Build fake git log NUL-separated output from (sha, author, date_iso, subject) tuples."""
    lines = [f"{sha}\x00{author}\x00{date}\x00{subject}" for sha, author, date, subject in commits]
    return "\n".join(lines)


def _mock_result(stdout="", returncode=0, stderr=""):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


class TestFetch:
    def test_returns_items(self):
        out = _make_git_output(
            ("abc1234abc1234", "Alice", "2026-08-01T10:00:00+00:00", "Initial commit"),
            ("def5678def5678", "Bob", "2026-08-02T12:00:00+00:00", "Add feature"),
        )
        with patch("subprocess.run", return_value=_mock_result(out)):
            items = fetch(".", limit=10)
        assert len(items) == 2
        assert items[0].title == "Initial commit"
        assert items[0].author == "Alice"
        assert items[0].body == "abc1234a"  # first 8 chars

    def test_limit_passed_to_git(self):
        with patch("subprocess.run", return_value=_mock_result("")) as mock_run:
            fetch(".", limit=5)
        args = mock_run.call_args[0][0]
        assert "-5" in args

    def test_path_passed_to_git(self):
        with patch("subprocess.run", return_value=_mock_result("")) as mock_run:
            fetch("/some/repo", limit=5)
        args = mock_run.call_args[0][0]
        assert "/some/repo" in args

    def test_defaults_to_dot(self):
        with patch("subprocess.run", return_value=_mock_result("")) as mock_run:
            fetch(limit=5)
        args = mock_run.call_args[0][0]
        assert "." in args

    def test_git_nonzero_raises_runtime_error(self):
        with patch("subprocess.run", return_value=_mock_result("", returncode=128, stderr="fatal: not a git repository")):
            with pytest.raises(RuntimeError, match="git log failed"):
                fetch(".")

    def test_empty_repo_returns_empty_list(self):
        with patch("subprocess.run", return_value=_mock_result("")):
            items = fetch(".")
        assert items == []

    def test_created_at_is_datetime(self):
        out = _make_git_output(
            ("abc1234abc1234", "Alice", "2026-08-01T10:00:00+00:00", "A commit"),
        )
        with patch("subprocess.run", return_value=_mock_result(out)):
            items = fetch(".")
        assert isinstance(items[0].created_at, datetime)
        assert items[0].created_at.tzinfo is not None

    def test_git_not_found_raises_runtime_error(self):
        with patch("subprocess.run", side_effect=FileNotFoundError("git not found")):
            with pytest.raises(RuntimeError, match="git not found"):
                fetch(".")

    def test_malformed_lines_skipped(self):
        # a line with fewer than 4 NUL-separated fields should be skipped silently
        out = "not\x00enough\nfields"
        with patch("subprocess.run", return_value=_mock_result(out)):
            items = fetch(".")
        assert items == []

    def test_returns_item_dataclass(self):
        out = _make_git_output(
            ("abc1234abc1234", "Alice", "2026-08-01T10:00:00+00:00", "Test commit"),
        )
        with patch("subprocess.run", return_value=_mock_result(out)):
            items = fetch(".")
        assert isinstance(items[0], Item)
