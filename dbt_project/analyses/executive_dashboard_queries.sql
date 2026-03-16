-- ============================================================
-- Executive Dashboard Queries
-- These queries demonstrate how mart tables power
-- a TOTVS RH People Analytics-style executive dashboard.
-- ============================================================

-- 1. Current headcount by department
select
    department,
    active_headcount,
    new_hires,
    terminations
from {{ ref('fct_headcount_monthly') }}
where report_month = (select max(report_month) from {{ ref('fct_headcount_monthly') }})
order by active_headcount desc;


-- 2. Trailing 12-month turnover rate by department
select
    department,
    round(avg(turnover_rate), 2) as avg_monthly_turnover_rate,
    round(avg(turnover_rate) * 12, 2) as annualized_turnover_rate
from {{ ref('fct_turnover_monthly') }}
where report_month >= (select max(report_month) - interval '12 months' from {{ ref('fct_turnover_monthly') }})
group by department
order by annualized_turnover_rate desc;


-- 3. Absenteeism trend (last 6 months, company-wide)
select
    report_month,
    sum(total_absence_hours) as company_absence_hours,
    round(avg(absence_rate), 2) as avg_absence_rate,
    round(avg(sick_leave_rate), 2) as avg_sick_rate
from {{ ref('fct_absenteeism_monthly') }}
where report_month >= (select max(report_month) - interval '6 months' from {{ ref('fct_absenteeism_monthly') }})
group by report_month
order by report_month;


-- 4. Promotion equity: rate by gender
select
    gender,
    sum(promotion_count) as total_promotions,
    round(avg(promotion_rate_pct), 2) as avg_promotion_rate
from {{ ref('fct_promotions_quarterly') }}
group by gender
order by avg_promotion_rate desc;


-- 5. Training compliance dashboard
select
    department,
    training_year,
    round(avg(completion_rate) * 100, 1) as avg_completion_pct,
    round(avg(mandatory_compliance_rate) * 100, 1) as mandatory_compliance_pct,
    round(avg(hours_per_employee), 1) as avg_hours_per_employee
from {{ ref('fct_training_adoption') }}
group by department, training_year
order by department, training_year;


-- 6. Recruiting efficiency by department (latest quarter)
select
    department,
    report_quarter,
    total_requisitions,
    total_hired,
    avg_days_to_hire,
    applicants_per_hire,
    top_source
from {{ ref('fct_recruiting_pipeline') }}
where report_quarter = (select max(report_quarter) from {{ ref('fct_recruiting_pipeline') }})
order by avg_days_to_hire;
