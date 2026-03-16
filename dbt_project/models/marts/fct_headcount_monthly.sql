with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="month",
        start_date="cast('2019-01-01' as date)",
        end_date="cast('2025-01-01' as date)"
    ) }}
),

months as (
    select cast(date_month as date) as report_month from date_spine
),

employees as (
    select * from {{ ref('stg_employees') }}
),

departments as (
    select distinct department from employees
),

month_dept as (
    select
        m.report_month,
        d.department
    from months m
    cross join departments d
),

headcount as (
    select
        md.report_month,
        md.department,

        -- active headcount at end of month
        count(case
            when e.hire_date <= md.report_month + interval '1 month' - interval '1 day'
            and (e.termination_date is null or e.termination_date > md.report_month + interval '1 month' - interval '1 day')
            then 1
        end) as active_headcount,

        -- new hires in this month
        count(case
            when e.hire_date >= md.report_month
            and e.hire_date < md.report_month + interval '1 month'
            then 1
        end) as new_hires,

        -- terminations in this month
        count(case
            when e.termination_date >= md.report_month
            and e.termination_date < md.report_month + interval '1 month'
            then 1
        end) as terminations,

        -- voluntary terminations
        count(case
            when e.termination_date >= md.report_month
            and e.termination_date < md.report_month + interval '1 month'
            and e.termination_reason like 'Voluntary%'
            then 1
        end) as voluntary_terminations,

        -- involuntary terminations
        count(case
            when e.termination_date >= md.report_month
            and e.termination_date < md.report_month + interval '1 month'
            and e.termination_reason like 'Involuntary%'
            then 1
        end) as involuntary_terminations

    from month_dept md
    left join employees e on e.department = md.department
    group by md.report_month, md.department
)

select
    *,
    year(report_month) as report_year,
    month(report_month) as report_month_num,
    quarter(report_month) as report_quarter
from headcount
