# -*- coding: utf-8 -*-
"""
generate_reports.py
학생별 NeuroHarmony BQ2 자동 리포트 생성 (ver.0.1)
"""

import pandas as pd
from fpdf import FPDF
from pathlib import Path

def generate_reports(input_path="data/processed/neuro_scored.csv",
                     output_dir="report/pdf"):
    # === 데이터 로드 ===
    df = pd.read_csv(input_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    students = df["student_name"].unique()

    for name in students:
        data = df[df["student_name"] == name].iloc[0]  # 첫 행 기준 요약
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("NotoSansKR", "", r"D:\ai-edu-stack\templates\검사지_통합\NotoSansKR-Regular.ttf")
        pdf.set_font("NotoSansKR", "", 14)

        # 제목
        pdf.set_text_color(30, 136, 229)
        pdf.cell(0, 10, f"NeuroHarmony BQ2 학생 리포트", ln=True, align="C")
        pdf.ln(8)
        pdf.set_text_color(0, 0, 0)

        # 기본 정보
        pdf.set_font("NotoSansKR", "", 12)
        pdf.cell(0, 10, f"학생 이름: {name}", ln=True)
        pdf.ln(4)

        # 주요 수치
        pdf.set_font("NotoSansKR", "", 11)
        fields = [
            "brain_average", "brain_balance", "avg_frequency", "total_power",
            "left_brain", "right_brain", "frequency", "raw_wave_power", "weight"
        ]
        for f in fields:
            if f in data:
                pdf.cell(60, 8, f"{f}", border=0)
                pdf.cell(0, 8, str(round(data[f], 2) if pd.notna(data[f]) else "—"), ln=True)

        # 하단 문구
        pdf.ln(10)
        pdf.set_font("NotoSansKR", "", 10)
        pdf.set_text_color(120)
        pdf.multi_cell(0, 6,
            "※ 본 리포트는 NeuroHarmony BQ2 결과 기반으로 생성되었습니다.\n"
            "비움과채움 AI교육팀 | enfedu.com",
            align="L"
        )

        # 저장
        output_file = Path(output_dir) / f"{name}_리포트.pdf"
        pdf.output(str(output_file))

        print(f"✅ {name} 리포트 생성 완료 → {output_file}")

    print("\n🎉 모든 학생 리포트 생성 완료!")

if __name__ == "__main__":
    generate_reports()
