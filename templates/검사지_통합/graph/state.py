# D:\ai-edu-stack\templates\검사지_통합\graph\state.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Union


class PipelineState(BaseModel):
    """
    LangGraph용 전역 상태
    """
    # 학생 데이터는 dict 또는 모델 객체 모두 허용
    student: Union[Dict[str, Any], BaseModel, None] = None
    scores: Dict[str, Any] = {}
    neuro: Dict[str, Any] = {}
    analysis: Dict[str, Any] = {}
    report: Dict[str, Any] = {}
    validated: Dict[str, Any] = {}
    raw_inputs: Dict[str, Any] = {}
    log: List[Dict[str, Any]] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def log_event(self, name: str, payload: Dict[str, Any]):
        self.log.append({"event": name, "data": payload})

    def print_log(self):
        for item in self.log:
            print(f"[{item['event']}] {item['data']}")

