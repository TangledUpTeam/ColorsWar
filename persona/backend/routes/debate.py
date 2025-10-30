"""
채팅 시뮬레이션 API 라우터
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from models import DebateStatusResponse, DebateMessageResponse, Side
from services import DebateService
from core.state import get_app_state

router = APIRouter(prefix="/api/debate", tags=["debate"])


@router.post("/start")
async def start_debate():
    """생성된 페르소나를 기반으로 채팅 세션 시작"""
    try:
        service = DebateService(get_app_state())
        result = service.start_debate()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/next", response_model=DebateMessageResponse)
async def next_message(side: Optional[Side] = None):
    """다음 채팅 생성 (좌/우 번갈아)"""
    try:
        service = DebateService(get_app_state())
        result = service.generate_next_message(side)
        return DebateMessageResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=DebateStatusResponse)
async def debate_status():
    """현재 채팅 상태 조회"""
    try:
        service = DebateService(get_app_state())
        result = service.get_debate_status()
        return DebateStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reset")
async def reset_debate():
    """채팅 세션 초기화"""
    service = DebateService(get_app_state())
    return service.reset_debate()

