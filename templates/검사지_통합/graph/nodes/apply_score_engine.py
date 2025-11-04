# -*- coding: utf-8 -*-
"""
apply_score_engine.py
기초형 NeuroHarmony BQ2 계산 엔진 (ver.0.1)
"""

import pandas as pd
import yaml
import numpy as np
from pathlib import Path

def apply_score_engine(input_path="data/processed/neuro_normalized.csv",
                       yaml_path="graph/score_engine.yaml",
                       output_path="data/processed/neuro_scored.csv"):
    # === YAML 로드 ===
    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    engine = cfg.get("score_engine", {})

    # === 데이터 로드 ===
    df = pd.read_csv(input_path)
    print(f"📄 표준화된 데이터 로드 완료: {len(df)}행")

    # === numeric 변환 (가능한 항목만) ===
    df["value_num"] = pd.to_numeric(df["value"], errors="coerce")

    # === 학생별로 피벗 (metric → column) ===
    pivot_df = df.pivot_table(index="student_name", 
                              columns="metric", 
                              values="value_num", 
                              aggfunc=lambda x: np.nanmean(x))
    pivot_df.reset_index(inplace=True)

    # === 계산식 적용 ===
    for col, expr in engine.items():
        try:
            if "mean(" in expr:
                target = expr.split("(")[1].split(")")[0]
                # mean 처리: target 컬럼 내 평균 (학생별 단일 컬럼이라 그대로 사용)
                pivot_df[col] = pivot_df[target]
            elif "sum(" in expr:
                target = expr.split("(")[1].split(")")[0]
                # sum 처리: 동일한 metric이 여러 번 등장했을 때 대비
                pivot_df[col] = df[df["metric"] == target].groupby("student_name")["value_num"].sum().values
            else:
                pivot_df[col] = pivot_df.eval(expr)
        except Exception as e:
            print(f"⚠️ {col} 계산 실패: {e}")



    # === 결과 저장 ===
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pivot_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("\n✅ 스코어 엔진 계산 완료!")
    print(f"저장 위치: {output_path}")
    print("\n📊 미리보기:")
    print(pivot_df.head(10).to_string(index=False))
    return pivot_df

if __name__ == "__main__":
    apply_score_engine()
