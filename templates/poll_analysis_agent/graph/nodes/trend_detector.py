# -*- coding: utf-8 -*-
"""
trend_detector.py
여론 변동 추세 및 주요 원인 분석 (더불어민주당 / 국민의힘 기준)
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import pandas as pd
from datetime import datetime, timedelta
import openai

# === OpenAI Key 불러오기 ===
key_path = r"D:\ai-edu-stack\templates\poll_analysis_agent\config\openai_key.txt"
with open(key_path, "r", encoding="utf-8") as f:
    openai.api_key = f.read().strip()

# === 경로 설정 ===
BASE_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent"
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === 최근 4회 여론조사 불러오기 ===
files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith("poll_data_")])
if len(files) < 2:
    print("📉 비교할 데이터가 충분하지 않습니다.")
    exit()

# 최근 두 개 파일만 비교
recent_files = files[-2:]
data = []
for f in recent_files:
    with open(os.path.join(DATA_DIR, f), "r", encoding="utf-8") as file:
        data.append(json.load(file))

# === DataFrame 변환 ===
df = pd.DataFrame(data)

# === 여론 변동 계산 ===
party_delta = {
    "더불어민주당": round(df["party"].iloc[-1]["더불어민주당"] - df["party"].iloc[-2]["더불어민주당"], 2),
    "국민의힘": round(df["party"].iloc[-1]["국민의힘"] - df["party"].iloc[-2]["국민의힘"], 2)
}
president_delta = round(df["president"].iloc[-1]["approval"] - df["president"].iloc[-2]["approval"], 2)

# === 분석 프롬프트 작성 ===
prompt = f"""
최근 여론조사 데이터를 분석해 주세요.

- 대통령 지지율 변동: {president_delta:+}%
- 더불어민주당 변동: {party_delta["더불어민주당"]:+}%
- 국민의힘 변동: {party_delta["국민의힘"]:+}%

이 수치를 기반으로, 정치적 맥락(정책, 사회 이슈, 감성 변화 등)을 고려한 
요약 분석을 한국어로 5~7문장 이내로 작성해 주세요.
"""

# === GPT

# === GPT 분석 요청 ===
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 정치 여론 분석가이다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=600
    )
    summary = response["choices"][0]["message"]["content"].strip()
except Exception as e:
    summary = f"🧠 [GPT 분석 오류]\n{str(e)}"

# === 결과 저장 ===
today = datetime.now().strftime("%Y-%m-%d")
trend_summary = {
    "date": today,
    "president_diff": president_delta,
    "party_diff": party_delta,
    "analysis": summary
}

save_path = os.path.join(OUTPUT_DIR, f"trend_summary_{today}.json")

# ✅ 한글 깨짐 방지용 (Windows PowerShell 완벽 대응)
with open(save_path, "w", encoding="utf-8-sig") as f:
    json.dump(trend_summary, f, ensure_ascii=False, indent=2)

print(f"📊 트렌드 및 인사이트 분석 완료 ({today})")
print(summary)
print(f"✅ 저장 완료: {save_path}")

