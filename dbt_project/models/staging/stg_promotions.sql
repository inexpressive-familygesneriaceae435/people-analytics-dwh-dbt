with source as (
    select * from {{ source('raw', 'raw_promotions') }}
),

cleaned as (
    select
        promotion_id,
        employee_id,
        cast(promotion_date as date) as promotion_date,
        previous_job_title,
        new_job_title,
        previous_job_level,
        new_job_level,
        previous_department,
        new_department,
        salary_change_pct,

        -- derived
        new_job_level - previous_job_level as level_change,
        case
            when previous_department != new_department then true
            else false
        end as is_lateral_move,
        year(cast(promotion_date as date)) as promotion_year,
        quarter(cast(promotion_date as date)) as promotion_quarter

    from source
)

select * from cleaned
