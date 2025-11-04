# -*- coding: utf-8 -*-
"""
report_generator_v1_1.py
────────────────────────
AI 여론 자동 분석 (v1.1)
4단계: PDF 리포트 자동 생성
"""

import os, json
from pathlib import Path
from fpdf import FPDF

# === 경로 설정 ===
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"

CONTEXT_FILE = DATA_DIR / "news_context" / "2025-11-04_context.json"
SCRIPT_FILE = DATA_DIR / "script" / "2025-11-04_summary.txt"
REPORT_DIR = DATA_DIR / "report"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = Path(r"C:\Users\sanga\Documents\NotoSansKR-Regular.ttf")

# === 데이터 로드 ===
context = json.load(open(CONTEXT_FILE, "r", encoding="utf-8"))
script_text = open(SCRIPT_FILE, "r", encoding="utf-8").read()

sent = context["sentiment"]
keywords = ", ".join(context["top_keywords"])
articles = context["representative_articles"]

# === PDF 클래스 ===
class PDFReport(FPDF):
    def header(self):
        self.set_font("Noto", size=16)
        self.cell(0, 10, "AI 여론 자동 분석 리포트", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font("Noto", size=9)
        self.multi_cell(0, 6, "※ 본 보고서는 NewsAPI 공개 데이터를 기반으로 AI가 자동 생성한 요약 리포트입니다.", align="C")

# === PDF 생성 ===
pdf = PDFReport(format="A4")
pdf.add_font("Noto", "", str(FONT_PATH), uni=True)
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# 제목
pdf.set_font("Noto", size=14)
pdf.cell(0, 10, f"📅 분석 날짜: {context['date']}", ln=True)

# 감성 요약
pdf.set_font("Noto", size=12)
pdf.multi_cell(0, 8, f"🧠 감성 분석 결과\n긍정: {sent['positive']}건 / 부정: {sent['negative']}건 / 중립: {sent['neutral']}건\n")

# 키워드
pdf.multi_cell(0, 8, f"🔍 주요 키워드: {keywords}\n")

# 대표 기사
pdf.set_font("Noto", size=12)
pdf.cell(0, 8, "🗞️ 대표 기사 Top 3:", ln=True)
for a in articles:
    pdf.set_font("Noto", size=11)
    pdf.multi_cell(0, 6, f"• {a['title']} ({a['source']})\n  {a['url']}\n")

pdf.ln(5)

# AI 해설 스크립트
pdf.set_font("Noto", size=12)
pdf.multi_cell(0, 8, "🎙️ AI 앵커 스크립트\n", align="L")
pdf.set_font("Noto", size=11)
pdf.multi_cell(0, 7, script_text, align="L")

# 저장
output_path = REPORT_DIR / f"{context['date']}_AI_여론리포트.pdf"
pdf.output(str(output_path))
print(f"📘 PDF 리포트 생성 완료 → {output_path}")
