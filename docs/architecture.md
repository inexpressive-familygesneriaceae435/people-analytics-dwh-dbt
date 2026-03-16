# Architecture — People Analytics DWH

## System Overview

```mermaid
graph TB
    subgraph Generation["Data Generation (Python)"]
        GEN["PeopleAnalyticsDataGenerator<br/>src/generate_data.py"] --> CSV["7 CSV Files<br/>(employees, absences, payroll,<br/>promotions, training, surveys, recruiting)"]
    end

    subgraph DWH["Data Warehouse (dbt + DuckDB)"]
        CSV --> SEEDS["dbt Seeds<br/>(raw schema)"]
        SEEDS --> STG["Staging Layer<br/>(7 views)"]
        STG --> INT["Intermediate Layer<br/>(5 views)"]
        INT --> MARTS["Marts Layer<br/>(9 tables)"]
    end

    subgraph Marts["Mart Models"]
        MARTS --> DIM_E["dim_employees"]
        MARTS --> DIM_D["dim_departments"]
        MARTS --> FCT_H["fct_headcount_monthly"]
        MARTS --> FCT_T["fct_turnover_monthly"]
        MARTS --> FCT_A["fct_absenteeism_monthly"]
        MARTS --> FCT_M["fct_internal_mobility"]
        MARTS --> FCT_P["fct_promotions_quarterly"]
        MARTS --> FCT_TR["fct_training_adoption"]
        MARTS --> FCT_R["fct_recruiting_pipeline"]
    end

    subgraph Quality["Data Quality"]
        MARTS --> TESTS["dbt Tests<br/>(unique, not_null,<br/>accepted_values,<br/>relationships,<br/>custom assertions)"]
    end
```

## dbt Layer Architecture

```mermaid
graph LR
    subgraph Raw["Raw (Seeds)"]
        R1[raw_employees]
        R2[raw_absences]
        R3[raw_payroll]
        R4[raw_promotions]
        R5[raw_training]
        R6[raw_surveys]
        R7[raw_recruiting]
    end

    subgraph Staging["Staging (Views)"]
        S1[stg_employees]
        S2[stg_absences]
        S3[stg_payroll]
        S4[stg_promotions]
        S5[stg_training]
        S6[stg_surveys]
        S7[stg_recruiting]
    end

    subgraph Intermediate["Intermediate (Views)"]
        I1[int_employee_tenure_bands]
        I2[int_absence_monthly]
        I3[int_compensation_history]
        I4[int_training_completion]
        I5[int_recruiting_funnel]
    end

    subgraph Marts["Marts (Tables)"]
        M1[dim_employees]
        M2[dim_departments]
        M3[fct_headcount_monthly]
        M4[fct_turnover_monthly]
        M5[fct_absenteeism_monthly]
        M6[fct_internal_mobility]
        M7[fct_promotions_quarterly]
        M8[fct_training_adoption]
        M9[fct_recruiting_pipeline]
    end

    R1 --> S1 --> I1 --> M1
    R2 --> S2 --> I2 --> M5
    R3 --> S3 --> I3
    R4 --> S4 --> M6
    R5 --> S5 --> I4 --> M8
    R6 --> S6 --> M1
    R7 --> S7 --> I5 --> M9
    S1 --> M2
    S1 --> M3 --> M4
    I1 --> M7
    M3 --> M5
```

## Semantic Layer Mapping

How mart models map to enterprise People Analytics dashboards (TOTVS RH, Workday, SAP SF):

| Mart Model | HR KPI | Enterprise Dashboard Equivalent |
|-----------|--------|-------------------------------|
| fct_headcount_monthly | Headcount, Growth Rate | Workforce Planning |
| fct_turnover_monthly | Turnover Rate (Vol/Invol) | Attrition Dashboard |
| fct_absenteeism_monthly | Absence Rate, Bradford Factor | Absenteeism Monitor |
| fct_internal_mobility | Mobility Rate, Promotion Rate | Career Development |
| fct_promotions_quarterly | Promotion Equity by Gender/Age | DEI & Equity Analytics |
| fct_training_adoption | Completion Rate, Compliance | Learning & Development |
| fct_recruiting_pipeline | Time-to-Fill, Source ROI | Talent Acquisition |
| dim_employees | Employee 360 Profile | Employee Directory |
| dim_departments | Department Scorecard | Organizational Health |

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Data Generation | Python + Faker + NumPy | Synthetic HR data with realistic correlations |
| Warehouse | DuckDB | Embedded analytical database (zero infrastructure) |
| Transformation | dbt-core + dbt-duckdb | SQL-based data transformation + testing |
| Testing | dbt tests + pytest | Data quality (dbt) + generator correctness (pytest) |
| CI/CD | GitHub Actions | Lint, test, dbt build on every push |
| Containerization | Docker + Docker Compose | Reproducible pipeline execution |
