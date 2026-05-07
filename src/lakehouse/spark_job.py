"""
PySpark + Iceberg: raw Parquet on MinIO -> Iceberg silver table (Hadoop catalog on S3A).

Run inside docker compose profile lakehouse (see README).
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

BUCKET = os.environ.get("MINIO_BUCKET", "rias-lake")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
ACCESS = os.environ.get("MINIO_ROOT_USER", "minioadmin")
SECRET = os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")


def _endpoint_host_port(url: str) -> tuple[str, str]:
    u = urlparse(url)
    host = u.hostname or "minio"
    port = str(u.port or 9000)
    return host, port


def build_spark() -> SparkSession:
    host, port = _endpoint_host_port(MINIO_ENDPOINT)
    spark = (
        SparkSession.builder.appName("rias-iceberg")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config("spark.sql.catalog.rias", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.rias.type", "hadoop")
        .config("spark.sql.catalog.rias.warehouse", f"s3a://{BUCKET}/iceberg-warehouse")
        .getOrCreate()
    )
    hconf = spark.sparkContext._jsc.hadoopConfiguration()
    hconf.set("fs.s3a.endpoint", f"{host}:{port}")
    hconf.set("fs.s3a.path.style.access", "true")
    hconf.set("fs.s3a.access.key", ACCESS)
    hconf.set("fs.s3a.secret.key", SECRET)
    hconf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    hconf.set("fs.s3a.connection.ssl.enabled", "false")
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main() -> None:
    spark = build_spark()
    raw_glob = f"s3a://{BUCKET}/raw/academic_performance/submissions/**/*.parquet"
    schema = T.StructType(
        [
            T.StructField("submission_id", T.StringType(), True),
            T.StructField("student_id", T.StringType(), True),
            T.StructField("course_id", T.StringType(), True),
            T.StructField("assignment_id", T.StringType(), True),
            T.StructField("score", T.DoubleType(), True),
            T.StructField("submitted_at", T.StringType(), True),
        ]
    )
    try:
        df = spark.read.schema(schema).parquet(raw_glob)
    except Exception:
        df = spark.createDataFrame([], schema)
    if df.rdd.isEmpty():
        # minimal row so catalog creation succeeds on first demo
        df = spark.createDataFrame(
            [
                (
                    "sub_seed",
                    "s0001",
                    "CS101",
                    "hw_0",
                    70.0,
                    "2025-01-01T00:00:00+00:00",
                )
            ],
            schema,
        )
    spark.sql("CREATE NAMESPACE IF NOT EXISTS rias.academic")
    (
        df.writeTo("rias.academic.silver_submissions")
        .using("iceberg")
        .tableProperty("format-version", "2")
        .createOrReplace()
    )
    gold = df.groupBy("student_id").agg(F.avg("score").alias("avg_grade"))
    (
        gold.writeTo("rias.academic.gold_student_grades")
        .using("iceberg")
        .tableProperty("format-version", "2")
        .createOrReplace()
    )
    spark.stop()


if __name__ == "__main__":
    main()
