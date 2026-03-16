"""Shared test fixtures for People Analytics DWH tests."""

from __future__ import annotations

import pytest

from src.generate_data import PeopleAnalyticsDataGenerator


@pytest.fixture(scope="session")
def generator() -> PeopleAnalyticsDataGenerator:
    """Small generator for fast test runs."""
    return PeopleAnalyticsDataGenerator(
        n_employees=200,
        start_date="2022-01-01",
        end_date="2024-06-30",
        random_state=42,
    )


@pytest.fixture(scope="session")
def all_tables(generator: PeopleAnalyticsDataGenerator) -> dict:
    """Generate all tables once for the test session."""
    return generator.generate_all()
