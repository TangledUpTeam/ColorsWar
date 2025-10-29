"""
말투/감정 학습 모듈 (MAE - Manner And Emotion)
댓글에서 말투 패턴과 감정을 추출하여 페르소나 학습에 활용
"""
import re
from typing import List, Dict, Tuple
from collections import Counter


class MannerAndEmotionAnalyzer:
    """말투와 감정 분석 클래스"""
    
    def __init__(self):
        # 공격적/비판적 표현 패턴
        self.aggressive_patterns = [
            r'[ㅋㅎ]{3,}',  # 비웃음
            r'ㅉㅉ',  # 혀 차는 소리
            r'에휴',  # 한숨
            r'[ㅅㅆ]발',  # 욕설
            r'[ㅂㅃ]신',  # 욕설
            r'[ㅈㅉ]까',  # 욕설
            r'개새',  # 욕설
            r'년아',  # 욕설
            r'놈',  # 비하
            r'따위',  # 비하
            r'애미',  # 욕설
            r'아빠',  # 비하적 맥락
        ]
        
        # 감정 키워드
        self.emotion_keywords = {
            '분노': ['화난다', '짜증', '열받', '빡친', '미친', '돌았', '또라이', '미쳤'],
            '냉소': ['ㅋㅋ', 'ㅎㅎ', 'ㅉㅉ', '웃기', '코미디', '쇼', '개그', '허구헌날'],
            '비판': ['문제', '잘못', '틀렸', '엉망', '개판', '최악', '실패', '무능', '한심'],
            '경멸': ['수준', '교육', '정신', '머리', '뇌', '따위', '놈', '년', '것'],
            '불신': ['믿을', '거짓', '사기', '조작', '속임', '꼼수', '뻔한', '당연'],
            '비아냥': ['그래봐야', '어차피', '어쩔', '뭐가', '무슨', '참나', '기가'],
        }
        
        # 말투 특징
        self.manner_patterns = {
            '반말': [r'이야\s*$', r'네\s*$', r'야\s*$', r'임\s*$', r'거든\s*$'],
            '명령형': [r'해라', r'하라', r'하세요', r'하십시오', r'해봐'],
            '의문공격': [r'뭐가\s+\S+', r'어떻게\s+\S+', r'왜\s+\S+', r'\S+냐\?', r'\S+니\?'],
            '극단적': ['완전', '진짜', '너무', '존나', '개', '극혐', '레전드', '실화'],
            '비교': ['보다', '보단', '~에 비해', '에 비하면', '차라리', '만도 못'],
        }
        
        # 좌파 특유 표현
        self.left_expressions = [
            '서민', '노동자', '을들', '88만원', '헬조선', '금수저', '흙수저', 
            '재벌', '대기업', '착취', '불평등', '양극화', '민생', '복지',
            '인권', '평등', '공정', '정의', '개혁', '적폐', '구시대'
        ]
        
        # 우파 특유 표현
        self.right_expressions = [
            '빨갱이', '종북', '좌빨', '반일', '친중', '문빠', '운동권',
            '안보', '국방', '자유', '시장', '기업', '성장', '법치', 
            '질서', '전통', '국가', '애국', '태극기', '보수'
        ]
    
    def analyze_comment(self, text: str, orientation: str = None) -> Dict:
        """단일 댓글 분석"""
        result = {
            'text': text,
            'orientation': orientation,
            'aggression_score': 0.0,
            'emotion_scores': {},
            'manner_features': [],
            'profanity_count': 0,
            'length': len(text),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
        }
        
        # 공격성 점수 계산
        aggression_count = 0
        for pattern in self.aggressive_patterns:
            aggression_count += len(re.findall(pattern, text))
        result['aggression_score'] = min(aggression_count / 5.0, 1.0)
        result['profanity_count'] = aggression_count
        
        # 감정 분석
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                result['emotion_scores'][emotion] = score
        
        # 말투 특징 추출
        for manner, patterns in self.manner_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    result['manner_features'].append(manner)
                    break
        
        # 성향별 특유 표현 확인
        if orientation == '좌파':
            result['ideology_expressions'] = [expr for expr in self.left_expressions if expr in text]
        elif orientation == '우파':
            result['ideology_expressions'] = [expr for expr in self.right_expressions if expr in text]
        else:
            result['ideology_expressions'] = []
        
        return result
    
    def analyze_batch(self, comments: List[Dict]) -> Dict:
        """여러 댓글 일괄 분석"""
        results = {
            'left': {'comments': [], 'summary': {}},
            'right': {'comments': [], 'summary': {}},
        }
        
        for comment in comments:
            text = comment.get('text', '')
            orientation = comment.get('political_orientation', '판단불가')
            
            if orientation not in ['좌파', '우파']:
                continue
            
            analysis = self.analyze_comment(text, orientation)
            
            side = 'left' if orientation == '좌파' else 'right'
            results[side]['comments'].append(analysis)
        
        # 각 진영별 요약 통계
        for side in ['left', 'right']:
            comments_data = results[side]['comments']
            if not comments_data:
                continue
            
            # 평균 공격성
            avg_aggression = sum(c['aggression_score'] for c in comments_data) / len(comments_data)
            
            # 가장 많이 사용된 감정
            all_emotions = []
            for c in comments_data:
                all_emotions.extend(c['emotion_scores'].keys())
            emotion_counter = Counter(all_emotions)
            
            # 가장 많이 사용된 말투
            all_manners = []
            for c in comments_data:
                all_manners.extend(c['manner_features'])
            manner_counter = Counter(all_manners)
            
            # 특유 표현 수집
            all_ideology_expr = []
            for c in comments_data:
                all_ideology_expr.extend(c.get('ideology_expressions', []))
            ideology_counter = Counter(all_ideology_expr)
            
            results[side]['summary'] = {
                'total_comments': len(comments_data),
                'avg_aggression': avg_aggression,
                'avg_length': sum(c['length'] for c in comments_data) / len(comments_data),
                'total_profanity': sum(c['profanity_count'] for c in comments_data),
                'top_emotions': emotion_counter.most_common(3),
                'top_manners': manner_counter.most_common(3),
                'top_ideology_expressions': ideology_counter.most_common(5),
            }
        
        return results
    
    def extract_training_data(self, analysis_result: Dict, side: str) -> Dict:
        """학습용 데이터 추출"""
        if side not in ['left', 'right']:
            raise ValueError("side must be 'left' or 'right'")
        
        side_data = analysis_result[side]
        summary = side_data['summary']
        
        # 공격적이고 특징적인 댓글 선별
        comments = side_data['comments']
        
        # 공격성 점수가 높은 상위 댓글
        aggressive_comments = sorted(
            comments, 
            key=lambda x: x['aggression_score'], 
            reverse=True
        )[:30]
        
        # 감정 표현이 풍부한 댓글
        emotional_comments = sorted(
            comments,
            key=lambda x: len(x['emotion_scores']),
            reverse=True
        )[:30]
        
        # 특유 표현이 많은 댓글
        ideological_comments = sorted(
            comments,
            key=lambda x: len(x.get('ideology_expressions', [])),
            reverse=True
        )[:30]
        
        # 중복 제거하면서 합치기
        selected_texts = set()
        for comment_list in [aggressive_comments, emotional_comments, ideological_comments]:
            for c in comment_list:
                selected_texts.add(c['text'])
        
        return {
            'orientation': '좌파' if side == 'left' else '우파',
            'training_texts': list(selected_texts),
            'style_summary': {
                'aggression_level': summary['avg_aggression'],
                'profanity_usage': summary['total_profanity'] / summary['total_comments'],
                'preferred_emotions': [e[0] for e in summary['top_emotions']],
                'preferred_manners': [m[0] for m in summary['top_manners']],
                'key_expressions': [e[0] for e in summary['top_ideology_expressions']],
            }
        }


def main():
    """테스트용 메인 함수"""
    # 테스트 댓글
    test_comments = [
        {
            'text': '이게 나라냐 진짜 ㅋㅋㅋ 서민은 죽으라는 거임? 재벌만 배불리는 썩은 나라',
            'political_orientation': '좌파'
        },
        {
            'text': '복지 확대 해야죠. 노동자들 권리 좀 지켜줘야 한다고 봅니다.',
            'political_orientation': '좌파'
        },
        {
            'text': '종북 좌빨들 때문에 나라 망한다 ㅉㅉ 안보가 먼저야',
            'political_orientation': '우파'
        },
        {
            'text': '자유시장 경제가 답이다. 규제 완화로 기업 살려야 함',
            'political_orientation': '우파'
        },
    ]
    
    analyzer = MannerAndEmotionAnalyzer()
    
    # 일괄 분석
    results = analyzer.analyze_batch(test_comments)
    
    # 결과 출력
    print("=" * 60)
    print("말투/감정 분석 결과")
    print("=" * 60)
    
    for side in ['left', 'right']:
        side_name = '좌파' if side == 'left' else '우파'
        print(f"\n[{side_name}]")
        summary = results[side]['summary']
        
        if not summary:
            print("  데이터 없음")
            continue
        
        print(f"  총 댓글: {summary['total_comments']}개")
        print(f"  평균 공격성: {summary['avg_aggression']:.2f}")
        print(f"  욕설 사용: {summary['total_profanity']}회")
        print(f"  주요 감정: {summary['top_emotions']}")
        print(f"  주요 말투: {summary['top_manners']}")
        print(f"  특유 표현: {summary['top_ideology_expressions']}")
        
        # 학습 데이터 추출
        training_data = analyzer.extract_training_data(results, side)
        print(f"\n  학습용 텍스트: {len(training_data['training_texts'])}개")
        print(f"  스타일 특징: {training_data['style_summary']}")


if __name__ == "__main__":
    main()

