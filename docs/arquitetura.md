# Arquitetura — Industrial Quality Monitor

## Visão geral do fluxo de dados

```
┌─────────────────────────────────────┐
│  Fonte Sintética                    │
│  src/gerar_dados.py                 │
│  → data/raw/inspecoes.csv           │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Ingestão e Validação (Pandas)      │
│  src/validar_dados.py               │
│  → data/processed/dados_validos.csv │
│  → data/processed/inconsistencias.csv│
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Persistência                       │
│  sql/schema.sql                     │
│  src/carregar_postgres.py           │
│  → PostgreSQL (tabela inspecoes)    │
└────────────┬────────────┬───────────┘
             │            │
             ▼            ▼
┌──────────────────┐  ┌──────────────────────────┐
│  Machine Learning│  │  RAG                     │
│  Scikit-learn    │  │  LangChain + embeddings  │
│  → modelo.joblib │  │  → índice vetorial       │
└────────┬─────────┘  └────────────┬─────────────┘
         │                         │
         └────────────┬────────────┘
                      ▼
         ┌─────────────────────────┐
         │  API (FastAPI)          │
         │  POST /predict          │
         │  POST /ask              │
         └─────────────────────────┘
```

## Princípios de design

1. **Progressão incremental** — cada fase reutiliza a anterior
2. **Reprodutibilidade** — seed fixa + scripts determinísticos
3. **Local-first** — zero dependência de serviços pagos
4. **Honestidade** — limitações documentadas (dados sintéticos)
5. **Aprendizado real** — código deve ser compreendido, não apenas executado
