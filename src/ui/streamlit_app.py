"""Embedded analytics UI: Cube.js + drill-down (faculty -> group -> student)."""

from __future__ import annotations

import os

import altair as alt
import pandas as pd
import requests
import streamlit as st

CUBE_URL = os.environ.get("CUBE_API_URL", "http://localhost:4000/cubejs-api/v1").rstrip("/")
SECRET = os.environ.get("CUBEJS_API_SECRET", "")


def cube_load(query: dict) -> pd.DataFrame:
    url = f"{CUBE_URL}/load"
    headers = {}
    if SECRET:
        headers["Authorization"] = SECRET
    r = requests.post(url, json={"query": query}, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json().get("data", [])
    return pd.DataFrame(data)


def pick_col(df: pd.DataFrame, name: str) -> str:
    """Pick Cube column by exact or case-insensitive name."""
    if name in df.columns:
        return name
    lower_map = {c.lower(): c for c in df.columns}
    hit = lower_map.get(name.lower())
    if hit:
        return hit
    # Fallback by suffix, e.g. StudentAnalytics.studentId vs studentid
    suffix = name.split(".")[-1].lower()
    for c in df.columns:
        if c.lower().endswith(suffix):
            return c
    raise KeyError(f"Column not found: {name}; got: {list(df.columns)}")


st.set_page_config(page_title="RIAS Analytics", layout="wide")
st.title("RIAS — встроенная аналитика (Cube.js)")

tab1, tab2 = st.tabs(["Успеваемость (drill-down)", "Занятость кампуса"])

with tab1:
    st.caption("Факультет → группа → студент")
    df_fac = cube_load(
        {
            "measures": ["StudentAnalytics.studentCount", "StudentAnalytics.avgGrade"],
            "dimensions": ["StudentAnalytics.faculty"],
        }
    )
    if df_fac.empty:
        st.warning("Нет данных из Cube.js. Подними compose и ClickHouse.")
    else:
        fac_col = pick_col(df_fac, "StudentAnalytics.faculty")
        faculty_values = sorted(df_fac[fac_col].dropna().astype(str).unique())
        faculty = st.selectbox("Факультет", faculty_values)
        df_grp = cube_load(
            {
                "measures": ["StudentAnalytics.studentCount", "StudentAnalytics.avgGrade"],
                "dimensions": ["StudentAnalytics.faculty", "StudentAnalytics.groupName"],
                "filters": [
                    {
                        "member": "StudentAnalytics.faculty",
                        "operator": "equals",
                        "values": [faculty],
                    }
                ],
            }
        )
        if not df_grp.empty:
            grp_fac_col = pick_col(df_grp, "StudentAnalytics.faculty")
            grp_name_col = pick_col(df_grp, "StudentAnalytics.groupName")
            grp_count_col = pick_col(df_grp, "StudentAnalytics.studentCount")
            grp_grade_col = pick_col(df_grp, "StudentAnalytics.avgGrade")
            df_grp_view = df_grp.rename(
                columns={
                    grp_fac_col: "faculty",
                    grp_name_col: "group",
                    grp_count_col: "students",
                    grp_grade_col: "avg_grade",
                }
            )
            df_grp_view["students"] = pd.to_numeric(df_grp_view["students"], errors="coerce")
            df_grp_view["avg_grade"] = pd.to_numeric(df_grp_view["avg_grade"], errors="coerce")
        else:
            df_grp_view = df_grp
        st.subheader("Группы")
        st.dataframe(df_grp_view, use_container_width=True)
        if not df_grp.empty:
            grp_chart = (
                alt.Chart(df_grp_view)
                .mark_bar()
                .encode(
                    x=alt.X("group:N", title="Группа"),
                    y=alt.Y("avg_grade:Q", title="Средний балл"),
                    color=alt.Color("group:N", legend=None),
                    tooltip=["faculty", "group", "students", "avg_grade"],
                )
                .properties(height=260)
            )
            st.altair_chart(grp_chart, use_container_width=True)
        if not df_grp.empty:
            grp_name_col = pick_col(df_grp, "StudentAnalytics.groupName")
            group = st.selectbox(
                "Группа",
                sorted(df_grp[grp_name_col].dropna().astype(str).unique()),
            )
            df_stu = cube_load(
                {
                    "measures": ["StudentAnalytics.avgGrade", "StudentAnalytics.avgEngagement"],
                    "dimensions": [
                        "StudentAnalytics.faculty",
                        "StudentAnalytics.groupName",
                        "StudentAnalytics.studentId",
                    ],
                    "filters": [
                        {
                            "member": "StudentAnalytics.faculty",
                            "operator": "equals",
                            "values": [faculty],
                        },
                        {
                            "member": "StudentAnalytics.groupName",
                            "operator": "equals",
                            "values": [group],
                        },
                    ],
                }
            )
            st.subheader("Студенты")
            stu_id_col = pick_col(df_stu, "StudentAnalytics.studentId")
            stu_grade_col = pick_col(df_stu, "StudentAnalytics.avgGrade")
            stu_eng_col = pick_col(df_stu, "StudentAnalytics.avgEngagement")
            df_stu_view = df_stu.rename(
                columns={
                    stu_id_col: "student_id",
                    stu_grade_col: "avg_grade",
                    stu_eng_col: "avg_engagement",
                }
            )
            df_stu_view["avg_grade"] = pd.to_numeric(df_stu_view["avg_grade"], errors="coerce")
            df_stu_view["avg_engagement"] = pd.to_numeric(df_stu_view["avg_engagement"], errors="coerce")
            st.dataframe(df_stu_view, use_container_width=True)
            stu_chart = (
                alt.Chart(df_stu_view)
                .mark_bar()
                .encode(
                    x=alt.X("student_id:N", title="Студент"),
                    y=alt.Y("avg_grade:Q", title="Средний балл"),
                    color=alt.Color("avg_grade:Q", title="Балл"),
                    tooltip=["student_id", "avg_grade", "avg_engagement"],
                )
                .properties(height=280)
            )
            st.altair_chart(stu_chart, use_container_width=True)

with tab2:
    st.caption("Агрегаты потока (ClickHouse, обновляется consumer-ом)")
    df_occ = cube_load(
        {
            "measures": ["CampusOccupancy.peopleMax"],
            "dimensions": ["CampusOccupancy.buildingId", "CampusOccupancy.windowStart"],
            "order": [["CampusOccupancy.windowStart", "desc"]],
            "limit": 50,
        }
    )
    if df_occ.empty:
        st.info("Пока нет потоковых данных. Запусти generator + consumer и подожди 20-30 секунд.")
    else:
        occ_time_col = pick_col(df_occ, "CampusOccupancy.windowStart")
        occ_bld_col = pick_col(df_occ, "CampusOccupancy.buildingId")
        occ_people_col = pick_col(df_occ, "CampusOccupancy.peopleMax")
        df_occ_view = df_occ.rename(
            columns={
                occ_time_col: "window_start",
                occ_bld_col: "building",
                occ_people_col: "people",
            }
        )
        df_occ_view["window_start"] = pd.to_datetime(df_occ_view["window_start"], errors="coerce")
        df_occ_view["people"] = pd.to_numeric(df_occ_view["people"], errors="coerce")
        df_occ_view = df_occ_view.dropna(subset=["window_start", "building", "people"]).sort_values(
            "window_start"
        )
        st.dataframe(df_occ_view.tail(100), use_container_width=True)
        occ_chart = (
            alt.Chart(df_occ_view)
            .mark_line(point=True)
            .encode(
                x=alt.X("window_start:T", title="Окно времени"),
                y=alt.Y("people:Q", title="Людей"),
                color=alt.Color("building:N", title="Корпус"),
                tooltip=["window_start", "building", "people"],
            )
            .properties(height=320)
        )
        st.altair_chart(occ_chart, use_container_width=True)
