# D:\ai-edu-stack\templates\검사지_통합\graph\nodes\extract_bq2_preview.py
import fitz
import pandas as pd
import re
from pathlib import Path

def extract_bq2_preview(pdf_path: str):
    """BQ2 PDF에서 표 형태의 지표와 수치를 추출"""
    doc = fitz.open(pdf_path)
    blocks_text = []
    
    for page in doc:
        blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, ...)
        for b in blocks:
            txt = b[4].strip()
            if txt:
                blocks_text.append(txt)
    doc.close()

    # 숫자와 문자 혼합된 라인만 추출
    lines = [line for line in blocks_text if re.search(r"[가-힣A-Za-z]", line) and re.search(r"\d", line)]

    pattern = re.compile(r"([A-Za-z가-힣\s]+)[=:：]?\s*([\d\.]+)")
    metrics = []
    for line in lines:
        matches = pattern.findall(line)
        for m in matches:
            key = m[0].strip()
            val = m[1].strip()
            if len(key) > 1 and re.search(r"\d", val):
                metrics.append({"metric": key, "value": val})

    df = pd.DataFrame(metrics).drop_duplicates()
    print(f"\n🧠 {pdf_path.name}에서 감지된 주요 지표:")
    print(df.to_string(index=False))
    return df

if __name__ == "__main__":
    neuro_dir = Path("data/raw/neuro")
    pdf_files = sorted(list(neuro_dir.glob("*.pdf")))

    if not pdf_files:
        print("❌ PDF 파일이 감지되지 않았습니다.")
    else:
        sample = pdf_files[0]
        print(f"\n📘 샘플 파일: {sample.name}")
        extract_bq2_preview(sample)
