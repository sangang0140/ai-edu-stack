# -*- coding: utf-8 -*-
"""
gmail_auth_setup.py
────────────────────
로컬에서 Gmail API 인증을 완료하고 token.json을 생성하는 스크립트
(Google Console의 OAuth 동의 화면을 열 수 없을 때 대체 사용)

✅ 기능
- gmail_key.json(client_secret.json) 기반 OAuth2 인증 실행
- token.json 자동 생성 및 저장
- Gmail 연결 테스트
"""

from __future__ import print_function
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# === Gmail API 권한 범위 (메일 전송 + 라벨 조회) ===
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

# === 경로 설정 ===
CONFIG_DIR = r"D:\ai-edu-stack\templates\poll_analysis_agent\config"
os.makedirs(CONFIG_DIR, exist_ok=True)

CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "gmail_key.json")  # OAuth 클라이언트 JSON 파일
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")

def main():
    creds = None

    # 기존 토큰이 있다면 불러오기
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # 새로 인증이 필요하면 실행
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"❌ Gmail 키 파일이 없습니다: {CREDENTIALS_PATH}")
                return
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # 인증 완료 후 token.json 저장
        with open(TOKEN_PATH, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
        print(f"✅ 인증 완료! 토큰이 생성되었습니다 → {TOKEN_PATH}")

    # === Gmail API 연결 테스트 ===
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        print("\n📧 Gmail 연결 성공! 라벨 목록 예시:")
        for label in results.get('labels', []):
            print("-", label['name'])
    except Exception as e:
        print(f"⚠️ Gmail 연결 테스트 중 오류: {e}")

if __name__ == '__main__':
    main()
