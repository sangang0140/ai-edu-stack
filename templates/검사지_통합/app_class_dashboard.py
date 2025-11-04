# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from pathlib import Path
from graph.flow.pipeline_graph import run_graph

# === 페이지 설정 ===
st.set_page_config(page_title="AI 교사 도우미 - 반 전체 대시보드", layout="wide")
st.title("🏫 반 전체 리포트 시각화 대시보드")
st.caption("LangGraph 기반 다중 학생 PDF 통합 분석")

# === 입력 파일 경로 ===
forms_csv = "data/raw/forms_2025-10-09.csv"
neuro_dir = Path("data/raw/neuro")
pdf_files = sorted(list(neuro_dir.glob("*.pdf")))

st.info(f"📘 Forms CSV: `{forms_csv}`")
st.write(f"🧾 감지된 PDF 파일 수: {len(pdf_files)}")

# === 실행 버튼 ===
if st.button("🚀 반 전체 리포트 생성 시작", type="primary"):
    results = []
    progress = st.progress(0)
    total = len(pdf_files)
    start_time = time.time()

    # --- 여러 학생 파일 순회 ---
    for idx, pdf_path in enumerate(pdf_files, 1):
        st.write(f"처리중: {pdf_path.name}")
        try:
            state = run_graph(forms_csv, str(pdf_path))

            # 안전 접근 함수 정의
            def _safe_get(obj, key, default=None):
                """dict 또는 객체 모두 안전하게 접근"""
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            # LangGraph 반환형에 관계없이 안전 접근
            report = _safe_get(state, "report", {})
            neuro = _safe_get(state, "neuro", {})
            analysis = _safe_get(state, "analysis", {})
            student = _safe_get(state, "student", {})

            sid = _safe_get(student, "student_id", "?")
            name = _safe_get(student, "name", pdf_path.stem)
            grade = _safe_get(student, "grade", "-")
            report_path = _safe_get(report, "md", None)
            analysis_text = _safe_get(analysis, "summary", "")

            theta = _safe_get(neuro, "theta_rel_open", 0)
            betaL = _safe_get(neuro, "betaL_rel_open", 0)
            betaH = _safe_get(neuro, "betaH_rel_open", 0)
            smr = _safe_get(neuro, "smr_rel_open", 0)

            results.append({
                "ID": sid,
                "이름": name,
                "학년": grade,
                "Theta": theta,
                "BetaL": betaL,
                "BetaH": betaH,
                "SMR": smr,
                "AI 요약": analysis_text or "(요약 없음)",
                "리포트": report_path or ""
            })

        except Exception as e:
            results.append({
                "ID": "에러",
                "이름": pdf_path.name,
                "학년": "-",
                "AI 요약": str(e)
            })

        progress.progress(idx / total)

    st.success(f"✅ 완료! {len(results)}명 분석 완료 (총 {time.time()-start_time:.1f}초)")

    # === 결과 테이블 ===
    df = pd.DataFrame(results)
    st.subheader("📋 학생별 요약표")
    st.dataframe(df, use_container_width=True)

    # === 뇌파 시각화 ===
    st.subheader("📈 주요 뇌파 지표 비교 (Theta, BetaL, BetaH, SMR)")

    import matplotlib.font_manager as fm
    plt.rcParams["font.family"] = "Malgun Gothic"   # 윈도우 한글 폰트
    plt.rcParams["axes.unicode_minus"] = False      # 음수 기호 깨짐 방지

    fig, ax = plt.subplots(figsize=(8, 4))
    for col in ["Theta", "BetaL", "BetaH", "SMR"]:
        if col not in df.columns:
            df[col] = 0
    df_plot = df[["이름", "Theta", "BetaL", "BetaH", "SMR"]].set_index("이름").fillna(0)
    df_plot.plot(kind="bar", ax=ax)
    ax.set_ylabel("상대 비율")
    ax.set_title("학생별 뇌파 비율 비교")
    st.pyplot(fig)

    # === AI 교사 요약 ===
    st.subheader("🧠 AI 교사 도우미 요약 비교")
    for _, row in df.iterrows():
        st.markdown(f"**{row['이름']}**: {row['AI 요약']}")

    # === 리포트 미리보기 ===
    st.subheader("📄 리포트 파일 보기")
    selected = st.selectbox("학생 선택", df["이름"])
    sel_row = df[df["이름"] == selected].iloc[0]

    report_path = sel_row.get("리포트", "")
    if report_path and Path(report_path).exists():
        with open(report_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning(f"⚠️ {selected} 학생의 리포트 파일이 존재하지 않습니다.")
