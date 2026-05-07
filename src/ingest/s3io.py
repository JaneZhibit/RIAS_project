"""Write Parquet to MinIO (S3-compatible)."""

from __future__ import annotations

import io
from typing import Any

import boto3
import pandas as pd
from botocore.client import Config

from src.config import get_settings


def _client():
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s["minio_endpoint"],
        aws_access_key_id=s["minio_access_key"],
        aws_secret_access_key=s["minio_secret_key"],
        # Keep local MinIO calls direct even if system proxies are configured.
        config=Config(signature_version="s3v4", proxies={}),
        region_name="us-east-1",
    )


def upload_parquet(df: pd.DataFrame, key: str, metadata: dict[str, str] | None = None) -> None:
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    body = buf.getvalue()
    s = get_settings()
    extra: dict[str, Any] = {}
    if metadata:
        extra["Metadata"] = {k: str(v)[:2048] for k, v in metadata.items()}
    _client().put_object(Bucket=s["minio_bucket"], Key=key, Body=body, **extra)
