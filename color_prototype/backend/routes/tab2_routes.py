"""
Tab2 라우터 - LoRA 페르소나
YouTube → 댓글 수집 → 분류 → MAE 분석 → LoRA 학습 → 토론
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
from modules.persona_lora import MannerAndEmotionAnalyzer, PersonaFineTuner, PersonaDebater
from modules.factcheck_engine import FactCheckEngine

router = APIRouter()

# 전역 상태
youtube_processor = YouTubeProcessor()
classifier = CommentClassifier()
mae_analyzer = MannerAndEmotionAnalyzer()
persona_tuner = PersonaFineTuner()
persona_debater = PersonaDebater(use_local_model=False)  # Ollama 모드
factcheck_engine = FactCheckEngine()


class YouTubePipelineRequest(BaseModel):
    youtube_url: str
    topic: str = "현재 정부 정책"
    rounds: int = 5
    train_model: bool = False  # 실제 LoRA 학습 여부 (시간 소요)


class FactCheckRequest(BaseModel):
    claim: str


@router.post("/youtube-pipeline")
async def run_youtube_pipeline(request: YouTubePipelineRequest):
    """
    YouTube 전체 파이프라인 실행 (LoRA 버전)
    1. 댓글 수집
    2. 좌/우 분류
    3. MAE 분석 (말투/감정)
    4. LoRA 학습 (선택)
    5. AI 토론
    """
    try:
        print(f"\n{'='*60}")
        print(f"Tab2: LoRA 페르소나 파이프라인 시작")
        print(f"{'='*60}\n")
        
        # 1. YouTube 처리
        print("📹 [1/6] YouTube 처리...")
        yt_result = youtube_processor.run_pipeline(request.youtube_url)
        
        if "error" in yt_result:
            raise HTTPException(status_code=400, detail=yt_result["error"])
        
        comments = yt_result.get("comments", [])
        if not comments:
            raise HTTPException(status_code=400, detail="댓글을 찾을 수 없습니다")
        
        # 2. 댓글 분류
        print("\n🔍 [2/6] 댓글 분류...")
        classified_comments = classifier.classify_batch(comments)
        stats = classifier.get_statistics(classified_comments)
        
        print(f"✓ 좌파: {len(stats['left_comments'])}개")
        print(f"✓ 우파: {len(stats['right_comments'])}개")
        
        if len(stats['left_comments']) < 5 or len(stats['right_comments']) < 5:
            raise HTTPException(
                status_code=400,
                detail=f"좌파 또는 우파 댓글이 부족합니다 (좌파: {len(stats['left_comments'])}, 우파: {len(stats['right_comments'])})"
            )
        
        # 3. MAE 분석 (말투/감정)
        print("\n🎨 [3/6] MAE 분석 (말투/감정)...")
        mae_result = mae_analyzer.analyze_batch(classified_comments)
        
        left_training_data = mae_analyzer.extract_training_data(mae_result, 'left')
        right_training_data = mae_analyzer.extract_training_data(mae_result, 'right')
        
        print(f"✓ 좌파 학습 데이터: {len(left_training_data['training_texts'])}개")
        print(f"✓ 우파 학습 데이터: {len(right_training_data['training_texts'])}개")
        
        # 4. LoRA 학습 (선택적)
        if request.train_model:
            print("\n🔥 [4/6] LoRA 파인튜닝 시작...")
            print("⚠ 주의: 실제 학습은 시간이 오래 걸립니다. Mock 모드로 실행합니다.")
            
            # Mock 모드로 실행
            left_model_path = persona_tuner.train_persona(left_training_data, "좌파", epochs=1)
            right_model_path = persona_tuner.train_persona(right_training_data, "우파", epochs=1)
            
            print(f"✓ 좌파 모델: {left_model_path}")
            print(f"✓ 우파 모델: {right_model_path}")
        else:
            print("\n⏭️ [4/6] LoRA 학습 건너뛰기 (train_model=False)")
        
        # 5. 페르소나 초기화
        print("\n🤖 [5/6] 페르소나 초기화...")
        persona_debater.initialize_personas(
            left_training_data['style_summary'],
            right_training_data['style_summary']
        )
        
        # 6. AI 토론
        print("\n🎭 [6/6] AI 토론 시작...")
        debate_log = persona_debater.start_debate(request.topic, request.rounds)
        
        print(f"\n{'='*60}")
        print("Tab2 파이프라인 완료!")
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
            "mae_analysis": {
                "left": {
                    "summary": mae_result['left']['summary'],
                    "training_texts_count": len(left_training_data['training_texts']),
                    "style_summary": left_training_data['style_summary']
                },
                "right": {
                    "summary": mae_result['right']['summary'],
                    "training_texts_count": len(right_training_data['training_texts']),
                    "style_summary": right_training_data['style_summary']
                }
            },
            "debate": debate_log,
            "message": "LoRA 페르소나 파이프라인 완료"
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
        "persona_engine": "LoRA (SOLAR-Mini)",
        "mode": "Ollama",
        "personas_initialized": persona_debater.left_persona is not None and persona_debater.right_persona is not None
    }

