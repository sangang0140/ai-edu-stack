# -*- coding: utf-8 -*-
"""
prompt_sync_generator.py
Flux 이미지 & Wan 비디오용 프롬프트 자동 매칭 생성기
"""

import os
import json
from datetime import datetime

# === 경로 설정 ===
BASE_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")

script_path = os.path.join(OUTPUT_DIR, f"youtube_script_{today}.txt")
visual_path = os.path.join(OUTPUT_DIR, f"visual_prompts_{today}.json")
video_path = os.path.join(OUTPUT_DIR, f"video_prompts_{today}.json")
pair_path = os.path.join(OUTPUT_DIR, f"prompt_pairs_{today}.json")

# === 스크립트 불러오기 ===
if not os.path.exists(script_path):
    print(f"❌ {script_path} 파일이 없습니다. insight_agent.py를 먼저 실행하세요.")
    exit()

with open(script_path, "r", encoding="utf-8") as f:
    text = f.read().strip()

# === 장면 분리 ===
segments = [seg.strip() for seg in text.split("\n") if seg.strip()]

# === 프롬프트 자동 생성 ===
visual_prompts = []
video_prompts = []
pairs = []

for i, seg in enumerate(segments, 1):
    scene_name = f"장면{i:02d}"
    
    # Flux용 프롬프트
    flux_prompt = f"{seg}, 16:9, 현실적 조명, 감성적인 색조, 한국 뉴스 스타일, 수채화풍"
    
    # Wan용 프롬프트
    wan_prompt = f"{seg} 내용을 기반으로 5초 길이의 24fps 영상, 카메라가 부드럽게 이동, 현실적 조명, 자연스러운 색감"
    
    visual_prompts.append({"scene": scene_name, "prompt": flux_prompt})
    video_prompts.append({"scene": scene_name, "prompt": wan_prompt})
    pairs.append({
        "scene": scene_name,
        "flux_prompt": flux_prompt,
        "wan_prompt": wan_prompt
    })

# === JSON 저장 ===
with open(visual_path, "w", encoding="utf-8") as f:
    json.dump(visual_prompts, f, ensure_ascii=False, indent=2)

with open(video_path, "w", encoding="utf-8") as f:
    json.dump(video_prompts, f, ensure_ascii=False, indent=2)

with open(pair_path, "w", encoding="utf-8") as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)

print(f"🎨 Flux 이미지 프롬프트 저장 완료 → {visual_path}")
print(f"🎞️ Wan 비디오 프롬프트 저장 완료 → {video_path}")
print(f"🔗 통합 프롬프트 쌍 저장 완료 → {pair_path}")
