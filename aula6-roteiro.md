---
layout: default
title: "Aula 6 — Roteiro (fonte)"
---

# Aula 6 — Evolução para Microsserviços com Validação

## Roteiro de condução (~120 min)

> **Duração-alvo:** 2h (com buffer no Bloco 10)
> **Callback obrigatório:** o serviço de Antifraude com GPU e perfil de escala próprio (Aula 5) como candidato nº 1 à extração — plantado desde os critérios da Aula 3, Seção 6. Pagar também: Contrato de Integração (Aula 4) como pré-condição, e o Unleash que a Aula 2 prometeu ("o mecanismo do canary").
> **Companions:** `aula6-perguntas-dificeis.md` (HTML de diagramas: a produzir)

## Visão de relance

| Bloco | Tempo | Título | O que construir no Excalidraw |
|---|---|---|---|
| 1 | 0–10 | **A história das 9h17** | Linha do tempo 14/11: deploy → canary 5% → p99 salta → rollback 90s |
| 2 | 10–22 | Por que agora: os 4 critérios | Tabela critérios (Aula 3) × estado do Antifraude, check por check |
| 3 | 22–32 | O que sai, o que fica | Mapa de contextos com Antifraude e Pagamentos saindo; Ledger com cadeado |
| 4 | 32–50 | **A migração de dados** | Coreografia expand → backfill → dual-run → contract, com o incidente do fuso |
| 5 | 50–62 | GitOps: o deploy vira ledger | Git (write model) → ArgoCD (reconciliação) → cluster (projeção) |
| 6 | 62–74 | Deploy ≠ release: flags e canary | Dial de tráfego 1%→5%→25%→100% + kill switch |
| 7 | 74–86 | **Anatomia dos 90 segundos** | A conta da Lei de Little errada vs certa (L = λ×W, os dois cenários) |
| 8 | 86–96 | O tecido contínuo de validação | Pipeline como sequência de tribunais (tabela etapa × juiz) |
| 9 | 96–110 | **O Runbook, ao vivo** | Esqueleto do Runbook de Extração preenchido com a turma |
| 10 | 110–120 | Fecho + gancho | 3 âncoras + a pergunta "quem gera essas métricas?" |

---

## Bloco 1 · [0–10] · A história das 9h17

**Objetivo:** abrir com o rollback automático como VITÓRIA, não fracasso — inverter a intuição da turma logo de cara.

- **Fala-chave:** "Dia 14 de novembro, 9h17: o canary pegou uma regressão de p99. Às 9h19, a máquina desfez o que a máquina fez. Ninguém acordou de madrugada — nem era madrugada. Uma semana depois subiu limpo. Essa aula é sobre por que isso é o melhor resultado possível."
- **Desenhe a linha do tempo:** 9h00 deploy (flag off) → 9h10 canary 1% ok → 9h15 canary 5% → 9h17 p99 80ms→2,4s → guarda viola → 9h19 rollback completo.
- **Pergunte:** "A primeira tentativa falhou. Isso foi um incidente?" (não — nenhum cliente afetado além do p99 momentâneo em 5%; incidente é erro SEM rede; aqui a rede segurou).
- **Nomeie a frase da aula:** "Extrair sem rede de validação é coragem; com rede, é rotina."
- **Armadilha:** não conte ainda POR QUE o p99 saltou — a Lei de Little fica guardada para o Bloco 7, como pagamento de suspense.

## Bloco 2 · [10–22] · Por que agora: os 4 critérios

**Objetivo:** extração como decisão por evidência, não por moda — os critérios da Aula 3 finalmente cumpridos.

- **Conduza:** retome a assimetria de Fowler da Aula 2 ("extrair cedo é caro; tarde é refactor — a assimetria favorece esperar"). Pergunta-ponte: "esperamos. Quando a espera acaba?"
- **Desenhe a tabela:** 4 critérios (fronteira estável / escala diferente / time dono / contrato pronto) × evidência do Antifraude. Marque um check por vez, contando a origem de cada evidência (Aula 3 → 4 → 5).
- **Fala-âncora:** "A fronteira sobreviveu à troca do miolo inteiro por um modelo de ML sem mudar a assinatura. Fronteira que sobrevive a isso é fronteira testada."
- **Pergunte:** "Qual critério a GPU da Aula 5 cumpre?" (escala diferente — o resto do monólito escala por CPU/IO; GPU no nó do monólito é hardware caro servindo código que não usa).
- **Armadilha:** não deixe virar checklist burocrático — cada critério é uma cicatriz de quem extraiu cedo demais e pagou.

## Bloco 3 · [22–32] · O que sai, o que fica

**Objetivo:** a decisão de NÃO extrair o Ledger como a mais arquitetural da aula.

- **Desenhe:** o mapa de contextos da Aula 3; recorte Antifraude (1º) e Pagamentos (2º) saindo como serviços; desenhe um cadeado no Contas e Ledger com a conta `pix_a_liquidar` dentro.
- **Fala-chave:** "A escrita do ledger fica no monólito, com a conta única de liquidação. A pendência do ADR-002 — 'se a contenção persistir, reparticionar' — continua aberta. E eu não vou ser eu a fechá-la."
- **Conduza os 3 motivos:** invariante transacional (rede no meio = saga/2PC sem necessidade demonstrada); p99 dentro do SLA ("incomoda não é evidência"); ledger por último, se um dia, pela equipe mais calejada.
- **Fala-âncora:** "O próximo ADR numerado, o 003, só nasce quando alguém decidir mexer na escrita do ledger — e hoje não é esse dia."
- **Pergunte:** "Por que Antifraude antes de Pagamentos?" (a aresta dele já tem fallback escrito e testado — errar ali custa degradação controlada; errar no Pagamentos custa Pix não liquidado).
- **Armadilha:** a turma vai querer discutir COMO reparticionar o ledger — corte: "essa conversa tem aula própria, e tem até dono: a Aula 8."

## Bloco 4 · [32–50] · A migração de dados

**Objetivo:** a parte que ninguém conta — dados são a extração de verdade.

**Parte A — a regra e a coreografia [32–42]**

- **Fala-chave:** "Extrair o código é a parte fácil. Todo mundo mostra caixinhas e setas; quase ninguém mostra a migração de dados."
- **Nomeie:** a regra de ouro da Aula 2 subindo de nível — "nenhum serviço lê o banco de outro. Nunca. Nem 'só essa query'." E a fitness function: usuário de banco do Antifraude sem GRANT em schema alheio (fronteira de permissão por ausência — eco da Aula 5).
- **Desenhe a coreografia:** expand (escrita dupla via Outbox — "o Outbox do ADR-002 alimentando a migração") → backfill (lotes, idempotente, retomável) → dual-run (velho decide, novo compara — "o shadow mode da Aula 5 aplicado a dados") → contract (só no fim, arquivar antes de apagar).
- **Pergunte:** "Escrita dupla não é o dual write problem que a Aula 2 proibiu?" (não — o monólito escreve UMA vez com Outbox na mesma transação; o banco novo é projeção assíncrona idempotente; ver perguntas-difíceis).

**Parte B — o incidente do fuso [42–50]**

- **Conte:** 3º dia de dual-run, divergência 0,4% — 40× o critério de 0,01%. Causa: backfill cortando janelas em meia-noite UTC vs Brasília. Correção: refazer o backfill por cima (idempotente!), divergência cai a 0,003%.
- **Fala-âncora:** "O dual-run existe para falhar cedo e barato. Esse erro em produção seria 'o antifraude anda estranho' semanas depois; no dual-run foi um número num dashboard custando zero reais."
- **Take-away:** "Migração sem reconciliação não é migração; é esperança com cronograma" — e ligue à reconciliação com o BACEN da Aula 1 (mesma disciplina, apontada para dentro).
- **Armadilha:** não deixe o incidente do fuso parecer descuido — é um desconhecido honesto que o processo foi DESENHADO para capturar.

## Bloco 5 · [50–62] · GitOps: o deploy vira ledger

**Objetivo:** a rima estrutural — Git como write model, cluster como projeção, ArgoCD como reconciliação.

- **Desenhe:** três caixas — Git (log imutável de intenções) → ArgoCD (loop: comparar/convergir) → cluster (estado materializado). Setas de reconciliação contínua.
- **Fala-chave:** "Reparem: é o ledger de novo. O commit é o lançamento; o cluster é o saldo; o ArgoCD é o job de reconciliação. Quando a mesma estrutura resolve dinheiro, extrato e infraestrutura, ela deixou de ser padrão e virou princípio."
- **Conduza as 3 consequências:** drift detection (o kubectl heroico de madrugada ou vira commit ou desaparece); rollback = git revert (mesmo mecanismo da ida, exercitado todo deploy); auditoria de graça ("o BACEN pergunta 'o que rodava dia X, quem aprovou' — a resposta é git log, não arqueologia").
- **Mostre o manifest:** o Application resumido; dedo em `selfHeal: true` e `targetRevision: main` ("a definição de produção é uma branch protegida").
- **Pergunte:** "Por que repo de deploy separado do repo de código?" (mudar o que o serviço FAZ e mudar o que está RODANDO são decisões de donos diferentes, com trilhas de auditoria diferentes).
- **Armadilha:** não escorregue para tutorial de Kubernetes — a aula é sobre o PRINCÍPIO de reconciliação, não sobre YAML.

## Bloco 6 · [62–74] · Deploy ≠ release: flags e canary

**Objetivo:** instalar a distinção-chave e a mecânica da entrega progressiva.

- **Fala-chave:** "Deploy é colocar código em produção. Release é colocar tráfego em cima dele. A engenharia de entrega moderna mora no espaço entre os dois."
- **Desenhe o dial:** rota antiga/rota nova com a flag de lançamento; progressão 1%→5%→25%→100%; ao lado, o kill switch como freio de emergência independente.
- **Conduza:** flag nasce OFF (deploy = não-evento); release = flag abrindo por fatias; guardas pré-declaradas (erro > baseline 0,1%; p99 > orçamento da aresta ~100ms); juiz automático (Argo Rollouts + Prometheus) — "reverte primeiro, notifica depois. Nessa ordem."
- **Seja honesto (fala literal):** "Quanto tempo por fatia? Cinco erros em 2.700 transações são muitos? Tem matemática séria aí — amostra, significância, o perigo de espiar antes da hora — e é o professor da Aula 8 que faz essa conta com vocês. Hoje: regras fixas e conservadoras. Grosseiro, mas grosseiro na direção segura."
- **Pergunte:** "Quem testa o kill switch, e quando?" (game day — a Aula 2 mandou testar tudo que só importa no dia ruim; kill switch não testado é decoração).
- **Armadilha:** não antecipe a estatística do canary (peeking, amostra) — é conteúdo nominal da Aula 8; aqui só o mecanismo.

## Bloco 7 · [74–86] · Anatomia dos 90 segundos

**Objetivo:** pagar o suspense do Bloco 1 com a Lei de Little — o clímax técnico da aula.

- **Conduza a conta ERRADA no quadro:** canary 5% da manhã → λ = 45 TPS; W medido NO MONÓLITO = 40ms; L = 45 × 0,04 = 1,8 conexões. Pool de 10 — "folga de 5×, parecia sobrado".
- **Vire a chave:** serviço novo = salto de rede a mais + cache local NASCENDO VAZIO → miss atrás de miss → W real ≈ 250ms. **L = 45 × 0,25 = 11,25 > pool de 10.** Esgotou.
- **Fala-âncora:** "O erro não foi a lei; foi o W de outro sistema. Lei de Little com W herdado é conta certa sobre premissa errada."
- **Conecte:** "Vocês conhecem essa espiral desde o dia 5 da Aula 2: espera de pool aumenta W, W maior aumenta L, L maior espera mais. O cotovelo da curva de filas — em miniatura, dentro de um canary de 5%. A rede segurou o que em 100% seria o dia 5 de novo."
- **Conduza as 3 correções da 2ª tentativa:** pool com W medido no dual-run + regra dos 70%; warm-up de cache no readiness ("instância só recebe tráfego quente"); progressão começando em 1%.
- **Pergunte:** "O warm-up não mascara a dependência de cache quente?" (não — a dependência foi ACEITA por escrito no Contrato de Integração, com fallback fail-closed; mascarar seria fingir que ir ao banco a cada consulta cabe no orçamento).
- **Armadilha:** não deixe a turma concluir "canary salvou, então pode errar dimensionamento" — a lição é medir W no sistema real, não terceirizar o erro para a rede.

## Bloco 8 · [86–96] · O tecido contínuo de validação

**Objetivo:** fitness functions deixam de ser evento e viram tecido — o pipeline como sequência de tribunais.

- **Desenhe o pipeline:** commit → PR (invariantes Σ, ArchUnit, GRANTs, Pact) → registry de schema → merge no repo de deploy → ArgoCD → smoke (deploy sem release) → canary com guardas → 100% → monitores contínuos (p99 por aresta, divergência de reconciliação, consumer lag).
- **Fala-chave:** "Pipeline não é esteira de empacotamento; é uma sequência de tribunais. Cada juiz veta cedo e barato; a mudança que chega a 100% passou por todos."
- **Etiquete cada juiz com a aula de origem** (1: invariantes; 2: ArchUnit/fitness; 3: schema conceito; 4: Pact/registry; 6: smoke/canary) — a turma precisa VER o curso inteiro convergindo no desenho.
- **Nomeie a semente:** "O professor das primeiras aulas chamou isso de Harness e prometeu a colheita na Aula 8. Hoje construímos a parte mecânica. Falta julgar mudanças propostas por não-humanos — e julgar com rigor estatístico. Falta exatamente uma aula... quer dizer, duas." (a 7 primeiro).
- **Armadilha:** não liste ferramenta por ferramenta como catálogo — o valor está na POSIÇÃO de cada tribunal, não na marca.

## Bloco 9 · [96–110] · O Runbook, ao vivo

**Objetivo:** escrever o artefato da aula com a turma — o Runbook de Extração como cicatriz acumulada.

- **Conduza:** projete o esqueleto vazio (Pré-condições / Plano de dados / Plano de release / Saída) e preencha perguntando à turma o que entra em cada seção — quase tudo já apareceu na aula; o exercício é RECONHECER.
- **Fala-âncora por linha-cicatriz:** "'W medido no serviço real' — de onde veio essa linha?" (9h17). "'Reconciliação diária com alerta'?" (o fuso). "'Arquivar → 30 dias → remover'?" (pressa de apagar tabela velha já perdeu mais dado que disco quebrado).
- **Conte o desfecho de Pagamentos:** semanas depois, o time da Marina extraiu o orquestrador — ACLs de DICT/SPI, timeouts do teto de 40s — seguindo o runbook. "O que eu tenho pra contar? Quase nada. Divergência de centavos na ACL pega no dual-run, canary em um dia, três parágrafos de retrospectiva. Drama tendendo a zero com risco intrínseco alto — é assim que se mede maturidade."
- **Fala-chave:** "Runbook bom não é escrito; é acumulado."
- **Pergunte:** "Por que o runbook exige remoção da flag na saída?" (flag é dívida com juros; o estado terminal saudável da flag de lançamento é não existir).
- **Armadilha:** não feche o runbook como burocracia — cada checkbox é um incidente que não vai se repetir.

## Bloco 10 · [110–120] · Fecho + gancho

**Objetivo:** as 3 âncoras e a ponte nominal para a Aula 7.

- **Recapitule as 3 âncoras:** (1) extração é evidência, não estilo — e a maior decisão foi NÃO extrair o ledger; (2) os dados são a extração de verdade — expand/contract, dual-run, reconciliação; (3) deploy ≠ release — a rede de validação é o que separa erro de incidente.
- **Fala de fecho (literal):** "Hoje, tudo foi julgado por números: o canary decidiu por métricas, o dual-run decidiu por métricas, a reconciliação alerta por métricas. Quem GERA esses números direito? Onde eles moram? E como se acha, no meio de 900 transações por segundo, o único Pix que demorou 9 segundos? Na próxima aula a gente abre a caixa que faz todo o resto ser possível: observabilidade. Tragam o pager."
- **Armadilha:** não responda nada sobre a Aula 7 — o "um Pix de 9 segundos" é gancho plantado de propósito (é a história de abertura de lá).

---

## Se sobrar tempo (buffer)

- Exercício rápido: "montem o plano de canary da extração de **Devoluções e Disputas** — quais guardas, qual fatia inicial, qual fallback?" (pega: o fluxo de MED tem SLA regulatório de 6h — a guarda não é p99 de request, é idade da fila; bom para mostrar que guarda se deriva do domínio).
- Discussão: quais dos 4 critérios **Identidade e Onboarding** já cumpre hoje? (fronteira estável sim; escala diferente não — segue no monólito, e está certo assim).
- Mostrar `git log` real do repo de deploy de um projeto qualquer como "diário de bordo de produção".

## Diagramas desta aula (HTML a produzir)

1. Linha do tempo das 9h17 (deploy → canary → violação → rollback 90s)
2. Tabela: 4 critérios da Aula 3 × evidência do Antifraude
3. Mapa de contextos com extrações e o cadeado no Ledger
4. **Coreografia da migração de dados: expand → backfill → dual-run → contract**
5. **GitOps como ledger: Git (write model) → ArgoCD (reconciliação) → cluster (projeção)**
6. Dial de release: flag + canary 1%→5%→25%→100% + kill switch
7. **A conta dos 90 segundos: L = λ×W errada (1,8) vs real (11,25 > pool 10)**
8. Pipeline como sequência de tribunais (com aula de origem de cada juiz)
9. Runbook de Extração (esqueleto para preencher ao vivo)
