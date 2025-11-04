# -*- coding: utf-8 -*-
from pathlib import Path
import re
import pandas as pd
from pydantic import BaseModel  # ✅ 함수 바깥으로 이동
from ..state import PipelineState


class _Student(BaseModel):  # ✅ 함수 바깥 (맨 왼쪽 정렬)
    student_id: str
    name: str
    grade: str


REQUIRED_COLUMNS = ['student_id', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5']


def _read_csv_any(path: str) -> pd.DataFrame:
    enc_candidates = ["utf-8", "utf-8-sig", "cp949", "euc-kr"]
    for enc in enc_candidates:
        try:
            return pd.read_csv(path, sep=None, engine="python", encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, sep=None, engine="python", encoding="latin1")


def _extract_sid_and_name_from_filename(pdf_path: str):
    p = Path(pdf_path)
    stem = p.stem
    m_sid = re.search(r"(S\d{3,4})", stem, re.I)
    sid = m_sid.group(1).upper() if m_sid else None
    name = None
    parts = stem.split("_")
    if len(parts) >= 2:
        cand = parts[1]
        m_name = re.search(r"[가-힣]{2,}", cand)
        if m_name:
            name = m_name.group(0)
    return sid, name


def run(state: PipelineState) -> PipelineState:
    forms_csv = state.raw_inputs.get('forms_csv')
    pdf_path = state.raw_inputs.get('neuro_pdf', '')
    schema_ok, anomalies = True, []

    if not forms_csv:
        state.validated = {'schema_ok': False, 'anomalies': [{'error': 'no_forms_csv'}]}
        state.log_event('validate_schema', state.validated)
        return state

    try:
        df = _read_csv_any(forms_csv)
    except Exception as e:
        state.validated = {'schema_ok': False, 'anomalies': [{'csv_read_error': str(e)}]}
        state.log_event('validate_schema', state.validated)
        return state

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        schema_ok = False
        anomalies.append({'missing_columns': missing})

    sid, name_from_file = _extract_sid_and_name_from_filename(pdf_path)
    df_sel = pd.DataFrame()

    if sid and 'student_id' in df.columns:
        df_sel = df[df['student_id'].astype(str).str.upper() == sid]
        if not df_sel.empty:
            df = df_sel.copy()

    if not df_sel.empty:
        rec = df.iloc[0].to_dict()
        student_id = str(sid or rec.get('student_id') or '-')
        student_name = rec.get('student_name') or rec.get('name') or name_from_file or '-'
        student_grade = rec.get('grade') or rec.get('학년') or '-'
    else:
        student_id = str(sid or '-')
        student_name = name_from_file or '-'
        student_grade = '-'
        anomalies.append({'no_csv_row_for': student_id})

    # ✅ 핵심: Pydantic 객체 생성 후 dict 변환
    student = _Student(student_id=student_id, name=student_name, grade=student_grade)
    state.student = student.dict()

    state.raw_inputs['forms_row'] = df.iloc[0].to_dict() if len(df) else {}

    state.validated = {
        'schema_ok': schema_ok,
        'anomalies': anomalies,
        'rows_after_filter': int(len(df)),
        'sid_selected': sid
    }
    state.log_event('validate_schema', state.validated)
    return state
