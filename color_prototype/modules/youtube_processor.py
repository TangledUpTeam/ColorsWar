"""
YouTube 파이프라인 통합 모듈
오디오 추출 → 전사 → 요약 → 댓글 수집 → 분석
"""
from pathlib import Path
from typing import List, Dict
import os
import re
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class YouTubeProcessor:
    """YouTube 전체 파이프라인 처리"""
    
    def __init__(self, base_dir: Path = None):
        if base_dir is None:
            self.base_dir = Path.cwd() / "color_prototype" / "data"
        else:
            self.base_dir = Path(base_dir)
        
        self.audio_dir = self.base_dir / "audio"
        self.scripts_dir = self.base_dir / "scripts"
        self.summaries_dir = self.base_dir / "summaries"
        self.comments_dir = self.base_dir / "comments"
        
        # 디렉토리 생성
        for d in [self.audio_dir, self.scripts_dir, self.summaries_dir, self.comments_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def extract_video_id(self, url_or_id: str) -> str:
        """YouTube URL에서 비디오 ID 추출"""
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
            return url_or_id
        
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url_or_id)
        if parsed.netloc:
            query = parse_qs(parsed.query)
            return query.get("v", [""])[0]
        return ""
    
    def download_audio(self, video_id: str) -> Path:
        """오디오 다운로드"""
        audio_path = self.audio_dir / f"{video_id}.mp3"
        if audio_path.exists():
            print(f"✓ 오디오 파일 존재: {audio_path}")
            return audio_path
        
        try:
            import yt_dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(audio_path.with_suffix('.%(ext)s')),
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            
            webm_path = audio_path.with_suffix('.webm')
            if webm_path.exists():
                webm_path.rename(audio_path)
            
            print(f"✓ 오디오 다운로드 완료: {audio_path}")
            return audio_path
        except Exception as e:
            print(f"⚠ 오디오 다운로드 실패: {e}")
            # Mock 파일 생성
            with open(audio_path, "w", encoding="utf-8") as f:
                f.write("mock audio")
            return audio_path
    
    def transcribe_audio(self, audio_path: Path) -> tuple[Path, str]:
        """음성 전사"""
        video_id = audio_path.stem
        script_path = self.scripts_dir / f"{video_id}.txt"
        
        if script_path.exists():
            with open(script_path, "r", encoding="utf-8") as f:
                text = f.read()
            print(f"✓ 전사 파일 존재: {script_path}")
            return script_path, text
        
        try:
            import whisper
            print("⏳ Whisper 모델 로딩 중...")
            model = whisper.load_model("base")
            print("⏳ 음성 전사 중...")
            result = model.transcribe(str(audio_path), language="ko")
            text = result["text"]
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            print(f"✓ 전사 완료: {len(text)} 문자")
            return script_path, text
        except Exception as e:
            print(f"⚠ 전사 실패: {e}")
            # Mock 텍스트 생성
            text = "정치 이슈에 대한 토론입니다. 현재 정부의 정책에 대해 다양한 의견이 있습니다."
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(text)
            return script_path, text
    
    def summarize_text(self, text: str, video_id: str) -> tuple[List[str], List[str]]:
        """텍스트 요약 및 키워드 추출"""
        # 간단한 요약: 긴 문장 우선 추출
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if len(s.strip()) > 20]
        sentences.sort(key=len, reverse=True)
        summary_sentences = sentences[:5]
        
        # 키워드 추출
        from collections import Counter
        words = re.findall(r'[가-힣]{2,}', text)
        word_counts = Counter(words)
        keywords = [word for word, _ in word_counts.most_common(10)]
        
        # 저장
        summary_path = self.summaries_dir / f"{video_id}_summary.txt"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("=== 요약 ===\n")
            for i, sent in enumerate(summary_sentences, 1):
                f.write(f"{i}. {sent}\n")
            f.write("\n=== 키워드 ===\n")
            f.write(", ".join(keywords))
        
        print(f"✓ 요약 완료: {len(summary_sentences)}개 문장, {len(keywords)}개 키워드")
        return summary_sentences, keywords
    
    def collect_comments(self, video_id: str) -> List[str]:
        """YouTube 댓글 수집"""
        api_key = os.getenv('YOUTUBE_DATA_API_KEY')
        
        if not api_key:
            print("⚠ YouTube API 키가 설정되지 않았습니다")
            # Mock 댓글 반환
            return [
                "정부 정책이 서민을 위한 것이 아니다. 복지 확대가 필요하다.",
                "시장 경제가 답이다. 규제를 완화해야 경제가 산다.",
                "노동자 권리를 보호해야 한다. 최저임금을 올려야 한다.",
                "안보가 최우선이다. 국방력을 강화해야 한다.",
                "환경 보호가 중요하다. 재생에너지로 전환해야 한다.",
            ]
        
        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            all_comments = []
            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=100
            )
            
            while request is not None:
                response = request.execute()
                for item in response.get('items', []):
                    try:
                        top = item['snippet']['topLevelComment']['snippet']
                        text = top.get('textDisplay', top.get('textOriginal', ''))
                        if isinstance(text, str) and len(text) > 10:
                            all_comments.append(text)
                    except:
                        pass
                    
                    for reply in item.get('replies', {}).get('comments', []):
                        try:
                            rt = reply.get('snippet', {}).get('textDisplay', '')
                            if isinstance(rt, str) and len(rt) > 10:
                                all_comments.append(rt)
                        except:
                            pass
                
                request = youtube.commentThreads().list_next(request, response)
            
            # 저장
            comments_path = self.comments_dir / f"{video_id}_comments.txt"
            with open(comments_path, "w", encoding="utf-8") as f:
                f.write(f"YouTube 댓글: {video_id}\n")
                f.write("=" * 50 + "\n\n")
                for i, c in enumerate(all_comments, 1):
                    f.write(f"{i}. {c}\n")
            
            print(f"✓ 댓글 수집 완료: {len(all_comments)}개")
            return all_comments
        
        except Exception as e:
            print(f"⚠ 댓글 수집 실패: {e}")
            return []
    
    def run_pipeline(self, youtube_url: str) -> Dict:
        """전체 파이프라인 실행"""
        print(f"\n{'='*60}")
        print(f"YouTube 파이프라인 시작: {youtube_url}")
        print(f"{'='*60}\n")
        
        # 1. 비디오 ID 추출
        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            return {"error": "유효하지 않은 YouTube URL"}
        
        print(f"📹 비디오 ID: {video_id}\n")
        
        # 2. 오디오 다운로드
        print("🎵 [1/5] 오디오 다운로드...")
        audio_path = self.download_audio(video_id)
        
        # 3. 음성 전사
        print("\n🎤 [2/5] 음성 전사...")
        script_path, text = self.transcribe_audio(audio_path)
        
        # 4. 요약 생성
        print("\n📝 [3/5] 요약 생성...")
        summary_sentences, keywords = self.summarize_text(text, video_id)
        
        # 5. 댓글 수집
        print("\n💬 [4/5] 댓글 수집...")
        comments = self.collect_comments(video_id)
        
        print(f"\n{'='*60}")
        print("YouTube 파이프라인 완료!")
        print(f"{'='*60}\n")
        
        return {
            "video_id": video_id,
            "audio_path": str(audio_path),
            "script_path": str(script_path),
            "text": text,
            "summary": summary_sentences,
            "keywords": keywords,
            "comments": comments
        }

