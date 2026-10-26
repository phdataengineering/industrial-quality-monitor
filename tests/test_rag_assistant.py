
"""Testes automatizados do Industrial Quality Monitor — Assistente RAG.

Os testes usam documentos reais do projeto e componentes simulados.
Não carregam embeddings, FAISS real ou modelos generativos.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

from src import rag_assistant as rag


class FakeVectorStore:
    """Simula a busca vetorial sem inicializar o FAISS."""

    def __init__(self, documentos: list[Any]) -> None:
        self.documentos = documentos
        self.chamadas = 0

    def similarity_search_with_score(
        self,
        pergunta: str,
        k: int = 4,
    ) -> list[tuple[Any, float]]:
        self.chamadas += 1

        # Para embeddings normalizados, distância 0.1 corresponde
        # à similaridade calculada pelo código de aproximadamente 0.95.
        return [
            (documento, 0.1)
            for documento in self.documentos[:k]
        ]


class FakeLLM:
    """Simula a resposta do modelo de linguagem."""

    def __init__(self, resposta: str = rag.REFUSAL) -> None:
        self.resposta = resposta
        self.chamadas = 0

    def invoke(self, prompt: str) -> str:
        self.chamadas += 1
        return self.resposta


class IndustrialQualityMonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.documentos = rag.carregar_documentos()
        cls.nomes_documentos = {
            documento.metadata.get("file_name", "")
            for documento in cls.documentos
        }

    def criar_assistente(
        self,
        resposta_llm: str = rag.REFUSAL,
    ) -> dict[str, Any]:
        vectorstore = FakeVectorStore(self.documentos)
        llm = FakeLLM(resposta_llm)

        return {
            "vectorstore": vectorstore,
            "llm": llm,
            "top_k": 4,
            "min_similarity": 0.40,
            "documentos_originais": self.documentos,
        }

    @staticmethod
    def nomes_fontes(resultado: dict[str, Any]) -> set[str]:
        return {
            documento.metadata.get("file_name", "")
            for documento in resultado.get("source_documents", [])
        }

    def test_documentos_esperados_existem(self) -> None:
        """Confirma a presença dos três procedimentos principais."""
        esperados = {
            "trinca.md",
            "dimensional.md",
            "superficie.md",
        }

        self.assertTrue(
            esperados.issubset(self.nomes_documentos),
            msg=(
                "Procedimentos ausentes: "
                f"{sorted(esperados - self.nomes_documentos)}"
            ),
        )

    def test_readme_nao_e_carregado(self) -> None:
        """O README não deve ser indexado como procedimento."""
        self.assertNotIn("readme.md", self.nomes_documentos)

    def test_codigo_de_trinca_no_plural(self) -> None:
        """O código DEF-TRI deve ser encontrado para 'trincas'."""
        resultado = rag.responder(
            self.criar_assistente(),
            "Qual é o código de defeito para trincas?",
        )

        self.assertIn("DEF-TRI", resultado["result"])
        self.assertEqual(
            resultado["answer_method"],
            "regra_documental",
        )
        self.assertIn("trinca.md", self.nomes_fontes(resultado))

    def test_codigo_de_trinca_no_singular(self) -> None:
        resultado = rag.responder(
            self.criar_assistente(),
            "Qual é o código de defeito para trinca?",
        )

        self.assertIn("DEF-TRI", resultado["result"])
        self.assertIn("trinca.md", self.nomes_fontes(resultado))

    def test_regra_de_trinca_acima_de_2mm(self) -> None:
        """Uma trinca profunda acima de 2 mm deve ser descartada."""
        assistente = self.criar_assistente()

        resultado = rag.responder(
            assistente,
            "O que fazer se a trinca for maior que 2mm?",
        )

        resposta = rag.normalizar(resultado["result"])

        self.assertIn("descart", resposta)
        self.assertIn("2 mm", resposta)
        self.assertIn("DEF-TRI", resultado["result"])
        self.assertEqual(
            resultado["answer_method"],
            "regra_documental",
        )
        self.assertIn("trinca.md", self.nomes_fontes(resultado))
        self.assertEqual(
            assistente["llm"].chamadas,
            0,
            "Uma regra documental crítica não deve depender do LLM.",
        )

    def test_regra_dimensional_com_virgula(self) -> None:
        resultado = rag.responder(
            self.criar_assistente(),
            "O que fazer com desvio dimensional superior a 0,5mm?",
        )

        resposta = rag.normalizar(resultado["result"])

        self.assertIn("descart", resposta)
        self.assertEqual(
            resultado["answer_method"],
            "regra_documental",
        )
        self.assertIn("dimensional.md", self.nomes_fontes(resultado))

    def test_regra_dimensional_com_espaco(self) -> None:
        resultado = rag.responder(
            self.criar_assistente(),
            "O que fazer com desvio dimensional superior a 0,5 mm?",
        )

        self.assertIn("descart", rag.normalizar(resultado["result"]))
        self.assertEqual(
            resultado["answer_method"],
            "regra_documental",
        )

    def test_regra_dimensional_com_ponto_decimal(self) -> None:
        resultado = rag.responder(
            self.criar_assistente(),
            "O que fazer com desvio dimensional acima de 0.5mm?",
        )

        self.assertIn("descart", rag.normalizar(resultado["result"]))
        self.assertEqual(
            resultado["answer_method"],
            "regra_documental",
        )

    def test_expressao_meio_milimetro(self) -> None:
        """Verifica a identificação de uma paráfrase do limite."""
        self.assertTrue(
            rag.menciona_meio_milimetro(
                "O desvio passou de meio milímetro."
            )
        )

    def test_pergunta_vazia(self) -> None:
        resultado = rag.responder(self.criar_assistente(), "   ")

        self.assertEqual(resultado["result"], "Digite uma pergunta.")
        self.assertEqual(resultado["source_documents"], [])
        self.assertEqual(resultado["answer_method"], "validacao")

    def test_pergunta_fora_do_escopo_e_recusada(self) -> None:
        """Assuntos sem relação com qualidade industrial são recusados."""
        assistente = self.criar_assistente()

        resultado = rag.responder(
            assistente,
            "Qual é a capital da França?",
        )

        self.assertEqual(resultado["result"], rag.REFUSAL)
        self.assertEqual(resultado["source_documents"], [])
        self.assertEqual(
            resultado["answer_method"],
            "recusa_fora_do_escopo",
        )
        self.assertEqual(
            assistente["vectorstore"].chamadas,
            0,
            "A busca não deve ser executada para pergunta fora do escopo.",
        )

    def test_politica_de_ferias_e_recusada(self) -> None:
        resultado = rag.responder(
            self.criar_assistente(),
            "Qual é a política de férias dos funcionários?",
        )

        self.assertEqual(resultado["result"], rag.REFUSAL)
        self.assertEqual(resultado["source_documents"], [])
        self.assertEqual(
            resultado["answer_method"],
            "recusa_fora_do_escopo",
        )

    def test_pergunta_tecnica_sem_regra_especifica_pode_ser_recusada(
        self,
    ) -> None:
        """Uma pergunta técnica não deve ser respondida sem evidência."""
        assistente = self.criar_assistente(resposta_llm=rag.REFUSAL)

        resultado = rag.responder(
            assistente,
            "Qual é a causa raiz de uma trinca?",
        )

        self.assertEqual(resultado["result"], rag.REFUSAL)
        self.assertEqual(resultado["source_documents"], [])
        self.assertEqual(
            resultado["answer_method"],
            "recusa_resposta_nao_validada",
        )

    def test_resposta_generativa_com_prefixo_e_normalizada(self) -> None:
        resposta = rag.validar_resposta_generativa(
            "Resposta: O lote deve ser inspecionado.",
            "Como tratar a inspeção de qualidade?",
            "O lote deve ser inspecionado.",
        )

        self.assertEqual(
            resposta,
            "O lote deve ser inspecionado.",
        )

    def test_resposta_generativa_vazia_e_recusada(self) -> None:
        resposta = rag.validar_resposta_generativa(
            "",
            "Como realizar a inspeção?",
            "O procedimento descreve a inspeção.",
        )

        self.assertEqual(resposta, rag.REFUSAL)

    def test_resposta_generativa_excessivamente_longa_e_recusada(
        self,
    ) -> None:
        resposta = rag.validar_resposta_generativa(
            "A" * 501,
            "Como realizar a inspeção?",
            "O procedimento descreve a inspeção.",
        )

        self.assertEqual(resposta, rag.REFUSAL)

    def test_regra_numerica_gerada_para_limite_e_recusada(self) -> None:
        """A validação não deve aceitar regra numérica gerada pelo LLM."""
        resposta = rag.validar_resposta_generativa(
            "A peça deve ser descartada acima de 0,5 mm.",
            "O que fazer com desvio dimensional acima de 0,5 mm?",
            "O procedimento trata de desvios dimensionais.",
        )

        self.assertEqual(resposta, rag.REFUSAL)

    def test_resultado_generativo_recusado_nao_exibe_fontes(self) -> None:
        assistente = self.criar_assistente(
            resposta_llm="A" * 501,
        )

        resultado = rag.responder(
            assistente,
            "Como funciona o procedimento de inspeção da peça?",
        )

        self.assertEqual(resultado["result"], rag.REFUSAL)
        self.assertEqual(resultado["source_documents"], [])
        self.assertEqual(resultado["scores"], [])
        self.assertEqual(
            resultado["answer_method"],
            "recusa_resposta_nao_validada",
        )

    def test_resposta_generativa_aceita_inclui_fontes(self) -> None:
        """Confirma a associação de fontes a uma resposta aceita."""
        resposta = "O procedimento descreve a inspeção da peça."

        assistente = self.criar_assistente(
            resposta_llm=resposta,
        )

        resultado = rag.responder(
            assistente,
            "Como funciona o procedimento de inspeção da peça?",
        )

        self.assertEqual(resultado["result"], resposta)
        self.assertEqual(
            resultado["answer_method"],
            "modelo_generativo",
        )
        self.assertTrue(resultado["source_documents"])
        self.assertTrue(resultado["scores"])

    def test_documentos_tem_metadados_de_origem(self) -> None:
        """As fontes devem permitir rastrear os arquivos consultados."""
        for documento in self.documentos:
            with self.subTest(
                arquivo=documento.metadata.get("file_name")
            ):
                self.assertTrue(documento.metadata.get("file_name"))
                self.assertTrue(documento.metadata.get("source"))
                self.assertTrue(documento.page_content.strip())

                caminho = Path(documento.metadata["source"])
                self.assertTrue(caminho.is_absolute())


if __name__ == "__main__":
    unittest.main(verbosity=2)
