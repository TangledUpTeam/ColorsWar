"""
AI 토론자 시스템 (LLM 기반, CPU 경량 버전)
페르소나를 반영해 새로운 댓글 스타일로 토론 생성
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Optional
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from model.comment_persona_engine import CommentPersonaEngine
from .models import Side, DebateMessage, AnalysisResult, DebateState


class AIDebater:
    """AI 토론자 (경량 LLM 기반)"""

    def __init__(self, side: Side, analysis: AnalysisResult, persona_engine: CommentPersonaEngine, llm_pipeline):
        self.side = side
        self.analysis = analysis
        self.persona_engine = persona_engine
        self.llm = llm_pipeline  # ✅ pipeline 공유
        self.device = "cpu"

    def generate_response(self, state: DebateState, opponent_message: Optional[DebateMessage] = None) -> str:
        """토론 응답 생성 (경량 모델 기반)"""
        side_str = "left" if self.side == Side.LEFT else "right"
        persona_prompt = self.persona_engine.get_persona_prompt(side_str)

        conversation = ""
        for msg in state.messages[-4:]:
            speaker = "나" if msg.side == self.side else "상대"
            conversation += f"{speaker}: {msg.content}\n"

        topic = state.current_topic or "정치 논쟁"
        opponent_text = opponent_message.content if opponent_message else "이 사안에 대해 너의 생각은 뭐야?"

        prompt = f"""
{persona_prompt}

현재 주제: {topic}

최근 대화:
{conversation}
상대: {opponent_text}
나:"""

        try:
            result = self.llm(
                prompt,
                max_new_tokens=150,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.llm.tokenizer.eos_token_id
            )[0]["generated_text"]

            response = result[len(prompt):].strip()
            if len(response) > 200:
                response = response.split(".")[0] + "."
            return response or "그 부분은 좀 더 생각해봐야겠네요."

        except Exception as e:
            print(f"⚠ 응답 생성 실패 ({self.side.name}): {e}")
            return "음... 다시 생각해볼게요."


class DebaterManager:
    """토론자 관리 (경량 모델 + LLM 파이프라인 공유)"""

    def __init__(self, analysis: AnalysisResult, persona_engine: CommentPersonaEngine):
        self.analysis = analysis
        self.persona_engine = persona_engine

        # ✅ 경량 모델 설정
        self.model_name = "skt/kogpt2-base-v2"
        self.device = "cpu"
        print(f"🤖 대화 모델 로딩 중: {self.model_name} ({self.device})")

        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                device_map=None,
                low_cpu_mem_usage=True
            ).to(self.device)

            llm_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=-1
            )

            print("✓ 대화 모델 로딩 완료! (CPU 경량 모드)\n")
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            llm_pipeline = None

        # 두 토론자 생성
        self.left_debater = AIDebater(Side.LEFT, analysis, persona_engine, llm_pipeline)
        self.right_debater = AIDebater(Side.RIGHT, analysis, persona_engine, llm_pipeline)

    def generate_response(self, side: Side, state: DebateState, opponent_message: Optional[DebateMessage] = None):
        """토론자별 응답 생성"""
        if side == Side.LEFT:
            return self.left_debater.generate_response(state, opponent_message)
        else:
            return self.right_debater.generate_response(state, opponent_message)
