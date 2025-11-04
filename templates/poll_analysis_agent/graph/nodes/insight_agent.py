# -*- coding: utf-8 -*-
"""
insight_agent.py
AI 여론 해설 스크립트 자동 생성기 (뉴스 앵커 스타일)
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from datetime import datetime
import openai

# === OpenAI Key 불러오기 ===
key_path = r"D:\ai-edu-stack\templates\poll_analysis_agent\config\openai_key.txt"
with open(key_path, "r", encoding="utf-8") as f:
    openai.api_key = f.read().strip()

# === 경로 설정 ===
BASE_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
trend_path = os.path.join(OUTPUT_DIR, f"trend_summary_{today}.json")
script_path = os.path.join(OUTPUT_DIR, f"youtube_script_{today}.txt")

# === 입력 데이터 확인 ===
if not os.path.exists(trend_path):
    print(f"❌ {trend_path} 파일이 없습니다. trend_detector.py를 먼저 실행하세요.")
    exit()

# === 트렌드 요약 불러오기 ===
with open(trend_path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

president_diff = data["president_diff"]
democrat_diff = data["party_diff"]["더불어민주당"]
power_diff = data["party_diff"]["국민의힘"]
analysis = data["analysis"]

# === 프롬프트 작성 ===
prompt = f"""
당신은 뉴스 앵커입니다.
다음 데이터를 바탕으로 오늘의 여론 브리핑 원고를 작성하세요.

- 대통령 지지율 변동: {president_diff:+}%
- 더불어민주당 지지율 변동: {democrat_diff:+}%
- 국민의힘 지지율 변동: {power_diff:+}%

요구사항:
1. 톤은 뉴스 앵커의 말투로 하며, '안녕하십니까'로 시작하세요.
2. 청중에게 설명하듯 자연스럽게 전달하세요.
3. 내용은 5~7문장, 한국어로 작성하세요.
4. 마지막에는 “이상, AI Agent Business의 여론 인사이트였습니다.”로 마무리하세요.

참고 분석:
{analysis}
"""

# === GPT 요청 ===
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 방송 뉴스 앵커이다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=700
    )
    anchor_script = response["choices"][0]["message"]["content"].strip()
except Exception as e:
    anchor_script = f"⚠️ AI 생성 오류: {str(e)}"

# === 결과 저장 ===
with open(script_path, "w", encoding="utf-8-sig") as f:
    f.write(anchor_script)

print(f"🎬 유튜브 해설 스크립트 생성 완료: {script_path}\n")
print("🗣️ 미리보기 ↓\n")
print(anchor_script[:800])
