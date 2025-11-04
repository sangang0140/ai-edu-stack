# -*- coding: utf-8 -*-
"""
email_sender.py
──────────────────────────────
AI 여론 자동 분석 v1.1 — 이메일 자동 발송 모듈

✅ 기능
- Gmail API (OAuth2) 기반 자동 이메일 전송
- config/token.json 인증 사용
- data/report/YYYY-MM-DD_AI_여론리포트.pdf 첨부
"""

import os
import datetime
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# === 경로 설정 ===
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
REPORT_DIR = BASE_DIR / "data" / "report"

# === Gmail 인증 불러오기 ===
def get_gmail_service():
    token_path = CONFIG_DIR / "token.json"
    if not token_path.exists():
        print(f"❌ Gmail 인증 토큰이 없습니다: {token_path}")
        print("👉 먼저 gmail_auth_setup.py를 실행해주세요.")
        exit()

    creds = Credentials.from_authorized_user_file(token_path)
    service = build("gmail", "v1", credentials=creds)
    return service

# === 이메일 전송 ===
def send_report_email(receiver_email: str):
    service = get_gmail_service()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    pdf_path = REPORT_DIR / f"{today}_AI_여론리포트.pdf"

    if not pdf_path.exists():
        print(f"⚠️ 리포트 파일이 존재하지 않습니다: {pdf_path}")
        return

    # 메일 구성
    msg = MIMEMultipart()
    msg["to"] = receiver_email
    msg["subject"] = f"[AI Agent Business] {today} AI 여론 자동 분석 리포트"
    body = MIMEText(
        f"안녕하세요 청춘님,\n\n"
        f"{today}의 AI 여론 자동 분석 리포트를 보내드립니다.\n"
        f"첨부된 PDF 파일을 확인해주세요.\n\n"
        f"- AI Agent Business 자동 리포터 🤖",
        "plain",
        "utf-8"
    )
    msg.attach(body)

    # 첨부 파일 추가
    with open(pdf_path, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header("Content-Disposition", "attachment", filename=pdf_path.name)
        msg.attach(attach)

    # Gmail API 전송
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    message = {"raw": raw_message}

    try:
        service.users().messages().send(userId="me", body=message).execute()
        print(f"✅ 이메일 전송 완료 → {receiver_email}")
        print(f"📎 첨부: {pdf_path.name}")
    except Exception as e:
        print(f"❌ 이메일 전송 실패: {e}")

# === 실행 ===
if __name__ == "__main__":
    receiver = "sangangddle@gmail.com"
    send_report_email(receiver)
