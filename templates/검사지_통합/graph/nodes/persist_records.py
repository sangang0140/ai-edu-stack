from ..state import PipelineState

def run(state: PipelineState) -> PipelineState:
    state.log_event('persist_records', {'stored': True})
    return state
