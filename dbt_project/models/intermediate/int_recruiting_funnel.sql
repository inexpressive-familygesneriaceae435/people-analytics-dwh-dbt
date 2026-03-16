with recruiting as (
    select * from {{ ref('stg_recruiting') }}
),

per_requisition as (
    select
        requisition_id,
        department,
        job_title,
        job_level,
        min(application_date) as first_application_date,
        max(hire_date) as last_hire_date,

        -- funnel counts
        count(*) as total_applicants,
        sum(case when status in ('Screened', 'Interviewed', 'Offered', 'Hired') then 1 else 0 end) as screened,
        sum(case when status in ('Interviewed', 'Offered', 'Hired') then 1 else 0 end) as interviewed,
        sum(case when status in ('Offered', 'Hired') then 1 else 0 end) as offered,
        sum(case when status = 'Hired' then 1 else 0 end) as hired,
        sum(case when status = 'Rejected' then 1 else 0 end) as rejected,
        sum(case when status = 'Withdrawn' then 1 else 0 end) as withdrawn,

        -- conversion rates
        round(
            sum(case when status in ('Screened', 'Interviewed', 'Offered', 'Hired') then 1.0 else 0 end)
            / nullif(count(*), 0), 3
        ) as screen_rate,

        round(
            sum(case when status in ('Interviewed', 'Offered', 'Hired') then 1.0 else 0 end)
            / nullif(sum(case when status in ('Screened', 'Interviewed', 'Offered', 'Hired') then 1 else 0 end), 0), 3
        ) as interview_rate,

        round(
            sum(case when status = 'Hired' then 1.0 else 0 end)
            / nullif(sum(case when status in ('Offered', 'Hired') then 1 else 0 end), 0), 3
        ) as offer_acceptance_rate,

        -- avg durations
        avg(days_to_screen) as avg_days_to_screen,
        avg(days_to_hire) as avg_days_to_hire,

        -- source mix
        count(distinct source) as distinct_sources

    from recruiting
    group by requisition_id, department, job_title, job_level
)

select * from per_requisition
