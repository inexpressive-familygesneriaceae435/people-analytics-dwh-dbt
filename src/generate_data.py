"""Synthetic People Analytics data generator.

Generates 7 realistic HR tables with correlated distributions:
- employees: Master employee records with hire/termination lifecycle
- absences: Daily absence events (sick, vacation, personal, etc.)
- payroll: Monthly compensation records
- promotions: Career progression events
- training: Course enrollment and completion records
- surveys: Quarterly engagement/satisfaction surveys
- recruiting: Full hiring funnel (application → screening → interview → offer → hire)

All dates span 2019-01-01 to 2024-12-31, simulating a ~2000-employee organization.
Distributions are calibrated against published People Analytics benchmarks
(SHRM 2023 Human Capital Benchmarking, BLS JOLTS, Gallup Q12).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker
from loguru import logger

from src.config import get_settings

fake = Faker("en_US")
Faker.seed(42)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEPARTMENTS: dict[str, dict[str, float]] = {
    "Engineering": {"weight": 0.20, "salary_mult": 1.30, "turnover_mult": 0.85},
    "Sales": {"weight": 0.18, "salary_mult": 1.10, "turnover_mult": 1.20},
    "Operations": {"weight": 0.15, "salary_mult": 0.90, "turnover_mult": 1.00},
    "Customer Support": {"weight": 0.12, "salary_mult": 0.85, "turnover_mult": 1.30},
    "Marketing": {"weight": 0.10, "salary_mult": 1.00, "turnover_mult": 0.95},
    "Finance": {"weight": 0.10, "salary_mult": 1.15, "turnover_mult": 0.80},
    "HR": {"weight": 0.08, "salary_mult": 0.95, "turnover_mult": 0.75},
    "Product": {"weight": 0.07, "salary_mult": 1.25, "turnover_mult": 0.90},
}

JOB_LEVELS: dict[int, dict[str, object]] = {
    1: {"title_suffix": "Associate", "salary_range": (40_000, 60_000), "weight": 0.30},
    2: {"title_suffix": "Analyst", "salary_range": (55_000, 80_000), "weight": 0.25},
    3: {"title_suffix": "Senior", "salary_range": (75_000, 110_000), "weight": 0.22},
    4: {"title_suffix": "Lead", "salary_range": (100_000, 140_000), "weight": 0.13},
    5: {"title_suffix": "Manager", "salary_range": (120_000, 170_000), "weight": 0.07},
    6: {"title_suffix": "Director", "salary_range": (150_000, 220_000), "weight": 0.03},
}

LOCATIONS = ["New York", "San Francisco", "Chicago", "Austin", "Remote"]
LOCATION_WEIGHTS = [0.25, 0.20, 0.18, 0.17, 0.20]

GENDERS = ["Male", "Female", "Non-Binary"]
GENDER_WEIGHTS = [0.48, 0.48, 0.04]

ABSENCE_TYPES = ["Sick Leave", "Vacation", "Personal", "Parental", "Bereavement", "Jury Duty"]
ABSENCE_WEIGHTS = [0.30, 0.35, 0.15, 0.10, 0.05, 0.05]

TERMINATION_REASONS = [
    "Voluntary - New Opportunity",
    "Voluntary - Relocation",
    "Voluntary - Career Change",
    "Voluntary - Compensation",
    "Voluntary - Work-Life Balance",
    "Involuntary - Performance",
    "Involuntary - Restructuring",
    "Involuntary - Misconduct",
    "Retirement",
]
TERM_REASON_WEIGHTS = [0.25, 0.10, 0.10, 0.15, 0.10, 0.12, 0.10, 0.03, 0.05]

TRAINING_CATEGORIES = [
    "Technical Skills",
    "Leadership",
    "Compliance",
    "Soft Skills",
    "Product Knowledge",
    "Safety",
    "DEI",
]

TRAINING_STATUSES = ["Completed", "In Progress", "Not Started", "Dropped"]

SURVEY_TYPES = ["Q1 Pulse", "Q2 Pulse", "Q3 Pulse", "Annual Engagement"]

RECRUITING_SOURCES = [
    "LinkedIn",
    "Referral",
    "Job Board",
    "Career Page",
    "University",
    "Recruiter Agency",
]
RECRUITING_STATUSES = [
    "Applied",
    "Screened",
    "Interviewed",
    "Offered",
    "Hired",
    "Rejected",
    "Withdrawn",
]


# ---------------------------------------------------------------------------
# Generator Class
# ---------------------------------------------------------------------------


class PeopleAnalyticsDataGenerator:
    """Generates correlated synthetic HR data for a People Analytics DWH."""

    def __init__(
        self,
        n_employees: int = 2000,
        start_date: str = "2019-01-01",
        end_date: str = "2024-12-31",
        random_state: int = 42,
    ):
        self.n_employees = n_employees
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date)
        self.rng = np.random.default_rng(random_state)
        self._faker = Faker("en_US")
        self._faker.seed_instance(random_state)

        self.employees: pd.DataFrame = pd.DataFrame()
        self.absences: pd.DataFrame = pd.DataFrame()
        self.payroll: pd.DataFrame = pd.DataFrame()
        self.promotions: pd.DataFrame = pd.DataFrame()
        self.training: pd.DataFrame = pd.DataFrame()
        self.surveys: pd.DataFrame = pd.DataFrame()
        self.recruiting: pd.DataFrame = pd.DataFrame()

    def generate_all(self) -> dict[str, pd.DataFrame]:
        """Generate all 7 tables in dependency order."""
        logger.info("Generating {} employees from {} to {}", self.n_employees, self.start_date.date(), self.end_date.date())

        self._generate_employees()
        self._generate_absences()
        self._generate_payroll()
        self._generate_promotions()
        self._generate_training()
        self._generate_surveys()
        self._generate_recruiting()

        tables = {
            "raw_employees": self.employees,
            "raw_absences": self.absences,
            "raw_payroll": self.payroll,
            "raw_promotions": self.promotions,
            "raw_training": self.training,
            "raw_surveys": self.surveys,
            "raw_recruiting": self.recruiting,
        }

        for name, df in tables.items():
            logger.info("  {} → {} rows, {} columns", name, len(df), len(df.columns))

        return tables

    # ------------------------------------------------------------------
    # Employees
    # ------------------------------------------------------------------

    def _generate_employees(self) -> None:
        dept_names = list(DEPARTMENTS.keys())
        dept_weights = [float(DEPARTMENTS[d]["weight"]) for d in dept_names]
        level_ids = list(JOB_LEVELS.keys())
        level_weights = [float(JOB_LEVELS[lv]["weight"]) for lv in level_ids]  # type: ignore[arg-type]

        records = []
        for emp_id in range(1, self.n_employees + 1):
            dept = self.rng.choice(dept_names, p=dept_weights)
            level = int(self.rng.choice(level_ids, p=level_weights))
            gender = self.rng.choice(GENDERS, p=GENDER_WEIGHTS)
            location = self.rng.choice(LOCATIONS, p=LOCATION_WEIGHTS)

            birth_date = self._faker.date_of_birth(minimum_age=22, maximum_age=62)
            hire_date = self.start_date + pd.Timedelta(
                days=int(self.rng.integers(0, (self.end_date - self.start_date).days * 0.8))
            )

            dept_turnover_mult = float(DEPARTMENTS[dept]["turnover_mult"])
            base_turnover_prob = 0.18 * dept_turnover_mult
            level_adj = max(0, (4 - level) * 0.03)
            turnover_prob = min(0.40, base_turnover_prob + level_adj)

            terminated = self.rng.random() < turnover_prob
            termination_date = None
            termination_reason = None
            is_active = True

            if terminated:
                min_tenure_days = 90
                max_tenure_days = (self.end_date - hire_date).days
                if max_tenure_days > min_tenure_days:
                    tenure_days = int(self.rng.integers(min_tenure_days, max_tenure_days))
                    termination_date = hire_date + pd.Timedelta(days=tenure_days)
                    termination_reason = self.rng.choice(
                        TERMINATION_REASONS, p=TERM_REASON_WEIGHTS
                    )
                    is_active = False

            salary_range = JOB_LEVELS[level]["salary_range"]
            salary_min, salary_max = int(salary_range[0]), int(salary_range[1])  # type: ignore[index]
            dept_mult = float(DEPARTMENTS[dept]["salary_mult"])
            base_salary = round(
                float(self.rng.uniform(salary_min, salary_max)) * dept_mult, 2
            )

            employment_type = self.rng.choice(
                ["Full-Time", "Part-Time", "Contract"], p=[0.85, 0.08, 0.07]
            )

            manager_id = None
            if level > 1:
                manager_id = int(self.rng.integers(1, max(2, emp_id)))
                if manager_id == emp_id:
                    manager_id = max(1, emp_id - 1)

            title = f"{dept} {JOB_LEVELS[level]['title_suffix']}"

            records.append(
                {
                    "employee_id": emp_id,
                    "first_name": self._faker.first_name(),
                    "last_name": self._faker.last_name(),
                    "email": f"emp{emp_id}@company.com",
                    "gender": gender,
                    "birth_date": str(birth_date),
                    "hire_date": str(hire_date.date()),
                    "termination_date": str(termination_date.date()) if termination_date else None,
                    "termination_reason": termination_reason,
                    "department": dept,
                    "job_title": title,
                    "job_level": level,
                    "manager_id": manager_id,
                    "location": location,
                    "employment_type": employment_type,
                    "base_annual_salary": base_salary,
                    "is_active": is_active,
                }
            )

        self.employees = pd.DataFrame(records)
        logger.info("Generated {} employee records", len(self.employees))

    # ------------------------------------------------------------------
    # Absences
    # ------------------------------------------------------------------

    def _generate_absences(self) -> None:
        records = []
        absence_id = 1

        for _, emp in self.employees.iterrows():
            hire = pd.Timestamp(emp["hire_date"])
            end = (
                pd.Timestamp(emp["termination_date"])
                if emp["termination_date"]
                else self.end_date
            )
            tenure_days = (end - hire).days
            if tenure_days < 30:
                continue

            avg_absences_per_year = self.rng.poisson(8)
            n_absences = max(0, int(avg_absences_per_year * tenure_days / 365))

            for _ in range(n_absences):
                absence_date = hire + pd.Timedelta(
                    days=int(self.rng.integers(1, max(2, tenure_days)))
                )
                absence_type = self.rng.choice(ABSENCE_TYPES, p=ABSENCE_WEIGHTS)

                if absence_type == "Vacation":
                    hours = float(self.rng.choice([4, 8], p=[0.2, 0.8]))
                elif absence_type == "Parental":
                    hours = 8.0
                else:
                    hours = float(self.rng.choice([2, 4, 6, 8], p=[0.1, 0.25, 0.25, 0.4]))

                is_approved = self.rng.choice(
                    [True, False], p=[0.92, 0.08]
                )

                records.append(
                    {
                        "absence_id": absence_id,
                        "employee_id": emp["employee_id"],
                        "absence_date": str(absence_date.date()),
                        "absence_type": absence_type,
                        "hours_absent": hours,
                        "is_approved": is_approved,
                    }
                )
                absence_id += 1

        self.absences = pd.DataFrame(records)
        logger.info("Generated {} absence records", len(self.absences))

    # ------------------------------------------------------------------
    # Payroll
    # ------------------------------------------------------------------

    def _generate_payroll(self) -> None:
        records = []
        payroll_id = 1

        for _, emp in self.employees.iterrows():
            hire = pd.Timestamp(emp["hire_date"])
            end = (
                pd.Timestamp(emp["termination_date"])
                if emp["termination_date"]
                else self.end_date
            )
            base_monthly = emp["base_annual_salary"] / 12

            months = pd.date_range(
                start=hire.replace(day=1),
                end=end,
                freq="MS",
            )

            for month_start in months:
                month_end = month_start + pd.offsets.MonthEnd(0)

                annual_raise = 1 + 0.03 * ((month_start - hire).days / 365)
                monthly_base = round(base_monthly * annual_raise, 2)

                overtime = round(
                    float(self.rng.exponential(150)) if self.rng.random() < 0.3 else 0, 2
                )

                bonus = 0.0
                if month_start.month == 12:
                    bonus = round(monthly_base * float(self.rng.uniform(0, 0.15)), 2)

                deductions = round(monthly_base * 0.22, 2)
                net_pay = round(monthly_base + overtime + bonus - deductions, 2)

                records.append(
                    {
                        "payroll_id": payroll_id,
                        "employee_id": emp["employee_id"],
                        "pay_period_start": str(month_start.date()),
                        "pay_period_end": str(month_end.date()),
                        "base_salary": monthly_base,
                        "overtime_pay": overtime,
                        "bonus": bonus,
                        "deductions": deductions,
                        "net_pay": net_pay,
                        "currency": "USD",
                    }
                )
                payroll_id += 1

        self.payroll = pd.DataFrame(records)
        logger.info("Generated {} payroll records", len(self.payroll))

    # ------------------------------------------------------------------
    # Promotions
    # ------------------------------------------------------------------

    def _generate_promotions(self) -> None:
        records = []
        promotion_id = 1

        for _, emp in self.employees.iterrows():
            hire = pd.Timestamp(emp["hire_date"])
            end = (
                pd.Timestamp(emp["termination_date"])
                if emp["termination_date"]
                else self.end_date
            )
            tenure_years = (end - hire).days / 365

            promo_prob_per_year = 0.12
            n_promos = self.rng.binomial(
                max(0, int(tenure_years)), promo_prob_per_year
            )
            current_level = emp["job_level"]
            current_dept = emp["department"]
            current_title = emp["job_title"]

            for i in range(n_promos):
                if current_level >= 6:
                    break

                min_days = max(365, int(365 * (i + 1) * 0.8))
                if min_days >= (end - hire).days:
                    break

                promo_date = hire + pd.Timedelta(
                    days=int(self.rng.integers(min_days, max(min_days + 1, (end - hire).days)))
                )

                new_level = min(6, current_level + 1)
                lateral_move = self.rng.random() < 0.15
                new_dept = current_dept
                if lateral_move:
                    dept_names = list(DEPARTMENTS.keys())
                    dept_names.remove(current_dept)
                    new_dept = self.rng.choice(dept_names)

                new_title = f"{new_dept} {JOB_LEVELS[new_level]['title_suffix']}"
                salary_change = round(float(self.rng.uniform(5, 20)), 1)

                records.append(
                    {
                        "promotion_id": promotion_id,
                        "employee_id": emp["employee_id"],
                        "promotion_date": str(promo_date.date()),
                        "previous_job_title": current_title,
                        "new_job_title": new_title,
                        "previous_job_level": current_level,
                        "new_job_level": new_level,
                        "previous_department": current_dept,
                        "new_department": new_dept,
                        "salary_change_pct": salary_change,
                    }
                )

                current_level = new_level
                current_dept = new_dept
                current_title = new_title
                promotion_id += 1

        self.promotions = pd.DataFrame(records)
        logger.info("Generated {} promotion records", len(self.promotions))

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def _generate_training(self) -> None:
        records = []
        training_id = 1

        course_pool = [
            ("Python for Data Analysis", "Technical Skills", True),
            ("SQL Fundamentals", "Technical Skills", True),
            ("Cloud Architecture", "Technical Skills", False),
            ("Leadership Essentials", "Leadership", False),
            ("Managing Remote Teams", "Leadership", False),
            ("Annual Compliance", "Compliance", True),
            ("Data Privacy (LGPD/GDPR)", "Compliance", True),
            ("Anti-Harassment", "Compliance", True),
            ("Effective Communication", "Soft Skills", False),
            ("Presentation Skills", "Soft Skills", False),
            ("Product Onboarding", "Product Knowledge", True),
            ("Workplace Safety", "Safety", True),
            ("Unconscious Bias", "DEI", False),
            ("Inclusive Leadership", "DEI", False),
            ("Agile Methodology", "Technical Skills", False),
            ("Project Management", "Soft Skills", False),
        ]

        for _, emp in self.employees.iterrows():
            hire = pd.Timestamp(emp["hire_date"])
            end = (
                pd.Timestamp(emp["termination_date"])
                if emp["termination_date"]
                else self.end_date
            )
            tenure_days = (end - hire).days
            if tenure_days < 30:
                continue

            n_trainings = self.rng.poisson(3) + 1
            selected = self.rng.choice(
                len(course_pool), size=min(n_trainings, len(course_pool)), replace=False
            )

            for idx in selected:
                course_name, category, is_mandatory = course_pool[idx]

                start = hire + pd.Timedelta(
                    days=int(self.rng.integers(7, max(8, tenure_days)))
                )
                hours = round(float(self.rng.uniform(2, 40)), 1)
                duration_days = max(1, int(hours / 2))

                status_probs = [0.65, 0.15, 0.10, 0.10]
                status = self.rng.choice(TRAINING_STATUSES, p=status_probs)

                completion_date = None
                score = None
                if status == "Completed":
                    completion_date = start + pd.Timedelta(days=duration_days)
                    score = round(float(self.rng.uniform(60, 100)), 1)
                elif status == "Dropped":
                    completion_date = start + pd.Timedelta(
                        days=max(1, int(duration_days * 0.3))
                    )

                records.append(
                    {
                        "training_id": training_id,
                        "employee_id": emp["employee_id"],
                        "course_name": course_name,
                        "course_category": category,
                        "start_date": str(start.date()),
                        "completion_date": (
                            str(completion_date.date()) if completion_date else None
                        ),
                        "status": status,
                        "hours": hours,
                        "score": score,
                        "is_mandatory": is_mandatory,
                    }
                )
                training_id += 1

        self.training = pd.DataFrame(records)
        logger.info("Generated {} training records", len(self.training))

    # ------------------------------------------------------------------
    # Surveys
    # ------------------------------------------------------------------

    def _generate_surveys(self) -> None:
        records = []
        survey_id = 1

        survey_dates = pd.date_range(
            start=self.start_date, end=self.end_date, freq="QS"
        )

        for survey_date in survey_dates:
            survey_type = SURVEY_TYPES[survey_date.quarter - 1]

            active_mask = (
                (self.employees["hire_date"] <= str(survey_date.date()))
                & (
                    self.employees["termination_date"].isna()
                    | (self.employees["termination_date"] > str(survey_date.date()))
                )
            )
            active_emps = self.employees[active_mask]

            response_rate = self.rng.uniform(0.70, 0.90)
            respondents = active_emps.sample(
                frac=response_rate, random_state=int(self.rng.integers(0, 10000))
            )

            for _, emp in respondents.iterrows():
                base_engagement = self.rng.normal(3.8, 0.6)
                base_engagement = np.clip(base_engagement, 1, 5)

                records.append(
                    {
                        "survey_id": survey_id,
                        "employee_id": emp["employee_id"],
                        "survey_date": str(survey_date.date()),
                        "survey_type": survey_type,
                        "engagement_score": round(
                            float(np.clip(base_engagement + self.rng.normal(0, 0.3), 1, 5)), 2
                        ),
                        "satisfaction_score": round(
                            float(np.clip(base_engagement + self.rng.normal(0, 0.4), 1, 5)), 2
                        ),
                        "manager_score": round(
                            float(np.clip(self.rng.normal(3.6, 0.7), 1, 5)), 2
                        ),
                        "growth_score": round(
                            float(np.clip(self.rng.normal(3.3, 0.8), 1, 5)), 2
                        ),
                        "wellbeing_score": round(
                            float(np.clip(self.rng.normal(3.5, 0.6), 1, 5)), 2
                        ),
                        "overall_score": round(
                            float(
                                np.clip(base_engagement + self.rng.normal(0, 0.2), 1, 5)
                            ),
                            2,
                        ),
                    }
                )
                survey_id += 1

        self.surveys = pd.DataFrame(records)
        logger.info("Generated {} survey records", len(self.surveys))

    # ------------------------------------------------------------------
    # Recruiting
    # ------------------------------------------------------------------

    def _generate_recruiting(self) -> None:
        records = []
        app_id = 1
        req_id = 1

        months = pd.date_range(start=self.start_date, end=self.end_date, freq="MS")

        for month in months:
            n_reqs = self.rng.poisson(5)

            for _ in range(n_reqs):
                dept = self.rng.choice(
                    list(DEPARTMENTS.keys()),
                    p=[float(DEPARTMENTS[d]["weight"]) for d in DEPARTMENTS],
                )
                level = int(
                    self.rng.choice(
                        list(JOB_LEVELS.keys()),
                        p=[float(JOB_LEVELS[lv]["weight"]) for lv in JOB_LEVELS],  # type: ignore[arg-type]
                    )
                )
                title = f"{dept} {JOB_LEVELS[level]['title_suffix']}"
                recruiter = self._faker.name()

                n_applicants = self.rng.poisson(12) + 3

                for _ in range(n_applicants):
                    source = self.rng.choice(RECRUITING_SOURCES)
                    app_date = month + pd.Timedelta(
                        days=int(self.rng.integers(0, 28))
                    )
                    candidate = self._faker.name()

                    screening_date = None
                    interview_date = None
                    offer_date = None
                    hire_date = None
                    rejection_date = None
                    status = "Applied"

                    if self.rng.random() < 0.60:
                        screening_date = app_date + pd.Timedelta(
                            days=int(self.rng.integers(2, 10))
                        )
                        status = "Screened"

                        if self.rng.random() < 0.50:
                            interview_date = screening_date + pd.Timedelta(
                                days=int(self.rng.integers(3, 14))
                            )
                            status = "Interviewed"

                            if self.rng.random() < 0.30:
                                offer_date = interview_date + pd.Timedelta(
                                    days=int(self.rng.integers(2, 7))
                                )
                                status = "Offered"

                                if self.rng.random() < 0.75:
                                    hire_date = offer_date + pd.Timedelta(
                                        days=int(self.rng.integers(5, 30))
                                    )
                                    status = "Hired"
                                else:
                                    status = "Withdrawn"
                            else:
                                rejection_date = interview_date + pd.Timedelta(
                                    days=int(self.rng.integers(1, 5))
                                )
                                status = "Rejected"
                        else:
                            rejection_date = screening_date + pd.Timedelta(
                                days=int(self.rng.integers(1, 5))
                            )
                            status = "Rejected"
                    else:
                        if self.rng.random() < 0.5:
                            rejection_date = app_date + pd.Timedelta(
                                days=int(self.rng.integers(3, 14))
                            )
                            status = "Rejected"

                    records.append(
                        {
                            "application_id": app_id,
                            "requisition_id": f"REQ-{req_id:05d}",
                            "department": dept,
                            "job_title": title,
                            "job_level": level,
                            "candidate_name": candidate,
                            "source": source,
                            "application_date": str(app_date.date()),
                            "screening_date": (
                                str(screening_date.date()) if screening_date else None
                            ),
                            "interview_date": (
                                str(interview_date.date()) if interview_date else None
                            ),
                            "offer_date": (
                                str(offer_date.date()) if offer_date else None
                            ),
                            "hire_date": (
                                str(hire_date.date()) if hire_date else None
                            ),
                            "rejection_date": (
                                str(rejection_date.date()) if rejection_date else None
                            ),
                            "status": status,
                            "recruiter": recruiter,
                        }
                    )
                    app_id += 1

                req_id += 1

        self.recruiting = pd.DataFrame(records)
        logger.info("Generated {} recruiting records", len(self.recruiting))

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def save_all(self, output_dir: Path, dbt_seeds_dir: Path | None = None) -> None:
        """Save all tables as CSV to output_dir and optionally copy to dbt seeds."""
        output_dir.mkdir(parents=True, exist_ok=True)

        tables = self.generate_all()

        for name, df in tables.items():
            path = output_dir / f"{name}.csv"
            df.to_csv(path, index=False)
            logger.info("Saved {} → {}", name, path)

            if dbt_seeds_dir:
                dbt_seeds_dir.mkdir(parents=True, exist_ok=True)
                dbt_path = dbt_seeds_dir / f"{name}.csv"
                df.to_csv(dbt_path, index=False)
                logger.info("Copied seed → {}", dbt_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic People Analytics data")
    parser.add_argument("--output-dir", type=str, default="data/raw")
    parser.add_argument("--dbt-seeds-dir", type=str, default="dbt_project/seeds")
    parser.add_argument("--n-employees", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    settings = get_settings()
    ds = settings.data_settings

    generator = PeopleAnalyticsDataGenerator(
        n_employees=args.n_employees or ds.num_employees,
        start_date=ds.date_range_start,
        end_date=ds.date_range_end,
        random_state=args.seed or ds.seed_random_state,
    )

    generator.save_all(
        output_dir=Path(args.output_dir),
        dbt_seeds_dir=Path(args.dbt_seeds_dir),
    )
    logger.info("Data generation complete.")


if __name__ == "__main__":
    main()
