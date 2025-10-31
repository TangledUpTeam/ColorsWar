import os
import requests
from typing import List, Dict

class ForceReclassifier:
    """판단불가/중도 댓글을 좌/우로 강제 재분류 (2025년 최신 프레임 반영)"""

    def __init__(self):
        # Ollama 서버 및 모델 설정
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        # Ollama 연결 가능 여부 확인
        self.ollama_available = self._check_ollama_connection()

        # 키워드 백업용 사전 (LLM 실패 시 사용)
        self.left_keywords = [
            "복지", "노동", "재분배", "서민", "인권", "언론개혁", "검찰개혁", "환경",
            "평등", "민주주의", "청년", "진보", "노조", "공공", "플랫폼노동", "전공의 무시",
            "의료붕괴", "권력형", "특검", "늑장대응", "외교무능", "임대차 보호"
        ]
        self.right_keywords = [
            "시장", "기업", "자유경제", "규제완화", "민영화", "보수", "질서", "안보",
            "동맹", "법치", "효율", "강경", "책임", "공산", "부정선거", "범죄자", "중국",
            "친중", "공공의료", "불법파업", "의사기득권", "강경대응", "관광 활성화"
        ]

    def _check_ollama_connection(self) -> bool:
        """Ollama 서버 연결 가능 여부 확인 (초기화 시 1회만)"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                print("✓ Ollama 서버 연결 성공 - LLM 분류 사용 가능")
                return True
        except Exception:
            pass
        
        print("ℹ️ Ollama 서버 연결 실패 - 키워드 기반 분류만 사용합니다.")
        return False

    def force_reclassify(self, comment_text: str, left_prior: float = 0.5, right_prior: float = 0.5) -> str:
        """
        좌파 또는 우파 중 하나로 반드시 분류 (LLM + 백업 혼합형)
        """
        left_prior = float(max(0.0, min(1.0, left_prior)))
        right_prior = float(max(0.0, min(1.0, right_prior)))

        # ====== 2024~2025 대한민국 주요 이슈 반영 프롬프트 ======
        system_prompt = """
당신은 대한민국의 최신 정치·사회 이슈를 분석해 댓글의 정치 성향을 분류하는 전문가입니다.
모든 발언은 반드시 '좌파' 또는 '우파' 중 하나로 분류해야 하며, 중도나 판단불가는 허용되지 않습니다.

■ 2024~2025 주요 이슈 맥락 요약
1️⃣ 의대정원 확대 논란
 - 좌파 시각: '졸속 추진', '의료 붕괴', '정부 독단', '전공의 무시'
 - 우파 시각: '의사 기득권', '불법파업', '공공의료 강화', '법치'

2️⃣ 중국인 무비자 입국 문제
 - 좌파 시각: '치안 불안', '여론 무시', '중국 눈치 보기'
 - 우파 시각: '관광 활성화', '한시적 조치', '내수 회복'

3️⃣ 캄보디아 인질·외교 논란
 - 좌파 시각: '늑장 대응', '외교 무능', '영사 실패'
 - 우파 시각: '신속 대응', '강경 외교', '구출 성공'

4️⃣ 디올 논란 / 대통령 배우자 특검 요구
 - 좌파 시각: '권력형 의혹', '특검 필요', '책임 회피', '사적 유용'
 - 우파 시각: '정치공세', '사생활 침해', '야당 물타기', '근거 없음'

5️⃣ 노동·노조 이슈
 - 좌파 시각: '노동권 보호', '손배 남용', '장시간 노동 반대'
 - 우파 시각: '불법파업 처벌', '법치주의', '기업 손실 최소화'

6️⃣ 부동산 정책
 - 좌파 시각: '투기 억제', '세제 형평', '임대차 보호'
 - 우파 시각: '공급 확대', '규제 완화', '재건축 완화'

7️⃣ 대북·안보
 - 좌파 시각: '긴장 완화', '대화·외교 우선', '확성기 중단'
 - 우파 시각: '강경 대응', '확성기 재개', '안보 우선'

8️⃣ 정치/사법
 - 좌파 시각: '검찰권 남용', '언론장악', '사법독립 위기'
 - 우파 시각: '법과 원칙', '검찰개혁 실패', '정치적 기소 남발'

9️⃣ 온라인 밈 / 세대갈등
 - 좌파 시각: '청년 소외', '젠더 혐오 비판', '공정 담론의 왜곡'
 - 우파 시각: 'PC주의 피로', '역차별', '이대남 무시', '페미 과잉'

판단 규칙:
- 긍정적으로 언급된 정책/인물/사건이 어느 진영의 프레임과 일치하는지를 본다.
- 비판이 어느 쪽을 향하는가를 핵심으로 삼는다.
- 풍자, 비꼼, 이모티콘, 인터넷 밈이라도 프레임 방향성은 유지된다.

출력은 반드시 '좌파' 또는 '우파' 한 단어만 하라.
"""

        user_prompt = f"""댓글: {comment_text}

사전확률 힌트:
- 좌파 prior: {left_prior:.3f}
- 우파 prior: {right_prior:.3f}

출력: 좌파 또는 우파 (한 단어만)
"""

        # Ollama 사용 가능할 때만 LLM 시도
        if self.ollama_available:
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": f"{system_prompt}\n\n{user_prompt}",
                        "stream": False,
                        "options": {"temperature": 0.2, "num_predict": 5, "num_ctx": 4096}
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    result = response.json().get("response", "").strip()
                    if any(x in result for x in ["좌파", "좌", "left"]):
                        return "좌파"
                    elif any(x in result for x in ["우파", "우", "right"]):
                        return "우파"
            except Exception:
                # 연결 실패 시 조용히 키워드 기반으로 전환 (에러 메시지 출력 안 함)
                pass

        # 키워드 기반 분류
        return self._keyword_based(comment_text, left_prior, right_prior)

    def _keyword_based(self, text: str, left_prior: float = 0.5, right_prior: float = 0.5) -> str:
        """키워드 + 사전확률 기반 간이 분류"""
        t = text.lower()
        l = sum(1 for kw in self.left_keywords if kw in t)
        r = sum(1 for kw in self.right_keywords if kw in t)
        l_score = left_prior + l
        r_score = right_prior + r
        return "좌파" if l_score >= r_score else "우파"

    def batch_reclassify(self, comments: List[Dict]) -> List[Dict]:
        """여러 댓글 일괄 재분류 (1차 확률 기반 priors 반영)"""
        reclassified = []
        for comment in comments:
            label = comment.get("political_orientation", "판단불가")
            conf = comment.get("classification_confidence", 0.5)
            lp = comment.get("left_prob", 0.5)
            rp = comment.get("right_prob", 0.5)

            if label in ("판단불가", "중도") or conf < 0.6:
                new_label = self.force_reclassify(comment["text"], left_prior=lp, right_prior=rp)
                comment["original_orientation"] = label
                comment["political_orientation"] = new_label
                comment["was_reclassified"] = True
                print(f"[재분류] {label} → {new_label} | {comment['text'][:40]}...")
            else:
                comment["was_reclassified"] = False
            reclassified.append(comment)
        return reclassified
