from pathlib import Path
import os

# 가볍게 모듈화된 컴포넌트들을 임포트
from .audio import AudioDownloader
from .transcribe import Transcriber
from .summarizer import Summarizer
from .comments import CommentCollector
from .analyzer import Analyzer
from .saver import ResultsSaver

# 기존 외부 의존 모듈(재분류기, 페르소나)은 기존 위치에서 import 시도
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from reclassifier import ForceReclassifier  # type: ignore
except Exception:
    # fallback mock if not available
    class ForceReclassifier:
        def batch_reclassify(self, comments):
            return comments

class YouTubeFullPipeline:
    def __init__(self, base_dir: Path = None):
        # base_dir가 str로 전달될 수 있으므로 항상 Path로 변환
        if base_dir is None:
            self.base_dir = Path.cwd()
        else:
            self.base_dir = Path(base_dir)
        self.audio = AudioDownloader(self.base_dir)
        self.transcriber = Transcriber(self.base_dir)
        self.summarizer = Summarizer(self.base_dir)
        self.collector = CommentCollector(self.base_dir)
        self.analyzer = Analyzer(ForceReclassifier())
        self.saver = ResultsSaver(self.data_dir)

    def extract_video_id(self, url_or_id: str) -> str:
        import re
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
            return url_or_id
        from urllib.parse import urlparse, parse_qs
        p = urlparse(url_or_id)
        if p.netloc:
            q = parse_qs(p.query)
            return q.get("v", [""])[0]
        return ""

    def run_full_pipeline(self, youtube_url: str):
        print(f"[파이프라인 시작] URL: {youtube_url}")

        # 1) 비디오 ID
        vid = self.extract_video_id(youtube_url)
        print(f"📹 비디오 ID: {vid}")
        if not vid:
            print("❌ 유효하지 않은 비디오 ID")
            return {}
        
        # 2단계: 오디오 다운로드
        print("🎵 오디오 다운로드 중...")
        audio_path = self.audio.download(vid)
        print(f"🎵 오디오 경로: {audio_path}")
        
        # 3단계: 음성 전사
        print("🎤 음성 전사 중...")
        script_path, text = self.transcriber.transcribe(audio_path)
        print(f"📝 전사 완료, 텍스트 길이: {len(text)} 문자")
        
        # 4단계: 요약 생성
        print("📝 요약 생성 중...")
        structured = self.summarizer.build_structured_summary(text)
        summary_sentences = self.summarizer.extract_summary(text, max_sentences=5)
        self.summarizer.save_summary(vid, summary_sentences)
        keywords = self.summarizer.extract_keywords_from_summary(summary_sentences)
        print(f"📝 요약 완료, 키워드: {keywords}")
        
        # 5단계: 댓글 수집
        print("💬 댓글 수집 중...")
        comments = self.collector.collect_comments(vid)
        print(f"💬 수집된 댓글 수: {len(comments) if comments else 0}")
        if not comments:
            print("❌ 댓글을 찾을 수 없습니다")
            return {}
        
        # 6단계: 댓글 분석
        print("🔍 댓글 분석 중...")
        analysis = self.analyzer.analyze_comments(comments, summary_sentences)
        self.saver.save_leftright_comments(vid, analysis.get('comments', []))
        print(f"  통계: {analysis.get('statistics', {})}")

        # 7) 결과 저장
        debate = []  # 토론 비활성화
        self.saver.save_results(vid, structured, analysis, debate, keywords)
        print("✅ 파이프라인 완료!")
        
        return {'video_id': vid, 'summary': structured, 'analysis': analysis, 'debate': debate}

# 간단 실행용 스크립트 유지
def main():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    url = "https://www.youtube.com/watch?v=QES-uZV3-gw"
    p = YouTubeFullPipeline(Path(__file__).parent)
    res = p.run_full_pipeline(url)
    print("완료:", bool(res))

if __name__ == "__main__":
    main()