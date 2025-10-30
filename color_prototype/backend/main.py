"""
Color Prototype FastAPI 메인 서버
2개 탭 (기존 페르소나 vs LoRA 페르소나) 통합
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys

# 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from routes import tab1_routes, tab2_routes

# FastAPI 앱 초기화
app = FastAPI(
    title="Color Prototype - AI 페르소나 배틀",
    description="YouTube 댓글 분석 → 페르소나 생성 → AI 토론 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# 라우터 등록
app.include_router(tab1_routes.router, prefix="/api/tab1", tags=["Tab1 - 기존 페르소나"])
app.include_router(tab2_routes.router, prefix="/api/tab2", tags=["Tab2 - LoRA 페르소나"])


@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 엔드포인트 - 프론트엔드 HTML 반환"""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Color Prototype</h1><p>Frontend not found</p>")


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "Color Prototype API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    print("""
==========================================
🎭 Color Prototype 서버 시작
------------------------------------------
📍 API 엔드포인트:
1️⃣ Tab1 (기존 페르소나):
   - POST /api/tab1/youtube-pipeline
   - POST /api/tab1/factcheck
   
2️⃣ Tab2 (LoRA 페르소나):
   - POST /api/tab2/youtube-pipeline
   - POST /api/tab2/factcheck

📚 API 문서: http://localhost:8000/docs
==========================================
    """)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

