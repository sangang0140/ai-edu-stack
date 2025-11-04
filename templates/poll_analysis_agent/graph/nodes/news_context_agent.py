# -*- coding: utf-8 -*-
"""
news_context_agent.py
여론 변동에 영향을 준 주요 뉴스를 자동 수집·요약
"""

import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from openai import OpenAI

# === 기본 경로 설정 ===
BASE_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
os.makedirs(OUTPUT_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
news_path = os.path.join(OUTPUT_DIR, f"related_news_{today}.json")

# === OpenAI API Key ===
key_path = os.path.join(CONFIG_DIR, "openai_key.txt")
if not os.path.exists(key_path):
    print(f"❌ OpenAI Key 파일이 없습니다: {key_path}")
    exit()

client = OpenAI(api_key=open(key_path, "r", encoding="utf-8").read().strip())

# === 뉴스 검색 키워드 ===
KEYWORDS = ["대통령 지지율", "국민의힘", "더불어민주당", "정치 이슈", "사회 이슈"]

def fetch_naver_news(keyword: str, limit: int = 5):
    """네이버 뉴스 검색 결과 상위 n개 제목 + URL 추출"""
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select(".news_tit")[:limit]
    return [{"title": i["title"], "url": i["href"]} for i in items]

# === 뉴스 수집 ===
collected_news = []
for kw in KEYWORDS:
    try:
        articles = fetch_naver_news(kw)
        if articles:
            collected_news.extend(articles)
    except Exception as e:
        print(f"⚠️ {kw} 수집 중 오류: {e}")

# === AI 요약 ===
titles = "\n".join([f"- {n['title']}" for n in collected_news])
prompt = f"""
다음은 최근 주요 뉴스 제목 목록입니다.
각 뉴스가 대통령 혹은 정당 지지율에 어떤 영향을 미칠 수 있는지
5줄 이내로 요약하고, 핵심 키워드를 포함한 간결한 분석을 작성해주세요.

{titles}
"""

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    summary = response.choices[0].message.content.strip()
except Exception as e:
    summary = f"⚠️ AI 요약 중 오류 발생: {e}"

# === 결과 저장 ===
output_data = {
    "date": today,
    "keywords": KEYWORDS,
    "news_titles": collected_news,
    "summary": summary
}

with open(news_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"🗞️ 주요 뉴스 분석 저장 완료 → {news_path}")
print("🧠 요약 미리보기 ↓\n")
print(summary)
