# Engenharia de Prompt para Claude Code
## Projeto: Industrial Quality Monitor

Este documento define como interagir com o **Claude Code** de forma eficiente, segura e alinhada ao objetivo de aprendizado real.

---

## 1. Arquivo de contexto permanente

O arquivo `CLAUDE.md` na raiz do projeto deve ser a fonte de verdade.  
O Claude Code lê esse arquivo automaticamente em muitos fluxos. Mantenha-o atualizado.

---

## 2. Template de início de sessão (cole no chat)

```markdown
Fase atual: [1 | 2 | 3 | 4 | 5 | 6]
Objetivo desta sessão: [1 frase clara e específica]

Situação atual:
- Já existe: [liste arquivos ou o que já funciona]
- Problema / erro atual: [cole o erro se houver]
- O que já tentei: [breve]

Pedidos:
1. Explique o que precisa ser feito e por quê
2. Liste os componentes necessários
3. Proponha a ordem de implementação em passos pequenos
4. Só gere código do primeiro passo depois que eu confirmar
```

---

## 3. Padrões de prompt de alta qualidade

### Bom prompt (exemplo)
```
Estou na Fase 2.
Objetivo: implementar a regra "se defeito = 'sim' então tipo_defeito deve estar preenchido".

Já tenho o arquivo src/validar_dados.py com a estrutura básica.
Quero que você:
1. Explique a melhor forma de implementar essa validação com Pandas
2. Mostre só a função responsável por essa regra
3. Me diga como testar isoladamente
```

### Mau prompt (evite)
```
Faz a validação completa dos dados pra mim.
```

---

## 4. Comandos úteis de controle

| Situação                        | Prompt recomendado                                      |
|--------------------------------|---------------------------------------------------------|
| IA está gerando código demais  | "Pare. Explique primeiro sem código."                   |
| Quero só análise               | "Não gere código. Apenas analise e proponha opções."    |
| Quero um passo por vez         | "Implemente apenas o passo 1. Espere minha confirmação."|
| Quero testar entendimento      | "Faça 3 perguntas socráticas sobre o que acabamos de fazer." |
| IA sugeriu ferramenta fora do escopo | "Isso está fora da fase atual. Fique apenas com a stack permitida." |

---

## 5. Checklist antes de enviar qualquer prompt

- [ ] Informei a **fase atual**?
- [ ] O objetivo da sessão está em **uma frase**?
- [ ] Limitei o que a IA **não** deve fazer?
- [ ] Pedi **explicação antes** do código?
- [ ] Tenho como **testar** o que ela vai devolver?

---

## 6. Fluxo ideal de uma sessão de 45–60 minutos

1. Colar o template de início de sessão
2. Pedir explicação + componentes
3. Confirmar a abordagem
4. Receber e implementar o primeiro pedaço de código
5. Rodar localmente e colar o resultado/erro
6. Ajustar
7. No final: responder às perguntas socráticas

---

## 7. O que nunca pedir ao Claude Code neste projeto

- "Gera o projeto inteiro"
- "Faz a Fase X completa"
- "Melhora tudo"
- "Cria a arquitetura ideal" (já está definida)
- Sugestões de Airflow, Kafka, Kubernetes, cloud paga (fora do escopo)

---

## 8. Atualização do CLAUDE.md

Sempre que uma decisão técnica importante for tomada (ex: escolha entre FAISS ou Chroma, mudança de schema, etc.), atualize o `CLAUDE.md` para que as próximas sessões mantenham consistência.
