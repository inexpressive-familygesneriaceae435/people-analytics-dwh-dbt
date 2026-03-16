with employees as (
    select * from {{ ref('int_employee_tenure_bands') }}
),

training as (
    select * from {{ ref('int_training_completion') }}
),

latest_survey as (
    select
        employee_id,
        engagement_score as latest_engagement_score,
        satisfaction_score as latest_satisfaction_score,
        manager_score as latest_manager_score,
        overall_score as latest_overall_score,
        survey_date as latest_survey_date,
        row_number() over (partition by employee_id order by survey_date desc) as rn
    from {{ ref('stg_surveys') }}
),

combined as (
    select
        e.employee_id,
        e.full_name,
        e.email,
        e.gender,
        e.birth_date,
        e.age,
        e.age_band,
        e.hire_date,
        e.termination_date,
        e.termination_reason,
        e.is_voluntary_termination,
        e.is_involuntary_termination,
        e.tenure_years,
        e.tenure_band,
        e.department,
        e.job_title,
        e.job_level,
        e.manager_id,
        e.location,
        e.employment_type,
        e.base_annual_salary,
        e.salary_band,
        e.salary_quartile,
        e.is_active,

        -- training
        coalesce(t.total_courses_enrolled, 0) as total_courses_enrolled,
        coalesce(t.courses_completed, 0) as courses_completed,
        coalesce(t.total_training_hours, 0) as total_training_hours,
        t.completion_rate,
        t.mandatory_completion_rate,
        t.avg_completion_score,

        -- latest survey
        s.latest_engagement_score,
        s.latest_satisfaction_score,
        s.latest_manager_score,
        s.latest_overall_score,
        s.latest_survey_date

    from employees e
    left join training t on e.employee_id = t.employee_id
    left join latest_survey s on e.employee_id = s.employee_id and s.rn = 1
)

select * from combined
