with absences as (
    select * from {{ ref('stg_absences') }}
),

monthly_agg as (
    select
        employee_id,
        absence_year,
        absence_month,
        count(*) as absence_count,
        sum(hours_absent) as absence_hours,
        count(distinct absence_type) as distinct_absence_types,
        sum(case when absence_type = 'Sick Leave' then hours_absent else 0 end) as sick_hours,
        sum(case when absence_type = 'Vacation' then hours_absent else 0 end) as vacation_hours,
        sum(case when is_approved then hours_absent else 0 end) as approved_hours,
        sum(case when not is_approved then hours_absent else 0 end) as unapproved_hours,

        -- Bradford Factor: S^2 * D (S = number of spells, D = total days)
        -- Simplified: each absence event = 1 spell, days = hours / 8
        power(count(*), 2) * (sum(hours_absent) / 8.0) as bradford_factor

    from absences
    group by employee_id, absence_year, absence_month
)

select * from monthly_agg
