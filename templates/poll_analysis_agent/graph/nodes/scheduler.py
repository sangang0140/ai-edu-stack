# -*- coding: utf-8 -*-
"""
scheduler.py
월요일(Realmeter), 금요일(Gallup) 자동 실행 + 10시 이후 즉시 실행 + 로그 저장
"""

import os
import time
import schedule
from datetime import datetime
import subprocess

BASE_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent"
GRAPH_DIR = os.path.join(BASE_DIR, "graph", "nodes")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log_write(message: str):
    """로그 파일에 기록"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(LOG_DIR, f"auto_run_{today}.txt")
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

def run_all():
    """전체 자동 실행 파이프라인"""
    today = datetime.now().strftime("%Y-%m-%d (%A)")
    log_write(f"\n🗓️ [{today}] 자동 실행 시작\n")

    steps = [
        "poll_collector.py",
        "trend_detector.py",
        "insight_agent.py",
        "report_generator.py",
        "subtitle_generator.py",
        "thumbnail_generator.py",
    ]

    for step in steps:
        script = os.path.join(GRAPH_DIR, step)
        log_write(f"▶ 실행 중: {step}")
        try:
            subprocess.run(["python", script], check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            log_write(f"✅ 완료: {step}")
        except subprocess.CalledProcessError as e:
            log_write(f"❌ 오류: {step}\n{e.stderr}")
        time.sleep(2)

    log_write(f"📂 결과는 {BASE_DIR}\\outputs 폴더에서 확인하세요.")
    log_write(f"✅ 모든 프로세스 완료 ({today})\n")

def monday_task():
    log_write("\n📊 월요일 — Realmeter 데이터 자동 수집 및 분석 중...\n")
    run_all()

def friday_task():
    log_write("\n📊 금요일 — Gallup 데이터 자동 수집 및 분석 중...\n")
    run_all()

# === 스케줄 등록 ===
schedule.every().monday.at("10:00").do(monday_task)
schedule.every().friday.at("10:00").do(friday_task)

# === 즉시 실행 (10시 이후 PowerShell 실행 시 바로 1회) ===
now = datetime.now()
weekday = now.weekday()  # 월=0, 금=4
hour = now.hour

if weekday == 0 and hour >= 10:
    log_write("\n⚡ 월요일 10시 이후 실행 감지 → Realmeter 루틴 즉시 실행\n")
    monday_task()
elif weekday == 4 and hour >= 10:
    log_write("\n⚡ 금요일 10시 이후 실행 감지 → Gallup 루틴 즉시 실행\n")
    friday_task()
else:
    log_write("🕒 월·금 오전 10시 자동 실행 대기 중... (PowerShell 창은 닫지 마세요)\n")

# === 무한 루프: 스케줄 대기 ===
while True:
    schedule.run_pending()
    time.sleep(30)
