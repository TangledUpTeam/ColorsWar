# 팩트체크 API 가이드

## 🚀 서버 시작

```bash
# 1. 패키지 설치 (최초 1회)
pip install fastapi uvicorn pydantic

# 2. 서버 시작
cd factcheck
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**서버 주소:** `http://localhost:8000`

---

## 📡 API 엔드포인트

### 1. 루트
```bash
GET /
```
**응답:**
```json
{
  "message": "팩트체크 API 서버",
  "version": "1.0.0",
  "endpoints": {
    "POST /factcheck": "단일 주장 팩트체크",
    "POST /factcheck/batch": "배치 팩트체크",
    "GET /health": "헬스체크"
  }
}
```

---

### 2. 헬스체크
```bash
GET /health
```
**응답:**
```json
{
  "status": "healthy",
  "system": "ready",
  "naver_api": true
}
```

---

### 3. 팩트체크 (단일)
```bash
POST /factcheck
Content-Type: application/json
```

**요청:**
```json
{
  "claim": "M5맥북 출시 임박",
  "max_results": 10
}
```

**응답:**
```json
{
  "claim": "M5맥북 출시 임박",
  "verdict": "True",
  "confidence_score": 7.5,
  "confidence_level": "높음",
  "reasoning": "5개의 관련 Evidence가 발견되었습니다. (신뢰도 7.5/10 - 높음)",
  "evidences": [
    {
      "text": "특히 맥북 프로 라인업은 M5 초급 모델이 먼저 출시될 예정...",
      "source": "네이버뉴스",
      "date": "Mon, 13 Oct 2025 11:44:00 +0900",
      "relevance": 0.84
    }
  ],
  "score_breakdown": {
    "multiple_sources": 2.0,
    "recency": 1.0,
    "matching_strength": 2.0,
    "contradictions": 0.0
  }
}
```

---

### 4. 팩트체크 (배치)
```bash
POST /factcheck/batch
Content-Type: application/json
```

**요청:**
```json
{
  "claims": [
    "M5맥북 출시 임박",
    "한강에 괴물 출현",
    "마을버스 요금인상"
  ],
  "max_results": 10
}
```

**응답:**
```json
{
  "results": [
    {
      "claim": "M5맥북 출시 임박",
      "verdict": "True",
      "confidence_score": 7.5,
      ...
    },
    {
      "claim": "한강에 괴물 출현",
      "verdict": "False",
      "confidence_score": 3.8,
      ...
    }
  ],
  "total": 3
}
```

---

## 💻 사용 예시

### cURL
```bash
# 단일 팩트체크
curl -X POST http://localhost:8000/factcheck \
     -H "Content-Type: application/json" \
     -d '{"claim": "M5맥북 출시 임박"}'

# 배치 팩트체크
curl -X POST http://localhost:8000/factcheck/batch \
     -H "Content-Type: application/json" \
     -d '{
       "claims": ["M5맥북 출시 임박", "한강에 괴물 출현"]
     }'
```

### Python
```python
import requests

# 단일 팩트체크
response = requests.post(
    "http://localhost:8000/factcheck",
    json={"claim": "M5맥북 출시 임박"}
)
result = response.json()
print(f"판정: {result['verdict']}")
print(f"신뢰도: {result['confidence_score']}/10")
```

### JavaScript (fetch)
```javascript
// 단일 팩트체크
fetch('http://localhost:8000/factcheck', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    claim: 'M5맥북 출시 임박'
  })
})
.then(res => res.json())
.then(data => {
  console.log('판정:', data.verdict);
  console.log('신뢰도:', data.confidence_score);
});
```

---

## 🔑 환경변수 (선택)

네이버 API를 사용하려면 `.env` 파일에 추가:

```bash
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```

없어도 크롤링 모드로 작동합니다.

---

## 📊 응답 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `claim` | string | 입력된 주장 |
| `verdict` | string | 판정 (True/False/Uncertain) |
| `confidence_score` | float | 신뢰도 (0-10) |
| `confidence_level` | string | 레벨 (매우 높음/높음/중간/낮음/매우 낮음) |
| `reasoning` | string | 판정 근거 |
| `evidences` | array | 수집된 증거 목록 |
| `score_breakdown` | object | 신뢰도 세부 점수 |

---

## ⚠️ 에러 응답

**400 Bad Request:**
```json
{
  "detail": "주장이 비어있습니다"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "팩트체크 실패: [에러 메시지]"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "시스템 초기화 중입니다"
}
```

---

## 📚 Swagger UI

서버 실행 후 브라우저에서 접속:

- **API 문서:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔧 프로덕션 배포

```bash
# Gunicorn 사용
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# Docker (선택)
docker build -t factcheck-api .
docker run -p 8000:8000 factcheck-api
```

---

## 📞 팀 협업

다른 팀원이 이 API를 호출하려면:

1. **서버 주소 공유:** `http://[your-ip]:8000`
2. **CORS 설정 완료:** 모든 도메인 허용됨
3. **엔드포인트:** `/factcheck` (POST)
4. **요청 형식:** JSON
5. **응답 형식:** JSON

**간단합니다!** 👍

