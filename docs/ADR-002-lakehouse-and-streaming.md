# ADR-002: Lakehouse tables and streaming aggregation

## Context

The brief requires Apache Iceberg (or Delta Lake) with Spark for Bronze/Silver/Gold, plus Flink or ksqlDB for sliding windows, and ClickHouse for serving.

## Decision

- **Spark + Iceberg** run in the optional Compose profile `lakehouse` (`docker compose --profile lakehouse run --rm spark-lakehouse`), writing Iceberg tables under the `rias` catalog into the MinIO warehouse path `s3a://<bucket>/iceberg-warehouse`.
- A **Pandas fallback** (`py -m src.lakehouse.pandas_lakehouse`) writes Bronze/Silver/Gold Parquet prefixes in MinIO when Spark is not available (laptops with limited RAM).
- **Streaming**: a Python consumer (`py -m src.streaming.window_consumer`) implements **5-minute window occupancy** per building from Kafka topics, writing into ClickHouse. This matches the lab semantics while avoiding a heavy Flink classpath on small machines. **Flink** remains available as an optional Compose profile `flink` for Flink UI exploration and future SQL jobs.

## Consequences

- Defense narrative should contrast the Python consumer (operational simplicity) with Flink (distributed state) and state when Flink would be introduced in production.
