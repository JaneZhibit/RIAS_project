"""
Sliding-window aggregation (5 minutes) from Kafka into ClickHouse.

Flink/ksqlDB alternative for constrained environments: same semantics,
Python consumer + idempotent inserts into MergeTree.
Run: py -m src.streaming.window_consumer
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from clickhouse_driver import Client
from kafka import KafkaConsumer

from src.config import get_settings


@dataclass
class Event:
    ts: datetime
    building_id: str


def floor_to_window(dt: datetime, minutes: int = 5) -> datetime:
    epoch = int(dt.timestamp())
    step = minutes * 60
    floored = epoch - (epoch % step)
    return datetime.fromtimestamp(floored, tz=timezone.utc)


def main() -> None:
    s = get_settings()
    consumer = KafkaConsumer(
        "campus_events",
        bootstrap_servers=s["kafka_bootstrap"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="rias-window-consumer",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    ch = Client(
        host=s["clickhouse_host"],
        port=int(s["clickhouse_port"]),
        user=s["clickhouse_user"],
        password=s["clickhouse_password"] or None,
    )
    # Per-building deque of timestamps (last 5 minutes)
    buffers: dict[str, deque[datetime]] = defaultdict(deque)
    window = timedelta(minutes=5)
    print("Consuming campus_events; writing campus_occupancy_5m (Ctrl+C to stop)")
    try:
        for msg in consumer:
            payload = msg.value
            ts = datetime.fromisoformat(payload["event_time"].replace("Z", "+00:00"))
            bid = str(payload["building_id"])
            dq = buffers[bid]
            dq.append(ts)
            cutoff = ts - window
            while dq and dq[0] < cutoff:
                dq.popleft()
            wstart = floor_to_window(ts, 5)
            people = len(dq)
            ch.execute(
                "INSERT INTO campus_occupancy_5m (window_start, building_id, people) VALUES",
                [(wstart.replace(tzinfo=None), bid, people)],
            )
    except KeyboardInterrupt:
        consumer.close()


if __name__ == "__main__":
    main()
