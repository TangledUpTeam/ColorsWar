"""
댓글 분류 모듈
좌파/우파 성향 분류 및 재분류
"""
import os
import requests
from typing import List, Dict


class CommentClassifier:
    """댓글 정치 성향 분류기"""
    
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        # 키워드 기반 분류
        self.left_keywords = [
            "복지", "재분배", "노동", "임금", "최저임금", "서민", "공공",
            "인권", "환경", "페미니즘", "성평등", "차별", "진보", "공정",
            "평화", "협력", "검찰개혁", "언론자유", "민주주의"
        ]
        
        self.right_keywords = [
            "시장", "기업", "투자", "경쟁", "규제완화", "민영화",
            "보수", "전통", "가정", "질서", "도덕", "안보", "군",
            "동맹", "미국", "국방", "법과질서", "효율"
        ]
    
    def classify_comment(self, text: str) -> tuple[str, float]:
        """단일 댓글 분류"""
        # 키워드 기반 분류
        left_score = sum(1 for kw in self.left_keywords if kw in text)
        right_score = sum(1 for kw in self.right_keywords if kw in text)
        
        if left_score > right_score:
            return "좌파", 0.7
        elif right_score > left_score:
            return "우파", 0.7
        else:
            return "판단불가", 0.5
    
    def reclassify_with_llm(self, text: str) -> str:
        """LLM을 사용한 재분류 (판단불가 → 좌파/우파)"""
        system_prompt = """당신은 대한민국 정치 성향 전문가입니다.
주어진 댓글을 반드시 '좌파' 또는 '우파' 중 하나로 분류해야 합니다.

좌파 특징: 복지 확대, 재분배, 노동자 권리, 환경 보호, 인권
우파 특징: 시장경제, 기업친화, 전통 가치, 국가안보

답변은 '좌파' 또는 '우파' 한 단어만 출력하세요."""
        
        user_prompt = f"다음 댓글을 좌파 또는 우파로 분류하세요:\n\n{text}\n\n답변:"
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 10}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                if "좌파" in result or "좌" in result:
                    return "좌파"
                elif "우파" in result or "우" in result:
                    return "우파"
        except:
            pass
        
        # 실패 시 키워드 기반
        left_score = sum(1 for kw in self.left_keywords if kw in text)
        right_score = sum(1 for kw in self.right_keywords if kw in text)
        return "좌파" if left_score >= right_score else "우파"
    
    def classify_batch(self, comments: List[str]) -> List[Dict]:
        """여러 댓글 일괄 분류"""
        results = []
        
        for i, text in enumerate(comments):
            orientation, confidence = self.classify_comment(text)
            
            comment_obj = {
                'id': f'comment_{i}',
                'text': text,
                'political_orientation': orientation,
                'classification_confidence': confidence,
                'was_reclassified': False
            }
            
            # 판단불가인 경우 재분류
            if orientation == "판단불가":
                new_orientation = self.reclassify_with_llm(text)
                comment_obj['political_orientation'] = new_orientation
                comment_obj['was_reclassified'] = True
                comment_obj['original_orientation'] = orientation
                print(f"[재분류] {orientation} → {new_orientation} | {text[:40]}...")
            
            results.append(comment_obj)
        
        return results
    
    def get_statistics(self, classified_comments: List[Dict]) -> Dict:
        """분류 통계"""
        stats = {'좌파': 0, '우파': 0, '중도': 0, '판단불가': 0}
        
        for comment in classified_comments:
            orientation = comment.get('political_orientation', '판단불가')
            stats[orientation] = stats.get(orientation, 0) + 1
        
        total = len(classified_comments) or 1
        
        return {
            'total': total,
            'counts': stats,
            'percentages': {k: round(v / total * 100, 1) for k, v in stats.items()},
            'left_comments': [c['text'] for c in classified_comments if c.get('political_orientation') == '좌파'],
            'right_comments': [c['text'] for c in classified_comments if c.get('political_orientation') == '우파']
        }

