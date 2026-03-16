with promotions as (
    select * from {{ ref('stg_promotions') }}
),

employees as (
    select * from {{ ref('int_employee_tenure_bands') }}
),

promo_detail as (
    select
        p.promotion_year as report_year,
        p.promotion_quarter as report_quarter,
        e.department,
        e.gender,
        e.tenure_band,
        e.age_band,

        count(*) as promotion_count,
        avg(p.salary_change_pct) as avg_salary_bump_pct,
        sum(case when p.is_lateral_move then 1 else 0 end) as lateral_moves,
        avg(p.level_change) as avg_level_jump

    from promotions p
    inner join employees e on p.employee_id = e.employee_id
    group by
        p.promotion_year,
        p.promotion_quarter,
        e.department,
        e.gender,
        e.tenure_band,
        e.age_band
),

dept_headcount as (
    select
        department,
        gender,
        tenure_band,
        age_band,
        count(*) as segment_size
    from employees
    group by department, gender, tenure_band, age_band
),

with_rates as (
    select
        pd.*,
        dh.segment_size,
        case
            when dh.segment_size > 0
            then round(pd.promotion_count * 100.0 / dh.segment_size, 2)
            else 0
        end as promotion_rate_pct

    from promo_detail pd
    left join dept_headcount dh
        on pd.department = dh.department
        and pd.gender = dh.gender
        and pd.tenure_band = dh.tenure_band
        and pd.age_band = dh.age_band
)

select * from with_rates
