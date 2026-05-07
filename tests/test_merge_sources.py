import pandas as pd

from src.ingest.flow import merge_sources


def test_merge_sources_fn():
    lms = pd.DataFrame(
        {
            "submission_id": ["l1"],
            "student_id": ["s1"],
            "course_id": ["CS101"],
            "assignment_id": ["hw1"],
            "score": [80.0],
            "submitted_at": ["2025-01-01T00:00:00Z"],
        }
    )
    csv = pd.DataFrame(
        {
            "student_id": ["s2"],
            "course_id": ["CS101"],
            "assignment_id": ["hw2"],
            "score": [90.0],
            "graded_at": ["2025-01-02T00:00:00Z"],
        }
    )
    out = merge_sources.fn(lms, csv)
    assert len(out) == 2
    assert out["submission_id"].is_unique
