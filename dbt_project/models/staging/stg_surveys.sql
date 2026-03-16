with source as (
    select * from {{ source('raw', 'raw_surveys') }}
),

cleaned as (
    select
        survey_id,
        employee_id,
        cast(survey_date as date) as survey_date,
        survey_type,
        engagement_score,
        satisfaction_score,
        manager_score,
        growth_score,
        wellbeing_score,
        overall_score,

        -- derived
        year(cast(survey_date as date)) as survey_year,
        quarter(cast(survey_date as date)) as survey_quarter,
        (engagement_score + satisfaction_score + manager_score + growth_score + wellbeing_score) / 5.0 as avg_dimension_score

    from source
)

select * from cleaned
