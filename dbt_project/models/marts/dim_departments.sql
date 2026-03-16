with employees as (
    select * from {{ ref('int_employee_tenure_bands') }}
),

dept_stats as (
    select
        department,
        count(*) as total_employees,
        sum(case when is_active then 1 else 0 end) as active_employees,
        sum(case when not is_active then 1 else 0 end) as terminated_employees,

        -- demographics
        round(avg(age), 1) as avg_age,
        round(avg(tenure_years), 2) as avg_tenure_years,
        round(avg(base_annual_salary), 2) as avg_salary,
        round(min(base_annual_salary), 2) as min_salary,
        round(max(base_annual_salary), 2) as max_salary,
        round(median(base_annual_salary), 2) as median_salary,

        -- composition
        sum(case when gender = 'Male' then 1 else 0 end) as male_count,
        sum(case when gender = 'Female' then 1 else 0 end) as female_count,
        sum(case when gender = 'Non-Binary' then 1 else 0 end) as non_binary_count,

        round(
            sum(case when gender = 'Female' then 1.0 else 0 end) / nullif(count(*), 0) * 100, 1
        ) as female_pct,

        -- employment type
        sum(case when employment_type = 'Full-Time' then 1 else 0 end) as full_time_count,
        sum(case when employment_type = 'Part-Time' then 1 else 0 end) as part_time_count,
        sum(case when employment_type = 'Contract' then 1 else 0 end) as contract_count,

        -- location
        count(distinct location) as distinct_locations

    from employees
    group by department
)

select * from dept_stats
