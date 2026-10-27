"""API REST para inferência ML e consulta documental RAG."""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ml_model: Optional[Any] = None
rag_assistant: Optional[Dict[str, Any]] = None
prediction_threshold = 0.5


def carregar_recursos() -> None:
    """Carrega o artefato ML local; o RAG pesado permanece sob demanda."""
    global ml_model, prediction_threshold
    if ml_model is not None:
        return
    model_path = BASE_DIR / "models" / "modelo_rf.joblib"
    if not model_path.exists():
        return
    try:
        artifact = joblib.load(model_path)
        if isinstance(artifact, dict) and "model" in artifact:
            ml_model = artifact["model"]
            prediction_threshold = float(artifact.get("threshold", 0.5))
        else:
            ml_model = artifact  # Compatibilidade com pipeline legado.
    except Exception:
        # Detalhes internos não são enviados ao cliente nem registrados com caminhos.
        print("Falha ao carregar o artefato de ML.")


def carregar_assistente_rag() -> Dict[str, Any]:
    """Importa embeddings/transformers somente no primeiro uso do endpoint RAG."""
    global rag_assistant
    if rag_assistant is None:
        from src.rag_assistant import criar_assistente
        rag_assistant = criar_assistente()
    return rag_assistant


def responder_rag(assistant: Dict[str, Any], question: str) -> Dict[str, Any]:
    from src.rag_assistant import responder
    return responder(assistant, question)


@asynccontextmanager
async def lifespan(app: FastAPI):
    carregar_recursos()
    yield


app = FastAPI(
    title="Industrial Quality Monitor API",
    description="Previsão de defeitos e consulta a procedimentos técnicos.",
    version="1.0.0",
    lifespan=lifespan,
)


class InspectionInput(BaseModel):
    turno: Literal["diurno", "tarde", "noturno"] = Field(..., json_schema_extra={"example": "noturno"})
    produto: Literal["A", "B", "C", "D"] = Field(..., json_schema_extra={"example": "A"})
    operador: Literal["OP01", "OP02", "OP03", "OP04", "OP05", "OP06", "OP07", "OP08"] = Field(..., json_schema_extra={"example": "OP01"})
    quantidade_inspecionada: int = Field(..., gt=0, json_schema_extra={"example": 150})


class PredictionOutput(BaseModel):
    previsao_defeito: bool
    probabilidade_defeito: float
    classe_prevista: str


class RAGQueryInput(BaseModel):
    pergunta: str = Field(..., min_length=2, max_length=500)


class RAGQueryOutput(BaseModel):
    resposta: str
    fontes: List[str] = Field(default_factory=list)
    metodo_resposta: str
    score_similaridade: Optional[float] = None


@app.get("/")
def root():
    return {"projeto": "Industrial Quality Monitor", "versao": "1.0.0", "status": "online", "documentacao": "/docs"}


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Liveness sem downloads nem inicialização de modelos."""
    return {"status": "healthy", "ml_model_loaded": ml_model is not None, "rag_assistant_loaded": rag_assistant is not None}


@app.get("/ready")
def readiness_check():
    if ml_model is None:
        raise HTTPException(status_code=503, detail="Modelo de ML não está carregado.")
    return {"status": "ready", "ml_model_loaded": True}


@app.post("/predict", response_model=PredictionOutput)
def predict_defect(input_data: InspectionInput):
    if ml_model is None:
        raise HTTPException(status_code=503, detail="Modelo de Machine Learning não está disponível no servidor.")
    try:
        row = pd.DataFrame([input_data.model_dump()])
        probabilities = ml_model.predict_proba(row)[0]
        classes = list(ml_model.classes_)
        defect_index = next((i for i, value in enumerate(classes) if str(value).lower() in {"1", "sim"}), None)
        if defect_index is None:
            raise ValueError("Modelo sem classe positiva de defeito.")
        probability = float(probabilities[defect_index])
        has_defect = probability >= prediction_threshold
        return PredictionOutput(
            previsao_defeito=has_defect,
            probabilidade_defeito=round(probability, 4),
            classe_prevista="sim" if has_defect else "nao",
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Erro durante o processamento da predição.") from None


@app.post("/rag/ask", response_model=RAGQueryOutput)
def ask_rag(query_input: RAGQueryInput):
    try:
        assistant = carregar_assistente_rag()
        result = responder_rag(assistant, query_input.pergunta)
        documents = result.get("source_documents", [])
        sources = sorted({doc.metadata.get("file_name", "documento") for doc in documents})
        return RAGQueryOutput(
            resposta=result.get("result", ""),
            fontes=sources,
            metodo_resposta=result.get("answer_method", "desconhecido"),
            score_similaridade=result.get("best_score"),
        )
    except Exception:
        raise HTTPException(status_code=503, detail="Assistente RAG indisponível no servidor.") from None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
