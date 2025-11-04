# graph/nodes/visual_generator.py
import os
import openai
import json
from datetime import datetime

# === OpenAI 키 불러오기 ===
key_path = r"D:\ai-edu-stack\templates\poll_analysis_agent\config\openai_key.txt"
with open(key_path, "r", encoding="utf-8") as f:
    openai.api_key = f.read().strip()

def generate_visual_prompts():
    """유튜브 스크립트를 기반으로 장면별 이미지/영상 프롬프트 생성"""
    # 최신 스크립트 파일 탐색
    output_dir = "outputs"
    latest_script = None
    for f in sorted(os.listdir(output_dir), reverse=True):
        if f.startswith("youtube_script") and f.endswith(".txt"):
            latest_script = os.path.join(output_dir, f)
            break

    if not latest_script:
        print("❌ youtube_script 파일을 찾을 수 없습니다.")
        return

    with open(latest_script, "r", encoding="utf-8") as f:
        script_text = f.read()

    prompt = f"""
다음은 유튜브 해설 스크립트입니다. 
이 내용을 4~6개의 장면(scene)으로 나누고, 각 장면에 맞는 AI 이미지 생성용 프롬프트를 작성하세요.

요청 형식(JSON):
[
  {{
    "scene": "인트로",
    "prompt": "한국 뉴스 스튜디오에서 앵커가 등장하는 장면, 16:9, 수채화풍, 감성적, realistic lighting"
  }},
  {{
    "scene": "본론",
    "prompt": "대통령 지지율 그래프와 도시의 풍경이 겹쳐지는 이미지, 감정적 대비, 16:9"
  }}
]

제작 기준:
- 인물은 반드시 '한국인'으로 표현
- 비율은 16:9
- 정치적 편향 없이 중립적인 시각 연출
- 감정의 흐름(서두→분석→전환→결론)이 자연스럽게 느껴지게 구성

스크립트 내용:
{script_text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    json_text = response["choices"][0]["message"]["content"]

    # 결과 저장
    output_path = os.path.join(output_dir, f"visual_prompts_{datetime.now().strftime('%Y-%m-%d')}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_text)

    print(f"🎨 장면별 프롬프트 생성 완료: {output_path}")
    print("\n🖼️ 미리보기 ↓\n")
    print(json_text)


if __name__ == "__main__":
    generate_visual_prompts()
