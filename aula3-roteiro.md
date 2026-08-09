---
layout: default
title: "Aula 3 — Roteiro (fonte)"
---

# Aula 3 — Modelagem de Domínio e Decisões Arquiteturais (SDD na prática)
## Roteiro de condução (~120 min)

> **Duração-alvo:** 2h — já desenhado para 2h de profundidade real.
> **Callback obrigatório:** a Aula 2 terminou com uma confissão — as fronteiras do monólito foram desenhadas "no olho". Esta aula conserta isso com técnica.
> **Companions:** `topologia-progressiva.html` (a Camada 3 se refina aqui) · `aula3-perguntas-dificeis.md`.
> **O insight-chave da aula:** o ponto quente que derrubou o sistema na Aula 2 era um **agregado grande demais** — problema de modelagem que se manifestou como problema de banco. Não perca esse momento (Bloco 6).

## Visão de relance

| Bloco | Tempo | Título | O que construir no Excalidraw |
|---|---|---|---|
| 1 | 0–8 | Cold open: o substantivo errado | Só a cena |
| 2 | 8–20 | DDD essencial | Vocabulário (sem diagrama) |
| 3 | 20–42 | Event Storming ao vivo do Pix | Diagrama 2 — rio de eventos |
| 4 | 42–56 | Contextos emergem + Context Map | Diagramas 3 e 4 |
| 5 | 56–66 | Fronteira de consistência | Diagrama 5 — agregado Ledger |
| 6 | 66–84 | **As 4 regras de agregado + o trade-off que liga à Aula 2** | Diagrama 6 — grande vs pequeno |
| 7 | 84–94 | **Versionamento de eventos** | Diagrama 7 — evolução de schema |
| 8 | 94–106 | SDD: spec + Context Engineering | Diagramas 8 e 9 |
| 9 | 106–116 | **Bounded context = microsserviço?** | Critérios de extração |
| 10 | 116–120 | Fecho e ponte | Recap |

---

## Bloco 1 · [0–8] · Cold open: o substantivo errado

- **Conduza:** a história do Diego (Antifraude, "conta" = identidade) e da Marina (Pagamentos, "conta" = sub-carteira). Cliente com duas carteiras dobra o limite diário sem disparar alerta.
- **Fala-âncora:** "Ninguém mentiu, ninguém foi descuidado. O bug morava **entre** os dois times, onde a mesma palavra significava duas coisas."
- **Pergunte:** "Quem já viveu uma versão disso?" (colha 1-2 relatos reais).
- **Armadilha:** não corrija ainda com "o certo seria usar uma palavra só" — a solução real (fronteira explícita, não uniformização) vem no Bloco 2.

---

## Bloco 2 · [8–20] · DDD essencial

- **Fala-chave:** "A solução não é todo mundo usar a mesma palavra. É saber **onde** uma palavra muda de significado, e desenhar uma fronteira ali."
- **Sequência:** linguagem ubíqua (vale dentro de um contexto) → bounded context → agregado (callback à invariante do ledger) → evento de domínio (nomeado no passado).
- **Pergunte:** "O erro do Diego e da Marina foi ter duas definições de 'conta'?" (não — foi não **saber** que existiam duas).
- **Armadilha:** não deixe DDD virar "documentar tudo". O ponto é fronteira explícita.

---

## Bloco 3 · [20–42] · Event Storming ao vivo (o exercício-estrela)

**Objetivo:** descobrir os contextos a partir dos eventos, ao vivo — não impor de cima.

- **Adicione os eventos no Excalidraw, um por um, no passado:** `PixIniciado → ChaveResolvida → LimitesValidados → FundosReservados → OrdemEnviadaAoSPI → PixLiquidado → (ramo) PixDevolvido`.
- **A cada evento, pergunte:** "quem, na organização, cuida disso?" — deixe a turma responder **antes** de você.
- **Fala-chave:** "Eu não decidi essa divisão antes de entrar na sala. Ela emergiu dos eventos — é isso que faz o event storming mais confiável que um palpite educado."
- **Armadilha:** resista a entregar os contextos prontos. O valor está em deixar a turma errar e ajustar ao vivo.
- **Dica:** construa os eventos de forma progressiva no Excalidraw — não mostre tudo de uma vez. O aluno precisa ver cada seta surgir para sentir a emergência dos contextos.

---

## Bloco 4 · [42–56] · Contextos emergem + Context Map

- **Desenhe o Diagrama 3:** agrupamento dos eventos em 5 contextos (Identidade, Contas&Ledger, Pagamentos, Antifraude, Devoluções).
- **Pergunte:** "Se o Diego e a Marina tivessem feito esse exercício juntos, o que teria acontecido quando 'conta' aparecesse duas vezes?" (o conflito ficaria visível na hora, lado a lado).
- **Desenhe o Diagrama 4 (context map):** Contas&Ledger upstream; Pagamentos com ACL explícito para o BACEN; Antifraude síncrono; Devoluções com ACL para o MED.
- **Fala-chave:** "O ACL já existia desde a Aula 1, sem esse nome — é o que traduz `pacs.008` para `PixIniciado` e nunca deixa o formato do BACEN vazar pra dentro do domínio."
- **Armadilha:** mencione conformista e shared kernel rapidamente; o foco é upstream/downstream e ACL.

---

## Bloco 5 · [56–66] · Fronteira de consistência

- **Desenhe o Diagrama 5:** agregado Ledger com a fronteira marcada; fora dela, comunicação por evento.
- **Fala-chave:** "Fronteira de consistência transacional = fronteira do agregado."
- **Pergunte:** "Por que o Outbox da Aula 2 publica os eventos **depois**, de forma assíncrona?" (porque o que precisava estar junto já aconteceu dentro do agregado — o que sobra, por definição, pode esperar).

---

## Bloco 6 · [66–84] · As 4 regras de agregado + o trade-off que liga à Aula 2

**Objetivo:** este é o bloco mais valioso do curso inteiro em termos de conexão entre aulas. Reserve o tempo.

**Parte A — as 4 regras (Vernon) [66–74]**

1. A **invariante define a fronteira** — comece pela pergunta "que regra eu nunca posso violar?"
2. Projete agregados **pequenos** — agregado grande é contenção disfarçada de conveniência.
3. Referencie outros agregados **por identidade**, não por objeto.
4. **Fora da fronteira, consistência eventual** — altere um, emita evento, o outro reage.

- **Fala-chave sobre a regra 4:** "Reparem que isso é literalmente o Outbox da Aula 2. Ele não é truque de infraestrutura — é consequência direta de ter desenhado agregados pequenos."

**Parte B — a revelação [74–80]**

- **Explicite a tensão:** as regras 2 e 4 se opõem. Agregado grande = mais invariantes protegidas + mais contenção. Pequeno = escala + mais consistência eventual para gerenciar.
- **Desenhe o Diagrama 6** e então faça a conexão, devagar:

  > "O ponto quente do ledger, que derrubou o TechPix no dia 5, era um **agregado grande demais**. A conta `pix_a_liquidar` estava dentro da fronteira transacional de todas as transações ao mesmo tempo. **Não era um problema de banco de dados; era um problema de modelagem de domínio que se manifestou como problema de banco.**"

- **Pare e deixe decantar.** Depois: "Quando a gente falou de 'reparticionar a escrita' na Aula 2, a gente estava falando, em DDD, de **redesenhar a fronteira do agregado**. É a mesma decisão vista de dois ângulos."

**Parte C — o exercício discutível [80–84]**

- **Pergunte:** "O limite diário de transferência pertence ao agregado da Conta?"
- Deixe a turma argumentar os dois lados: a favor (é invariante, regra 1) e contra (serializa todas as transferências daquele cliente — ponto quente por decisão de modelagem).
- **A resposta honesta:** depende do rigor exigido. Precisão absoluta → dentro, e pague a contenção. Pequeno excesso momentâneo tolerável → fora, atualizado por evento.
- **Fecho do bloco:** "Reparem que essa é uma decisão de **negócio**, não de engenharia. E é exatamente o tipo de coisa que merece um ADR."

---

## Bloco 7 · [84–94] · Versionamento de eventos

**Objetivo:** o problema que ninguém planeja e que aparece no mês seis.

- **Fala-chave de abertura:** "No momento em que o Outbox publica `PixLiquidado` e três serviços consomem, o formato dele deixou de ser detalhe interno — virou uma **interface com três clientes**."
- **Coloque o problema:** "Mês seis, vocês precisam renomear um campo. O que acontece com os consumidores antigos? E com os eventos antigos, retidos no broker, que podem ser reprocessados?"
- **Desenhe o Diagrama 7** e apresente as 3 estratégias: só adicionar (retrocompatível), versionar o tipo (`v1`/`v2` convivendo), registro de schema (rejeita publicação incompatível).
- **Conecte:** "O schema registry é a fitness function da Aula 2, aplicada a contrato de evento."
- **Alerta prático:** "Em sistema financeiro, com retenção de anos por auditoria, vocês **vão** ler eventos escritos por código que não existe mais. Planejem desde o primeiro evento — retrofitar depois é doloroso."

---

## Bloco 8 · [94–106] · SDD: a spec + Spec Kit + Context Engineering

- **Escreva a spec do contexto Pagamentos ao vivo:** linguagem, invariantes, eventos, dependências, SLA herdado.
- **Pergunte:** "Qual linha dessa spec, virando teste automático, teria pegado o bug do Diego e da Marina?" (a linha "Linguagem", que distingue explicitamente 'Pagamento' de 'Transferência').
- **Mostre o Spec Kit (GitHub):** desenhe o pipeline `/speckit.constitution → specify → clarify → plan → tasks → analyze → implement` e a árvore `.specify/memory/constitution.md` + `specs/001-…/spec.md·plan.md·tasks.md`. Roda dentro do agente de código (Claude Code, Copilot, Gemini CLI).
- **Fala-chave:** "A constituição do TechPix já estava escrita — a gente só não sabia o nome: Σ=Σ, E2E ID único, falhar fechado. O ADR é a jurisprudência; a constituição é a lei consolidada."
- **Pergunte:** "Que pergunta o `/speckit.clarify` faria sobre a spec do limite diário do Diego?" ("quando você escreve 'conta', quer dizer identidade ou sub-carteira?" — o bug da abertura não sobrevive ao clarify).
- **Desenhe o Diagrama 9 (Context Engineering):** o que entra na janela do agente (spec, glossário do contexto, ADRs, eventos) vs. o que fica **de fora** (internals de Antifraude e Identidade).
- **Fala-chave de fecho:** "O bounded context de vocês é, literalmente, a unidade de contexto que um agente deveria receber."
- **Armadilha:** não deixe virar aula de sintaxe de ferramenta. O ponto é a ordem imposta (princípios → spec → plano → tarefas → verificação) e a analogia bounded-context ↔ context-window. "A ferramenta passa; o fluxo fica."

---

## Bloco 9 · [106–116] · Bounded context = microsserviço?

**Objetivo:** desarmar a confusão que causa projetos de microsserviços fracassados.

- **Pergunte primeiro** e deixe a turma responder antes de você.
- **A resposta:** um serviço nunca deve conter **mais de um** contexto; mas um contexto pode perfeitamente ser só um módulo do monólito — e frequentemente **deve**.
- **Os 4 critérios que justificam extrair:** escala diferente, ciclo de deploy diferente, time diferente (o mais comum e legítimo), requisito de isolamento de falha distinto.
- **O alerta de fecho:** "Se nenhum critério se aplica, extrair só compra os **custos** de sistema distribuído — latência, falha parcial, consistência eventual, observabilidade — sem nenhum benefício. Vocês pagaram e não levaram o produto."
- **A formulação para guardar:** "**Bounded context é decisão de modelagem; microsserviço é decisão de topologia.**"

---

## Bloco 10 · [116–120] · Fecho e ponte

- **Recapitule os 5 pontos** (Seção 7 do conteúdo completo).
- **Fala de transição:** "Eu não leciono as próximas aulas — outro professor vai construir a comunicação entre esses contextos e extrair alguns para serviços. Mas eu volto na Aula 8 para fechar o círculo."
- **Frase de encerramento:** "Da fé, na Aula 1, para a evidência, na Aula 8 — e a linguagem que vocês desenharam hoje é o que torna essa evolução segura, com humano ou com agente."

---

## Se sobrar tempo (buffer)

- Aprofundar os 9 padrões de context map do DDD clássico (partnership, customer-supplier, separate ways, big ball of mud, open host service, published language).
- Discutir property-based testing das invariantes da spec: em vez de testar casos, gerar milhares de entradas aleatórias e verificar que a invariante nunca quebra.
- **Exercício (10 min):** encontrar outra palavra do TechPix que provavelmente significa coisas diferentes em contextos diferentes — "limite"? "cliente"? "transação"? "pagamento"?

---

## Diagramas desta aula (ver aula3-roteiro.html)

1. Mapa narrativo do curso.
2. Rio de eventos do Pix (event storming).
3. Contextos emergindo do agrupamento.
4. Context map (upstream/downstream, ACL, BACEN).
5. Agregado Ledger e a fronteira de consistência.
6. **Agregado grande vs pequeno** — o trade-off que explica o dia 5.
7. **Versionamento de evento** — as 3 estratégias.
8. Spec do contexto Pagamentos.
9. Context Engineering: o que entra / o que fica de fora.
