# -*- coding: utf-8 -*-
"""
normalize_metrics.py
NeuroHarmony BQ2 PDF 추출 결과(metric, value) 표준화 처리
"""

import pandas as pd
import yaml
from pathlib import Path

def normalize_metrics(input_path="data/processed/neuro_df.csv",
                      yaml_path="graph/metric_map.yaml",
                      output_path="data/processed/neuro_normalized.parquet"):
    # === YAML 로드 ===
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    metric_map = config.get("metric_map", {})

    # === 데이터 로드 ===
    df = pd.read_csv(input_path)
    print(f"📄 원본 데이터 로드 완료: {len(df)}행")

    # === metric 표준화 ===
    df["normalized_metric"] = df["metric"].map(metric_map).fillna(df["metric"])

    # === value 타입 변환 ===
    def convert_value(v):
        try:
            # 날짜형은 그대로 둠
            if any(x in str(v) for x in [".", ":", "-"]) and not str(v).replace(".", "", 1).isdigit():
                return str(v)
            return float(str(v).replace(",", "").strip())
        except:
            return str(v)
    df["value_clean"] = df["value"].apply(convert_value)

    # === 컬럼 정리 ===
    df = df[["student_name", "normalized_metric", "value_clean", "file_name"]]
    df.rename(columns={
        "normalized_metric": "metric",
        "value_clean": "value"
    }, inplace=True)

    # === 저장 ===
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    # value 컬럼 문자열로 통일 후 저장
    df["value"] = df["value"].astype(str)

    df.to_parquet(output_path, index=False)
    df.to_csv(output_path.replace(".parquet", ".csv"), index=False, encoding="utf-8-sig")


    print("\n✅ 표준화 완료!")
    print(f"총 {len(df)}행 → 저장 위치: {output_path}")
    print("\n📊 미리보기:")
    print(df.head(10).to_string(index=False))
    return df

if __name__ == "__main__":
    normalize_metrics()
