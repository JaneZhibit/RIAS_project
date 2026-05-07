-- Analytics tables for Cube.js / Grafana (seed + stream consumer fills occupancy)
CREATE TABLE IF NOT EXISTS analytics_student_daily (
    day Date,
    faculty LowCardinality(String),
    group_name LowCardinality(String),
    student_id String,
    avg_grade Float64,
    engagement_score Float64
) ENGINE = MergeTree ORDER BY (day, faculty, group_name, student_id);

INSERT INTO analytics_student_daily (day, faculty, group_name, student_id, avg_grade, engagement_score) VALUES ('2025-01-01', 'CS', 'CS-101', 's0001', 88.5, 0.72);
INSERT INTO analytics_student_daily (day, faculty, group_name, student_id, avg_grade, engagement_score) VALUES ('2025-01-01', 'CS', 'CS-101', 's0002', 76.0, 0.55);
INSERT INTO analytics_student_daily (day, faculty, group_name, student_id, avg_grade, engagement_score) VALUES ('2025-01-01', 'CS', 'CS-201', 's0003', 65.5, 0.48);
INSERT INTO analytics_student_daily (day, faculty, group_name, student_id, avg_grade, engagement_score) VALUES ('2025-01-01', 'ENG', 'ENG-205', 's0004', 84.0, 0.81);
INSERT INTO analytics_student_daily (day, faculty, group_name, student_id, avg_grade, engagement_score) VALUES ('2025-01-02', 'CS', 'CS-101', 's0001', 90.0, 0.74);
INSERT INTO analytics_student_daily (day, faculty, group_name, student_id, avg_grade, engagement_score) VALUES ('2025-01-02', 'MATH', 'MATH-110', 's0002', 95.0, 0.60);

CREATE TABLE IF NOT EXISTS campus_occupancy_5m (
    window_start DateTime,
    building_id LowCardinality(String),
    people UInt32
) ENGINE = MergeTree ORDER BY (window_start, building_id);

-- Gold feature table (batch + Feast registration)
CREATE TABLE IF NOT EXISTS gold_student_features (
    student_id String,
    snapshot_date Date,
    avg_grade_30d Float64,
    lms_actions_7d UInt32,
    attendance_ratio_14d Float64
) ENGINE = MergeTree ORDER BY (student_id, snapshot_date);

INSERT INTO gold_student_features (student_id, snapshot_date, avg_grade_30d, lms_actions_7d, attendance_ratio_14d) VALUES ('s0001', '2025-01-20', 89.2, 42, 0.91);
INSERT INTO gold_student_features (student_id, snapshot_date, avg_grade_30d, lms_actions_7d, attendance_ratio_14d) VALUES ('s0002', '2025-01-20', 85.5, 28, 0.78);
INSERT INTO gold_student_features (student_id, snapshot_date, avg_grade_30d, lms_actions_7d, attendance_ratio_14d) VALUES ('s0003', '2025-01-20', 65.8, 12, 0.55);
INSERT INTO gold_student_features (student_id, snapshot_date, avg_grade_30d, lms_actions_7d, attendance_ratio_14d) VALUES ('s0004', '2025-01-20', 84.0, 35, 0.88);
