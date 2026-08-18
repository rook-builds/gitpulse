"""Shared fixtures for gitpulse tests."""

from datetime import datetime, timezone

import pytest

from gitpulse.core import Item


@pytest.fixture
def sample_items():
    return [
        Item(
            title="Initial commit",
            url="",
            author="alice",
            score=0,
            comments=0,
            created_at=datetime(2026, 7, 10, 17, 43, 30, tzinfo=timezone.utc),
            body="abc12345",
        ),
        Item(
            title="Add feature, with commas",
            url="",
            author="bob",
            score=0,
            comments=0,
            created_at=datetime(2026, 7, 9, 12, 0, 0, tzinfo=timezone.utc),
            body="def67890",
        ),
    ]


@pytest.fixture
def empty_items():
    return []
