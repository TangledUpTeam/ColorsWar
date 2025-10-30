from typing import List, Dict, Any
from pathlib import Path

class Analyzer:
    def __init__(self, reclassifier):
        # reclassifier must implement batch_reclassify(list[dict]) -> list[dict]
        self.reclassifier = reclassifier

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        s1 = set(text1.lower().split())
        s2 = set(text2.lower().split())
        if not s1 and not s2: return 0.0
        inter = len(s1 & s2)
        union = len(s1 | s2) or 1
        return inter / union

    def filter_comments_by_similarity(self, comments: List[str], summary_sentences: List[str], max_comments: int = 500) -> List[Dict]:
        summary_text = " ".join(summary_sentences)
        objs = []
        for i, text in enumerate(comments):
            sim = self.calculate_similarity(text, summary_text)
            objs.append({
                'id': f'yt_{i}',
                'text': text,
                'similarity_score': sim,
                'author': f'사용자{i+1}'
            })
        objs.sort(key=lambda x: x['similarity_score'], reverse=True)
        return objs[:max_comments]

    def analyze_comments(self, comments: List[str], summary_sentences: List[str]) -> Dict[str, Any]:
        filtered = self.filter_comments_by_similarity(comments, summary_sentences, max_comments=500)
        if not filtered:
            return {'comments': [], 'statistics': {}, 'left_comments': [], 'right_comments': [], 'similarity_stats': {}}

        for c in filtered:
            words = c['text'].split()
            c['keywords'] = [w for w in words if len(w) > 2][:5]
            text = c['text']
            if any(kw in text for kw in ['복지','평등','노동','환경','인권','재분배','진보','서민']):
                c['political_orientation'] = '좌파'; c['classification_confidence'] = 0.7
            elif any(kw in text for kw in ['시장','안보','전통','규제완화','보수','자유경제','기업']):
                c['political_orientation'] = '우파'; c['classification_confidence'] = 0.7
            else:
                c['political_orientation'] = '판단불가'; c['classification_confidence'] = 0.5
            c['classification_reasoning'] = '키워드 기반 분류'

        reclassified = self.reclassifier.batch_reclassify(filtered)

        stats = {'좌파':0,'우파':0,'중도':0,'판단불가':0}
        for c in reclassified:
            stats[c.get('political_orientation','판단불가')] = stats.get(c.get('political_orientation','판단불가'),0)+1
        total = len(reclassified) or 1
        final_stats = {k: {'count': v, 'percentage': round(v/total*100,1)} for k,v in stats.items()}

        sims = [c.get('similarity_score',0) for c in reclassified]
        sim_stats = {'average': sum(sims)/len(sims) if sims else 0, 'max': max(sims) if sims else 0, 'min': min(sims) if sims else 0}

        return {
            'comments': reclassified,
            'statistics': final_stats,
            'left_comments': [c['text'] for c in reclassified if c.get('political_orientation')=='좌파'],
            'right_comments': [c['text'] for c in reclassified if c.get('political_orientation')=='우파'],
            'similarity_stats': sim_stats
        }