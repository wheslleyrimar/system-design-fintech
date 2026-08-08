---
layout: default
title: "Aula 1 — Guia de perguntas difíceis"
---

# Aula 1 — Guia de perguntas difíceis
*Munição de embasamento para quando a plateia técnica empurrar. Cada resposta assume uma audiência sênior que já operou sistemas em produção.*

---

## Sobre o ledger de partida dobrada

**"Isso não é over-engineering para uma fintech pequena? Por que não um `UPDATE saldo = saldo - 100` com um lock e ponto final?"**

Porque o custo de partida dobrada não é sobre escala — é sobre auditoria e recuperação de desastre, que toda fintech regulada precisa desde o dia 1, independente do tamanho. Um `UPDATE` sem log não sobrevive a uma pergunta do BACEN de "como vocês chegaram nesse saldo há 8 meses". E o custo real de gravar dois lançamentos em vez de atualizar uma coluna é marginal — estamos falando de uma linha extra numa tabela append-only, não de dobrar a complexidade do sistema. A pergunta certa não é "isso é caro demais", é "o que eu perco se não fizer isso" — e a resposta é: a capacidade de provar, depois do fato, que o dinheiro nunca sumiu.

**"Vocês gravam 2-3 lançamentos por transação. Isso não dobra/triplica o custo de storage e IOPS?"**

Sim, e isso é exatamente o trade-off que a Seção 2.5 torna explícito com números: ~260 bilhões de lançamentos/ano em vez de ~87 bilhões de transações, o que dá 75-130 TB/ano em vez de um terço disso. A resposta não é evitar o custo — é reconhecê-lo e desenhar para ele: particionamento por tempo, tiering para storage frio depois de N meses, compressão em cold storage. O custo de storage é ordens de magnitude mais barato que o custo de um incidente regulatório por falta de trilha de auditoria.

## Sobre idempotência

**"O que acontece se o cliente nunca recebe resposta nenhuma — nem sucesso, nem erro — e desiste de tentar? A chave fica pendurada para sempre?"**

Depende do design do timeout do registro de idempotência. Na prática, um registro em estado "em andamento" que nunca chega a "concluído" dentro de uma janela razoável (segundos, não minutos, dado o orçamento de 40s do Pix) deveria disparar uma verificação de reconciliação — ou o processo original ainda está rodando (e vai eventualmente concluir e atualizar o registro), ou ele morreu no meio (crash do processo), e nesse caso o sistema precisa de um mecanismo de "reaper" que detecta registros travados e decide: retomar de onde parou (se o estado permitir) ou marcar como falho e permitir um novo retry com nova chave. Isso é exatamente o motivo pelo qual "estado explícito no log" (Seção 2.4) importa: sem estado explícito, vocês não sabem se é seguro retomar ou não.

**"Quanto tempo vocês guardam as chaves de idempotência? Isso não cresce para sempre?"**

Não precisa. A chave só importa durante a janela em que um retry plausível pode chegar — tipicamente minutos a poucas horas, não para sempre. Depois disso, o registro de idempotência pode ser arquivado ou expirado; o ledger em si (a fonte da verdade) continua para sempre, mas o mecanismo de dedup é uma estrutura auxiliar com TTL.

## Sobre a matemática de capacidade

**"Seu fator de pico de 5× é chutado. Como eu defendo isso numa reunião de verdade?"**

Você não defende o número — defende o **processo**. Em uma reunião real, o próximo passo depois dessa estimativa de guardanapo é instrumentar o sistema real e medir o fator de pico observado (comparando TPS do minuto mais carregado do dia contra a média diária, por várias semanas). A estimativa de 5× serve para dimensionar a primeira versão da infraestrutura, não para ser a palavra final. O ponto pedagógico da Seção 2.5 é: vocês nunca têm todos os dados no dia 1, mas isso não é desculpa para não estimar com critério — é motivo para estimar com margem e instrumentar cedo para substituir a estimativa por medição real assim que possível.

**"Por que usar dados de 2026 do Pix inteiro, e não um número específico da minha empresa?"**

Porque no dia 1 de um projeto, vocês não têm dado histórico próprio — e o dado agregado do mercado, calibrado pela fatia de mercado esperada, é a melhor aproximação disponível. Se a fintech de vocês mira 1% do mercado de Pix, multiplicam a estimativa de pico nacional por 0,01. Reparem que isso é diferente de "chutar um número": é aplicar um fator de participação de mercado, explícito e revisável, sobre um dado real.

## Sobre a Lei de Little e capacidade

**"A Lei de Little assume sistema em estado estacionário. Isso não é irreal num pico de tráfego, que é justamente instável por definição?"**

É uma objeção correta e mostra que a pessoa conhece a ferramenta. A Lei de Little é exata em estado estacionário, mas continua sendo uma **boa aproximação** para dimensionamento mesmo sob picos, desde que vocês apliquem numa janela de tempo curta o suficiente para o sistema estar "quase estacionário" dentro dela — por exemplo, calculando L para o TPS médio de cada minuto do pico, em vez de para o dia inteiro. Ela não substitui teste de carga real; ela dá a vocês uma primeira aproximação, defensável, antes de gastar uma sprint inteira montando esse teste.

**"900 TPS e 45 conexões parece pouco. Por que não simplesmente colocar um pool de 1000 conexões e nunca mais se preocupar com isso?"**

Duas razões. Primeiro, cada conexão de banco tem custo de memória e overhead de contexto no próprio banco — mesmo bancos modernos degradam com milhares de conexões ociosas, então superdimensionar o pool "só para garantir" tem custo real, não é grátis. Segundo, e mais importante: um pool gigante não resolve a causa raiz, que é a **latência por operação subindo sob contenção** — se a latência de cada escrita passa de 50ms para 500ms porque o lock está disputado, aumentar o pool só adia o esgotamento, não resolve a fila de espera pelo recurso que está realmente contencionado (o lock da conta, não a conexão em si). É por isso que a resposta real, na Aula 2, é reparticionar — não é só aumentar o pool.

## Sobre isolamento e particionamento

**"Por que não usar Spanner/CockroachDB/Yugabyte e deixar o particionamento pro banco resolver sozinho?"**

Essa é uma opção legítima, e muitas fintechs modernas fazem exatamente isso — trocam a complexidade de gerenciar sharding manual pelo custo operacional e financeiro de um banco distribuído nativamente consistente. A diferença não é "certo vs errado", é onde vocês preferem pagar o custo: gerenciar particionamento e sagas vocês mesmos (mais controle, mais trabalho de engenharia) vs. pagar a um banco distribuído para abstrair isso (menos trabalho, menos controle sobre o comportamento exato sob contenção, e tipicamente mais caro em infraestrutura). Sistemas legados ou com restrições de já estarem rodando em Postgres/MySQL tradicional tendem a precisar do caminho manual; green-field com orçamento para isso frequentemente escolhe o banco distribuído.

**"E se, depois de particionar por `hash(conta_id)`, uma partição específica ficar muito mais quente que as outras — um cliente com volume gigantesco, por exemplo?"**

Isso é o problema clássico de "chave quente" dentro de um esquema de particionamento, e hashing simples não resolve sozinho. As saídas comuns: particionamento mais granular só para as contas de altíssimo volume (tratamento especial, um "shard dedicado" para grandes contas); ou redesenhar a chave de partição para incluir um componente de tempo/sequência, distribuindo até as escritas de uma única conta muito ativa. Vale mencionar que isso é, coincidentemente, o mesmo tipo de problema que big techs de e-commerce resolvem para contas de vendedores muito grandes — não é exclusivo de fintech.

**"Vocês citaram Postgres, CockroachDB, Spanner, DynamoDB, Vitess. Qual eu deveria escolher para o meu ledger, de verdade?"**

Não existe resposta universal, mas existe uma heurística defensável: se o volume de escrita esperado cabe confortavelmente num nó bem dimensionado com particionamento nativo (a maioria das fintechs no primeiro ou segundo ano de operação), Postgres com serializable e boa disciplina de partição é a escolha mais simples de operar e depurar — vocês entendem exatamente o que está acontecendo. Migrem para um NewSQL (CockroachDB, YugabyteDB) quando o throughput de escrita genuinamente ultrapassar o que a verticalização e o particionamento manual sustentam, ou quando vocês precisarem de distribuição geográfica real. Reservem Spanner (ou o equivalente gerenciado de nuvem) para quando a escala for verdadeiramente global e a consistência externa for um requisito de negócio, não só desejável. E evitem um banco de chave-valor puro como fonte da verdade do ledger — a invariante central atravessa múltiplas linhas por natureza, e isso empurra a complexidade de volta para a aplicação.

## Sobre CAP/PACELC

**"CAP e PACELC não são só jargão de palestra? Isso muda alguma decisão real que eu vou tomar?"**

Muda, e de forma bem concreta: toda vez que vocês decidem "esse dado precisa de leitura forte ou pode ser eventual", vocês estão aplicando PACELC, com ou sem o nome. O valor de nomear o framework é ter vocabulário compartilhado no time para justificar a decisão por escrito (no ADR) em vez de "porque eu achei melhor assim". Peçam para qualquer engenheiro sênior descrever o trade-off de consistência de um sistema que ele já operou — ele vai descrever PACELC nas próprias palavras, mesmo sem usar o nome.

## Sobre a infraestrutura do BACEN

**"O que acontece se o próprio DICT ou SPI cair? Isso não é um ponto único de falha nacional?"**

É, estruturalmente — e é por isso que o BACEN se compromete com metas de disponibilidade agressivas (99,9% para o SPI) e mantém canais primário e secundário de transmissão de mensagens (o secundário com um teto de tempo bem mais folgado, 45 minutos, para cenários degradados). Do lado de vocês, a defesa não é "torcer para o BACEN nunca cair" — é desenhar para degradação graciosa: filas de mensagens que retêm ordens de pagamento durante uma indisponibilidade do SPI e as reenviam quando ele volta, comunicação clara ao usuário de que o Pix está temporariamente indisponível, e nunca duplo-processamento quando o sistema volta (de novo, idempotência).

**"O rate limit do DICT parece pequeno (2 tokens/min para PF). Isso não quebra qualquer app com volume razoável?"**

O limite pequeno é por **usuário final**, não por participante — cada usuário fazendo poucas consultas por minuto é o padrão de uso normal (ninguém consulta uma chave Pix 10 vezes por minuto legitimamente). O limite que importa para o volume agregado da fintech é o de **participante**, que escala por categoria até 25 mil tokens/minuto. Ou seja, o rate limit não é um teto de capacidade de negócio — é uma defesa contra abuso individual, calibrada para nunca incomodar o uso legítimo.

## Sobre Recuperação de Valores

**"Rastrear um grafo entre instituições diferentes, em tempo real, para bloquear fundos — isso não é tecnicamente inviável em escala nacional?"**

É genuinamente difícil, e é exatamente por isso que o mecanismo tem SLAs generosos comparados ao Pix normal — p99 de 6 horas para concluir uma devolução por fraude confirmada, contra os poucos segundos de uma liquidação normal. O desenho não exige travessia de grafo em tempo real síncrono; exige um processo assíncrono, coordenado pelo DICT como autoridade central de marcação, onde cada salto do rastreamento dispara uma notificação para a próxima instituição, que responde dentro de uma janela de tempo regulada. É mais parecido com um workflow distribuído de longa duração (dias, no limite) do que com uma query de grafo instantânea.

**"E se o fraudador mover o dinheiro para fora do Pix inteiramente — sacar em dinheiro, por exemplo — antes do rastreamento chegar nele?"**

Isso é uma limitação real e reconhecida do mecanismo: ele rastreia o dinheiro **dentro** do sistema Pix. Uma vez que os recursos saem do sistema (saque, conversão para outro ativo, transferência internacional), o rastreamento via DICT perde o rastro, e o caso passa a depender de investigação policial/judicial tradicional. É por isso que o **bloqueio cautelar** de até 72 horas existe: ele dá uma janela para agir antes que o dinheiro saia do sistema, mas não é garantia absoluta.

## Sobre ADR / SDD / IA

**"Isso não é só documentação chique? Documentação sempre fica desatualizada."**

A diferença central é que uma spec bem escrita, com invariantes explícitas, vira **teste automático** — ela não fica silenciosamente desatualizada porque, se o comportamento do sistema divergir da spec, o teste quebra e alguém precisa decidir: o código está errado, ou a spec está desatualizada e precisa de um novo ADR. Documentação tradicional não tem esse mecanismo de verificação; ela só descreve, nunca confere. SDD fecha esse loop.

**"Por que eu confiaria numa proposta de um agente de IA sobre algo tão crítico quanto o ledger?"**

Vocês não confiam no agente — confiam no aparato que valida a proposta dele, que é o mesmo aparato que validaria a proposta de um humano júnior fazendo a mesma mudança: testes derivados das invariantes, revisão humana obrigatória antes de qualquer rollout, canary com guardrails, rollback automático. O agente pode errar; o sistema é desenhado para que o erro dele custe, no máximo, o que custaria o erro de um engenheiro humano seguindo o mesmo processo — nunca mais que isso. Isso fica muito mais concreto na Aula 8, mas vale plantar a régua de expectativa aqui.
