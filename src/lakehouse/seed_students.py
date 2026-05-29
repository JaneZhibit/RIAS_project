import random
from datetime import datetime, timedelta

from clickhouse_driver import Client

from src.config import get_settings


def main():
    s = get_settings()
    ch = Client(
        host=s["clickhouse_host"],
        port=int(s["clickhouse_port"]),
        user=s["clickhouse_user"],
        password=s["clickhouse_password"] or None,
    )
    
    faculties = ["CS", "MATH", "ENG", "PHYS", "BIO"]
    groups = {
        "CS": ["CS-101", "CS-102", "CS-201"],
        "MATH": ["MATH-110", "MATH-120"],
        "ENG": ["ENG-205", "ENG-301"],
        "PHYS": ["PHYS-101"],
        "BIO": ["BIO-101", "BIO-102"],
    }
    
    daily_records = []
    gold_records = []
    
    print("Generating student data...")
    # Generate 500 students
    for i in range(1, 501):
        sid = f"s{i:04d}"
        fac = random.choice(faculties)
        grp = random.choice(groups[fac])
        
        base_grade = random.uniform(50, 95)
        base_eng = random.uniform(0.3, 0.95)
        
        # Add to analytics_student_daily (last 30 days)
        for d in range(30):
            day = datetime(2025, 1, 1).date() + timedelta(days=d)
            grade = min(100.0, max(0.0, base_grade + random.uniform(-5, 5)))
            eng = min(1.0, max(0.0, base_eng + random.uniform(-0.1, 0.1)))
            daily_records.append((day, fac, grp, sid, round(grade, 2), round(eng, 2)))
            
        # Add to gold_student_features
        snapshot = datetime(2025, 1, 30).date()
        grade_30d = round(base_grade, 2)
        lms_acts = random.randint(10, 100)
        att_ratio = round(base_eng, 2)
        gold_records.append((sid, snapshot, grade_30d, lms_acts, att_ratio))

    print(f"Inserting {len(daily_records)} daily records...")
    ch.execute("TRUNCATE TABLE IF EXISTS analytics_student_daily")
    ch.execute(
        "INSERT INTO analytics_student_daily (day, faculty, group_name, student_id, avg_grade, engagement_score) VALUES",
        daily_records
    )
    
    print(f"Inserting {len(gold_records)} gold records...")
    ch.execute("TRUNCATE TABLE IF EXISTS gold_student_features")
    ch.execute(
        "INSERT INTO gold_student_features (student_id, snapshot_date, avg_grade_30d, lms_actions_7d, attendance_ratio_14d) VALUES",
        gold_records
    )
    
    print("Done! Restarting Cube.js container is recommended.")

if __name__ == "__main__":
    main()
