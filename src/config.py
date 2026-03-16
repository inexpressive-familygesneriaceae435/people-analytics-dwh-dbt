"""Application configuration using Pydantic BaseSettings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class DataSettings(BaseSettings):
    """Synthetic data generation settings."""

    seed_random_state: int = 42
    num_employees: int = 2000
    date_range_start: str = "2019-01-01"
    date_range_end: str = "2024-12-31"

    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}


class DbtSettings(BaseSettings):
    """dbt project settings."""

    dbt_project_dir: str = "dbt_project"
    dbt_profiles_dir: str = "dbt_project"
    dbt_target: str = "dev"
    duckdb_path: str = "data/people_analytics.duckdb"

    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}


class AppSettings(BaseSettings):
    """Root application settings."""

    log_level: str = "INFO"
    base_dir: Path = Path(__file__).resolve().parent.parent

    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}

    @property
    def data_settings(self) -> DataSettings:
        return DataSettings()

    @property
    def dbt_settings(self) -> DbtSettings:
        return DbtSettings()


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Singleton settings instance."""
    return AppSettings()
