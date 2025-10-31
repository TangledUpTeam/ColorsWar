from typing import List, Dict, Any
import re
import math

def _softmax(a: float, b: float) -> (float, float):
    ma = max(a, b)
    ea, eb = math.exp(a - ma), math.exp(b - ma)
    s = ea + eb
    return ea / s, eb / s

def _normalize(text: str) -> str:
    t = re.sub(r"<br\s*/?>", " ", text)
    t = re.sub(r"[^\w\u3131-\u318E\uAC00-\uD7A3\s!?~]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t.lower()

NEGATIONS = {"아니다", "아닌", "안", "못", "거짓", "허위", "no", "not"}

# 2025 이슈 반영 확장 키워드
LEFT_FRAMES = {
    "이재명", "민주당", "언론개혁", "검찰개혁", "복지", "노동", "전공의 무시", "의료붕괴",
    "특검 필요", "외교 무능", "임대차 보호", "투기 억제", "노동권", "대화", "평화", "협력",
    "환경", "인권", "재분배", "서민", "청년", "플랫폼노동", "젠더 평등", "소수자"
}
RIGHT_FRAMES = {
    "윤석열", "국민의힘", "법치", "안보", "시장", "기업", "규제완화", "공급 확대", "재건축 완화",
    "공공의료 강화", "의사기득권", "불법파업", "강경 대응", "확성기", "동맹", "군사력",
    "친중", "공산화", "부정선거", "범죄자", "검찰 정상화", "질서", "효율", "책임", "전통", "가정"
}

POS_EMO = {"축하", "만세", "고맙", "감사", "사랑"}
NEG_EMO = {"망했", "실패", "지옥", "분노", "혐오", "싫다"}
EMOJI_POS = {"❤", "💙", "💗", "💟", "🥰", "👏"}
EMOJI_NEG = {"💀", "🤮", "😡", "👎"}

def extract_features(text: str) -> Dict[str, Any]:
    t = _normalize(text)
    feats = {"left": 0.0, "right": 0.0, "hits": []}

    # 이슈별 좌/우 프레임 감지
    for word in LEFT_FRAMES:
        if word in t:
            feats["left"] += 1.0
            feats["hits"].append(f"L:{word}")
    for word in RIGHT_FRAMES:
        if word in t:
            feats["right"] += 1.0
            feats["hits"].append(f"R:{word}")

    # 감정/이모지 방향성
    if any(k in t for k in POS_EMO) or any(ch in text for ch in EMOJI_POS):
        if any(k in t for k in ["이재명", "민주", "복지", "노동"]):
            feats["left"] += 0.8; feats["hits"].append("긍정→좌파")
        if any(k in t for k in ["윤석열", "국힘", "시장", "법치"]):
            feats["right"] += 0.8; feats["hits"].append("긍정→우파")
    if any(k in t for k in NEG_EMO) or any(ch in text for ch in EMOJI_NEG):
        if any(k in t for k in ["이재명", "민주"]):
            feats["right"] += 0.6; feats["hits"].append("부정→좌파비판")
        if any(k in t for k in ["윤석열", "국힘"]):
            feats["left"] += 0.6; feats["hits"].append("부정→우파비판")

    # 단어 카운트 기반 확률
    left_prob, right_prob = _softmax(feats["left"], feats["right"])
    label = "좌파" if left_prob > right_prob else "우파"
    confidence = round(max(left_prob, right_prob), 3)
    
    # 극단성 점수: 각 진영의 순수 점수 차이 (좌파면 left-right, 우파면 right-left)
    extremity_score = feats["left"] - feats["right"] if label == "좌파" else feats["right"] - feats["left"]

    return {
        "label": label, 
        "confidence": confidence, 
        "hits": feats["hits"],
        "left_score": feats["left"],
        "right_score": feats["right"],
        "extremity_score": extremity_score  # 극단성 점수
    }

class Analyzer:
    """LLM 없이 키워드/프레임 기반으로만 좌·우 분류"""

    def __init__(self):
        pass

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        s1, s2 = set(text1.lower().split()), set(text2.lower().split())
        if not s1 or not s2: return 0.0
        return len(s1 & s2) / len(s1 | s2)

    def filter_comments_by_similarity(self, comments: List[str], summary_sentences: List[str], max_comments: int = 500) -> List[Dict]:
        summary_text = " ".join(summary_sentences)
        objs = []
        for i, text in enumerate(comments):
            sim = self.calculate_similarity(text, summary_text)
            objs.append({"id": f"yt_{i}", "text": text, "similarity_score": sim, "author": f"사용자{i+1}"})
        objs.sort(key=lambda x: x["similarity_score"], reverse=True)
        return objs[:max_comments]

    def analyze_comments(self, comments: List[str], summary_sentences: List[str], top_k: int = 5) -> Dict[str, Any]:
        """
        summaries 기반으로 댓글 분석 후 극좌/극우 댓글 각 top_k개만 추출
        
        Args:
            comments: 전체 댓글 리스트
            summary_sentences: 영상 요약 문장 리스트
            top_k: 좌파/우파 각각 추출할 극단 댓글 개수 (기본 5개)
        """
        filtered = self.filter_comments_by_similarity(comments, summary_sentences)
        if not filtered:
            return {'comments': [], 'statistics': {}, 'left_comments': [], 'right_comments': []}

        # 모든 댓글 분석
        analyzed = []
        for obj in filtered:
            res = extract_features(obj["text"])
            obj["political_orientation"] = res["label"]
            obj["classification_confidence"] = res["confidence"]
            obj["hits"] = res["hits"]
            obj["left_score"] = res["left_score"]
            obj["right_score"] = res["right_score"]
            obj["extremity_score"] = res["extremity_score"]
            analyzed.append(obj)

        # 확신도 0.55 미만 제외
        analyzed = [c for c in analyzed if c["classification_confidence"] >= 0.55]

        # 좌파/우파 분리
        left_comments = [c for c in analyzed if c["political_orientation"] == "좌파"]
        right_comments = [c for c in analyzed if c["political_orientation"] == "우파"]

        # 극단성 점수 기준으로 정렬 (높은 순)
        left_comments.sort(key=lambda x: x["extremity_score"], reverse=True)
        right_comments.sort(key=lambda x: x["extremity_score"], reverse=True)

        # 상위 top_k개만 선택
        top_left = left_comments[:top_k]
        top_right = right_comments[:top_k]
        
        # 최종 선택된 댓글들만 반환
        final = top_left + top_right

        stats = {"좌파": len(top_left), "우파": len(top_right)}
        total = len(final) or 1
        stats = {k: {"count": v, "percentage": round(v/total*100, 1)} for k, v in stats.items()}

        return {
            "comments": final,
            "statistics": stats,
            "left_comments": [c["text"] for c in top_left],
            "right_comments": [c["text"] for c in top_right],
        }
