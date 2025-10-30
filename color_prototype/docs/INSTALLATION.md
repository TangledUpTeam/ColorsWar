# Color Prototype - 상세 설치 가이드

## 📋 시스템 요구사항

### 최소 요구사항
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.9 이상
- **RAM**: 8GB 이상
- **디스크**: 10GB 이상 여유 공간

### 권장 사양
- **RAM**: 16GB 이상
- **GPU**: NVIDIA GPU (Tab2 LoRA 학습 시)
- **디스크**: SSD 권장

## 🔧 설치 단계

### 1. Python 설치 확인

```bash
python --version
# 또는
python3 --version
```

Python 3.9 이상이 필요합니다. 없다면 [python.org](https://www.python.org/downloads/)에서 다운로드하세요.

### 2. 프로젝트 준비

```bash
# 프로젝트 디렉토리로 이동
cd color_prototype
```

### 3. 가상환경 생성 (권장)

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

가상환경이 활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다.

### 4. 패키지 설치

```bash
# 기본 패키지 설치
pip install -r requirements.txt
```

**설치 시간**: 약 5-10분 (인터넷 속도에 따라 다름)

#### 설치 오류 해결

**Windows에서 bitsandbytes 오류:**
```bash
# bitsandbytes는 Windows에서 문제가 있을 수 있습니다
# 다음 명령으로 건너뛰기:
pip install -r requirements.txt --no-deps
pip install bitsandbytes-windows
```

**Linux에서 권한 오류:**
```bash
pip install -r requirements.txt --user
```

### 5. 환경변수 설정

#### 5.1. .env 파일 생성

프로젝트 루트에 `.env` 파일을 생성하세요:

```bash
# Windows
type nul > .env

# Linux/Mac
touch .env
```

#### 5.2. API 키 설정

`.env` 파일을 열고 다음 내용을 추가:

```
# 필수: YouTube Data API
YOUTUBE_DATA_API_KEY=your_youtube_api_key_here

# 선택: 네이버 검색 API (팩트체크용)
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# 선택: Ollama 설정
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

#### 5.3. YouTube API 키 발급

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. "API 및 서비스" → "라이브러리" 이동
4. "YouTube Data API v3" 검색 및 활성화
5. "사용자 인증 정보" → "사용자 인증 정보 만들기" → "API 키"
6. 생성된 API 키를 `.env` 파일에 붙여넣기

#### 5.4. 네이버 API 키 발급 (선택)

1. [네이버 개발자 센터](https://developers.naver.com/) 접속
2. 애플리케이션 등록
3. "검색" API 선택
4. Client ID와 Client Secret을 `.env` 파일에 붙여넣기

### 6. Ollama 설치 (선택, 권장)

Ollama는 로컬 LLM을 실행하는 도구입니다.

#### Windows
1. [Ollama 다운로드](https://ollama.ai/download)
2. 설치 프로그램 실행
3. 명령 프롬프트에서 확인:
```bash
ollama --version
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### macOS
```bash
brew install ollama
```

#### 모델 다운로드
```bash
# llama3.2 모델 다운로드 (권장)
ollama pull llama3.2

# 또는 다른 모델
ollama pull mistral
ollama pull gemma2
```

### 7. 설치 확인

```bash
# Python 패키지 확인
pip list | grep fastapi
pip list | grep transformers

# 환경변수 확인 (Python에서)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('YouTube API:', 'OK' if os.getenv('YOUTUBE_DATA_API_KEY') else 'NOT SET')"

# Ollama 확인 (설치한 경우)
ollama list
```

## 🚀 서버 실행

### 기본 실행
```bash
cd backend
python main.py
```

### 커스텀 포트
```bash
# 8001 포트로 실행
uvicorn main:app --host 0.0.0.0 --port 8001
```

### 백그라운드 실행 (Linux/Mac)
```bash
nohup python main.py > server.log 2>&1 &
```

### 서버 확인
브라우저에서 다음 URL 접속:
- **웹 인터페이스**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health

## 🐛 문제 해결

### 1. 모듈 import 오류
```
ModuleNotFoundError: No module named 'xxx'
```
**해결**: 
```bash
pip install -r requirements.txt --force-reinstall
```

### 2. CUDA 오류 (GPU 관련)
```
RuntimeError: CUDA out of memory
```
**해결**: 
- Tab1 (CPU 모드) 사용
- 또는 배치 크기 줄이기

### 3. YouTube API 할당량 초과
```
quotaExceeded
```
**해결**: 
- 다음 날까지 대기
- 또는 새 프로젝트 생성

### 4. Ollama 연결 실패
```
Connection refused
```
**해결**: 
```bash
# Ollama 실행 확인
ollama serve

# 또는 재시작
# Windows: 작업 관리자에서 Ollama 종료 후 재시작
# Linux/Mac: sudo systemctl restart ollama
```

### 5. 포트 충돌
```
Address already in use
```
**해결**: 
```bash
# 다른 포트 사용
uvicorn main:app --port 8001

# 또는 기존 프로세스 종료 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 📝 다음 단계

설치가 완료되었다면:
1. [빠른 시작 가이드](QUICK_START.md) 읽기
2. [메인 README](../README.md) 확인
3. 첫 번째 테스트 실행

## 💬 도움말

추가 도움이 필요하면 이슈를 등록해주세요!

