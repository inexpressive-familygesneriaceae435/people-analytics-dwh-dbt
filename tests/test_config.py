"""Tests for application configuration."""

from __future__ import annotations

from src.config import DataSettings, DbtSettings, get_settings


class TestDataSettings:
    def test_defaults(self) -> None:
        ds = DataSettings()
        assert ds.seed_random_state == 42
        assert ds.num_employees == 2000
        assert ds.date_range_start == "2019-01-01"
        assert ds.date_range_end == "2024-12-31"


class TestDbtSettings:
    def test_defaults(self) -> None:
        dbt = DbtSettings()
        assert dbt.dbt_project_dir == "dbt_project"
        assert dbt.dbt_target == "dev"
        assert "duckdb" in dbt.duckdb_path


class TestAppSettings:
    def test_singleton(self) -> None:
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_nested_settings(self) -> None:
        s = get_settings()
        assert isinstance(s.data_settings, DataSettings)
        assert isinstance(s.dbt_settings, DbtSettings)
