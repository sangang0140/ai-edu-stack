from pathlib import Path
from typing import Dict, Any
from ..state import PipelineState

DATA_RAW = Path(__file__).resolve().parents[2] / 'data' / 'raw'
DATA_RAW.mkdir(parents=True, exist_ok=True)

def run(state: PipelineState) -> PipelineState:
    # raw_inputs에 forms_csv와 neuro_pdf가 이미 포함되어 있음
    payload = state.raw_inputs or {}
    state.log_event("ingest_inputs", {"keys": list(payload.keys())})
    return state

