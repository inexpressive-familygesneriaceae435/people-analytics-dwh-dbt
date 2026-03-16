with funnel as (
    select * from {{ ref('int_recruiting_funnel') }}
),

recruiting as (
    select * from {{ ref('stg_recruiting') }}
),

quarterly as (
    select
        f.department,
        year(f.first_application_date) as report_year,
        quarter(f.first_application_date) as report_quarter_num,
        concat(year(f.first_application_date), '-Q', quarter(f.first_application_date)) as report_quarter,

        count(distinct f.requisition_id) as total_requisitions,
        sum(f.total_applicants) as total_applicants,
        sum(f.screened) as total_screened,
        sum(f.interviewed) as total_interviewed,
        sum(f.offered) as total_offered,
        sum(f.hired) as total_hired,
        sum(f.rejected) as total_rejected,
        sum(f.withdrawn) as total_withdrawn,

        -- avg conversion rates across requisitions
        round(avg(f.screen_rate), 3) as avg_screen_rate,
        round(avg(f.interview_rate), 3) as avg_interview_rate,
        round(avg(f.offer_acceptance_rate), 3) as avg_offer_acceptance_rate,

        -- time metrics
        round(avg(f.avg_days_to_screen), 1) as avg_days_to_screen,
        round(avg(f.avg_days_to_hire), 1) as avg_days_to_hire,

        -- cost efficiency proxy (applicants per hire)
        case
            when sum(f.hired) > 0
            then round(sum(f.total_applicants) * 1.0 / sum(f.hired), 1)
            else null
        end as applicants_per_hire

    from funnel f
    group by
        f.department,
        year(f.first_application_date),
        quarter(f.first_application_date)
),

source_effectiveness as (
    select
        year(application_date) as report_year,
        quarter(application_date) as report_quarter_num,
        department,
        source,
        count(*) as applications,
        sum(case when status = 'Hired' then 1 else 0 end) as hires,
        case
            when count(*) > 0
            then round(sum(case when status = 'Hired' then 1.0 else 0 end) / count(*) * 100, 2)
            else 0
        end as hire_rate_pct

    from recruiting
    group by year(application_date), quarter(application_date), department, source
),

best_source as (
    select
        report_year,
        report_quarter_num,
        department,
        source as top_source,
        hire_rate_pct as top_source_hire_rate,
        row_number() over (
            partition by report_year, report_quarter_num, department
            order by hires desc, hire_rate_pct desc
        ) as rn
    from source_effectiveness
)

select
    q.*,
    bs.top_source,
    bs.top_source_hire_rate
from quarterly q
left join best_source bs
    on q.report_year = bs.report_year
    and q.report_quarter_num = bs.report_quarter_num
    and q.department = bs.department
    and bs.rn = 1
