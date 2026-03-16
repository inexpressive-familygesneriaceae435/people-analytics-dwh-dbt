-- Validates that hire_date is always before termination_date.

select
    employee_id,
    hire_date,
    termination_date
from {{ ref('stg_employees') }}
where termination_date is not null
  and hire_date >= termination_date
