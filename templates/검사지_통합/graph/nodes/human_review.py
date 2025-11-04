from ..state import PipelineState

def run(state: PipelineState) -> PipelineState:
    state.log_event('human_review', {'approved': True})
    return state
