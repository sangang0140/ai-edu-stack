# -*- coding: utf-8 -*-
"""
subtitle_generator.py
AI 앵커 스크립트를 기반으로 유튜브 자막용 텍스트 자동 생성기
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from datetime import datetime

# === 기본 경로 설정 ===
BASE_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
script_path = os.path.join(OUTPUT_DIR, f"youtube_script_{today}.txt")
subtitle_path = os.path.join(OUTPUT_DIR, f"subtitles_{today}.txt")

# === 스크립트 파일 확인 ===
if not os.path.exists(script_path):
    print(f"❌ {script_path} 파일이 없습니다. insight_agent.py를 먼저 실행하세요.")
    exit()

# === 스크립트 로드 ===
with open(script_path, "r", encoding="utf-8") as f:
    text = f.read().strip()

# === 문장 단위 분리 (".", "?", "!" 등 기준)
sentences = re.split(r'(?<=[.!?])\s+', text)
sentences = [s.strip() for s in sentences if s.strip()]

# === 자막 형식 변환 ===
subtitles = []
for i, sentence in enumerate(sentences, 1):
    subtitles.append(f"{i}\n{sentence}\n")

# === 저장 ===
with open(subtitle_path, "w", encoding="utf-8") as f:
    f.write("\n".join(subtitles))

print(f"🎞️ 자막 텍스트 자동 생성 완료 → {subtitle_path}")
print("🗣️ 미리보기 ↓\n")
print("\n".join(subtitles[:10]) + "\n...\n(이하 생략)")
