with training as (
    select * from {{ ref('stg_training') }}
),

employees as (
    select * from {{ ref('stg_employees') }}
),

headcount as (
    select
        department,
        sum(case when is_active then 1 else 0 end) as active_headcount
    from employees
    group by department
),

dept_training as (
    select
        e.department,
        t.training_year,
        t.course_category,

        count(distinct t.employee_id) as employees_trained,
        count(*) as total_enrollments,
        sum(case when t.is_completed then 1 else 0 end) as completions,
        sum(case when t.is_dropped then 1 else 0 end) as drops,
        sum(t.hours) as total_hours,
        avg(case when t.is_completed then t.score end) as avg_score,

        round(
            sum(case when t.is_completed then 1.0 else 0 end) / nullif(count(*), 0), 3
        ) as completion_rate,

        -- mandatory compliance
        sum(case when t.is_mandatory and t.is_completed then 1 else 0 end) as mandatory_completed,
        sum(case when t.is_mandatory then 1 else 0 end) as mandatory_total,
        round(
            sum(case when t.is_mandatory and t.is_completed then 1.0 else 0 end)
            / nullif(sum(case when t.is_mandatory then 1 else 0 end), 0), 3
        ) as mandatory_compliance_rate

    from training t
    inner join employees e on t.employee_id = e.employee_id
    group by e.department, t.training_year, t.course_category
),

with_coverage as (
    select
        dt.*,
        h.active_headcount,
        case
            when h.active_headcount > 0
            then round(dt.employees_trained * 100.0 / h.active_headcount, 1)
            else 0
        end as training_coverage_pct,

        case
            when dt.employees_trained > 0
            then round(dt.total_hours / dt.employees_trained, 1)
            else 0
        end as hours_per_employee

    from dept_training dt
    left join headcount h on dt.department = h.department
)

select * from with_coverage
