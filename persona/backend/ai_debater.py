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

<<<<<<< Updated upstream
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
=======
        # 토론 주제 (summary_sentences) 구성
        topic_summary = "\n".join(self.keywords) if self.keywords else "정치, 사회"

        # 이전 응답들 (중복 방지용)
        previous_responses_str = ""
        if self.previous_responses:
            recent_responses = self.previous_responses[-5:]  # 최근 5개만
            previous_responses_str = "\n".join([f"- {resp[:100]}..." for resp in recent_responses])

        # 시스템 프롬프트
        system_prompt = f"""{persona_prompt}

중요 규칙:
1. 이전에 했던 말을 반복하지 마세요.
2. 새로운 관점이나 논거를 제시하세요.
3. 한국어로 자연스럽게 작성하세요.
4. 댓글 스타일로 간결하게 작성하세요 (1문장).
5. 상대방을 비난하세요
6. 실제 사람처럼 해줘
7. ㅋㅋ 같은 인터넷 말투 같은것도 사용해줘 
8. 공격적으로 자주 욕도 하고 강한 주장을 펼치세요."""

        # 사용자 프롬프트
        user_prompt = f"""현재 토론 주제 (영상 요약):
{topic_summary}

최근 대화:
{conversation_history}

상대방: {opponent_text}

당신의 응답을 작성하세요. 다음 사항을 반드시 지켜주세요:
- 이전에 했던 다음 표현들을 반복하지 마세요:
{previous_responses_str if previous_responses_str else "(첫 발언입니다)"}

- 위 영상 요약 내용과 관련된 새로운 논점을 제시하세요.
- 2-3문장으로 간결하게 작성하세요.
- 유튜브 댓글 스타일로 자연스럽게 작성하세요."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,  # 다양성을 위해 높은 temperature
                max_tokens=100,
                presence_penalty=0.6,  # 반복 억제
                frequency_penalty=0.6   # 반복 억제
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            # 생성된 응답이 너무 길면 자르기
            if len(generated_text) > 60:
                sentences = generated_text.split('.')
                generated_text = '.'.join(sentences[:3]) + '.'
            
            # 이전 응답에 추가 (중복 방지용)
            self.previous_responses.append(generated_text)
            
            # 너무 많이 쌓이면 오래된 것 제거
            if len(self.previous_responses) > 20:
                self.previous_responses = self.previous_responses[-20:]
            
            return generated_text or f"{side_name}의 입장에서 더 생각해볼 필요가 있겠네요."
>>>>>>> Stashed changes

        except Exception as e:
            print(f"⚠ 응답 생성 실패 ({self.side.name}): {e}")
            return "음... 다시 생각해볼게요."


class DebaterManager:
    """토론자 관리 (경량 모델 + LLM 파이프라인 공유)"""

    def __init__(self, analysis: AnalysisResult, persona_engine: CommentPersonaEngine):
        self.analysis = analysis
        self.persona_engine = persona_engine
<<<<<<< Updated upstream
=======
        self.keywords = keywords or []
        
        print(f"\n{'='*60}")
        print(f"🤖 AI 토론자 초기화 중... (모델: {model})")
        print(f"{'='*60}")
        print(f"\n🎯 토론 주제:")
        if self.keywords:
            # 1문장 주제면 크게 출력
            if len(self.keywords) == 1:
                print(f"\n   💬 \"{self.keywords[0]}\"\n")
            else:
                for i, sentence in enumerate(self.keywords, 1):
                    print(f"   {i}. {sentence}")
        else:
            print("   (주제 없음)")
        print(f"{'='*60}\n")
>>>>>>> Stashed changes

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
