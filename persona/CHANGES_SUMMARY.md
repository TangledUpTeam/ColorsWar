# 변경 사항 요약

## 작업 완료 내역

### ✅ 요구사항
1. ✅ OpenAI GPT-4o-mini 사용 (기존 로컬 LLM 대체)
2. ✅ 좌/우 각 5개 댓글 랜덤 샘플링하여 페르소나 학습
3. ✅ YouTube 영상의 keywords를 토론 주제로 활용
4. ✅ 중복 방지 로직 (같은 말 반복하지 않음)
5. ✅ persona 폴더 내부 파일만 수정

---

## 수정된 파일 (persona 폴더 내부만)

### 1. `persona/backend/config/settings.py`
**변경 내용**:
- OpenAI API 키 설정 추가 (`openai_api_key`)
- OpenAI 모델 설정 추가 (`openai_model`, 기본값: "gpt-4o-mini")

**코드**:
```python
# OpenAI 설정
openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
openai_model: str = "gpt-4o-mini"
```

---

### 2. `persona/model/comment_persona_engine.py`
**변경 내용**:
- 전체 재작성: 로컬 LLM → OpenAI 기반
- **5개 댓글 랜덤 샘플링** 로직 추가
- JSON 파싱 강화
- 폴백 메커니즘 (OpenAI 실패 시 기본 페르소나 생성)

**주요 기능**:
```python
def generate_persona_via_llm(self, side: str):
    # 5개 댓글 랜덤 샘플링
    sampled_comments = random.sample(comments, min(5, len(comments)))
    
    # OpenAI API 호출
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[...],
        temperature=0.7,
        max_tokens=800
    )
```

---

### 3. `persona/backend/ai_debater.py`
**변경 내용**:
- 전체 재작성: 로컬 LLM → OpenAI 기반
- **Keywords 기반 토론** 로직 추가
- **중복 방지 로직** 추가 (이전 응답 추적)
- `presence_penalty`, `frequency_penalty` 활용

**주요 기능**:
```python
class AIDebater:
    def __init__(self, ..., keywords: Optional[List[str]] = None):
        self.keywords = keywords or []
        self.previous_responses: List[str] = []  # 중복 방지
    
    def generate_response(self, state, opponent_message):
        # Keywords를 프롬프트에 포함
        keywords_str = ", ".join(self.keywords)
        
        # 이전 응답을 프롬프트에 포함하여 중복 방지
        previous_responses_str = "\n".join(self.previous_responses[-5:])
        
        # OpenAI 호출 (반복 억제 파라미터)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[...],
            temperature=0.9,
            presence_penalty=0.6,  # 반복 억제
            frequency_penalty=0.6  # 반복 억제
        )
```

---

### 4. `persona/backend/services/debate_service.py`
**변경 내용**:
- `start_debate()` 메서드에 `keywords` 파라미터 추가
- OpenAI 설정을 DebaterManager에 전달

**코드**:
```python
def start_debate(
    self, 
    initial_topic: Optional[str] = None,
    keywords: Optional[List[str]] = None  # ← 추가
) -> Dict:
    # DebaterManager에 keywords 전달
    self.app_state.debater_manager = DebaterManager(
        dummy_analysis, 
        self.persona_engine,
        openai_api_key=settings.openai_api_key,
        model=settings.openai_model,
        keywords=keywords or []  # ← 전달
    )
```

---

### 5. `persona/backend/services/persona_service.py`
**변경 내용**:
- 5개 샘플링 정보를 응답에 포함
- 로그 메시지 개선

**코드**:
```python
def generate_personas(self) -> Dict:
    return {
        "message": "페르소나 생성 완료 (각 5개 댓글 기반)",
        "left_persona": left_persona,
        "right_persona": right_persona,
        "sampling_info": {
            "left_total": left_count,
            "left_sampled": 5,
            "right_total": right_count,
            "right_sampled": 5
        }
    }
```

---

### 6. `persona/backend/core/state.py`
**변경 내용**:
- CommentPersonaEngine 초기화 시 OpenAI 설정 전달

**코드**:
```python
def __init__(self):
    from ..config.settings import settings
    openai_api_key = settings.openai_api_key
    openai_model = settings.openai_model
    
    self.persona_engine = CommentPersonaEngine(
        openai_api_key=openai_api_key,
        model=openai_model
    )
```

---

### 7. `persona/backend/routes/debate.py`
**변경 내용**:
- `/api/debate/start` 엔드포인트에 `keywords` 파라미터 추가

**코드**:
```python
@router.post("/start")
async def start_debate(
    initial_topic: Optional[str] = Body(None),
    keywords: Optional[List[str]] = Body(None)  # ← 추가
):
    service = DebateService(get_app_state())
    result = service.start_debate(initial_topic=initial_topic, keywords=keywords)
    return result
```

---

### 8. `persona/backend/requirements.txt`
**변경 내용**:
- `openai>=1.0.0` 패키지 추가

---

## 사용 방법

### 1. OpenAI API 키 설정
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="your_api_key_here"

# Linux/Mac
export OPENAI_API_KEY="your_api_key_here"
```

### 2. 패키지 설치
```bash
cd persona
pip install -r backend/requirements.txt
```

### 3. 서버 실행
```bash
python backend/main.py
```

### 4. API 사용 예시
```python
import requests

# 1. 댓글 추가 (좌/우 각 5개 이상)
requests.post("http://localhost:8000/api/comments/left", json={
    "comments": ["좌파 댓글1", "좌파 댓글2", ..., "좌파 댓글5"]
})
requests.post("http://localhost:8000/api/comments/right", json={
    "comments": ["우파 댓글1", "우파 댓글2", ..., "우파 댓글5"]
})

# 2. 페르소나 생성 (각 5개씩 랜덤 샘플링)
requests.post("http://localhost:8000/api/comments/generate-persona")

# 3. 토론 시작 (keywords 전달)
requests.post("http://localhost:8000/api/debate/start", json={
    "keywords": ["경제", "복지", "세금"]
})

# 4. 토론 진행 (자동으로 좌/우 번갈아)
requests.post("http://localhost:8000/api/debate/next")
```

---

## 기술적 특징

### 1. 5개 댓글 샘플링
- 전체 댓글 중 **랜덤하게 5개**를 선택하여 페르소나 학습
- 매번 다른 샘플링으로 다양한 페르소나 생성 가능

### 2. Keywords 기반 토론
- YouTube 영상에서 추출한 keywords를 토론 주제로 활용
- 각 AI 토론자가 keywords를 중심으로 논쟁 전개

### 3. 중복 방지 메커니즘
- **이전 응답 추적**: 최근 20개 응답 저장
- **프롬프트에 포함**: "이전에 했던 표현을 반복하지 마세요"
- **OpenAI 파라미터**: `presence_penalty=0.6`, `frequency_penalty=0.6`
- **높은 temperature**: 0.9로 설정하여 다양성 증가

### 4. OpenAI GPT-4o-mini 사용
- 빠른 응답 속도
- 저렴한 비용
- 높은 품질의 한국어 생성

---

## 주의 사항

1. **OpenAI API 키 필수**: 환경 변수 `OPENAI_API_KEY` 설정 필요
2. **비용 발생**: OpenAI API 사용 시 비용 발생 (gpt-4o-mini는 저렴)
3. **최소 댓글 수**: 좌/우 각 5개 이상 필요
4. **인터넷 연결 필수**: OpenAI API 호출을 위해 필요

---

## 테스트 방법

```bash
cd persona
python test_api.py
```

또는 수동 테스트:
```bash
# 서버 실행
python backend/main.py

# 다른 터미널에서
curl -X POST http://localhost:8000/api/comments/left \
  -H "Content-Type: application/json" \
  -d '{"comments": ["댓글1", "댓글2", "댓글3", "댓글4", "댓글5"]}'
```

---

## 문의 및 지원

문제 발생 시 `SETUP_GUIDE.md`의 트러블슈팅 섹션을 참고하세요.

