# -*- coding: utf-8 -*-
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from fpdf import FPDF
from datetime import datetime

# === 기본 경로 설정 ===
base_dir = r"D:\ai-edu-stack\templates\poll_analysis_agent"
output_dir = os.path.join(base_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")

trend_path = os.path.join(output_dir, f"trend_summary_{today}.json")
script_path = os.path.join(output_dir, f"youtube_script_{today}.txt")
report_path = os.path.join(output_dir, f"poll_report_{today}.pdf")

# === 데이터 로드 ===
def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:  # ← utf-8-sig 로 변경
        return json.load(f)
    return None

trend_data = load_json(trend_path)
if not trend_data:
    print(f"❌ {trend_path} 파일이 없습니다. trend_detector.py를 먼저 실행하세요.")
    exit()

if not os.path.exists(script_path):
    print(f"❌ {script_path} 파일이 없습니다. insight_agent.py를 먼저 실행하세요.")
    exit()

with open(script_path, "r", encoding="utf-8") as f:
    base_script = f.read().strip()

# === 뉴스 앵커 스타일 스크립트 ===
anchor_script = f"""
안녕하십니까, AI Agent Business의 여론 브리핑입니다.

오늘({today}) 발표된 주요 여론조사 결과를 전해드리겠습니다.

{base_script}

이번 결과는 최근 정치·사회적 이슈가 국민 여론에 어떠한 영향을 미쳤는지를 보여주고 있습니다.
향후 여론의 흐름에 주목할 필요가 있습니다.

이상, AI 에이전트가 전하는 오늘의 여론 리포트였습니다.
"""

# === PDF 생성 ===
pdf = FPDF()
pdf.add_page()

font_path = r"C:\Users\sanga\Documents\NanumGothic.ttf"

if not os.path.exists(font_path):
    print(f"⚠️ 폰트 파일을 찾을 수 없습니다: {font_path}")
    print("NanumGothic.ttf 파일을 C:\\Users\\sanga\\Documents 폴더에 복사해 주세요.")
else:
    try:
        pdf.add_font('NanumGothic', '', font_path)
        pdf.set_font('NanumGothic', '', 14)
    except Exception as e:
        print(f"⚠️ 폰트 로드 중 오류 발생: {e}")
        pdf.set_font("Arial", size=14)

    pdf.multi_cell(0, 10, anchor_script)
    pdf.output(report_path)

    print(f"📰 AI 앵커 스타일 리포트 생성 완료 → {report_path}")
    print("🎙️ 미리보기 ↓\n")
    print(anchor_script[:800] + "...\n(이하 생략)")
