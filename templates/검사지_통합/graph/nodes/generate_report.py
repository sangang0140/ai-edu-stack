# -*- coding: utf-8 -*-
import re
from pathlib import Path
from ..state import PipelineState

# 출력 경로 설정
OUTPUT = Path(__file__).resolve().parents[2] / "outputs" / "reports"
OUTPUT.mkdir(parents=True, exist_ok=True)

def run(state: PipelineState) -> PipelineState:
    print("🟢 [generate_report] 노드 실행 시작")

    # 기본 데이터 추출
    student = state.student or {}
    scores = state.scores.get("values", {})
    flags = state.scores.get("flags", [])
    analysis = getattr(state, "analysis", {}).get("summary", "")

    name = student.get("name", "-")
    sid = student.get("student_id", "-")
    grade = student.get("grade", "-")

    # 안전한 파일명 생성
    # 파일명에서 경로 기호(\, /) 제거
    safe_sid = re.search(r'(S\d{3,4})', str(sid))
    safe_sid = safe_sid.group(1) if safe_sid else Path(str(sid)).stem
    filename = f"report_{safe_sid}.md"
    out_path = OUTPUT / filename


    # 보고서 내용 구성
    md = f"""# 통합 결과 요약

**학생**: {name} ({sid}) | **학년**: {grade}

## 1) 핵심 지표
{scores}

## 2) 리스크 플래그
{flags}

## 3) 해석 요약
{analysis}

## 4) 4주 개입 권고(요약)
- 학부모: 가정에서 10분 대화 + 주 2회 훈련
- 학교: 담임과 주간 점검 루틴
"""

    # 파일 저장
    out_path.write_text(md, encoding="utf-8-sig")
    print(f"🟢 Report saved at: {out_path}")

    # LangGraph에서 상태를 복사해 반환
    new_state = state.copy(update={
        "report": {"md": str(out_path)}
    })
    new_state.log_event("generate_report", {"path": str(out_path)})
    return new_state
