from pathlib import Path
from typing import Dict
from ..state import PipelineState
import os, io, re
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# === OCR 유틸 ===
def _ocr_pdf_to_text(pdf_path: str, lang: str = "kor+eng") -> str:
    """PDF → 이미지 → OCR 문자열 추출"""
    tess = os.getenv("TESSERACT_PATH")
    if tess and os.path.exists(tess):
        pytesseract.pytesseract.tesseract_cmd = tess
    doc = fitz.open(pdf_path)
    texts = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        try:
            t = pytesseract.image_to_string(img, lang=lang)
        except Exception:
            t = pytesseract.image_to_string(img)
        texts.append(t)
    return "\n".join(texts)

# === 내부 파서 함수들 ===
def _avg_pair(lv, rv):
    """좌/우 평균"""
    try:
        if lv is None or rv is None:
            return None
        return round((float(lv) + float(rv)) / 2, 3)
    except Exception:
        return None

def _best_block(text: str) -> str:
    """가장 숫자가 많은 블록 추출"""
    blocks = text.split("\n\n")
    if not blocks:
        return text
    return max(blocks, key=lambda b: len(re.findall(r"\d", b)))

def _parse_pairs_from_text(txt: str) -> dict:
    """텍스트에서 Theta, BetaL 등 숫자 패턴 추출"""
    pat = re.compile(
        r"(Theta|세타|θ)\D*?([0-9]+(?:\.[0-9]+)?)\D*?([0-9]+(?:\.[0-9]+)?)|"
        r"(BetaL|저\s*베타|βL)\D*?([0-9]+(?:\.[0-9]+)?)\D*?([0-9]+(?:\.[0-9]+)?)|"
        r"(BetaH|고\s*베타|βH)\D*?([0-9]+(?:\.[0-9]+)?)\D*?([0-9]+(?:\.[0-9]+)?)|"
        r"(SMR|에스엠알|Sensorimotor)\D*?([0-9]+(?:\.[0-9]+)?)\D*?([0-9]+(?:\.[0-9]+)?)",
        re.I
    )
    result = {}
    for m in pat.finditer(txt):
        g = [x for x in m.groups() if x]
        if not g:
            continue
        label = None
        nums = []
        for x in g:
            if re.search(r"[A-Za-z가-힣β]", x):
                label = x
            else:
                nums.append(float(x))
        if label and len(nums) >= 2:
            label = label.lower()
            if "theta" in label or "세타" in label or "θ" in label:
                result["Theta"] = tuple(nums[:2])
            elif "betal" in label or "저" in label:
                result["BetaL"] = tuple(nums[:2])
            elif "betah" in label or "고" in label:
                result["BetaH"] = tuple(nums[:2])
            elif "smr" in label or "sensorimotor" in label:
                result["SMR"] = tuple(nums[:2])
    return result


def _unglue_numbers(s: str) -> str:
    """
    붙은 연속 소수점 숫자 (예: '44.553.8') 패턴 분리
    '44.553.8' → '44.55 3.8'
    """
    s = re.sub(r"(\d+\.\d{1,2})(?=\d)", r"\1 ", s)
    return s


def _parse_compact_table(text: str) -> dict:
    """Delta/Theta/Alpha/... 표에서 숫자 붙은 경우 파싱"""
    label_line = None
    for ln in text.splitlines():
        if re.search(r"(Delta|델타).*(Theta|세타|θ).*(Alpha|알파).*(SMR|에스엠알).*(BetaL|저\s*베타|βL).*(BetaH|고\s*베타|βH)", ln, re.I):
            label_line = ln
            break
    if not label_line:
        return {}

    order, toks = [], label_line.split()
    for tok in toks:
        t = tok.lower()
        if "theta" in t or "세타" in t or "θ" in t:
            order.append("Theta")
        elif "betal" in t or "βl" in t or "저" in t:
            order.append("BetaL")
        elif "betah" in t or "βh" in t or "고" in t:
            order.append("BetaH")
        elif "smr" in t or "sensorimotor" in t or "에스엠알" in t:
            order.append("SMR")

    lines = text.splitlines()
    idx = lines.index(label_line)
    tail = "\n".join(lines[idx + 1: idx + 6])
    tail = _unglue_numbers(tail)
    nums = re.findall(r"[+-]?\d+(?:\.\d+)?", tail)

    vals = []
    for s in nums:
        try:
            vals.append(float(s))
        except Exception:
            pass

    pairs, i = {}, 0
    for lab in order:
        if i + 1 < len(vals):
            pairs[lab] = (vals[i], vals[i + 1])
            i += 2
        else:
            break
    return pairs


# === 핵심 실행 함수 ===
def run(state: PipelineState) -> PipelineState:
    pdf_path = state.raw_inputs.get("neuro_pdf")
    if not pdf_path:
        state.log_event("neuro_parse", {"status": "no_pdf"})
        return state

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        state.log_event("neuro_parse", {"status": "not_found", "path": str(pdf_path)})
        return state

    all_text = ""
    pairs = {}

    # 1️⃣ 우선 텍스트 파서로 시도
    try:
        with fitz.open(pdf_path) as doc:
            all_text = "\n".join(page.get_text() for page in doc)
        pairs = _parse_pairs_from_text(all_text)
    except Exception:
        pass

    # 2️⃣ 값이 전혀 없으면 compact table 시도
    if not pairs:
        pairs = _parse_compact_table(all_text)

    # 3️⃣ 좌/우 평균 계산
    theta = _avg_pair(*(pairs.get("Theta") or (None, None)))
    betaL = _avg_pair(*(pairs.get("BetaL") or (None, None)))
    betaH = _avg_pair(*(pairs.get("BetaH") or (None, None)))
    smr   = _avg_pair(*(pairs.get("SMR")   or (None, None)))

    # 기본 태그 설정
    source_tag = "text_only"

    # 4️⃣ 전부 None이면 OCR 폴백 시도
    vals_now = [v for v in [theta, betaL, betaH, smr] if v is not None]
    if not vals_now:
        try:
            ocr_text = _ocr_pdf_to_text(str(pdf_path))
            all_text = ((all_text or "") + "\n" + (ocr_text or "")).strip()
            focus_text = _best_block(all_text)
            text_pairs = _parse_pairs_from_text(focus_text) or _parse_compact_table(all_text)

            theta = _avg_pair(*(text_pairs.get("Theta") or (None, None)))
            betaL = _avg_pair(*(text_pairs.get("BetaL") or (None, None)))
            betaH = _avg_pair(*(text_pairs.get("BetaH") or (None, None)))
            smr   = _avg_pair(*(text_pairs.get("SMR")   or (None, None)))

            source_tag = "ocr_text"
        except Exception:
            source_tag = "text_only"

    # === 결과 저장 ===
    parsed = {
        "theta_rel_open": theta,
        "betaL_rel_open": betaL,
        "betaH_rel_open": betaH,
        "smr_rel_open": smr,
        "source": source_tag,
    }

    state.raw_inputs["neuro_parsed"] = parsed
    state.log_event("neuro_parse", {"status": "ok", **parsed})
    return state
