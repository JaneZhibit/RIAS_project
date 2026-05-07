"""Central settings from environment (local + Docker)."""

from __future__ import annotations

import os
from functools import lru_cache


@lru_cache
def get_settings() -> dict[str, str]:
    return {
        "minio_endpoint": os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        "minio_access_key": os.getenv("MINIO_ROOT_USER", "minioadmin"),
        "minio_secret_key": os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
        "minio_bucket": os.getenv("MINIO_BUCKET", "rias-lake"),
        "kafka_bootstrap": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092"),
        "clickhouse_host": os.getenv("CLICKHOUSE_HOST", "localhost"),
        "clickhouse_port": os.getenv("CLICKHOUSE_PORT", "9009"),
        "clickhouse_user": os.getenv("CLICKHOUSE_USER", "rias"),
        "clickhouse_password": os.getenv("CLICKHOUSE_PASSWORD", "rias"),
        "lms_api_base": os.getenv("LMS_API_BASE_URL", "http://localhost:8000"),
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        "prefect_api_url": os.getenv("PREFECT_API_URL", "http://localhost:4200/api"),
    }
