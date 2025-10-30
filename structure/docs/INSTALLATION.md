# 색깔전쟁 - AI 페르소나 배틀 시스템 설치 가이드

## 빠른 시작 (완전 무료!)

### 1. 패키지 설치

```bash
pip install fastapi uvicorn requests
```

### 2. Ollama 설치 및 모델 다운로드

**Ollama는 완전 무료 로컬 AI 모델입니다!**

```bash
# 1. Ollama 다운로드 및 설치
# Windows: https://ollama.com/download
# Linux/Mac: curl -fsSL https://ollama.com/install.sh | sh

# 2. 모델 다운로드 (한국어 지원)
ollama pull llama3.2

# 또는 한국어 최적화 모델
ollama pull qwen2.5
```

> 💡 자세한 Ollama 설치 가이드는 `OLLAMA_SETUP.md` 참조

### 3. 서버 실행

```bash
cd test
python app_battle.py
```

또는:

```bash
uvicorn app_battle:app --host 0.0.0.0 --port 5000
```

### 4. 브라우저에서 접속

```
http://localhost:5000
```

> 🎉 **API 키 불필요!** Ollama는 로컬에서 무료로 실행됩니다.

## 테스트

### 빠른 테스트

```bash
python quick_test.py
```

### 전체 테스트

```bash
python test_battle_system.py
```

## 파일 구조

```
test/
├── app_battle.py              # 메인 FastAPI 애플리케이션
├── persona_service.py         # AI 페르소나 토론 서비스
├── reclassifier.py            # 판단불가 댓글 재분류
├── battle.html                # 프론트엔드 UI
├── battle.js                  # 프론트엔드 로직
├── quick_test.py              # 빠른 테스트 스크립트
├── test_battle_system.py      # 전체 테스트 스크립트
├── README_BATTLE.md           # 상세 문서
└── INSTALLATION.md            # 설치 가이드 (이 파일)
```

## 주요 API 엔드포인트

### 1. 댓글 분석 및 학습

```http
POST /api/battle/analyze-and-learn
Content-Type: application/json

{
  "keywords": ["정부", "정책"],
  "comments": ["댓글1", "댓글2"]
}
```

### 2. AI 페르소나 토론 시작

```http
POST /api/battle/start-debate
Content-Type: application/json

{
  "topic": "현재 정부 정책",
  "rounds": 3
}
```

### 3. 학습 데이터 조회

```http
GET /api/battle/training-data
```

## 문제 해결

### "백엔드 모듈을 찾을 수 없습니다" 메시지

정상입니다. Mock 클래스가 자동으로 사용됩니다.

### "connection refused" 또는 Ollama 연결 오류

Ollama가 실행 중인지 확인:

```bash
ollama serve
```

### AI 응답 품질이 낮음

한국어 최적화 모델 사용:

```bash
ollama pull qwen2.5
```

.env 파일에 설정:
```
OLLAMA_MODEL=qwen2.5
```

### 포트 5000이 이미 사용 중

다른 포트를 사용:

```bash
uvicorn app_battle:app --port 8000
```

## 요구사항

- Python 3.8 이상
- Ollama 설치 (완전 무료!)
- 2-5GB 디스크 공간 (모델 크기에 따라)

## 다음 단계

1. 브라우저에서 `http://localhost:5000` 접속
2. 테스트 댓글 데이터 입력 (기본값 사용 가능)
3. "댓글 분석 및 학습 시작" 버튼 클릭
4. AI 페르소나 토론 자동 시작 및 결과 확인
5. 다른 영상 댓글로 추가 학습 가능 (데이터 누적됨)

## 추가 정보

자세한 내용은 `README_BATTLE.md`를 참조하세요.

