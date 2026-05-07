# Runbook — local demo (Windows)

## Prerequisites

- Docker Desktop
- Python 3.11+ with launcher `py`
- Optional: Terraform CLI for `infra/terraform`

## 1. Start the stack

```powershell
cd RIAS_project
docker compose up -d postgres minio minio-init redpanda redpanda-topic-init clickhouse grafana prefect-server lms-api cube streamlit-ui
```

Wait until `docker compose ps` shows services up. MinIO console: `http://localhost:9001` (user/password `minioadmin` by default).

## 2. Python environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and adjust if needed.

## 3. Ingest (Prefect flow)

With LMS API reachable at `http://localhost:8000`:

```powershell
py -m src.ingest.flow
```

## 4. Bronze/Silver/Gold without Spark

```powershell
py -m src.lakehouse.pandas_lakehouse
```

## 5. Feast

Требуется Python **ниже 3.13** для пакета Feast (см. `requirements-feast.txt`). Установка: `py -m pip install -r requirements-feast.txt`.

```powershell
cd feast_repo
feast apply
cd ..
```

## 6. Streaming demo

Terminal A:

```powershell
py -m src.streaming.generator
```

Terminal B:

```powershell
py -m src.streaming.window_consumer
```

## 7. Spark + Iceberg (optional)

```powershell
docker compose --profile lakehouse run --rm spark-lakehouse
```

## 8. Flink UI (optional)

```powershell
docker compose --profile flink up -d flink-jobmanager flink-taskmanager
```

Open `http://localhost:8081`.

## 9. UIs

- Grafana: `http://localhost:3000` (admin/admin)
- Cube.js dev: `http://localhost:4000`
- Streamlit: `http://localhost:8501`

## 10. Terraform MinIO sample

Stop Compose MinIO if port clash, then:

```powershell
cd infra\terraform
terraform init
terraform apply
```

API: `http://localhost:19005` (see Terraform outputs).

## Remote Debian (last step)

Copy the repository, install Docker, reuse the same `docker compose` file, open firewall ports as needed, and bind services to the VPS IP.
