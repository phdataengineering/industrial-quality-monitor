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

```
Fonte sintética → Validação (Pandas) → PostgreSQL
                                      ↘
                                       ML (Scikit-learn) → API FastAPI
                                      ↗
                               RAG (LangChain + embeddings locais)
```

---

## Status atual

| Fase | Nome                          | Status      |
|------|-------------------------------|-------------|
| 1    | Estrutura + Dados sintéticos  | Em andamento |
| 2    | Validação e ETL com Pandas    | Pendente    |
| 3    | Pipeline → PostgreSQL         | Pendente    |
| 4    | Machine Learning              | Pendente    |
| 5    | LLMs + RAG                    | Pendente    |
| 6    | API + Docker                  | Pendente    |

---

## Como rodar (Fase 1)

### Pré-requisitos
- Python 3.11+
- Ambiente virtual

```bash
# Criar e ativar venv
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / WSL
source .venv/bin/activate

# Instalar dependências mínimas da Fase 1
pip install pandas
```

### Gerar os dados

```bash
python src/gerar_dados.py
```

Saída esperada:
- ~1000 registros
- Taxa global de defeito ≈ 10%
- Turno noturno com taxa mais alta que o diurno
- Arquivo gerado em `data/raw/inspecoes.csv`

---

## Estrutura do repositório

```
industrial-quality-monitor/
├── data/
│   ├── raw/              # CSV sintético (não versionado)
│   └── processed/        # dados validados (não versionado)
├── src/
│   ├── gerar_dados.py    # Fase 1
│   ├── validar_dados.py  # Fase 2
│   ├── carregar_postgres.py
│   ├── treinar_modelo.py
│   ├── rag_assistant.py
│   └── api.py
├── sql/
│   └── schema.sql
├── docs/
│   ├── procedimentos/    # documentos para RAG
│   ├── arquitetura.md
│   └── limitacoes.md
├── tests/
├── notebooks/
├── .gitignore
├── README.md
├── requirements.txt
└── Dockerfile
```

---

## Decisões técnicas importantes

- **Seed fixa (42)** → reprodutibilidade obrigatória
- **Sinal intencional no turno noturno** → permite que o modelo de ML aprenda algo útil
- **Stack 100% local e gratuita** → zero dependência de API paga
- **Dados sintéticos** → elimina risco de vazamento de informação confidencial

---

## Regras de uso de IA (obrigatórias)

1. Antes de gerar código → pedir explicação da tarefa e dos componentes
2. Durante → alterações pequenas, justificadas e verificáveis
3. Depois → executar e testar localmente
4. Ao finalizar → explicar com as próprias palavras o que o código faz

> Se você não consegue explicar uma linha sem consultar a IA, essa linha ainda não é sua.

---

## Licença

MIT
