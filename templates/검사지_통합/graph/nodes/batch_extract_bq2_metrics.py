# -*- coding: utf-8 -*-
"""
batch_extract_bq2_metrics.py
NeuroHarmony BQ2 PDF 다중 추출 및 통합 처리
"""

import fitz
import pandas as pd
import re
from pathlib import Path

def extract_metrics_from_pdf(pdf_path):
    """단일 PDF에서 지표명 + 수치 추출"""
    doc = fitz.open(pdf_path)
    blocks_text = []
    for page in doc:
        blocks = page.get_text("blocks")
        for b in blocks:
            txt = b[4].strip()
            if txt:
                blocks_text.append(txt)
    doc.close()

    # 숫자와 문자 모두 포함된 라인만 필터링
    lines = [line for line in blocks_text if re.search(r"[가-힣A-Za-z]", line) and re.search(r"\d", line)]
    pattern = re.compile(r"([A-Za-z가-힣\s]+)[=:：]?\s*([\d\.]+)")

    metrics = []
    for line in lines:
        matches = pattern.findall(line)
        for m in matches:
            key, val = m[0].strip(), m[1].strip()
            if len(key) > 1 and re.search(r"\d", val):
                metrics.append({"metric": key, "value": val})

    df = pd.DataFrame(metrics).drop_duplicates()
    df["student_name"] = pdf_path.stem.split("_")[1] if "_" in pdf_path.stem else pdf_path.stem
    df["file_name"] = pdf_path.name
    return df


def batch_extract():
    """폴더 내 모든 PDF 처리"""
    neuro_dir = Path("data/raw/neuro")
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(list(neuro_dir.glob("*.pdf")))
    if not pdf_files:
        print("❌ PDF 파일이 감지되지 않았습니다.")
        return

    all_records = []
    for pdf in pdf_files:
        print(f"📘 처리 중: {pdf.name}")
        try:
            df = extract_metrics_from_pdf(pdf)
            if not df.empty:
                all_records.append(df)
        except Exception as e:
            print(f"⚠️ {pdf.name} 처리 중 오류: {e}")

    if all_records:
        neuro_df = pd.concat(all_records, ignore_index=True)
        neuro_df.to_parquet(output_dir / "neuro_df.parquet", index=False)
        neuro_df.to_csv(output_dir / "neuro_df.csv", index=False, encoding="utf-8-sig")
        print("\n✅ 모든 PDF 분석 완료!")
        print(f"총 파일 수: {len(pdf_files)}개")
        print(f"총 추출 행 수: {len(neuro_df)}")
        print(f"저장 위치: {output_dir / 'neuro_df.parquet'}")
        print("\n📊 미리보기:")
        print(neuro_df.head(10).to_string(index=False))
    else:
        print("⚠️ 추출된 데이터가 없습니다.")

if __name__ == "__main__":
    batch_extract()
