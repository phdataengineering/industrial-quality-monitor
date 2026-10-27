# Limitações do Modelo de Machine Learning

Este documento detalha as limitações do modelo preditivo treinado na Fase 4 do projeto.

## 1. Natureza dos Dados
- **Dados Sintéticos:** Os dados foram gerados artificialmente com sementes fixas. Eles não capturam a complexidade, os ruídos e as variáveis ocultas de um ambiente industrial real.
- **Sinal Intencional:** A maior taxa de defeitos no turno noturno foi inserida deliberadamente para que o modelo tivesse um padrão para aprender. Em dados reais, a causa raiz pode ser multifatorial (fadiga, iluminação, manutenção).

## 2. Desbalanceamento de Classes
- A taxa global de defeitos é de aproximadamente 10%. Isso cria um forte desbalanceamento (90% "Sem Defeito" vs 10% "Com Defeito").
- **Métrica de referência (seed 42, split estratificado 80/20, threshold 0,5):** a execução validada produziu 27 exemplos positivos no teste. A Random Forest encontrou 6 (recall 0,22), com 48 falsos positivos e F1 de 0,15 para a classe positiva. A regressão logística teve F1 de 0,29. As métricas podem variar entre versões de bibliotecas.
- **Threshold:** o valor de 0,5 é fixo e também é salvo com o pipeline. O conjunto de teste não é usado para escolher threshold, evitando vazamento da avaliação.

## 3. Uso em Produção
- **Não utilizar para decisões reais:** Este modelo é estritamente educacional.
- Em um cenário real, técnicas como **SMOTE** (Synthetic Minority Over-sampling Technique) ou ajuste fino de `scale_pos_weight` no XGBoost seriam necessárias para equilibrar as classes sem gerar tantos falsos positivos.

## 4. Importância das Features
- Na execução validada, `quantidade_inspecionada` dominou a importância (43%). Isso pode indicar que o modelo usa o tamanho do lote como atalho, em vez de aprender características intrínsecas do produto.
- `turno_noturno` ficou em 2º lugar (6,5%), refletindo o sinal sintético inserido nos dados.
