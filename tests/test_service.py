from dataclasses import replace
from pathlib import Path

from src.config import Settings
from src.models import Persona
from src.service import SupportService


def make_service(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "auth.md").write_text("# API auth\nA 401 means a missing or expired bearer token. Check the Authorization header and token expiry.", encoding="utf-8")
    settings = replace(Settings(), data_dir=data, db_dir=tmp_path / "db", gemini_api_key="", retrieval_threshold=0.05)
    service = SupportService(settings)
    service.ingest()
    return service


def test_end_to_end_offline(tmp_path):
    result = make_service(tmp_path).respond("Our API has a 401. Show token and header diagnostics.")
    assert result.persona.persona == Persona.TECHNICAL
    assert result.sources
    assert "Diagnosis" in result.response


def test_message_length_validation(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        make_service(tmp_path).respond("x" * 4001)

