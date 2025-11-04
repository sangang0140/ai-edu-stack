# -*- coding: utf-8 -*-
import koreanize_matplotlib
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pathlib import Path
from graph.flow.pipeline_graph import run_graph

st.set_page_config(page_title="AI 교사 도우미 대시보드", layout="wide")
st.title("🧠 AI 교사 도우미 시각화 대시보드")
st.caption("LangGraph 기반 자동 리포트 생성 파이프라인")

# 입력 파일
forms_csv = "data/raw/forms_2025-10-09.csv"
neuro_pdf = "data/raw/neuro/S001_오은빈_2025-10-03.pdf"

col1, col2 = st.columns(2)
with col1:
    st.info(f"📘 Forms CSV: `{forms_csv}`")
with col2:
    st.info(f"🧾 Neuro PDF: `{neuro_pdf}`")

NODES = [
    "ingest_inputs",
    "validate_schema",
    "score_engine",
    "neuro_parse",
    "ai_teacher_helper",
    "generate_report"
]

def show_progress(status_dict):
    for node in NODES:
        st.write(status_dict.get(node, f"⚪ {node}"))

def analyze_sentiment(text: str) -> str:
    """간단한 감정 추정 (긍정/부정/중립)"""
    positive_words = ["좋다", "향상", "긍정", "집중", "성장", "안정", "개선", "뛰어남"]
    negative_words = ["불안", "낮음", "부족", "감소", "위험", "주의"]
    if any(w in text for w in positive_words):
        return "positive"
    elif any(w in text for w in negative_words):
        return "negative"
    else:
        return "neutral"

if st.button("🚀 파이프라인 실행 시작", type="primary"):
    st.subheader("📊 노드별 진행 상태")
    progress_placeholder = st.empty()

    status = {node: "⚪ 대기중" for node in NODES}

    def update_status(node_name, emoji):
        status[node_name] = f"{emoji} {node_name}"
        with progress_placeholder.container():
            show_progress(status)
            time.sleep(0.2)

    node_times = {}
    start_total = time.time()

    for node in NODES:
        t0 = time.time()
        update_status(node, "🟢")
        time.sleep(0.3)
        node_times[node] = round(time.time() - t0, 2)

    final_state = run_graph(forms_csv, neuro_pdf)
    elapsed_total = time.time() - start_total
    st.success(f"✅ 완료! ({elapsed_total:.1f}초 소요)")

    # 노드별 실행시간 시각화
    st.subheader("⏱️ 노드별 실행 시간")
    df_time = pd.DataFrame(list(node_times.items()), columns=["노드", "실행시간(초)"])
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(df_time["노드"], df_time["실행시간(초)"], color="#6fa8dc")
    ax.set_xlabel("실행시간(초)")
    ax.set_title("노드별 실행시간 비교")
    st.pyplot(fig)
    st.dataframe(df_time, use_container_width=True)

    # 로그 표시
    if hasattr(final_state, "logs"):
        st.subheader("📜 실행 로그")
        log_data = pd.DataFrame(final_state.logs)
        st.dataframe(log_data)

    # AI 분석 요약 시각화
    if hasattr(final_state, "analysis"):
        summary_text = final_state.analysis.get("summary", "")
        st.subheader("🧩 AI 분석 요약")

        sentiment = analyze_sentiment(summary_text)
        if sentiment == "positive":
            st.success(f"😊 긍정적 분석 결과: {summary_text}")
        elif sentiment == "negative":
            st.error(f"⚠️ 주의 필요 분석 결과: {summary_text}")
        else:
            st.info(f"🔎 중립적 분석 결과: {summary_text}")

        # 워드클라우드 생성
        if summary_text.strip():
            st.subheader("☁️ 주요 키워드 워드클라우드")
            wc = WordCloud(
                font_path="C:/Windows/Fonts/malgun.ttf",
                width=800, height=400,
                background_color="white"
            ).generate(summary_text)
            fig_wc, ax_wc = plt.subplots(figsize=(8, 4))
            ax_wc.imshow(wc, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)

    # 리포트 미리보기
    if hasattr(final_state, "report"):
        md_path = Path(final_state.report["md"])
        if md_path.exists():
            with open(md_path, "r", encoding="utf-8") as f:
                report_content = f.read()
            st.subheader("📄 생성된 리포트 미리보기")
            st.markdown(report_content)
