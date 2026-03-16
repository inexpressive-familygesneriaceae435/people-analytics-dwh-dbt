-- Validates that monthly turnover rates are within reasonable bounds (0-50%).
-- Rates above 50% per month would indicate a data quality issue.

select
    report_month,
    department,
    turnover_rate
from {{ ref('fct_turnover_monthly') }}
where turnover_rate < 0 or turnover_rate > 50
