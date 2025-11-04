from langgraph.graph import StateGraph, START, END
from ..state import PipelineState
from ..nodes import (
    ingest_inputs,
    validate_schema,
    score_engine,
    neuro_parse,
    ai_teacher_helper,
    generate_report,
)

def run_graph(forms_csv: str, neuro_pdf: str):
    """
    LangGraph 기반 파이프라인 실행 함수
    """
    graph = StateGraph(PipelineState)

    # 노드 등록
    graph.add_node("ingest_inputs", ingest_inputs.run)
    graph.add_node("validate_schema", validate_schema.run)
    graph.add_node("score_engine", score_engine.run)
    graph.add_node("neuro_parse", neuro_parse.run)
    graph.add_node("ai_teacher_helper", ai_teacher_helper.run)
    graph.add_node("generate_report", generate_report.run)

    # 노드 간 연결
    graph.add_edge(START, "ingest_inputs")
    graph.add_edge("ingest_inputs", "validate_schema")
    graph.add_edge("validate_schema", "score_engine")
    graph.add_edge("score_engine", "neuro_parse")
    graph.add_edge("neuro_parse", "ai_teacher_helper")
    graph.add_edge("ai_teacher_helper", "generate_report")
    graph.add_edge("generate_report", END)

    app = graph.compile()

    # 초기 상태 (빈값으로 시작)
    state = PipelineState(
        raw_inputs={"forms_csv": forms_csv, "neuro_pdf": neuro_pdf},
        scores={},
        student={"name": "-", "student_id": "-", "grade": "-"}
    )

    # 그래프 실행
    final_state = app.invoke(state)

    # ✅ 결과 report 안전하게 추출
    report_path = (
        final_state.report
        if hasattr(final_state, "report")
        else final_state.get("report", {})
    )

    print(f"✅ Graph completed. Report: {report_path}")
    return final_state
