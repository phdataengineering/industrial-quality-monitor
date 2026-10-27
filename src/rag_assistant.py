
"""
Industrial Quality Monitor — Assistente RAG
Arquivo: src/rag_assistant.py

Funcionalidades:
- Carrega procedimentos Markdown, excluindo README.md.
- Cria embeddings locais e índice vetorial FAISS.
- Bloqueia perguntas fora do escopo.
- Recupera evidências e apresenta as fontes consultadas.
- Prioriza regras documentais para respostas críticas.
- Evita usar o modelo generativo para códigos e regras numéricas
  que possam ser respondidos diretamente pelos procedimentos.
"""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from transformers import pipeline


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs" / "procedimentos"

EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

GENERATION_MODEL = os.getenv(
    "RAG_GENERATION_MODEL",
    "google/flan-t5-small",
)

TOP_K = int(os.getenv("RAG_TOP_K", "4"))
MIN_COSINE_SIMILARITY = float(
    os.getenv("RAG_MIN_COSINE_SIMILARITY", "0.40")
)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 75


class FaissVectorIndex:
    """Busca FAISS direta; usa distância exata NumPy no Windows."""

    def __init__(self, documents: list[Document], embeddings: Any) -> None:
        import numpy as np

        self.documents = documents
        self.embeddings = embeddings
        vectors = np.asarray(
            embeddings.embed_documents([doc.page_content for doc in documents]),
            dtype="float32",
        )
        if vectors.ndim != 2 or len(vectors) != len(documents):
            raise ValueError("Embeddings inválidos para criar índice FAISS.")
        self.index = None
        self.vectors = vectors
        if sys.platform != "win32":
            import faiss

            self.index = faiss.IndexFlatL2(vectors.shape[1])
            self.index.add(vectors)

    @classmethod
    def from_documents(cls, documents: list[Document], embeddings: Any):
        return cls(documents, embeddings)

    def similarity_search_with_score(
        self, query: str, k: int = 4
    ) -> list[tuple[Document, float]]:
        import numpy as np

        vector = np.asarray(
            [self.embeddings.embed_query(query)], dtype="float32"
        )
        if self.index is None:
            differences = self.vectors - vector[0]
            distances = np.einsum("ij,ij->i", differences, differences)
            indexes = np.argsort(distances)[: min(k, len(self.documents))]
            matches = [(self.documents[i], float(distances[i])) for i in indexes]
            return matches

        distances, indexes = self.index.search(vector, min(k, len(self.documents)))
        return [
            (self.documents[index], float(distance))
            for index, distance in zip(indexes[0], distances[0])
            if index >= 0
        ]

REFUSAL = (
    "Não encontrei informações suficientes nos procedimentos "
    "técnicos disponíveis para responder a essa pergunta."
)

TERMOS_ESCOPO = {
    "qualidade", "procedimento", "procedimentos", "defeito", "defeitos",
    "trinca", "trincas", "dimensional", "desvio", "tolerancia",
    "superficie", "oxidacao", "corrosao", "rugosidade", "mancha",
    "manchas", "risco", "riscos", "peca", "pecas", "lote", "refugo",
    "retrabalho", "usinagem", "fundicao", "paquimetro", "inspecao",
    "reinspecao", "reinspecionar", "calibracao", "ferramenta",
    "ferramentas", "maquina", "maquinas", "material", "materiais",
    "producao", "fabricacao", "medicao", "medir", "fosfatizacao",
    "def-tri", "def-sup", "codigo de defeito", "nao conformidade",
    "nao conformidades", "certificado", "descarte", "descartar",
    "supervisor", "operador",
}


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar(texto: str) -> str:
    """Padroniza texto, remove acentos e normaliza espaços."""
    texto = texto.lower().replace("²", "2")
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def tokens(texto: str) -> set[str]:
    return set(
        re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalizar(texto))
    )


def menciona_meio_milimetro(texto: str) -> bool:
    q = normalizar(texto)

    return bool(
        re.search(
            r"(?<!\d)0[.,]5\s*(?:mm|milimetro|milimetros)\b",
            q,
        )
        or re.search(r"\bmeio\s+milimetro\b", q)
    )


def menciona_limite_superior(texto: str) -> bool:
    palavras = tokens(texto)

    return bool(
        {
            "superior", "maior", "acima", "ultrapassa",
            "ultrapassar", "excede", "exceder",
        }.intersection(palavras)
    )


# ============================================================
# CONTROLE DE ESCOPO
# ============================================================

def pergunta_dentro_do_escopo(pergunta: str) -> bool:
    q = normalizar(pergunta)
    palavras = tokens(q)

    for termo in TERMOS_ESCOPO:
        termo_normalizado = normalizar(termo)

        if " " in termo_normalizado:
            if termo_normalizado in q:
                return True
        elif termo_normalizado in palavras:
            return True

    return False


# ============================================================
# CARREGAMENTO DE DOCUMENTOS
# ============================================================

def carregar_documentos() -> list[Document]:
    if not DOCS_DIR.exists():
        raise FileNotFoundError(
            f"Pasta de procedimentos não encontrada: {DOCS_DIR}"
        )

    arquivos = sorted(DOCS_DIR.rglob("*.md"))
    arquivos = [
        arquivo
        for arquivo in arquivos
        if arquivo.name.lower() != "readme.md"
    ]

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum procedimento Markdown foi encontrado. "
            f"Diretório verificado: {DOCS_DIR}"
        )

    documentos: list[Document] = []

    for arquivo in arquivos:
        conteudo = arquivo.read_text(encoding="utf-8").strip()

        if not conteudo:
            print(f"Aviso: documento vazio ignorado: {arquivo.name}")
            continue

        documentos.append(
            Document(
                page_content=conteudo,
                metadata={
                    "source": str(arquivo.resolve()),
                    "file_name": arquivo.name,
                },
            )
        )

    if not documentos:
        raise RuntimeError("Nenhum procedimento válido foi carregado.")

    return documentos


def documentos_por_nome(
    documentos: list[Document],
    nome: str,
) -> list[Document]:
    nome = nome.lower()

    return [
        doc for doc in documentos
        if doc.metadata.get("file_name", "").lower() == nome
    ]


def texto_dos_documentos(documentos: list[Document]) -> str:
    return "\n".join(doc.page_content for doc in documentos)


# ============================================================
# INICIALIZAÇÃO
# ============================================================

def criar_assistente() -> dict[str, Any]:
    print("=== INICIANDO FASE 5: ASSISTENTE RAG ===")
    print(f"Diretório dos documentos: {DOCS_DIR}")

    print("Carregando procedimentos...")
    documentos = carregar_documentos()
    print(f"{len(documentos)} documentos carregados.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n", ". ", " ", ""],
        add_start_index=True,
    )

    chunks = splitter.split_documents(documentos)

    if not chunks:
        raise RuntimeError("Nenhum chunk foi criado.")

    print(f"{len(chunks)} chunks criados.")
    print("Criando embeddings locais...")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    print("Criando índice FAISS...")
    vectorstore = FaissVectorIndex.from_documents(chunks, embeddings)

    print(f"Carregando modelo local: {GENERATION_MODEL}...")

    gerador = pipeline(
        task="text2text-generation",
        model=GENERATION_MODEL,
        tokenizer=GENERATION_MODEL,
        max_new_tokens=100,
        do_sample=False,
        truncation=True,
        device=-1,
    )

    llm = HuggingFacePipeline(pipeline=gerador)

    print("Assistente preparado.")

    return {
        "vectorstore": vectorstore,
        "llm": llm,
        "top_k": TOP_K,
        "min_similarity": MIN_COSINE_SIMILARITY,
        "documentos_originais": documentos,
    }


# ============================================================
# RECUPERAÇÃO VETORIAL
# ============================================================

def recuperar_documentos(
    assistente: dict[str, Any],
    pergunta: str,
) -> tuple[list[Document], list[float], float | None]:
    """
    O FAISS usa distância L2 ao quadrado neste índice.
    Com embeddings normalizados:
        cosseno = 1 - distância L2 ao quadrado / 2
    """
    resultados = assistente["vectorstore"].similarity_search_with_score(
        pergunta,
        k=assistente["top_k"],
    )

    candidatos: list[tuple[Document, float]] = []

    for documento, distancia in resultados:
        distancia = float(distancia)
        similaridade = max(
            -1.0,
            min(1.0, 1.0 - distancia / 2.0),
        )
        candidatos.append((documento, similaridade))

    candidatos.sort(key=lambda item: item[1], reverse=True)

    melhor_score = candidatos[0][1] if candidatos else None
    limite = assistente["min_similarity"]

    relevantes = [
        (documento, score)
        for documento, score in candidatos
        if score >= limite
    ]

    documentos = [doc for doc, _ in relevantes]
    scores = [score for _, score in relevantes]

    return documentos, scores, melhor_score


# ============================================================
# REGRAS DOCUMENTAIS
# ============================================================

def responder_codigo_defeito(
    pergunta: str,
    documentos: list[Document],
) -> tuple[str, list[Document]] | None:
    """
    Resolve códigos consultando o procedimento correspondente completo.
    Não depende do chunk recuperado pelo FAISS.
    """
    q = normalizar(pergunta)
    palavras = tokens(q)

    pede_codigo = bool(
        {"codigo", "identificador"}.intersection(palavras)
        or "codigo de defeito" in q
        or "qual o codigo" in q
        or "qual e o codigo" in q
    )

    if not pede_codigo:
        return None

    # Importante: "trinca" in q também reconhece "trincas".
    if "trinca" in q:
        procedimento = documentos_por_nome(documentos, "trinca.md")

        if not procedimento:
            return None

        texto = texto_dos_documentos(procedimento)
        codigos = re.findall(
            r"\bDEF-[A-Z0-9-]+\b",
            texto,
            flags=re.IGNORECASE,
        )
        codigos = {codigo.upper() for codigo in codigos}

        if "DEF-TRI" in codigos:
            return (
                "O código de defeito para trincas é DEF-TRI.",
                procedimento,
            )

        return None

    if any(
        termo in q
        for termo in ("superficie", "oxidacao", "corrosao")
    ):
        procedimento = documentos_por_nome(documentos, "superficie.md")

        if not procedimento:
            return None

        texto = texto_dos_documentos(procedimento)
        codigos = re.findall(
            r"\bDEF-[A-Z0-9-]+\b",
            texto,
            flags=re.IGNORECASE,
        )
        codigos = {codigo.upper() for codigo in codigos}

        if "DEF-SUP" in codigos:
            return (
                "O código documentado para defeitos de superfície é DEF-SUP.",
                procedimento,
            )

        return None

    # Sem assunto específico, só responde quando houver um único código
    # nos documentos considerados.
    contexto = texto_dos_documentos(documentos)
    codigos = re.findall(
        r"\bDEF-[A-Z0-9-]+\b",
        contexto,
        flags=re.IGNORECASE,
    )
    codigos = list(dict.fromkeys(c.upper() for c in codigos))

    if len(codigos) == 1:
        return (
            f"O código de defeito encontrado no contexto é {codigos[0]}.",
            documentos,
        )

    return None


def responder_regra_trinca(
    pergunta: str,
    documentos: list[Document],
) -> tuple[str, list[Document]] | None:
    q = normalizar(pergunta)
    palavras = tokens(q)

    pergunta_trinca = (
        "trinca" in q
        and re.search(r"\b2\s*mm\b", q) is not None
        and bool(
            {"maior", "acima", "superior", "profunda"}.intersection(palavras)
        )
    )

    if not pergunta_trinca:
        return None

    procedimento = documentos_por_nome(documentos, "trinca.md")

    if not procedimento:
        return None

    texto = normalizar(texto_dos_documentos(procedimento))

    tem_regra_descarte = (
        "trinca" in texto
        and re.search(r"\b2\s*mm\b", texto) is not None
        and any(
            termo in texto
            for termo in ("descartada", "descartado", "descartar", "refugo")
        )
    )

    if not tem_regra_descarte:
        return None

    partes = []

    if "isolar o lote afetado" in texto:
        partes.append("Isolar o lote afetado.")

    if "notificar o supervisor de qualidade" in texto:
        partes.append("Notificar o supervisor de qualidade.")

    if "def-tri" in texto and "registrar" in texto:
        partes.append("Registrar a ocorrência com o código DEF-TRI.")

    partes.append(
        "Se a trinca for profunda e maior que 2 mm, "
        "a peça deve ser descartada (refugo)."
    )

    return " ".join(partes), procedimento


def responder_regra_dimensional(
    pergunta: str,
    documentos: list[Document],
) -> tuple[str, list[Document]] | None:
    q = normalizar(pergunta)
    palavras = tokens(q)

    pergunta_dimensional = bool(
        {"dimensional", "desvio", "tolerancia"}.intersection(palavras)
    )

    if not (
        pergunta_dimensional
        and menciona_meio_milimetro(q)
        and menciona_limite_superior(q)
    ):
        return None

    procedimento = documentos_por_nome(documentos, "dimensional.md")

    if not procedimento:
        return None

    texto = normalizar(texto_dos_documentos(procedimento))

    tem_limite_documentado = (
        menciona_meio_milimetro(texto)
        and any(
            termo in texto
            for termo in ("desvio dimensional", "desvio", "tolerancia")
        )
    )

    tem_regra_descarte = any(
        termo in texto
        for termo in (
            "descartada", "descartado", "descartar",
            "descarte", "refugo",
        )
    )

    if not (tem_limite_documentado and tem_regra_descarte):
        return None

    return (
        "Se o desvio dimensional for superior a 0,5 mm, "
        "a peça deve ser descartada, conforme o procedimento "
        "de desvio dimensional.",
        procedimento,
    )


def responder_regra_documental(
    pergunta: str,
    documentos: list[Document],
) -> tuple[str, list[Document]] | None:
    """
    A ordem é intencional: códigos e regras críticas são resolvidos
    por documentos completos antes de qualquer geração por LLM.
    """
    for funcao in (
        responder_codigo_defeito,
        responder_regra_trinca,
        responder_regra_dimensional,
    ):
        resultado = funcao(pergunta, documentos)

        if resultado:
            return resultado

    return None


# ============================================================
# VALIDAÇÃO DA RESPOSTA GENERATIVA
# ============================================================

def validar_resposta_generativa(
    resposta: str,
    pergunta: str,
    contexto: str,
) -> str:
    resposta = re.sub(
        r"^\s*(?:resposta|answer)\s*:\s*",
        "",
        resposta.strip(),
        flags=re.IGNORECASE,
    ).strip()

    if not resposta:
        return REFUSAL

    if normalizar(resposta) == normalizar(REFUSAL):
        return REFUSAL

    if len(resposta) > 500:
        return REFUSAL

    linhas = [linha.strip() for linha in resposta.splitlines() if linha.strip()]

    if len(linhas) > 5:
        return REFUSAL

    if any(
        marcador in normalizar(resposta)
        for marcador in (
            "fonte:", "causas provaveis", "contexto:",
            "procedimento:", "identificacao",
        )
    ):
        return REFUSAL

    resposta_normalizada = normalizar(resposta)
    contexto_normalizado = normalizar(contexto)

    if len(resposta_normalizada) >= 100:
        if resposta_normalizada in contexto_normalizado:
            return REFUSAL

    # Não aceitar uma regra numérica crítica gerada pelo modelo.
    if menciona_meio_milimetro(pergunta) and re.search(
        r"\b\d+(?:[.,]\d+)?\s*mm\b",
        resposta_normalizada,
    ):
        return REFUSAL

    return resposta


# ============================================================
# RESPOSTA PRINCIPAL
# ============================================================

def responder(
    assistente: dict[str, Any],
    pergunta: str,
) -> dict[str, Any]:
    if not pergunta or not pergunta.strip():
        return {
            "result": "Digite uma pergunta.",
            "source_documents": [],
            "scores": [],
            "answer_method": "validacao",
        }

    pergunta = pergunta.strip()

    if not pergunta_dentro_do_escopo(pergunta):
        return {
            "result": REFUSAL,
            "source_documents": [],
            "scores": [],
            "answer_method": "recusa_fora_do_escopo",
        }

    documentos_recuperados, scores, melhor_score = recuperar_documentos(
        assistente,
        pergunta,
    )

    if not documentos_recuperados:
        return {
            "result": REFUSAL,
            "source_documents": [],
            "scores": [],
            "best_score": melhor_score,
            "answer_method": "recusa_por_relevancia",
        }

    # Regras críticas consultam os documentos completos, não só os chunks.
    documentos_originais = assistente.get(
        "documentos_originais",
        documentos_recuperados,
    )

    resultado_regra = responder_regra_documental(
        pergunta,
        documentos_originais,
    )

    if resultado_regra:
        resposta, fontes = resultado_regra

        return {
            "result": resposta,
            "source_documents": fontes,
            "scores": scores,
            "best_score": melhor_score,
            "answer_method": "regra_documental",
        }

    contexto = "\n\n".join(
        f"Fonte: {doc.metadata.get('file_name', 'documento')}\n"
        f"{doc.page_content.strip()}"
        for doc in documentos_recuperados
    )

    prompt = (
        "Você é um assistente técnico de qualidade industrial. "
        "Responda em português, de forma curta e direta. "
        "Use somente informações explicitamente presentes no contexto. "
        "Não invente limites, códigos, causas ou ações. "
        "Não copie o documento inteiro. "
        "Se o contexto não responder diretamente à pergunta, responda "
        f"exatamente: {REFUSAL}\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Pergunta: {pergunta}\n"
        "Resposta:"
    )

    geracao = assistente["llm"].invoke(prompt)

    resposta = validar_resposta_generativa(
        str(geracao),
        pergunta,
        contexto,
    )

    aceita = resposta != REFUSAL

    return {
        "result": resposta,
        "source_documents": documentos_recuperados if aceita else [],
        "scores": scores if aceita else [],
        "best_score": melhor_score,
        "answer_method": (
            "modelo_generativo"
            if aceita
            else "recusa_resposta_nao_validada"
        ),
    }


# ============================================================
# IMPRESSÃO DOS RESULTADOS
# ============================================================

def imprimir_resultado(
    pergunta: str,
    resultado: dict[str, Any],
) -> None:
    print(f"\nPergunta: {pergunta}")
    print(f"Resposta: {resultado['result']}")
    print("Fontes consultadas:")

    documentos = resultado.get("source_documents", [])

    if not documentos:
        print(" - Nenhuma fonte considerada suficientemente relevante.")

        melhor = resultado.get("best_score")
        if melhor is not None:
            print(f"Melhor similaridade: {melhor:.4f}")

        print(f"Método de resposta: {resultado.get('answer_method')}")
        return

    fontes_vistas = set()

    for documento in documentos:
        fonte = documento.metadata.get("source", "fonte desconhecida")

        if fonte not in fontes_vistas:
            print(f" - {fonte}")
            fontes_vistas.add(fonte)

    scores = resultado.get("scores", [])

    if scores:
        print(
            "Similaridades de cosseno: "
            + ", ".join(f"{score:.4f}" for score in scores)
        )

    print(f"Método de resposta: {resultado.get('answer_method')}")


# ============================================================
# TESTES DE CONTROLE
# ============================================================

def executar_testes(assistente: dict[str, Any]) -> None:
    print("\n=== TESTES DE CONTROLE ===")

    perguntas = [
        "O que fazer se a trinca for maior que 2mm?",
        "Qual a política de férias dos funcionários?",
        "Qual é o código de defeito para trincas?",
        "Qual é o código de defeito para trinca?",
        "O que fazer com desvio dimensional superior a 0,5mm?",
        "O que fazer com desvio dimensional superior a 0,5 mm?",
        "O que fazer com desvio dimensional acima de 0.5mm?",
        "Qual é a capital da França?",
    ]

    for pergunta in perguntas:
        resultado = responder(assistente, pergunta)
        imprimir_resultado(pergunta, resultado)


if __name__ == "__main__":
    try:
        assistente = criar_assistente()
        executar_testes(assistente)
    except Exception as erro:
        print(f"\nERRO AO EXECUTAR O ASSISTENTE: {erro}")
        raise
