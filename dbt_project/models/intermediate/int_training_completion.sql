with training as (
    select * from {{ ref('stg_training') }}
),

per_employee as (
    select
        employee_id,
        count(*) as total_courses_enrolled,
        sum(case when is_completed then 1 else 0 end) as courses_completed,
        sum(case when is_dropped then 1 else 0 end) as courses_dropped,
        sum(case when status = 'In Progress' then 1 else 0 end) as courses_in_progress,
        sum(hours) as total_training_hours,
        avg(case when is_completed then score end) as avg_completion_score,

        -- completion rate
        round(
            sum(case when is_completed then 1.0 else 0 end) / nullif(count(*), 0),
            3
        ) as completion_rate,

        -- mandatory compliance
        sum(case when is_mandatory then 1 else 0 end) as mandatory_courses,
        sum(case when is_mandatory and is_completed then 1 else 0 end) as mandatory_completed,
        round(
            sum(case when is_mandatory and is_completed then 1.0 else 0 end)
            / nullif(sum(case when is_mandatory then 1 else 0 end), 0),
            3
        ) as mandatory_completion_rate,

        -- category breadth
        count(distinct course_category) as distinct_categories,
        count(distinct training_year) as active_training_years

    from training
    group by employee_id
)

select * from per_employee
