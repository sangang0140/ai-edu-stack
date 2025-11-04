# -*- coding: utf-8 -*-
"""
poll_collector.py
여론조사 데이터 수집 (더불어민주당 / 국민의힘 중심)
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from datetime import datetime

# === 경로 설정 ===
BASE_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent"
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")

# === 여론조사 더미 데이터 (임시 예시) ===
poll_data = {
    "date": today,
    "source": "Realmeter" if datetime.now().weekday() == 0 else "Gallup",
    "president": {
        "approval": 42.5,
        "disapproval": 51.0
    },
    "party": {
        "더불어민주당": 38.4,
        "국민의힘": 32.7
    }
}

# === 저장 ===
save_path = os.path.join(DATA_DIR, f"poll_data_{today}.json")

with open(save_path, "w", encoding="utf-8") as f:
    json.dump(poll_data, f, ensure_ascii=False, indent=2)

print(f"✅ 여론조사 데이터 생성 완료: {save_path}")
