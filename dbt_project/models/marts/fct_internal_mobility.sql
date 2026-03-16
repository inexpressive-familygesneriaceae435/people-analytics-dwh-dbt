with promotions as (
    select * from {{ ref('stg_promotions') }}
),

employees as (
    select * from {{ ref('stg_employees') }}
),

headcount as (
    select
        report_quarter,
        department,
        sum(active_headcount) / nullif(count(*), 0) as avg_quarterly_headcount
    from {{ ref('fct_headcount_monthly') }}
    group by report_quarter, department
),

quarterly_mobility as (
    select
        p.promotion_year,
        p.promotion_quarter,
        e.department,

        count(*) as total_movements,
        sum(case when not p.is_lateral_move then 1 else 0 end) as vertical_promotions,
        sum(case when p.is_lateral_move then 1 else 0 end) as lateral_moves,
        sum(case when p.level_change > 1 then 1 else 0 end) as skip_level_promotions,

        round(avg(p.salary_change_pct), 1) as avg_salary_change_pct,
        round(avg(p.level_change), 2) as avg_level_change

    from promotions p
    inner join employees e on p.employee_id = e.employee_id
    group by p.promotion_year, p.promotion_quarter, e.department
),

with_rates as (
    select
        qm.*,
        concat(qm.promotion_year, '-Q', qm.promotion_quarter) as report_quarter,
        h.avg_quarterly_headcount,

        case
            when h.avg_quarterly_headcount > 0
            then round(qm.total_movements * 100.0 / h.avg_quarterly_headcount, 2)
            else 0
        end as mobility_rate,

        case
            when h.avg_quarterly_headcount > 0
            then round(qm.vertical_promotions * 100.0 / h.avg_quarterly_headcount, 2)
            else 0
        end as promotion_rate

    from quarterly_mobility qm
    left join headcount h
        on h.report_quarter = qm.promotion_quarter
        and h.department = qm.department
)

select * from with_rates
