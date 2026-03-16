with payroll as (
    select * from {{ ref('stg_payroll') }}
),

annual_comp as (
    select
        employee_id,
        pay_year,
        sum(base_salary) as annual_base_salary,
        sum(overtime_pay) as annual_overtime,
        sum(bonus) as annual_bonus,
        sum(total_compensation) as annual_total_compensation,
        sum(deductions) as annual_deductions,
        sum(net_pay) as annual_net_pay,
        count(*) as months_paid,
        avg(base_salary) as avg_monthly_base

    from payroll
    group by employee_id, pay_year
),

with_growth as (
    select
        *,
        lag(annual_total_compensation) over (
            partition by employee_id order by pay_year
        ) as prev_year_compensation,

        case
            when lag(annual_total_compensation) over (
                partition by employee_id order by pay_year
            ) > 0
            then round(
                (annual_total_compensation - lag(annual_total_compensation) over (
                    partition by employee_id order by pay_year
                )) / lag(annual_total_compensation) over (
                    partition by employee_id order by pay_year
                ) * 100, 2
            )
        end as yoy_compensation_growth_pct

    from annual_comp
)

select * from with_growth
