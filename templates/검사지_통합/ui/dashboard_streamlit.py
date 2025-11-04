# -*- coding: utf-8 -*-
"""
dashboard_streamlit.py
NeuroHarmony BQ2 결과 요약 대시보드 (표 중심 ver.0.1)
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# === 페이지 설정 ===
st.set_page_config(page_title="🧠 NeuroHarmony 반 전체 요약 대시보드", layout="wide")
st.title("🧠 NeuroHarmony BQ2 결과 요약표")
st.caption("비움과채움 AI교육팀 | 반 전체 데이터 기반 자동 요약 (표 중심 Ver.0.1)")

# === 데이터 로드 ===
data_path = Path("data/processed/neuro_scored.csv")

if not data_path.exists():
    st.error("❌ 분석된 데이터 파일이 없습니다.\n먼저 apply_score_engine.py를 실행해 주세요.")
    st.stop()

df = pd.read_csv(data_path)

# === 요약 통계 ===
st.subheader("📊 반 전체 요약 통계")
summary = df.select_dtypes(include='number').describe().T
summary = summary[["mean", "std", "min", "max"]].rename(
    columns={"mean": "평균", "std": "표준편차", "min": "최소값", "max": "최대값"}
)

# 👩‍🎓 학생별 주요 지표
st.subheader("👩‍🎓 학생별 주요 지표")

# 학생 선택 박스
cols = st.columns(2)
with cols[0]:
    student = st.selectbox("학생 선택", df["student_name"].unique())
with cols[1]:
    st.markdown("")

# 학생 데이터 필터링
student_df = df[df["student_name"] == student]

# 학생 데이터 표시
st.write(f"**{student} 학생 데이터 요약**")

st.dataframe(
    student_df.style.format(
        lambda v: f"{v:.2f}" if isinstance(v, (int, float)) else str(v)
    ),
    use_container_width=True
)

# === 파일 다운로드 ===
st.download_button(
    label="📥 CSV로 다운로드",
    data=df.to_csv(index=False, encoding="utf-8-sig"),
    file_name="neuro_scored_summary.csv",
    mime="text/csv",
)

st.success("✅ 데이터 로드 및 요약 완료!")
