# ADR-001: Orchestration and infrastructure-as-code

## Context

The semester brief requires Terraform for cloud-style resources, Prefect or Airflow for orchestration, and local-first development on Windows.

## Decision

- **Docker Compose** is the primary way to run MinIO, Redpanda, ClickHouse, Grafana, Prefect server, LMS API, Cube.js, and Streamlit locally.
- **Terraform** under `infra/terraform/` provisions an **S3-compatible MinIO** container on the Docker provider using non-default host ports (`19005` / `19006`) so it can coexist with the Compose MinIO stack when needed for IaC demonstrations.
- **Prefect 2** orchestrates batch ingest with retries and optional Telegram notifications.

## Consequences

- Students can develop without paid cloud accounts.
- Two MinIO entry points are possible (Compose vs Terraform); documentation must state which endpoint to use.
