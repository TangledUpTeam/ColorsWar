"""
FastAPI 팩트체크 API 서버

사용법:
    # 서버 시작
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
    
    # 테스트
    curl -X POST http://localhost:8000/factcheck \
         -H "Content-Type: application/json" \
         -d '{"claim": "M5맥북 출시 임박"}'
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from .models.evidence_searcher import EvidenceSearcher
from .models.judge_local import LocalFactCheckJudge
from .models.confidence_scorer import ConfidenceScorer
from .models.document_source_universal import UniversalNewsSearchSource

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="팩트체크 API",
    description="뉴스 기반 팩트체크 시스템 (한국 + 해외)",
    version="1.0.0"
)

# CORS 설정 (다른 팀원 프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에선 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수로 시스템 초기화 (재사용)
searcher = None
judge = None
scorer = None


def initialize_system():
    """팩트체크 시스템 초기화 (지연 초기화)"""
    global searcher, judge, scorer
    
    if searcher and judge and scorer:
        return  # 이미 초기화됨
    
    print("🚀 팩트체크 시스템 초기화 중...")
    
    try:
        # 1) 범용 뉴스 소스
        universal_source = UniversalNewsSearchSource(max_results_per_source=10)
        
        # 2) Evidence 검색기
        searcher = EvidenceSearcher(
            document_source=universal_source,
            embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # 3) 판정자
        judge = LocalFactCheckJudge(method="rule_based")
        
        # 4) 신뢰도 평가기
        scorer = ConfidenceScorer()
        
        print("✅ 팩트체크 시스템 초기화 완료!")
        
        # 네이버 API 키 확인
        if os.getenv("NAVER_CLIENT_ID"):
            print("✅ 네이버 API 키 설정됨")
        else:
            print("⚠️  네이버 API 키 미설정 (크롤링 모드)")
    
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 시스템 초기화 시도 (실패해도 계속 진행)"""
    try:
        initialize_system()
    except Exception as e:
        print(f"⚠️  시작 시 초기화 실패, 첫 요청 시 재시도: {e}")


# Request/Response 모델
class FactCheckRequest(BaseModel):
    claim: str
    max_results: Optional[int] = 10
    
    class Config:
        json_schema_extra = {
            "example": {
                "claim": "M5맥북 출시 임박",
                "max_results": 10
            }
        }


class EvidenceResponse(BaseModel):
    text: str
    source: str
    date: str
    relevance: float


class FactCheckResponse(BaseModel):
    claim: str
    verdict: str
    confidence_score: float
    confidence_level: str
    reasoning: str
    evidences: List[EvidenceResponse]
    score_breakdown: dict


class BatchFactCheckRequest(BaseModel):
    claims: List[str]
    max_results: Optional[int] = 10


class HealthResponse(BaseModel):
    status: str
    system: str
    naver_api: bool


# API 엔드포인트
@app.get("/", response_model=dict)
async def root():
    """API 루트"""
    return {
        "message": "팩트체크 API 서버",
        "version": "1.0.0",
        "endpoints": {
            "POST /factcheck": "단일 주장 팩트체크",
            "POST /factcheck/batch": "배치 팩트체크",
            "GET /health": "헬스체크"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy" if searcher else "initializing",
        "system": "ready",
        "naver_api": bool(os.getenv("NAVER_CLIENT_ID"))
    }


@app.post("/factcheck", response_model=FactCheckResponse)
async def factcheck(request: FactCheckRequest):
    """
    단일 주장 팩트체크
    
    Args:
        request: 팩트체크 요청 (claim, max_results)
    
    Returns:
        팩트체크 결과 (verdict, confidence, evidences 등)
    """
    # 지연 초기화 (첫 요청 시 초기화)
    if not searcher or not judge or not scorer:
        try:
            initialize_system()
        except Exception as e:
            raise HTTPException(
                status_code=503, 
                detail=f"시스템 초기화 실패: {str(e)}"
            )
    
    try:
        claim = request.claim.strip()
        
        if not claim:
            raise HTTPException(status_code=400, detail="주장이 비어있습니다")
        
        # 1) Evidence 검색
        evidences = searcher.search(claim)
        
        if not evidences:
            return FactCheckResponse(
                claim=claim,
                verdict="Uncertain",
                confidence_score=1.0,
                confidence_level="매우 낮음",
                reasoning="관련 Evidence를 찾을 수 없습니다.",
                evidences=[],
                score_breakdown={}
            )
        
        # 2) 판정
        judge_result = judge.judge(claim, evidences)
        
        # 3) 신뢰도 평가
        confidence = scorer.score(evidences, judge_result)
        confidence_level = scorer.get_confidence_level(confidence.total_score)
        
        # 4) 최종 판정 (신뢰도 기반)
        if confidence.total_score < 5.5:
            final_verdict = "False"
            final_reasoning = f"{judge_result.reasoning} (신뢰도 {confidence.total_score:.1f}/10 - 낮음)"
        elif 5.5 <= confidence.total_score <= 7.0:
            final_verdict = "Uncertain"
            final_reasoning = f"{judge_result.reasoning} (신뢰도 {confidence.total_score:.1f}/10 - 애매함)"
        else:
            final_verdict = "True"
            final_reasoning = f"{judge_result.reasoning} (신뢰도 {confidence.total_score:.1f}/10 - 높음)"
        
        # 5) 응답 생성
        return FactCheckResponse(
            claim=claim,
            verdict=final_verdict,
            confidence_score=round(confidence.total_score, 2),
            confidence_level=confidence_level,
            reasoning=final_reasoning,
            evidences=[
                EvidenceResponse(
                    text=ev.text,
                    source=ev.source,
                    date=ev.date,
                    relevance=round(ev.final_score, 2)
                )
                for ev in evidences
            ],
            score_breakdown=confidence.breakdown
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"팩트체크 실패: {str(e)}")


@app.post("/factcheck/batch")
async def batch_factcheck(request: BatchFactCheckRequest):
    """
    배치 팩트체크 (여러 주장 한번에)
    
    Args:
        request: 배치 요청 (claims 리스트)
    
    Returns:
        팩트체크 결과 리스트
    """
    # 지연 초기화 (첫 요청 시 초기화)
    if not searcher or not judge or not scorer:
        try:
            initialize_system()
        except Exception as e:
            raise HTTPException(
                status_code=503, 
                detail=f"시스템 초기화 실패: {str(e)}"
            )
    
    try:
        results = []
        
        for claim in request.claims:
            try:
                # 단일 팩트체크 재사용
                result = await factcheck(FactCheckRequest(
                    claim=claim,
                    max_results=request.max_results
                ))
                results.append(result)
            except Exception as e:
                # 개별 실패는 에러 포함해서 계속 진행
                results.append({
                    "claim": claim,
                    "error": str(e)
                })
        
        return {"results": results, "total": len(results)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 팩트체크 실패: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

