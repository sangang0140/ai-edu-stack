# -*- coding: utf-8 -*-
"""
thumbnail_generator.py
AI 뉴스 썸네일용 Flux 이미지 프롬프트 자동 생성기 (영문 변환 포함)
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime
import openai

# === 기본 설정 ===
BASE_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
SCRIPT_PATH = os.path.join(OUTPUT_DIR, f"youtube_script_{today}.txt")
PROMPT_KR_PATH = os.path.join(OUTPUT_DIR, f"thumbnail_prompt_kr_{today}.txt")
PROMPT_EN_PATH = os.path.join(OUTPUT_DIR, f"thumbnail_prompt_en_{today}.txt")

key_path = r"D:\ai-edu-stack\templates\poll_analysis_agent\config\openai_key.txt"
with open(key_path, "r", encoding="utf-8") as f:
    openai.api_key = f.read().strip()

# === 스크립트 확인 ===
if not os.path.exists(SCRIPT_PATH):
    print(f"❌ {SCRIPT_PATH} 파일이 없습니다. insight_agent.py를 먼저 실행하세요.")
    exit()

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script_text = f.read().strip()

# === 1️⃣ 한글 Flux 프롬프트 생성 ===
prompt_kr = f"""
다음 뉴스 스크립트를 바탕으로 유튜브 썸네일에 어울리는 Flux 이미지 프롬프트를 한국어로 만들어 주세요.

조건:
- 뉴스의 핵심 감정을 시각적으로 표현
- 인물, 배경, 분위기, 조명, 색감 등을 묘사
- 텍스트는 넣지 마세요
- 16:9 비율, 드라마틱하고 현실적인 조명

뉴스 스크립트:
{script_text}
"""

response_kr = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 AI 이미지 생성용 프롬프트 디자이너입니다."},
        {"role": "user", "content": prompt_kr}
    ]
)

prompt_kr_text = response_kr["choices"][0]["message"]["content"].strip()

# === 2️⃣ 영어로 자연스럽게 번역 (Flux 호환형) ===
prompt_en = f"""
Translate the following Korean image prompt into a natural, descriptive English prompt for Flux text-to-image model.
Keep artistic, cinematic details and 16:9 ratio indication.

Korean prompt:
{prompt_kr_text}
"""

response_en = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a professional AI image prompt translator for diffusion models."},
        {"role": "user", "content": prompt_en}
    ]
)

prompt_en_text = response_en["choices"][0]["message"]["content"].strip()

# === 3️⃣ 파일 저장 ===
with open(PROMPT_KR_PATH, "w", encoding="utf-8") as f:
    f.write(prompt_kr_text)

with open(PROMPT_EN_PATH, "w", encoding="utf-8") as f:
    f.write(prompt_en_text)

print(f"🖼️ 썸네일용 Flux 프롬프트 생성 완료")
print(f"🇰🇷 한국어 버전 → {PROMPT_KR_PATH}")
print(f"🇺🇸 영어 버전 → {PROMPT_EN_PATH}\n")
print("🎨 미리보기 (EN) ↓\n")
print(prompt_en_text)
