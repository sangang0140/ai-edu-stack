# D:\ai-edu-stack\templates\검사지_통합\graph\nodes\ai_teacher_helper.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from ..state import PipelineState

# -------------------------------------------------------------
# AI 교사 도우미 노드 (3단 구조 해석)
# -------------------------------------------------------------
def run(state: PipelineState) -> PipelineState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)

    neuro = state.neuro or {}
    student = state.student or {}

    # 학생 기본 정보
    name = student.get("name", "학생")
    grade = student.get("grade", "N/A")

    # 뇌파 주요 지표
    theta = neuro.get("theta_rel_open")
    smr = neuro.get("smr_rel_open")
    betaL = neuro.get("betaL_rel_open")
    betaH = neuro.get("betaH_rel_open")

    # 요약용 입력 텍스트
    input_text = f"""
    학생 이름: {name}
    학년: {grade}
    측정된 주요 뇌파 상대세기:
    - Theta: {theta}
    - SMR: {smr}
    - BetaL: {betaL}
    - BetaH: {betaH}

    위 데이터를 기반으로,
    ① 핵심 요약(집중력/정서/습관)  
    ② 훈련 포인트(실행 가능한 루틴)  
    ③ 격려 문장(따뜻한 멘트)  
    3단 구성으로 분석해 주세요.
    분석 결과는 문단 구분을 명확히 해주세요.
    """

    # AI 해석 생성
    response = llm.invoke([HumanMessage(content=input_text)])
    summary = response.content.strip()


    # 상태 업데이트
    state.analysis = {"summary": summary}
    state.log_event("ai_teacher_helper", {"summary": summary[:120] + "..."})  # ✅ summary로 수정
    return state

