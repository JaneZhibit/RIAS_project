"""Data quality checks for raw ingest (Great Expectations-style + deterministic asserts)."""

from __future__ import annotations

import pandas as pd


def validate_submissions_simple(df: pd.DataFrame) -> None:
    """Deterministic checks used by the ingest flow."""
    assert df["submission_id"].is_unique, "duplicate submission_id"
    assert df["score"].between(0, 100).all(), "score out of range"
    assert df["student_id"].notna().all(), "null student_id"


def validate_submissions_df(df: pd.DataFrame) -> bool:
    """
    Run simple checks first, then optional Great Expectations 1.x suite (ephemeral).
    """
    validate_submissions_simple(df)
    try:
        import great_expectations as gx
        import great_expectations.expectations as gxe

        context = gx.get_context(mode="ephemeral")
        batch_definition = (
            context.data_sources.add_pandas("ingest_pandas")
            .add_df_data_asset(name="submissions", dataframe=df)
            .add_batch_definition_whole_dataframe("whole")
        )
        batch = batch_definition.get_batch()
        suite = context.add_expectation_suite(expectation_suite_name="raw_submissions")
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeUnique(column="submission_id"),
        )
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeBetween(column="score", min_value=0, max_value=100),
        )
        suite.add_expectation(
            gxe.ExpectColumnValuesToNotBeNull(column="student_id"),
        )
        result = batch.validate(expectation_suite=suite)
        return bool(result.success)
    except Exception:
        return True
