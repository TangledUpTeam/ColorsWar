"""
팩트체크 엔진 통합 모듈
네이버 + DuckDuckGo 검색 → 증거 수집 → 신뢰도 평가
"""
import os
import re
import requests
from typing import List, Dict, Optional
from collections import Counter


class FactCheckEngine:
    """간소화된 팩트체크 엔진"""
    
    def __init__(self):
        self.naver_client_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    def check_claim(self, claim: str) -> Dict:
        """주장 팩트체크"""
        print(f"\n{'='*60}")
        print(f"📋 팩트체크 시작: {claim}")
        print(f"{'='*60}\n")
        
        # 1. 키워드 추출
        keywords = self._extract_keywords(claim)
        print(f"🔍 키워드: {', '.join(keywords)}")
        
        # 2. 뉴스 검색
        print("\n📰 뉴스 검색 중...")
        articles = self._search_news(keywords)
        print(f"✓ 수집된 기사: {len(articles)}개")
        
        # 3. 증거 분석
        print("\n🔬 증거 분석 중...")
        evidences = self._analyze_evidences(claim, articles)
        print(f"✓ 관련 증거: {len(evidences)}개")
        
        # 4. 신뢰도 평가
        print("\n⭐ 신뢰도 평가 중...")
        confidence_score, verdict = self._calculate_confidence(evidences)
        
        result = {
            "claim": claim,
            "verdict": verdict,
            "confidence_score": confidence_score,
            "evidences": evidences[:5],  # 상위 5개
            "total_sources": len(articles)
        }
        
        print(f"\n{'='*60}")
        print(f"판정: {verdict}")
        print(f"신뢰도: {confidence_score:.1f}/10")
        print(f"{'='*60}\n")
        
        return result
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 한글 명사 추출 (간단 버전)
        words = re.findall(r'[가-힣]{2,}', text)
        
        # 불용어 제거
        stopwords = ['이다', '있다', '하다', '되다', '그것', '저것', '것이', '같은', '대한', '위한']
        words = [w for w in words if w not in stopwords and len(w) >= 2]
        
        # 빈도 기반 상위 키워드
        word_counts = Counter(words)
        keywords = [word for word, _ in word_counts.most_common(5)]
        
        return keywords if keywords else [text[:20]]
    
    def _search_news(self, keywords: List[str]) -> List[Dict]:
        """뉴스 검색 (네이버 + DuckDuckGo)"""
        articles = []
        
        # 네이버 뉴스 검색
        if self.naver_client_id and self.naver_client_secret:
            articles.extend(self._search_naver(keywords))
        
        # DuckDuckGo 검색 (폴백)
        if len(articles) < 5:
            articles.extend(self._search_duckduckgo(keywords))
        
        return articles
    
    def _search_naver(self, keywords: List[str]) -> List[Dict]:
        """네이버 뉴스 검색"""
        query = ' '.join(keywords)
        url = "https://openapi.naver.com/v1/search/news.json"
        
        headers = {
            "X-Naver-Client-Id": self.naver_client_id,
            "X-Naver-Client-Secret": self.naver_client_secret
        }
        
        params = {
            "query": query,
            "display": 10,
            "sort": "date"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for item in data.get('items', []):
                    # HTML 태그 제거
                    title = re.sub(r'<[^>]+>', '', item.get('title', ''))
                    description = re.sub(r'<[^>]+>', '', item.get('description', ''))
                    
                    articles.append({
                        'title': title,
                        'content': description,
                        'source': '네이버 뉴스',
                        'date': item.get('pubDate', ''),
                        'url': item.get('link', '')
                    })
                
                return articles
        except Exception as e:
            print(f"⚠ 네이버 검색 실패: {e}")
        
        return []
    
    def _search_duckduckgo(self, keywords: List[str]) -> List[Dict]:
        """DuckDuckGo 검색 (폴백)"""
        try:
            from duckduckgo_search import DDGS
            
            query = ' '.join(keywords) + ' 뉴스'
            articles = []
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))
                
                for result in results:
                    articles.append({
                        'title': result.get('title', ''),
                        'content': result.get('body', ''),
                        'source': 'DuckDuckGo',
                        'date': '',
                        'url': result.get('href', '')
                    })
            
            return articles
        except Exception as e:
            print(f"⚠ DuckDuckGo 검색 실패: {e}")
        
        return []
    
    def _analyze_evidences(self, claim: str, articles: List[Dict]) -> List[Dict]:
        """증거 분석"""
        evidences = []
        
        # 주장과 기사 내용 비교
        claim_words = set(re.findall(r'[가-힣]{2,}', claim))
        
        for article in articles:
            content = article['title'] + ' ' + article['content']
            content_words = set(re.findall(r'[가-힣]{2,}', content))
            
            # 단어 교집합 기반 관련도 계산
            intersection = claim_words & content_words
            union = claim_words | content_words
            
            if union:
                relevance = len(intersection) / len(union)
            else:
                relevance = 0.0
            
            if relevance > 0.1:  # 최소 관련도
                evidences.append({
                    'title': article['title'],
                    'content': article['content'][:200],
                    'source': article['source'],
                    'date': article['date'],
                    'url': article['url'],
                    'relevance': round(relevance, 2)
                })
        
        # 관련도 순 정렬
        evidences.sort(key=lambda x: x['relevance'], reverse=True)
        
        return evidences
    
    def _calculate_confidence(self, evidences: List[Dict]) -> tuple[float, str]:
        """신뢰도 계산"""
        if not evidences:
            return 3.0, "Uncertain"
        
        # 기본 점수
        base_score = 5.0
        
        # 증거 개수 보너스 (최대 +2점)
        evidence_bonus = min(len(evidences) * 0.5, 2.0)
        
        # 관련도 평균 보너스 (최대 +2점)
        avg_relevance = sum(e['relevance'] for e in evidences) / len(evidences)
        relevance_bonus = avg_relevance * 2.0
        
        # 출처 다양성 보너스 (최대 +1점)
        unique_sources = len(set(e['source'] for e in evidences))
        source_bonus = min(unique_sources * 0.3, 1.0)
        
        # 최종 점수 (10점 만점)
        confidence_score = min(base_score + evidence_bonus + relevance_bonus + source_bonus, 10.0)
        
        # 판정
        if confidence_score >= 7.0:
            verdict = "True"
        elif confidence_score >= 5.5:
            verdict = "Uncertain"
        else:
            verdict = "False"
        
        return confidence_score, verdict

