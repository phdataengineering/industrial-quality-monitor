# 1. Atualiza o README.md com o status da Fase 3
@"
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

Fonte sintética -> Validação (Pandas) -> PostgreSQL
                                      -> ML (Scikit-learn) -> API FastAPI
                                      -> RAG (LangChain + embeddings locais)

---

## Status atual

| Fase | Nome                          | Status      |
|------|-------------------------------|-------------|
| 1    | Estrutura + Dados sintéticos  | Concluída   |
| 2    | Validação e ETL com Pandas    | Concluída   |
| 3    | Pipeline -> PostgreSQL         | Concluída   |
| 4    | Machine Learning              | Pendente    |
| 5    | LLMs + RAG                    | Pendente    |
| 6    | API + Docker                  | Pendente    |

---

## Como rodar (Fases 1 a 3)

### Pré-requisitos
- Python 3.11+
- Ambiente virtual
- PostgreSQL instalado e rodando localmente

### Configuração do Banco de Dados (Fase 3)
1. Crie um banco de dados no PostgreSQL chamado `industrial_quality`.
2. Crie um arquivo `.env` na raiz do projeto com as credenciais:
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=industrial_quality
   DB_USER=postgres
   DB_PASSWORD=sua_senha_aqui
3. Execute o script SQL `sql/schema.sql` no Query Tool do pgAdmin para criar a tabela `inspecoes`.

### Executando o Pipeline
1. Gerar os dados: `python src/gerar_dados.py`
2. Validar os dados: `python src/validar_dados.py`
3. Carregar no banco: `python src/carregar_postgres.py`

---

## Fase 3: Detalhes do Pipeline

### Modelagem da Tabela `inspecoes`
- `id_ordem` (VARCHAR): Chave primária
- `data` (DATE): Data da inspeção
- `produto` (VARCHAR): Código do produto
- `turno` (VARCHAR): Turno (diurno, tarde, noturno)
- `operador` (VARCHAR): Código do operador
- `quantidade_inspecionada` (INTEGER)
- `defeito` (VARCHAR): 'sim' ou 'nao'
- `tipo_defeito` (VARCHAR)
- `quantidade_defeito` (INTEGER)

### Estrutura do repositório
industrial-quality-monitor/
├── data/ (raw/ e processed/ não versionados)
├── src/
│   ├── gerar_dados.py
│   ├── validar_dados.py
│   ├── carregar_postgres.py
│   ├── treinar_modelo.py
│   ├── rag_assistant.py
│   └── api.py
├── sql/schema.sql
├── docs/
├── tests/
├── .gitignore
├── .env
├── README.md
└── requirements.txt

---

## Regras de uso de IA (obrigatórias)
1. Antes de gerar código -> pedir explicação da tarefa e dos componentes
2. Durante -> alterações pequenas, justificadas e verificáveis
3. Depois -> executar e testar localmente
4. Ao finalizar -> explicar com as próprias palavras o que o código faz

> Se você não consegue explicar uma linha sem consultar a IA, essa linha ainda não é sua.

---

## Licença
MIT
"@ | Out-File -FilePath README.md -Encoding utf8

# 2. Adiciona todos os arquivos modificados ao Git
git add .

# 3. Faz o commit com a mensagem da Fase 3
git commit -m "docs: atualiza README com status das fases 1 a 3 e instrucoes do PostgreSQL"

# 4. Envia para o GitHub
git push