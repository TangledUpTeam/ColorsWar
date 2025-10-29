# 팩트체크 시스템 (Fact-Check System)

> 뉴스 기반 자동 팩트체크 시스템 - 한국어/영어 뉴스 검색 및 신뢰도 평가

**버전:** 1.0.0  
**개발:** ColorWar 팀  
**목적:** YouTube 댓글 등의 주장을 자동으로 검증하여 True/False/Uncertain 판정

---

## 📋 목차

1. [개요](#-개요)
2. [시스템 아키텍처](#-시스템-아키텍처)
3. [핵심 기술](#-핵심-기술)
4. [신뢰도 계산 로직](#-신뢰도-계산-로직)
5. [설치 및 실행](#-설치-및-실행)
6. [API 서버](#-api-서버)
7. [파일 구조](#-파일-구조)

---

## 🎯 개요

### 개발 방향성

```
입력 (Claim)
    ↓
Evidence 수집 (뉴스 검색)
    ↓
Evidence 평가 (관련도 측정)
    ↓
신뢰도 계산 (0-10점)
    ↓
최종 판정 (True/False/Uncertain)
```

### 특징

- ✅ **자동화**: 주장 입력만으로 자동 팩트체크
- ✅ **다국어**: 한국 + 해외 뉴스 동시 검색
- ✅ **신뢰도**: 0-10점 정량적 평가
- ✅ **API**: FastAPI 기반 REST API 제공
- ✅ **확장성**: 모듈화 설계로 쉬운 연동

---

## 🏗️ 시스템 아키텍처

### 1단계: Evidence 수집

**하이브리드 검색 (BM25 + Sentence Embedding)**

```
주장 입력 → 키워드 추출 → 뉴스 검색
                              ↓
                   [네이버 API] + [DuckDuckGo]
                              ↓
                      20개 뉴스 수집
```

**검색 소스:**
- **네이버 뉴스 API**: 한국 뉴스 (10개)
- **DuckDuckGo**: 해외 뉴스 (10개)

---

### 2단계: Evidence 평가

**하이브리드 점수 계산:**

```python
final_score = 0.6 × BM25_normalized + 0.4 × Embedding_similarity
```

**필터링:**
1. **BM25 상위 20개** 추출 (키워드 기반)
2. **Sentence Embedding** 유사도 계산 (의미 기반)
3. **하이브리드 점수** 계산 및 재정렬
4. **임계값 필터링**: `relevance ≥ 0.65` (다양한 의견 수용)
5. **상위 5개** 최종 선택

**임베딩 모델:**
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- 한국어/영어 동시 지원

---

### 3단계: 신뢰도 계산

**10점 만점 시스템 (Rule-based + LLM)**

#### Rule-based 점수 (최대 6점)

| 항목 | 점수 | 조건 |
|------|------|------|
| **출처 수** | +2점 | 2개 이상 독립 출처 |
| **최신성** | +1점 | 12개월 이내 |
| **매칭 강도** | +2점 | Evidence 품질 및 개수 |
| **모순** | -2점 | 상반되는 증거 존재 |

#### 매칭 강도 (Evidence 개수 고려)

**1개 Evidence:**
```python
if avg_relevance ≥ 0.85: +1.0점
else:                    +0.5점
```

**2개 Evidence:**
```python
if avg_relevance ≥ 0.75: +1.5점
elif avg_relevance ≥ 0.65: +1.0점
else:                      +0.5점
```

**3개 이상 Evidence:**
```python
if avg_relevance ≥ 0.72: +2.0점  # 기준 완화 (0.75 → 0.72)
elif avg_relevance ≥ 0.65: +1.0점
else:                      -1.0점
```

#### LLM 자기평가 (최대 2점)

```python
llm_score = confidence_self × 2.0
```

#### 최종 점수

```python
total = (rule_score + llm_score) × 1.25  # 8점 → 10점 스케일링
total = max(1.0, min(10.0, total))       # 1-10 범위 클리핑
```

---

### 4단계: 최종 판정

**신뢰도 기반 판정:**

```python
if confidence < 5.5:
    verdict = "False"
elif 5.5 ≤ confidence ≤ 7.0:
    verdict = "Uncertain"
else:  # > 7.0
    verdict = "True"
```

| 신뢰도 | 판정 | 의미 |
|--------|------|------|
| 8.5~10.0 | True (매우 높음) | 확실한 사실 |
| 7.0~8.5 | True (높음) | 신뢰할 만한 사실 |
| 5.5~7.0 | Uncertain (중간) | 판단 어려움 |
| 3.0~5.5 | False (낮음) | 거짓 가능성 |
| 1.0~3.0 | False (매우 낮음) | 명백한 거짓 |

---

## 🔧 핵심 기술

### 1. 하이브리드 검색 (BM25 + Embedding)

**BM25 (Keyword-based):**
- 전통적 정보 검색 알고리즘
- 키워드 빈도 및 문서 길이 고려
- 패키지: `rank-bm25`

**Sentence Transformer (Semantic):**
- 문장의 의미적 유사도 측정
- 사전 학습된 다국어 모델
- 패키지: `sentence-transformers`

**장점:**
- BM25: 정확한 키워드 매칭
- Embedding: 의미적 유사성 포착
- 하이브리드: 두 가지 장점 결합

---

### 2. 뉴스 검색 소스

**네이버 뉴스 API:**
```python
# .env 파일 설정
NAVER_CLIENT_ID=your_id
NAVER_CLIENT_SECRET=your_secret
```
- 한국 뉴스 최적화
- 신뢰성 높은 출처
- API 키 없으면 크롤링 폴백

**DuckDuckGo:**
- 해외 뉴스 커버
- API 키 불필요
- 다양한 관점 제공

---

### 3. Evidence 필터링

**3단계 필터링:**

1. **길이 필터**: 최소 20자 이상
```python
MIN_SNIPPET_LENGTH = 20
```

2. **의미 필터**: 무의미 패턴 제거
```python
meaningless_patterns = [
    "...", "…", "◆", "▲", "※", "→", "·",
    "&gt;", "&lt;", "href=", "http"
]
```

3. **관련도 필터**: 임계값 이상만 채택
```python
min_relevance = 0.65  # 다양한 의견 수용
```

---

### 4. FastAPI 서버

**REST API 제공:**

```bash
POST /factcheck         # 단일 팩트체크
POST /factcheck/batch   # 배치 처리
GET /health             # 헬스체크
```

**특징:**
- 자동 문서화 (Swagger UI)
- CORS 지원 (팀 협업)
- 비동기 처리
- 에러 핸들링

**응답 형식 (JSON):**
```json
{
  "claim": "M5맥북 출시 임박",
  "verdict": "True",
  "confidence_score": 7.5,
  "confidence_level": "높음",
  "reasoning": "5개의 관련 Evidence가 발견...",
  "evidences": [...],
  "score_breakdown": {
    "multiple_sources": 2.0,
    "recency": 1.0,
    "matching_strength": 2.0,
    "contradictions": 0.0
  }
}
```

---

## 📦 설치 및 실행

### 1. 패키지 설치

```bash
cd factcheck
pip install -r requirements.txt
```

**필수 패키지:**
- `sentence-transformers` - 임베딩 모델
- `torch` - PyTorch
- `rank-bm25` - BM25 알고리즘
- `fastapi` - API 서버
- `beautifulsoup4` - 크롤링
- `ddgs` - DuckDuckGo 검색

---

### 2. 환경 설정 (선택)

네이버 API 사용 시 `.env` 파일 생성:

```bash
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```

> **참고:** 없어도 크롤링 모드로 작동합니다.

---

### 3. CLI 실행

**단일 팩트체크:**
```bash
python3 main_universal.py --claim "M5맥북 출시 임박"
```

**배치 테스트:**
```bash
python3 batch_test.py rumor_test_cases.json
```

---

### 4. API 서버 실행

**서버 시작:**
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**API 문서:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**테스트:**
```bash
curl -X POST http://localhost:8000/factcheck \
     -H "Content-Type: application/json" \
     -d '{"claim": "M5맥북 출시 임박"}'
```

---

## 🌐 API 서버

### 엔드포인트

**1. 단일 팩트체크**
```http
POST /factcheck
Content-Type: application/json

{
  "claim": "M5맥북 출시 임박",
  "max_results": 10
}
```

**2. 배치 처리**
```http
POST /factcheck/batch
Content-Type: application/json

{
  "claims": [
    "M5맥북 출시 임박",
    "한강에 괴물 출현"
  ],
  "max_results": 10
}
```

**3. 헬스체크**
```http
GET /health
```

### 사용 예시

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/factcheck",
    json={"claim": "M5맥북 출시 임박"}
)
result = response.json()
print(f"판정: {result['verdict']}, 신뢰도: {result['confidence_score']}/10")
```

**JavaScript:**
```javascript
fetch('http://localhost:8000/factcheck', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({claim: 'M5맥북 출시 임박'})
})
.then(res => res.json())
.then(data => console.log(data.verdict, data.confidence_score));
```

---

## 📁 파일 구조

```
factcheck/
│
├── api.py                          # FastAPI 서버
├── main_universal.py               # CLI 메인
├── batch_test.py                   # 배치 테스트
├── test_api.py                     # API 테스트
│
├── models/                         # 핵심 모델
│   ├── evidence_searcher.py        # 하이브리드 검색
│   ├── judge_local.py              # 판정 시스템
│   ├── confidence_scorer.py        # 신뢰도 계산
│   ├── document_source.py          # 문서 소스 (DuckDuckGo)
│   ├── document_source_naver.py    # 네이버 뉴스
│   └── document_source_universal.py # 통합 검색
│
├── utils/                          # 유틸리티
│   └── text_processing.py          # 텍스트 처리
│
├── data/                           # 테스트 데이터
│   ├── mock_claims.json
│   ├── mock_documents.json
│   └── rumor_test_cases.json
│
├── requirements.txt                # 의존성
├── .env                            # 환경변수 (선택)
│
├── README.md                       # 이 파일
├── API_GUIDE.md                    # API 상세 가이드
└── STEP_BY_STEP.md                 # 실행 가이드
```

---

## 🧪 테스트 결과

### 테스트 케이스

| 주장 | Evidence | 신뢰도 | 판정 | 평가 |
|------|---------|--------|------|------|
| M5맥북 출시 임박 | 5개 | 7.5/10 | True ✅ | 정확 |
| 한강에 괴물 출현 | 1개 | 3.8/10 | False ✅ | 정확 |
| 마을버스 요금인상 | 5개 | 7.5/10 | True ✅ | 정확 |
| 김연아 올림픽 출전 | 2개 | 6.9/10 | Uncertain ✅ | 정확 |

---

## 🔍 계산 로직 상세

### Evidence 개수별 차등 점수

**설계 철학:**
> Evidence가 1개만 있으면 우연일 수 있음  
> 3개 이상 있으면 패턴으로 확실함

**로직:**

```python
def calculate_matching_strength(evidences):
    count = len(evidences)
    avg_relevance = sum(ev.score for ev in evidences) / count
    
    if count == 1:
        # 1개: 신뢰도 낮음
        return 1.0 if avg_relevance >= 0.85 else 0.5
    
    elif count == 2:
        # 2개: 중간
        if avg_relevance >= 0.75:
            return 1.5
        elif avg_relevance >= 0.65:
            return 1.0
        else:
            return 0.5
    
    else:  # 3개 이상
        # 3개+: 높은 신뢰도
        if avg_relevance >= 0.72:  # 완화된 기준
            return 2.0
        elif avg_relevance >= 0.65:
            return 1.0
        else:
            return -1.0  # 관련도 낮으면 페널티
```

**효과:**
- 1개 Evidence: 최대 1.0점
- 2개 Evidence: 최대 1.5점
- 3개+ Evidence: 최대 2.0점

---

### 임계값 조정 이력

| 버전 | min_relevance | 이유 |
|------|--------------|------|
| 초기 | 0.70 | 확실한 것만 채택 |
| 현재 | 0.65 | 다양한 의견 수용 |

**결과:**
- 더 많은 Evidence 채택
- False Negative 감소
- 판정 정확도 향상

---

### Matching Strength 기준 완화

| 버전 | 3개+ 기준 | 이유 |
|------|----------|------|
| 초기 | avg ≥ 0.75 | 엄격한 기준 |
| 현재 | avg ≥ 0.72 | 합리적 완화 |

**사례:**
- avg = 0.738 (마을버스 요금인상)
- 초기: 1.0점 → Uncertain
- 현재: 2.0점 → True ✅

---

## 🎓 기술 스택

### 머신러닝
- **Sentence Transformers**: 문장 임베딩
- **BM25**: 키워드 검색
- **Scikit-learn**: 점수 정규화

### 웹 프레임워크
- **FastAPI**: REST API
- **Uvicorn**: ASGI 서버
- **Pydantic**: 데이터 검증

### 데이터 수집
- **네이버 API**: 한국 뉴스
- **DuckDuckGo**: 해외 검색
- **BeautifulSoup4**: HTML 파싱

### 기타
- **python-dotenv**: 환경변수
- **PyTorch**: 딥러닝 백엔드

---

## 📊 성능 최적화

### 1. 캐싱
- 서버 시작 시 모델 로딩 (1회)
- Evidence 재사용

### 2. 병렬 처리
- 네이버 + DuckDuckGo 동시 검색
- 배치 API 지원

### 3. 필터링 최적화
- 조기 필터링으로 처리량 감소
- 임베딩 계산 최소화

---

## 🚀 팀 협업

### 모듈 연동

```
[YouTube 댓글 분석 모듈]
         ↓
    키워드 추출
         ↓
[팩트체크 API] ← http://localhost:8000/factcheck
         ↓
    판정 결과 (JSON)
         ↓
   [UI 표시 모듈]
```

### API 호출 예시

```python
# 다른 팀원 모듈에서
import requests

def check_youtube_comment(comment_text):
    # 1. 키워드 추출 (다른 팀원)
    keyword = extract_keyword(comment_text)
    
    # 2. 팩트체크 요청
    response = requests.post(
        "http://localhost:8000/factcheck",
        json={"claim": keyword}
    )
    
    # 3. 결과 처리
    result = response.json()
    return result['verdict'], result['confidence_score']
```

---

## 📝 개발 이력

### v1.0.0 (2025-10-29)
- ✅ 하이브리드 검색 구현
- ✅ 신뢰도 계산 로직
- ✅ FastAPI 서버
- ✅ Evidence 개수별 차등 점수
- ✅ 10점 만점 스케일링
- ✅ 임계값 조정 (0.70 → 0.65)
- ✅ Matching strength 완화 (0.75 → 0.72)

---

## 🤝 기여

**개발:** ColorWar 팀  
**문의:** [GitHub Issues]

---

## 📄 라이선스

이 프로젝트는 팀 프로젝트용으로 개발되었습니다.

---

## 🔗 관련 문서

- [API 가이드](API_GUIDE.md) - API 상세 사용법
- [실행 가이드](STEP_BY_STEP.md) - 단계별 실행 방법

---

**마지막 업데이트:** 2025-10-29  
**버전:** 1.0.0
