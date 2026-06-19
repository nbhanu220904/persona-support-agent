from __future__ import annotations

from typing import Any

from .classifier import PersonaClassifier
from .config import Settings
from .escalator import Escalator
from .generator import ResponseGenerator
from .models import ChatTurn, SupportResult
from .rag_pipeline import RAGPipeline


class SupportService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.settings.validate()
        client: Any | None = None
        if self.settings.gemini_api_key:
            from google import genai
            client = genai.Client(api_key=self.settings.gemini_api_key)
        self.classifier = PersonaClassifier(client, self.settings.gemini_model)
        self.rag = RAGPipeline(self.settings.data_dir, self.settings.db_dir, client, self.settings.embedding_model)
        self.generator = ResponseGenerator(client, self.settings.gemini_model)
        self.escalator = Escalator(self.settings.retrieval_threshold, self.settings.frustration_turn_threshold)

    @property
    def mode(self) -> str:
        return "Gemini" if self.settings.gemini_api_key else "Local evaluation"

    def ingest(self, force: bool = False) -> int:
        return self.rag.ingest(force)

    def respond(self, message: str, history: list[ChatTurn] | None = None) -> SupportResult:
        clean = message.strip()
        if not clean:
            raise ValueError("Please enter a support question.")
        if len(clean) > 4000:
            raise ValueError("Message must be 4,000 characters or fewer.")
        history = (history or [])[-self.settings.max_history_turns :]
        persona = self.classifier.classify(clean)
        sources = self.rag.retrieve(clean, self.settings.top_k)
        decision = self.escalator.decide(clean, persona, sources, history)
        response = self.generator.generate(clean, persona.persona, sources, decision.escalated)
        handoff = self.escalator.handoff(clean, persona, sources, history, decision) if decision.escalated else None
        return SupportResult(response, persona, sources, decision, handoff)

