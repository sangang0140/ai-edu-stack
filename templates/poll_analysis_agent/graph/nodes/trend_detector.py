# -*- coding: utf-8 -*-
"""
trend_detector.py
AI 여론 리포트 자동화 템플릿 - 여론 변동 추세 및 주요 원인 분석
(로컬 실행 + GitHub Actions 환경 모두 호환)
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime
import openai
from pathlib import Path

# === 🧩 한글 출력 설정 (Windows PowerShell 대응) ===
sys.stdout.reconfigure(encoding='utf-8')

# === 🔑 OpenAI API Key 불러오기 (GitHub Secrets > 로컬 파일 순서) ===
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    key_path = Path(__file__).resolve().parents[2] / "config" / "openai_key.txt"
    if key_path.exists():
        with open(key_path, "r", encoding="utf-8") as f:
            openai_api_key = f.read().strip()
    else:
        raise ValueError("❌ OpenAI API Key를 찾을 수 없습니다. 환경변수 또는 openai_key.txt를 확인하세요.")

openai.api_key = openai_api_key
print("✅ OpenAI API Key 로드 완료")

# === 📁 경로 설정 (로컬 & GitHub Actions 호환) ===
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === 🗂️ 최근 여론조사 파일 2개 로드 ===
files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith("poll_data_")])
if len(files) < 2:
    print("📉 비교할 데이터가 충분하지 않습니다.")
    sys.exit(0)

recent_files = files[-2:]
data = []
for f in recent_files:
    with open(DATA_DIR / f, "r", encoding="utf-8") as file:
        data.append(json.load(file))

# === 📊 DataFrame 변환 ===
df = pd.DataFrame(data)

# === 📈 여론 변동 계산 ===
try:
    party_delta = {
        "더불어민주당": round(df["party"].iloc[-1]["더불어민주당"] - df["party"].iloc[-2]["더불어민주당"], 2),
        "국민의힘": round(df["party"].iloc[-1]["국민의힘"] - df["party"].iloc[-2]["국민의힘"], 2)
    }
    president_delta = round(df["president"].iloc[-1]["approval"] - df["president"].iloc[-2]["approval"], 2)
except Exception as e:
    print(f"⚠️ 데이터 구조 오류: {e}")
    sys.exit(1)

# === 💬 GPT 프롬프트 작성 ===
today = datetime.now().strftime("%Y-%m-%d")
prompt = f"""
최근 여론조사 데이터를 분석해 주세요.

- 대통령 지지율 변동: {president_delta:+}%
- 더불어민주당 변동: {party_delta["더불어민주당"]:+}%
- 국민의힘 변동: {party_delta["국민의힘"]:+}%

이 수치를 기반으로 정치적 맥락(정책, 사회 이슈, 감성 변화 등)을 고려하여
5~7문장 내외의 한국어 분석 요약을 작성해 주세요.
"""

# === 🧠 GPT 분석 요청 ===
try:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 정치 여론 데이터를 분석하는 AI 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=600
    )
    summary = response["choices"][0]["message"]["content"].strip()
except Exception as e:
    summary = f"⚠️ [GPT 분석 오류]\n{str(e)}"

# === 💾 결과 저장 ===
trend_summary = {
    "date": today,
    "president_diff": president_delta,
    "party_diff": party_delta,
    "analysis": summary
}

save_path = OUTPUT_DIR / f"trend_summary_{today}.json"
with open(save_path, "w", encoding="utf-8-sig") as f:
    json.dump(trend_summary, f, ensure_ascii=False, indent=2)

# === 🧾 출력 ===
print(f"📊 트렌드 및 인사이트 분석 완료 ({today})")
print(summary)
print(f"✅ 저장 완료: {save_path}")
