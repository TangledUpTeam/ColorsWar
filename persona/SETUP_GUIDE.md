# ColorsWar Persona 모듈 - OpenAI 설정 가이드

## 개요
이 모듈은 OpenAI GPT-4o-mini를 사용하여 유튜브 댓글 기반 페르소나를 생성하고 AI 토론을 시뮬레이션합니다.

## 주요 변경 사항

### 1. OpenAI 기반 페르소나 생성
- **이전**: 로컬 LLM (skt/kogpt2-base-v2) 사용
- **현재**: OpenAI GPT-4o-mini 사용
- **샘플링**: 좌/우 각 5개 댓글을 랜덤 샘플링하여 학습

### 2. Keywords 기반 토론
- YouTube 영상에서 추출한 keywords를 토론 주제로 활용
- 각 페르소나가 keywords를 중심으로 논쟁

### 3. 중복 방지 로직
- 이전 응답 기록을 추적하여 같은 말 반복 방지
- OpenAI의 `presence_penalty`와 `frequency_penalty` 활용

## 설치 및 설정

### 1. 필수 패키지 설치
```bash
cd persona
pip install -r backend/requirements.txt
```

### 2. OpenAI API 키 설정

#### 방법 1: 환경 변수 설정 (권장)
**Windows (PowerShell)**:
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

**Windows (CMD)**:
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
```

**Linux/Mac**:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

#### 방법 2: .env 파일 생성
`persona` 폴더에 `.env` 파일을 생성하고 다음 내용을 추가:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 3. 서버 실행
```bash
cd persona
python backend/main.py
```

또는:
```bash
cd persona
./start_server.bat  # Windows
./start_server.sh   # Linux/Mac
```

## 사용 방법

### 1. 댓글 수집 및 페르소나 생성
```python
import requests

# 좌파 댓글 추가
requests.post("http://localhost:8000/api/comments/left", json={
    "comments": ["댓글1", "댓글2", "댓글3", "댓글4", "댓글5"]
})

# 우파 댓글 추가
requests.post("http://localhost:8000/api/comments/right", json={
    "comments": ["댓글1", "댓글2", "댓글3", "댓글4", "댓글5"]
})

# 페르소나 생성 (각 5개씩 랜덤 샘플링)
response = requests.post("http://localhost:8000/api/comments/generate-persona")
print(response.json())
```

### 2. Keywords 기반 토론 시작
```python
# 토론 시작 (keywords 전달)
response = requests.post("http://localhost:8000/api/debate/start", json={
    "keywords": ["경제", "복지", "세금", "정책"]
})
print(response.json())

# 다음 메시지 생성 (자동으로 좌/우 번갈아)
response = requests.post("http://localhost:8000/api/debate/next")
print(response.json())
```

## 수정된 파일 목록

### persona 폴더 내부만 수정됨:
1. **persona/backend/config/settings.py**
   - OpenAI API 키 및 모델 설정 추가

2. **persona/model/comment_persona_engine.py**
   - OpenAI GPT-4o-mini 기반으로 완전히 재작성
   - 5개 댓글 랜덤 샘플링 로직 추가

3. **persona/backend/ai_debater.py**
   - OpenAI 기반으로 완전히 재작성
   - Keywords 기반 토론 로직 추가
   - 중복 방지 로직 추가 (이전 응답 추적)

4. **persona/backend/services/debate_service.py**
   - Keywords 파라미터 추가
   - OpenAI 설정 전달

5. **persona/backend/services/persona_service.py**
   - 5개 샘플링 정보 반환

6. **persona/backend/core/state.py**
   - OpenAI 설정을 CommentPersonaEngine에 전달

7. **persona/backend/routes/debate.py**
   - Keywords 파라미터 받도록 API 수정

8. **persona/backend/requirements.txt**
   - `openai>=1.0.0` 패키지 추가

## 주의 사항

1. **OpenAI API 키 필수**: 환경 변수 또는 .env 파일에 반드시 설정해야 합니다.
2. **비용**: OpenAI API 사용 시 비용이 발생합니다. gpt-4o-mini는 저렴한 모델입니다.
3. **최소 댓글 수**: 좌/우 각 5개 이상의 댓글이 필요합니다.
4. **인터넷 연결**: OpenAI API 호출을 위해 인터넷 연결이 필요합니다.

## 트러블슈팅

### OpenAI API 키 오류
```
ValueError: OpenAI API 키가 설정되지 않았습니다.
```
→ 환경 변수 `OPENAI_API_KEY`를 설정하거나 .env 파일을 생성하세요.

### 댓글 부족 오류
```
ValueError: 댓글이 충분하지 않습니다. 좌:3, 우:2 (각 5개 이상 필요)
```
→ 좌파/우파 각각 최소 5개 이상의 댓글을 추가하세요.

### 패키지 설치 오류
```
ImportError: openai 패키지가 설치되지 않았습니다.
```
→ `pip install openai` 또는 `pip install -r backend/requirements.txt`를 실행하세요.

## 기술 스택
- **LLM**: OpenAI GPT-4o-mini
- **프레임워크**: FastAPI
- **언어**: Python 3.8+
- **주요 라이브러리**: openai, fastapi, pydantic

