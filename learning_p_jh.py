"""
페르소나 파인튜닝 모듈 (LoRA 방식)
beomi/KoAlpaca-Polyglot-12.8B 기반 좌우파 페르소나 학습
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset


class PersonaFineTuner:
    """페르소나 파인튜닝 클래스"""
    
    def __init__(self, base_model: str = "Upstage/SOLAR-Mini-Instruct", use_8bit: bool = True):
        self.base_model_name = base_model
        self.use_8bit = use_8bit
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 모델 저장 경로
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.tokenizer = None
        self.model = None
        
        print(f"디바이스: {self.device}")
        if self.device == "cpu":
            print("Warning: GPU를 사용할 수 없습니다. CPU로 실행하면 매우 느립니다.")
    
    def load_base_model(self):
        """베이스 모델 로드"""
        print(f"베이스 모델 로딩 중: {self.base_model_name}")
        
        try:
            # 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
            
            # 모델 로드 (8bit 양자화 옵션)
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
            print("대안: 더 작은 모델(nlpai-lab/kullm-polyglot-5.8b)을 사용하거나 Mock 모드로 전환합니다.")
            return False
    
    def prepare_training_data(self, comments: List[str], style_summary: Dict, orientation: str) -> Dataset:
        """학습 데이터 준비"""
        print(f"{orientation} 페르소나 학습 데이터 준비 중...")
        
        # 시스템 프롬프트 생성
        system_prompt = self._create_system_prompt(style_summary, orientation)
        
        # 학습용 데이터 생성
        training_examples = []
        
        for comment in comments[:100]:  # 상위 100개만 사용
            # 입력-출력 쌍 생성
            # 주제를 추출하여 그에 대한 응답으로 학습
            example = {
                'instruction': f"{orientation} 관점에서 현재 이슈에 대해 공격적이고 비판적으로 의견을 말해주세요.",
                'input': "",
                'output': comment,
                'system': system_prompt,
            }
            training_examples.append(example)
        
        # 추가 학습 데이터: 스타일 강화
        style_examples = self._create_style_examples(style_summary, orientation)
        training_examples.extend(style_examples)
        
        print(f"총 {len(training_examples)}개 학습 샘플 생성")
        
        # Dataset 객체 생성
        dataset = Dataset.from_list(training_examples)
        
        return dataset
    
    def _create_system_prompt(self, style_summary: Dict, orientation: str) -> str:
        """스타일 기반 시스템 프롬프트 생성"""
        emotions = ", ".join(style_summary.get('preferred_emotions', []))
        expressions = ", ".join(style_summary.get('key_expressions', [])[:5])
        
        if orientation == "좌파":
            base = """당신은 진보 성향의 공격적이고 비판적인 토론자입니다.
복지, 평등, 노동자 권리, 재분배를 강력히 주장합니다.
기득권과 재벌, 보수 정치를 신랄하게 비판합니다.

**중요: 오직 한국어만 사용하세요. 영어나 외국어는 절대 사용하지 마세요.**"""
        else:
            base = """당신은 보수 성향의 공격적이고 비판적인 토론자입니다.
자유시장, 안보, 전통 가치, 법과 질서를 강력히 주장합니다.
좌파 정책과 포퓰리즘을 신랄하게 비판합니다.

**중요: 오직 한국어만 사용하세요. 영어나 외국어는 절대 사용하지 마세요.**"""
        
        style = f"""
말투 특징:
- 공격성: {"높음" if style_summary.get('aggression_level', 0) > 0.5 else "중간"}
- 주요 감정: {emotions}
- 자주 쓰는 표현: {expressions}
- 반말과 비아냥거림 사용
- 가끔 적절한 욕설 사용 (재미있게)
- SNL/블랙코미디 스타일
- 순수 한국어로만 표현"""
        
        return base + "\n" + style
    
    def _create_style_examples(self, style_summary: Dict, orientation: str) -> List[Dict]:
        """스타일 학습용 추가 예제 생성"""
        examples = []
        
        if orientation == "좌파":
            topics = [
                "재벌 특혜 정책",
                "최저임금 동결",
                "노동권 탄압",
                "복지 예산 삭감",
                "서민 경제"
            ]
            
            style_responses = [
                "아 진짜 ㅋㅋㅋ 또 재벌 감세? 서민은 죽으라는 소리네. 이게 나라냐",
                "최저임금도 못 올려주면서 대기업한테는 세금 깎아주기 바쁘네 ㅉㅉ",
                "노동자들 권리는 개나 줘버리고 기업만 살찌우는 정책 개판이네",
                "복지 예산은 줄이면서 부자 감세는 왜 이리 열심히 하냐? 역겹다 진짜",
                "서민 경제? 그딴 거 신경이나 쓰냐 ㅋㅋ 재벌 배만 불리면 그만이지"
            ]
        else:
            topics = [
                "포퓰리즘 정책",
                "안보 태세",
                "무분별한 복지",
                "시장 경제",
                "국가 경쟁력"
            ]
            
            style_responses = [
                "표 얻으려고 돈 뿌리기만 하면 나라 거덜나는 거 모르냐? 좌빨 포퓰리즘 질렸다",
                "북한은 핵 개발하는데 우리는 평화타령 ㅋㅋ 안보 개판 만들려고?",
                "공짜로 다 줘봐라. 나라 경제 망하면 책임질 거냐? 생각이란 걸 해라",
                "시장에 맡겨야 할 걸 정부가 다 간섭하니까 경제가 이 모양이지 ㅉㅉ",
                "규제 투성이로 만들어놓고 경쟁력 떨어진다고? 당연한 거 아니냐"
            ]
        
        for topic, response in zip(topics, style_responses):
            examples.append({
                'instruction': f"{topic}에 대해 {orientation} 관점에서 공격적으로 의견을 말해주세요.",
                'input': "",
                'output': response,
                'system': self._create_system_prompt(style_summary, orientation),
            })
        
        return examples
    
    def format_instruction(self, example: Dict) -> Dict:
        """Alpaca 포맷으로 변환"""
        if not self.tokenizer:
            return example
        
        # Alpaca 포맷
        if example['input']:
            text = f"""### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
        else:
            text = f"""### Instruction:
{example['instruction']}

### Response:
{example['output']}"""
        
        # 토크나이징
        result = self.tokenizer(
            text,
            truncation=True,
            max_length=512,
            padding="max_length",
        )
        
        result["labels"] = result["input_ids"].copy()
        
        return result
    
    def train_persona(
        self, 
        dataset: Dataset, 
        orientation: str,
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
    ) -> str:
        """페르소나 학습 실행"""
        print(f"\n{'='*60}")
        print(f"{orientation} 페르소나 LoRA 파인튜닝 시작")
        print(f"{'='*60}")
        
        if not self.model or not self.tokenizer:
            print("Error: 모델이 로드되지 않았습니다.")
            return None
        
        # LoRA 설정
        lora_config = LoraConfig(
            r=8,  # LoRA rank
            lora_alpha=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # SOLAR-Mini attention 모듈
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        # LoRA 적용
        model = get_peft_model(self.model, lora_config)
        model.print_trainable_parameters()
        
        # 데이터셋 전처리
        tokenized_dataset = dataset.map(
            self.format_instruction,
            remove_columns=dataset.column_names,
        )
        
        # 학습 설정
        output_dir = self.models_dir / f"persona_{orientation.lower()}_lora"
        
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            learning_rate=learning_rate,
            fp16=True if self.device == "cuda" else False,
            logging_steps=10,
            save_strategy="epoch",
            optim="adamw_torch",
            warmup_steps=50,
        )
        
        # Trainer 초기화
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
        )
        
        # 학습 실행
        print(f"\n학습 시작... (에폭: {epochs})")
        trainer.train()
        
        # 모델 저장
        model.save_pretrained(str(output_dir))
        self.tokenizer.save_pretrained(str(output_dir))
        
        print(f"\n✓ {orientation} 페르소나 학습 완료!")
        print(f"저장 위치: {output_dir}")
        
        return str(output_dir)


class MockPersonaFineTuner:
    """실제 모델 없이 테스트용 Mock 클래스"""
    
    def __init__(self, base_model: str = "mock", use_8bit: bool = False):
        self.base_model_name = base_model
        print("Mock 모드로 실행됩니다.")
    
    def load_base_model(self):
        print("Mock: 베이스 모델 로드 완료")
        return True
    
    def prepare_training_data(self, comments: List[str], style_summary: Dict, orientation: str) -> Dict:
        print(f"Mock: {orientation} 학습 데이터 준비 ({len(comments)}개 댓글)")
        return {'mock': True, 'comments': comments, 'orientation': orientation}
    
    def train_persona(self, dataset: Dict, orientation: str, **kwargs) -> str:
        print(f"Mock: {orientation} 페르소나 학습 완료 (시뮬레이션)")
        
        # Mock 모델 파일 생성
        output_dir = Path("models") / f"persona_{orientation.lower()}_lora"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        mock_config = {
            'model_type': 'mock',
            'orientation': orientation,
            'training_samples': len(dataset.get('comments', [])),
        }
        
        with open(output_dir / "config.json", "w", encoding="utf-8") as f:
            json.dump(mock_config, f, ensure_ascii=False, indent=2)
        
        return str(output_dir)


def main():
    """테스트용 메인 함수"""
    print("페르소나 파인튜닝 테스트")
    print("=" * 60)
    
    # Mock 모드로 테스트
    tuner = MockPersonaFineTuner()
    
    if not tuner.load_base_model():
        print("모델 로드 실패")
        return
    
    # 테스트 데이터
    left_comments = [
        "재벌 특혜 정책 진짜 역겹다",
        "서민은 죽으라는 거냐",
        "복지 확대가 답이다",
    ]
    
    left_style = {
        'aggression_level': 0.7,
        'preferred_emotions': ['분노', '비판'],
        'key_expressions': ['서민', '재벌', '복지'],
    }
    
    # 학습 데이터 준비
    dataset = tuner.prepare_training_data(left_comments, left_style, "좌파")
    
    # 학습 실행
    model_path = tuner.train_persona(dataset, "좌파")
    
    print(f"\n최종 모델 경로: {model_path}")


if __name__ == "__main__":
    main()

