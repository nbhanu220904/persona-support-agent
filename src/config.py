from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    embedding_model: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    top_k: int = int(os.getenv("TOP_K", "4"))
    retrieval_threshold: float = float(os.getenv("RETRIEVAL_THRESHOLD", "0.28"))
    frustration_turn_threshold: int = int(os.getenv("FRUSTRATION_TURN_THRESHOLD", "2"))
    max_history_turns: int = int(os.getenv("MAX_HISTORY_TURNS", "12"))
    local_fallback: bool = _bool("ENABLE_LOCAL_FALLBACK", True)
    data_dir: Path = ROOT / "data"
    db_dir: Path = ROOT / "chroma_db"

    def validate(self) -> None:
        if not 1 <= self.top_k <= 10:
            raise ValueError("TOP_K must be between 1 and 10")
        if not 0 <= self.retrieval_threshold <= 1:
            raise ValueError("RETRIEVAL_THRESHOLD must be between 0 and 1")

