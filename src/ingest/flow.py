"""Prefect flow: LMS API + CSV -> MinIO raw Parquet + validation + lineage metadata."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pandas as pd
from prefect import flow, get_run_logger, task
from prefect.settings import PREFECT_API_URL, temporary_settings

from src.config import get_settings
from src.ingest.ge_validation import validate_submissions_df
from src.ingest.s3io import upload_parquet
from src.ingest.telegram_notify import send_telegram


@task(retries=3, retry_delay_seconds=10)
def fetch_lms_submissions(limit: int = 100) -> pd.DataFrame:
    s = get_settings()
    url = f"{s['lms_api_base'].rstrip('/')}/api/v1/submissions"
    # Avoid OS/IDE proxy auto-detection for local service calls.
    r = httpx.get(url, params={"limit": limit}, timeout=30.0, trust_env=False)
    r.raise_for_status()
    data = r.json()["items"]
    return pd.DataFrame(data)


@task(retries=2, retry_delay_seconds=5)
def load_csv_grades(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


@task
def merge_sources(lms_df: pd.DataFrame, csv_df: pd.DataFrame) -> pd.DataFrame:
    """Align CSV grades with LMS-shaped raw rows."""
    csv_df = csv_df.copy()
    csv_df["submission_id"] = (
        "csv_" + csv_df["student_id"].astype(str) + "_" + csv_df["assignment_id"].astype(str)
    )
    csv_df["submitted_at"] = csv_df["graded_at"]
    csv_df = csv_df.rename(columns={})
    cols = ["submission_id", "student_id", "course_id", "assignment_id", "score", "submitted_at"]
    csv_part = csv_df[cols]
    lms_part = lms_df[[c for c in cols if c in lms_df.columns]]
    out = pd.concat([lms_part, csv_part], ignore_index=True)
    out = out.drop_duplicates(subset=["submission_id"], keep="first")
    return out


@task
def validate_raw(df: pd.DataFrame) -> pd.DataFrame:
    ok = validate_submissions_df(df)
    if not ok:
        raise ValueError("Great Expectations validation failed")
    return df


@task
def write_raw_parquet(df: pd.DataFrame) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"raw/academic_performance/submissions/{ts}/part-000.parquet"
    lineage = {
        "domain": "academic_performance",
        "sources": "lms_api:/api/v1/submissions;file:grades_export.csv",
        "sink": f"s3://{get_settings()['minio_bucket']}/{key}",
        "run_ts": ts,
    }
    upload_parquet(df, key, metadata=lineage)
    return key


@flow(name="rias-raw-ingest", log_prints=True)
def ingest_academic_flow(csv_path: str | None = None) -> str:
    logger = get_run_logger()
    root = Path(__file__).resolve().parents[2]
    csv = Path(csv_path) if csv_path else root / "data" / "sample" / "grades_export.csv"
    try:
        lms_df = fetch_lms_submissions()
        csv_df = load_csv_grades(csv)
        merged = merge_sources(lms_df, csv_df)
        validated = validate_raw(merged)
        key = write_raw_parquet(validated)
        logger.info("Raw ingest OK: %s rows -> %s", len(validated), key)
        return key
    except Exception as e:
        send_telegram(f"RIAS ingest failed: {e}")
        raise


if __name__ == "__main__":
    # Some Windows environments inject local traffic via a proxy and break
    # Prefect API calls to localhost with intermittent 502 responses.
    os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1")
    os.environ.setdefault("no_proxy", "localhost,127.0.0.1")
    # Ensure local CLI runs are visible in Prefect Server UI.
    api_url = os.getenv("PREFECT_API_URL") or get_settings()["prefect_api_url"]
    with temporary_settings({PREFECT_API_URL: api_url}):
        ingest_academic_flow()
