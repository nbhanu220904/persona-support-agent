from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Any, Iterable

from pypdf import PdfReader

from .models import RetrievedChunk


def local_embedding(text: str, dimensions: int = 384) -> list[float]:
    """Deterministic signed feature-hash embedding for offline evaluation."""
    vector = [0.0] * dimensions
    tokens = re.findall(r"[a-z0-9_-]+", text.lower())
    features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
    for token in features:
        digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
        value = int.from_bytes(digest, "big")
        vector[value % dimensions] += 1.0 if value & 1 else -1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


class RAGPipeline:
    def __init__(self, data_dir: Path, db_dir: Path, embedding_client: Any | None = None, embedding_model: str = "", collection_name: str = "lumina_support") -> None:
        import chromadb

        self.data_dir, self.embedding_client, self.embedding_model = data_dir, embedding_client, embedding_model
        self.collection = chromadb.PersistentClient(path=str(db_dir)).get_or_create_collection(collection_name, metadata={"hnsw:space": "cosine"})

    def _embed(self, texts: list[str], task: str) -> list[list[float]]:
        if self.embedding_client:
            try:
                response = self.embedding_client.models.embed_content(model=self.embedding_model, contents=texts, config={"task_type": task})
                return [list(item.values) for item in response.embeddings]
            except Exception:
                pass
        return [local_embedding(text) for text in texts]

    def _documents(self) -> Iterable[tuple[str, str, str, int | None]]:
        for path in sorted(self.data_dir.iterdir()):
            if path.suffix.lower() in {".md", ".txt"}:
                text = path.read_text(encoding="utf-8")
                section = "Overview"
                for block in re.split(r"\n(?=#{1,3} )", text):
                    heading = re.match(r"#{1,3}\s+(.+)", block)
                    if heading:
                        section = heading.group(1).strip()
                    yield path.name, block.strip(), section, None
            elif path.suffix.lower() == ".pdf":
                for page_no, page in enumerate(PdfReader(path).pages, 1):
                    yield path.name, page.extract_text() or "", f"Page {page_no}", page_no

    @staticmethod
    def _chunk(text: str, size: int = 850, overlap: int = 120) -> list[str]:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return []
        chunks, start = [], 0
        while start < len(text):
            end = min(len(text), start + size)
            if end < len(text):
                boundary = max(text.rfind(". ", start, end), text.rfind("; ", start, end))
                if boundary > start + size // 2:
                    end = boundary + 1
            chunks.append(text[start:end].strip())
            if end >= len(text):
                break
            start = max(start + 1, end - overlap)
        return chunks

    def ingest(self, force: bool = False) -> int:
        if force:
            self.collection.delete(where={"kind": "support_article"})
        records: list[tuple[str, str, str, int | None]] = []
        for source, text, section, page in self._documents():
            for index, chunk in enumerate(self._chunk(text)):
                chunk_id = hashlib.sha256(f"{source}:{section}:{index}:{chunk}".encode()).hexdigest()
                records.append((chunk_id, chunk, source, page, section))
        existing = set(self.collection.get(ids=[r[0] for r in records])["ids"]) if records else set()
        fresh = [r for r in records if r[0] not in existing]
        for offset in range(0, len(fresh), 32):
            batch = fresh[offset : offset + 32]
            texts = [r[1] for r in batch]
            self.collection.add(
                ids=[r[0] for r in batch], documents=texts,
                embeddings=self._embed(texts, "RETRIEVAL_DOCUMENT"),
                metadatas=[{"source": r[2], "page": r[3] or 0, "section": r[4], "kind": "support_article"} for r in batch],
            )
        return len(fresh)

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievedChunk]:
        if self.collection.count() == 0:
            self.ingest()
        result = self.collection.query(query_embeddings=self._embed([query], "RETRIEVAL_QUERY"), n_results=min(top_k, self.collection.count()), include=["documents", "metadatas", "distances"])
        items = []
        for text, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
            items.append(RetrievedChunk(text, metadata["source"], metadata["section"], metadata["page"] or None, max(0.0, min(1.0, 1.0 - distance))))
        return items

