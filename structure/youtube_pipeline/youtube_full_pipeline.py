from __future__ import annotations

from pathlib import Path
import sys
import os

from .audio import AudioDownloader
from .transcribe import Transcriber
from .summarizer import Summarizer
from .comments import CommentCollector
from .analyzer import Analyzer
from .saver import ResultsSaver

# 프로젝트 루트(= structure)를 sys.path에 추가 (선택 모듈 로딩용)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from reclassifier import ForceReclassifier  # type: ignore
    from persona_service import PersonaBattleService  # type: ignore
except Exception:
    # 사용 불가 시 간단 목업
    class ForceReclassifier:
        def batch_reclassify(self, comments):
            return comments

    class PersonaBattleService:
        def initialize_personas(self, left, right):
            pass

        def start_debate(self, topic, rounds=5):
            return []


class YouTubeFullPipeline:
    def __init__(self, base_dir: Path | None = None):
        # base_dir 기준으로 structure/data를 찾아 data 루트를 고정
        anchor = Path(base_dir) if base_dir is not None else PROJECT_ROOT
        self.data_dir = self._resolve_data_dir(anchor)
        # 기존 코드 호환성을 위해 base_dir도 유지
        self.base_dir = self.data_dir

        # 각 컴포넌트는 data 루트를 기준으로 동작
        self.audio = AudioDownloader(self.data_dir)
        self.transcriber = Transcriber(self.data_dir)
        self.summarizer = Summarizer(self.data_dir)
        self.collector = CommentCollector(self.data_dir)
        self.analyzer = Analyzer(ForceReclassifier())
        self.saver = ResultsSaver(self.data_dir)
        self.battle_service = PersonaBattleService()

    def _resolve_data_dir(self, anchor: Path) -> Path:
        if anchor.name == "data":
            return anchor
        if (anchor / "data").exists():
            return anchor / "data"
        if (anchor.parent / "data").exists():
            return anchor.parent / "data"
        return anchor / "data"

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

    def run_full_pipeline(self, youtube_url: str, topic: str = "현안 정책 이슈", rounds: int = 5):
        print(f"[파이프라인 시작] URL: {youtube_url}")

        # 1) 비디오 ID
        vid = self.extract_video_id(youtube_url)
        print(f"- 비디오 ID: {vid}")
        if not vid:
            print("[에러] 유효하지 않은 URL/ID")
            return {}

        # 2) 오디오 다운로드 (yt_dlp + FFmpeg → mp3만 저장)
        print("- 오디오 다운로드 중...")
        audio_path = self.audio.download(vid)
        print(f"  저장: {audio_path}")

        # 3) 음성 → 텍스트
        print("- 음성 텍스트 변환 중...")
        script_path, text = self.transcriber.transcribe(audio_path)
        print(f"  스크립트 길이: {len(text)} 문자 -> {script_path}")

        # 4) 5줄 요약 + 키워드
        print("- 요약 생성 중...")
        structured = self.summarizer.build_structured_summary(text)
        summary_sentences = self.summarizer.extract_summary(text, max_sentences=5)
        self.summarizer.save_summary(vid, summary_sentences)
        keywords = self.summarizer.extract_keywords_from_summary(summary_sentences)
        print(f"  키워드: {keywords}")

        # 5) YouTube API로 댓글 수집 (.env 키 사용)
        print("- 댓글 수집 중(YouTube API)...")
        comments = self.collector.collect_comments(vid)
        print(f"  수집된 댓글 수: {len(comments) if comments else 0}")
        if not comments:
            print("[경고] 댓글을 찾지 못했습니다")
            return {}

        # 6) 댓글 분석/좌우 분류
        print("- 댓글 분석/좌우 분류 중...")
        analysis = self.analyzer.analyze_comments(comments, summary_sentences)
        self.saver.save_leftright_comments(vid, analysis.get('comments', []))
        print(f"  통계: {analysis.get('statistics', {})}")

        # 7) (선택) AI 토론 구성
        print("- AI 토론 구성 중...")
        if analysis.get('left_comments') and analysis.get('right_comments'):
            self.battle_service.initialize_personas(analysis['left_comments'], analysis['right_comments'])
            debate = self.battle_service.start_debate(topic, rounds=rounds)
            print(f"  토론 메시지 수: {len(debate)}")
        else:
            print("[안내] 좌/우파 댓글이 부족하여 토론을 생략합니다")
            debate = []

        # 8) 결과 저장
        self.saver.save_results(vid, structured, analysis, debate, keywords)
        print("[파이프라인 완료]")

        return {"video_id": vid, "summary": structured, "analysis": analysis, "debate": debate}


def main():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    url = "dQw4w9WgXcQ"
    p = YouTubeFullPipeline(Path(__file__).parent)
    res = p.run_full_pipeline(url)
    print("완료:", bool(res))


if __name__ == "__main__":
    main()

