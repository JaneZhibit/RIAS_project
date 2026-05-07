"""Simulate campus / LMS events into Kafka (Redpanda). Run: py -m src.streaming.generator"""

from __future__ import annotations

import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

from src.config import get_settings

BUILDINGS = ["A", "B", "C", "MAIN"]
EVENT_TYPES = ["enter_building", "submit_assignment", "open_lms"]


def main() -> None:
    s = get_settings()
    producer = KafkaProducer(
        bootstrap_servers=s["kafka_bootstrap"],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=5,
    )
    topic = "campus_events"
    rng = random.Random(7)
    print(f"Publishing to {topic} at {s['kafka_bootstrap']}")
    try:
        while True:
            ev = {
                "event_time": datetime.now(timezone.utc).isoformat(),
                "building_id": rng.choice(BUILDINGS),
                "event_type": rng.choice(EVENT_TYPES),
                "student_id": f"s{rng.randint(1, 50):04d}",
            }
            producer.send(topic, value=ev)
            producer.flush()
            time.sleep(0.5 + rng.random() * 1.5)
    except KeyboardInterrupt:
        producer.close()


if __name__ == "__main__":
    main()
