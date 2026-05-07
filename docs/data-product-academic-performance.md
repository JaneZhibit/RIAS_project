# Data Product: `academic_performance`

## Purpose

Curated datasets and features that describe student grades and assignment outcomes for analytics and ML (e.g., grade forecasting).

## Interfaces

| Interface | Format | Consumers |
|-----------|--------|-----------|
| Raw submissions | Parquet in MinIO `raw/academic_performance/submissions/` | Prefect ingest, GE validation |
| Silver submissions | Parquet `silver/...` or Iceberg `rias.academic.silver_submissions` | Gold transforms, Spark |
| Gold aggregates | Parquet `gold/...` or Iceberg `rias.academic.gold_student_grades` | Feast, BI |
| Feature file | `feast_repo/data/gold_student_features.parquet` | Feast offline store |

## SLA (lab defaults)

- **Freshness:** raw layer updated on each successful ingest run (manual or scheduled).
- **Completeness:** ingest fails if LMS API is unreachable after retries or if GE validation fails.
- **Retention:** MinIO bucket retention is manual (lab); production would set lifecycle rules.

## Data quality

- Unique `submission_id`.
- `score` in \[0, 100\].
- Non-null `student_id`.

## Ownership

- Team: RIAS lab project.
- Lineage tags are attached as S3 object metadata from the ingest flow (`domain`, `sources`, `sink`, `run_ts`).
