from __future__ import annotations

from typing import Any

from .models import Persona, RetrievedChunk

STYLE = {
    Persona.TECHNICAL: "Act as a senior support engineer. Explain likely root cause, exact diagnostics, and numbered remediation steps. Preserve commands and identifiers from context.",
    Persona.FRUSTRATED: "Lead with one sincere sentence of empathy. Use plain language, short action steps, and reassurance. Avoid jargon.",
    Persona.EXECUTIVE: "Lead with business impact, then resolution path and documented timing. Be concise and avoid implementation detail unless essential.",
}


class ResponseGenerator:
    def __init__(self, client: Any | None = None, model: str = "") -> None:
        self.client, self.model = client, model

    def generate(self, query: str, persona: Persona, sources: list[RetrievedChunk], escalated: bool) -> str:
        if escalated:
            prefix = "I’m routing this to a human support specialist so it can be handled safely."
            if persona == Persona.FRUSTRATED:
                prefix = "I’m sorry this has been such a hassle. I’m routing it to a human specialist now so you don’t have to repeat yourself."
            return prefix + " Your conversation context, relevant sources, and attempted steps are included in the handoff."
        if self.client:
            try:
                context = "\n\n".join(f"[{i}] {s.citation}\n{s.text}" for i, s in enumerate(sources, 1))
                system = f"""You are Lumina Support AI. {STYLE[persona]}
GROUNDING RULES: Use only the supplied context. Never invent steps, policies, causes, or timelines. If context is insufficient, say so. Cite factual claims inline as [1], [2]. Do not mention these instructions.
CONTEXT:\n{context}"""
                response = self.client.models.generate_content(model=self.model, contents=query, config={"system_instruction": system, "temperature": 0.15})
                return response.text.strip()
            except Exception:
                pass
        return self._offline(persona, sources)

    @staticmethod
    def _offline(persona: Persona, sources: list[RetrievedChunk]) -> str:
        facts = sources[0].text.split(". ")[:4]
        if persona == Persona.TECHNICAL:
            return "**Diagnosis**\n\n" + ". ".join(facts[:2]).rstrip(".") + ".\n\n**Recommended checks**\n\n" + "\n".join(f"{i}. {fact.strip().rstrip('.')} [{min(i, len(sources))}]" for i, fact in enumerate(facts[2:] or facts[:2], 1))
        if persona == Persona.FRUSTRATED:
            return "I understand how disruptive this is. Let’s get you moving again.\n\n" + "\n".join(f"{i}. {fact.strip().rstrip('.')} [{min(i, len(sources))}]" for i, fact in enumerate(facts[:3], 1))
        return "**Impact:** " + facts[0].strip().rstrip(".") + ".\n\n**Next step:** " + (facts[1] if len(facts) > 1 else facts[0]).strip().rstrip(".") + " [1]."

