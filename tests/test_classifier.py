from src.classifier import PersonaClassifier
from src.models import Persona


def test_technical_persona():
    assert PersonaClassifier().classify("Show the API OAuth header and 401 logs").persona == Persona.TECHNICAL


def test_frustrated_persona():
    assert PersonaClassifier().classify("Nothing works! This is unacceptable and urgent!").persona == Persona.FRUSTRATED


def test_executive_persona():
    assert PersonaClassifier().classify("What is the revenue impact and resolution timeline?").persona == Persona.EXECUTIVE


def test_empty_message_rejected():
    import pytest
    with pytest.raises(ValueError):
        PersonaClassifier().classify("  ")

