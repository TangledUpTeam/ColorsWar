"""
AI 페르소나 서비스
좌파/우파 페르소나가 학습된 댓글을 기반으로 토론
"""
import os
import requests
import json
from typing import List, Dict


class AIPersona:
    """AI 페르소나 베이스 클래스"""
    
    def __init__(self, orientation: str, training_comments: List[str]):
        self.orientation = orientation
        self.training_comments = training_comments
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.conversation_history = []
        
    def get_system_prompt(self) -> str:
        """페르소나별 시스템 프롬프트"""
        raise NotImplementedError
    
    def generate_response(self, opponent_message: str = None) -> str:
        """상대방 메시지에 대한 응답 생성"""
        raise NotImplementedError


class LeftPersona(AIPersona):
    """좌파 페르소나"""
    
    def __init__(self, training_comments: List[str]):
        super().__init__("좌파", training_comments)
    
    def get_system_prompt(self) -> str:
        comments_summary = "\n".join([f"- {c}" for c in self.training_comments[:30]])
        
        return f"""당신은 진보/좌파 성향의 AI 페르소나입니다.

다음은 실제 좌파 성향 댓글들에서 학습한 내용입니다:
{comments_summary}

당신의 입장:
- 복지 확대와 소득 재분배 강조
- 노동자와 서민의 권리 보호
- 환경 보호와 지속가능성 중시
- 소수자 인권과 평등 가치 옹호
- 정부의 적극적 시장 개입 지지
- 진보적이고 개혁적인 변화 추구

토론 스타일:
- 열정적이고 감정적
- 사회 정의와 평등을 강조
- 구체적인 사례와 통계 활용
- 상대방의 특권층 편향을 지적

학습한 댓글의 논조와 주장을 반영하여 응답하세요.
200-300자 내외로 간결하게 답변하세요."""

    def generate_response(self, opponent_message: str = None, topic: str = None) -> str:
        """응답 생성"""
        if opponent_message is None:
            # 첫 발언
            user_prompt = f"주제 '{topic}'에 대한 좌파 입장을 학습한 댓글을 바탕으로 주장하세요."
        else:
            # 반박
            user_prompt = f"상대방 주장: {opponent_message}\n\n위 우파 주장에 대해 학습한 좌파 댓글을 바탕으로 강력히 반박하세요."
        
        try:
            full_prompt = f"{self.get_system_prompt()}\n\n{user_prompt}"
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 300
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                message = response.json().get("response", "").strip()
                if message:
                    self.conversation_history.append({"role": "assistant", "content": message})
                    return message
            
            # 폴백 - 학습된 댓글 기반 응답
            if self.training_comments:
                # 학습된 댓글에서 키워드 추출하여 응답 생성
                keywords = []
                for comment in self.training_comments[:5]:
                    words = comment.split()
                    keywords.extend([w for w in words if len(w) > 2][:3])
                
                # 좌파 성향 키워드 강조
                left_keywords = ["복지", "평등", "노동", "환경", "인권", "재분배", "진보", "서민", "정부", "정책"]
                found_keywords = [kw for kw in keywords if any(left_kw in kw for left_kw in left_keywords)]
                
                if topic:
                    if found_keywords:
                        return f"주제 '{topic}'에 대해, 학습된 댓글에서 본 바와 같이 {', '.join(found_keywords[:2])} 등의 관점에서 복지 확대와 소득 재분배가 시급합니다. 서민을 위한 정책이 필요합니다."
                    else:
                        return f"주제 '{topic}'에 대해, 복지 확대와 소득 재분배가 시급합니다. 서민을 위한 정책이 필요합니다."
                else:
                    if found_keywords:
                        return f"학습된 댓글들을 보면 {', '.join(found_keywords[:2])} 등의 문제가 심각합니다. 복지 확대와 소득 재분배가 시급합니다. 서민을 위한 정책이 필요합니다."
                    else:
                        return "복지 확대와 소득 재분배가 시급합니다. 서민을 위한 정책이 필요합니다."
            else:
                return "복지 확대와 소득 재분배가 시급합니다. 서민을 위한 정책이 필요합니다."
            
        except Exception as e:
            print(f"좌파 페르소나 응답 생성 오류: {str(e)}")
            return "복지 확대와 소득 재분배가 시급합니다. 서민을 위한 정책이 필요합니다."


class RightPersona(AIPersona):
    """우파 페르소나"""
    
    def __init__(self, training_comments: List[str]):
        super().__init__("우파", training_comments)
    
    def get_system_prompt(self) -> str:
        comments_summary = "\n".join([f"- {c}" for c in self.training_comments[:30]])
        
        return f"""당신은 보수/우파 성향의 AI 페르소나입니다.

다음은 실제 우파 성향 댓글들에서 학습한 내용입니다:
{comments_summary}

당신의 입장:
- 자유 시장 경제와 기업 활동 중시
- 작은 정부와 규제 완화 지향
- 전통적 가치와 질서 존중
- 국가 안보와 국익 우선
- 개인의 책임과 자유 강조
- 실용주의와 점진적 변화 선호

토론 스타일:
- 논리적이고 실용적
- 경제 성장과 효율성 강조
- 역사적 사례와 경험 인용
- 상대방의 이상주의를 비판

학습한 댓글의 논조와 주장을 반영하여 응답하세요.
200-300자 내외로 간결하게 답변하세요."""

    def generate_response(self, opponent_message: str = None, topic: str = None) -> str:
        """응답 생성"""
        if opponent_message is None:
            # 첫 발언
            user_prompt = f"주제 '{topic}'에 대한 우파 입장을 학습한 댓글을 바탕으로 주장하세요."
        else:
            # 반박
            user_prompt = f"상대방 주장: {opponent_message}\n\n위 좌파 주장에 대해 학습한 우파 댓글을 바탕으로 논리적으로 반박하세요."
        
        try:
            full_prompt = f"{self.get_system_prompt()}\n\n{user_prompt}"
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 300
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                message = response.json().get("response", "").strip()
                if message:
                    self.conversation_history.append({"role": "assistant", "content": message})
                    return message
            
            # 폴백 - 학습된 댓글 기반 응답
            if self.training_comments:
                # 학습된 댓글에서 키워드 추출하여 응답 생성
                keywords = []
                for comment in self.training_comments[:5]:
                    words = comment.split()
                    keywords.extend([w for w in words if len(w) > 2][:3])
                
                # 우파 성향 키워드 강조
                right_keywords = ["시장", "안보", "전통", "규제완화", "보수", "자유경제", "기업", "성장", "효율", "개인"]
                found_keywords = [kw for kw in keywords if any(right_kw in kw for right_kw in right_keywords)]
                
                if topic:
                    if found_keywords:
                        return f"주제 '{topic}'에 대해, 학습된 댓글에서 본 바와 같이 {', '.join(found_keywords[:2])} 등의 관점에서 자유 시장 경제가 답입니다. 규제 완화로 경제를 살려야 합니다."
                    else:
                        return f"주제 '{topic}'에 대해, 자유 시장 경제가 답입니다. 규제 완화로 경제를 살려야 합니다."
                else:
                    if found_keywords:
                        return f"학습된 댓글들을 보면 {', '.join(found_keywords[:2])} 등의 문제가 있습니다. 자유 시장 경제가 답입니다. 규제 완화로 경제를 살려야 합니다."
                    else:
                        return "자유 시장 경제가 답입니다. 규제 완화로 경제를 살려야 합니다."
            else:
                return "자유 시장 경제가 답입니다. 규제 완화로 경제를 살려야 합니다."
            
        except Exception as e:
            print(f"우파 페르소나 응답 생성 오류: {str(e)}")
            return "자유 시장 경제가 답입니다. 규제 완화로 경제를 살려야 합니다."


class PersonaBattleService:
    """페르소나 간 토론 관리 서비스"""
    
    def __init__(self):
        self.left_persona = None
        self.right_persona = None
        
    def initialize_personas(self, left_comments: List[str], right_comments: List[str]):
        """페르소나 초기화"""
        self.left_persona = LeftPersona(left_comments)
        self.right_persona = RightPersona(right_comments)
        
    def start_debate(self, topic: str = "현재 정부 정책", rounds: int = 3) -> List[Dict]:
        """
        토론 시작
        
        Args:
            topic: 토론 주제
            rounds: 토론 라운드 수
            
        Returns:
            토론 메시지 리스트
        """
        if not self.left_persona or not self.right_persona:
            raise ValueError("페르소나가 초기화되지 않았습니다.")
        
        debate_messages = []
        
        print(f"\n{'='*60}")
        print(f"페르소나 토론 시작: {topic}")
        print(f"{'='*60}\n")
        
        # 1라운드: 좌파 먼저 시작
        print("[1라운드] 좌파 주장")
        left_message = self.left_persona.generate_response(topic=topic)
        debate_messages.append({
            "round": 1,
            "speaker": "좌파",
            "message": left_message,
            "timestamp": self._get_timestamp()
        })
        print(f"좌파: {left_message.encode('utf-8', errors='ignore').decode('utf-8')}\n")
        
        # 2라운드부터: 번갈아가며 반박
        for round_num in range(2, rounds + 1):
            # 우파 반박
            print(f"[{round_num}라운드] 우파 반박")
            right_message = self.right_persona.generate_response(
                opponent_message=debate_messages[-1]["message"]
            )
            debate_messages.append({
                "round": round_num,
                "speaker": "우파",
                "message": right_message,
                "timestamp": self._get_timestamp()
            })
            print(f"우파: {right_message.encode('utf-8', errors='ignore').decode('utf-8')}\n")
            
            # 좌파 재반박 (마지막 라운드가 아니면)
            if round_num < rounds:
                print(f"[{round_num}라운드] 좌파 재반박")
                left_message = self.left_persona.generate_response(
                    opponent_message=right_message
                )
                debate_messages.append({
                    "round": round_num,
                    "speaker": "좌파",
                    "message": left_message,
                    "timestamp": self._get_timestamp()
                })
                print(f"좌파: {left_message.encode('utf-8', errors='ignore').decode('utf-8')}\n")
        
        print(f"{'='*60}")
        print(f"토론 종료 (총 {len(debate_messages)}개 발언)")
        print(f"{'='*60}\n")
        
        return debate_messages
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프"""
        from datetime import datetime
        return datetime.now().isoformat()

