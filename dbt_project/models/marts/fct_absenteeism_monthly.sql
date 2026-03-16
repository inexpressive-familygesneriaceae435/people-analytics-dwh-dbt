with absences as (
    select * from {{ ref('int_absence_monthly') }}
),

employees as (
    select * from {{ ref('stg_employees') }}
),

headcount as (
    select * from {{ ref('fct_headcount_monthly') }}
),

dept_absences as (
    select
        a.absence_year,
        a.absence_month,
        e.department,
        sum(a.absence_hours) as total_absence_hours,
        sum(a.sick_hours) as total_sick_hours,
        sum(a.vacation_hours) as total_vacation_hours,
        sum(a.absence_count) as total_absence_events,
        avg(a.bradford_factor) as avg_bradford_factor,
        count(distinct a.employee_id) as employees_with_absences

    from absences a
    inner join employees e on a.employee_id = e.employee_id
    group by a.absence_year, a.absence_month, e.department
),

combined as (
    select
        make_date(da.absence_year, da.absence_month, 1) as report_month,
        da.department,
        da.total_absence_hours,
        da.total_sick_hours,
        da.total_vacation_hours,
        da.total_absence_events,
        da.avg_bradford_factor,
        da.employees_with_absences,
        h.active_headcount,

        -- absence rate = (total_absence_hours) / (headcount * standard_hours) * 100
        -- standard month = 176 hours (22 days * 8 hours)
        case
            when h.active_headcount > 0
            then round(da.total_absence_hours / (h.active_headcount * 176.0) * 100, 2)
            else 0
        end as absence_rate,

        -- sick leave rate
        case
            when h.active_headcount > 0
            then round(da.total_sick_hours / (h.active_headcount * 176.0) * 100, 2)
            else 0
        end as sick_leave_rate,

        -- pct of employees with at least one absence
        case
            when h.active_headcount > 0
            then round(da.employees_with_absences * 100.0 / h.active_headcount, 1)
            else 0
        end as pct_employees_absent

    from dept_absences da
    inner join headcount h
        on h.report_month = make_date(da.absence_year, da.absence_month, 1)
        and h.department = da.department
)

select * from combined
