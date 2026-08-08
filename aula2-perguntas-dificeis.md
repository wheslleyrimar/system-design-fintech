---
layout: default
title: "Aula 2 — Guia de perguntas difíceis"
---

# Aula 2 — Guia de perguntas difíceis
*Munição de embasamento para quando a plateia técnica empurrar.*

---

## Sobre monólito vs microsserviços

**"A gente já está em microsserviços há dois anos. Essa aula é sobre o quê, então — dizer que erramos?"**

Não. A aula é sobre **por que** as fronteiras estão onde estão, e se elas ainda fazem sentido. Times que já estão em microsserviços têm uma versão diferente do mesmo problema: fronteiras que foram desenhadas por conveniência organizacional (um serviço por time) em vez de por domínio, e que agora produzem chamadas em cadeia — o famoso "para exibir uma tela eu chamo sete serviços". O conteúdo do dia 5 se aplica igual, só que a contenção aparece em outro lugar: no serviço que todos os outros precisam chamar. Se isso soa familiar, a Aula 3 é a que mais vai servir a vocês.

**"'Monolith first' não é conselho datado? Hoje ferramenta de infraestrutura tornou microsserviço muito mais barato."**

O custo que caiu foi o de **operar** — provisionar, deployar, observar. O custo que **não** caiu é o de raciocinar sobre um sistema distribuído: falha parcial, consistência eventual entre serviços, depuração de uma transação que atravessa seis processos. E, mais importante, não caiu o custo de **mover uma fronteira errada**: refatorar entre dois módulos no mesmo processo é um dia de trabalho; entre dois serviços com bancos separados e contratos publicados, é um projeto de trimestre. O argumento do "monolith first" nunca foi sobre custo de infraestrutura — é sobre reversibilidade da decisão de fronteira.

## Sobre a curva de filas

**"Essa fórmula ρ/(1−ρ) assume distribuição de chegada aleatória (M/M/1). Meu tráfego não é aleatório — tem padrão diário claro. A fórmula vale?"**

Excelente objeção, e a resposta é: a fórmula exata não, o **comportamento** sim. Modelos de fila mais realistas (com múltiplos servidores, ou variabilidade de serviço diferente) mudam os coeficientes, mas todos preservam a propriedade central — a espera cresce de forma não-linear e explode perto da saturação. O padrão diário do tráfego não elimina a curva; ele só diz **quando** você chega perto do cotovelo. Na prática, a fórmula simples serve como intuição de ordem de grandeza e como argumento para não operar acima de 70%; ela não serve para prever o p99 exato — para isso, teste de carga.

**"70% de utilização como teto significa desperdiçar 30% da infraestrutura. Como eu justifico esse custo?"**

Reformulem a pergunta para a diretoria: não é "30% de desperdício", é "o preço de não ficar fora do ar no dia de maior receita do mês". E dê o número: a diferença entre operar a 70% e a 95% é a diferença entre um fator de espera 2,3 e um fator 19 — oito vezes mais lento, com a mesma infraestrutura mais carregada. Além disso, num sistema financeiro, existe o argumento regulatório: o índice de disponibilidade é monitorado pelo BACEN, e furá-lo tem consequência formal, não só reputacional. A folga não é desperdício; é conformidade.

## Sobre retry storm

**"Se eu implementar retry budget e parar de retentar, não estou desistindo de transações que poderiam ter sucesso?"**

Sim, algumas. E é a escolha certa. Pensem no contrafactual: sem o budget, aquelas retentativas aumentam a carga, o que aumenta a latência de **todas** as transações, o que gera mais timeouts, o que gera mais retentativas. Você não está escolhendo entre "salvar essas transações" e "perder essas transações" — está escolhendo entre "perder algumas agora, de forma controlada" e "perder muito mais, de forma descontrolada, alguns minutos depois". A matemática da Seção 3 é o argumento.

**"O cliente móvel é que faz retry, e eu não controlo o app dos usuários. Como aplico backoff com jitter?"**

Dois caminhos. Primeiro: o app **é** de vocês, então backoff com jitter é uma mudança de cliente que vale priorizar — e vale medir quanto do seu tráfego de pico é retry, porque o número costuma surpreender. Segundo, e mais imediato: se vocês não controlam o cliente, a defesa se move para o servidor — load shedding com resposta **rápida e explícita** (um erro claro, imediato, em vez de um timeout longo) reduz o dano, porque o cliente que recebe erro rápido consome muito menos recurso do que o cliente que fica pendurado até o timeout. Falhar rápido é uma cortesia com o próprio sistema.

## Sobre particionamento

**"Você diz para medir a distribuição das chaves antes de particionar. Medir como, se o sistema ainda não está particionado?"**

Com uma consulta agregada sobre o tráfego histórico: quantas transações por conta, no período de pico, ordenado por volume decrescente. Se a curva for muito inclinada — as 10 contas maiores concentrando uma fatia grande do total — vocês têm o problema antes de particionar. Isso é uma tarde de trabalho de análise que evita meses de migração mal desenhada. E vale como regra geral de System Design: **a distribuição da sua chave de partição é um dado que você pode medir hoje, no sistema atual, antes de tomar a decisão.**

**"Sub-particionar em baldes quebra a invariante? Como eu garanto Σ débitos = Σ créditos com o saldo espalhado em 20 linhas?"**

Não quebra, mas muda onde ela é verificada. A invariante continua verdadeira no conjunto — a soma dos 20 baldes mais os lançamentos correspondentes continua balanceada. O que muda é que a verificação deixa de ser uma leitura de uma linha e passa a ser uma agregação. Na prática, isso significa: (a) a reconciliação periódica precisa somar os baldes, e (b) qualquer regra que dependa do saldo exato daquela conta em tempo real fica mais caras de avaliar. É por isso que essa técnica se aplica bem a contas de recebimento de alto volume (onde o saldo instantâneo raramente é consultado por regra crítica) e mal a contas onde cada operação precisa checar limite contra o saldo exato.

## Sobre Outbox e CDC

**"Se o relay do Outbox cair, os eventos param de sair. Isso não é um novo ponto único de falha?"**

É um ponto de falha, mas de tipo muito melhor que o anterior. Reparem na diferença: se o relay cai, **nada se perde** — os eventos continuam gravados na tabela, e serão publicados quando ele voltar. O sistema fica com **atraso**, não com **perda**. Compare com o dual write, onde uma falha no momento errado significa evento que nunca existiu. Trocar "risco de perda silenciosa" por "risco de atraso visível" é um dos melhores trade-offs disponíveis em sistemas distribuídos. E, operacionalmente, o relay é stateless e replicável — a defesa é rodar mais de um, com coordenação para não publicar em duplicado (ou aceitar duplicação, já que os consumidores são idempotentes).

**"CDC lendo o WAL não acopla meu sistema ao formato interno do banco? E se eu quiser trocar de banco?"**

Acopla, sim, e é um custo real do CDC que vale nomear. Duas mitigações: primeiro, o acoplamento fica confinado a **um** componente (o conector), não espalhado pela aplicação — trocar de banco significa trocar o conector, não reescrever produtores de evento. Segundo, o formato do **evento publicado** é seu, não do banco: o conector traduz mudança de linha em evento de domínio, e essa tradução é onde vocês mantêm a independência. Dito isso, se trocar de banco é um cenário realista no seu horizonte, o poller — que usa só SQL padrão — é a escolha mais conservadora, e a recomendação de "comece com poller" ganha um argumento extra.

## Sobre ferramentas

**"Circuit breaker na aplicação (Resilience4j) ou no service mesh (Envoy)? Qual eu escolho?"**

A diferença que decide: a biblioteca **conhece a semântica do seu domínio**, a malha não. Um circuit breaker de aplicação pode distinguir "o DICT retornou 404, que é resposta legítima de chave inexistente" de "o DICT retornou 503, que é falha" — e não abrir o circuito no primeiro caso. Uma malha, operando na camada de rede, tende a tratar códigos de erro de forma mais genérica. Por outro lado, a malha aplica a política uniformemente, sem depender de cada time lembrar de configurar a biblioteca. Recomendação prática: malha para a política de base uniforme, biblioteca nos pontos onde a semântica de domínio importa — e o caminho do DICT, com sua distinção entre 404 e 503, é exatamente um desses pontos.

**"Teste de degrau em produção não é arriscado? Como eu testo o comportamento do pool sem derrubar o sistema real?"**

Em produção, sim, é arriscado — e é por isso que a prática madura é fazer isso em ambiente de carga dedicado, com dados sintéticos e a mesma topologia de produção. O que **pode** ser feito com segurança em produção é o "game day" controlado: escolher uma janela de baixo tráfego, injetar carga adicional de forma incremental com um mecanismo de parada imediata, e observar. E existe uma variação valiosa: em vez de aumentar a carga, **reduzir a capacidade** — desligar deliberadamente instâncias até chegar perto do cotovelo. Isso produz o mesmo efeito de utilização alta com muito mais controle, porque religar é instantâneo.
