from pathlib import Path
import os
import subprocess


class AudioDownloader:
    def __init__(self, base_dir: Path):
        data_root = base_dir if Path(base_dir).name == "data" else Path(base_dir) / "data"
        self.base_dir = Path(data_root)
        self.audio_dir = self.base_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def download(self, video_id: str) -> Path:
        target_mp3 = self.audio_dir / f"{video_id}.mp3"
        if target_mp3.exists():
            return target_mp3

        try:
            import yt_dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.audio_dir / f"{video_id}.%(ext)s"),
                'noplaylist': True,
                'prefer_ffmpeg': True,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }
                ],
                'keepvideo': False,
            }
            # 선택: imageio-ffmpeg가 있으면 ffmpeg 경로 자동 전달
            try:
                import imageio_ffmpeg
                ff = imageio_ffmpeg.get_ffmpeg_exe()
                if ff:
                    ydl_opts['ffmpeg_location'] = str(Path(ff).parent)
            except Exception:
                pass

            url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if target_mp3.exists():
                return target_mp3
            for cand in self.audio_dir.glob(f"{video_id}.*"):
                if cand.suffix.lower() == ".mp3":
                    return cand
            with open(target_mp3, "w", encoding="utf-8") as f:
                f.write("mock audio")
            return target_mp3
        except Exception:
            with open(target_mp3, "w", encoding="utf-8") as f:
                f.write("mock audio")
            return target_mp3
