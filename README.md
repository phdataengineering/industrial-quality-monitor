# Industrial Quality Monitor

Pipeline demonstrativo de dados de inspeção de qualidade industrial, com preparação e validação de dados, armazenamento em PostgreSQL, análises SQL e experimentação com modelos de Machine Learning para classificação de defeitos.

> **Projeto de portfólio:** Engenharia de Dados e fundamentos de Engenharia de IA.  
> **Dados:** sintéticos, gerados para fins educacionais.  
> **Uso:** demonstração e aprendizado; não utilizar os resultados para decisões industriais reais.  
> **Independência:** projeto pessoal, sem vínculo, endosso ou uso de dados de qualquer empregador.

---

## 1. Objetivos

O projeto demonstra, de forma incremental e reproduzível, etapas de um fluxo de dados industrial:

- geração e organização de dados sintéticos;
- validação e preparação dos dados com Python e Pandas;
- carga de dados em banco relacional PostgreSQL;
- consultas SQL para análise de defeitos por turno, produto e período;
- experimentação com modelos clássicos de Machine Learning;
- documentação de resultados, limitações e próximos passos.

A proposta é evoluir o pipeline por fases, sem apresentar funcionalidades planejadas como se já estivessem implementadas.

## 2. Arquitetura geral

```text
Dados sintéticos
      |
      v
Geração e preparação (Python)
      |
      v
Validação e transformação (Pandas)
      |
      v
PostgreSQL
      |
      +----> Consultas analíticas SQL
      |
      +----> Experimentos de Machine Learning (scikit-learn)
                    |
                    v
             Avaliação e documentação

Etapas futuras planejadas:
PostgreSQL -> API (FastAPI)
Documentos técnicos -> recuperação contextual (RAG) -> assistente
Empacotamento e execução reproduzível com Docker
```

A arquitetura acima distingue as etapas já desenvolvidas das evoluções planejadas. A implementação de API, RAG e Docker depende das fases futuras do projeto.

## 3. Status do projeto

| Fase | Entrega | Status |
|---|---|---|
| 1 | Estrutura inicial e geração de dados sintéticos | Concluída |
| 2 | Validação e preparação dos dados com Pandas | Concluída |
| 3 | Carga do conjunto validado no PostgreSQL | Concluída |
| 4 | Experimentos iniciais de Machine Learning e avaliação | Em desenvolvimento / resultados experimentais documentados |
| 5 | Assistente de consulta a documentos técnicos com RAG | Planejada |
| 6 | API e empacotamento com Docker | Planejada |

> Atualize esta tabela sempre que uma fase for efetivamente concluída e testada. Não marque uma etapa como concluída apenas porque seus arquivos foram criados.

## 4. Tecnologias

- **Python 3.11+** — geração e processamento de dados;
- **Pandas** — validação e transformação tabular;
- **PostgreSQL** — persistência relacional;
- **SQL** — consultas analíticas;
- **scikit-learn** — experimentos de classificação;
- **Git e GitHub** — versionamento e documentação.

FastAPI, Docker, LangChain e componentes de RAG são tecnologias previstas para etapas futuras; não devem ser interpretadas como funcionalidades já entregues.

## 5. Estrutura do repositório

Estrutura esperada com base nos componentes documentados do projeto:

```text
industrial-quality-monitor/
├── data/
│   ├── raw/                 # Dados sintéticos de origem (não versionados, se configurado)
│   └── processed/           # Dados preparados (não versionados, se configurado)
├── src/
│   ├── gerar_dados.py
│   ├── validar_dados.py
│   ├── carregar_postgres.py
│   ├── treinar_modelo.py    # Usado na fase de experimentação de ML, se presente
│   ├── rag_assistant.py     # Etapa planejada ou em desenvolvimento, se presente
│   └── api.py               # Etapa planejada ou em desenvolvimento, se presente
├── sql/
│   ├── schema.sql
│   └── consultas_analiticas.sql
├── docs/
│   └── limitacoes.md
├── tests/
├── .gitignore
├── requirements.txt
└── README.md
```

A árvore é uma referência documental: confirme os arquivos existentes no repositório antes de considerar todos os itens implementados. O arquivo `.env` deve ser criado localmente e **não deve ser enviado ao Git**.

## 6. Pré-requisitos

- Python 3.11 ou superior;
- PostgreSQL instalado e em execução;
- Git;
- ambiente virtual Python;
- dependências listadas em `requirements.txt`.

Os comandos abaixo pressupõem execução a partir da raiz do repositório e que os nomes dos scripts correspondam aos arquivos existentes.

## 7. Configuração do ambiente

### 7.1 Criar e ativar um ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No Linux ou WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 7.2 Configurar o PostgreSQL

Crie um banco de dados chamado `industrial_quality`. Em seguida, crie um arquivo `.env` na raiz do projeto com os parâmetros de conexão:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=industrial_quality
DB_USER=postgres
DB_PASSWORD=SUBSTITUA_PELA_SUA_SENHA
```

Substitua o valor de exemplo pela senha local do PostgreSQL. Não compartilhe credenciais nem as inclua em commits, capturas de tela públicas ou logs.

O código precisa carregar essas variáveis de ambiente para que a configuração seja aplicada. Verifique o mecanismo utilizado pelos scripts e as dependências instaladas antes de executar o pipeline.

### 7.3 Criar a tabela

Execute o conteúdo de `sql/schema.sql` no banco `industrial_quality`, por exemplo, usando o Query Tool do pgAdmin ou o cliente `psql`.

Confira o esquema real antes da carga. A tabela `inspecoes` deve ser compatível com as colunas esperadas pelo script de carregamento.

## 8. Executar o pipeline de dados

Execute as etapas na ordem abaixo, a partir da raiz do projeto:

```bash
python src/gerar_dados.py
python src/validar_dados.py
python src/carregar_postgres.py
```

1. **Geração:** cria os registros sintéticos usados no experimento.
2. **Validação:** verifica e prepara os dados antes da carga.
3. **Carga:** grava os registros validados no PostgreSQL.

Os nomes e formatos dos arquivos de entrada e saída dependem da implementação atual dos scripts. Se ocorrer um erro, confirme os caminhos configurados, a existência dos arquivos gerados, a conexão com o banco e a correspondência entre o esquema SQL e os dados.

## 9. Modelo de dados

A tabela `inspecoes` representa registros sintéticos de inspeção. As colunas documentadas para o projeto são:

| Campo | Tipo lógico | Descrição |
|---|---|---|
| `id_ordem` | Texto | Identificador da ordem ou registro; verificar no `schema.sql` se é a chave primária |
| `data` | Data | Data da inspeção |
| `produto` | Texto | Código ou identificador sintético do produto |
| `turno` | Texto | Turno de produção, por exemplo: diurno, tarde ou noturno |
| `operador` | Texto | Identificador sintético do operador |
| `quantidade_inspecionada` | Inteiro | Quantidade de unidades inspecionadas |
| `defeito` | Texto/categoria | Indicador de defeito, representado por `sim` ou `nao` |
| `tipo_defeito` | Texto/categoria | Categoria do defeito, quando aplicável |
| `quantidade_defeito` | Inteiro | Quantidade de unidades defeituosas registrada |

Os tipos físicos, restrições, nulabilidade e chaves efetivas são definidos em `sql/schema.sql`. Essa documentação não substitui a inspeção do esquema implementado.

## 10. Consultas analíticas SQL

O arquivo `sql/consultas_analiticas.sql` reúne consultas para investigar:

- taxa de defeitos por turno;
- taxa de defeitos por produto;
- evolução mensal da taxa de defeitos.

As consultas calculam a proporção de **registros de inspeção marcados com defeito** sobre o total de registros em cada grupo. Isso não é necessariamente a mesma métrica que a proporção de unidades defeituosas sobre unidades inspecionadas. Para calcular uma taxa por unidade, a fórmula deve utilizar `quantidade_defeito` e `quantidade_inspecionada`, conforme as regras de negócio e a qualidade dos dados.

As consultas usam funções compatíveis com PostgreSQL, como `TO_CHAR` para agrupar datas por mês. Execute-as no banco após a carga dos dados e valide os resultados antes de utilizá-los em gráficos ou relatórios.

## 11. Machine Learning: experimento e interpretação

A fase de Machine Learning explora a classificação de registros de inspeção em função da presença de defeito. O objetivo é aprender o processo de preparação, treinamento, avaliação e interpretação de modelos, não produzir um sistema pronto para operação industrial.

Resultados experimentais registrados durante o desenvolvimento:

- a proporção global de registros com defeito é de aproximadamente 10%, conforme o conjunto sintético usado no experimento;
- a Regressão Logística apresentou F1-score de 0,29;
- a Random Forest ajustada para priorizar recall apresentou F1-score de 0,24 e maior ocorrência de falsos positivos no experimento;
- a importância de atributos indicou `quantidade_inspecionada` em aproximadamente 43% e `turno_noturno` em aproximadamente 6,4%, segundo a execução documentada.

Esses valores são resultados de um experimento específico, não garantias de desempenho futuro. Eles devem ser recalculados quando os dados, a divisão treino/teste, as variáveis ou os parâmetros do modelo forem alterados. Consulte `docs/limitacoes.md` para a interpretação e as restrições conhecidas.

### Métricas que merecem atenção

- **Precision:** entre os registros sinalizados como defeituosos, quantos realmente pertencem à classe positiva.
- **Recall:** entre os registros realmente defeituosos, quantos o modelo identificou.
- **F1-score:** média harmônica entre precision e recall.
- **Matriz de confusão:** mostra verdadeiros positivos, falsos positivos, verdadeiros negativos e falsos negativos.

Em contexto industrial, falsos positivos podem provocar inspeções desnecessárias; falsos negativos podem deixar defeitos passarem despercebidos. A escolha do limiar de classificação deve considerar os custos de cada tipo de erro e ser validada com especialistas e dados representativos.

## 12. Limitações conhecidas

1. **Dados sintéticos:** não representam toda a variabilidade, os ruídos, as dependências e as variáveis ocultas de uma operação industrial real.
2. **Padrões introduzidos artificialmente:** a maior taxa de defeitos no turno noturno foi inserida deliberadamente nos dados para permitir que o experimento investigasse esse padrão. O modelo pode aprender uma relação criada pela própria simulação.
3. **Desbalanceamento de classes:** uma proporção aproximada de 90% de registros sem defeito e 10% com defeito pode dificultar a avaliação e favorecer métricas aparentemente boas em modelos pouco úteis.
4. **Risco de falsos positivos:** ajustar um modelo para aumentar o recall pode aumentar a quantidade de alertas incorretos.
5. **Importância de atributos não é causalidade:** a importância estimada para `quantidade_inspecionada` ou `turno_noturno` não prova que esses fatores causam defeitos. É necessário verificar vazamento de dados, correlações artificiais e adequação das variáveis.
6. **Sem validação operacional:** os resultados não foram estabelecidos como evidência de eficácia em uma linha de produção real.

Técnicas como ponderação de classes, ajuste de limiar e reamostragem podem ser investigadas, mas nenhuma delas garante melhora. Métodos como SMOTE devem ser aplicados somente aos dados de treinamento, dentro do processo de validação, para evitar vazamento de informação. Consulte `docs/limitacoes.md` para detalhes adicionais.

**Não utilize este modelo para liberar ou bloquear lotes, interromper linhas, aprovar produtos ou tomar decisões de qualidade reais.** Qualquer uso operacional exigiria dados representativos, validação independente, monitoramento, governança e aprovação dos responsáveis pelo processo.

## 13. Segurança e boas práticas

- Mantenha `.env`, senhas, tokens e outras credenciais fora do controle de versão.
- Use dados sintéticos e identificadores fictícios nos exemplos públicos.
- Evite executar scripts sem compreender suas entradas, saídas e efeitos.
- Valide os dados antes de gravá-los no banco.
- Registre as versões das dependências e os parâmetros relevantes dos experimentos.
- Não apresente resultados sintéticos como evidências de desempenho industrial real.
- Faça alterações pequenas, execute os testes disponíveis e documente limitações conhecidas.

## 14. Testes e reprodutibilidade

Execute os testes existentes com:

```bash
python -m pytest
```

O comando pressupõe que `pytest` esteja instalado e que existam testes compatíveis no diretório `tests/`. Se ainda não houver testes implementados, registre isso como trabalho pendente em vez de afirmar que a suíte passou.

Para tornar os experimentos reproduzíveis, documente a origem sintética dos dados, as sementes aleatórias utilizadas, a versão das bibliotecas, a estratégia de divisão dos dados e os parâmetros dos modelos. Reexecute o pipeline completo sempre que alterar a geração, a validação ou o esquema.

## 15. Uso de IA durante o desenvolvimento

A IA generativa pode apoiar explicações, revisão, depuração e elaboração de testes, mas não substitui a compreensão e a verificação do código.

1. Antes de implementar, entenda o problema e os componentes envolvidos.
2. Faça alterações pequenas e justificadas.
3. Execute o código e os testes localmente.
4. Revise os resultados, as mensagens de erro e os efeitos sobre os dados.
5. Explique com suas próprias palavras o que foi implementado e quais são suas limitações.

> O objetivo do portfólio é demonstrar aprendizado verificável. Código sugerido por IA só deve ser considerado concluído depois de revisado, executado e compreendido.

## 16. Roadmap

- [x] Estrutura inicial e geração de dados sintéticos
- [x] Validação e preparação com Pandas
- [x] Persistência no PostgreSQL
- [ ] Consolidar testes automatizados e validações de qualidade dos dados
- [ ] Reforçar a avaliação de Machine Learning, incluindo validação adequada e análise de erros
- [ ] Implementar e documentar o assistente RAG para procedimentos técnicos
- [ ] Expor funcionalidades por uma API FastAPI
- [ ] Empacotar os serviços com Docker e documentar a execução local

Os itens marcados como concluídos devem ser mantidos somente enquanto refletirem o estado verificável do repositório.

## 17. Licença

O repositório declara a licença MIT. Confirme a existência de um arquivo `LICENSE` válido e mantenha o texto da licença consistente com essa declaração. Se o arquivo de licença ainda não estiver presente, adicione-o antes de afirmar que o projeto está formalmente licenciado sob MIT.

---

**Autor:** `phdataengineering`  
**Repositório:** https://github.com/phdataengineering/industrial-quality-monitor
