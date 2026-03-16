-- Validates that monthly absence rates are within reasonable bounds (0-100%).

select
    report_month,
    department,
    absence_rate
from {{ ref('fct_absenteeism_monthly') }}
where absence_rate < 0 or absence_rate > 100
