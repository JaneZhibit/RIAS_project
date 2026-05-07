"""Minimal LMS API simulator: submissions and activity for ingest demos."""

from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="LMS Simulator", version="0.1.0")

_STUDENT_IDS = [f"s{i:04d}" for i in range(1, 51)]
_COURSES = ["CS101", "CS201", "MATH110", "ENG205"]


class Submission(BaseModel):
    student_id: str
    course_id: str
    assignment_id: str
    score: float = Field(ge=0, le=100)
    submitted_at: datetime | None = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/submissions")
def list_submissions(limit: int = 100) -> dict[str, Any]:
    """Synthetic paginated submissions (deterministic-ish per process)."""
    rng = random.Random(42)
    rows: list[dict[str, Any]] = []
    for i in range(min(limit, 200)):
        sid = rng.choice(_STUDENT_IDS)
        cid = rng.choice(_COURSES)
        score = float(rng.randint(40, 100))
        ts = _utcnow()
        rows.append(
            {
                "submission_id": f"sub_{i:06d}",
                "student_id": sid,
                "course_id": cid,
                "assignment_id": f"hw_{rng.randint(1, 8)}",
                "score": score,
                "submitted_at": ts.isoformat(),
            }
        )
    return {"items": rows, "count": len(rows)}


@app.post("/api/v1/submissions")
def create_submission(body: Submission) -> dict[str, Any]:
    ts = body.submitted_at or _utcnow()
    return {
        "submission_id": f"sub_new_{int(ts.timestamp())}",
        "student_id": body.student_id,
        "course_id": body.course_id,
        "assignment_id": body.assignment_id,
        "score": body.score,
        "submitted_at": ts.isoformat(),
    }
