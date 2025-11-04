# -*- coding: utf-8 -*-
"""
news_context_agent_v1_1_part3.py
────────────────────────────────
AI 여론 자동 분석 (v1.1)
3단계: 유튜브 스크립트 및 자막 자동 생성
"""

import os, json
from pathlib import Path
from openai import OpenAI

# === 경로 설정 ===
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"
CONFIG_DIR = BASE_DIR.parent.parent / "config"

CONTEXT_PATH = DATA_DIR / "news_context" / "2025-11-04_context.json"
SCRIPT_DIR = DATA_DIR / "script"
SUBTITLE_DIR = DATA_DIR / "subtitle"

SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
SUBTITLE_DIR.mkdir(parents=True, exist_ok=True)

# === OpenAI Key 로드 ===
key_path = CONFIG_DIR / "openai_key.txt"
if not key_path.exists():
    print(f"❌ OpenAI Key 파일이 없습니다: {key_path}")
    exit()
client = OpenAI(api_key=open(key_path, "r", encoding="utf-8").read().strip())

# === 데이터 로드 ===
context = json.load(open(CONTEXT_PATH, "r", encoding="utf-8"))
sent = context["sentiment"]
keywords = ", ".join(context["top_keywords"])
articles = context["representative_articles"]

# === 1️⃣ 프롬프트 구성 ===
article_lines = "\n".join([
    f"- {a['title']} ({a['source']})" for a in articles
])

prompt = f"""
다음은 {context['date']} 기준 AI가 분석한 주요 뉴스 요약 데이터입니다.
이를 바탕으로 유튜브 영상 해설용 스크립트를 작성해주세요.
조건:
1. 시청자가 이해하기 쉽게 5~7문장으로 요약
2. 따뜻하고 객관적인 AI 앵커 톤
3. 각 문장은 15~25자 정도로 자연스럽게 끝나야 함
4. 마지막에는 한 줄 소감(“AI의 시선에서 본 오늘의 여론”)으로 마무리

감성 비율: 긍정 {sent['positive']}, 부정 {sent['negative']}, 중립 {sent['neutral']}
핵심 키워드: {keywords}
대표 기사:
{article_lines}
"""

# === 2️⃣ AI 스크립트 생성 ===
print("🧠 유튜브 해설 스크립트 생성 중...")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)
script_text = response.choices[0].message.content.strip()

# === 3️⃣ 자막 문장 분리 ===
subtitles = []
for line in script_text.split("."):
    line = line.strip()
    if len(line) > 5:
        subtitles.append(line)

# === 4️⃣ 결과 저장 ===
script_file = SCRIPT_DIR / f"{context['date']}_summary.txt"
subtitle_file = SUBTITLE_DIR / f"{context['date']}_subtitle.txt"

with open(script_file, "w", encoding="utf-8") as f:
    f.write(script_text)

with open(subtitle_file, "w", encoding="utf-8") as f:
    f.write("\n".join(subtitles))

print(f"📜 스크립트 저장 완료 → {script_file}")
print(f"💬 자막 텍스트 저장 완료 → {subtitle_file}")
