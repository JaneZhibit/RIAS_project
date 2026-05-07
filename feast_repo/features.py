from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

student = Entity(name="student", join_keys=["student_id"])

student_stats_source = FileSource(
    name="gold_student_features_source",
    path="data/gold_student_features.parquet",
    timestamp_field="snapshot_date",
)

student_training_features = FeatureView(
    name="student_training_features",
    entities=[student],
    ttl=timedelta(days=3650),
    schema=[
        Field(name="avg_grade_30d", dtype=Float32),
        Field(name="lms_actions_7d", dtype=Int64),
        Field(name="attendance_ratio_14d", dtype=Float32),
    ],
    source=student_stats_source,
)
