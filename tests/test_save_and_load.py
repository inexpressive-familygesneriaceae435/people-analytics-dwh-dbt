"""Tests for CSV save/load functionality."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.generate_data import PeopleAnalyticsDataGenerator


@pytest.fixture
def tmp_generator(tmp_path: Path) -> tuple[PeopleAnalyticsDataGenerator, Path, Path]:
    gen = PeopleAnalyticsDataGenerator(
        n_employees=50, start_date="2023-01-01", end_date="2024-01-01", random_state=99
    )
    raw_dir = tmp_path / "raw"
    seeds_dir = tmp_path / "seeds"
    return gen, raw_dir, seeds_dir


class TestSaveAll:
    def test_creates_csv_files(self, tmp_generator: tuple) -> None:
        gen, raw_dir, seeds_dir = tmp_generator
        gen.save_all(raw_dir, seeds_dir)

        expected_files = [
            "raw_employees.csv", "raw_absences.csv", "raw_payroll.csv",
            "raw_promotions.csv", "raw_training.csv", "raw_surveys.csv",
            "raw_recruiting.csv",
        ]
        for f in expected_files:
            assert (raw_dir / f).exists(), f"Missing {f} in raw dir"
            assert (seeds_dir / f).exists(), f"Missing {f} in seeds dir"

    def test_csv_round_trip(self, tmp_generator: tuple) -> None:
        gen, raw_dir, seeds_dir = tmp_generator
        gen.save_all(raw_dir)
        loaded = pd.read_csv(raw_dir / "raw_employees.csv")
        assert len(loaded) == 50
        assert "employee_id" in loaded.columns

    def test_no_seeds_dir(self, tmp_generator: tuple) -> None:
        gen, raw_dir, _ = tmp_generator
        gen.save_all(raw_dir, dbt_seeds_dir=None)
        assert (raw_dir / "raw_employees.csv").exists()
