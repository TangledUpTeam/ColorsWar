# Ollama 설치 및 사용 가이드 (무료!)

## 왜 Ollama인가?

✅ **완전 무료** - OpenAI API 비용 없음  
✅ **로컬 실행** - 인터넷 없이도 작동  
✅ **빠른 속도** - 로컬에서 즉시 응답  
✅ **개인정보 보호** - 데이터가 외부로 나가지 않음

---

## 1️⃣ Ollama 설치

### Windows

1. https://ollama.com/download 에서 다운로드
2. 설치 파일 실행
3. 설치 완료!

### Linux/Mac

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## 2️⃣ 모델 다운로드

터미널에서 실행:

```bash
# 추천: Llama 3.2 (빠르고 가벼움, 한국어 지원)
ollama pull llama3.2

# 또는 다른 모델 선택:
ollama pull mistral        # 영어에 강함
ollama pull gemma2         # Google 모델
ollama pull qwen2.5        # 중국어/한국어 강함
```

### 모델 크기 비교

| 모델 | 크기 | 속도 | 한국어 품질 |
|------|------|------|-------------|
| llama3.2 | ~2GB | ⚡⚡⚡ | ⭐⭐⭐ |
| mistral | ~4GB | ⚡⚡ | ⭐⭐ |
| qwen2.5 | ~4GB | ⚡⚡ | ⭐⭐⭐⭐ |
| gemma2 | ~5GB | ⚡⚡ | ⭐⭐⭐ |

---

## 3️⃣ Ollama 서버 시작

### 자동 시작 (권장)

Ollama를 설치하면 **자동으로 백그라운드에서 실행**됩니다.

### 수동 시작

```bash
ollama serve
```

### 확인

```bash
# 모델 목록 확인
ollama list

# 테스트
ollama run llama3.2 "안녕하세요"
```

---

## 4️⃣ 색깔전쟁 시스템 실행

### .env 파일 설정 (선택사항)

```bash
# 기본값을 사용하므로 설정 안해도 됩니다
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 서버 실행

```bash
cd test

# 방법 1: Python으로 실행
python app_battle.py

# 방법 2: uvicorn으로 실행 (권장)
uvicorn app_battle:app --host 0.0.0.0 --port 5000 --reload
```

### 브라우저 접속

```
http://localhost:5000
```

---

## 🔧 문제 해결

### "connection refused" 오류

→ Ollama가 실행 중인지 확인하세요:

```bash
ollama serve
```

### 모델이 너무 느림

→ 더 작은 모델 사용:

```bash
ollama pull llama3.2:1b  # 1B 파라미터 (가장 빠름)
```

.env 파일에서:
```
OLLAMA_MODEL=llama3.2:1b
```

### 한국어 품질이 별로임

→ 한국어에 최적화된 모델 사용:

```bash
ollama pull qwen2.5
```

.env 파일에서:
```
OLLAMA_MODEL=qwen2.5
```

---

## 💡 추천 설정

### 개발/테스트용 (빠른 속도)

```bash
ollama pull llama3.2:1b
```

```env
OLLAMA_MODEL=llama3.2:1b
```

### 실사용 (품질 우선)

```bash
ollama pull qwen2.5
```

```env
OLLAMA_MODEL=qwen2.5
```

---

## 📊 성능 비교

### OpenAI GPT-4o-mini (유료)
- ✅ 품질: 최고
- ❌ 비용: $0.15/1M tokens
- ❌ 속도: 네트워크 지연
- ❌ 개인정보: 외부 전송

### Ollama Llama 3.2 (무료)
- ✅ 비용: 완전 무료
- ✅ 속도: 매우 빠름 (로컬)
- ✅ 개인정보: 안전 (로컬)
- ⚠️ 품질: 우수 (GPT-4보다는 낮음)

---

## 🎯 빠른 시작 요약

```bash
# 1. Ollama 설치
# https://ollama.com/download

# 2. 모델 다운로드
ollama pull llama3.2

# 3. 서버 확인 (자동 실행됨)
ollama list

# 4. 색깔전쟁 실행
cd test
uvicorn app_battle:app --host 0.0.0.0 --port 5000 --reload

# 5. 브라우저 접속
# http://localhost:5000
```

---

## 🔄 OpenAI로 다시 전환하려면?

기존 OpenAI 방식으로 돌아가려면:

```bash
# 1. openai 패키지 설치
pip install openai

# 2. .env 파일 생성
OPENAI_API_KEY=sk-your-api-key

# 3. 환경 변수 설정
USE_OPENAI=true
```

코드는 Ollama가 실패하면 자동으로 키워드 기반 분류로 폴백됩니다.

---

## 📚 더 알아보기

- Ollama 공식 문서: https://ollama.com/
- 모델 목록: https://ollama.com/library
- GitHub: https://github.com/ollama/ollama

---

**Ollama로 완전 무료로 AI 페르소나 배틀을 즐기세요! 🎭**

