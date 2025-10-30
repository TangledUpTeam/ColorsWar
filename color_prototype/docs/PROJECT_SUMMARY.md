# Color Prototype - 프로젝트 요약

## 🎯 프로젝트 개요

Color Prototype은 YouTube 정치 댓글을 분석하여 좌우파 AI 페르소나를 생성하고, 이들이 실시간으로 토론하는 것을 시뮬레이션하는 통합 시스템입니다.

## 📊 구현된 기능

### ✅ 완료된 모듈

#### 1. YouTube 파이프라인 (`modules/youtube_processor.py`)
- ✅ 오디오 다운로드 (yt-dlp)
- ✅ 음성 전사 (Whisper)
- ✅ 텍스트 요약
- ✅ 댓글 수집 (YouTube Data API)
- ✅ 키워드 추출

#### 2. 댓글 분류기 (`modules/classifier.py`)
- ✅ 키워드 기반 좌/우파 분류
- ✅ LLM 기반 재분류 (Ollama)
- ✅ 판단불가 댓글 강제 분류
- ✅ 통계 생성

#### 3. 기존 페르소나 (`modules/persona_original.py`)
- ✅ kogpt2 기반 페르소나 생성
- ✅ 댓글 학습 및 스타일 분석
- ✅ Ollama 기반 토론 생성
- ✅ CPU 최적화

#### 4. LoRA 페르소나 (`modules/persona_lora.py`)
- ✅ MAE (말투/감정) 분석
- ✅ SOLAR-Mini + LoRA 파인튜닝
- ✅ 공격성 점수 계산
- ✅ 감정 패턴 분석
- ✅ 성향별 특유 표현 추출

#### 5. 팩트체크 엔진 (`modules/factcheck_engine.py`)
- ✅ 네이버 뉴스 검색
- ✅ DuckDuckGo 검색
- ✅ 키워드 추출
- ✅ 증거 분석
- ✅ 신뢰도 평가

#### 6. FastAPI 백엔드
- ✅ Tab1 라우터 (기존 페르소나)
- ✅ Tab2 라우터 (LoRA 페르소나)
- ✅ CORS 설정
- ✅ 에러 핸들링
- ✅ API 문서 자동 생성

#### 7. 웹 프론트엔드
- ✅ 2개 탭 UI
- ✅ YouTube URL 입력
- ✅ 실시간 결과 표시
- ✅ 토론 메시지 애니메이션
- ✅ 팩트체크 인터페이스
- ✅ 반응형 디자인

## 🏗️ 프로젝트 구조

```
color_prototype/
├── backend/                    # FastAPI 백엔드
│   ├── main.py                # 메인 서버 (완료)
│   └── routes/                # API 라우터
│       ├── __init__.py        # 라우터 초기화 (완료)
│       ├── tab1_routes.py     # Tab1 API (완료)
│       └── tab2_routes.py     # Tab2 API (완료)
│
├── frontend/                   # 웹 프론트엔드
│   ├── index.html             # 메인 HTML (완료)
│   └── app.js                 # JavaScript (완료)
│
├── modules/                    # 핵심 모듈
│   ├── __init__.py            # 모듈 초기화 (완료)
│   ├── youtube_processor.py   # YouTube 파이프라인 (완료)
│   ├── classifier.py          # 댓글 분류기 (완료)
│   ├── persona_original.py    # 기존 페르소나 (완료)
│   ├── persona_lora.py        # LoRA 페르소나 (완료)
│   └── factcheck_engine.py    # 팩트체크 (완료)
│
├── data/                       # 데이터 저장
│   ├── audio/                 # 오디오 파일
│   ├── scripts/               # 전사 텍스트
│   ├── summaries/             # 요약
│   ├── comments/              # 댓글
│   └── models/                # 학습된 모델
│
├── docs/                       # 문서
│   ├── PROJECT_SUMMARY.md     # 프로젝트 요약 (완료)
│   ├── INSTALLATION.md        # 설치 가이드 (완료)
│   ├── QUICK_START.md         # 빠른 시작 (완료)
│   └── Summary.txt            # 원본 요약 (완료)
│
├── requirements.txt            # 패키지 목록 (완료)
├── require_envkey.txt          # 환경변수 가이드 (완료)
├── README.md                   # 메인 README (완료)
└── .gitignore                  # Git 무시 파일 (완료)
```

## 🔄 실행 흐름

### Tab1: 기존 페르소나 (kogpt2)

```
YouTube URL 입력
    ↓
오디오 다운로드 (yt-dlp)
    ↓
음성 전사 (Whisper)
    ↓
텍스트 요약
    ↓
댓글 수집 (YouTube API)
    ↓
좌/우파 분류 (키워드 + LLM)
    ↓
페르소나 생성 (kogpt2)
    ↓
AI 토론 (Ollama)
    ↓
결과 표시
```

### Tab2: LoRA 페르소나 (SOLAR-Mini)

```
YouTube URL 입력
    ↓
오디오 다운로드 (yt-dlp)
    ↓
음성 전사 (Whisper)
    ↓
텍스트 요약
    ↓
댓글 수집 (YouTube API)
    ↓
좌/우파 분류 (키워드 + LLM)
    ↓
MAE 분석 (말투/감정)
    ↓
LoRA 파인튜닝 (선택)
    ↓
AI 토론 (Ollama)
    ↓
결과 표시
```

## 🎨 주요 특징

### 1. 2가지 페르소나 모드
- **Tab1 (kogpt2)**: 빠르고 경량, CPU 지원
- **Tab2 (LoRA)**: 정교하고 고급, GPU 권장

### 2. 전체 파이프라인 자동화
- YouTube URL 입력만으로 전체 과정 자동 실행
- 오디오 → 전사 → 요약 → 댓글 → 분류 → 토론

### 3. 실시간 웹 인터페이스
- 2개 탭으로 모드 전환
- 실시간 결과 표시
- 애니메이션 효과

### 4. 팩트체크 통합
- 네이버 + DuckDuckGo 검색
- 증거 기반 판정
- 신뢰도 점수

## 📈 성능 특징

### Tab1 (기존 페르소나)
- **모델 크기**: ~500MB (kogpt2)
- **실행 시간**: 3-5분
- **메모리**: 4-8GB
- **CPU 지원**: ✅

### Tab2 (LoRA 페르소나)
- **모델 크기**: ~2GB (SOLAR-Mini)
- **실행 시간**: 5-10분 (학습 시 더 오래)
- **메모리**: 8-16GB
- **GPU 권장**: ✅

## 🔧 기술 스택

### 백엔드
- **프레임워크**: FastAPI 0.109.0
- **서버**: Uvicorn
- **환경변수**: python-dotenv

### AI/ML
- **LLM**: kogpt2, SOLAR-Mini, Ollama
- **음성 인식**: Whisper
- **임베딩**: sentence-transformers
- **토픽 모델링**: BERTopic, HDBSCAN
- **파인튜닝**: LoRA (PEFT)

### 데이터 수집
- **YouTube**: google-api-python-client
- **오디오**: yt-dlp
- **검색**: 네이버 API, DuckDuckGo

### 프론트엔드
- **HTML5**: 시맨틱 마크업
- **CSS3**: 그라디언트, 애니메이션
- **JavaScript**: Fetch API, DOM 조작

## 📝 사용된 원본 파일

### 통합된 파일
1. ✅ `learning_p_jh.py` → `modules/persona_lora.py`
2. ✅ `mae_jh.py` → `modules/persona_lora.py`
3. ✅ `start_fight_jh.py` → `modules/persona_lora.py`
4. ✅ `structure/youtube_pipeline/*` → `modules/youtube_processor.py`
5. ✅ `structure/reclassifier.py` → `modules/classifier.py`
6. ✅ `persona/model/comment_persona_engine.py` → `modules/persona_original.py`
7. ✅ `persona/backend/ai_debater.py` → `modules/persona_original.py`
8. ✅ `factcheck/*` → `modules/factcheck_engine.py`

### 참고된 파일
- ✅ `Summary.txt` → `docs/Summary.txt`
- ✅ `Summary_And_Request.txt` → 구현 요구사항

## ✨ 구현 완료 사항

### 요구사항 체크리스트
- ✅ Summary.txt 파일 참고
- ✅ learning_p_jh.py, mae_jh.py, start_fight_jh.py 활용
- ✅ color_prototype 폴더 생성
- ✅ 파일들을 라우터로 정리
- ✅ md/txt 파일들도 라우터로 정리
- ✅ 1번 버튼 (기존 페르소나) 구현
- ✅ 2번 버튼 (LoRA 페르소나) 구현
- ✅ requirements.txt 생성
- ✅ require_envkey.txt 생성

## 🚀 다음 단계

프로젝트가 완성되었습니다! 이제:

1. **설치**: [INSTALLATION.md](INSTALLATION.md) 참고
2. **실행**: [QUICK_START.md](QUICK_START.md) 참고
3. **사용**: [README.md](../README.md) 참고

## 💡 개선 가능 사항 (향후)

1. **데이터베이스 추가**: 결과 영구 저장
2. **사용자 인증**: 개인별 프로젝트 관리
3. **실시간 스트리밍**: WebSocket 기반 실시간 업데이트
4. **더 많은 모델**: GPT-4, Claude 등 추가
5. **배포**: Docker, Kubernetes 지원

## 📞 문의

프로젝트 관련 문의는 이슈로 등록해주세요!

