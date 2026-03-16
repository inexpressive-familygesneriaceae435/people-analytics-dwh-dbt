FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Default: run full pipeline
CMD ["bash", "-c", "python -m src.generate_data && cd dbt_project && dbt deps && dbt seed --target dev && dbt run --target dev && dbt test --target dev"]
