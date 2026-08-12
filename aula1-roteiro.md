---
layout: default
title: "Aula 1 — Roteiro (fonte)"
---

# Curso System Design — Arquitetura de Sistemas Financeiros com IA
# Aula 1 — Fundamentos de Arquitetura em Fintech

> **Formato:** ao vivo · **Duração-alvo:** ~124 min (2h + alguns minutos) — este roteiro já é desenhado para 2h de profundidade real; com a Lei de Little e as tecnologias nomeadas, ele roda um pouco além de 120min. Corte a seção "se sobrar tempo" se precisar encaixar em 120 exatos.
> **Caso contínuo:** fintech fictícia **TechPix** — desenhada ao vivo e evoluída o curso inteiro.
> **Dois fios condutores:** Fintech/BACEN (ledger → PIX → DICT/SPI → SLA 40s → Recuperação de Valores) · IA (SDD → Context Engineering → Harness → Looping).
> **Companion:** consulte `aula1-perguntas-dificeis.md` se a turma empurrar em qualquer ponto — tem munição de embasamento pronta.

## Visão de relance

| Bloco | Tempo | Título | O que construir no Excalidraw |
|---|---|---|---|
| 1 | 0–8 | Cold open: o pagamento fantasma | Só a pergunta (sem desenho) |
| 2 | 8–20 | Por que dinheiro é diferente | Diagrama 1 — as 4 propriedades |
| 3 | 20–32 | O ledger de partida dobrada | Diagrama 2 — átomo do dinheiro + write/read model |
| 4 | 32–50 | Capacidade: números reais + Lei de Little | Diagrama 6 — matemática de capacidade |
| 5 | 50–64 | Isolamento, particionamento e tecnologias reais | Diagrama 7 — locking, sharding, saga, tecnologias |
| 6 | 64–80 | "Aconteceu quantas vezes?" (idempotência) | Diagrama 3 — idempotência |
| 7 | 80–96 | O arquiteto e os trade-offs (CAP/PACELC) | Diagrama 4 — PACELC |
| 8 | 96–110 | O guardanapo do TechPix + Recuperação de Valores | Diagrama 5 — arquitetura + BACEN + Diagrama 8 — grafo de rastreamento |
| 9 | 110–120 | Decidir por escrito: ADR → Spec | Diagrama 9 — ADR-001 |
| 10 | 120–124 | Fecho e ganchos | Recap + mapa do curso |

> Os diagramas renderizados estão em `aula1-roteiro.html`. Abaixo, cada um vem descrito para você construir ao vivo no Excalidraw.

---

## Bloco 1 · [0–8] · Cold open: o pagamento fantasma

**Objetivo:** criar tensão e provar que o "óbvio" não é óbvio. *Nada de slide ou desenho ainda.*

- **Conduza:** conte a cena — 2h47, Black Friday, PIX de R$5.000, tela travada, cliente toca 3 vezes. Digite no Excalidraw **apenas**: `Pagou 1×, 3× ou 0×?`
- **Pergunte:** "Quem já levou (ou causou) uma cobrança dupla? O que falhou na arquitetura, não no código?" — colha 2-3 respostas.
- **Fala-âncora:** "A resposta a essa pergunta não é uma linha de código. É uma decisão de arquitetura. E é ela que a gente vai construir hoje, com profundidade de verdade — não só conceito, mas implementação."
- **Armadilha:** não diga a palavra "idempotência" ainda — segure até o Bloco 6, senão você queima o clímax.

---

## Bloco 2 · [8–20] · Por que dinheiro é diferente

**Objetivo:** estabelecer as 4 propriedades do dinheiro e as 4 decisões que elas forçam — o primeiro exercício de derivação (não palpite) da aula.

- **Fala-chave:** "As decisões grandes de arquitetura não são gosto — são deriváveis do domínio. Vamos derivar juntos."
- **Percorra a tabela das 4 propriedades** (conservação, irreversibilidade, auditabilidade, correção > disponibilidade) → as 4 decisões que cada uma força.
- **Pergunte, antes de revelar cada decisão:** "dado que dinheiro é conservado, o que isso força vocês a fazer na escrita?" — deixe a turma chutar antes de confirmar "ledger de partida dobrada".
- **Armadilha:** não deixe isso virar uma lista decorada. O valor é o raciocínio "propriedade → decisão", não a lista em si.

**Diagrama 1 — as 4 propriedades → 4 decisões (desenhe):**
- Quatro linhas: Conservação → Ledger partida dobrada; Irreversibilidade → Idempotência + falhar fechado; Auditabilidade → Imutabilidade/append-only; Correção > disponibilidade → Consistência forte no núcleo.

---

## Bloco 3 · [20–32] · O ledger de partida dobrada

**Objetivo:** o átomo do sistema — Pacioli, a regra Σ débitos = Σ créditos, e a virada conceitual "log é a verdade, saldo é projeção".

- **Fala-chave:** "Num sistema comum você cria e apaga dado à vontade. Aqui, dinheiro é conservado: todo débito tem um crédito. Isso é partida dobrada — 500 anos, base de todo core bancário."
- **Pergunte:** "Se saldo é só um número numa coluna, o que acontece em duas escritas concorrentes?" (puxa race condition/*lost update* → por que o ledger precisa de transação — gancho direto pro Bloco 5).
- **Ponte BACEN:** "No PIX, a liquidação final ocorre no SPI, em moeda de banco central. Você nunca 'tem' o dinheiro — você registra um direito sobre ele."
- **Armadilha:** não deixe confundirem **saldo** (projeção derivada, read model) com **ledger** (a verdade, write model).

**Diagrama 2 — o átomo do dinheiro (desenhe):**
- Três caixas: `conta pagador (−R$100)` → `transação` → `conta recebedor (+R$100)`.
- Dentro da transação, dois lançamentos: `débito · pagador R$100` e `crédito · recebedor R$100`.
- Faixa de invariante embaixo: **Σ débitos = Σ créditos, sempre. O saldo é projeção derivada — nunca a fonte da verdade.**

---

## Bloco 4 · [32–50] · Capacidade: o exercício com números reais (+ Lei de Little)

**Objetivo:** o momento mais "professor ao vivo fazendo conta" da aula. Nada de número chutado — tudo a partir de dados reais do BACEN, com o aluno acompanhando cada passo no Excalidraw. Este bloco cresceu — avise que vai ter uma segunda parte densa (Lei de Little).

- **Digite no Excalidraw os dados brutos:** "jan-mai/2026: 36,3 bilhões de transações Pix, R$16 tri, +26% a/a" (fonte: BACEN).
- **Faça a conta ao vivo, passo a passo** (não pule etapa — o valor pedagógico está no processo):
  1. Anualizar: 36,3 bi / 5 meses × 12 ≈ **87 bilhões/ano**.
  2. Diário: 87 bi / 365 ≈ **238 milhões/dia**. Conferir com o recorde real: 313,3 milhões em 5/dez/2025.
  3. TPS médio: 238 mi / 86.400 s ≈ **2.750 TPS** — bate com o "quase 3 mil/s" que o próprio BACEN divulgou. **Pare aqui e deixe a turma sentir esse "bateu" — é o momento de confiança da aula.**
  4. TPS de pico (estimativa, não oficial): dia de recorde ≈ 3.626 TPS de média; aplicando fator de pico 5× ≈ **18 mil TPS no pico nacional agregado**.
  5. Lançamentos: ×3 por transação ≈ 260 bilhões de lançamentos/ano.
  6. Armazenamento: ×300-500 bytes/registro ≈ **75-130 TB/ano**, só de ledger.
- **Fala-chave (a técnica, não só o número):** "Dado real da fonte oficial + fator de pico estimado com critério = capacidade defensável, mesmo sem número de pico publicado."
- **Pergunte:** "Por que o TPS de pico é uma estimativa e o TPS médio não é?"
- **Segunda parte — a Lei de Little (não pule, é a ferramenta mais subestimada de System Design):** construa `L = λ × W` no Excalidraw. Explique: concorrência = taxa de chegada × tempo no sistema.
  7. Assuma 5% de mercado para o TechPix: 18 mil × 0,05 = **900 TPS** na infraestrutura própria.
  8. Com 50 ms por escrita: L = 900 × 0,05 = **45 conexões simultâneas** no pico — número pequeno e tranquilizador.
  9. **O golpe pedagógico:** "e se, sob contenção, essa escrita passar de 50ms para 500ms?" → L = 900 × 0,5 = **450 conexões**. "Se o pool foi dimensionado pra 100... é isso, com número, que é o esgotamento de pool da Aula 2."
  10. IOPS: 900 TPS × 3 lançamentos ≈ 2.700 escritas/s — muito abaixo da capacidade de um SSD NVMe (500k-1M IOPS). **"O disco nunca é o gargalo. É coordenação."**
- **Armadilha:** não deixe a Lei de Little passar batida como "só uma fórmula". O valor está no golpe do passo 9 — a turma precisa *sentir* o pool esgotando por causa da matemática, não por afirmação.

**Diagrama 6 — matemática de capacidade + Lei de Little (ver HTML):** funil dos 6 passos + a virada de 45→450 conexões.

---

## Bloco 5 · [50–64] · Isolamento, particionamento e tecnologias reais

**Objetivo:** descer da abstração "consistência forte" para a implementação real em banco de dados — com nomes de tecnologia de verdade. Bloco de maior densidade técnica da aula — avise a turma.

- **Fala-chave de abertura:** "Até agora 'consistência forte' foi uma propriedade abstrata. Vamos dar nome e sobrenome a ela — inclusive o nome do banco de dados."
- **Explique os níveis de isolamento** em ordem crescente: read committed → snapshot/repeatable read (write skew) → serializable (protege Σ=Σ, custa aborto/retry sob contenção).
- **Pergunte:** "Qual desses três níveis vocês usariam para o ledger? E para o extrato?"
- **Explique locking pessimista vs. controle de concorrência otimista** — sob alta contenção, o otimista também sofre (tempestade de retentativas).
- **Explique particionamento**: `hash(conta_id) mod N`, caso fácil vs. difícil → two-phase commit vs. saga.
- **Nomeie tecnologias reais (não pule esta parte — é o que a turma pediu):**
  - **PostgreSQL**: serializable via **SSI**, roda em paralelo e aborta ao detectar estrutura perigosa. Muitas fintechs rodam o ledger inteiro nele, bem particionado, até o throughput exigir algo mais.
  - **MySQL/InnoDB**: repeatable read com **next-key locking** (trava linha + lacuna) — mecanismo diferente do Postgres pro mesmo problema.
  - **CockroachDB / YugabyteDB / TiDB**: particionamento automático via **Raft** por faixa de dados, rebalanceamento automático de chave quente, e só oferecem serializable — não tem opção mais fraca.
  - **Spanner**: soma **consistência externa** via TrueTime ao serializable distribuído — a garantia mais forte em produção hoje.
  - **DynamoDB**: forte por item é fácil; transação multi-item (`TransactWriteItems`) tem limites — desafio real pra um ledger.
  - **Vitess** (YouTube, Slack): a prova viva de que `hash(conta_id) mod N` roda em produção, em escala nacional, sobre MySQL comum.
- **Pergunte:** "Dado tudo isso, vocês começariam o TechPix com Postgres bem particionado, ou já iriam de CockroachDB?" (não há resposta errada — o valor é justificar o trade-off).
- **Armadilha:** não deixe esse bloco ficar 100% teórico. Sempre volte pro TechPix: "é essa fila de lock, numa única conta de liquidação, que vai explodir no dia 5 — Aula 2."

**Diagrama 7 — isolamento/locking/sharding + tecnologias (ver HTML):** os 3 níveis de isolamento em escada; pessimista vs. otimista; partição com caso fácil/difícil; logos/nomes das tecnologias reais.

---

## Bloco 6 · [64–80] · "Aconteceu quantas vezes?" (idempotência)

**Objetivo:** pagar a dívida do cold open. Idempotência e *exactly-once lógico*.

- **Fala-chave:** "A rede falha, o cliente reenvia. Sem proteção, 3 requests viram 3 débitos. A chave de idempotência transforma 'tentou 3×' em 'aconteceu 1×'."
- **Detalhe técnico:** a chave nasce no **cliente** e viaja com a requisição; no PIX ela se materializa no `EndToEndId` (E2E ID), com o ISPB do participante embutido. A API guarda `key → resultado`; um retry devolve o mesmo resultado, **não reexecuta**.
- **Pergunte:** "A chave deve nascer no cliente ou no servidor? Por quê?" (no cliente — se o servidor gera, cada retry vira chave nova e o dedup morre).
- **Armadilha:** idempotência **não** é só um `UNIQUE` no banco. O caso difícil é a segunda requisição concorrente que chega **antes** de a primeira commitar — conecte direto ao Bloco 5: é o mesmo problema de isolamento/locking, agora aplicado à deduplicação.

**Diagrama 3 — idempotência (desenhe):**
- Coluna esquerda `cliente`: 3 requisições empilhadas, todas `POST /pix · key abc-123` (timeout → reenvio).
- Seta para `API · dedup por chave`: "1ª executa e guarda key→resultado; 2ª e 3ª devolvem o mesmo resultado, não reexecutam".
- Seta para `ledger`: **débito aplicado 1×**.
- Faixa de alerta embaixo (vermelho): **Sem a chave: 3 tentativas = 3 débitos. No PIX o estorno só via MED/Recuperação de Valores.**

---

## Bloco 7 · [80–96] · O arquiteto e os trade-offs (CAP/PACELC)

**Objetivo:** definir o ofício — arquiteto é quem torna trade-off **explícito e defensável**. Sair de CAP para **PACELC**, com exemplos reais.

- **Fala-chave:** "Arquitetura são as decisões caras de reverter. Toda decisão de fintech é um trade-off: consistência custa latência; disponibilidade custa consistência."
- **Aplique ao TechPix:** o **ledger** fica no polo forte; o **extrato/feed** fica no polo eventual.
- **Exemplos reais (não pule):** Google Spanner (PC/PC, via TrueTime) vs. DynamoDB/Cassandra (PA/EL, consistência ajustável) vs. Postgres num nó só.
- **Ponte BACEN:** "O teto normativo do PIX é 40 s ponta a ponta (Manual de Tempos do Pix v7.0) — mas o SPI real roda em p99 de 4,6 s. Bem mais folgado do que o '10 segundos' que todo mundo repete."
- **Pergunte:** "Onde no TechPix vocês aceitariam consistência eventual? E onde jamais?"
- **Armadilha:** desfaça o mito "eventual = errado". Eventual é *correto, com atraso limitado*.

**Diagrama 4 — PACELC (desenhe):**
- Barra horizontal com dois polos. Esquerda: `consistência forte` → **ledger (escrita)**. Direita: `consistência eventual` → **extrato / feed**.
- Linha PACELC: **se Particiona → Availability ou Consistency; senão (Else) → Latency ou Consistency.**
- Selo: **teto normativo PIX 40 s ponta a ponta · SPI real p99 4,6 s.**

---

## Bloco 8 · [96–110] · O guardanapo do TechPix + Recuperação de Valores

**Objetivo:** montar a arquitetura de guardanapo e apresentar o achado mais atual da aula — o rastreamento de fraude por grafo.

- **Fala-chave:** "Esse é o TechPix hoje. Guardem esse desenho: na Aula 2 ele racha, na Aula 3 a gente corta em contextos, na Aula 8 ele se conserta sozinho."
- **Explique as caixas do BACEN:** `SPI`, `DICT` (com o token bucket anti-scraping — 404 custa 20× mais que 200), `STR`.
- **Pergunte:** "Qual dessas caixas é a mais perigosa de escalar?" — ledger e DICT síncrono. Gancho da Aula 2.
- **Vire a chave para Recuperação de Valores:** "MED evoluiu. Hoje, quando alguém sofre fraude, o BACEN não devolve só da conta que recebeu — ele rastreia um **grafo**: a transação raiz, e todos os saltos subsequentes para onde o dinheiro foi." Explique: grafo de rastreamento, contas no caminho todas contribuem, marcação de fraude em cascata no DICT, bloqueio cautelar de até 72h, SLA de conclusão p99 6h (fraude) / p95 48h (falha operacional), o código `MD06` no `pacs.004`.
- **Pergunte:** "Por que isso é um problema de sistema distribuído **federado**, e não só uma query no seu próprio banco?" (o dinheiro salta entre instituições diferentes — TechPix não controla os outros bancos).
- **Armadilha:** não desenhe o guardanapo com detalhe demais (caixas grandes) — mas dê ao grafo de rastreamento o tempo que ele merece, é conteúdo novo e denso.

**Diagrama 5 — arquitetura + BACEN (desenhe):**
- Fluxo: `app/cliente` → `API/BFF (idempotency-key)` → `core: pagamentos + ledger` → `BACEN (SPI / DICT / STR)`.
- Selo: **o caminho todo cabe no teto de 40 s — na prática, poucos segundos**.
- Selo de alerta: **racha na Aula 2: ledger + DICT síncrono**.

**Diagrama 8 — grafo de rastreamento (ver HTML):** transação raiz → nós subsequentes (saltos entre contas/instituições) → contas marcadas, com o bloqueio cautelar e os SLAs anotados.

---

## Bloco 9 · [110–120] · Decidir por escrito: ADR → Spec

**Objetivo:** transformar decisão em artefato; escrever o **ADR-001 ao vivo** e plantar a semente do **SDD**.

- **Fala-chave:** "Uma decisão que não está escrita não existe — vira boato. E aqui está a virada: esse mesmo ADR vira uma spec que um agente de IA lê e implementa igual a vocês. É o começo do Spec-Driven Development."
- **Pergunte:** "Qual é a consequência dolorosa do ADR-001?" — "latência no write". Gancho exato da Aula 8.
- **Armadilha:** ADR não é documentação eterna. É datado, imutável e pode ser **substituído** (`superseded`) — like o ADR-002 vai complementar (não substituir) esse aqui, na Aula 2.

**Diagrama 9 — ADR-001 (escreva ao vivo):**
```
ADR-001 · Consistência forte no ledger      [aceito · 2026-07-30]

Contexto:      PIX é irreversível; saldo não pode ficar negativo;
               liquidação final no SPI; teto normativo de 40s.
Decisão:       lançamentos imutáveis em double-entry; escrita ACID,
               serializable, síncrona; idempotência por identidade
               de operação (E2E ID correlaciona; devolução tem a
               sua); correção só por lançamento compensatório.
Consequências: (+) correção garantida
               (+) invariantes viram teste — base do Harness
               (−) latência na escrita — a validar em produção
               (−) contenção sob pico — o preço do isolamento forte

→ Vira spec executável (SDD). Na Aula 8, um agente questiona o
  "− latência" com dados reais e propõe o ADR-003.
```

---

## Bloco 10 · [120–124] · Fecho e ganchos

**Objetivo:** consolidar e amarrar no resto do curso.

- **Recap (peça para a turma completar):** ledger = *a verdade*; capacidade = *dado real + estimativa com critério*; isolamento = *o preço técnico da consistência forte*; idempotência = *correção sob incerteza*; trade-off explícito = *o ofício do arquiteto*; Recuperação de Valores = *fraude como problema de grafo federado*.
- **Callback:** volte ao mapa do curso — o guardanapo racha na 2, vira contextos na 3, se conserta na 8.
- **Deixa mental:** "Onde no sistema de vocês vocês estão decidindo na fé, sem evidência? Na Aula 8 a gente troca fé por evidência."
- **Frase de encerramento:** "Hoje vocês decidiram na fé — mas com números reais debaixo do braço, não achismo. Guardem o ADR-001: um dia a produção, e um agente, vão ter opinião sobre ele."

---

## Glossário rápido (BACEN / PIX)

- **SPI** — Sistema de Pagamentos Instantâneos; liquidação em moeda de banco central, operado pelo BC.
- **DICT** — Diretório de Identificadores de Contas Transacionais; resolve chave Pix → conta; anti-scraping por token bucket.
- **STR** — Sistema de Transferência de Reservas; trilho de alto valor (TED).
- **E2E ID / EndToEndId** — identificador único ponta a ponta de cada transação Pix.
- **MED** — Mecanismo Especial de Devolução; trilho de estorno em caso de fraude/falha.
- **Recuperação de Valores** — extensão do MED que rastreia por grafo para onde o dinheiro fraudado foi desviado.
- **PSP** — Prestador de Serviço de Pagamento (a "fintech" no ecossistema).
- **ISO 20022 / pacs** — padrão de mensageria; `pacs.008` (pagamento), `pacs.002` (status), `pacs.004` (devolução, código `MD06` no MED).

---

## Conceitos técnicos gerais desta aula

- **Isolamento (read committed / snapshot / serializable)** — proteção crescente contra anomalias de concorrência.
- **Locking pessimista vs. controle de concorrência otimista** — as duas famílias de defesa contra escrita concorrente.
- **Two-phase commit vs. Saga** — atomicidade forte entre partições vs. consistência eventual com compensação.

## Conceitos de IA plantados nesta aula (colhidos na Aula 8)

- **Spec-Driven Development (SDD)** — o ADR-001 vira spec executável; fonte da verdade que humano e agente leem igual.
- **Harness (semente)** — a consequência "− latência" será *validada em produção* (feature flag, canary), não decidida na fé.
- **Looping (semente)** — "decidir na fé → decidir na evidência" é o loop de feedback que a Aula 8 fecha.

---

## Se sobrar tempo (buffer, não obrigatório)

- Aprofundar TrueTime do Spanner: como GPS + relógio atômico limitam a incerteza entre datacenters.
- Discutir por que "SELECT FOR UPDATE" sozinho não escala: fila de lock cresce linear com contenção.
- **Exercício:** em duplas, refazer a matemática de capacidade do Bloco 4 assumindo que o TechPix tem 5% do mercado nacional — qual o TPS de pico esperado só na infraestrutura dele?
