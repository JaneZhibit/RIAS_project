import pandas as pd

from src.ingest.ge_validation import validate_submissions_df, validate_submissions_simple


def test_validate_submissions_simple_ok():
    df = pd.DataFrame(
        {
            "submission_id": ["a", "b"],
            "student_id": ["s1", "s2"],
            "score": [10.0, 20.0],
        }
    )
    validate_submissions_simple(df)


def test_validate_submissions_df_success():
    df = pd.DataFrame(
        {
            "submission_id": ["a", "b"],
            "student_id": ["s1", "s2"],
            "score": [10.0, 20.0],
        }
    )
    assert validate_submissions_df(df) is True
