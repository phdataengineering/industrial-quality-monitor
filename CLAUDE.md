# Instruções para Claude Code — Industrial Quality Monitor

## Contexto do autor
- Nível de programação: iniciante a intermediário inicial
- Tempo: até 1 hora por dia
- Orçamento: ferramentas locais e gratuitas
- Hardware: Windows 11 + WSL2, Intel i7 10ª geração, 16 GB RAM, GTX 1650 4 GB

## Stack atual
- Dados e ETL: Python, Pandas, pytest
- Banco: PostgreSQL, psycopg2, SQLAlchemy
- ML: Scikit-learn e joblib
- RAG: LangChain Core, langchain-text-splitters e langchain-huggingface; FAISS via `faiss-cpu` diretamente. Não usar `langchain-community` (descontinuado).
- API: FastAPI e Docker
- Interface de demonstração: Streamlit em container independente, chamando a API via `API_BASE_URL`

## Segurança e dados
- Use somente dados sintéticos.
- Nunca versionar `.env`, credenciais, dumps, dados gerados ou artefatos de modelo.
- O `.dockerignore` deve excluir credenciais e dados locais do build.
- Não exponha detalhes internos de exceções pela API.

## Forma de trabalho
- Explique mudanças em português claro e em blocos pequenos.
- Justifique as decisões e execute verificações solicitadas pelo usuário.
- Ao concluir, resuma o comportamento e as limitações das alterações.

## Objetivo
Construir um portfólio reprodutível e compreender cada componente antes de apresentá-lo.
