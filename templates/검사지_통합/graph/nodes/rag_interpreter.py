from ..state import PipelineState

def run(state: PipelineState) -> PipelineState:
    scores = state.scores.get('values', {})
    flags = state.scores.get('flags', [])
    insights = {
        'summary': f"요약: 핵심 지표 {scores}.",
        'risk': flags,
        'guidance': ['학부모 소통 강화','주 2회 집중력 훈련 활동'],
    }
    state.analysis = insights
    state.log_event('rag_interpreter', insights)
    return state
