from src.escalator import Escalator
from src.models import ChatTurn, Persona, PersonaResult, RetrievedChunk


def persona(kind=Persona.EXECUTIVE):
    return PersonaResult(kind, .9, "test")


def source(score=.8):
    return [RetrievedChunk("content", "guide.md", "Overview", None, score)]


def test_sensitive_billing_escalates():
    decision = Escalator(.3, 2).decide("Refund my duplicate charge", persona(), source(), [])
    assert decision.escalated
    assert "Sensitive" in decision.reasons[0]


def test_low_confidence_escalates():
    assert Escalator(.5, 2).decide("unknown", persona(), source(.1), []).escalated


def test_repeated_frustration_escalates():
    history = [ChatTurn("user", "still broken", Persona.FRUSTRATED.value)]
    decision = Escalator(.3, 2).decide("Still broken!", persona(Persona.FRUSTRATED), source(), history)
    assert decision.escalated


def test_grounded_normal_question_does_not_escalate():
    assert not Escalator(.3, 2).decide("How do I sign in?", persona(), source(), []).escalated

