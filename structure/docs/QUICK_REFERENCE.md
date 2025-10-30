# 빠른 참조 가이드

## 🎯 자주 수정하는 부분

### 📍 주요 파일 위치

| 수정 내용 | 파일 | 줄 번호 |
|-----------|------|---------|
| 좌파 입장 | `persona_service.py` | 44-50 |
| 좌파 스타일 | `persona_service.py` | 52-56 |
| 우파 입장 | `persona_service.py` | 115-121 |
| 우파 스타일 | `persona_service.py` | 123-127 |
| 응답 길이 | `persona_service.py` | 59, 130 |
| 라운드 수 | `battle.html` | 405 (기본값) |
| 라운드 수 | `battle.js` | 122 (코드) |
| 학습 데이터 개수 | `persona_service.py` | 37, 108 |

---

## ⚡ 1분 수정 가이드

### 라운드 수 늘리기
**파일**: `battle.html` 405번째 줄
```html
value="5"    →    value="10"
```

### 응답 더 길게
**파일**: `persona_service.py` 59, 130번째 줄
```python
200-300자    →    500-800자
```

### 좌파 더 공격적으로
**파일**: `persona_service.py` 52-56번째 줄
```python
토론 스타일:
- 매우 열정적이고 투쟁적
- 불평등을 날카롭게 비판
```

### 우파 더 논리적으로
**파일**: `persona_service.py` 123-127번째 줄
```python
토론 스타일:
- 매우 논리적이고 체계적
- 데이터와 통계 중심
```

---

## 🔧 자주 묻는 질문

### Q1. 토론이 너무 짧아요
**A**: `battle.html` 405번째 줄
```html
value="5" → value="10"
```

### Q2. 응답이 너무 간단해요
**A**: `persona_service.py` 59, 130번째 줄
```python
200-300자 → 500-800자
```

### Q3. AI가 너무 예의 바르게 말해요
**A**: `persona_service.py` 52-56, 123-127번째 줄
```python
토론 스타일:
- 공격적이고 도발적
- 상대방 논리를 강하게 반박
```

### Q4. 페르소나 성격 바꾸고 싶어요
**A**: `persona_service.py`
- 좌파: 44-56번째 줄
- 우파: 115-127번째 줄

### Q5. 더 많은 학습 데이터 사용하고 싶어요
**A**: `persona_service.py` 37, 108번째 줄
```python
[:30] → [:50]
```

---

## 📝 체크리스트

### 수정 후 확인사항
- [ ] 파일 저장
- [ ] 서버 자동 재시작 확인 (터미널에서 "Reloading..." 메시지)
- [ ] 브라우저 새로고침 (F5)
- [ ] 새로운 댓글 분석 시작
- [ ] 토론 결과 확인

---

## 🎨 인기있는 커스터마이징

### 1. 격렬한 토론
```python
# persona_service.py
토론 스타일:
- 🔥 매우 공격적이고 도발적
- ⚔️ 상대방 논리를 강하게 공격
- 💢 감정적이고 열정적
```

### 2. 학술적 토론
```python
# persona_service.py
토론 스타일:
- 📚 학술적이고 체계적
- 📊 데이터와 연구 결과 중심
- 🎓 정중하고 논리적
```

### 3. 재미있는 토론
```python
# persona_service.py
토론 스타일:
- 😄 유머러스하고 재치있게
- 💭 비유와 예시를 많이 사용
- 🎭 캐릭터를 살려서 표현
```

---

## 🚀 고급 팁

### 모델 성능 향상
```bash
# 더 좋은 모델로 변경
ollama pull qwen2.5

# .env 파일
OLLAMA_MODEL=qwen2.5
```

### 응답 속도 향상
```bash
# 더 빠른 모델 사용
ollama pull llama3.2:1b

# .env 파일
OLLAMA_MODEL=llama3.2:1b
```

### Temperature 조절
```python
# persona_service.py 78, 149번째 줄
"temperature": 0.8    # 0.0-2.0
```
- 낮음(0.1-0.3): 일관적, 예측가능
- 중간(0.5-0.8): 균형잡힘 ⭐
- 높음(1.0-2.0): 창의적, 다양함

---

## 📚 더 자세한 정보

- **페르소나 상세 가이드**: `PERSONA_GUIDE.md`
- **토론 설정 가이드**: `DEBATE_SETTINGS.md`
- **Ollama 설정**: `OLLAMA_SETUP.md`
- **전체 가이드**: `START_HERE.md`

---

**이 파일을 북마크해두고 빠르게 참조하세요! 🎯**

