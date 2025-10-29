"""텍스트 처리 유틸리티"""
import re
from typing import List


def split_into_sentences(text: str) -> List[str]:
    """
    문서를 문장 단위로 분할 (스니펫 생성)
    
    Args:
        text: 분할할 텍스트
        
    Returns:
        문장 리스트
    """
    # 한국어 문장 분할 (마침표, 물음표, 느낌표 기준)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def normalize_score(scores: List[float]) -> List[float]:
    """
    점수를 0-1 범위로 정규화
    
    Args:
        scores: 정규화할 점수 리스트
        
    Returns:
        정규화된 점수 리스트
    """
    if not scores:
        return []
    
    min_score = min(scores)
    max_score = max(scores)
    
    if max_score == min_score:
        return [1.0] * len(scores)
    
    return [(s - min_score) / (max_score - min_score) for s in scores]


def clean_text(text: str) -> str:
    """
    텍스트 전처리
    
    Args:
        text: 정제할 텍스트
        
    Returns:
        정제된 텍스트
    """
    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

