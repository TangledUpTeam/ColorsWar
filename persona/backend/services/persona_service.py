"""
페르소나 생성 서비스
수집된 댓글을 기반으로 LLM을 통해 페르소나를 생성합니다.
"""
from typing import Dict, Optional
from ..core.state import AppState
from ..config.settings import settings


class PersonaService:
    """페르소나 생성 및 조회 비즈니스 로직"""
    
    def __init__(self, app_state: AppState):
        self.app_state = app_state
        self.persona_engine = app_state.persona_engine
    
    def generate_personas(self) -> Dict:
        """
        수집된 좌/우 댓글을 기반으로 LLM이 페르소나 생성
        
        Returns:
            Dict: 생성된 좌파/우파 페르소나 정보
            
        Raises:
            ValueError: 댓글 수가 부족한 경우
            RuntimeError: 페르소나 생성 실패 시
        """
        min_comments = settings.min_comments_for_persona
        left_count = len(self.persona_engine.left_comments)
        right_count = len(self.persona_engine.right_comments)
        
        if left_count < min_comments or right_count < min_comments:
            raise ValueError(
                f"댓글이 충분하지 않습니다. "
                f"좌:{left_count}, 우:{right_count} "
                f"(각 {min_comments}개 이상 필요)"
            )
        
        left_persona = self.persona_engine.generate_persona_via_llm("left")
        right_persona = self.persona_engine.generate_persona_via_llm("right")
        
        if not left_persona or not right_persona:
            raise RuntimeError("페르소나 생성 실패")
        
        return {
            "message": "페르소나 생성 완료",
            "left_persona": left_persona,
            "right_persona": right_persona
        }
    
    def get_persona(self, side: str) -> Optional[Dict]:
        """
        특정 성향의 페르소나 조회
        
        Args:
            side: "left" 또는 "right"
            
        Returns:
            Optional[Dict]: 페르소나 정보 또는 None
        """
        return self.persona_engine.get_persona(side)
    
    def is_ready(self) -> bool:
        """
        페르소나가 준비되었는지 확인
        
        Returns:
            bool: 준비 완료 여부
        """
        return self.persona_engine.is_ready()

