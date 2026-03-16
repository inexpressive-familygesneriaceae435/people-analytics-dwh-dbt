with source as (
    select * from {{ source('raw', 'raw_absences') }}
),

cleaned as (
    select
        absence_id,
        employee_id,
        cast(absence_date as date) as absence_date,
        absence_type,
        hours_absent,
        is_approved,

        -- date parts for aggregation
        year(cast(absence_date as date)) as absence_year,
        month(cast(absence_date as date)) as absence_month,
        quarter(cast(absence_date as date)) as absence_quarter,
        dayofweek(cast(absence_date as date)) as absence_day_of_week

    from source
)

select * from cleaned
