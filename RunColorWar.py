"""
ColorWar 통합 실행 파일
YouTube 댓글 분석 → AI 페르소나 → 팩트체크 통합 시스템
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import sys
import os

# 모듈 경로 추가
BASE_DIR = Path(__file__).parent.resolve()

# 라우터 임포트
factcheck_app = None
comments_router = persona_router = debate_router = persona_health_router = None
youtube_router = topic_router = None

try:
    # Factcheck 모듈 - 패키지로 정상 임포트
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    from factcheck.api import app as factcheck_app
    print("✓ Factcheck 모듈 로드 완료")
except Exception as e:
    print(f"⚠️  Factcheck 모듈 로드 실패: {e}")
    import traceback
    traceback.print_exc()

try:
    # Persona 모듈 - 패키지 기준 임포트
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    from persona.backend.routes import (
        comments_router,
        persona_router,
        debate_router,
        health_router as persona_health_router,
    )
    print("✓ Persona 모듈 로드 완료")
except Exception as e:
    print(f"⚠️  Persona 모듈 로드 실패: {e}")
    import traceback
    traceback.print_exc()

try:
    # Structure 모듈
    structure_sys_path = str(BASE_DIR / "structure")
    if structure_sys_path not in sys.path:
        sys.path.insert(0, structure_sys_path)
    
    from routes.youtube_routes import router as youtube_router
    from routes.topic_routes import router as topic_router
    print("✓ Structure 모듈 로드 완료")
except Exception as e:
    print(f"⚠️  Structure 모듈 로드 실패: {e}")
    import traceback
    traceback.print_exc()

# ---------------------------------------------------------
# ✅ FastAPI 앱 초기화
# ---------------------------------------------------------
app = FastAPI(
    title="ColorWar - 정치 댓글 분석 시스템",
    description="""
    YouTube 정치 댓글을 수집하고, AI 페르소나를 생성하여 토론을 시뮬레이션하며, 
    뉴스 팩트체크 기능까지 제공하는 종합 정치 분석 시스템입니다.
    
    ## 주요 기능
    - 📹 YouTube 파이프라인: 댓글 수집 및 분석
    - 🎭 AI 페르소나: 좌/우 성향 페르소나 생성 및 토론
    - 📰 팩트체크: 뉴스 기반 신뢰도 평가
    """,
    version="1.0.0"
)

# ---------------------------------------------------------
# ✅ CORS 미들웨어
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# ✅ 정적 파일 서빙
# ---------------------------------------------------------
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# ---------------------------------------------------------
# ✅ 라우터 등록
# ---------------------------------------------------------

# 1. Factcheck 모듈 (서브 앱 마운트)
if factcheck_app:
    app.mount("/api/factcheck", factcheck_app)
    print("✓ Factcheck 모듈 로드 완료")

# 2. Persona 모듈 (라우터 등록)
if comments_router:
    app.include_router(comments_router, prefix="/api/persona", tags=["Persona - 댓글"])
if persona_router:
    app.include_router(persona_router, prefix="/api/persona", tags=["Persona - 생성"])
if debate_router:
    app.include_router(debate_router, prefix="/api/persona", tags=["Persona - 토론"])
if persona_health_router:
    app.include_router(persona_health_router, prefix="/api/persona", tags=["Persona - 상태"])
if comments_router or persona_router:
    print("✓ Persona 모듈 로드 완료")

# 3. Structure 모듈 (라우터 등록)
if youtube_router:
    app.include_router(youtube_router, prefix="/api/structure", tags=["Structure - YouTube"])
if topic_router:
    app.include_router(topic_router, prefix="/api/structure", tags=["Structure - 주제분석"])
if youtube_router or topic_router:
    print("✓ Structure 모듈 로드 완료")

# ---------------------------------------------------------
# ✅ 루트 엔드포인트
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 엔드포인트 - 프론트엔드 HTML 반환"""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    
    # 프론트엔드 없으면 API 정보 반환
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ColorWar API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                max-width: 600px;
            }
            h1 { font-size: 3rem; margin: 0 0 20px 0; }
            p { font-size: 1.2rem; margin: 10px 0; }
            a {
                color: #fff;
                text-decoration: none;
                background: rgba(255,255,255,0.2);
                padding: 10px 20px;
                border-radius: 10px;
                display: inline-block;
                margin-top: 20px;
                transition: all 0.3s;
            }
            a:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎭 ColorWar</h1>
            <p>정치 댓글 분석 시스템</p>
            <p>YouTube 댓글 → AI 페르소나 → 팩트체크</p>
            <a href="/docs">📚 API 문서 보기</a>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """전체 시스템 헬스 체크"""
    return {
        "status": "healthy",
        "service": "ColorWar API",
        "version": "1.0.0",
        "modules": {
            "factcheck": factcheck_app is not None,
            "persona": comments_router is not None,
            "structure": youtube_router is not None
        }
    }


# ---------------------------------------------------------
# ✅ 로컬 실행
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    
    print("""
==========================================
🎭 ColorWar 통합 서버 시작
==========================================
📍 API 엔드포인트:

1️⃣  Structure (YouTube 파이프라인)
   - POST /api/structure/youtube-pipeline
   - POST /api/structure/analyze-topics
   - GET  /api/structure/status

2️⃣  Persona (AI 페르소나 & 토론)
   - POST /api/persona/api/comments/left
   - POST /api/persona/api/comments/right
   - POST /api/persona/api/comments/generate-persona
   - POST /api/persona/api/debate/start
   - POST /api/persona/api/debate/next

3️⃣  Factcheck (뉴스 팩트체크)
   - POST /api/factcheck/factcheck
   - POST /api/factcheck/factcheck/batch
   - GET  /api/factcheck/health

📚 API 문서: http://localhost:8000/docs
🏥 헬스체크: http://localhost:8000/health
==========================================
    """)
    
    uvicorn.run(
        "RunColorWar:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

