---
layout: default
title: "Aula 5 — Roteiro (fonte)"
---

# Aula 5 — Núcleo da Fintech com IA e Agentes

## Roteiro de condução (~120 min)

> **Duração-alvo:** 2h, com buffer no fim.
> **Callback obrigatório:** o orçamento de ~100 ms no p99 da chamada síncrona Pagamentos→Antifraude, declarado no Contrato de Integração da Aula 4 — hoje esse orçamento ganha um inquilino (o modelo). Retomar também: fail-open/fail-closed (Aula 4), Outbox/CQRS (Aula 2), "falhar fechado" e a regra "o agente lê, propõe, mas nunca move dinheiro" (Aula 1).
> **Companions:** `aula5-perguntas-dificeis.md` (HTML de diagramas: a produzir).

## Visão de relance

| Bloco | Tempo | Título | O que construir no Excalidraw |
|---|---|---|---|
| 1 | 0–10 | **O golpe dos R$ 49,90** | Linha do tempo da madrugada: dezenas de contas, rajadas de valores idênticos, regras dizendo "inocente" |
| 2 | 10–22 | Regra vs. modelo | Dois planos: regras como retas cortando o espaço; o padrão do golpe passando entre elas |
| 3 | 22–34 | **O modelo sugere, a regra decide** | As 3 camadas (regras duras → modelo → política) + a tabela da política de decisão |
| 4 | 34–50 | O orçamento de 100 ms | Decomposição do orçamento (rede, features, inferência, folga) empilhada dentro da barra dos 100 ms |
| 5 | 50–64 | Feature store | Rio de eventos do Outbox alimentando loja online + loja offline; treino vs. inferência |
| 6 | 64–74 | Modelos abertos vs. API | Tabela de trade-offs; a linha divisória "dado sensível dentro / borda fora" |
| 7 | 74–88 | **Shadow mode** | Dois vereditos por transação (real × hipotético); o quadrante de divergências |
| 8 | 88–102 | **MCP e a manhã da Carla** | As 6 telas da Carla → copiloto com cardápio de ferramentas MCP (só leitura); a ferramenta que NÃO existe |
| 9 | 102–114 | O artefato: Model Card + Política | Escrever o Model Card ao vivo, campo a campo |
| 10 | 114–120 | Fecho e gancho | As 3 âncoras + Antifraude pronto para extração (Aula 6) |

---

## Bloco 1 · [0–10] · O golpe dos R$ 49,90

**Objetivo:** abrir com o incidente que nenhuma regra pegou — e que funcionou sem nada quebrar.

- **Fala-chave:** "Na Aula 4 o sistema quebrou sem ninguém errar. Hoje é pior: o sistema funcionou perfeitamente — e foi assim que ele falhou."
- **Desenhe a linha do tempo:** 2h31 da madrugada de 3/out (ecoar as 2h47 da Ana, Aula 1), dezenas de contas laranja com KYC válido, centenas de Pix de R$ 49,90, cada checagem de regra respondendo "inocente".
- **Pergunte:** "Que regra vocês escreveriam para pegar isso — sem bloquear o churrasco de domingo que também gera rajada de Pix pequenos?" (deixar a turma tentar e falhar: cada regra proposta ou tem furo ou tem falso positivo — esse desconforto é o motor da aula).
- **Nomeie:** "O fraudador não quebra regras. Ele explora o **espaço entre as regras**."
- **Fala-âncora:** "**Regra pega o golpe de ontem; padrão pega o golpe de hoje.**" (frase do Diego na parede — escrever grande, ela volta o tempo todo).
- **Armadilha:** não deixar a turma concluir "então IA resolve fraude". O MED e o bloqueio cautelar contiveram o prejuízo — o trilho regulatório da Aula 1 continua sendo a rede final.

## Bloco 2 · [10–22] · Regra vs. modelo

**Objetivo:** estabelecer por que modelo complementa (e não substitui) regra.

- **Desenhe o espaço de decisão:** eixos (valor × frequência, simplificado); regras como retas cortando o plano; o cluster do golpe passando entre as retas; a superfície curva do modelo envolvendo o cluster.
- **Conduza:** as 3 virtudes da regra (explicável, rápida, determinística) — nenhuma delas negociável em fintech; o limite estrutural (regra enxerga o que o autor previu; o espaço de fraude é combinatório).
- **Fala-chave:** "Cada regra nova fecha um vão e ilumina, para o fraudador, onde ficam os outros."
- **Pergunte:** "O modelo precisa ter visto uma rajada de R$ 49,90 no treino para pegá-la?" (não — ele aprende a região do espaço onde a combinação de sinais mora; generalização é o ponto).
- **Armadilha:** não entrar em arquitetura de rede neural / algoritmo de treino. O curso é de System Design: o modelo é um componente com contrato, latência e modos de falha.

## Bloco 3 · [22–34] · O modelo sugere, a regra decide

**Objetivo:** a frase mais importante da aula, materializada na política de decisão.

- **Fala-âncora:** "**O modelo não decide nada. Nunca.** Ele produz um número. Quem converte número em ação é uma tabela determinística, versionada, com dono."
- **Desenhe as 3 camadas** na ordem de travessia: regras duras (µs) → modelo (ms) → política (µs). Transação barrada na camada 1 nem chega ao modelo.
- **Desenhe a tabela da política** (score × valor → ação) e circule as duas últimas linhas: score indisponível → fail-open ≤ R$200, fail-closed acima. "As linhas mais importantes são as que tratam o silêncio do modelo."
- **Conecte:** fail-open/fail-closed é decisão de NEGÓCIO (Aula 4); "falhar fechado" no valor alto é lei desde a Aula 1.
- **Conduza (LGPD/BACEN):** explicar a decisão ≠ explicar os pesos. "Score 912, política v14, linha 4" é auditável; "o modelo achou" não é. **Explicabilidade mora na política.**
- **Pergunte:** "Por que quem calibra o limiar da política não deve ser o mesmo time que treina o modelo?" (contrapeso de incentivo: afinar política para esconder fraqueza do modelo precisa ter atrito).
- **Armadilha:** plateia vai querer discutir XAI/interpretabilidade de modelo. Reconheça que existe, e devolva: o compromisso regulatório exigível está na política — não prometa explicar neurônio.

## Bloco 4 · [34–50] · O orçamento de 100 ms

**Objetivo:** inferência em tempo real como problema de orçamento de latência — o callback da Aula 4 pago em números.

- **Desenhe a barra dos 100 ms** e empilhe: rede ~5 · regras duras ~1 · features 10–15 · inferência 10–20 · política ~1 · **folga ~60**.
- **Fala-chave:** "A folga não é gordura — é o que separa o p50 do p99. Quem orça o caso típico em 80 dos 100 mora em violação."
- **Conduza:** a inferência NÃO é a fatia maior — o modelo de score é um classificador especializado (10–20 ms), não um LLM; a fatia perigosa é a busca de features.
- **Pergunte:** "O que acontece quando o deadline vence sem score?" (deadline propagation da Aula 4 → política executa as linhas de fallback; latência imprevisível vira falha previsível — filosofia de circuit breaker).
- **Regra prática:** monitorar a taxa de acionamento do fallback — "raríssima → rotineira" é problema de capacidade, não de arquitetura.
- **Armadilha:** não deixar passar a ideia de "chamar um LLM por API no caminho crítico do Pix". Fazer a conta na hora se alguém propuser: p99 de API externa × 900 TPS × orçamento de 100 ms — não fecha.

## Bloco 5 · [50–64] · Feature store: o rio vira alimento

**Objetivo:** a decisão de arquitetura mais bonita da aula — features prontas, alimentadas pelo Outbox.

- **Pergunte primeiro:** "A feature 'Pix recebidos na última hora' — como ela fica pronta em 10 ms sem varrer o ledger?" (não pode varrer: leitura pesada no caminho de escrita foi a causa raiz do dia 5, Aula 2).
- **Desenhe:** `PixLiquidado` saindo do Outbox → consumidor idempotente (dedup por EndToEndId, Aula 4) → loja **online** (valor atual, chave-valor, ms) + loja **offline** (histórico, serve o treino).
- **Fala-chave:** "É CQRS de novo. A loja online é mais um read model — só que quem lê não é o extrato da Ana, é o modelo do Diego."
- **Conduza a honestidade:** atraso eventual de 100–300 ms na loja online → rajadas de segundos exploram a janela → por isso as regras duras (contadores transacionais) ficam NA FRENTE. "Camada rápida e burra na frente; camada lenta e esperta atrás."
- **Desenhe a tabela treino × inferência** (quando, dados, latência, hardware, falha) e o registro de modelos como o artefato-ponte: "'Qual modelo decidiu?' precisa de resposta tão precisa quanto 'qual versão do código estava no ar?'"
- **Armadilha:** não introduzir produto/vendor de feature store; é um padrão, não uma compra.

## Bloco 6 · [64–74] · Modelos abertos vs. API

**Objetivo:** onde o peso mora se decide por sensibilidade do dado, não por moda.

- **Contextualize:** o score é modelo pequeno treinado em casa — a questão aberto×API nasce quando o TechPix quer linguagem (dossiês, PLD-FT, copiloto).
- **Desenhe a tabela de trade-offs:** LGPD / latência / custo em escala / capacidade / operação.
- **Fala-âncora:** "**Núcleo com dado sensível → modelo aberto, dentro de casa. Borda sem dado sensível → API pode.** É o 'forte no núcleo, eventual na borda' da Aula 1, transplantado."
- **Nomeie:** quantização e destilação — os dois botões que fazem modelo aberto caber no orçamento (sem entrar em como treinar).
- **Pergunte:** "Anonimizar e mandar pra API resolve?" (grafo de contas anonimizado de verdade deixa de ser útil; pseudonimizado continua dado pessoal — a ginástica jurídica não fecha no núcleo).
- **Armadilha:** não deixar virar debate ideológico open source × big tech. Critério: sensibilidade do dado e criticidade da decisão, caso a caso.

## Bloco 7 · [74–88] · Shadow mode

**Objetivo:** confiança em componente não-determinístico se constrói por observação.

- **Pergunte de abertura:** "Métricas offline lindas. Liga o modelo na política amanhã?" (deixar o desconforto responder).
- **Desenhe:** cada transação gerando DOIS vereditos — real (regras decidem) × hipotético (modelo, registrado e ignorado); o quadrante de divergências (modelo bloquearia/regra passou; regra bloquearia/modelo passaria) com cada divergência indo a análise humana.
- **Fala-chave:** "Falso positivo em pagamento não é estatística — é cliente com Pix travado às 2h da manhã. É incidente de confiança."
- **Conte o fecho do círculo:** rodada de sombra sobre o histórico de setembro acende o golpe dos R$ 49,90 retroativamente. Honestidade: isso não prova que pega o *próximo* golpe — prova que enxerga uma classe de padrão que regra nenhuma cobria.
- **Conecte para frente:** "Rodar o novo ao lado do velho, com tráfego real, antes de dar poder de decisão — guardem o desenho. Semana que vem ele se chama canary." (Só a semente; a mecânica é da Aula 6, a matemática é da Aula 8.)
- **Plante a inquietação da Aula 7:** "E quando o modelo é quem decide e o mundo muda — como saber se ele continua bom? Modelo não quebra com stack trace. Segurem essa pergunta duas semanas."
- **Armadilha:** não antecipar estatística de canary (tamanho de amostra, significância) — território da Aula 8.

## Bloco 8 · [88–102] · MCP e a manhã da Carla

**Objetivo:** o outro lado do balcão — IA ajudando humano a decidir; fronteira de permissão por ausência.

- **Apresente a Carla** e desenhe as 6 telas dela: histórico, cadastro (Identidade), grafo de contas (o mesmo da Recuperação de Valores, Aula 1), casos similares, fila do MED, marcações do DICT. "Vinte minutos montando contexto, cinco decidindo."
- **Desenhe o copiloto:** LLM aberto rodando dentro de casa (Bloco 6 aplicado) + cardápio de ferramentas via **MCP** (retomar a sigla da Aula 1): `consultar_historico`, `casos_similares`, `grafo_de_contas`, `status_med` — cada contexto expõe um servidor de LEITURA.
- **Fala-âncora:** "No cardápio do copiloto **não existe** `bloquear_conta`. Não é instrução no prompt — é **ausência estrutural de capacidade**. Fronteira de permissão por ausência."
- **Conduza:** dossiê com evidência citada e linkada → alucinação vira constrangimento detectável, não decisão errada; quem clica em "bloquear" é a Carla, autenticada e auditada como ela.
- **Pergunte:** "Por que a proteção 'a ferramenta não existe' é mais forte que 'o prompt manda não usar'?" (prompt é pedido; cardápio é capacidade — e o manifesto de ferramentas é configuração versionada com fitness function no pipeline).
- **Marque a porta fechada:** "Agente lendo métricas de produção e specs, propondo evolução da ARQUITETURA — a extrapolação está certa, e é a Aula 8, quando o professor de vocês volta. Hoje os princípios ficaram prontos."
- **Armadilha:** não demonstrar prompt/ferramenta de LLM ao vivo; o assunto é a fronteira arquitetural, não o produto.

## Bloco 9 · [102–114] · O artefato: Model Card + Política de Decisão

**Objetivo:** registrar a governança do componente não-determinístico — o irmão da spec da Aula 3.

- **Escreva o Model Card ao vivo,** campo a campo: propósito, o que o modelo vê, **o que NUNCA vê** (raça, CEP como proxy — com checagem automática da lista de features a cada versão: fitness function da Aula 2 com alvo novo), desempenho (p99 ≤ 20 ms), fallback (linhas 5–6 da política), auditoria (versão do modelo + versão da política + score + ação + EndToEndId), limites conhecidos, donos por camada.
- **Fala-chave:** "A lista de features é decisão de **governança**, não detalhe de engenharia."
- **Pergunte:** "Por que registrar 'limites conhecidos' por escrito em vez de alegar neutralidade?" (limites escritos são defensáveis e acionáveis; neutralidade alegada não se sustenta em auditoria).
- **Nomeie o não-ADR:** "O próximo ADR numerado, o 003, só nasce quando alguém mexer na escrita do ledger — e hoje não é esse dia." (Gancho silencioso para a Aula 8.)
- **Armadilha:** não deixar o Model Card virar burocracia decorativa — cada linha respondeu a uma objeção real da aula (fallback→Bloco 4, features vetadas→viés, auditoria→LGPD/BACEN).

## Bloco 10 · [114–120] · Fecho e gancho

**Objetivo:** as 3 âncoras e a ponte para a extração.

- **Recapitule:** (1) o modelo sugere, a regra decide — explicabilidade mora na política; (2) inferência é problema de orçamento — feature store alimentada pelo rio de eventos; (3) confiança por observação — sombra, fronteira por ausência, humano no irreversível.
- **Fala de encerramento (gancho pra Aula 6):** "O Antifraude agora tem GPU, retreino mensal, perfil de tráfego próprio e um contrato maduro na frente. Ele não cabe mais no monólito — os critérios do professor da Aula 3 estão ficando verdes um a um. Semana que vem a gente tira ele de lá, ao vivo, com rede embaixo. E eu já aviso: a primeira tentativa vai dar errado — do jeito certo."

---

## Se sobrar tempo (buffer)

- Exercício rápido: dar 3 transações fictícias (valores/horários/idades de conta) + a tabela da política, e pedir a ação de cada uma — inclusive uma com score indisponível (testa se fixaram as linhas de fallback).
- Discussão: "que feature vocês proporiam para o modelo — e qual vocês teriam vergonha de defender diante do regulador?" (aquece governança de features).
- Voltar ao quadrante de divergências da sombra e perguntar qual dos dois lados (modelo mais rígido × regra mais rígida) custa mais caro para o TechPix — e por quê a resposta muda com o valor da transação.

## Diagramas desta aula (HTML a produzir)

1. Linha do tempo do golpe dos R$ 49,90 (2h31, contas laranja, rajadas).
2. Espaço de decisão: regras como retas × superfície do modelo envolvendo o cluster do golpe.
3. **As 3 camadas: regras duras → modelo → política de decisão (com a tabela).**
4. **A barra dos 100 ms decomposta (rede/regras/features/inferência/folga).**
5. Feature store: Outbox → consumidor idempotente → loja online + loja offline; treino × inferência; registro de modelos.
6. Tabela de trade-offs modelo aberto × API, com a linha divisória núcleo/borda.
7. **Shadow mode: dois vereditos por transação e o quadrante de divergências.**
8. **A manhã da Carla: 6 telas → copiloto MCP com cardápio só-leitura (e a ferramenta que não existe).**
9. Model Card + Política de Decisão (o artefato, campo a campo).
