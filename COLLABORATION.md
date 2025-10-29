# 🤝 ColorWar 협업 가이드

## 📋 개발 환경

### 팀 구성
- **macOS 개발자**: 팩트체크 모듈
- **Windows 개발자**: 유튜브 댓글 분석 등

---

## 🔧 초기 설정 (모든 팀원)

### 1. Git Clone

```bash
git clone <repository-url>
cd ColorWar
```

### 2. 환경 변수 설정 (팩트체크 모듈)

```bash
cd factcheck
cp .env.example .env

# .env 파일 편집 (실제 API 키 입력)
# macOS/Linux
nano .env

# Windows (VS Code)
code .env
```

**중요:** `.env` 파일은 절대 Git에 커밋하지 마세요!

### 3. Python 가상환경

#### macOS / Linux

```bash
cd factcheck
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows (PowerShell)

```powershell
cd factcheck
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Windows (CMD)

```cmd
cd factcheck
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

---

## 🚀 실행 방법

### 팩트체크 API 서버

```bash
cd factcheck
source venv/bin/activate  # Windows: venv\Scripts\activate

# API 서버 실행
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 테스트 실행

```bash
# 배치 테스트
python batch_test.py

# 단일 테스트
python main_universal.py "M5 맥북 출시 임박"
```

---

## 📁 프로젝트 구조

```
ColorWar/
├── factcheck/              # 팩트체크 모듈 (포트 8000)
│   ├── api.py             # FastAPI 서버
│   ├── requirements.txt
│   ├── .env              # ⚠️ Git 제외 (민감 정보)
│   └── .env.example      # ✅ Git 포함 (템플릿)
│
├── youtube_comment/       # 유튜브 댓글 분석 (포트 8001)
│   └── ...
│
├── ui/                    # UI 모듈 (포트 8002)
│   └── ...
│
├── .gitignore            # macOS + Windows 협업 설정
└── COLLABORATION.md      # 이 파일
```

---

## 🔒 .gitignore 주요 항목

### macOS 제외 파일
- `.DS_Store` - Finder 설정
- `._*` - 썸네일 캐시
- `.AppleDouble` - 리소스 포크

### Windows 제외 파일
- `Thumbs.db` - 썸네일 캐시
- `Desktop.ini` - 폴더 설정
- `*.lnk` - 바로가기

### Python 제외 파일
- `__pycache__/` - 바이트코드 캐시
- `*.pyc` - 컴파일된 파일
- `venv/` - 가상환경
- `.env` - 환경 변수 (민감 정보)

---

## 🌐 API 엔드포인트 규칙

### 포트 할당

| 모듈 | 포트 | 설명 |
|------|------|------|
| factcheck | 8000 | 팩트체크 API |
| youtube | 8001 | 댓글 분석 API |
| ui | 8002 | 프론트엔드 |

### 엔드포인트 네이밍

각 모듈은 자신의 이름을 prefix로 사용:

```
factcheck:  /factcheck/*
            /factcheck/batch
            /health

youtube:    /youtube/*
            /health  (향후 /youtube/health로 변경 권장)
```

**주의:** `/health` 같은 공통 엔드포인트는 충돌 가능성이 있으므로, prefix 추가를 권장합니다.

---

## 📦 모듈 통합 방법

### 방법 1: 독립 실행 (개발 단계 - 현재)

각자 다른 포트에서 독립 실행:

```bash
# 터미널 1
cd factcheck
uvicorn api:app --port 8000

# 터미널 2
cd youtube
uvicorn api:app --port 8001
```

**호출:**
```bash
curl http://localhost:8000/factcheck -d '{"claim":"..."}'
curl http://localhost:8001/youtube/analyze -d '{"url":"..."}'
```

### 방법 2: 서브 애플리케이션 마운트 (통합 단계)

`main.py` 생성:

```python
from fastapi import FastAPI
from factcheck.api import app as factcheck_app
from youtube.api import app as youtube_app

main_app = FastAPI(title="ColorWar API")

# 서브 애플리케이션 마운트
main_app.mount("/factcheck", factcheck_app)
main_app.mount("/youtube", youtube_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(main_app, host="0.0.0.0", port=8000)
```

**실행:**
```bash
python main.py
```

**호출:**
```bash
curl http://localhost:8000/factcheck/factcheck -d '{"claim":"..."}'
curl http://localhost:8000/youtube/analyze -d '{"url":"..."}'
```

---

## 🐛 자주 발생하는 문제

### 1. Python 명령어 차이

| macOS/Linux | Windows |
|-------------|---------|
| `python3` | `python` |
| `pip3` | `pip` |

### 2. 줄바꿈 문자 (CRLF vs LF)

Git 설정으로 자동 변환:

```bash
# Windows에서 설정 (체크아웃 시 CRLF, 커밋 시 LF)
git config --global core.autocrlf true

# macOS/Linux에서 설정 (항상 LF)
git config --global core.autocrlf input
```

### 3. 경로 구분자

```python
# 잘못된 방법 (Windows에서 오류)
path = "factcheck/data/file.json"  # ❌

# 올바른 방법 (모든 OS에서 작동)
from pathlib import Path
path = Path("factcheck") / "data" / "file.json"  # ✅

# 또는
import os
path = os.path.join("factcheck", "data", "file.json")  # ✅
```

### 4. 환경 변수 로드 실패

```python
# .env 파일 로드 확인
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 로드

# 확인
print(os.getenv("NAVER_CLIENT_ID"))  # None이면 .env 없음
```

---

## ✅ 커밋 전 체크리스트

- [ ] `.env` 파일 제외 확인 (`git status`에서 안 보여야 함)
- [ ] API 키, 비밀번호 등 민감 정보 제거
- [ ] `__pycache__/` 제외 확인
- [ ] `.DS_Store` (macOS) 제외 확인
- [ ] `Thumbs.db` (Windows) 제외 확인
- [ ] 테스트 실행 (`pytest` or `python batch_test.py`)
- [ ] 코드 포맷팅 (`black .` or `autopep8`)

---

## 🔄 Git 워크플로우

### 1. 작업 시작

```bash
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. 작업 중

```bash
git add .
git commit -m "feat: 기능 설명"
```

### 3. 푸시 및 PR

```bash
git push origin feature/your-feature-name
# GitHub에서 Pull Request 생성
```

### 커밋 메시지 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 추가
chore: 빌드/설정 변경
```

---

## 🆘 도움이 필요할 때

### 팩트체크 모듈

- 담당자: [이름]
- 문서: `factcheck/README.md`, `factcheck/API_GUIDE.md`
- 포트: 8000

### 유튜브 모듈

- 담당자: [이름]
- 포트: 8001

---

## 📚 추가 문서

- [팩트체크 API 가이드](factcheck/API_GUIDE.md)
- [팩트체크 README](factcheck/README.md)
- [프로젝트 전체 README](README.md)

---

**마지막 업데이트:** 2025-10-29  
**버전:** 1.0.0

