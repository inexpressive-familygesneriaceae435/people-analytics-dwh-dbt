with source as (
    select * from {{ source('raw', 'raw_recruiting') }}
),

cleaned as (
    select
        application_id,
        requisition_id,
        department,
        job_title,
        job_level,
        candidate_name,
        source,
        cast(application_date as date) as application_date,
        cast(screening_date as date) as screening_date,
        cast(interview_date as date) as interview_date,
        cast(offer_date as date) as offer_date,
        cast(hire_date as date) as hire_date,
        cast(rejection_date as date) as rejection_date,
        status,
        recruiter,

        -- stage durations (days)
        case
            when screening_date is not null
            then datediff('day', cast(application_date as date), cast(screening_date as date))
        end as days_to_screen,

        case
            when interview_date is not null and screening_date is not null
            then datediff('day', cast(screening_date as date), cast(interview_date as date))
        end as days_to_interview,

        case
            when offer_date is not null and interview_date is not null
            then datediff('day', cast(interview_date as date), cast(offer_date as date))
        end as days_to_offer,

        case
            when hire_date is not null
            then datediff('day', cast(application_date as date), cast(hire_date as date))
        end as days_to_hire,

        -- year/quarter for aggregation
        year(cast(application_date as date)) as application_year,
        quarter(cast(application_date as date)) as application_quarter

    from source
)

select * from cleaned
