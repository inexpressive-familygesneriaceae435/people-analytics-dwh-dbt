with source as (
    select * from {{ source('raw', 'raw_training') }}
),

cleaned as (
    select
        training_id,
        employee_id,
        course_name,
        course_category,
        cast(start_date as date) as start_date,
        cast(completion_date as date) as completion_date,
        status,
        hours,
        score,
        is_mandatory,

        -- derived
        case when status = 'Completed' then true else false end as is_completed,
        case when status = 'Dropped' then true else false end as is_dropped,
        year(cast(start_date as date)) as training_year,
        quarter(cast(start_date as date)) as training_quarter,
        case
            when completion_date is not null and start_date is not null
            then datediff('day', cast(start_date as date), cast(completion_date as date))
            else null
        end as days_to_complete

    from source
)

select * from cleaned
