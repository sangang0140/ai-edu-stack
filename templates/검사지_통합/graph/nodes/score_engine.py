import pandas as pd
from ..state import PipelineState

def run(state: PipelineState) -> PipelineState:
    forms_csv = state.raw_inputs.get("forms_csv")
    df = pd.read_csv(forms_csv, sep=None, engine="python", encoding="utf-8-sig") if forms_csv else pd.DataFrame()

    sid = None
    neuro_pdf = state.raw_inputs.get("neuro_pdf")
    if neuro_pdf:
        # 예: data/raw/neuro\S001_홍길동_2025-09-01.pdf → "S001"
        sid = str(neuro_pdf).split("\\")[-1].split("_")[0].upper()

    # 매칭 행 찾기
    if sid and not df.empty:
        row = df[df["student_id"].str.upper() == sid]
        if not row.empty:
            student_data = row.iloc[0].to_dict()
            # ✅ LangGraph는 dict 형태로 저장해야 함 (Pydantic 모델 금지)
            state.student = {**student_data}
            state.log_event("score_engine", {"matched_student": student_data})
        else:
            state.student = {"student_id": sid, "name": "-", "grade": "-"}
    else:
        state.student = {"student_id": sid or "Unknown", "name": "-", "grade": "-"}

    return state
