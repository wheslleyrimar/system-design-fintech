---
layout: default
title: "Aula 2 — Roteiro (fonte)"
---

# Aula 2 — Fundamentos da Evolução Arquitetural
## Roteiro de condução (~120 min)

> **Duração-alvo:** 2h — este roteiro já é desenhado para 2h de profundidade real.
> **Callback obrigatório:** a Aula 1 terminou plantando isto: "guardem o ADR-001, porque um dia a produção vai ter opinião sobre ele" e o guardanapo já dizia "racha na Aula 2: ledger + DICT síncrono". Esta aula é o pagamento dessa dívida.
> **Companions:** `topologia-progressiva.html` (camadas 5, 6 e 7 caem nesta aula) · `aula2-perguntas-dificeis.md`.

## Visão de relance

| Bloco | Tempo | Título | O que construir no Excalidraw |
|---|---|---|---|
| 1 | 0–8 | Cold open: o dia 5 | Só a cena (sem desenho) |
| 2 | 8–20 | O monólito não é o vilão | Diagrama 1 — monólito modular |
| 3 | 20–32 | Arquitetura evolutiva & fitness functions | Diagrama 2 — loop de fitness function |
| 4 | 32–52 | **A matemática do dia 5** (curva de filas + retry storm) | Diagrama 3 — curva do cotovelo |
| 5 | 52–70 | Anatomia da fratura | Diagrama 4 — hotspot + DICT/pool |
| 6 | 70–84 | Desacoplamento incremental | Diagrama 5 — Strangler Fig |
| 7 | 84–96 | Outbox + CQRS | Diagrama 6 — Outbox |
| 8 | 96–108 | **Quanto o particionamento compra?** | Diagrama 7 — a conta quente |
| 9 | 108–116 | **As ferramentas reais** | Tabela de tecnologias |
| 10 | 116–120 | ADR-002 + gancho pra Aula 3 | Diagrama 8 — ADR-002 |

---

## Bloco 1 · [0–8] · Cold open: o dia 5

**Objetivo:** reativar a tensão da Aula 1 e mostrar que uma decisão "correta" ainda pode quebrar na prática.

- **Conduza:** conte a cena do dia 5 — meio-dia, salário caiu, tráfego triplica em 20 minutos, o sistema não cai, fica **lento**, cada vez mais lento.
- **Fala-âncora:** "Eu avisei na Aula 1: guardem o ADR-001, porque um dia a produção vai ter opinião sobre ele. Hoje é esse dia."
- **Pergunte:** "O tráfego triplicou. O sistema ficou três vezes mais lento?" — deixe a turma dizer "não, ficou muito pior" e **não explique ainda**. O porquê é o clímax do Bloco 4.
- **Armadilha:** não revele ainda que o ledger e o DICT são os pontos de fratura.

---

## Bloco 2 · [8–20] · O monólito não é o vilão

**Objetivo:** desfazer o mito "monólito = ruim"; monólito modular como decisão defensável.

- **Fala-chave:** "O vilão não é monólito. É Big Ball of Mud — zero fronteira interna."
- **Desenhe o Diagrama 1:** módulos do TechPix dentro de UM deployable.
- **Desenhe o Diagrama 1b (a travessia):** um Pix atravessando os 6 módulos, passos numerados 1–8, com a linha dentro/fora (TechPix | DICT/SPI). É o desenho clássico de payment system aplicado ao TechPix. Termine apontando o passo 8: "extrato e notificação no mesmo processo — guardem."
- **Preencha a tabela de módulos:** responsabilidade · dados que possui · quem chama · comunicação. "Seis módulos" só vira arquitetura quando cada linha está preenchida.
- **Sobre Cartões:** seja honesto — é fronteira reservada, não funcionalidade. O trilho de cartões (PSP, bandeiras, settlement D+n) está fora do escopo do curso.
- **Pergunte:** "Se Cartões faz um JOIN direto na tabela do Ledger porque 'é mais rápido', isso ainda é monólito modular?" (não — é bola de lama com nome bonito).
- **Regra prática:** só extraia um módulo para serviço depois que a fronteira ficar estável **por meses**. Extrair cedo é caro; extrair tarde custa um refactor. A assimetria favorece esperar.
- **Armadilha:** não deixe "monólito modular" virar desculpa para nunca evoluir.

---

## Bloco 3 · [20–32] · Arquitetura evolutiva & fitness functions

**Objetivo:** formalizar "arquitetura é filme, não foto"; fitness function como mecanismo.

- **Desenhe o Diagrama 2:** loop `proposta → fitness function → gate → produção`.
- **Explique os 4 tipos:** atômica vs holística; disparada (CI) vs contínua (produção).
- **Dê os 3 exemplos do TechPix:** teste de dependência de arquitetura, monitor de p99, game day de carga.
- **Semente de IA (uma frase, não um desvio):** "Uma fitness function que barra um deploy tem o mesmo formato de um eval que barra a proposta de um agente. Vocês já estão construindo o Harness."
- **Armadilha:** não aprofunde IA aqui.

---

## Bloco 4 · [32–52] · A matemática do dia 5 (o clímax intelectual da aula)

**Objetivo:** explicar, com número, por que triplicar o tráfego produziu colapso e não degradação proporcional. Este é o bloco mais denso — avise a turma.

**Parte A — a curva de filas [32–42]**

- **Abra com a padaria, não com a fórmula:** um caixa só, atendimento de 10 s, clientes chegando em rajada. Pergunta: "quanto tempo o cliente espera na fila?" Defina utilização em palavras (fração do tempo com o caixa ocupado) ANTES de mostrar o ρ — e avise: "ρ (rô) é só o apelido grego de utilização".
- **Escreva a fórmula no Excalidraw, primeiro em palavras:** `espera na fila = tempo de um atendimento × [utilização ÷ (1 − utilização)]` — e só então a versão dos livros, `fator = ρ / (1 − ρ)`. Nomeie o denominador: "1 − ρ é a folga".
- **Fala-chave:** "Olhem embaixo da divisão. Quando a utilização se aproxima de 100%, a folga vai a zero — e dividir por quase zero dá um número gigante. Não é uma reta — é um cotovelo."
- **Faça a conta em três perguntas, uma por vez:** (1) de cada 100 minutos, quantos o caixa passa ocupado? (2) quantos sobram de folga? (3) divida um pelo outro — o resultado é quantos atendimentos de fila existem na sua frente. 90 ÷ 10 = 9 → 9 × 10 s = 90 s.
- **Desenhe o Diagrama 3a (a padaria em três linhas):** para 50%, 90% e 95% — a linha do tempo do caixa (blocos ocupado/livre), a fila média em bolinhas, e a conta ao lado. O ponto visual: os buracos livres são o que drena a fila, e é o buraco que some primeiro. Frase-âncora: "o caixa nunca ficou mais lento — só mais ocupado. Toda a piora veio da fila."
- **Construa a tabela ao vivo**, linha por linha, agora com transação de 5 ms: 50% → 1,0 (5 ms) · 70% → 2,3 (~12 ms) · 80% → 4,0 (20 ms) · 90% → 9,0 (45 ms) · 95% → 19 (95 ms) · 99% → 99 (~500 ms).
- **M/M/1 é parêntese, não bloqueio:** "1" = um atendente; os dois "M" = chegadas e atendimentos aleatórios. Só o nome para quem for pesquisar.
- **Pare em 80→95%:** "A utilização subiu 15 pontos e a espera **quintuplicou**. É por isso que a intuição linear falha."
- **A regra operacional (o take-away mais prático da aula):** "Nunca dimensionem sistema financeiro para operar acima de 70% no pico. Aquela folga que parece desperdício é o que separa 'lento' de 'fora do ar'."
- **Se perguntarem a fonte dos 70%:** não é teorema — é regra de bolso que cai da tabela (a curva é lisa; Gunther chama o "joelho" de folclore). Âncoras citáveis (links no conteúdo completo): doc do DynamoDB auto scaling usa 70% como alvo do exemplo canônico (faixa 20–90%); SRE do Google, cap. "Addressing Cascading Failures", trata operar perto da capacidade como causa de cascata e manda folga N+2.
- **Pergunte:** "Quando alguém disser 'esses servidores estão a 40%, dá pra cortar metade', o que vocês respondem agora?"

**Parte B — o composto com Lei de Little + retry storm [42–52]**

- **Relembre Little em 30 s, na própria padaria:** chegam 2 clientes/min × 3 min lá dentro = 6 pessoas na loja a qualquer momento. `L = λ × W`: dentro = chegada/s × tempo lá dentro. Traduza as letras (λ = taxa de chegada; W = tempo no sistema — o que a curva explode; L = transações simultâneas, cada uma ocupando uma conexão do pool).
- **Encadeie os 5 passos no Excalidraw:** tráfego 3× → utilização 30%→90% → W explode (fator 0,4→9) → L explode (45→450 conexões) → pool de 100 esgota → timeout → **retry** → volta ao passo 1, pior.
- **Nomeie:** "Isso é retry storm. O tráfego que ele recebe agora não é a demanda dos usuários — é a demanda **mais** as retentativas que ele próprio causou. O sistema está se atacando."
- **A ironia (excelente pergunta):** "A idempotência da Aula 1 protegeu a correção — ninguém foi cobrado 3×. Ela protegeu a disponibilidade?" (Não. As 3 tentativas consumiram recurso 3×. Idempotência resolve duplicação de efeito, não amplificação de carga.)
- **Apresente as 3 defesas:** backoff exponencial **com jitter** (explique por que sem jitter você sincroniza as tempestades), retry budget (existe ponto em que insistir é pior que desistir), load shedding.
- **Armadilha:** não deixe a fórmula virar exercício de matemática. Cada número precisa voltar ao dia 5.

---

## Bloco 5 · [52–70] · Anatomia da fratura

**Objetivo:** com a matemática na mão, mostrar os dois pontos exatos.

**Parte A — hotspot do ledger:** toda escrita na mesma conta de liquidação compete pelo mesmo lock; a fila cresce; o orçamento de latência é comido pelo próprio sistema, não pelo SPI.
- **Pergunte:** "Isso significa que o ADR-001 estava errado?" (Não — a decisão de força continua certa; o problema é a implementação ingênua da partição.)

**Parte B — DICT e esgotamento de pool:** a chamada síncrona segura thread/conexão; sob pico, mais requisições esperando do que o pool aguenta; **falha em cascata** contamina o que nada tem a ver com o DICT.

- **Apresente as 3 defesas:** bulkhead (isolar pools por dependência), circuit breaker (falhar rápido), timeout calibrado ao p99 real (se o DICT responde em 1s no p99, esperar 10s é desperdiçar o orçamento).
- **Desenhe o Diagrama 4.**
- **Armadilha:** deixe claro que essas defesas não removem a necessidade de consultar o DICT — mudam o **comportamento** quando ele atrasa.

---

## Bloco 6 · [70–84] · Desacoplamento incremental

**Objetivo:** Strangler Fig e Branch by Abstraction como alternativas seguras a "reescrever tudo".

- **Encene a reunião do dia seguinte:** dev com adrenalina do plantão pede microsserviços citando Netflix. Desmonte com o diagnóstico da Seção 4: o lock da `pix_a_liquidar` num serviço separado continua existindo — só ganhou uma viagem de rede; o pool esgotado se resolve com bulkhead, dentro ou fora do monólito. Nenhuma fratura tem "deploy único" como causa raiz.
- **Plante a pergunta aberta:** "Ok, tudo não. Mas alguma coisa a gente extrai — o quê, e como saberíamos?" Não responda: fronteiras com técnica é a Aula 3; critérios de evidência para extrair vêm adiante no curso.
- **Fala-chave:** "Microsserviços trocam o problema da contenção pelo problema da distribuição — quem extrai sem critério paga os dois."
- **Desenhe o Diagrama 5:** monólito + fachada/roteador + novo componente, tráfego migrando aos poucos.
- **Conecte à topologia:** "Reparem que a fachada do Strangler Fig **é** o balanceador L7 da Camada 1 da topologia. Não é componente novo — é uso novo de um componente que já existia."
- **Pergunte:** "No TechPix, o que sai do monólito primeiro — a resolução de chave via DICT, ou a escrita do ledger?" (a resolução de chave: é o que sofre esgotamento de pool e tem menor acoplamento com a consistência forte).
- **Armadilha:** não deixe a turma pular para "vamos virar microsserviços".

---

## Bloco 7 · [84–96] · Outbox + CQRS

**Objetivo:** resolver o dual-write problem; materializar o CQRS semeado na Aula 1.

- **Fala-chave:** "E se o sistema grava no banco e cai antes de publicar o evento? Esse é o dual write problem — um dos jeitos mais silenciosos de ficar inconsistente sem ninguém perceber."
- **Desenhe o Diagrama 6:** mesma transação grava ledger + outbox; relay publica assíncrono.
- **Pergunte:** "Por que a tabela de outbox é, estruturalmente, a mesma ideia do ledger da Aula 1?" (log append-only — mesma solução, nova camada).
- **Poller vs CDC:** mencione as duas implementações e a recomendação (comece com poller, migre para CDC quando for problema **medido**).
- **Feche com o 4º consumidor — Reconciliação (Seção 5.5):** bate o ledger contra o extrato da Conta PI, por E2E ID. Três resultados: bateu; está em nós e não no BACEN (janela, depois investigação); está no BACEN e não em nós (alarme, gente olhando agora). Regras: divergência nunca vira correção automática; correção entra como lançamento novo. É a caixa de settlement → reconciliation dos diagramas clássicos de payment system.
- **Armadilha:** outbox não substitui consistência forte no ledger — resolve a propagação do evento.

---

## Bloco 8 · [96–108] · Quanto o particionamento realmente compra?

**Objetivo:** desfazer a expectativa de ganho linear. Este bloco evita uma decepção caríssima em projeto real.

- **Pergunte primeiro:** "Se eu dividir a escrita em 8 partições, eu tenho 8× mais capacidade?" — deixe a turma dizer "sim" antes de você desmontar.
- **Construa o contra-exemplo no Excalidraw:** o TechPix tem uma conta de marketplace com 15% de todo o volume. 7 partições ficam com ~12% cada; a partição do marketplace fica com ~27%.
- **Aplique a curva do Bloco 4:** "Se o sistema está a 60% de utilização média, aquela partição está perto de 100%. O sistema tem 8 partições, mas o gargalo é 1."
- **Nomeie:** Lei de Amdahl — o ganho de paralelizar é limitado pela fração que não paraleliza. A conta quente é essa fração.
- **Apresente as 3 saídas, com custo:** sub-particionar em baldes (escrita rápida, leitura mais caras), agregar antes de escrever (menos escritas, granularidade de 1s), isolar a conta quente (bulkhead aplicado a dados).
- **Take-away:** "Antes de particionar, **meçam a distribuição real das chaves**. Descobrir isso depois de uma migração de meses é a forma mais caras de aprender."

---

## Bloco 9 · [108–116] · As ferramentas reais

**Objetivo:** dar nomes, para virar "o que eu pesquiso na segunda-feira".

Percorra rápido, sem se alongar em nenhuma:

| Necessidade | Ferramenta |
|---|---|
| Fitness function de arquitetura | **ArchUnit** (Java/Kotlin), `import-linter` (Python), `dependency-cruiser` (JS/TS), `go-arch-lint` (Go) |
| Circuit breaker, bulkhead, retry | **Resilience4j** (biblioteca) ou **Envoy**/service mesh (infraestrutura) |
| CDC para o Outbox | **Debezium** (lê o WAL) |
| Broker | **Kafka** (log, retém e reprocessa) vs **RabbitMQ**/**SQS** (fila) |
| Feature flags | **Unleash** (open source), **LaunchDarkly** (comercial) |
| Teste de carga | **k6**, **Gatling**, **JMeter** |

- **Trade-off que vale explicitar:** biblioteca (conhece a semântica do domínio) vs service mesh (transparente, mas genérica).
- **A dica que a maioria erra:** "Teste de carga que sobe suave **não** reproduz o dia 5. Vocês precisam de teste de **degrau** — 30% para 300% instantaneamente. Teste suave mede capacidade; degrau mede sobrevivência."
- **Alerta sobre flags:** construir o próprio sistema de flags é subestimado — o difícil não é o `if`, é propagar mudança em segundos para centenas de instâncias, com auditoria.

---

## Bloco 10 · [116–120] · ADR-002 + gancho pra Aula 3

- **Escreva o ADR-002 ao vivo** (ver conteúdo completo, Seção 8).
- **Pergunte:** "O que a linha 'Revisão' deixa em aberto?" (reparticionar a escrita do ledger — candidato a ADR-003, que a Aula 8 vai fechar).
- **Confissão de fecho:** "Hoje eu desenhei os módulos do monólito meio no olho — Contas, Pagamentos, Antifraude. Isso foi palpite educado, não técnica."
- **Frase de encerramento:** "Na Aula 3 vocês vão descobrir por que uma palavra como 'conta' pode significar coisas diferentes dependendo de quem fala — e por que isso quebra sistemas de um jeito bem mais sutil que um pico de tráfego."

---

## Se sobrar tempo (buffer)

- Aprofundar a distinção entre latência de fila e latência de serviço, e por que medir só a média esconde a fila.
- Discutir "shadow traffic" / dark launch: rodar o novo componente em paralelo, comparando saídas, sem servir resposta ao cliente.
- **Exercício (10 min):** em duplas, calcular o fator de espera para 85% e 92% de utilização, e decidir em qual dos dois vocês aceitariam operar um ledger.

---

## Diagramas desta aula (ver aula2-roteiro.html)

1. Monólito modular do TechPix.
1b. **A travessia** — um Pix atravessando os 6 módulos, numerado 1–8, com a fronteira dentro/fora (BACEN).
2. Loop de fitness function.
3a. **A padaria em três linhas** (50/90/95%: linha do tempo do caixa + fila média + a conta).
3. **Curva do cotovelo** (utilização × espera) + encadeamento do retry storm.
4. Anatomia da fratura (hotspot + DICT/pool).
5. Strangler Fig.
6. Outbox + CQRS (com os 4 consumidores — o 4º é a Reconciliação).
7. **A conta quente** (por que 8 partições não dão 8× de capacidade).
8. ADR-002.
9. **Retrato arquitetural** de fim de aula: a travessia + tudo que a aula construiu, em verde (defesas na borda, bulkhead, partições, Outbox → Kafka → read models + reconciliação).
