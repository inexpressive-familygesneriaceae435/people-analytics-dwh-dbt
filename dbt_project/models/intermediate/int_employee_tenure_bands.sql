with employees as (
    select * from {{ ref('stg_employees') }}
),

banded as (
    select
        *,

        case
            when tenure_years < 1 then '<1yr'
            when tenure_years < 3 then '1-3yr'
            when tenure_years < 5 then '3-5yr'
            when tenure_years < 10 then '5-10yr'
            else '10+yr'
        end as tenure_band,

        case
            when age < 30 then '<30'
            when age < 40 then '30-39'
            when age < 50 then '40-49'
            else '50+'
        end as age_band,

        ntile(4) over (order by base_annual_salary) as salary_quartile,

        case
            when ntile(4) over (order by base_annual_salary) = 1 then 'Q1 (Bottom 25%)'
            when ntile(4) over (order by base_annual_salary) = 2 then 'Q2'
            when ntile(4) over (order by base_annual_salary) = 3 then 'Q3'
            when ntile(4) over (order by base_annual_salary) = 4 then 'Q4 (Top 25%)'
        end as salary_band

    from employees
)

select * from banded
