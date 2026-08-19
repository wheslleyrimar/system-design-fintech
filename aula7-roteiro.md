---
layout: default
title: "Aula 7 — Roteiro (fonte)"
---

# Aula 7 — Observabilidade e Operação Inteligente

## Roteiro de condução (~120 min)

> **Duração-alvo:** 2h (com buffer embutido no Bloco 10)
> **Callback obrigatório:** o canary da Aula 6 decide com base em métricas — mas quem gera essas métricas direito? Esta aula paga essa promessa. Segundo callback: o dia 5 da Aula 2 (o TechPix que afundou) contrastado com o dia 5 desta aula (o TechPix que aguentou o recorde nacional).
> **Companions:** `aula7-perguntas-dificeis.md` · HTML de diagramas: a produzir

## Visão de relance

| Bloco | Tempo | Título | O que construir no Excalidraw |
|---|---|---|---|
| 1 | 0–8 | O dia 5 que não doeu | Linha do tempo do 5/12/2025: 313,3 mi nacional, 900 TPS na TechPix, painel verde |
| 2 | 8–18 | A reclamação da Ana: 9 segundos verdes | Média 1,9s · p99 3,4s · e um ponto vermelho fora de tudo |
| 3 | 18–30 | Monitorar vs observar + os três pilares | Tabela das 3 perguntas: quanto? / o quê? / por onde? |
| 4 | 30–44 | Métricas: RED, USE, percentis, cardinalidade | RED por serviço + a conta dos 100 milhões de séries |
| 5 | 44–56 | Logs estruturados e o presente do BACEN | JSON de log + E2E ID costurando 4 serviços |
| 6 | 56–72 | **Tracing: a caça aos 9 segundos** | O trace da Ana, span a span, com o elefante de 6,9s |
| 7 | 72–84 | Monitorando o modelo: drift e fallback | Painel do Diego: 4 famílias de métricas de inferência |
| 8 | 84–98 | SLO e error budget: a moeda de release | Cadeia SLI→SLO→budget + burn rate |
| 9 | 98–110 | Incidentes e postmortem blameless | Template do postmortem do caso Ana (4 fatores, 4 ações) |
| 10 | 110–120 | **Catálogo de SLOs + o sinal que ninguém lê** | A tabela de 5 meses do p99 do ledger, subindo |

---

## Bloco 1 · [0–8] · O dia 5 que não doeu

**Objetivo:** abrir com um anti-incidente — o contraste entre o dia 5 da Aula 2 e o 5/12/2025 é o argumento de venda da aula inteira.

- **Fala-chave:** "Deixa eu começar de um jeito que nenhuma aula desse curso começou: sem incidente."
- **Desenhe o Diagrama 1:** linha do tempo do dia do recorde — 313,3 milhões de transações no país (o número da Aula 1!), pico de 900 TPS na TechPix (a previsão da Lei de Little, cravada), utilização parando em 65%, abaixo da regra dos 70%.
- **Conecte:** Rafael, o on-call, passou o dia sem uma página. Canary de Devoluções progrediu 1%→100% no meio do pico como rotina.
- **Fala-âncora:** "A diferença entre aquele dia 5 e este não é sorte — é que agora a gente enxerga."
- **Armadilha:** não deixe virar autoelogio de ferramenta; o ponto é que enxergar tem disciplina e custo, e a aula ensina os dois.

## Bloco 2 · [8–18] · A reclamação da Ana: 9 segundos verdes

**Objetivo:** instalar o paradoxo que conduz a aula — a reclamação real que os painéis juram que não existe.

- **Conduza:** no fim da tarde gloriosa, chega um ticket. A cliente é a Ana — a mesma das 2h47 da Aula 1. Pix para uma confeitaria recém-aberta: 9 segundos. Não falhou, não duplicou (idempotência segue firme) — mas 9 segundos para quem se acostumou com 2 é pânico.
- **Desenhe o Diagrama 2:** os agregados do dia (média 1,9s · p99 3,4s · erro 0,08%) todos verdes — e um ponto vermelho solitário fora da curva.
- **Pergunte:** "Pelo painel, esse Pix existe?" (não — média linda, p99 dentro do SLO; e é exatamente esse o problema).
- **Fala-âncora:** "Como se encontra uma agulha que a média jura que não está no palheiro?"
- **Armadilha:** não resolva o mistério agora; ele é o fio dos Blocos 5 e 6. Segure a ansiedade da turma.

## Bloco 3 · [18–30] · Monitorar vs observar + os três pilares

**Objetivo:** separar os dois conceitos e apresentar os pilares como três perguntas, não três produtos.

- **Nomeie:** monitoramento responde perguntas que você previu (known unknowns); observabilidade responde perguntas que você ainda não fez (unknown unknowns).
- **Fala-chave:** "'Por que o Pix da Ana das 16h41 levou 9 segundos?' — essa pergunta não estava em dashboard nenhum. Se o sistema é observável, a resposta está lá dentro esperando a pergunta."
- **Desenhe o Diagrama 3:** tabela dos três pilares como perguntas — métrica = "quanto?", log = "o que exatamente?", trace = "por onde?" — com custo relativo de cada um.
- **Take-away:** os três pilares não competem; eles se revezam na mesma investigação.
- **Armadilha:** a turma vai querer discutir ferramenta (Grafana vs Datadog). Corte: observabilidade é propriedade do sistema, não da ferramenta.

## Bloco 4 · [30–44] · Métricas: RED, USE, percentis, cardinalidade

**Objetivo:** o essencial de métricas com as três pegadinhas que derrubam times no primeiro ano.

- **Conduza — Parte A [30–36]:** RED por serviço (Rate, Errors, Duration) sobre a malha pós-Aula 6; USE por recurso. Conecte à Aula 2: saturação é o vigia do cotovelo ρ/(1−ρ) — fila avisa antes da utilização machucar.
- **Nomeie:** duas métricas de primeira classe da TechPix: consumer lag (cicatriz da Aula 4) e contenção de lock em `pix_a_liquidar` (cicatriz da Aula 2). "Guardem a segunda — ela volta no fim da aula."
- **Conduza — Parte B [36–44]:** percentis: coleta em histograma; **percentil não se agrega por média** (p99 de 200ms + p99 de 2s ≠ 1,1s); a 900 TPS, 1% além do p99 = 540 transações/minuto invisíveis.
- **Desenhe o Diagrama 4:** a conta da cardinalidade: 10 endpoints × 5 códigos = 50 séries; + `conta_id` (2 mi contas) = 100 milhões de séries. O Prometheus não morre de tráfego; morre de cardinalidade.
- **Regra prática:** métrica é para agregado; identificador é para log e trace. "Essa pergunta se responde com outro pilar."
- **Armadilha:** não deixe a turma sair achando que p99 basta — o gancho do Bloco 6 é justamente o que o p99 não vê.

## Bloco 5 · [44–56] · Logs estruturados e o presente do BACEN

**Objetivo:** log como evento de máquina, correlação obrigatória, e a revelação do E2E ID.

- **Desenhe o Diagrama 5:** o JSON de log do retry da feature store (mostrar campos: `e2e_id`, `tentativa`, `timeout_ms`, `chave_pix: [MASCARADO]`).
- **Fala-âncora:** "O regulador obrigou a TechPix a ter rastreamento distribuído antes de a gente saber o nome disso." O EndToEndId da Aula 1 — o mesmo da idempotência e da reconciliação — é o ID de correlação natural de todo o fluxo Pix.
- **Pergunte:** "O que NUNCA entra num log de fintech?" (chave Pix, CPF, credencial — LGPD; mascaramento na biblioteca central, verificado por fitness function no CI, no espírito da Aula 2).
- **Conduza:** sampling com viés — 100% de erros/warnings, fração do caminho feliz; trace amostrado retém seus logs. Distinga: log operacional se amostra; ledger (registro contábil) jamais.
- **Armadilha:** alguém vai propor "logar tudo em DEBUG e filtrar depois". Resposta: DEBUG vaza para produção no primeiro incidente, e a fatura de armazenamento chega antes.

## Bloco 6 · [56–72] · Tracing: a caça aos 9 segundos (clímax)

**Objetivo:** resolver o mistério da Ana ao vivo, span a span — o momento mais forte da aula.

- **Conduza — Parte A [56–62]:** OpenTelemetry: trace = jornada, span = segmento aninhado; propagação de contexto (`traceparent` W3C) pega carona na mesma infraestrutura do deadline propagation da Aula 4. Amostragem na cauda: 100% dos lentos/erros retidos — "a agulha já estava separada do palheiro quando caiu".
- **Desenhe o Diagrama 6 — Parte B [62–72]:** o trace da Ana, linha a linha: DICT 38ms (cache!), ledger 58ms, SPI 2,1s… e o elefante: **6,9s no Antifraude — 4 tentativas × 1,5s de timeout + backoffs 100/200/400ms contra a feature store**.
- **Revele a causa-raiz:** conta da confeitaria recém-criada → cold start de features → biblioteca legada com timeout e retry próprios, surda ao deadline de 100ms da Aula 4. E o detalhe fino: **o fallback fail-closed da Aula 5 nunca disparou** — a feature store nunca "falhou de vez", ficou quase-respondendo até a 4ª tentativa.
- **Fala-âncora:** "Retry esconde falha; deadline revela. A média mente, o p99 esconde, o trace confessa."
- **Pergunte:** "Por que nenhuma métrica gritou?" (contas novas = 0,002% do tráfego — não move nem o p99,9; o agregado protege o sistema, não cada cliente).
- **Nomeie:** exemplar — o link do balde do histograma para o trace; e a métrica nova criada no dia seguinte (`feature_store_cold_start`, etiqueta `conta_tipo`, cardinalidade 2). "Cada investigação transforma uma pergunta nova em um medidor permanente."
- **Armadilha:** não deixe a discussão virar "de quem foi a culpa" — guarde essa energia para o Bloco 9.

## Bloco 7 · [72–84] · Monitorando o modelo: drift e fallback

**Objetivo:** estender a observabilidade ao componente não-determinístico da Aula 5.

- **Fala-âncora:** "Modelo não quebra com stack trace; ele apodrece em silêncio. A métrica é o exame de sangue — você não espera o infarto para medir a pressão."
- **Nomeie:** drift de dados (a entrada mudou) vs drift de conceito (a relação entrada→resposta mudou).
- **Desenhe o Diagrama 7:** o painel do Diego, 4 famílias — distribuição do score vs referência; distribuição por feature; taxa de fallback + p99 de inferência (a métrica que faltou no caso da Ana!); sombra × ativo.
- **Conduza:** o problema do ground truth atrasado — o rótulo verdadeiro chega com o MED, semanas depois; por isso tudo acima é indicador antecedente, e os rótulos fecham o ciclo depois.
- **Plante (sutil):** "Produção gera sinal, sinal vira avaliação, avaliação vira decisão. Guardem esse desenho de ciclo — o professor que volta na próxima aula vai generalizá-lo, e vocês vão perceber que já o conheciam."
- **Armadilha:** não entre em como retreinar modelo — é curso de arquitetura, não de ML; a fronteira é a métrica e a política de decisão.

## Bloco 8 · [84–98] · SLO e error budget: a moeda de release

**Objetivo:** a cadeia SLI→SLO→SLA e o error budget como mecanismo político-matemático.

- **Nomeie:** SLI = a medição; SLO = a meta interna; SLA = a promessa externa com consequência. Regra: SLO interno sempre mais apertado que SLA externo (TechPix: 99,95% e 3,5s internos sob o teto regulatório de 40s e o índice BACEN da Aula 1).
- **Desenhe o Diagrama 8:** 99,95% em 30 dias = **21,6 minutos de error budget**. Budget sobrando → pode ousar (extrair serviço, canary agressivo); budget queimado → congela release arriscado.
- **Fala-âncora:** "A guerra entre quem quer lançar e quem quer estabilidade deixa de ser opinião e vira aritmética combinada de antemão."
- **Conecte à Aula 6:** o canary decidia com limiares fixos (erro > 0,1%, p99); o error budget dá contexto de negócio a esses limiares.
- **Conduza:** alertar no sintoma, não na causa — CPU a 90% no serviço de GPU é terça-feira normal; burn rate é o único alerta que merece acordar o Rafael, porque carrega prova matemática. Queima lenta = ticket de horário comercial.
- **Pergunte:** "Alerta de fila do pool enchendo: página ou dashboard?" (warning de horário comercial — saturação antecipa, mas sem cliente sofrendo não se acorda ninguém).
- **Armadilha:** a objeção "e a meta de 100% do BACEN?" tem resposta pronta no guia de perguntas difíceis — o próprio regulador usa valores de referência de 80–90%; meta inatingível interna destrói a régua.

## Bloco 9 · [98–110] · Incidentes e postmortem blameless

**Objetivo:** fechar o caso da Ana como processo: severidades, runbook, postmortem.

- **Conduza:** dois canais legítimos de investigação — o alerta quantitativo e a voz do cliente. O caso da Ana entrou pelo segundo, e não deveria mesmo ter alertado (0,002% não queima budget). Severidades: SEV1 (dinheiro errado / fluxo fora — sala de guerra), SEV2 (degradação com cliente sofrendo), SEV3 (caso da Ana). Runbook escrito de cabeça fria; kill switch da Aula 6 como arma do on-call.
- **Fala-âncora:** "O postmortem é o ADR do incidente — imutável, datado, e sem culpados."
- **Desenhe o Diagrama 9:** o postmortem do caso Ana: linha do tempo + 4 fatores contribuintes (biblioteca fora da disciplina da Aula 4; nenhuma fitness function proibindo retry próprio; fallback cego a degradação; métrica de cold start inexistente) + 4 ações com dono e prazo. Nenhum nome no banco dos réus.
- **Pergunte:** "Punir o dev da biblioteca antiga preveniria o próximo incidente?" (não — produziria silêncio; quem esconde quase-acidente mata a informação que previne a repetição; responsabilidade blameless = dono da ação corretiva, não réu do erro).
- **Nomeie:** MTTR > MTBF — falha é regime permanente com SPI/DICT/Banco Beta no caminho; otimizar recuperação, não perfeição. No núcleo (ledger, Σ) vale o contrário — é o "forte no núcleo, eventual na borda" da Aula 1 virando filosofia de operação.
- **Armadilha:** não deixe "blameless" virar caricatura de impunidade — a fronteira (negligência repetida é gestão, não postmortem) está no guia de perguntas difíceis.

## Bloco 10 · [110–120] · Catálogo de SLOs + o sinal que ninguém lê (gancho Aula 8)

**Objetivo:** escrever o artefato da aula ao vivo e armar o gancho final do curso.

- **Escreva ao vivo (Diagrama 10a):** o Catálogo de SLOs da TechPix — por linha: SLI, SLO, budget, dono (Pix ponta a ponta 99,95%/3,5s; ledger p99 ≤ 80ms; lag do extrato ≤ 300ms; antifraude ≤ 100ms + fallback ≤ 0,5%; DICT herdado ≤ 1s). Frise: artefato da família da spec — "o próximo ADR numerado, o 003, só nasce quando alguém decidir mexer na escrita do ledger — e hoje não é esse dia."
- **Desenhe o Diagrama 10b — o final:** a série de 5 meses: p99 de escrita do ledger 42→45→49→54→58ms; contenção do lock 3,1%→7,2%; TPS 410→700. Tudo verde. Tudo subindo.
- **Fala-âncora:** "Isso não é um incidente. Não viola SLO. Não acorda o Rafael. É uma tendência lenta que um dia cruza um limiar — e a linha 'Revisão' do ADR-002 está persistindo nos meus dashboards, não mais como hipótese."
- **Pergunte (e deixe no ar):** "Quem lê esse sinal? Um humano esquece, um alerta não dispara para tendência, uma reunião trimestral olha para trás." (não responda — É o gancho.)
- **Encerramento literal:** "O sistema agora produz evidência de sobra. O que falta é o leitor. Na próxima aula, o professor que abriu esse curso volta para apresentá-lo — e fechar o círculo: da fé, na Aula 1, para a evidência, na Aula 8."
- **Armadilha:** não diga "agente de IA" — a revelação é da Aula 8. O máximo permitido: "uma categoria nova de leitor".

---

## Se sobrar tempo (buffer)

- Aprofundar amostragem híbrida (cabeça + gatilho na cauda) para componentes de altíssimo volume.
- Exercício-relâmpago: dar 3 alertas reais ("CPU 92%", "burn rate 14× na janela de 1h", "fila do consumidor de extrato crescendo há 20 min") e a turma classifica: página, ticket ou dashboard? (dashboard/diagnóstico · página · ticket de horário comercial).
- Mostrar um exemplar funcionando: do balde 5–10s do histograma direto para o trace da Ana.
- Discussão: quais das 4 ações do postmortem da Ana são fitness functions? (a proibição de retry próprio no CI — conexão direta com a Aula 2.)

## Diagramas desta aula (HTML a produzir)

1. Linha do tempo do 5/12/2025 — o dia 5 que não doeu (contraste com o dia 5 da Aula 2)
2. Os agregados verdes e o ponto vermelho da Ana
3. Os três pilares como três perguntas
4. A conta da cardinalidade (50 séries → 100 milhões)
5. O log estruturado com E2E ID costurando os serviços
6. **O trace da Ana, span a span (clímax — 6,9s no Antifraude)**
7. O painel de inferência do Diego (4 famílias)
8. SLI→SLO→error budget + burn rate
9. O postmortem blameless do caso Ana (4 fatores, 4 ações)
10. **O Catálogo de SLOs + a série de 5 meses do ledger subindo (gancho Aula 8)**
