from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict


class Summarizer:
    def __init__(self, base_dir: Path):
        data_root = base_dir if Path(base_dir).name == "data" else Path(base_dir) / "data"
        self.summaries_dir = Path(data_root) / "summaries"
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

    def extract_summary(self, text: str, max_sentences: int = 5) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+|\n+|\r+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        sentences.sort(key=len, reverse=True)
        return sentences[:max_sentences]

    def extract_keywords_from_summary(self, summary: List[str]) -> List[str]:
        summary_text = " ".join(summary)
        words = re.findall(r"[가-힣]{2,}", summary_text)
        wc: Dict[str, int] = {}
        for w in words:
            wc[w] = wc.get(w, 0) + 1
        keywords = sorted(wc.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in keywords[:10]]

    def build_structured_summary(self, text: str) -> Dict[str, str]:
        sentences = re.split(r"(?<=[.!?])\s+|\n+|\r+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        cands = sorted(sentences, key=len, reverse=True)[:12]

        def pick(buf: List[str]) -> str:
            return buf.pop(0) if buf else ""

        buf = cands.copy()
        structured = {
            "overview": pick(buf),
            "sayings": pick(buf),
            "context": pick(buf),
            "result": pick(buf),
        }
        return structured

    def save_summary(self, video_id: str, summary: List[str]) -> Path:
        fpath = self.summaries_dir / f"{video_id}_summary.txt"
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"YouTube 영상 요약: {video_id}\n")
            f.write("=" * 50 + "\n\n")
            for i, s in enumerate(summary, 1):
                f.write(f"{i}. {s}\n")
        return fpath

