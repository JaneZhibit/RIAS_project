#!/usr/bin/env bash
set -euo pipefail
PACKAGES="org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2,org.apache.hadoop:hadoop-aws:3.4.0,com.amazonaws:aws-java-sdk-bundle:1.12.262"
exec /opt/spark/bin/spark-submit \
  --packages "${PACKAGES}" \
  /opt/spark/work-dir/spark_job.py
