# -*- coding: utf-8 -*-
"""
insight_agent.py
AI 여론 리포트 자동화 템플릿 - 인사이트 분석 노드 (OpenAI SDK v1.x 대응)
"""

import os
import json
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

# === 📄 트렌드 요약 불러오기 ===
today = datetime.now().strftime("%Y-%m-%d")
base_dir = Path(__file__).resolve().parents[2]
trend_path = base_dir / "data" / "processed" / f"trend_summary_{today}.json"
insight_output_path = base_dir / "data" / "processed" / f"insight_summary_{today}.json"

if not trend_path.exists():
    raise FileNotFoundError(f"⚠️ 트렌드 요약 파일이 없습니다: {trend_path}")

with open(trend_path, "r", encoding="utf-8") as f:
    trend_summary = json.load(f)

# === 💬 GPT 인사이트 생성 ===
prompt = f"""
다음은 오늘({today})의 여론조사 트렌드입니다.

상승 정당: {trend_summary['up_parties']}
하락 정당: {trend_summary['down_parties']}
주요 이슈: {trend_summary['major_issue']}

이 내용을 기반으로,
- 여론의 방향성
- 정책적 함의
- 사회적 의미
를 중심으로 5문장 내외로 요약해 주세요.
"""

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 정치사회 트렌드 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    insight_text = response.choices[0].message.content.strip()
except Exception as e:
    insight_text = f"⚠️ OpenAI API 호출 실패: {e}"

# === 💾 저장 ===
insight_data = {
    "date": today,
    "insight": insight_text
}

insight_output_path.parent.mkdir(parents=True, exist_ok=True)
with open(insight_output_path, "w", encoding="utf-8") as f:
    json.dump(insight_data, f, ensure_ascii=False, indent=2)

print(f"✅ 인사이트 분석 완료: {insight_output_path}")
print(f"💡 요약 내용: {insight_text}")
