"""
페르소나 토론 실행 모듈
학습된 좌우파 페르소나가 공격적으로 토론
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import requests


class PersonaDebater:
    """페르소나 토론 클래스"""
    
    def __init__(self, use_local_model: bool = False):
        self.use_local_model = use_local_model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Ollama 백업 (로컬 모델 실패 시)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "solar-mini")  # SOLAR-Mini-Instruct 사용
        
        self.left_persona = None
        self.right_persona = None
        
        self.models_dir = Path("models")
    
    def load_persona(self, orientation: str) -> Optional[object]:
        """학습된 페르소나 로드"""
        model_path = self.models_dir / f"persona_{orientation.lower()}_lora"
        
        if not model_path.exists():
            print(f"Warning: {orientation} 페르소나 모델이 없습니다. Ollama로 대체합니다.")
            return None
        
        if not self.use_local_model:
            print(f"{orientation} 페르소나: Ollama 사용")
            return None
        
        try:
            print(f"{orientation} 페르소나 로딩 중...")
            
            # 토크나이저 로드
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            
            # 베이스 모델 + LoRA 어댑터 로드
            base_model_name = "Upstage/SOLAR-Mini-Instruct"
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
            )
            
            # LoRA 어댑터 적용
            model = PeftModel.from_pretrained(base_model, str(model_path))
            
            if self.device == "cuda":
                model = model.to(self.device)
            
            model.eval()
            
            print(f"✓ {orientation} 페르소나 로드 완료")
            
            return {
                'model': model,
                'tokenizer': tokenizer,
                'orientation': orientation,
            }
            
        except Exception as e:
            print(f"Error: {orientation} 페르소나 로드 실패: {e}")
            print("Ollama로 대체합니다.")
            return None
    
    def initialize_personas(self):
        """좌우파 페르소나 초기화"""
        print("\n페르소나 초기화 중...")
        
        self.left_persona = self.load_persona("좌파")
        self.right_persona = self.load_persona("우파")
        
        if not self.left_persona and not self.right_persona:
            print("로컬 모델을 사용할 수 없습니다. Ollama 모드로 전환합니다.")
            self.use_local_model = False
    
    def generate_response_local(
        self, 
        persona: Dict, 
        topic: str, 
        opponent_message: str = None,
        max_length: int = 150
    ) -> str:
        """로컬 모델로 응답 생성"""
        model = persona['model']
        tokenizer = persona['tokenizer']
        orientation = persona['orientation']
        
        # 프롬프트 구성 (한국어 강제)
        if opponent_message:
            instruction = f"{topic}에 대해 상대방의 주장을 반박하며 {orientation} 관점에서 공격적으로 의견을 말해주세요. 반드시 순수 한국어만 사용하고 영어 단어는 절대 쓰지 마세요."
            input_text = f"상대방 주장: {opponent_message}"
        else:
            instruction = f"{topic}에 대해 {orientation} 관점에서 공격적이고 비판적으로 의견을 말해주세요. 반드시 순수 한국어만 사용하고 영어 단어는 절대 쓰지 마세요."
            input_text = ""
        
        if input_text:
            prompt = f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:
"""
        else:
            prompt = f"""### Instruction:
{instruction}

### Response:
"""
        
        # 토크나이징
        inputs = tokenizer(prompt, return_tensors="pt")
        if self.device == "cuda":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 생성
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.8,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        # 디코딩
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Response 부분만 추출
        if "### Response:" in response:
            response = response.split("### Response:")[-1].strip()
        
        return response
    
    def generate_response_ollama(
        self,
        orientation: str,
        topic: str,
        opponent_message: str = None,
        conversation_history: List[Dict] = None
    ) -> str:
        """Ollama로 응답 생성"""
        
        # 시스템 프롬프트
        if orientation == "좌파":
            system_prompt = """당신은 진보 성향의 공격적이고 비판적인 한국인 토론자입니다.
복지, 평등, 노동자 권리를 강력히 주장하며 재벌과 기득권을 신랄하게 비판합니다.
말투는 공격적이고 비아냥거리며, SNL/블랙코미디 스타일로 말합니다.

**절대 규칙: 오직 순수 한글로만 말하세요!**
- 영어 단어 사용 절대 금지 (예: policy, economy, welfare 등)
- 일본어 사용 절대 금지
- 한자어도 가능한 순수 한글로 표현
- 외국어가 나오려고 하면 즉시 한글로 바꾸세요

올바른 표현:
- "정책이 문제다" (O)
- "policy가 문제다" (X)
- "복지를 늘려야" (O)  
- "welfare를 늘려야" (X)

반말을 사용하고, ㅋㅋ, ㅉㅉ 같은 한글 표현을 자주 쓰며, 가끔 욕설도 섞어 재미있게 말합니다."""
        else:
            system_prompt = """당신은 보수 성향의 공격적이고 비판적인 한국인 토론자입니다.
시장경제, 안보, 전통 가치, 법과 질서를 강력히 주장하며 좌파 정책을 신랄하게 비판합니다.
말투는 공격적이고 비아냥거리며, SNL/블랙코미디 스타일로 말합니다.

**절대 규칙: 오직 순수 한글로만 말하세요!**
- 영어 단어 사용 절대 금지 (예: freedom, security, market 등)
- 일본어 사용 절대 금지
- 한자어도 가능한 순수 한글로 표현
- 외국어가 나오려고 하면 즉시 한글로 바꾸세요

올바른 표현:
- "시장이 답이다" (O)
- "market이 답이다" (X)
- "안보가 중요해" (O)
- "security가 중요해" (X)

반말을 사용하고, ㅋㅋ, ㅉㅉ 같은 한글 표현을 자주 쓰며, 가끔 욕설도 섞어 재미있게 말합니다."""
        
        # 사용자 프롬프트
        if opponent_message:
            user_prompt = f"""주제: {topic}

상대방이 이렇게 말했습니다:
"{opponent_message}"

이제 당신의 차례입니다. 상대방의 주장을 신랄하게 반박하고 당신의 의견을 공격적으로 말하세요.

**중요: 영어, 일본어, 한자 절대 금지! 순수 한글로만 말하세요!**
(2-3문장으로 간결하고 강렬하게)"""
        else:
            user_prompt = f"""주제: {topic}

이 주제에 대해 당신의 의견을 공격적이고 비판적으로 말하세요.

**중요: 영어, 일본어, 한자 절대 금지! 순수 한글로만 말하세요!**
(2-3문장으로 간결하고 강렬하게)"""
        
        try:
            # 한국어 강제를 위한 최종 프롬프트
            final_prompt = f"""{system_prompt}

{user_prompt}

**마지막 경고: 영어(English), 일본어(日本語), 한자(漢字) 사용 시 즉시 실격입니다!**
**오직 한글로만 응답하세요. 예: "정책", "경제", "복지", "시장" 등**"""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": final_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,
                        "top_p": 0.9,
                        "num_predict": 150,
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                return result if result else f"[{orientation}] 할 말이 없네 ㅋㅋ"
            else:
                return f"[{orientation}] 응답 생성 실패"
                
        except Exception as e:
            print(f"Ollama 오류: {e}")
            return self._fallback_response(orientation, topic, opponent_message)
    
    def _fallback_response(self, orientation: str, topic: str, opponent_message: str = None) -> str:
        """백업 응답 (Ollama 실패 시)"""
        if orientation == "좌파":
            responses = [
                f"또 {topic} 타령이냐? ㅋㅋ 서민은 안중에도 없지",
                f"{topic}? 재벌이나 배불리는 정책 그만해라 진짜",
                f"에휴 {topic} 가지고 뭘 하겠다고 ㅉㅉ 복지나 신경 써라",
            ]
        else:
            responses = [
                f"{topic}? 또 포퓰리즘 하려고? 나라 거덜낼 작정이냐",
                f"좌빨들 {topic} 타령 ㅋㅋ 안보나 챙겨라",
                f"{topic} 이런 소리 하니까 경제가 이 모양이지 ㅉㅉ",
            ]
        
        import random
        return random.choice(responses)
    
    def start_debate(
        self,
        topic: str,
        rounds: int = 5,
        save_result: bool = True
    ) -> List[Dict]:
        """토론 시작"""
        print("\n" + "=" * 60)
        print(f"페르소나 토론 시작!")
        print(f"주제: {topic}")
        print(f"라운드: {rounds}")
        print("=" * 60 + "\n")
        
        debate_log = []
        previous_message = None
        
        for round_num in range(1, rounds + 1):
            print(f"\n[라운드 {round_num}]")
            print("-" * 60)
            
            # 좌파 발언
            print("좌파 페르소나 생성 중...")
            if self.left_persona and self.use_local_model:
                left_message = self.generate_response_local(
                    self.left_persona,
                    topic,
                    previous_message
                )
            else:
                left_message = self.generate_response_ollama(
                    "좌파",
                    topic,
                    previous_message
                )
            
            print(f"🔴 좌파: {left_message}\n")
            
            debate_log.append({
                'round': round_num,
                'speaker': '좌파',
                'message': left_message,
            })
            
            # 우파 발언
            print("우파 페르소나 생성 중...")
            if self.right_persona and self.use_local_model:
                right_message = self.generate_response_local(
                    self.right_persona,
                    topic,
                    left_message
                )
            else:
                right_message = self.generate_response_ollama(
                    "우파",
                    topic,
                    left_message
                )
            
            print(f"🔵 우파: {right_message}\n")
            
            debate_log.append({
                'round': round_num,
                'speaker': '우파',
                'message': right_message,
            })
            
            previous_message = right_message
        
        print("=" * 60)
        print("토론 종료!")
        print("=" * 60)
        
        # 결과 저장
        if save_result:
            self._save_debate_log(topic, debate_log)
        
        return debate_log
    
    def _save_debate_log(self, topic: str, debate_log: List[Dict]):
        """토론 결과 저장"""
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 저장
        json_file = results_dir / f"debate_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                'topic': topic,
                'timestamp': timestamp,
                'rounds': len(debate_log) // 2,
                'debate': debate_log,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 토론 결과 저장: {json_file}")


def main():
    """테스트용 메인 함수"""
    print("페르소나 토론 테스트")
    print("=" * 60)
    
    # 토론자 초기화
    debater = PersonaDebater(use_local_model=False)  # Ollama 모드
    debater.initialize_personas()
    
    # 토론 시작
    topic = "현재 정부의 경제 정책"
    debate_log = debater.start_debate(topic, rounds=3)
    
    print(f"\n총 {len(debate_log)}개 발언 생성됨")


if __name__ == "__main__":
    main()

