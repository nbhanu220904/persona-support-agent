from __future__ import annotations

import json
import re
from typing import Any

from .models import Persona, PersonaResult

TECH = {"api", "sdk", "http", "oauth", "token", "header", "logs", "stack", "database", "webhook", "401", "403", "500", "latency", "configuration", "endpoint"}
FRUSTRATED = {"frustrated", "angry", "ridiculous", "nothing works", "again", "urgent", "immediately", "terrible", "unacceptable", "fed up", "demand"}
EXEC = {"impact", "operations", "revenue", "roi", "timeline", "sla", "executive", "business", "customers", "downtime", "risk", "forecast"}


class PersonaClassifier:
    def __init__(self, client: Any | None = None, model: str = "") -> None:
        self.client, self.model = client, model

    def classify(self, message: str) -> PersonaResult:
        message = message.strip()
        if not message:
            raise ValueError("Message cannot be empty")
        if self.client:
            try:
                return self._classify_llm(message)
            except Exception:
                pass
        return self._classify_rules(message)

    def _classify_rules(self, message: str) -> PersonaResult:
        lower = message.lower()
        scores = {
            Persona.TECHNICAL: sum(term in lower for term in TECH),
            Persona.FRUSTRATED: sum(term in lower for term in FRUSTRATED) + min(message.count("!"), 2),
            Persona.EXECUTIVE: sum(term in lower for term in EXEC),
        }
        persona = max(scores, key=scores.get)
        if not scores[persona]:
            persona = Persona.FRUSTRATED if any(x in lower for x in ("can't", "cannot", "problem", "issue")) else Persona.EXECUTIVE
        total = max(1, sum(scores.values()))
        confidence = min(0.96, 0.58 + (scores[persona] / total) * 0.32)
        sentiment = "negative" if scores[Persona.FRUSTRATED] else "neutral"
        clues = [t for t in (TECH | FRUSTRATED | EXEC) if t in lower][:3]
        reasoning = "Matched communication signals" + (f": {', '.join(clues)}" if clues else " and intent")
        return PersonaResult(persona, confidence, reasoning, sentiment)

    def _classify_llm(self, message: str) -> PersonaResult:
        from google.genai import types

        prompt = """Classify this support message into exactly one persona. Technical Expert uses APIs, logs, configs and wants detail. Frustrated User uses emotional or urgent language. Business Executive focuses on impact, risk, outcomes and timelines. Return strict JSON with persona, confidence (0-1), reasoning, and sentiment."""
        schema = {
            "type": "OBJECT",
            "properties": {
                "persona": {"type": "STRING", "enum": [p.value for p in Persona]},
                "confidence": {"type": "NUMBER"},
                "reasoning": {"type": "STRING"},
                "sentiment": {"type": "STRING"},
            },
            "required": ["persona", "confidence", "reasoning", "sentiment"],
        }
        result = self.client.models.generate_content(
            model=self.model,
            contents=message,
            config=types.GenerateContentConfig(system_instruction=prompt, response_mime_type="application/json", response_schema=schema, temperature=0.0),
        )
        data = json.loads(re.sub(r"^```json|```$", "", result.text.strip()))
        return PersonaResult(Persona(data["persona"]), float(data["confidence"]), data["reasoning"], data["sentiment"])

