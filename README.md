# Industrial Quality Monitor

Pipeline de dados de inspeção de qualidade industrial com previsão de refugo e assistente de consulta a procedimentos técnicos.

> Projeto de portfólio autodidata em **Engenharia de Dados** e **Engenharia de IA**.  
> Dados 100% sintéticos. Sem vínculo com qualquer empregador.

---

## Objetivo

Construir, em 90 dias, um portfólio público e reproduzível que demonstre competências em:

- ETL, SQL e modelagem relacional
- Machine Learning clássico (Scikit-learn)
- RAG com LLMs locais
- APIs (FastAPI) + Docker

---

## Arquitetura (visão geral)

```text
Fonte sintética -> Validação (Pandas) -> PostgreSQL
                                      -> ML (Scikit-learn) -> API FastAPI
                                      -> RAG (LangChain + embeddings locais)
```

---

## Status atual

| Fase | Nome | Status |
| :--- | :--- | :--- |
| 1 | Estrutura + Dados sintéticos | ✅ Concluída |
| 2 | Validação e ETL com Pandas | ✅ Concluída |
| 3 | Pipeline -> PostgreSQL | ✅ Concluída |
| 4 | Machine Learning | ✅ Concluída |
| 5 | LLMs + RAG | ✅ Concluída |
| 6 | API + Docker | Pendente |

---

## Como rodar (Fases 1 a 5)

### Pré-requisitos
- Python 3.11+
- Ambiente virtual (`venv`)
- PostgreSQL instalado e rodando localmente

```bash
# Criar e ativar venv
python -m venv .venv

# Windows
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Configuração do Banco de Dados (Fase 3)
1. Crie um banco de dados no PostgreSQL chamado `industrial_quality`.
2. Configure o arquivo `.env` na raiz com suas credenciais.
3. Execute o script `sql/schema.sql` no Query Tool do pgAdmin.

### Executando o Pipeline
```bash
# Gerar dados
python src/gerar_dados.py

# Validar dados
python src/validar_dados.py

# Carregar no banco
python src/carregar_postgres.py

# Treinar modelo ML
python src/treinar_modelo.py

# Executar Assistente RAG e Testes
python src/rag_assistant.py
pytest tests/test_rag_assistant.py
```

---

## Detalhes das Fases Concluídas

### Fase 3: Pipeline para PostgreSQL
- Modelagem da tabela `inspecoes` com índices de performance.
- Consultas analíticas salvas em `sql/consultas_analiticas.sql` (taxa de defeito por turno, produto e evolução mensal).

### Fase 4: Machine Learning
- **Modelos:** Regressão Logística (Baseline) e Random Forest (Principal).
- **Sinal Aprendido:** A feature `turno_noturno` foi a 2ª mais importante, confirmando a calibração dos dados.
- **Modelo Salvo:** Artefato gerado em `models/modelo_rf.joblib`.
- **Limitações:** Documentadas em `docs/limitacoes.md`.

### Fase 5: Assistente RAG com LLMs Locais
- **Indexação Vetorial:** Uso de `FAISS` e embeddings locais (`sentence-transformers/all-MiniLM-L6-v2`).
- **Geração Local:** Integração com Hugging Face Pipeline (`google/flan-t5-small`).
- **Segurança Documental:** Camada de controle de escopo e regras determinísticas para dados críticos (códigos de defeito e limites dimensionais) antes do uso de IA generativa.
- **Testes Automatizados:** Suíte completa em `tests/test_rag_assistant.py` cobrindo cenários de escopo, recusa e validação.

---

## Estrutura do Repositório

```text
industrial-quality-monitor/
├── data/                  # (raw/ e processed/ não versionados)
├── src/
│   ├── gerar_dados.py
│   ├── validar_dados.py
│   ├── carregar_postgres.py
│   ├── treinar_modelo.py
│   ├── rag_assistant.py
│   └── api.py
├── sql/
│   ├── schema.sql
│   └── consultas_analiticas.sql
├── docs/
│   ├── procedimentos/     # Documentação técnica em Markdown
│   ├── arquitetura.md
│   └── limitacoes.md
├── tests/
│   └── test_rag_assistant.py
├── models/                # (não versionado)
├── .gitignore
├── .env
├── README.md
├── requirements.txt
└── Dockerfile
```

---

## Decisões Técnicas Importantes

- **Seed fixa (42):** Reprodutibilidade obrigatória.
- **Sinal intencional no turno noturno:** Permite que o modelo de ML aprenda algo útil.
- **Stack 100% local e gratuita:** Zero dependência de API paga.
- **Dados sintéticos:** Elimina risco de vazamento de informação confidencial.
- **Credenciais via `.env`:** Segurança e boas práticas.

---

## Regras de Uso de IA (Obrigatórias)

1. Antes de gerar código -> pedir explicação da tarefa e dos componentes.
2. Durante -> alterações pequenas, justificadas e verificáveis.
3. Depois -> executar e testar localmente.
4. Ao finalizar -> explicar com as próprias palavras o que o código faz.

> *Se você não consegue explicar uma linha sem consultar a IA, essa linha ainda não é sua.*

---

## Licença

MIT