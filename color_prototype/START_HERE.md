# 🎭 Color Prototype - 시작하기

## 환영합니다! 👋

Color Prototype은 YouTube 정치 댓글을 분석하여 AI 페르소나를 생성하고 토론을 시뮬레이션하는 시스템입니다.

## 🚀 빠른 시작 (5분)

### 1단계: 패키지 설치
```bash
pip install -r requirements.txt
```

### 2단계: API 키 설정
프로젝트 루트에 `.env` 파일 생성:
```
YOUTUBE_DATA_API_KEY=your_youtube_api_key
```

### 3단계: 서버 실행
```bash
cd backend
python main.py
```

### 4단계: 웹 접속
브라우저에서 http://localhost:8000 접속

## 📚 상세 가이드

- **설치 가이드**: [docs/INSTALLATION.md](docs/INSTALLATION.md)
- **빠른 시작**: [docs/QUICK_START.md](docs/QUICK_START.md)
- **프로젝트 요약**: [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)
- **전체 문서**: [README.md](README.md)

## 🎯 주요 기능

### 1️⃣ Tab1 - 기존 페르소나 (kogpt2)
- 빠른 실행 (3-5분)
- CPU 지원
- 경량 모델

### 2️⃣ Tab2 - LoRA 페르소나 (SOLAR-Mini)
- 정교한 분석 (5-10분)
- MAE 분석 포함
- GPU 권장

### 📰 팩트체크
- 네이버 + DuckDuckGo 검색
- 증거 기반 판정
- 신뢰도 평가

## ⚠️ 필수 요구사항

- Python 3.9+
- YouTube Data API 키
- 8GB RAM 이상

## 💡 첫 테스트

1. YouTube URL 입력 (예: `dQw4w9WgXcQ`)
2. 토론 주제 입력 (예: "현재 정부 정책")
3. "YouTube 분석 및 AI 토론 시작" 클릭
4. 결과 확인!

## 🐛 문제 발생 시

- [INSTALLATION.md](docs/INSTALLATION.md)의 "문제 해결" 섹션 참고
- 이슈 등록

## 📞 도움말

질문이나 문제가 있으면 이슈를 등록해주세요!

---

**즐거운 사용 되세요! 🎉**

