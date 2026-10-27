"""Integração pequena para validar FAISS sem baixar modelos Hugging Face."""
from langchain_core.documents import Document

from src.rag_assistant import FaissVectorIndex


class TinyEmbeddings:
    def embed_documents(self, texts):
        return [[1.0, 0.0] if "trinca" in text else [0.0, 1.0] for text in texts]

    def embed_query(self, text):
        return [1.0, 0.0]


def test_faiss_direct_index_returns_nearest_document():
    docs = [Document(page_content="procedimento de trinca"), Document(page_content="procedimento de superfície")]
    index = FaissVectorIndex.from_documents(docs, TinyEmbeddings())

    results = index.similarity_search_with_score("trinca", k=1)

    assert results[0][0].page_content == "procedimento de trinca"
    assert results[0][1] == 0.0
