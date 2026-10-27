"""Direct route-handler tests; no network server or model downloads required."""
from __future__ import annotations
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import src.api as api


class FakeModel:
    classes_ = [0, 1]
    def predict_proba(self, frame):
        assert frame.iloc[0]["turno"] == "noturno"
        assert frame.iloc[0]["produto"] == "A"
        assert frame.iloc[0]["operador"] == "OP01"
        return [[0.2, 0.8]]


@pytest.fixture(autouse=True)
def resources(monkeypatch):
    monkeypatch.setattr(api, "ml_model", FakeModel())
    monkeypatch.setattr(api, "prediction_threshold", 0.5)
    monkeypatch.setattr(api, "rag_assistant", None)


def payload(**updates):
    data = {"turno": "noturno", "produto": "A", "operador": "OP01", "quantidade_inspecionada": 100}
    data.update(updates)
    return data


def test_root_endpoint():
    response = api.root()
    assert response["projeto"] == "Industrial Quality Monitor"
    assert response["status"] == "online"


def test_health_is_liveness_and_does_not_load_models(monkeypatch):
    def fail_if_called():
        raise AssertionError("health não deve tentar carregar modelos")
    monkeypatch.setattr(api, "carregar_recursos", fail_if_called)
    assert api.health_check()["status"] == "healthy"


def test_readiness_requires_loaded_model(monkeypatch):
    assert api.readiness_check()["status"] == "ready"
    monkeypatch.setattr(api, "ml_model", None)
    with pytest.raises(HTTPException) as error:
        api.readiness_check()
    assert error.value.status_code == 503


def test_predict_uses_training_categories_and_class_probability():
    request = api.InspectionInput.model_validate(payload())
    response = api.predict_defect(request)
    assert response.model_dump() == {
        "previsao_defeito": True,
        "probabilidade_defeito": 0.8,
        "classe_prevista": "sim",
    }


def test_predict_rejects_unknown_categories():
    with pytest.raises(ValidationError):
        api.InspectionInput.model_validate(payload(produto="produto_A", operador="operador_OP01"))


def test_rag_question_is_limited_to_500_characters():
    with pytest.raises(ValidationError):
        api.RAGQueryInput.model_validate({"pergunta": "x" * 501})


def test_predict_returns_503_without_model(monkeypatch):
    monkeypatch.setattr(api, "ml_model", None)
    request = api.InspectionInput.model_validate(payload())
    with pytest.raises(HTTPException) as error:
        api.predict_defect(request)
    assert error.value.status_code == 503


def test_rag_endpoint_uses_lazy_loader(monkeypatch):
    document = SimpleNamespace(metadata={"file_name": "trinca.md"})
    monkeypatch.setattr(api, "carregar_assistente_rag", lambda: {"ready": True})
    monkeypatch.setattr(api, "responder_rag", lambda assistant, question: {
        "result": "A peça deve ser descartada.", "source_documents": [document],
        "answer_method": "regra_documental", "best_score": 0.91,
    })
    response = api.ask_rag(api.RAGQueryInput(pergunta="O que fazer com trinca?"))
    assert response.fontes == ["trinca.md"]
    assert response.metodo_resposta == "regra_documental"


def test_rag_unavailable_does_not_leak_internal_error(monkeypatch):
    def fail():
        raise RuntimeError("internal path")
    monkeypatch.setattr(api, "carregar_assistente_rag", fail)
    with pytest.raises(HTTPException) as error:
        api.ask_rag(api.RAGQueryInput(pergunta="Como inspecionar a peça?"))
    assert error.value.status_code == 503
    assert "internal path" not in error.value.detail
