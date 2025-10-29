# 색깔전쟁 - AI 페르소나 배틀 시스템

## 개요

댓글을 분석하여 좌파/우파로 분류하고, 학습된 데이터를 기반으로 AI 페르소나가 실시간으로 토론하는 시스템입니다.

## 주요 기능

1. **댓글 분석 및 분류**
   - 키워드 기반 댓글 필터링
   - 자동 키워드 추출
   - AI 기반 정치 성향 분류
   - 판단불가/중도 댓글 강제 재분류 (좌/우 중 하나로)

2. **학습 데이터 누적**
   - 분류된 좌파/우파 댓글을 메모리에 누적 저장
   - 서버 실행 중에는 계속 유지
   - 여러 영상의 댓글을 계속 학습 가능

3. **AI 페르소나 토론**
   - 좌파/우파 페르소나가 학습된 댓글을 바탕으로 토론
   - 실시간 채팅 형식으로 번갈아가며 응답
   - 3-5 라운드 토론 진행

## 파일 구조

```
test/
├── app_battle.py           # FastAPI 메인 애플리케이션
├── persona_service.py      # AI 페르소나 토론 서비스
├── reclassifier.py         # 판단불가 댓글 재분류 모듈
├── battle.html             # 프론트엔드 HTML
├── battle.js               # 프론트엔드 JavaScript
├── test_comments.html      # 기존 테스트 페이지 (참고용)
├── test_comments.js        # 기존 테스트 JS (참고용)
└── app_test_only.py        # 기존 테스트 앱 (참고용)
```

## 설치 및 실행

### 1. 필요한 패키지 설치

```bash
pip install fastapi uvicorn openai python-dotenv
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```
OPENAI_API_KEY=your-api-key-here
```

### 3. 서버 실행

```bash
# test 디렉토리에서
python app_battle.py

# 또는
uvicorn app_battle:app --host 0.0.0.0 --port 5000
```

### 4. 브라우저에서 접속

```
http://localhost:5000
```

## 사용 방법

### 1단계: 댓글 입력
- 영상 키워드를 콤마로 구분하여 입력
- 댓글을 한 줄에 하나씩 입력

### 2단계: 분석 시작
- "댓글 분석 및 학습 시작" 버튼 클릭
- 자동으로 다음 과정이 진행됩니다:
  1. 키워드 필터링
  2. 키워드 추출
  3. 정치 성향 1차 분류
  4. 판단불가/중도 재분류
  5. 학습 데이터 저장
  6. AI 페르소나 토론 자동 시작

### 3단계: 결과 확인
- 각 단계별 결과를 화면에서 확인
- AI 페르소나 간 실시간 토론 관람

### 4단계: 추가 학습 (선택)
- 다른 영상의 댓글을 추가로 입력하여 다시 분석
- 이전 학습 데이터에 계속 누적됨
- 더 많은 데이터로 페르소나가 더 풍부한 토론 진행

## API 엔드포인트

### POST /api/battle/analyze-and-learn
댓글 분석 및 학습 데이터 저장

**요청:**
```json
{
  "keywords": ["정부", "정책", "대통령"],
  "comments": ["댓글1", "댓글2", "..."]
}
```

**응답:**
```json
{
  "step3_filtered": {...},
  "step4_keywords": {...},
  "step5_classified": {
    "training_data_accumulated": {
      "left": 10,
      "right": 8
    },
    ...
  }
}
```

### POST /api/battle/start-debate
AI 페르소나 토론 시작

**요청:**
```json
{
  "topic": "현재 정부 정책",
  "rounds": 3
}
```

**응답:**
```json
{
  "topic": "현재 정부 정책",
  "messages": [
    {
      "round": 1,
      "speaker": "좌파",
      "message": "...",
      "timestamp": "..."
    },
    ...
  ]
}
```

### GET /api/battle/training-data
현재 학습 데이터 조회

**응답:**
```json
{
  "left": {
    "count": 10,
    "comments": ["...", "..."]
  },
  "right": {
    "count": 8,
    "comments": ["...", "..."]
  }
}
```

## 주의사항

1. **OpenAI API 키 필요**: 페르소나 토론과 재분류를 위해 OpenAI API 키가 필요합니다.

2. **메모리 저장**: 학습 데이터는 메모리에만 저장되므로 서버 재시작 시 초기화됩니다.

3. **비용**: OpenAI API 사용량에 따라 비용이 발생할 수 있습니다.

4. **백엔드 의존성**: `backend.services.comment_service`와 `backend.models.classifier`가 없는 경우 간단한 Mock 클래스를 사용합니다.

## 문제 해결

### 백엔드 모듈을 찾을 수 없습니다
- Mock 클래스가 자동으로 사용되므로 기본 기능은 작동합니다
- 완전한 기능을 위해서는 원본 프로젝트의 backend 모듈이 필요합니다

### OpenAI API 오류
- `.env` 파일의 API 키를 확인하세요
- API 사용 한도를 확인하세요

### 토론이 시작되지 않음
- 학습 데이터가 충분한지 확인하세요 (좌/우 각각 최소 1개 이상)
- 콘솔 로그를 확인하여 오류 메시지를 확인하세요

## 라이선스

© 2025 색깔전쟁

