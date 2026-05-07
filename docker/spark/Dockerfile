FROM apache/spark:3.5.0
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY docker/spark/entrypoint.sh /opt/spark/bin/rias-spark-entrypoint.sh
RUN chmod +x /opt/spark/bin/rias-spark-entrypoint.sh \
    && chown spark:spark /opt/spark/bin/rias-spark-entrypoint.sh
USER spark
WORKDIR /opt/spark/work-dir
ENTRYPOINT ["/opt/spark/bin/rias-spark-entrypoint.sh"]
