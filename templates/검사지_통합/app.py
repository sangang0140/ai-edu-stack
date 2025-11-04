# ==========================================================
# app.py : LangGraph 기반 실행 진입점
# ==========================================================

from graph.flow.pipeline_graph import run_graph

# ==========================================================
# 메인 실행 블록
# ==========================================================
if __name__ == "__main__":
    # (1) 입력 CSV 경로
    forms_csv = "data/raw/forms_2025-10-09.csv"

    # (2) 분석할 BQ2 PDF 파일 경로
    neuro_pdf = "data/raw/neuro/S001_오은빈_2025-10-03.pdf"

    # (3) LangGraph 기반 파이프라인 실행
    run_graph(forms_csv, neuro_pdf)
