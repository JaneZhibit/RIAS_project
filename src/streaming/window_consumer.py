"""
Sliding-window aggregation (5 minutes) from Kafka into ClickHouse.

Flink/ksqlDB alternative for constrained environments: same semantics,
Python consumer + idempotent inserts into MergeTree.
Run: py -m src.streaming.window_consumer
"""

from __future__ import annotations

import json
import random
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from clickhouse_driver import Client
from kafka import KafkaConsumer

from src.config import get_settings

VK_TOKEN = "vk1.a.nxVoufLzFpw7oAYKjNWLJ4ISz2PC9PzehsZ7TFU757l79uYrRA7_nd1rW6QHg1irWQax0uVBGDnruhtmBCtWtSL-2zJlwxbFi2HN_7DkszWUUZvLsh4QU0Zr5EHz6hb44kZqCVpqCv2681OWEudZg3JSE-P_p6Tvct2YdPiYty48sehLem555s1ynrxh4PHS8z8Xqv1Q6_qDnvpcBHaysA"
VK_API_VERSION = "5.131"
LAST_ALERT_TIME = {}

def send_vk_alert(building_id: str, people: int):
    """Send VK alert to all users who allowed messages to the bot."""
    global LAST_ALERT_TIME
    now = datetime.now()
    # Rate limit: 1 alert per 5 minutes per building
    if building_id in LAST_ALERT_TIME and (now - LAST_ALERT_TIME[building_id]).total_seconds() < 300:
        return
        
    try:
        url = f"https://api.vk.com/method/messages.getConversations?filter=all&v={VK_API_VERSION}&access_token={VK_TOKEN}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req).read()
        data = json.loads(resp)
        if "response" in data:
            for item in data["response"]["items"]:
                peer_id = item["conversation"]["peer"]["id"]
                send_url = "https://api.vk.com/method/messages.send"
                post_data = urllib.parse.urlencode({
                    "peer_id": peer_id,
                    "message": f"🚨 ВНИМАНИЕ! Превышение лимита в корпусе {building_id}!\nСейчас там {people} человек.",
                    "random_id": random.randint(1, 2147483647),
                    "v": VK_API_VERSION,
                    "access_token": VK_TOKEN
                }).encode("utf-8")
                urllib.request.urlopen(urllib.request.Request(send_url, data=post_data))
            LAST_ALERT_TIME[building_id] = now
            print(f"Sent VK alert for {building_id}")
    except Exception as e:
        print("VK Alert error:", e)


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
            
            # Send alert if there are more than 60 people
            if people > 60:
                send_vk_alert(bid, people)
    except KeyboardInterrupt:
        consumer.close()


if __name__ == "__main__":
    main()
