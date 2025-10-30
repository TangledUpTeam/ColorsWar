"""
색깔전쟁 - AI 페르소나 배틀 시스템
댓글 분석 + 학습 + 페르소나 토론
"""
import os
import sys
import io
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import logging
from dotenv import load_dotenv

# 오직 최상위(.env)만 사용
ROOT_ENV = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
try:
    loaded = load_dotenv(ROOT_ENV, override=True)
    print(f"[dotenv] loaded(app root-only): {ROOT_ENV} -> {loaded}")
except Exception as e:
    print(f"[dotenv] app load error: {e}")

# Windows 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

# 외부/프로젝트 모듈 (core 관련 임포트 제거)
from reclassifier import ForceReclassifier
from persona_service import PersonaBattleService
from youtube_pipeline.youtube_full_pipeline import YouTubeFullPipeline

# 요청/응답 모델
class YouTubePipelineRequest(BaseModel):
    youtube_url: str
    topic: str = "현재 정부 정책"
    rounds: int = 5

class YouTubePipelineResponse(BaseModel):
    success: bool
    video_id: str | None = None
    summary: dict | None = None
    analysis: dict | None = None
    debate: list | None = None
    message: str | None = None

app = FastAPI(title="색깔전쟁 - AI 페르소나 배틀", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 정적 파일 제공(존재 시)
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    path = os.path.join(static_dir, "battle.html")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>battle.html 파일을 찾을 수 없습니다.</h1>")

@app.post("/api/youtube-pipeline", response_model=YouTubePipelineResponse)
async def run_youtube_pipeline(request: YouTubePipelineRequest):
    """
    YouTube 전체 파이프라인 실행 (오디오->전사->요약->댓글수집->분석->토론)
    core 패키지 참조는 제거되어 youtube_pipeline + persona_service/reclassifier 사용.
    """
    pipeline = YouTubeFullPipeline(base_dir=os.path.dirname(__file__))
    try:
        res = pipeline.run_full_pipeline(request.youtube_url, topic=request.topic, rounds=request.rounds)
        if not res:
            raise HTTPException(status_code=500, detail="파이프라인 처리 실패 (결과가 비어있음)")
        return YouTubePipelineResponse(
            success=True,
            video_id=res.get("video_id"),
            summary=res.get("summary"),
            analysis=res.get("analysis"),
            debate=res.get("debate"),
            message="파이프라인 실행 완료"
        )
    except HTTPException:
        raise
    except Exception as e:
        # 전체 스택트레이스 로그 출력(uvicorn 콘솔과 stderr에 남음)
        logging.exception("유튜브 파이프라인 실행 중 예외 발생")
        traceback.print_exc()
        # 클라이언트에는 간단한 메시지 전달
        raise HTTPException(status_code=500, detail=f"파이프라인 처리 실패: {e}")

# 간단 서버 시작 스크립트
if __name__ == "__main__":
    uvicorn.run("app_battle:app", host="0.0.0.0", port=5000, reload=True, log_level="info")
