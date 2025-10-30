"""
판단불가/중도 댓글 강제 재분류 모듈 (2025 최신 세분화 버전)
최근 1년간 대한민국 정치·사회 이슈 및 밈 반영
좌파 또는 우파 중 반드시 하나로 분류
"""
import os
import requests
import json


class ForceReclassifier:
    """판단불가 댓글을 좌/우파로 강제 재분류"""

    def __init__(self):
        # Ollama 로컬 서버 URL (기본값)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")  # ex: "mistral", "gemma2", "llama3.2" 등

        # 키워드 기반 보조 분류 세분화 (2025년 이슈 반영)
        self.left_keywords = [
            # 경제/복지
            "복지", "재분배", "노동", "임금", "최저임금", "서민", "공공", "국가 책임",
            # 사회/문화
            "인권", "환경", "페미니즘", "성평등", "청년보호", "차별", "진보", "공정",
            # 외교/안보
            "대북", "평화", "외교", "협력", "중립", "다자주의",
            # 제도/민주주의
            "검찰개혁", "언론자유", "참여", "투명", "민주주의", "분권",
            # 신세대/온라인 문화
            "플랫폼노동", "청년문제", "AI", "디지털격차", "복지국가"
        ]

        self.right_keywords = [
            # 경제/시장
            "시장", "기업", "투자", "경쟁", "규제완화", "민영화", "세금감면", "자유경제",
            # 사회/문화
            "보수", "전통", "가정", "질서", "도덕", "책임", "역할", "안정",
            # 외교/안보
            "안보", "군", "동맹", "미국", "일본", "북한", "강경", "국방", "국가안보",
            # 제도/리더십
            "강한리더십", "효율", "법과질서", "권위", "안정", "국가중심",
            # 신세대/밈
            "남혐", "여혐", "한남", "이대남", "맘충", "정치적 올바름", "PC주의"
        ]

    def force_reclassify(self, comment_text: str) -> str:
        """
        댓글을 좌파 또는 우파 중 하나로 강제 분류

        Args:
            comment_text: 댓글 텍스트
        Returns:
            "좌파" 또는 "우파"
        """
        system_prompt = """당신은 대한민국 최근 1년간의 정치·사회 이슈, 젠더 갈등, 경제정책, 외교, 밈 문화를 분석한 정치 성향 전문가입니다.
주어진 댓글을 반드시 '좌파' 또는 '우파' 중 하나로 분류해야 합니다.
중도나 판단불가는 절대 허용되지 않습니다.

좌파 특징:
- 복지 확대, 재분배, 노동자 권리, 환경 보호, 소수자 인권, 청년 및 플랫폼 노동 보호
- 교육·문화의 진보적 변화 옹호, 권력 견제와 제도 개혁 강조
- 외교에서 자주·균형·협력 지향

우파 특징:
- 시장경제, 기업친화, 작은 정부, 전통 가치, 국가안보 우선
- 문화·사회에서 보수적 질서 및 역할 강조
- 외교에서 동맹 강화, 강경 대응 중시

애매한 경우에도 반드시 미세한 단서를 찾아 한쪽으로 분류하세요.
답변은 '좌파' 또는 '우파' 한 단어만 출력하세요."""

        user_prompt = f"""다음 댓글을 좌파 또는 우파로 분류하세요:

댓글: {comment_text}

답변 형식: 좌파 또는 우파 (한 단어만)"""

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
                if any(x in result for x in ["좌파", "좌", "left"]):
                    return "좌파"
                elif any(x in result for x in ["우파", "우", "right"]):
                    return "우파"

            # 실패 시 키워드 기반 분류
            return self._keyword_based(comment_text)

        except Exception as e:
            print(f"⚠️ 재분류 중 오류: {str(e)} — 키워드 기반으로 대체합니다.")
            return self._keyword_based(comment_text)

    def _keyword_based(self, text: str) -> str:
        """키워드 기반 간이 분류 (백업용)"""
        l = sum(1 for kw in self.left_keywords if kw in text)
        r = sum(1 for kw in self.right_keywords if kw in text)
        return "좌파" if l >= r else "우파"

    def batch_reclassify(self, comments: list) -> list:
        """여러 댓글 일괄 재분류"""
        reclassified = []
        for comment in comments:
            orientation = comment.get('political_orientation', '판단불가')
            if orientation in ['판단불가', '중도']:
                new_orientation = self.force_reclassify(comment['text'])
                comment['political_orientation'] = new_orientation
                comment['was_reclassified'] = True
                comment['original_orientation'] = orientation
                print(f"[재분류] {orientation} → {new_orientation} | {comment['text'][:40]}...")
            else:
                comment['was_reclassified'] = False
            reclassified.append(comment)
        return reclassified