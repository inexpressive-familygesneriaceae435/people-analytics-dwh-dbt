"""Tests for the synthetic data generator."""

from __future__ import annotations

import pandas as pd

from src.generate_data import (
    ABSENCE_TYPES,
    DEPARTMENTS,
    GENDERS,
    RECRUITING_STATUSES,
    TRAINING_STATUSES,
    PeopleAnalyticsDataGenerator,
)


class TestEmployees:
    def test_row_count(self, all_tables: dict) -> None:
        assert len(all_tables["raw_employees"]) == 200

    def test_required_columns(self, all_tables: dict) -> None:
        expected = {
            "employee_id", "first_name", "last_name", "email", "gender",
            "birth_date", "hire_date", "department", "job_title", "job_level",
            "location", "employment_type", "base_annual_salary", "is_active",
        }
        assert expected.issubset(set(all_tables["raw_employees"].columns))

    def test_employee_id_unique(self, all_tables: dict) -> None:
        df = all_tables["raw_employees"]
        assert df["employee_id"].is_unique

    def test_departments_valid(self, all_tables: dict) -> None:
        df = all_tables["raw_employees"]
        valid_depts = set(DEPARTMENTS.keys())
        assert set(df["department"].unique()).issubset(valid_depts)

    def test_genders_valid(self, all_tables: dict) -> None:
        df = all_tables["raw_employees"]
        assert set(df["gender"].unique()).issubset(set(GENDERS))

    def test_job_levels_range(self, all_tables: dict) -> None:
        df = all_tables["raw_employees"]
        assert df["job_level"].min() >= 1
        assert df["job_level"].max() <= 6

    def test_salary_positive(self, all_tables: dict) -> None:
        df = all_tables["raw_employees"]
        assert (df["base_annual_salary"] > 0).all()

    def test_hire_before_termination(self, all_tables: dict) -> None:
        df = all_tables["raw_employees"]
        terminated = df[df["termination_date"].notna()].copy()
        terminated["hire_dt"] = pd.to_datetime(terminated["hire_date"])
        terminated["term_dt"] = pd.to_datetime(terminated["termination_date"])
        assert (terminated["hire_dt"] < terminated["term_dt"]).all()

    def test_active_flag_consistency(self, all_tables: dict) -> None:
        df = all_tables["raw_employees"]
        active = df[df["is_active"]]
        assert active["termination_date"].isna().all()

    def test_reproducibility(self) -> None:
        g1 = PeopleAnalyticsDataGenerator(n_employees=50, random_state=123)
        g2 = PeopleAnalyticsDataGenerator(n_employees=50, random_state=123)
        t1 = g1.generate_all()
        t2 = g2.generate_all()
        pd.testing.assert_frame_equal(t1["raw_employees"], t2["raw_employees"])


class TestAbsences:
    def test_not_empty(self, all_tables: dict) -> None:
        assert len(all_tables["raw_absences"]) > 0

    def test_absence_id_unique(self, all_tables: dict) -> None:
        assert all_tables["raw_absences"]["absence_id"].is_unique

    def test_absence_types_valid(self, all_tables: dict) -> None:
        df = all_tables["raw_absences"]
        assert set(df["absence_type"].unique()).issubset(set(ABSENCE_TYPES))

    def test_hours_positive(self, all_tables: dict) -> None:
        df = all_tables["raw_absences"]
        assert (df["hours_absent"] > 0).all()

    def test_employee_id_exists(self, all_tables: dict) -> None:
        emp_ids = set(all_tables["raw_employees"]["employee_id"])
        abs_ids = set(all_tables["raw_absences"]["employee_id"])
        assert abs_ids.issubset(emp_ids)


class TestPayroll:
    def test_not_empty(self, all_tables: dict) -> None:
        assert len(all_tables["raw_payroll"]) > 0

    def test_payroll_id_unique(self, all_tables: dict) -> None:
        assert all_tables["raw_payroll"]["payroll_id"].is_unique

    def test_base_salary_positive(self, all_tables: dict) -> None:
        df = all_tables["raw_payroll"]
        assert (df["base_salary"] > 0).all()

    def test_net_pay_calculated(self, all_tables: dict) -> None:
        df = all_tables["raw_payroll"]
        expected = df["base_salary"] + df["overtime_pay"] + df["bonus"] - df["deductions"]
        pd.testing.assert_series_equal(df["net_pay"], expected, check_names=False)


class TestPromotions:
    def test_promotion_id_unique(self, all_tables: dict) -> None:
        df = all_tables["raw_promotions"]
        if len(df) > 0:
            assert df["promotion_id"].is_unique

    def test_salary_change_positive(self, all_tables: dict) -> None:
        df = all_tables["raw_promotions"]
        if len(df) > 0:
            assert (df["salary_change_pct"] > 0).all()

    def test_level_progression(self, all_tables: dict) -> None:
        df = all_tables["raw_promotions"]
        if len(df) > 0:
            assert (df["new_job_level"] >= df["previous_job_level"]).all()


class TestTraining:
    def test_not_empty(self, all_tables: dict) -> None:
        assert len(all_tables["raw_training"]) > 0

    def test_training_id_unique(self, all_tables: dict) -> None:
        assert all_tables["raw_training"]["training_id"].is_unique

    def test_statuses_valid(self, all_tables: dict) -> None:
        df = all_tables["raw_training"]
        assert set(df["status"].unique()).issubset(set(TRAINING_STATUSES))

    def test_completed_has_score(self, all_tables: dict) -> None:
        df = all_tables["raw_training"]
        completed = df[df["status"] == "Completed"]
        assert completed["score"].notna().all()


class TestSurveys:
    def test_not_empty(self, all_tables: dict) -> None:
        assert len(all_tables["raw_surveys"]) > 0

    def test_survey_id_unique(self, all_tables: dict) -> None:
        assert all_tables["raw_surveys"]["survey_id"].is_unique

    def test_scores_bounded(self, all_tables: dict) -> None:
        df = all_tables["raw_surveys"]
        score_cols = [
            "engagement_score", "satisfaction_score", "manager_score",
            "growth_score", "wellbeing_score", "overall_score",
        ]
        for col in score_cols:
            assert df[col].min() >= 1.0, f"{col} has values below 1.0"
            assert df[col].max() <= 5.0, f"{col} has values above 5.0"


class TestRecruiting:
    def test_not_empty(self, all_tables: dict) -> None:
        assert len(all_tables["raw_recruiting"]) > 0

    def test_application_id_unique(self, all_tables: dict) -> None:
        assert all_tables["raw_recruiting"]["application_id"].is_unique

    def test_statuses_valid(self, all_tables: dict) -> None:
        df = all_tables["raw_recruiting"]
        assert set(df["status"].unique()).issubset(set(RECRUITING_STATUSES))

    def test_hired_has_hire_date(self, all_tables: dict) -> None:
        df = all_tables["raw_recruiting"]
        hired = df[df["status"] == "Hired"]
        assert hired["hire_date"].notna().all()


class TestAllTables:
    def test_seven_tables_generated(self, all_tables: dict) -> None:
        assert len(all_tables) == 7

    def test_table_names(self, all_tables: dict) -> None:
        expected = {
            "raw_employees", "raw_absences", "raw_payroll",
            "raw_promotions", "raw_training", "raw_surveys", "raw_recruiting",
        }
        assert set(all_tables.keys()) == expected
