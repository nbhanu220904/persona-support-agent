from __future__ import annotations

import re

from .models import ChatTurn, EscalationDecision, Persona, PersonaResult, RetrievedChunk

SENSITIVE = {"billing", "refund", "charge", "charged", "legal", "lawsuit", "attorney", "delete account", "account ownership", "bank", "card"}
ACTION_PATTERNS = [r"(?:tried|attempted|already)\s+([^.!?]+)", r"(?:cleared|reset|restarted|reinstalled)\s+([^.!?]+)"]


class Escalator:
    def __init__(self, confidence_threshold: float, frustration_turn_threshold: int) -> None:
        self.threshold, self.frustration_threshold = confidence_threshold, frustration_turn_threshold

    def decide(self, message: str, persona: PersonaResult, sources: list[RetrievedChunk], history: list[ChatTurn]) -> EscalationDecision:
        reasons: list[str] = []
        lower = message.lower()
        if not sources or sources[0].score < self.threshold:
            reasons.append("Low retrieval confidence")
        if any(term in lower for term in SENSITIVE):
            reasons.append("Sensitive billing, legal, or account issue")
        recent_frustration = sum(t.persona == Persona.FRUSTRATED.value for t in history[-6:] if t.role == "user")
        if persona.persona == Persona.FRUSTRATED and recent_frustration + 1 >= self.frustration_threshold:
            reasons.append("Repeated unresolved frustration")
        if any(phrase in lower for phrase in ("human agent", "real person", "supervisor", "escalate this")):
            reasons.append("Customer requested a human")
        priority = "urgent" if len(reasons) > 1 or any(x in lower for x in ("legal", "fraud", "production down")) else "normal"
        return EscalationDecision(bool(reasons), reasons, priority)

    @staticmethod
    def handoff(message: str, persona: PersonaResult, sources: list[RetrievedChunk], history: list[ChatTurn], decision: EscalationDecision) -> dict:
        attempts = []
        for turn in [*history, ChatTurn("user", message)]:
            if turn.role == "user":
                for pattern in ACTION_PATTERNS:
                    attempts.extend(m.group(1).strip() for m in re.finditer(pattern, turn.content, re.I))
        return {
            "persona": persona.persona.value,
            "issue_summary": message[:300],
            "conversation_history": [{"role": t.role, "content": t.content} for t in history[-10:]] + [{"role": "user", "content": message}],
            "retrieved_documents": sorted({s.citation for s in sources}),
            "actions_already_attempted": list(dict.fromkeys(attempts)) or ["No customer-attempted actions identified"],
            "escalation_reasons": decision.reasons,
            "priority": decision.priority,
            "recommended_next_steps": ["Verify customer identity before account-specific changes", "Review the cited article context and account telemetry", "Contact the customer and confirm resolution"],
        }

