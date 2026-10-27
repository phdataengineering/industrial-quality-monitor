# Arquitetura — Industrial Quality Monitor

## Fluxo de dados

```text
Gerador sintético -> validação Pandas -> CSV validado -> PostgreSQL
                                           |                 (análises SQL)
                                           -> treino ML -> artefato joblib -> API /predict
Procedimentos Markdown -> embeddings Hugging Face + FAISS -> API /rag/ask
Usuário -> Streamlit (simulador e procedimentos) -> API FastAPI
```

## Responsabilidades e operação

- O PostgreSQL armazena inspeções para consultas analíticas. A API não consulta o banco durante uma predição: ela carrega o pipeline ML do arquivo `models/modelo_rf.joblib`.
- O Docker constrói esse artefato de forma reproduzível a partir dos dados sintéticos fixos do repositório. Fora do Docker, gere, valide e treine os dados antes de iniciar a API.
- O endpoint RAG inicializa embeddings e o modelo de geração no primeiro pedido `/rag/ask`. Health checks não fazem downloads.
- `/health` mede liveness; `/ready` retorna 503 enquanto o modelo ML não estiver carregado.
- A interface Streamlit tem duas abas, chama a API internamente por `http://industrial-api:8000` no Compose e é publicada localmente em `http://localhost:8501`.
- O Compose inicia frontend, API e PostgreSQL. A inicialização do frontend aguarda a prontidão da API. O schema SQL é aplicado pelo entrypoint do PostgreSQL quando o volume é criado pela primeira vez. A carga do CSV é feita pelo script `src/carregar_postgres.py`.

## Segurança e persistência

- `.dockerignore` impede que `.env`, `.git`, dados e artefatos locais sejam copiados para o contexto de build.
- Portas do Compose escutam apenas em `127.0.0.1` por padrão.
- A carga SQL apaga e recarrega linhas dentro de uma transação, sem recriar a tabela nem remover constraints e índices.
- O container da API roda sem privilégios de root.
- O container Streamlit também roda sem root; perguntas são limitadas e respostas do RAG são exibidas como texto sem interpretação de HTML/Markdown.
- O cliente HTTP tem timeouts explícitos e não registra payloads nem respostas dos usuários.
- O artefato ML registra versão, seed, features e threshold junto ao pipeline para facilitar rastreabilidade.
- O índice vetorial usa FAISS no container Linux; no Windows há uma busca exata NumPy para contornar incompatibilidades da DLL nativa.
- Use somente dados sintéticos neste projeto. Os modelos e regras são demonstrativos, não destinados a decisões de produção.
