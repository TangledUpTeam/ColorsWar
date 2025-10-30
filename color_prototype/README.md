# Color Prototype - AI 페르소나 배틀 시스템

YouTube 댓글을 분석하여 좌우파 AI 페르소나를 생성하고 토론을 시뮬레이션하는 통합 시스템입니다.

## 🎯 주요 기능

### 1️⃣ Tab1: 기존 페르소나 (kogpt2)
- **경량 모델**: skt/kogpt2-base-v2 사용
- **빠른 실행**: CPU에서도 빠르게 동작
- **전체 파이프라인**:
  1. YouTube 댓글 수집
  2. 좌/우파 자동 분류
  3. 페르소나 생성
  4. AI 토론 시뮬레이션
  5. 팩트체크 (선택)

### 2️⃣ Tab2: LoRA 페르소나 (SOLAR-Mini)
- **고급 모델**: Upstage/SOLAR-Mini-Instruct + LoRA
- **MAE 분석**: 말투와 감정 패턴 분석
- **정교한 페르소나**: 더 세밀한 성향 학습
- **전체 파이프라인**:
  1. YouTube 댓글 수집
  2. 좌/우파 자동 분류
  3. MAE 분석 (말투/감정)
  4. LoRA 파인튜닝 (선택)
  5. AI 토론 시뮬레이션
  6. 팩트체크 (선택)

## 📦 설치 방법

### 1. 저장소 클론
```bash
cd color_prototype
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`require_envkey.txt` 파일을 참고하여 프로젝트 루트에 `.env` 파일을 생성하세요.

**필수 환경변수:**
```
YOUTUBE_DATA_API_KEY=your_youtube_api_key
```

**선택 환경변수:**
```
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## 🚀 실행 방법

### 서버 시작
```bash
cd backend
python main.py
```

서버가 시작되면 브라우저에서 접속:
- **웹 인터페이스**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 📁 프로젝트 구조

```
color_prototype/
├── backend/              # FastAPI 백엔드
│   ├── main.py          # 메인 서버
│   └── routes/          # API 라우터
│       ├── tab1_routes.py  # Tab1 (기존 페르소나)
│       └── tab2_routes.py  # Tab2 (LoRA 페르소나)
├── frontend/            # 웹 프론트엔드
│   ├── index.html       # 메인 HTML
│   └── app.js           # JavaScript
├── modules/             # 핵심 모듈
│   ├── youtube_processor.py    # YouTube 파이프라인
│   ├── classifier.py           # 댓글 분류기
│   ├── persona_original.py     # 기존 페르소나 (kogpt2)
│   ├── persona_lora.py         # LoRA 페르소나
│   └── factcheck_engine.py     # 팩트체크 엔진
├── data/                # 데이터 저장 폴더
│   ├── audio/          # 오디오 파일
│   ├── scripts/        # 전사 텍스트
│   ├── summaries/      # 요약
│   ├── comments/       # 댓글
│   └── models/         # 학습된 모델
├── docs/               # 문서
├── requirements.txt    # 패키지 목록
└── require_envkey.txt  # 환경변수 가이드
```

## 🔧 사용 방법

### 1. Tab1 (기존 페르소나) 사용
1. YouTube URL 입력
2. 토론 주제 입력 (선택)
3. 토론 라운드 수 설정
4. "YouTube 분석 및 AI 토론 시작" 버튼 클릭
5. 결과 확인

### 2. Tab2 (LoRA 페르소나) 사용
1. YouTube URL 입력
2. 토론 주제 입력 (선택)
3. 토론 라운드 수 설정
4. "YouTube 분석 및 AI 토론 시작" 버튼 클릭
5. MAE 분석 결과 확인
6. AI 토론 결과 확인

### 3. 팩트체크 사용
1. 각 탭 하단의 팩트체크 섹션으로 이동
2. 팩트체크할 주장 입력
3. "팩트체크 실행" 버튼 클릭
4. 판정 결과 및 증거 확인

## 🎨 주요 차이점

| 기능 | Tab1 (기존) | Tab2 (LoRA) |
|------|------------|-------------|
| 모델 | kogpt2 | SOLAR-Mini + LoRA |
| 속도 | 빠름 | 느림 (학습 시) |
| CPU 지원 | ✅ | ⚠️ (GPU 권장) |
| MAE 분석 | ❌ | ✅ |
| 페르소나 정교함 | 기본 | 고급 |
| 사용 추천 | 빠른 테스트 | 정교한 분석 |

## 📚 API 엔드포인트

### Tab1 (기존 페르소나)
- `POST /api/tab1/youtube-pipeline` - YouTube 파이프라인 실행
- `POST /api/tab1/factcheck` - 팩트체크 실행
- `GET /api/tab1/status` - 상태 조회

### Tab2 (LoRA 페르소나)
- `POST /api/tab2/youtube-pipeline` - YouTube 파이프라인 실행
- `POST /api/tab2/factcheck` - 팩트체크 실행
- `GET /api/tab2/status` - 상태 조회

## ⚠️ 주의사항

1. **YouTube API 키**: 댓글 수집을 위해 필수
2. **Ollama**: AI 토론을 위해 Ollama 설치 권장
3. **GPU**: Tab2 (LoRA) 학습 시 GPU 권장
4. **시간**: 전체 파이프라인은 5-10분 소요 가능

## 🐛 문제 해결

### YouTube API 오류
- API 키가 올바른지 확인
- API 할당량 초과 여부 확인

### Ollama 연결 오류
- Ollama가 실행 중인지 확인
- OLLAMA_URL이 올바른지 확인

### 모델 로딩 오류
- 인터넷 연결 확인
- 디스크 공간 확인 (모델 다운로드 필요)

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

## 👥 기여

버그 리포트 및 기능 제안은 이슈로 등록해주세요.

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

