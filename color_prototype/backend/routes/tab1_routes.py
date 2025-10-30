"""
Tab1 라우터 - 기존 페르소나 (kogpt2)
YouTube → 댓글 수집 → 분류 → 페르소나 생성 → 토론
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import sys

# 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.youtube_processor import YouTubeProcessor
from modules.classifier import CommentClassifier
from modules.persona_original import PersonaEngine, DebateEngine
from modules.factcheck_engine import FactCheckEngine

router = APIRouter()

# 전역 상태 (간단한 구현)
youtube_processor = YouTubeProcessor()
classifier = CommentClassifier()
persona_engine = PersonaEngine()
debate_engine = DebateEngine(persona_engine)
factcheck_engine = FactCheckEngine()


class YouTubePipelineRequest(BaseModel):
    youtube_url: str
    topic: str = "현재 정부 정책"
    rounds: int = 5


class FactCheckRequest(BaseModel):
    claim: str


@router.post("/youtube-pipeline")
async def run_youtube_pipeline(request: YouTubePipelineRequest):
    """
    YouTube 전체 파이프라인 실행
    1. 댓글 수집
    2. 좌/우 분류
    3. 페르소나 생성 (kogpt2)
    4. AI 토론
    """
    try:
        print(f"\n{'='*60}")
        print(f"Tab1: 기존 페르소나 파이프라인 시작")
        print(f"{'='*60}\n")
        
        # 1. YouTube 처리
        print("📹 [1/5] YouTube 처리...")
        yt_result = youtube_processor.run_pipeline(request.youtube_url)
        
        if "error" in yt_result:
            raise HTTPException(status_code=400, detail=yt_result["error"])
        
        comments = yt_result.get("comments", [])
        if not comments:
            raise HTTPException(status_code=400, detail="댓글을 찾을 수 없습니다")
        
        # 2. 댓글 분류
        print("\n🔍 [2/5] 댓글 분류...")
        classified_comments = classifier.classify_batch(comments)
        stats = classifier.get_statistics(classified_comments)
        
        print(f"✓ 좌파: {len(stats['left_comments'])}개")
        print(f"✓ 우파: {len(stats['right_comments'])}개")
        
        if len(stats['left_comments']) < 5 or len(stats['right_comments']) < 5:
            raise HTTPException(
                status_code=400,
                detail=f"좌파 또는 우파 댓글이 부족합니다 (좌파: {len(stats['left_comments'])}, 우파: {len(stats['right_comments'])})"
            )
        
        # 3. 페르소나 생성
        print("\n🤖 [3/5] 페르소나 생성...")
        persona_engine.add_comments(stats['left_comments'], stats['right_comments'])
        
        left_persona = persona_engine.generate_persona("left")
        right_persona = persona_engine.generate_persona("right")
        
        # 4. AI 토론
        print("\n🎭 [4/5] AI 토론 시작...")
        debate_log = debate_engine.start_debate(request.topic, request.rounds)
        
        print(f"\n{'='*60}")
        print("Tab1 파이프라인 완료!")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "video_id": yt_result.get("video_id"),
            "summary": {
                "text": yt_result.get("text", "")[:500],
                "keywords": yt_result.get("keywords", [])
            },
            "classification": {
                "total": stats['total'],
                "left_count": len(stats['left_comments']),
                "right_count": len(stats['right_comments']),
                "statistics": stats['counts']
            },
            "personas": {
                "left": left_persona,
                "right": right_persona
            },
            "debate": debate_log,
            "message": "기존 페르소나 파이프라인 완료"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"파이프라인 처리 실패: {str(e)}")


@router.post("/factcheck")
async def run_factcheck(request: FactCheckRequest):
    """팩트체크 실행"""
    try:
        result = factcheck_engine.check_claim(request.claim)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        print(f"❌ 팩트체크 오류: {e}")
        raise HTTPException(status_code=500, detail=f"팩트체크 실패: {str(e)}")


@router.get("/status")
async def get_status():
    """현재 상태 조회"""
    return {
        "status": "ready",
        "persona_engine": "kogpt2",
        "left_comments": len(persona_engine.left_comments),
        "right_comments": len(persona_engine.right_comments),
        "personas_generated": persona_engine.left_persona is not None and persona_engine.right_persona is not None
    }

