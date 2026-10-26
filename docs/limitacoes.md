# Limitações do Modelo de Machine Learning

Este documento detalha as limitações do modelo preditivo treinado na Fase 4 do projeto.

## 1. Natureza dos Dados
- **Dados Sintéticos:** Os dados foram gerados artificialmente com sementes fixas. Eles não capturam a complexidade, os ruídos e as variáveis ocultas de um ambiente industrial real.
- **Sinal Intencional:** A maior taxa de defeitos no turno noturno foi inserida deliberadamente para que o modelo tivesse um padrão para aprender. Em dados reais, a causa raiz pode ser multifatorial (fadiga, iluminação, manutenção).

## 2. Desbalanceamento de Classes
- A taxa global de defeitos é de aproximadamente 10%. Isso cria um forte desbalanceamento (90% "Sem Defeito" vs 10% "Com Defeito").
- **Impacto:** O modelo Random Forest, ao tentar maximizar o Recall (achar todos os defeitos), gerou uma alta taxa de Falsos Positivos (121 em 200 amostras de teste). Na prática, isso faria a linha de produção parar desnecessariamente.
- **O Baseline:** Curiosamente, a Regressão Logística teve um desempenho geral mais equilibrado (F1-Score de 0.29) do que a Random Forest ajustada (F1-Score de 0.24), demonstrando que modelos mais simples podem ser mais robustos em cenários com ruído.

## 3. Uso em Produção
- **Não utilizar para decisões reais:** Este modelo é estritamente educacional.
- Em um cenário real, técnicas como **SMOTE** (Synthetic Minority Over-sampling Technique) ou ajuste fino de `scale_pos_weight` no XGBoost seriam necessárias para equilibrar as classes sem gerar tantos falsos positivos.

## 4. Importância das Features
- A feature `quantidade_inspecionada` dominou a importância (43%). Isso pode indicar que o modelo está usando o tamanho do lote como um "atalho" para prever a probabilidade de defeito, em vez de aprender as características intrínsecas do produto.
- O `turno_noturno` ficou em 2º lugar (6.4%), confirmando que o sinal de qualidade foi capturado.