"""
Lightweight Bronze/Silver/Gold on MinIO using Pandas (no Spark).
Use when Spark profile is unavailable. Run: py -m src.lakehouse.pandas_lakehouse
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import boto3
import pandas as pd
from botocore.client import Config
from io import BytesIO

from src.config import get_settings


def _s3():
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


def _read_latest_raw_parquet() -> pd.DataFrame:
    s = get_settings()
    client = _s3()
    prefix = "raw/academic_performance/submissions/"
    keys = []
    token = None
    while True:
        kwargs = {"Bucket": s["minio_bucket"], "Prefix": prefix}
        if token:
            kwargs["ContinuationToken"] = token
        resp = client.list_objects_v2(**kwargs)
        for obj in resp.get("Contents", []):
            k = obj["Key"]
            if k.endswith(".parquet"):
                keys.append(k)
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
    if not keys:
        return pd.DataFrame(
            columns=[
                "submission_id",
                "student_id",
                "course_id",
                "assignment_id",
                "score",
                "submitted_at",
            ]
        )
    latest = sorted(keys)[-1]
    body = client.get_object(Bucket=s["minio_bucket"], Key=latest)["Body"].read()
    return pd.read_parquet(BytesIO(body))


def _put_parquet(df: pd.DataFrame, key: str) -> None:
    buf = BytesIO()
    df.to_parquet(buf, index=False)
    s = get_settings()
    _s3().put_object(Bucket=s["minio_bucket"], Key=key, Body=buf.getvalue())


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw = _read_latest_raw_parquet()
    bronze_key = f"bronze/academic_performance/submissions/{ts}/part.parquet"
    _put_parquet(raw, bronze_key)
    silver = raw.drop_duplicates(subset=["submission_id"]).copy()
    silver["score"] = silver["score"].clip(0, 100)
    silver_key = f"silver/academic_performance/submissions/{ts}/part.parquet"
    _put_parquet(silver, silver_key)
    gold = (
        silver.groupby("student_id", as_index=False)["score"]
        .mean()
        .rename(columns={"score": "avg_grade"})
    )
    gold_key = f"gold/academic_performance/student_grades/{ts}/part.parquet"
    _put_parquet(gold, gold_key)
    out = Path(__file__).resolve().parents[2] / "feast_repo" / "data" / "gold_student_features.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    # Feast training table shape
    feat = gold.rename(columns={"avg_grade": "avg_grade_30d"})
    feat["snapshot_date"] = pd.to_datetime(datetime.now(timezone.utc))
    feat["lms_actions_7d"] = 0
    feat["attendance_ratio_14d"] = 0.8
    feat.to_parquet(out, index=False)
    print("Wrote", bronze_key, silver_key, gold_key, "and", out)


if __name__ == "__main__":
    main()
