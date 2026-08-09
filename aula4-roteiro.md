---
layout: default
title: "Aula 4 — Roteiro (fonte)"
---

# Aula 4 — Comunicação, Integração e Resiliência

## Roteiro de condução (~120 min)

> **Duração-alvo:** 2h com buffer embutido no Bloco 10.
> **Callback obrigatório:** a passagem de bastão da Aula 3 ("quem assume daqui é outro professor") e o bug Diego-e-Marina — o incidente de abertura é o mesmo fantasma, um andar abaixo, em tempo de execução.
> **Companions:** `aula4-perguntas-dificeis.md` · HTML de diagramas: a produzir.

## Visão de relance

| Bloco | Tempo | Título | O que construir no Excalidraw |
|---|---|---|---|
| 1 | 0–8 | Quem sou eu, e o bastão | Nada — só a frase "contrato é arquitetura" grande, para preencher depois |
| 2 | 8–20 | **A sexta-feira do extrato congelado** | Linha do tempo do incidente (19h47 → 20h51) com a fila entupindo |
| 3 | 20–32 | O mapa vira malha | Context map da Aula 3 ganhando estilo por aresta (cheia = síncrono, tracejada = assíncrono) |
| 4 | 32–46 | Síncrono bem-feito | Cadeia de chamadas com o deadline viajando e encolhendo |
| 5 | 46–60 | Assíncrono bem-feito | Fila com veneno na frente, DLQ ao lado, medidor de lag |
| 6 | 60–74 | **Mudanças seguras de contrato** | Expand/contract em 3 quadros + registry como porteiro do CI |
| 7 | 74–86 | Resiliência por aresta | Tabela de políticas do caminho crítico, linha a linha |
| 8 | 86–98 | Fail-open × fail-closed | Balança com R$ nas duas bandejas; régua de valor segmentada |
| 9 | 98–112 | **O Contrato de Integração** | A entrada Pagamentos→Antifraude escrita ao vivo |
| 10 | 112–120 | Fecho + gancho da Aula 5 | Circular os "100 ms" da aresta do Antifraude |

---

## Bloco 1 · [0–8] · Quem sou eu, e o bastão

**Objetivo:** estabelecer a voz nova sem quebrar a continuidade do curso.

- **Fala-chave:** "Eu sou o professor que chamam quando o sistema já está no ar. O professor anterior desenhou com vocês um sistema correto; meu trabalho é fazer ele sobreviver ao contato com a produção."
- **Conduza:** cite explicitamente o que você leu ao assumir: ADR-001, ADR-002 (com a linha de revisão em aberto), a spec de Pagamentos, o context map. "Eu não vou contradizer nada disso. Vou estressar tudo isso."
- **Escreva no canto do quadro, sem explicar ainda:** "contrato é arquitetura".
- **Armadilha:** não gastar tempo demais em apresentação pessoal — dois minutos de credencial (plantão, incidentes) bastam; a credibilidade real vem do incidente do Bloco 2.

## Bloco 2 · [8–20] · A sexta-feira do extrato congelado

**Objetivo:** o incidente condutor — mudança de contrato semanticamente certa quebrando consumidor em silêncio.

- **Desenhe a linha do tempo:** 19h47 deploy do Antifraude (`contaId` → `carteiraId` no `LimitesValidados`) · 19h52 projetor de leitura falha e entra em loop · 20h12 primeira ligação no suporte · 20h19 Rafael acordado **pelo telefone, não por alerta** · 20h27 causa encontrada · 20h34 hotfix aceita os dois campos · 20h51 fila de ~300 mil eventos drenada.
- **Fala-chave:** "Nenhum centavo se moveu errado. E mesmo assim trezentas pessoas ligaram achando que o dinheiro tinha sumido. Numa fintech, a percepção de que o dinheiro sumiu é quase tão cara quanto o dinheiro sumir."
- **Conecte à Aula 3:** "Lembram do Diego e da Marina? A renomeação era a *correção* daquele bug — a linguagem ubíqua aplicada. A correção certa, entregue do jeito errado. O bug deles morava entre dois times em tempo de projeto; este mora entre dois componentes em tempo de execução."
- **Pergunte:** "Quem errou aqui?" (ninguém — e é exatamente por isso que é problema de arquitetura, não de pessoa; se a resposta da turma for "o Diego", segure e desmonte: deploy revisado, testado, semanticamente correto).
- **Armadilha:** não resolver o incidente agora — o registry só aparece no Bloco 6; deixe a turma desconfortável com "como isso deveria ter sido impossível?".

## Bloco 3 · [20–32] · O mapa vira malha

**Objetivo:** transformar o context map em decisões de comunicação, aresta por aresta.

- **Desenhe:** o context map da Aula 3; vá repassando cada aresta com a pergunta-critério e marcando: linha cheia (síncrono) ou tracejada (assíncrono).
- **Fala-chave (critério):** "Quem chama consegue continuar o trabalho sem a resposta? Se não consegue, é síncrono e vocês pagam em disponibilidade. Se consegue, é assíncrono e vocês pagam em entendimento."
- **Nomeie o aforismo:** "**Síncrono acopla disponibilidade; assíncrono acopla entendimento.** A sexta-feira foi um risco semântico cobrado em horário comercial."
- **Pergunte:** "Pagamentos → Antifraude: cheia ou tracejada?" (cheia — a decisão bloqueia o próximo passo; sem `LimitesValidados` não há envio ao SPI).
- **Mostre a matemática da corrente:** 4 elos síncronos a 99,9% = 99,6% no melhor caso. "A Aula 2 mostrou essa conta esganando um pool. Hoje a gente vai dar a cada elo uma política de falha."
- **Armadilha:** a turma vai querer discutir ferramenta (Kafka? RabbitMQ?) — corte: "ferramenta é a Aula 2, apêndice; hoje é política".

## Bloco 4 · [32–46] · Síncrono bem-feito

**Objetivo:** REST na borda / gRPC no miolo; deadline propagation; timeout derivado; Idempotency-Key.

- **Desenhe:** cadeia app → Pagamentos → Antifraude → feature store, com um carimbo de deadline viajando e o tempo restante encolhendo a cada salto.
- **Fala-chave:** "Timeout local e independente gera trabalho zumbi: o fundo da pilha suando por uma requisição que o cliente já abandonou. Deadline propagado faz a cadeia inteira desistir junta."
- **Conecte à Aula 2:** "No esgotamento do pool do dia 5, parte daquelas 100 conexões trabalhava para requisições já abandonadas. Deadline é a vacina."
- **Regra prática:** "Timeout default de framework é uma decisão de arquitetura tomada por quem nunca viu o seu sistema. DICT: ~1,2 s porque o SLA é p99 ≤ 1 s. Antifraude: 150 ms porque o orçamento é 100."
- **Idempotency-Key:** "a chave da Aula 1 vira header; chave igual + corpo diferente = 422, sempre."
- **Pergunte:** "Por que o E2E ID serve de Idempotency-Key no Pix?" (identifica a intenção ponta a ponta, nasce antes do primeiro envio e sobrevive a todos os retries — Aula 1, Seção 3.4).
- **Armadilha:** não deixar virar aula de gRPC — o argumento decisivo é deadline e contrato compilado, não benchmark de serialização.

## Bloco 5 · [46–60] · Assíncrono bem-feito

**Objetivo:** consumidor idempotente, ordem por chave, consumer lag, DLQ/poison message, backpressure.

- **Desenhe:** a fila do incidente — mensagem envenenada na frente, 300 mil atrás; ao lado, a DLQ como "estacionamento"; em cima, um medidor de lag subindo sem ninguém olhando.
- **Fala-chave:** "Retry resolve falha transitória. Mensagem envenenada é falha permanente — pode tentar um milhão de vezes, o campo não renasce. Retry infinito em falha permanente transforma um evento ruim em paralisação total."
- **As duas perguntas obrigatórias de todo consumidor novo:** "O que acontece se essa mensagem chegar duas vezes? E fora de ordem?" (dedup por E2E ID ou upsert; partição por conta_id — ordem por chave, nunca global).
- **Nomeie:** "**Quem pede ordem global está pedindo um gargalo com outras palavras**" — conecte ao ponto quente da Aula 2.
- **Honestidade sobre DLQ:** estacionar quebra a ordem da chave; para fluxo ordenado, pausa por chave. "No mínimo, saibam qual modo o consumidor de vocês implementa — descobrir durante o incidente é tarde."
- **Pergunte:** "Que alerta teria transformado 40 minutos em 2?" (lag do consumidor amarrado à promessa de 100–300 ms do ADR-002 — promessa sem métrica é promessa já quebrada).
- **Armadilha:** não aprofundar dimensionamento de lag agora — "quanto de lag alerta" está no guia de perguntas difíceis; o ponto do bloco é a existência da métrica.

## Bloco 6 · [60–74] · Mudanças seguras de contrato

**Objetivo:** o clímax — expand/contract, schema registry, Pact; o incidente vira impossível.

- **Fala-âncora:** "Evento publicado é contrato público — o professor da Aula 3 avisou. Hoje isso vira processo: toda mudança quebra-contrato vira três mudanças compatíveis."
- **Desenhe os 3 quadros:** EXPANDIR (payload com `contaId` **e** `carteiraId`) → MIGRAR (consumidores trocando um a um, produtor observando quem ainda lê o velho) → CONTRAIR (campo velho removido quando telemetria mostra zero leitores).
- **Desenhe o registry como porteiro do CI:** publish do schema sem `contaId` → recusado com mensagem educada. **Fala-chave:** "A quebra morre no CI, semanas antes de qualquer sexta-feira. Reparem: é uma fitness function — a mesma espécie da Aula 2 — aplicada a contrato."
- **Pact em uma frase:** "o consumidor declara em teste o que usa; o CI do provedor roda isso e não deixa quebrar quem depende. De brinde: o inventário de quem usa o quê — a informação que não existia às 20h19 da sexta."
- **Pergunte:** "Com registry + Pact, o incidente do Bloco 2 acontece?" (não — a renomeação seca é recusada na publicação; o caminho oferecido é o expand/contract).
- **Take-away:** "Velocidade de mudança não se mede pela pressa do produtor; mede-se pela ausência de vítimas entre os consumidores."
- **Armadilha:** a objeção "isso triplica o trabalho" vai vir — responda com a conta do incidente (40 min + 300 ligações vs dois deploys extras sem coordenação) e siga; a versão longa está no guia de perguntas.

## Bloco 7 · [74–86] · Resiliência por aresta

**Objetivo:** o arsenal da Aula 2 vira política declarada, por escrito, por aresta.

- **Fala-chave:** "A diferença entre um sistema que *tem* circuit breaker e um sistema *operável* é saber onde, com que limiar, e por quê — por escrito."
- **Desenhe a tabela de políticas** (DICT / Antifraude / SPI / Ledger / projetores), linha a linha, comentando as três surpresas:
  - Antifraude com **zero retry**: "orçamento de 100 ms não compra retry — é aritmética, não descaso."
  - Breaker no SPI: "não protege o Banco Central — protege vocês do acúmulo; é o mecanismo do dia 5 com o SPI no papel do DICT."
  - Ledger sem fallback: "**não existe fallback para a verdade** — falhou a reserva, falha fechado. 'Aceitar e acertar depois' é criar dinheiro por otimismo."
- **Pergunte:** "Por que o timeout do SPI é 6 s e não 40 s?" (o p99 real do SPI é 4,6 s; 6 s dá folga honesta — esperar 40 s é segurar conexão por uma resposta que estatisticamente não vem).
- **Armadilha:** não recapitular a mecânica interna de breaker/bulkhead — a Aula 2 já deu; o bloco é sobre *declarar política*, não sobre reensinar padrão.

## Bloco 8 · [86–98] · Fail-open × fail-closed

**Objetivo:** a decisão de fallback do Antifraude como decisão de negócio segmentada por valor.

- **Desenhe a balança:** bandeja esquerda "fail-closed: 100% dos Pix recusados durante a degradação — receita, reputação, índice BACEN"; bandeja direita "fail-open: janela de caça para fraudador". No meio, a régua: ≤ R$ 200 passa com flag de análise; acima, falha fechado.
- **Fala-âncora:** "Essa segmentação não é decisão de engenharia — é decisão de negócio que a engenharia executa. O número R$ 200 é apetite de risco; quem assina é Risco e Produto, em tempo de paz, com data."
- **Fala-chave (a pior versão):** "A pior política de risco da empresa é a que mora num `catch` genérico, tomada por omissão, descoberta durante o incidente, na frente do regulador. Eu já vi. Não recomendo."
- **Pergunte:** "Se o Antifraude cair 10 minutos no pico de 900 TPS, quantos Pix o fail-closed recusa?" (~540 mil operações — 900 × 600 s; o número torna o custo do 'seguro' visível e a conversa com o negócio inevitável).
- **Armadilha:** a turma vai querer decidir o número "certo" — corte: o ponto não é R$ 200 vs R$ 100, é *quem* decide e *quando*; calibração é trabalho contínuo com dados (Aula 7).

## Bloco 9 · [98–112] · O Contrato de Integração

**Objetivo:** escrever o artefato ao vivo — a entrada Pagamentos → Antifraude completa.

- **Escreva ao vivo** a entrada da Seção 6 do conteúdo: estilo, contrato + regra de compatibilidade, processo de mudança, orçamento (100 ms p99 / timeout 150 / deadline propagado), zero retry, breaker, fallback com assinatura do Risco e data, consumidores via Pact, donos (Diego e Marina — nominalmente), observação de métricas.
- **Fala-chave:** "A spec da Aula 3 descreve o *interior* da fronteira; este documento descreve as *arestas*. Irmãos."
- **Distinga de ADR:** "ADR é imutável e pontual; isto é vivo e versionado. E o próximo ADR numerado, o 003, só nasce quando alguém decidir mexer na escrita do ledger — e hoje não é esse dia. A `pix_a_liquidar` segue lá, única. Anotem que eu disse isso."
- **Regra do documento vivo:** "Para cada afirmação, perguntem: *o que fica vermelho se isso mentir?* Afirmação sem resposta é a parte que já morreu — ou corta, ou instrumenta."
- **Pergunte:** "Por que o fallback tem data e assinatura?" (porque é decisão de negócio com dono e validade — sem isso, volta a ser um catch anônimo).
- **Armadilha:** não escrever as 8 arestas — uma entrada completa ensina o formato; as demais são exercício.

## Bloco 10 · [112–120] · Fecho + gancho da Aula 5

**Objetivo:** três âncoras e a promessa da IA no orçamento de 100 ms.

- **Recapitule as três âncoras:** contrato é arquitetura · síncrono acopla disponibilidade, assíncrono acopla entendimento · resiliência é política declarada, não heroísmo de plantão.
- **Circule no quadro os "100 ms"** da aresta Pagamentos → Antifraude.
- **Fala de encerramento:** "Hoje, atrás dessa aresta, moram regras — limiares e listas que o Diego mantém. Na próxima aula eu conto a história de uma madrugada de outubro em que um golpe passou por todas as regras sem quebrar nenhuma. E aí a gente vai enfiar um modelo de machine learning dentro desses 100 milissegundos — e encarar a pergunta que define IA em fintech: quando o modelo diz 'talvez', quem decide?"
- **Armadilha:** não spoilar a mecânica do golpe (os R$ 49,90) — a Aula 5 abre com ela.

---

## Se sobrar tempo (buffer)

- Percorrer mais 2–3 arestas da tabela do Bloco 3 com a turma decidindo estilo e orçamento (Devoluções ↔ Pagamentos é boa: assíncrona com SLA em horas — MED p99 6 h).
- Exercício-relâmpago: "desenhem o expand/contract para mudar o **tipo** de um campo (string → objeto estruturado de valor monetário)" — mais duro que renomear; conecta ao shared kernel da Aula 3.
- Discussão: "que promessa do sistema de vocês hoje não tem métrica amarrada?" — cada aluno nomeia uma.

## Diagramas desta aula (HTML a produzir)

1. Linha do tempo do incidente da sexta-feira (19h47 → 20h51), com fila entupindo e telefone tocando antes do alerta.
2. Context map com estilos por aresta (cheia/tracejada) e orçamentos.
3. **Deadline propagation** — o carimbo de expiração viajando e encolhendo pela cadeia.
4. Fila com poison message + DLQ + medidor de lag.
5. **Expand/contract em três quadros**, com o schema registry de porteiro do CI.
6. Tabela de políticas de resiliência por aresta.
7. Balança fail-open × fail-closed com régua de valor.
8. A entrada do Contrato de Integração (Pagamentos → Antifraude) diagramada.
