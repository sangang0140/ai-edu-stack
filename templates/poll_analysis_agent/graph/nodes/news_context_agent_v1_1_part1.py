# -*- coding: utf-8 -*-
"""
news_context_agent_v1_1_part1.py
────────────────────────────────
AI 여론 자동 분석 (v1.1)
1단계: 뉴스 수집 모듈 (파일 방식 API 키 관리)

- config/newsapi_key.txt 에서 NewsAPI 키 자동 읽기
- 여론조사 변동 키워드 기반 뉴스 수집
- 출력: data/news_raw/YYYY-MM-DD_news.json
"""

import os
import json
import datetime
import requests
from pathlib import Path

# === 경로 설정 ===
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR.parent / "config"
DATA_DIR = BASE_DIR.parent.parent / "data" / "news_raw"

DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# === NewsAPI 키 파일 로드 ===
key_path = CONFIG_DIR / "newsapi_key.txt"
if not key_path.exists():
    print(f"❌ API 키 파일이 없습니다: {key_path}")
    print("👉 파일을 생성하고 NewsAPI 키를 한 줄로 입력해주세요.")
    exit()

with open(key_path, "r", encoding="utf-8") as f:
    NEWS_API_KEY = f.read().strip()

if not NEWS_API_KEY:
    print("⚠️ newsapi_key.txt 파일이 비어 있습니다. API 키를 입력해주세요.")
    exit()

# === 날짜 범위 설정 ===
def get_date_range(center_date: str, days: int = 3):
    """발표일 기준 ±3일 범위 날짜 리스트 생성"""
    center = datetime.datetime.strptime(center_date, "%Y-%m-%d")
    return [(center + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-days, days + 1)]

# === 뉴스 수집 함수 ===
def fetch_news(keyword: str, target_date: str, language: str = "ko"):
    """특정 키워드와 날짜로 뉴스 기사 수집"""
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={keyword}&from={target_date}&to={target_date}"
        f"&language={language}&sortBy=relevancy&apiKey={NEWS_API_KEY}"
    )
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print(f"❌ {keyword} ({target_date}) 요청 오류: {res.status_code}")
            return []
        data = res.json().get("articles", [])
        return [
            {
                "date": target_date,
                "keyword": keyword,
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "source": a.get("source", {}).get("name"),
            }
            for a in data
        ]
    except Exception as e:
        print(f"⚠️ {keyword} ({target_date}) 수집 중 오류: {e}")
        return []

# === 전체 뉴스 수집 ===
def collect_news(keywords, report_date: str):
    """여러 키워드에 대해 뉴스 수집 실행"""
    all_articles = []
    for kw in keywords:
        for d in get_date_range(report_date, days=3):
            articles = fetch_news(kw, d)
            if articles:
                all_articles.extend(articles)
                print(f"✅ {kw} ({d}) 뉴스 {len(articles)}건 수집 완료")

    # === 결과 저장 ===
    output_path = DATA_DIR / f"{report_date}_news.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"📦 뉴스 저장 완료: {output_path}")
    return output_path

# === 테스트 실행 ===
if __name__ == "__main__":
    test_keywords = ["대통령", "국민의힘", "더불어민주당"]
    test_date = datetime.datetime.now().strftime("%Y-%m-%d")
    collect_news(test_keywords, test_date)
