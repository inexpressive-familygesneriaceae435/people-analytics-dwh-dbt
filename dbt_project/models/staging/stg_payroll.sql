with source as (
    select * from {{ source('raw', 'raw_payroll') }}
),

cleaned as (
    select
        payroll_id,
        employee_id,
        cast(pay_period_start as date) as pay_period_start,
        cast(pay_period_end as date) as pay_period_end,
        base_salary,
        overtime_pay,
        bonus,
        deductions,
        net_pay,
        currency,

        -- derived
        base_salary + overtime_pay + bonus as total_compensation,
        year(cast(pay_period_start as date)) as pay_year,
        month(cast(pay_period_start as date)) as pay_month,
        quarter(cast(pay_period_start as date)) as pay_quarter

    from source
)

select * from cleaned
