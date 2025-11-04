# flux_generator_comfy.py
import os, json, requests, time

# ✅ ComfyUI 서버 주소 (청춘님 환경)
COMFY_URL = "http://127.0.0.1:8188/prompt"

def generate_flux_images():
    output_dir = "outputs"
    scenes_dir = os.path.join(output_dir, "scenes")
    os.makedirs(scenes_dir, exist_ok=True)

    # 최신 visual_prompts 파일 찾기
    latest_file = sorted(
        [f for f in os.listdir(output_dir) if f.startswith("visual_prompts")],
        reverse=True
    )[0]
    json_path = os.path.join(output_dir, latest_file)
    with open(json_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    print(f"🎨 ComfyUI Flux 자동화 시작: {json_path}")
    print(f"🔗 연결 중... {COMFY_URL}")

    for idx, item in enumerate(prompts, start=1):
        scene = item["scene"]
        prompt = item["prompt"]

        payload = {
            "prompt": {
                "1": {
                    "class_type": "KSampler",
                    "inputs": {
                        "text": prompt,
                        "seed": -1,
                        "steps": 25,
                        "cfg": 7,
                        "width": 1280,
                        "height": 720,
                        "sampler_name": "euler",
                        "model": "Flux.1-schnell"
                    }
                }
            }
        }

        try:
            res = requests.post(COMFY_URL, json=payload, timeout=300)
            res.raise_for_status()
            print(f"✅ [{idx}] {scene} 생성 요청 완료 (ComfyUI 대기열에 등록됨)")
        except Exception as e:
            print(f"⚠️ [{idx}] {scene} 오류: {e}")
        time.sleep(1)

    print("\n🎉 모든 프롬프트를 ComfyUI로 전송했습니다.")
    print("📌 ComfyUI에서 ‘Queue Prompt’ 버튼을 눌러 실제 생성 실행.")

if __name__ == "__main__":
    generate_flux_images()
