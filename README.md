# RIAS — семестровая платформа данных (вуз)

Локальный стек по ТЗ: MinIO (S3), Redpanda (Kafka API), ClickHouse, Grafana, Prefect, Great Expectations, Feast, Cube.js, Streamlit, опционально Spark+Iceberg и Flink.

## Быстрый старт

Рекомендуется **Python 3.11 или 3.12** для полного стека (включая Feast). На **Python 3.13** строка `requirements-feast.txt` не ставит Feast — используй отдельное venv 3.11 или только Docker-часть.

1. Установи зависимости Python и подними Docker:

```powershell
docker compose up -d postgres minio minio-init redpanda redpanda-topic-init clickhouse grafana prefect-server lms-api cube streamlit-ui
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m pip install -r requirements-feast.txt
copy .env.example .env
```

2. Ingest в raw (Parquet в MinIO):

```powershell
py -m src.ingest.flow
```

3. Bronze/Silver/Gold без Spark:

```powershell
py -m src.lakehouse.pandas_lakehouse
```

4. Feast (из каталога `feast_repo`):

```powershell
cd feast_repo
feast apply
cd ..
```

5. Потоковая демонстрация (два терминала):

```powershell
py -m src.streaming.generator
py -m src.streaming.window_consumer
```

6. Spark + Iceberg (профиль `lakehouse`):

```powershell
docker compose --profile lakehouse run --rm spark-lakehouse
```

7. Flink UI (профиль `flink`):

```powershell
docker compose --profile flink up -d flink-jobmanager flink-taskmanager
```

## Сервисы

| Сервис | URL |
|--------|-----|
| MinIO API | http://localhost:9000 |
| MinIO Console | http://localhost:9001 |
| Redpanda Kafka (внешний) | localhost:19092 |
| ClickHouse HTTP | http://localhost:8123 |
| ClickHouse native (хост) | localhost:9009 |
| Grafana | http://localhost:3000 (admin/admin) |
| Prefect UI | http://localhost:4200 |
| LMS API | http://localhost:8000/docs |
| Cube.js | http://localhost:4000 |
| Streamlit | http://localhost:8501 |

## Тесты

```powershell
py -m pytest -q
```

## Terraform (пример IaC)

См. [infra/terraform](infra/terraform) и [docs/runbook.md](docs/runbook.md).

## Документация

- [Runbook](docs/runbook.md)
- [Data Product: academic_performance](docs/data-product-academic-performance.md)
- [ADR-001](docs/ADR-001-orchestration-and-iac.md)
- [ADR-002](docs/ADR-002-lakehouse-and-streaming.md)

## Телеграм-алерты

Заполни `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` в `.env` (не коммить).
