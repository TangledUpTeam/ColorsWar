"""
기존 페르소나 모듈 (kogpt2 기반)
경량 모델로 빠른 페르소나 생성 및 토론
"""
import os
import json
import re
import requests
from typing import List, Dict, Optional
from collections import Counter
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


class PersonaEngine:
    """댓글 기반 페르소나 생성 엔진 (kogpt2)"""
    
    def __init__(self):
        self.left_comments = []
        self.right_comments = []
        self.left_persona = None
        self.right_persona = None
        
        # kogpt2 모델 로드
        model_id = "skt/kogpt2-base-v2"
        print(f"🚀 페르소나 생성 LLM 로딩 중: {model_id}...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            ).to("cpu")
            
            self.llm = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1  # CPU
            )
            
            print("✓ 페르소나 생성 LLM 로딩 완료! (CPU 경량 모드)\n")
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            self.model, self.llm = None, None
    
    def add_comments(self, left_comments: List[str], right_comments: List[str]):
        """댓글 추가"""
        self.left_comments.extend([c.strip() for c in left_comments if c.strip()])
        self.right_comments.extend([c.strip() for c in right_comments if c.strip()])
        print(f"좌파 댓글: {len(self.left_comments)}개, 우파 댓글: {len(self.right_comments)}개")
    
    def generate_persona(self, side: str) -> Optional[Dict]:
        """페르소나 생성"""
        comments = self.left_comments if side == "left" else self.right_comments
        
        if len(comments) < 5:
            print(f"[{side}] 댓글 부족: {len(comments)}개")
            return self._create_default_persona(side, comments)
        
        side_name = '진보(좌파)' if side == 'left' else '보수(우파)'
        print(f"\n{'='*60}")
        print(f"🤖 {side_name} 페르소나 생성 시작... (댓글 {len(comments)}개)")
        print(f"{'='*60}\n")
        
        prompt = f"""다음은 {side_name} 성향의 정치 뉴스 댓글입니다.
말투, 감정, 가치관을 분석해 JSON으로 요약하세요.

댓글:
{chr(10).join(comments[:15])}

JSON 형식으로만 출력하세요:
{{
  "summary": "한 문장 요약",
  "values": ["핵심가치1", "핵심가치2"],
  "tone": ["말투특징1", "말투특징2"],
  "emotion": "감정스타일",
  "keywords": ["키워드1", "키워드2"],
  "quote_examples": ["예시1", "예시2"]
}}"""
        
        try:
            if not self.llm:
                raise RuntimeError("LLM이 초기화되지 않았습니다.")
            
            print("⏳ LLM 처리 중...")
            result = self.llm(
                prompt,
                max_new_tokens=300,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )[0]["generated_text"]
            
            json_start = result.find("{")
            json_end = result.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                print("⚠ JSON 응답 없음 → 기본 페르소나 생성")
                persona = self._create_default_persona(side, comments)
            else:
                try:
                    json_str = result[json_start:json_end]
                    persona = json.loads(json_str)
                except json.JSONDecodeError:
                    print("⚠ JSON 파싱 실패 → 기본 페르소나 생성")
                    persona = self._create_default_persona(side, comments)
            
            print(f"✅ {side_name} 페르소나 생성 완료!")
            
            if side == "left":
                self.left_persona = persona
            else:
                self.right_persona = persona
            
            return persona
        
        except Exception as e:
            print(f"❌ 페르소나 생성 실패: {e}")
            return self._create_default_persona(side, comments)
    
    def _create_default_persona(self, side: str, comments: List[str]) -> Dict:
        """기본 페르소나 생성"""
        words = []
        for c in comments:
            words.extend(re.findall(r'[가-힣]+', c))
        top_keywords = [w for w, _ in Counter(words).most_common(10) if len(w) >= 2]
        
        side_name = "진보(좌파)" if side == "left" else "보수(우파)"
        return {
            "summary": f"{side_name} 성향의 기본 페르소나",
            "values": ["사회 정의", "변화"] if side == "left" else ["안정", "전통"],
            "tone": ["열정적", "직설적"] if side == "left" else ["냉정한", "논리적"],
            "emotion": "확신",
            "keywords": top_keywords[:8],
            "quote_examples": comments[:3]
        }
    
    def get_persona_prompt(self, side: str) -> str:
        """페르소나 프롬프트 생성"""
        persona = self.left_persona if side == "left" else self.right_persona
        side_name = "진보(좌파)" if side == "left" else "보수(우파)"
        
        if not persona:
            return f"당신은 {side_name} 성향의 한국 댓글러입니다."
        
        return f"""당신은 {side_name} 성향의 한국 유튜브 댓글러입니다.

페르소나 특성:
- 요약: {persona.get('summary', 'N/A')}
- 핵심 가치: {', '.join(persona.get('values', []))}
- 말투: {', '.join(persona.get('tone', []))}
- 감정: {persona.get('emotion', 'N/A')}
- 자주 쓰는 키워드: {', '.join(persona.get('keywords', [])[:5])}

실제 댓글 예시:
{chr(10).join([f'- {ex}' for ex in persona.get('quote_examples', [])[:3]])}

위 패턴과 어투를 참고하여 자연스럽고 실감나는 댓글을 작성하세요."""


class DebateEngine:
    """AI 토론 엔진 (Ollama 기반)"""
    
    def __init__(self, persona_engine: PersonaEngine):
        self.persona_engine = persona_engine
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    def generate_response(self, side: str, topic: str, opponent_message: str = None) -> str:
        """응답 생성"""
        persona_prompt = self.persona_engine.get_persona_prompt(side)
        
        if opponent_message:
            user_prompt = f"""주제: {topic}

상대방 주장: {opponent_message}

위 주장에 대해 당신의 페르소나를 반영하여 반박하세요. (2-3문장)"""
        else:
            user_prompt = f"""주제: {topic}

이 주제에 대해 당신의 페르소나를 반영하여 의견을 말하세요. (2-3문장)"""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{persona_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 200
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                message = response.json().get("response", "").strip()
                if message:
                    return message
            
            # 폴백
            return self._fallback_response(side, topic)
        
        except Exception as e:
            print(f"⚠ 응답 생성 실패: {e}")
            return self._fallback_response(side, topic)
    
    def _fallback_response(self, side: str, topic: str) -> str:
        """폴백 응답"""
        if side == "left":
            return f"{topic}에 대해 복지 확대와 소득 재분배가 필요합니다. 서민을 위한 정책이 시급합니다."
        else:
            return f"{topic}에 대해 자유 시장 경제가 답입니다. 규제 완화로 경제를 살려야 합니다."
    
    def start_debate(self, topic: str, rounds: int = 5) -> List[Dict]:
        """토론 시작"""
        print(f"\n{'='*60}")
        print(f"🎭 AI 페르소나 토론 시작")
        print(f"주제: {topic}")
        print(f"라운드: {rounds}")
        print(f"{'='*60}\n")
        
        debate_log = []
        previous_message = None
        
        for round_num in range(1, rounds + 1):
            print(f"[라운드 {round_num}]")
            
            # 좌파 발언
            left_message = self.generate_response("left", topic, previous_message)
            print(f"🔴 좌파: {left_message}\n")
            debate_log.append({
                'round': round_num,
                'speaker': '좌파',
                'message': left_message
            })
            
            # 우파 발언
            right_message = self.generate_response("right", topic, left_message)
            print(f"🔵 우파: {right_message}\n")
            debate_log.append({
                'round': round_num,
                'speaker': '우파',
                'message': right_message
            })
            
            previous_message = right_message
        
        print(f"{'='*60}")
        print("토론 종료!")
        print(f"{'='*60}\n")
        
        return debate_log

