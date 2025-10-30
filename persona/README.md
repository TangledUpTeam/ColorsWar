# 정치 댓글 전쟁 시뮬레이터 (로컬 LLM 버전)

로컬 GPU 기반 한국어 LLM을 사용하여 좌파/우파 AI가 댓글창에서 싸우는 시뮬레이터

## 🎯 주요 기능

- **댓글 수집**: CLI 테스트 스크립트를 통한 자동 댓글 수집
- **페르소나 학습**: 수집된 댓글을 기반으로 각 진영의 어투와 패턴 학습
- **댓글 분석**: 규칙 기반 고속 분석 (메모리 효율적)
- **AI 토론**: skt/kogpt2-base-v2 모델로 실감나는 댓글 전쟁 생성
- **로그 출력**: 컬러풀한 CLI 출력으로 전체 과정 시각화

## 🏗️ 프로젝트 구조 (모듈화)

```
persona/backend/
├── config/                 # 설정 관리
│   ├── __init__.py
│   └── settings.py         # 환경 변수 및 설정 중앙 관리
├── core/                   # 핵심 모듈
│   ├── __init__.py
│   └── state.py            # 전역 상태 관리 (싱글톤)
├── routes/                 # API 라우터 (기능별 분리)
│   ├── __init__.py
│   ├── comments.py         # 댓글 수집 API
│   ├── persona.py          # 페르소나 생성 API
│   ├── debate.py           # 토론 시뮬레이션 API
│   └── health.py           # 헬스체크 API
├── services/               # 비즈니스 로직 레이어
│   ├── __init__.py
│   ├── comment_service.py  # 댓글 관련 비즈니스 로직
│   ├── persona_service.py  # 페르소나 생성 비즈니스 로직
│   └── debate_service.py   # 토론 관리 비즈니스 로직
├── models.py               # Pydantic 데이터 모델
├── ai_debater.py           # AI 토론자 (LLM 기반)
├── analyzer.py             # 댓글 분석기
├── sentiment_tracker.py    # 감정 추적
└── main.py                 # FastAPI 앱 진입점 (간소화)
```

**아키텍처 특징:**
- ✅ **관심사 분리**: API 라우팅, 비즈니스 로직, 상태 관리 명확히 분리
- ✅ **재사용성**: 서비스 레이어는 독립적으로 재사용 가능
- ✅ **테스트 용이성**: 각 계층을 독립적으로 테스트 가능
- ✅ **확장성**: 새 기능 추가 시 적절한 계층에 추가
- ✅ **설정 관리**: 환경별 설정을 쉽게 변경 가능

## 📋 요구사항

### 하드웨어
- **GPU**: NVIDIA GPU (VRAM 6GB 이상 권장)
  - KISTI-KONI/KONI-Llama3-8B-Instruct: ~4-5GB VRAM (8bit 양자화)
  - 댓글 분석은 규칙 기반으로 메모리 절약
  - **GTX 1060 6GB 이상이면 작동!**
- **RAM**: 16GB 이상
- **저장공간**: 20GB 이상 (모델 다운로드용)

### 소프트웨어
- Python 3.9 이상
- CUDA 11.8 이상 (GPU 사용시)
- pip

## 🚀 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd Color_War
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

### 4. 모델 다운로드
첫 실행 시 자동으로 모델이 다운로드됩니다 (~20GB).
인터넷 연결이 필요하며, 다운로드에 시간이 소요됩니다.

## 📖 사용법

### 1. 서버 실행
```bash
# Windows
start_server.bat

# Linux/Mac
./start_server.sh
```

**최초 실행 시:**
- 대화 생성 모델 로딩에 1-2분 소요됩니다
- 이후에는 빠르게 동작합니다!

서버가 `http://localhost:8000`에서 실행됩니다.

### 2. CLI 테스트 실행

**CLI 기반 테스트 스크립트로 전체 워크플로우를 로그로 확인:**

```bash
# Windows
test.bat

# Linux/Mac
./test.sh
```

**고급 옵션:**
```bash
# 기본 테스트 (10개 메시지)
python test_api.py

# 20개 메시지 생성
python test_api.py --messages 20

# 빠른 테스트 (페르소나 생성까지만)
python test_api.py --quick

# 도움말
python test_api.py --help
```

**출력 예시:**
```
🧠 정치 댓글 전쟁 시뮬레이터 API 테스트
시작 시각: 2025-10-29 14:30:00

1️⃣ 서버 상태 확인
✓ 서버 상태: healthy
  CUDA 사용 가능: True
  디바이스: cuda

2️⃣ 좌파 댓글 수집
ℹ 7개의 댓글 전송 중...
  └─ 진보적 개혁이 필요합니다
  └─ 복지 예산을 대폭 늘려야 해요
  └─ ... 외 4개
✓ 좌파 댓글 7개 수집 완료

...

7️⃣ 댓글 전쟁 시뮬레이션 (10개 메시지)
ℹ AI들이 실시간으로 논쟁 중입니다...

🔵 좌파:
복지 예산 확대는 사회 안전망 강화의 핵심입니다!
└─ 주제: 정치적 공정성 | 메시지 #1 | 생성시간: 3.2초

🔴 우파:
재정 건전성을 고려하지 않은 무분별한 복지는 위험합니다.
└─ 주제: 정치적 공정성 | 메시지 #2 | 생성시간: 3.5초

...
```

**API 문서 확인 (선택):** `http://localhost:8000/docs`

### 3. 수동 API 테스트 (선택)

**로그 테스트 스크립트(`test_api.py`)를 사용하면 아래 과정이 자동화됩니다!**

수동으로 테스트하려면:

```bash
# 좌파 댓글 수집
curl -X POST "http://localhost:8000/api/comments/left" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": [
      "진보적 개혁이 필요합니다",
      "평등한 사회를 만들어야 해요",
      "복지 정책 확대가 시급합니다"
    ]
  }'

# 우파 댓글 수집
curl -X POST "http://localhost:8000/api/comments/right" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": [
      "경제 성장이 우선입니다",
      "안보가 가장 중요합니다",
      "전통적 가치를 지켜야 합니다"
    ]
  }'
```

### 4. 수집 상태 확인
```bash
curl "http://localhost:8000/api/comments/stats"
```

### 5. 댓글 분석
페르소나가 준비되면 (각 진영 5개 이상) 분석을 시작합니다.

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "comments_text": "이 정부는 정말 답이 없네요\n그럼 당신들이 하면 잘하나요?\n..."
  }'
```

### 6. 토론 시작
```bash
# 토론 시작
curl -X POST "http://localhost:8000/api/debate/start"

# 다음 메시지 생성 (자동으로 좌파/우파 번갈아가며)
curl -X POST "http://localhost:8000/api/debate/next"

# 토론 상태 확인
curl "http://localhost:8000/api/debate/status"
```

## 📡 API 엔드포인트

### 댓글 수집 (`routes/comments.py`)
- `POST /api/comments/left` - 좌파 댓글 수집
- `POST /api/comments/right` - 우파 댓글 수집
- `GET /api/comments/stats` - 수집 통계
- `POST /api/comments/reset` - 댓글 초기화

### 페르소나 생성 (`routes/persona.py`)
- `POST /api/comments/generate-persona` - LLM 기반 페르소나 생성

### 토론 (`routes/debate.py`)
- `POST /api/debate/start` - 토론 시작
- `POST /api/debate/next` - 다음 메시지 생성
- `GET /api/debate/status` - 토론 상태 조회
- `POST /api/debate/reset` - 토론 초기화

### 기타 (`routes/health.py`)
- `GET /api/health` - 서버 상태 확인
- `GET /docs` - API 문서 (Swagger UI)

## 🔧 메모리 최적화

### 현재 설정 (8bit 양자화)
- ✅ **자동 적용됨**: 8bit 양자화로 VRAM 사용량 50% 절감
- VRAM 4-5GB만으로 작동 (원래 8GB 필요)
- GTX 1060 6GB, RTX 3060 등에서 작동

### 더 메모리를 절약하려면 (4bit)
`backend/ai_debater.py`에서 수정:

```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,  # 4bit으로 변경
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)
```

이렇게 하면 VRAM 2-3GB만 사용 (속도는 약간 느려짐)

### CPU 전용 모드
GPU가 없는 경우 CPU에서도 실행 가능하지만 매우 느립니다.
자동으로 CPU 모드로 전환됩니다.

## 🎨 사용 예시

### Python으로 전체 워크플로우
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 좌파 댓글 수집
left_comments = [
    "진보적 개혁이 필요해요",
    "복지 예산을 늘려야 합니다",
    "평등한 사회를 만들어야 해요"
]
requests.post(f"{BASE_URL}/api/comments/left", json={"comments": left_comments})

# 2. 우파 댓글 수집
right_comments = [
    "경제 성장이 우선입니다",
    "안보가 가장 중요합니다",
    "재정 건전성을 지켜야 합니다"
]
requests.post(f"{BASE_URL}/api/comments/right", json={"comments": right_comments})

# 3. 통계 확인
stats = requests.get(f"{BASE_URL}/api/comments/stats").json()
print(f"수집된 댓글: 좌파 {stats['left_count']}, 우파 {stats['right_count']}")

# 4. 분석
analysis_result = requests.post(
    f"{BASE_URL}/api/analyze",
    json={"comments_text": "정치 관련 댓글들..."}
).json()

# 5. 토론 시작
debate_state = requests.post(f"{BASE_URL}/api/debate/start").json()

# 6. 댓글 전쟁 시뮬레이션 (10개)
for i in range(10):
    response = requests.post(f"{BASE_URL}/api/debate/next").json()
    message = response['message']
    side = "🔵 좌파" if message['side'] == 'left' else "🔴 우파"
    print(f"{side}: {message['content']}")
```

## ⚙️ 설정 커스터마이징

`backend/config/settings.py`에서 다음 설정을 변경할 수 있습니다:

```python
# 서버 설정
host = "127.0.0.1"
port = 8000

# LLM 모델 설정
persona_model_name = "skt/kogpt2-base-v2"
debater_model_name = "skt/kogpt2-base-v2"

# 디바이스 설정
device = "cpu"  # "cpu" 또는 "cuda"

# 댓글 수집 설정
min_comments_for_persona = 5  # 페르소나 생성에 필요한 최소 댓글 수

# 토론 설정
initial_topic = "정치적 공정성"
```

환경 변수로도 설정 가능 (`.env` 파일 생성):
```
HOST=0.0.0.0
PORT=8080
DEVICE=cuda
MIN_COMMENTS_FOR_PERSONA=10
```

## 🐛 트러블슈팅

### CUDA out of memory
- ✅ 이미 최적화됨: 대화 생성 모델만 로딩
- 댓글 분석은 규칙 기반 (메모리 효율적)
- 필요시 4bit 양자화 사용 가능

### 모델 다운로드 실패
- Hugging Face 토큰 설정: `huggingface-cli login`
- 인터넷 연결 확인
- 프록시 설정 확인

### 응답이 너무 느림
- **최초 실행**: 모델 로딩에 1-2분 소요 (정상)
- **이후 사용**: 빠르게 동작 (3-5초)
- GPU 사용 확인: 웹 UI 상단 서버 상태 또는 `/api/health`
- CPU 모드는 매우 느림 (GPU 권장)

### Import 오류
- 모든 `__init__.py` 파일이 생성되었는지 확인
- 가상환경 활성화 확인: `source venv/bin/activate` (Linux) 또는 `venv\Scripts\activate` (Windows)

## 📝 라이선스

MIT License

## 🤝 기여

이슈와 PR은 언제나 환영합니다!

## 📧 문의

이슈 트래커를 이용해주세요.

