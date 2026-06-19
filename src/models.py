from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Persona(StrEnum):
    TECHNICAL = "Technical Expert"
    FRUSTRATED = "Frustrated User"
    EXECUTIVE = "Business Executive"


@dataclass(slots=True)
class PersonaResult:
    persona: Persona
    confidence: float
    reasoning: str
    sentiment: str = "neutral"


@dataclass(slots=True)
class RetrievedChunk:
    text: str
    source: str
    section: str
    page: int | None
    score: float

    @property
    def citation(self) -> str:
        location = f"page {self.page}" if self.page else self.section
        return f"{self.source} - {location}"


@dataclass(slots=True)
class ChatTurn:
    role: str
    content: str
    persona: str | None = None


@dataclass(slots=True)
class EscalationDecision:
    escalated: bool
    reasons: list[str] = field(default_factory=list)
    priority: str = "normal"


@dataclass(slots=True)
class SupportResult:
    response: str
    persona: PersonaResult
    sources: list[RetrievedChunk]
    escalation: EscalationDecision
    handoff: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

