from pathlib import Path

from src.rag_pipeline import RAGPipeline, local_embedding


def test_local_embedding_is_deterministic_and_normalized():
    first = local_embedding("bearer token authentication")
    assert first == local_embedding("bearer token authentication")
    assert abs(sum(x * x for x in first) - 1) < 1e-8


def test_ingestion_and_metadata(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "auth.md").write_text("# Authentication\nUse a bearer token in the Authorization header.", encoding="utf-8")
    rag = RAGPipeline(data, tmp_path / "db", collection_name="test")
    assert rag.ingest() == 1
    results = rag.retrieve("Authorization bearer token", 1)
    assert results[0].source == "auth.md"
    assert results[0].section == "Authentication"
    assert results[0].score > 0

