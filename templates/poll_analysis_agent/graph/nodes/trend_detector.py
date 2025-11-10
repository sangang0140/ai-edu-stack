# -*- coding: utf-8 -*-
"""
trend_detector.py
AI 여론 리포트 자동화 템플릿 - 트렌드 감지 노드 (OpenAI SDK v1.x 대응)
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# === 🔑 OpenAI API Key 로드 ===
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    key_path = Path(__file__).resolve().parents[2] / "config" / "openai_key.txt"
    if key_path.exists():
        openai_api_key = key_path.read_text(encoding="utf-8").strip()

if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY 환경변수가 없거나 openai_key.txt 파일이 없습니다.")

client = OpenAI(api_key=openai_api_key)

# === 📊 데이터 로드 ===
today = datetime.now().strftime("%Y-%m-%d")
base_dir = Path(__file__).resolve().parents[2]
raw_path = base_dir / "data" / "raw" / f"poll_data_{today}.json"
trend_output_path = base_dir / "data" / "processed" / f"trend_summary_{today}.json"

if not raw_path.exists():
    raise FileNotFoundError(f"⚠️ 여론조사 데이터 파일이 없습니다: {raw_path}")

with open(raw_path, "r", encoding="utf-8") as f:
    poll_data = json.load(f)

# === 🧮 트렌드 계산 ===
df = pd.DataFrame(poll_data["results"])
df["change"] = df["approval"] - df["previous"]

trend_up = df[df["change"] > 0]["party"].tolist()
trend_down = df[df["change"] < 0]["party"].tolist()

trend_summary = {
    "date": today,
    "up_parties": trend_up,
    "down_parties": trend_down,
    "major_issue": poll_data.get("major_issue", "N/A"),
}

# === 💬 GPT 요약 ===
prompt = f"""
오늘({today})의 여론조사 트렌드를 요약해 주세요.
상승 정당: {trend_up}
하락 정당: {trend_down}
주요 이슈: {poll_data.get('major_issue', '없음')}
"""

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 정치 여론 데이터를 분석하는 AI 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    summary_text = response.choices[0].message.content.strip()
except Exception as e:
    summary_text = f"⚠️ OpenAI API 호출 실패: {e}"

trend_summary["ai_summary"] = summary_text

# === 💾 결과 저장 ===
trend_output_path.parent.mkdir(parents=True, exist_ok=True)
with open(trend_output_path, "w", encoding="utf-8") as f:
    json.dump(trend_summary, f, ensure_ascii=False, indent=2)

print(f"✅ 트렌드 분석 완료: {trend_output_path}")
print(f"📈 AI 요약: {summary_text}")
