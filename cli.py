from __future__ import annotations

import json

from src.models import ChatTurn
from src.service import SupportService


def main() -> None:
    service, history = SupportService(), []
    added = service.ingest()
    print(f"Lumina Support AI ({service.mode}); {added} new knowledge chunks indexed. Type 'exit' to quit.")
    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in {"exit", "quit"}:
            break
        try:
            result = service.respond(query, history)
        except ValueError as exc:
            print(exc)
            continue
        print(f"\nPersona: {result.persona.persona.value} ({result.persona.confidence:.0%})")
        print("Sources:", ", ".join(s.citation for s in result.sources) or "none")
        print("Escalated:", result.escalation.escalated)
        print("\nLumina:", result.response)
        if result.handoff:
            print("\nHandoff:\n", json.dumps(result.handoff, indent=2))
        history.extend([ChatTurn("user", query, result.persona.persona.value), ChatTurn("assistant", result.response)])


if __name__ == "__main__":
    main()

