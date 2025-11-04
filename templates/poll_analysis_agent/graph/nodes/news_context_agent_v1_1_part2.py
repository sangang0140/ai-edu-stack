# -*- coding: utf-8 -*-
"""
news_context_agent_v1_1_part2.py
────────────────────────────────
AI 여론 자동 분석 (v1.1)
2단계: 감성·연관 분석 모듈 (출처 포함)

입력: data/news_raw/2025-11-04_news.json
출력: data/news_context/2025-11-04_context.json
"""

import os, json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import pipeline

# === 경로 설정 ===
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"
RAW_PATH = DATA_DIR / "news_raw" / "2025-11-04_news.json"
OUTPUT_PATH = DATA_DIR / "news_context"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# === 1️⃣ 뉴스 로드 ===
if not RAW_PATH.exists():
    print(f"❌ 뉴스 원본 파일이 없습니다: {RAW_PATH}")
    exit()

with open(RAW_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)

if not articles:
    print("⚠️ 뉴스 데이터가 비어 있습니다.")
    exit()

print(f"📰 총 {len(articles)}건의 뉴스 로드 완료")

# === 2️⃣ 감성 분석 ===
print("🧠 감성 분석 중... (약간의 시간이 걸립니다)")
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    device=-1  # 👈 CPU 강제
)
texts = [f"{a['title']} {a['description'] or ''}" for a in articles]
sources = [a.get("source", "Unknown") for a in articles]
urls = [a.get("url", "") for a in articles]

sentiments = sentiment_analyzer(texts, truncation=True)

# 점수 계산
positive = sum(1 for s in sentiments if "4" in s["label"] or "5" in s["label"])
negative = sum(1 for s in sentiments if "1" in s["label"] or "2" in s["label"])
neutral = len(sentiments) - positive - negative

print(f"✅ 감성 분석 완료: 긍정 {positive} / 부정 {negative} / 중립 {neutral}")

# === 3️⃣ 주요 키워드 추출 ===
print("🔍 주요 키워드 추출 중...")
vectorizer = TfidfVectorizer(max_features=50, stop_words=["뉴스", "보도", "기자"])
X = vectorizer.fit_transform(texts)
top_keywords = vectorizer.get_feature_names_out()[:10].tolist()
print(f"✨ 주요 키워드: {', '.join(top_keywords)}")

# === 4️⃣ 클러스터링 및 대표 기사 선정 ===
print("🗂️ 기사 클러스터링 및 대표 기사 선정 중...")
k = 3 if len(articles) > 10 else 1
kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(X)

representatives = []
for i in range(k):
    cluster_idx = [j for j, label in enumerate(kmeans.labels_) if label == i]
    if not cluster_idx:
        continue
    idx = cluster_idx[0]
    representatives.append({
        "title": articles[idx]["title"],
        "source": sources[idx],
        "url": urls[idx],
        "sentiment": sentiments[idx]["label"]
    })

# === 5️⃣ 결과 요약 ===
summary = {
    "date": "2025-11-04",
    "total_articles": len(articles),
    "sentiment": {"positive": positive, "negative": negative, "neutral": neutral},
    "top_keywords": top_keywords,
    "representative_articles": representatives,
    "disclaimer": "※ 본 분석은 NewsAPI에서 수집한 공개 뉴스 데이터를 기반으로 작성되었습니다."
}

# === 6️⃣ 결과 저장 ===
OUTPUT_FILE = OUTPUT_PATH / "2025-11-04_context.json"
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"📦 감성·연관 분석 결과 저장 완료 → {OUTPUT_FILE}")
