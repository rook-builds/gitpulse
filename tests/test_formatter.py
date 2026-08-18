"""Tests for gitpulse.core formatters."""

import csv
import io
import json

from gitpulse.core import to_csv, to_json, to_table, to_text


class TestToText:
    def test_includes_title(self, sample_items):
        assert "Initial commit" in to_text(sample_items)

    def test_includes_author(self, sample_items):
        assert "alice" in to_text(sample_items)

    def test_includes_hash(self, sample_items):
        assert "abc12345" in to_text(sample_items)

    def test_empty(self, empty_items):
        assert "No items found" in to_text(empty_items)


class TestToJson:
    def test_valid_json(self, sample_items):
        data = json.loads(to_json(sample_items))
        assert data["count"] == 2
        assert data["items"][0]["title"] == "Initial commit"

    def test_created_at_iso(self, sample_items):
        data = json.loads(to_json(sample_items))
        assert data["items"][0]["created_at"].startswith("2026-07-10")


class TestToTable:
    def test_has_header(self, sample_items):
        assert "| # | Subject |" in to_table(sample_items)

    def test_has_rows(self, sample_items):
        assert to_table(sample_items).count("\n") >= 3


class TestToCsv:
    def test_roundtrips(self, sample_items):
        rows = list(csv.reader(io.StringIO(to_csv(sample_items))))
        assert rows[0] == ["title", "author", "created_at", "hash"]
        assert rows[1][0] == "Initial commit"
