from __future__ import annotations

from pathlib import Path
import os
from typing import List

from dotenv import load_dotenv

# .env 로드 (structure/env/.env)
load_dotenv(dotenv_path=Path(__file__).parent.parent / "env" / ".env")


class CommentCollector:
    def __init__(self, base_dir: Path):
        data_root = base_dir if Path(base_dir).name == "data" else Path(base_dir) / "data"
        self.base_dir = Path(data_root)
        self.comments_dir = self.base_dir / "comments"
        self.comments_dir.mkdir(parents=True, exist_ok=True)

    def collect_comments(self, video_id: str) -> List[str]:
        api_key = os.getenv("YOUTUBE_API_KEY")
        print(f"- YouTube API 키: {'감지됨' if api_key else '없음'}")
        if not api_key:
            print("[에러] YOUTUBE_API_KEY가 설정되지 않았습니다 (structure/env/.env)")
            return []

        try:
            from googleapiclient.discovery import build
            youtube = build("youtube", "v3", developerKey=api_key)
            print("  API 연결 성공")
            all_comments = self.extract_all_comments(youtube, video_id)
            print(f"  API 수집 원본 개수: {len(all_comments)}")
            filtered = [c for c in all_comments if isinstance(c, str) and len(c.strip()) > 10]
            print(f"  필터링 후 개수: {len(filtered)}")
            self.save_comments(video_id, filtered)
            return filtered
        except Exception as e:
            print(f"[에러] YouTube API 오류: {e}")
            return []

    def extract_all_comments(self, youtube, video_id: str) -> List[str]:
        all_comments: List[str] = []
        try:
            request = youtube.commentThreads().list(part="snippet,replies", videoId=video_id, maxResults=100)
            while request is not None:
                response = request.execute()
                for item in response.get('items', []):
                    try:
                        top = item['snippet']['topLevelComment']['snippet']
                        text = top.get('textDisplay', top.get('textOriginal', ''))
                        if isinstance(text, str):
                            all_comments.append(text)
                    except Exception:
                        pass
                    for r in item.get('replies', {}).get('comments', []):
                        try:
                            rt = r.get('snippet', {}).get('textDisplay', '')
                            if isinstance(rt, str):
                                all_comments.append(rt)
                        except Exception:
                            pass
                request = youtube.commentThreads().list_next(request, response)
        except Exception:
            return []
        return all_comments

    def save_comments(self, video_id: str, comments: List[str]) -> Path:
        fpath = self.comments_dir / f"{video_id}_comments.txt"
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"YouTube 댓글: {video_id}\n")
            f.write("=" * 50 + "\n\n")
            for i, c in enumerate(comments, 1):
                f.write(f"{i}. {c}\n")
        return fpath

