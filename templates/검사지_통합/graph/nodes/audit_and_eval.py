from ..state import PipelineState

def run(state: PipelineState) -> PipelineState:
    state.log_event('audit_and_eval', {'collected': True})
    return state
