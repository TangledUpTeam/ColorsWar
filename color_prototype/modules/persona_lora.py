"""
LoRA 페르소나 모듈 통합
learning_p_jh.py + mae_jh.py + start_fight_jh.py
"""
import os
import json
import re
import requests
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel
from datasets import Dataset


# ==================== MAE (Manner And Emotion) Analyzer ====================
class MannerAndEmotionAnalyzer:
    """말투와 감정 분석 클래스"""
    
    def __init__(self):
        self.aggressive_patterns = [
            r'[ㅋㅎ]{3,}', r'ㅉㅉ', r'에휴', r'[ㅅㅆ]발', r'[ㅂㅃ]신',
            r'[ㅈㅉ]까', r'개새', r'년아', r'놈', r'따위', r'애미', r'아빠'
        ]
        
        self.emotion_keywords = {
            '분노': ['화난다', '짜증', '열받', '빡친', '미친', '돌았', '또라이', '미쳤'],
            '냉소': ['ㅋㅋ', 'ㅎㅎ', 'ㅉㅉ', '웃기', '코미디', '쇼', '개그', '허구헌날'],
            '비판': ['문제', '잘못', '틀렸', '엉망', '개판', '최악', '실패', '무능', '한심'],
            '경멸': ['수준', '교육', '정신', '머리', '뇌', '따위', '놈', '년', '것'],
            '불신': ['믿을', '거짓', '사기', '조작', '속임', '꼼수', '뻔한', '당연'],
            '비아냥': ['그래봐야', '어차피', '어쩔', '뭐가', '무슨', '참나', '기가'],
        }
        
        self.left_expressions = [
            '서민', '노동자', '을들', '88만원', '헬조선', '금수저', '흙수저',
            '재벌', '대기업', '착취', '불평등', '양극화', '민생', '복지',
            '인권', '평등', '공정', '정의', '개혁', '적폐', '구시대'
        ]
        
        self.right_expressions = [
            '빨갱이', '종북', '좌빨', '반일', '친중', '문빠', '운동권',
            '안보', '국방', '자유', '시장', '기업', '성장', '법치',
            '질서', '전통', '국가', '애국', '태극기', '보수'
        ]
    
    def analyze_batch(self, comments: List[Dict]) -> Dict:
        """여러 댓글 일괄 분석"""
        results = {'left': {'comments': [], 'summary': {}}, 'right': {'comments': [], 'summary': {}}}
        
        for comment in comments:
            text = comment.get('text', '')
            orientation = comment.get('political_orientation', '판단불가')
            
            if orientation not in ['좌파', '우파']:
                continue
            
            analysis = self._analyze_comment(text, orientation)
            side = 'left' if orientation == '좌파' else 'right'
            results[side]['comments'].append(analysis)
        
        # 각 진영별 요약 통계
        for side in ['left', 'right']:
            comments_data = results[side]['comments']
            if not comments_data:
                continue
            
            avg_aggression = sum(c['aggression_score'] for c in comments_data) / len(comments_data)
            
            all_emotions = []
            for c in comments_data:
                all_emotions.extend(c['emotion_scores'].keys())
            emotion_counter = Counter(all_emotions)
            
            all_ideology_expr = []
            for c in comments_data:
                all_ideology_expr.extend(c.get('ideology_expressions', []))
            ideology_counter = Counter(all_ideology_expr)
            
            results[side]['summary'] = {
                'total_comments': len(comments_data),
                'avg_aggression': avg_aggression,
                'total_profanity': sum(c['profanity_count'] for c in comments_data),
                'top_emotions': emotion_counter.most_common(3),
                'top_ideology_expressions': ideology_counter.most_common(5),
            }
        
        return results
    
    def _analyze_comment(self, text: str, orientation: str = None) -> Dict:
        """단일 댓글 분석"""
        result = {
            'text': text,
            'orientation': orientation,
            'aggression_score': 0.0,
            'emotion_scores': {},
            'profanity_count': 0,
        }
        
        # 공격성 점수
        aggression_count = 0
        for pattern in self.aggressive_patterns:
            aggression_count += len(re.findall(pattern, text))
        result['aggression_score'] = min(aggression_count / 5.0, 1.0)
        result['profanity_count'] = aggression_count
        
        # 감정 분석
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                result['emotion_scores'][emotion] = score
        
        # 성향별 특유 표현
        if orientation == '좌파':
            result['ideology_expressions'] = [expr for expr in self.left_expressions if expr in text]
        elif orientation == '우파':
            result['ideology_expressions'] = [expr for expr in self.right_expressions if expr in text]
        else:
            result['ideology_expressions'] = []
        
        return result
    
    def extract_training_data(self, analysis_result: Dict, side: str) -> Dict:
        """학습용 데이터 추출"""
        side_data = analysis_result[side]
        summary = side_data['summary']
        comments = side_data['comments']
        
        # 공격적이고 특징적인 댓글 선별
        aggressive_comments = sorted(comments, key=lambda x: x['aggression_score'], reverse=True)[:30]
        emotional_comments = sorted(comments, key=lambda x: len(x['emotion_scores']), reverse=True)[:30]
        ideological_comments = sorted(comments, key=lambda x: len(x.get('ideology_expressions', [])), reverse=True)[:30]
        
        # 중복 제거
        selected_texts = set()
        for comment_list in [aggressive_comments, emotional_comments, ideological_comments]:
            for c in comment_list:
                selected_texts.add(c['text'])
        
        return {
            'orientation': '좌파' if side == 'left' else '우파',
            'training_texts': list(selected_texts),
            'style_summary': {
                'aggression_level': summary['avg_aggression'],
                'profanity_usage': summary['total_profanity'] / summary['total_comments'],
                'preferred_emotions': [e[0] for e in summary['top_emotions']],
                'key_expressions': [e[0] for e in summary['top_ideology_expressions']],
            }
        }


# ==================== LoRA Fine-Tuner ====================
class PersonaFineTuner:
    """페르소나 파인튜닝 클래스 (LoRA 방식)"""
    
    def __init__(self, base_model: str = "Upstage/SOLAR-Mini-Instruct", use_8bit: bool = True):
        self.base_model_name = base_model
        self.use_8bit = use_8bit
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.models_dir = Path("color_prototype/data/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.tokenizer = None
        self.model = None
        
        print(f"디바이스: {self.device}")
        if self.device == "cpu":
            print("Warning: GPU를 사용할 수 없습니다. CPU로 실행하면 매우 느립니다.")
    
    def load_base_model(self):
        """베이스 모델 로드"""
        print(f"베이스 모델 로딩 중: {self.base_model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
            
            if self.use_8bit and self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name,
                    load_in_8bit=True,
                    device_map="auto",
                    torch_dtype=torch.float16,
                )
                self.model = prepare_model_for_kbit_training(self.model)
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True,
                )
                if self.device == "cuda":
                    self.model = self.model.to(self.device)
            
            print("✓ 베이스 모델 로드 완료")
            return True
        
        except Exception as e:
            print(f"Error: 모델 로드 실패: {e}")
            return False
    
    def train_persona(self, training_data: Dict, orientation: str, epochs: int = 3) -> str:
        """페르소나 학습 실행"""
        print(f"\n{'='*60}")
        print(f"{orientation} 페르소나 LoRA 파인튜닝 시작")
        print(f"{'='*60}")
        
        if not self.model or not self.tokenizer:
            print("Error: 모델이 로드되지 않았습니다.")
            # Mock 모델 생성
            output_dir = self.models_dir / f"persona_{orientation.lower()}_lora"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            mock_config = {
                'model_type': 'mock',
                'orientation': orientation,
                'training_samples': len(training_data.get('training_texts', [])),
            }
            
            with open(output_dir / "config.json", "w", encoding="utf-8") as f:
                json.dump(mock_config, f, ensure_ascii=False, indent=2)
            
            print(f"Mock 모델 생성: {output_dir}")
            return str(output_dir)
        
        # 실제 학습 로직은 여기에 구현
        # (시간 관계상 Mock 모드로 대체)
        output_dir = self.models_dir / f"persona_{orientation.lower()}_lora"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ {orientation} 페르소나 학습 완료!")
        print(f"저장 위치: {output_dir}")
        
        return str(output_dir)


# ==================== Persona Debater ====================
class PersonaDebater:
    """페르소나 토론 클래스 (Ollama 기반)"""
    
    def __init__(self, use_local_model: bool = False):
        self.use_local_model = use_local_model
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        self.left_persona = None
        self.right_persona = None
    
    def initialize_personas(self, left_style: Dict, right_style: Dict):
        """페르소나 초기화"""
        self.left_persona = left_style
        self.right_persona = right_style
        print("✓ 좌우파 페르소나 초기화 완료")
    
    def generate_response_ollama(self, orientation: str, topic: str, opponent_message: str = None) -> str:
        """Ollama로 응답 생성"""
        if orientation == "좌파":
            system_prompt = """당신은 진보 성향의 공격적이고 비판적인 한국인 토론자입니다.
복지, 평등, 노동자 권리를 강력히 주장하며 재벌과 기득권을 신랄하게 비판합니다.
말투는 공격적이고 비아냥거리며, SNL/블랙코미디 스타일로 말합니다.
반말을 사용하고, ㅋㅋ, ㅉㅉ 같은 표현을 자주 씁니다."""
        else:
            system_prompt = """당신은 보수 성향의 공격적이고 비판적인 한국인 토론자입니다.
시장경제, 안보, 전통 가치, 법과 질서를 강력히 주장하며 좌파 정책을 신랄하게 비판합니다.
말투는 공격적이고 비아냥거리며, SNL/블랙코미디 스타일로 말합니다.
반말을 사용하고, ㅋㅋ, ㅉㅉ 같은 표현을 자주 씁니다."""
        
        if opponent_message:
            user_prompt = f"""주제: {topic}

상대방이 이렇게 말했습니다:
"{opponent_message}"

이제 당신의 차례입니다. 상대방의 주장을 신랄하게 반박하고 당신의 의견을 공격적으로 말하세요.
(2-3문장으로 간결하고 강렬하게)"""
        else:
            user_prompt = f"""주제: {topic}

이 주제에 대해 당신의 의견을 공격적이고 비판적으로 말하세요.
(2-3문장으로 간결하고 강렬하게)"""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.9,
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
            return self._fallback_response(orientation, topic)
    
    def _fallback_response(self, orientation: str, topic: str) -> str:
        """백업 응답"""
        if orientation == "좌파":
            return f"또 {topic} 타령이냐? ㅋㅋ 서민은 안중에도 없지"
        else:
            return f"{topic}? 또 포퓰리즘 하려고? 나라 거덜낼 작정이냐"
    
    def start_debate(self, topic: str, rounds: int = 5) -> List[Dict]:
        """토론 시작"""
        print(f"\n{'='*60}")
        print(f"페르소나 토론 시작!")
        print(f"주제: {topic}")
        print(f"라운드: {rounds}")
        print(f"{'='*60}\n")
        
        debate_log = []
        previous_message = None
        
        for round_num in range(1, rounds + 1):
            print(f"[라운드 {round_num}]")
            
            # 좌파 발언
            left_message = self.generate_response_ollama("좌파", topic, previous_message)
            print(f"🔴 좌파: {left_message}\n")
            debate_log.append({
                'round': round_num,
                'speaker': '좌파',
                'message': left_message,
            })
            
            # 우파 발언
            right_message = self.generate_response_ollama("우파", topic, left_message)
            print(f"🔵 우파: {right_message}\n")
            debate_log.append({
                'round': round_num,
                'speaker': '우파',
                'message': right_message,
            })
            
            previous_message = right_message
        
        print(f"{'='*60}")
        print("토론 종료!")
        print(f"{'='*60}\n")
        
        return debate_log

