from typing import List, Dict, Any
import re
import math

def _softmax(a: float, b: float) -> (float, float):
    ma = max(a, b)
    ea = math.exp(a - ma)
    eb = math.exp(b - ma)
    s = ea + eb
    return ea / s, eb / s

def _normalize(text: str) -> str:
    # 한글은 lower() 적용하지 않음
    t = re.sub(r"<br\s*/?>", " ", text)
    # 특수문자 제거 (한글/영문/숫자/공백/!?~만 유지)
    t = re.sub(r"[^\w\u3131-\u318E\uAC00-\uD7A3\s!?~]", " ", t)
    # 공백 정리
    t = re.sub(r"\s+", " ", t).strip()
    # 영문만 소문자로 변환
    t = t.lower()
    return t

NEGATIONS = {"아니다", "아닌", "안", "못", "부정", "거짓", "허위", "가짜", "no", "not"}

LEFT_EXPLICIT = [
    "이재명 대통령", "이재명 축하", "민주당 승리", "언론개혁", "검찰개혁",
    "내란세력 척결", "mbc 고생", "극우", "친일 척결", "뉴라이트 척결",
    "눈물", "행복", "만세"
]
RIGHT_EXPLICIT = [
    "공산화", "중국 밑", "친중 독재", "범죄자 대통령", "나라 망했다",
    "부정선거", "당선 무효", "베네수엘라", "주한미군 철수", "문재앙"
]

EVENT_FRAMES = {
    "left": [
        ("내란", 2.0), ("계엄 비판", 2.0), ("내란세력", 2.0), ("검찰 해체", 1.5),
        ("mbc 칭찬", 1.2), ("tk 비판", 1.0), ("언론개혁", 1.5)
    ],
    "right": [
        ("계엄 정당", 2.0), ("부정선거", 2.0), ("공산화", 2.0), ("중국 밑", 2.0),
        ("범죄자 대통령", 1.8), ("나라 망했다", 1.5)
    ]
}

# 매핑: 표현 -> 표준 키
CANON = {
    "내란세력": "내란세력",
    "계엄": "계엄",
    "부정선거": "부정선거",
    "공산화": "공산화",
    "중국": "중국 밑",
    "친중": "중국 밑",
    "mbc": "mbc 칭찬",
    "tk": "tk 비판",
    "대구": "tk 비판",
    "경북": "tk 비판",
    "축하": "이재명 축하",
    "이재명": "이재명 대통령",
    "범죄자": "범죄자 대통령",
    "망했": "나라 망했다"
}

POS_EMO = {"축하", "만세", "행복", "눈물", "감격"}
NEG_EMO = {"망했", "지옥", "역모", "분노", "혐오"}

EMOJI_POS = {"🎉", "💙", "❤", "💗", "💟"}
EMOJI_NEG = {"💀", "🤮", "😡"}

LAUGHTER = re.compile(r"(ㅋㅋ+|ㅎㅎ+)")
JARGON_NO_POL = re.compile(r"^(와|헐|하|음+|또 보러옴|심심할때마다|좋앙|대단).*", re.I)

def extract_features(text: str) -> Dict[str, Any]:
    t = _normalize(text)
    toks = t.split()
    tokens = toks[:]
    # 간단 부정어 윈도우 반영: 부정어가 가까이 있으면 프레임 반전 플래그
    neg_window = any(tok in NEGATIONS for tok in tokens[:6])

    feats = {"left": 0.0, "right": 0.0, "hits_left": [], "hits_right": [], "notes": []}

    # 명시적 지지/비판
    if "이재명" in t and any(k in t for k in ["축하", "대통령", "만세", "고맙"]):
        feats["left"] += 2.5; feats["hits_left"].append("이재명 대통령/축하")
    if "대한민국" in t and "만세" in t:
        feats["left"] += 1.5; feats["hits_left"].append("대한민국 만세")
    if any(k in t for k in ["범죄자", "전과", "당선 무효"]):
        feats["right"] += 2.0; feats["hits_right"].append("범죄자/무효 프레임")
    if "부정선거" in t:
        feats["right"] += 2.0; feats["hits_right"].append("부정선거")
    if any(k in t for k in ["공산", "중국", "친중"]):
        feats["right"] += 2.0; feats["hits_right"].append("공산화/중국 밈")
    if "mbc" in t and any(k in t for k in ["고생", "감사", "최고"]):
        feats["left"] += 1.3; feats["hits_left"].append("MBC 칭찬")
    if any(k in t for k in ["내란세력", "계엄 비판", "계엄 반대", "쿠데타 비판"]):
        feats["left"] += 2.0; feats["hits_left"].append("내란/계엄 비판")

    # 이벤트 프레임 매핑
    for raw, std in CANON.items():
        if raw in t:
            if std in {"내란세력", "mbc 칭찬", "tk 비판", "언론개혁", "이재명 축하", "이재명 대통령"}:
                feats["left"] += 1.0; feats["hits_left"].append(std)
            if std in {"계엄", "부정선거", "공산화", "중국 밑", "범죄자 대통령", "나라 망했다"}:
                feats["right"] += 1.0; feats["hits_right"].append(std)

    # 정서/이모지
    if any(k in t for k in POS_EMO) or any(ch in text for ch in EMOJI_POS):
        if "이재명" in t or "민주" in t or "mbc" in t or "대한민국" in t:
            feats["left"] += 0.8; feats["hits_left"].append("긍정정서→이재명/민주/mbc/대한민국")
    if any(k in t for k in NEG_EMO) or any(ch in text for ch in EMOJI_NEG):
        if "이재명" in t or "민주" in t:
            feats["right"] += 0.6; feats["hits_right"].append("부정정서→이재명")

    # 밈 강도
    if LAUGHTER.search(t):  # ㅋㅋ/ㅎㅎ
        feats["notes"].append("meme:laughter")
    if JARGON_NO_POL.match(text.strip()):
        feats["notes"].append("low-context")

    # 부정어 반전 보정
    if neg_window and feats["right"] > feats["left"] and "가짜" in t:
        feats["left"] += 0.4; feats["notes"].append("negation_flip_hint")

    return feats

def classify_primary(comment_text: str) -> Dict[str, Any]:
    feats = extract_features(comment_text)
    left_score = feats["left"]
    right_score = feats["right"]

    # 아주 약한 신호만 있을 때 잡담 처리
    low_signal = (left_score < 1.0 and right_score < 1.0)
    left_prob, right_prob = _softmax(left_score, right_score)

    if low_signal or abs(left_prob - right_prob) < 0.08:
        label = "판단불가"
        confidence = 0.5
    else:
        if left_prob > right_prob:
            label = "좌파"
            confidence = round(left_prob, 3)
        else:
            label = "우파"
            confidence = round(right_prob, 3)

    return {
        "label": label,
        "left_prob": round(left_prob, 4),
        "right_prob": round(right_prob, 4),
        "confidence": confidence,
        "features": feats
    }


class Analyzer:
    """댓글 분석 및 정치 성향 분류 Analyzer"""

    def __init__(self, reclassifier):
        # reclassifier must implement batch_reclassify(list[dict]) -> list[dict]
        self.reclassifier = reclassifier

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        s1 = set(text1.lower().split())
        s2 = set(text2.lower().split())
        if not s1 and not s2: 
            return 0.0
        inter = len(s1 & s2)
        union = len(s1 | s2) or 1
        return inter / union

    def filter_comments_by_similarity(self, comments: List[str], summary_sentences: List[str], max_comments: int = 500) -> List[Dict]:
        summary_text = " ".join(summary_sentences)
        objs = []
        for i, text in enumerate(comments):
            sim = self.calculate_similarity(text, summary_text)
            objs.append({
                'id': f'yt_{i}',
                'text': text,
                'similarity_score': sim,
                'author': f'사용자{i+1}'
            })
        objs.sort(key=lambda x: x['similarity_score'], reverse=True)
        return objs[:max_comments]

    def _primary_pass(self, items: List[Dict]) -> List[Dict]:
        """1차 분류: classify_primary 사용"""
        enriched = []
        for obj in items:
            res = classify_primary(obj["text"])
            obj["political_orientation"] = res["label"] if res["label"] in ("좌파", "우파") else "판단불가"
            obj["classification_confidence"] = res["confidence"]
            obj["left_prob"] = res["left_prob"]
            obj["right_prob"] = res["right_prob"]
            obj["features"] = res["features"]
            enriched.append(obj)
        return enriched

    def analyze_comments(self, comments: List[str], summary_sentences: List[str]) -> Dict[str, Any]:
        filtered = self.filter_comments_by_similarity(comments, summary_sentences, max_comments=500)
        if not filtered:
            return {'comments': [], 'statistics': {}, 'left_comments': [], 'right_comments': [], 'undetermined_comments': [], 'similarity_stats': {}}

        # 1차 분류
        first_pass = self._primary_pass(filtered)
        
        # 2차 재분류 (판단불가, 중도, 또는 confidence < 0.6인 것만)
        final = self.reclassifier.batch_reclassify(first_pass)

        # 통계 계산
        stats = {'좌파': 0, '우파': 0, '판단불가': 0}
        for c in final:
            label = c.get('political_orientation', '판단불가')
            if label not in stats: 
                stats[label] = 0
            stats[label] += 1

        total = len(final) or 1
        final_stats = {k: {'count': v, 'percentage': round(v/total*100, 1)} for k, v in stats.items()}

        # Similarity 통계
        sims = [c.get('similarity_score', 0) for c in final]
        sim_stats = {
            'average': round(sum(sims)/len(sims), 4) if sims else 0,
            'max': max(sims) if sims else 0,
            'min': min(sims) if sims else 0
        }

        return {
            'comments': final,
            'statistics': final_stats,
            'left_comments': [c['text'] for c in final if c.get('political_orientation') == '좌파'],
            'right_comments': [c['text'] for c in final if c.get('political_orientation') == '우파'],
            'undetermined_comments': [c['text'] for c in final if c.get('political_orientation') == '판단불가'],
            'similarity_stats': sim_stats
        }
