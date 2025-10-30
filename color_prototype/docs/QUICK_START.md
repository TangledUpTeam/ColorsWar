# Color Prototype - 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### 1단계: 환경 설정 (1분)

```bash
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt
```

### 2단계: API 키 설정 (2분)

프로젝트 루트에 `.env` 파일 생성:

```
YOUTUBE_DATA_API_KEY=your_youtube_api_key_here
```

**YouTube API 키 발급 방법:**
1. https://console.cloud.google.com/apis/credentials 접속
2. 프로젝트 생성
3. YouTube Data API v3 활성화
4. API 키 생성
5. `.env` 파일에 붙여넣기

### 3단계: 서버 실행 (1분)

```bash
cd backend
python main.py
```

### 4단계: 웹 접속 (1분)

브라우저에서 http://localhost:8000 접속

## 💡 첫 번째 테스트

### Tab1 (기존 페르소나) 테스트

1. **YouTube URL 입력**
   - 예시: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - 또는 비디오 ID만: `dQw4w9WgXcQ`

2. **토론 주제 입력** (선택)
   - 예시: "현재 정부 정책"

3. **라운드 수 설정**
   - 기본값: 5

4. **실행 버튼 클릭**
   - 처리 시간: 약 3-5분

5. **결과 확인**
   - 댓글 통계
   - 좌우파 분류
   - AI 토론 내용

## 🎨 Tab2 (LoRA 페르소나) 테스트

Tab1과 동일한 방법으로 사용하되, 추가로 MAE 분석 결과를 확인할 수 있습니다.

## 📰 팩트체크 테스트

1. 각 탭 하단의 팩트체크 섹션으로 이동
2. 주장 입력 예시:
   - "비트코인 가격이 급등했다"
   - "삼성전자 반도체 수출이 증가했다"
3. "팩트체크 실행" 버튼 클릭
4. 판정 결과 확인

## ⚡ 선택 사항: Ollama 설치

더 나은 AI 토론을 위해 Ollama 설치 권장:

```bash
# Ollama 설치 (https://ollama.ai/)
# Windows: 설치 프로그램 다운로드
# Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh

# 모델 다운로드
ollama pull llama3.2

# Ollama 실행 확인
ollama list
```

`.env` 파일에 추가:
```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## 🐛 문제 발생 시

### YouTube API 오류
```
오류: YouTube API 키가 설정되지 않았습니다
```
→ `.env` 파일에 `YOUTUBE_DATA_API_KEY` 확인

### 포트 충돌
```
오류: Address already in use
```
→ 다른 포트 사용: `uvicorn main:app --port 8001`

### 모델 다운로드 느림
```
⏳ 모델 로딩 중...
```
→ 첫 실행 시 모델 다운로드로 시간 소요 (정상)

## 📚 다음 단계

- [전체 문서](../README.md) 읽기
- [API 문서](http://localhost:8000/docs) 확인
- 다양한 YouTube 영상으로 테스트

## 💬 도움말

문제가 해결되지 않으면 이슈를 등록해주세요!

