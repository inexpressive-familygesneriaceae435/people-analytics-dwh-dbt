# Data Dictionary — People Analytics DWH

## Overview

Synthetic dataset simulating a **~2,000-employee organization** across 6 years (2019–2024). Seven source tables model the full employee lifecycle: hiring, compensation, absences, career progression, training, engagement, and recruiting.

Distributions are calibrated against published People Analytics benchmarks (SHRM 2023 Human Capital Benchmarking Report, BLS JOLTS, Gallup Q12 meta-analysis).

---

## Raw Tables

### raw_employees

Master employee records. One row per employee.

| Column | Type | Range/Values | Description |
|--------|------|-------------|-------------|
| employee_id | int | 1–2000 | Unique identifier (PK) |
| first_name | string | — | Generated first name |
| last_name | string | — | Generated last name |
| email | string | emp{id}@company.com | Corporate email |
| gender | string | Male/Female/Non-Binary (48/48/4%) | Self-reported gender |
| birth_date | date | — | Date of birth (age 22–62) |
| hire_date | date | 2019-01-01 to ~2024-10-01 | Employment start date |
| termination_date | date | nullable | Employment end date |
| termination_reason | string | nullable | 9 categories (Voluntary/Involuntary/Retirement) |
| department | string | 8 departments | Organizational unit |
| job_title | string | {Dept} {Level Suffix} | Current role title |
| job_level | int | 1–6 | 1=Associate → 6=Director |
| manager_id | int | nullable | References employee_id |
| location | string | 5 locations | Office/Remote location |
| employment_type | string | Full-Time/Part-Time/Contract (85/8/7%) | Employment category |
| base_annual_salary | float | 34,000–286,000 | Annual gross salary (USD) |
| is_active | bool | true/false | Currently employed |

### raw_absences

Daily absence events. Multiple rows per employee.

| Column | Type | Range/Values | Description |
|--------|------|-------------|-------------|
| absence_id | int | sequential | Unique identifier (PK) |
| employee_id | int | FK → raw_employees | Employee reference |
| absence_date | date | within employment period | Date of absence |
| absence_type | string | 6 types | Sick Leave, Vacation, Personal, Parental, Bereavement, Jury Duty |
| hours_absent | float | 2–8 | Hours absent on this date |
| is_approved | bool | 92% true | Manager approval status |

### raw_payroll

Monthly compensation records. One row per employee per month.

| Column | Type | Range/Values | Description |
|--------|------|-------------|-------------|
| payroll_id | int | sequential | Unique identifier (PK) |
| employee_id | int | FK → raw_employees | Employee reference |
| pay_period_start | date | 1st of month | Period start |
| pay_period_end | date | last of month | Period end |
| base_salary | float | > 0 | Monthly base (includes 3% annual raise) |
| overtime_pay | float | ≥ 0 | Overtime compensation (30% probability) |
| bonus | float | ≥ 0 | Year-end bonus (December only, 0–15% of base) |
| deductions | float | ~22% of base | Taxes + benefits |
| net_pay | float | base + overtime + bonus − deductions | Take-home pay |
| currency | string | USD | Payment currency |

### raw_promotions

Career progression events. Zero or more per employee.

| Column | Type | Range/Values | Description |
|--------|------|-------------|-------------|
| promotion_id | int | sequential | Unique identifier (PK) |
| employee_id | int | FK → raw_employees | Employee reference |
| promotion_date | date | after hire + ≥1 year | Date of promotion |
| previous_job_title | string | — | Title before promotion |
| new_job_title | string | — | Title after promotion |
| previous_job_level | int | 1–5 | Level before |
| new_job_level | int | 2–6 | Level after (always ≥ previous) |
| previous_department | string | — | Department before (may differ for lateral moves) |
| new_department | string | — | Department after |
| salary_change_pct | float | 5–20% | Salary increase percentage |

### raw_training

Course enrollment and completion. Multiple per employee.

| Column | Type | Range/Values | Description |
|--------|------|-------------|-------------|
| training_id | int | sequential | Unique identifier (PK) |
| employee_id | int | FK → raw_employees | Employee reference |
| course_name | string | 16 courses | Course title |
| course_category | string | 7 categories | Technical Skills, Leadership, Compliance, etc. |
| start_date | date | after hire | Enrollment date |
| completion_date | date | nullable | Completion/drop date |
| status | string | 4 statuses | Completed (65%), In Progress (15%), Not Started (10%), Dropped (10%) |
| hours | float | 2–40 | Course duration |
| score | float | 60–100, nullable | Assessment score (only for Completed) |
| is_mandatory | bool | varies by course | Compliance requirement flag |

### raw_surveys

Quarterly engagement survey responses.

| Column | Type | Range/Values | Description |
|--------|------|-------------|-------------|
| survey_id | int | sequential | Unique identifier (PK) |
| employee_id | int | FK → raw_employees | Respondent reference |
| survey_date | date | quarterly (QS) | Survey administration date |
| survey_type | string | Q1-Q3 Pulse, Annual Engagement | Survey cadence |
| engagement_score | float | 1.0–5.0 | Employee engagement |
| satisfaction_score | float | 1.0–5.0 | Job satisfaction |
| manager_score | float | 1.0–5.0 | Manager effectiveness |
| growth_score | float | 1.0–5.0 | Career growth perception |
| wellbeing_score | float | 1.0–5.0 | Wellbeing/work-life balance |
| overall_score | float | 1.0–5.0 | Overall experience |

### raw_recruiting

Full hiring pipeline records.

| Column | Type | Range/Values | Description |
|--------|------|-------------|-------------|
| application_id | int | sequential | Unique identifier (PK) |
| requisition_id | string | REQ-XXXXX | Job requisition reference |
| department | string | 8 departments | Hiring department |
| job_title | string | — | Position title |
| job_level | int | 1–6 | Position level |
| candidate_name | string | — | Candidate name |
| source | string | 6 sources | LinkedIn, Referral, Job Board, Career Page, University, Recruiter Agency |
| application_date | date | monthly | Application submission date |
| screening_date | date | nullable | Phone screen date |
| interview_date | date | nullable | Interview date |
| offer_date | date | nullable | Offer extension date |
| hire_date | date | nullable | Hire date (only for status=Hired) |
| rejection_date | date | nullable | Rejection date |
| status | string | 7 statuses | Applied → Screened → Interviewed → Offered → Hired/Rejected/Withdrawn |
| recruiter | string | — | Assigned recruiter name |

---

## Departments

| Department | Headcount Weight | Salary Multiplier | Turnover Multiplier |
|-----------|:---:|:---:|:---:|
| Engineering | 20% | 1.30x | 0.85x |
| Sales | 18% | 1.10x | 1.20x |
| Operations | 15% | 0.90x | 1.00x |
| Customer Support | 12% | 0.85x | 1.30x |
| Marketing | 10% | 1.00x | 0.95x |
| Finance | 10% | 1.15x | 0.80x |
| HR | 8% | 0.95x | 0.75x |
| Product | 7% | 1.25x | 0.90x |

---

## Data Quality Notes

- **All data is synthetic** — no real personal information
- Employee IDs are sequential (1–N)
- Termination dates are always after hire dates (90+ day minimum tenure)
- Payroll records span from hire month to termination/current month
- Survey response rate varies 70–90% per quarter
- Recruiting funnel follows realistic conversion: ~60% screened, ~50% of screened interviewed, ~30% of interviewed offered, ~75% offer acceptance
