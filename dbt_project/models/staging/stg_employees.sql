with source as (
    select * from {{ source('raw', 'raw_employees') }}
),

cleaned as (
    select
        employee_id,
        first_name,
        last_name,
        first_name || ' ' || last_name as full_name,
        email,
        gender,
        cast(birth_date as date) as birth_date,
        cast(hire_date as date) as hire_date,
        cast(termination_date as date) as termination_date,
        termination_reason,
        department,
        job_title,
        job_level,
        manager_id,
        location,
        employment_type,
        base_annual_salary,
        is_active,

        -- derived fields
        round(
            datediff('day', cast(hire_date as date), coalesce(cast(termination_date as date), current_date)) / 365.25,
            2
        ) as tenure_years,

        datediff('year', cast(birth_date as date), current_date) as age,

        case
            when termination_reason is not null
                and termination_reason like 'Voluntary%'
            then true
            else false
        end as is_voluntary_termination,

        case
            when termination_reason is not null
                and termination_reason like 'Involuntary%'
            then true
            else false
        end as is_involuntary_termination

    from source
)

select * from cleaned
