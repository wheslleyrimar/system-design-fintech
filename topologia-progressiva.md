---
layout: default
title: "A topologia progressiva do TechPix"
---

# A topologia progressiva do TechPix
*Companion de System Design — o desenho que você constrói ao vivo, camada por camada, ao longo do curso*

---

## Como usar este documento

Este é o artefato central de System Design do curso. Enquanto os outros arquivos explicam **conceitos**, este mostra **o desenho** — a arquitetura do TechPix sendo construída no Excalidraw, uma camada por vez, cada camada justificada por uma falha concreta que ela previne.

A regra de condução é simples e vale para as quatro aulas: **nunca desenhe uma caixa antes de a turma sentir a dor que justifica ela.** Se você desenhar um load balancer no começo, é decoração — todo mundo já viu load balancer. Se você desenhar depois de mostrar que uma única instância cai e leva o Pix inteiro junto, aí a caixa significa algo.

Cada camada abaixo traz: o gatilho (a dor), o que entra no desenho, a escolha técnica com trade-off real, os números, e onde isso cai no curso.

**Mapa das camadas por aula:**

| Camada | O que entra | Aula |
|---|---|---|
| 0 | O guardanapo — 4 caixas | 1 |
| 1 | Borda: DNS, WAF, load balancer, terminação TLS | 1 |
| 2 | Gateway/BFF: rate limit, autenticação, idempotência | 1 |
| 3 | Serviços: stateless, autoscaling | 1 (refinado em bounded contexts na 3) |
| 4 | Integração BACEN: mTLS, certificados, RSFN, ACL | 1 |
| 5 | Dados: primary, réplicas, particionamento, pool | 2 |
| 6 | Cache: Redis, cache-aside, e o limite regulatório do DICT | 2 |
| 7 | Assíncrono: broker, outbox relay, DLQ, ordenação | 2 |
| 8 | Continuidade: multi-AZ, RTO/RPO, degradação graciosa | 1 (fundamento) → validada na 8 |

---

## Camada 0 — O guardanapo

**Gatilho:** nenhum. Este é o ponto de partida, e ele é deliberadamente ingênuo.

Vocês já viram esse desenho na Aula 1: `app do cliente → API → core com o ledger → BACEN`. Quatro caixas. Eu quero que vocês guardem uma coisa sobre ele: **esse desenho está tecnicamente correto e operacionalmente inviável.** Ele descreve o fluxo lógico de um Pix com precisão — e não sobreviveria a dez minutos de produção real.

Nas próximas camadas, eu não vou "corrigir" esse desenho. Eu vou **acrescentar** a ele, e cada coisa que eu acrescentar vai ser resposta a uma pergunta que vocês mesmos vão fazer.

A primeira pergunta é a mais óbvia de todas, e eu quero que alguém faça: *"onde exatamente essa API está rodando?"*

---

## Camada 1 — A borda

**Gatilho:** a API do guardanapo é uma caixa só. Se ela é um processo num servidor, então esse servidor é um ponto único de falha para o Pix inteiro do TechPix. Reinicialização, deploy, pico de tráfego, um cabo — qualquer coisa derruba tudo.

**O que entra no desenho, da ponta para dentro:**

**DNS.** Antes de qualquer pacote chegar em vocês, o cliente resolve um nome. Isso parece trivial, mas tem duas decisões de arquitetura escondidas. A primeira é o TTL do registro — um TTL baixo (30 a 60 segundos) permite que vocês redirecionem tráfego rápido numa emergência, ao custo de mais consultas de resolução; um TTL alto reduz consultas mas te amarra por minutos ou horas durante um incidente. Para um sistema financeiro, TTL baixo é quase sempre a escolha certa: a capacidade de desviar tráfego em um minuto vale mais que a economia de consultas DNS. A segunda decisão é se vocês usam **DNS geográfico ou anycast** para direcionar cada cliente para a região mais próxima — o que só importa se vocês operarem em mais de uma região, e a gente chega lá na Camada 8.

**WAF (Web Application Firewall).** Uma camada que inspeciona requisições antes de elas chegarem à sua aplicação, bloqueando padrões conhecidos de ataque e absorvendo tráfego volumétrico. Numa fintech, ela tem um papel extra que vale nomear: **absorver o que não deveria chegar ao seu orçamento de latência.** Lembrem do teto de 40 segundos do Pix — cada requisição maliciosa que consome recurso do seu sistema é orçamento roubado de uma transação legítima. O WAF é a primeira linha de defesa desse orçamento, não só da segurança.

**Load balancer — e aqui tem uma escolha real.** Existem duas famílias, e a diferença importa:

- Um balanceador **L4** opera na camada de transporte: ele olha IP e porta, e distribui conexões TCP sem abrir o conteúdo. É mais rápido, mais barato, e não sabe nada sobre HTTP — não consegue rotear por caminho de URL, nem repetir uma requisição que falhou.
- Um balanceador **L7** opera na camada de aplicação: ele entende HTTP, então consegue rotear `/pix` para um conjunto de instâncias e `/extrato` para outro, fazer retry de uma requisição idempotente, e aplicar políticas por rota.

Para o TechPix, o L7 é o que habilita algo que vai ser essencial na Aula 2: **rotear tráfego por caminho** é exatamente o mecanismo da fachada do Strangler Fig. Se vocês têm um L7 na borda, migrar uma rota do monólito para um serviço novo é uma mudança de configuração de roteamento, não uma reescrita.

**Terminação TLS.** Onde a conexão criptografada do cliente "termina" e vira tráfego interno. Se ela termina no balanceador, vocês ganham CPU nos serviços (a criptografia é feita uma vez, na borda) mas o tráfego entre balanceador e serviço passa a ser interno — e aí a pergunta séria numa fintech é: **esse tráfego interno é criptografado também?** Para dados financeiros, a resposta defensável é sim, e isso se chama criptografia em trânsito ponta a ponta, não só na borda. É um custo de CPU que vocês pagam de propósito.

**Health check.** É o que faz o balanceador saber que uma instância morreu. E aqui tem uma armadilha que derruba sistema de verdade: um health check que só responde "o processo está vivo" é praticamente inútil. Se a instância está viva mas perdeu conexão com o banco, ela responde "estou saudável", continua recebendo tráfego, e falha toda requisição. O health check precisa checar as dependências críticas — mas **não todas**, senão vocês criam o efeito oposto: se o health check testa o DICT e o DICT fica lento, todas as suas instâncias se declaram doentes ao mesmo tempo e vocês tiram o sistema inteiro do ar por causa de uma dependência externa. A disciplina é: health check verifica o que a instância **precisa** para servir (banco próprio, sim), não o que ela **chama** (DICT, não).

**Números:** com o pico estimado de 900 TPS na infra do TechPix (aquele 5% do pico nacional que a gente calculou na Aula 1), e supondo que cada instância de aplicação sustente confortavelmente 100 a 200 requisições por segundo, vocês precisam de algo entre 5 e 9 instâncias só para o caminho de pagamento no pico — e mais um tanto de folga para não operar no limite. Reparem que isso já responde "quantas caixas eu desenho": não é uma, e não é cinquenta.

---

## Camada 2 — Gateway / BFF

**Gatilho:** agora vocês têm N instâncias atrás de um balanceador. Mas todas elas estão fazendo, cada uma por conta própria, o mesmo trabalho repetido: validar quem está chamando, checar limite de requisições, extrair a chave de idempotência. Pior: se essa lógica está espalhada em cada serviço, ela vai divergir entre eles — e divergência em validação de segurança é como vulnerabilidade nasce.

**O que entra:** uma camada de gateway (ou BFF — Backend For Frontend, se ela também compõe respostas específicas para cada tipo de cliente) com quatro responsabilidades bem delimitadas:

**Autenticação — e a distinção que muita gente confunde.** Autenticação é "quem é você"; autorização é "você pode fazer isso". O gateway é o lugar certo para a **autenticação** — validar o token, confirmar a identidade, rejeitar quem não se identificou. Mas a **autorização** de negócio precisa ficar no serviço de domínio, e não no gateway. Por que? Porque a pergunta "essa cliente pode transferir R$5.000 desta conta?" depende de saldo, de limite, de antifraude, de titularidade — tudo conhecimento do domínio de Pagamentos, que o gateway não tem e não deveria ter. Um gateway que tenta decidir autorização de negócio vira, inevitavelmente, um lugar onde regra de domínio vaza para a infraestrutura.

**Rate limiting próprio.** Reparem que isso é diferente do rate limit do DICT que vimos na Aula 1 — aquele é imposto ao TechPix pelo BACEN; este é o TechPix se protegendo dos próprios clientes. A implementação clássica é a mesma família de algoritmo: **token bucket** ou **sliding window**. E aqui vai um detalhe de arquitetura distribuída que quase todo mundo erra na primeira tentativa: se vocês têm 9 instâncias de gateway e cada uma mantém seu próprio contador em memória, o limite efetivo é 9 vezes o que vocês configuraram. Rate limit distribuído precisa de estado compartilhado — tipicamente um Redis com operações atômicas de incremento — o que introduz uma dependência de rede no caminho crítico. O trade-off honesto: contador local é rápido e impreciso; contador centralizado é preciso e adiciona latência mais um ponto de falha.

**Validação da chave de idempotência.** O gateway é o lugar natural para exigir que a requisição traga a chave (rejeitando com erro claro quem não trouxe), mas **não** para resolver a deduplicação — porque, como a gente viu na Aula 1, a deduplicação precisa ser atômica com a escrita no ledger, e o gateway não participa daquela transação. O gateway exige; o domínio deduplica.

**Propagação de contexto de rastreamento.** O gateway gera (ou aceita) um identificador de correlação que acompanha a requisição por todos os serviços que ela atravessar. Isso parece detalhe de observabilidade, mas é decisão de arquitetura: sem isso, investigar uma transação que falhou em produção significa procurar em N sistemas sem nada que os conecte. E numa fintech, "investigar uma transação específica" é uma exigência regulatória, não uma conveniência de engenharia.

**A armadilha do gateway.** Nomeie isso explicitamente para a turma: o gateway começa como uma camada fina de infraestrutura e tem uma tendência gravitacional a acumular regra de negócio, porque é "o lugar onde tudo passa". Quando isso acontece, ele vira um monólito novo, mais difícil de mudar que o original — e agora, com o agravante de estar no caminho crítico de tudo. A disciplina é: se a lógica precisa conhecer o domínio, ela não pertence ao gateway.

---

## Camada 3 — Os serviços

**Gatilho:** o "core" do guardanapo é uma caixa só, com ledger, pagamentos, cartões e antifraude dentro. Na Aula 2 a gente vai ver isso rachar; na Aula 3 a gente descobre as fronteiras certas por event storming. Aqui, na topologia, a pergunta é operacional: **o que essas caixas precisam ser para escalar?**

**A propriedade que importa: stateless.** Um serviço sem estado local pode ser replicado, morto e recriado à vontade, porque nenhuma requisição depende de ter caído na mesma instância da anterior. Isso é o que habilita autoscaling de verdade. E o inverso é a armadilha: se vocês guardam sessão em memória local, ou um cache local que a lógica assume estar quente, ou pior, um passo de uma transação de múltiplas etapas, vocês criaram afinidade — e afinidade mata escala elástica, porque agora a instância que morre leva estado com ela.

Onde o estado mora, então? Nas camadas 5, 6 e 7 — banco, cache e broker. Serviço é lógica; estado é infraestrutura dedicada a guardar estado. Essa separação é o que faz o resto funcionar.

**Autoscaling — e por qual métrica.** A escolha da métrica de escalonamento é uma decisão real. CPU é a métrica default e é razoável para serviços que fazem trabalho computacional. Mas para um serviço que passa a maior parte do tempo **esperando** — esperando o DICT, esperando o SPI, esperando o banco — CPU vai ficar baixa enquanto o serviço já está saturado de requisições em espera. Para esses, a métrica honesta é **profundidade de fila** ou **requisições em voo** — e reparem que isso é exatamente o `L` da Lei de Little que a gente calculou na Aula 1. A Lei de Little não serve só para dimensionar pool de conexões; ela é a métrica certa para escalar um serviço que espera.

E o alerta que vale dar: autoscaling tem **latência de reação**. Uma nova instância leva tempo para subir, aquecer conexões, entrar no balanceador — dezenas de segundos, no melhor caso. Num pico que sobe em segundos, como o do dia 5 da Aula 2, o autoscaling chega **depois** do estrago. Ele é proteção contra crescimento de carga, não contra picos abruptos. Contra picos abruptos, a defesa é capacidade pré-provisionada mais as táticas da Camada 8.

**Comunicação entre serviços.** Aqui a topologia encontra o DDD da Aula 3. A regra: comunicação **síncrona** (uma chamada direta, esperando resposta) só dentro do caminho crítico e só quando a resposta é indispensável para continuar — o antifraude, por exemplo, precisa responder antes de o pagamento seguir. Todo o resto — notificação, extrato, feed, analytics — é **assíncrono**, via evento, e isso é a Camada 7. Cada chamada síncrona que vocês adicionam ao caminho crítico multiplica a probabilidade de falha (se cada dependência tem 99,9% de disponibilidade, três delas em série já derrubam o composto para ~99,7%) e soma latência ao orçamento de 40 segundos. Chamada síncrona é dívida; assíncrono é o padrão.

---

## Camada 4 — A integração com o BACEN

**Gatilho:** a caixa "BACEN" do guardanapo esconde o fato de que vocês estão saindo da sua infraestrutura e entrando numa rede regulada, com exigências que vocês não negociam.

**A rede é dedicada, não a internet pública.** A comunicação com o SPI e o DICT acontece pela **RSFN**, a Rede do Sistema Financeiro Nacional. Isso muda a topologia de forma concreta: não é um serviço seu chamando uma API pública; é uma conectividade dedicada, com requisitos de rede específicos, e tipicamente redundante — porque se essa conectividade cai, vocês param de transacionar Pix, ponto.

**Certificados digitais e mTLS.** A comunicação é autenticada por **certificado digital** em ambas as direções — o que se chama **mTLS**, ou TLS mútuo: não é só o cliente verificando que o servidor é quem diz ser (o TLS comum de qualquer site), é também o servidor verificando o cliente pelo certificado dele. Na prática, isso significa que o TechPix se identifica ao BACEN criptograficamente, e vice-versa.

E aqui há uma consequência operacional que ninguém lembra até doer: **certificado expira.** Um certificado vencido derruba a integração com a mesma eficiência de um cabo cortado — e a falha é especialmente cruel porque acontece num instante previsível que ninguém previu. As decisões de arquitetura que caem disso: onde os certificados são armazenados (nunca no repositório de código, nunca em imagem de container — em um gerenciador de secrets dedicado), quem tem acesso a eles, como a rotação é feita **antes** do vencimento, e que alarme dispara com semanas de antecedência.

*Nota de honestidade para a turma:* os requisitos exatos de certificado (autoridade certificadora aceita, tipo, algoritmo, prazo) estão definidos nos manuais de segurança e comunicação do próprio BACEN, e mudam. Eu vou ensinar a **estrutura** — mTLS, rede dedicada, rotação — e vocês consultam o manual vigente para os parâmetros exatos. Não decore número de manual regulatório; saiba que ele existe e onde procurar.

**A camada anticorrupção, agora como topologia.** Na Aula 3 a gente vai chamar isso de ACL e tratar como conceito de DDD. Na topologia, ela é um componente real e desenhável: o adaptador que fala ISO 20022 (`pacs.008`, `pacs.002`, `pacs.004`) para fora, e eventos de domínio para dentro. Colocá-la como componente separado tem três benefícios concretos: o formato de mensagem do BACEN nunca vaza para dentro dos seus serviços; quando o BACEN muda o formato — e ele muda, como vimos com o Pix Automático — só esse componente muda; e o pool de conexões dele fica **isolado** do resto do sistema, o que é literalmente o bulkhead da Aula 2 desenhado na topologia.

**Idempotência, de novo, e por que aqui é diferente.** A idempotência da Aula 1 protegia vocês do cliente que toca três vezes. Esta protege vocês de vocês mesmos: quando o TechPix envia uma ordem ao SPI e a resposta não volta, vocês não sabem se o SPI liquidou. Reenviar sem cuidado pode duplicar uma liquidação real. É por isso que o E2E ID viaja na mensagem — ele é a chave que permite ao SPI reconhecer o reenvio. E a consequência de topologia: vocês precisam de um mecanismo de **reconciliação**, um processo que compara o que vocês registraram contra o que o BACEN registrou, e resolve divergências. Isso não é um serviço opcional de "nice to have"; é o que impede que uma incerteza de rede vire dinheiro divergente.

---

## Camada 5 — Os dados

**Gatilho:** este é o momento da Aula 2. O dia 5, o pico, a fila de lock, o pool esgotado. Aqui a gente desenha a resposta.

**Primary e réplicas.** Uma instância primária que aceita escrita, e N réplicas que servem leitura. A pergunta que a turma sempre faz e que vale explorar: *"por que não escrever nas réplicas também?"* Porque escrita em múltiplos nós exige coordenação de consenso entre eles, e é exatamente esse custo de coordenação que a gente mapeou na Aula 1 como a origem da contenção. Um primary único para escrita é a escolha que mantém a invariante `Σ débitos = Σ créditos` simples de garantir.

**Replica lag — o número que define a experiência.** As réplicas ficam atrás do primary por um intervalo — tipicamente 100 a 300 milissegundos numa rede saudável, mas que **cresce sob carga de escrita**, exatamente quando vocês menos querem. E isso produz o bug mais confuso de sistemas com CQRS: a cliente faz um Pix, o ledger grava no primary, a tela recarrega e consulta uma réplica que ainda não recebeu a atualização — e ela vê o saldo antigo. Do ponto de vista dela, o dinheiro desapareceu por meio segundo. Tecnicamente, o sistema está correto; para ela, está quebrado.

A solução tem nome: **read-your-own-writes**. As estratégias reais são (a) rotear a leitura daquele cliente específico para o primary durante alguns segundos após ele escrever, (b) o cliente carregar um marcador da versão que ele escreveu e a leitura esperar a réplica alcançar essa versão, ou (c) simplesmente devolver o resultado já conhecido na resposta da escrita, sem reconsultar. A opção (c) é a mais simples e resolve a maioria dos casos — e é subestimada.

**Particionamento (sharding) — o desenho.** A Aula 1 já deu a mecânica: `hash(conta_id) mod N`. Na topologia, isso vira múltiplos conjuntos primary/réplica, cada um responsável por uma faixa de contas, com uma camada de roteamento decidindo para onde cada requisição vai. Os pontos que valem no Excalidraw: escolher `N` com folga desde o começo (rebalancear depois é doloroso; usar hashing consistente reduz essa dor), o caso da transação que atravessa partições (two-phase commit ou saga, como já vimos), e o problema da **conta quente** — um cliente de volume gigantesco que satura sua partição sozinho, e que precisa de tratamento dedicado.

**Pool de conexões — o callback da Lei de Little.** Aqui vocês fecham o círculo do cálculo da Aula 1: 900 TPS × 50 ms = 45 conexões; sob contenção, 900 × 500 ms = 450 conexões; pool de 100 esgota. Na topologia, a decisão é onde o pool vive. Se cada uma das 9 instâncias de aplicação mantém seu próprio pool de 50 conexões, o banco vê até 450 conexões — e bancos relacionais degradam com milhares de conexões, porque cada uma custa memória e contexto. É por isso que existe **pooler externo** (o PgBouncer é o exemplo canônico no mundo Postgres): uma camada entre aplicação e banco que multiplexa muitas conexões de aplicação sobre poucas conexões reais de banco. É uma caixa a mais no desenho que resolve um problema que só aparece em escala.

---

## Camada 6 — Cache

**Gatilho:** leitura é ordens de magnitude mais frequente que escrita, e cada leitura que bate no banco é capacidade que vocês poderiam ter usado para escrever.

**O padrão: cache-aside.** A aplicação consulta o cache; se achou (*hit*), usa; se não achou (*miss*), busca no banco, guarda no cache e devolve. Simples, e é o padrão certo para a maioria dos casos.

**Os três problemas reais, que valem nomear:**

**Invalidação.** É o problema difícil de cache, e a razão é conceitual: um cache é uma **cópia**, e cópia de dado que muda fica errada. As estratégias são TTL (o dado expira sozinho depois de um tempo — simples, mas você convive com dado velho até expirar), invalidação explícita na escrita (mais correto, mas agora a escrita precisa saber tudo que precisa invalidar, o que acopla), ou nunca cachear o que muda muito. Numa fintech, a linha divisória é clara: **saldo não se cacheia com TTL longo**, porque saldo errado na tela é dano real de confiança. Dados de referência que mudam raramente — tabelas de configuração, parâmetros — são candidatos naturais.

**Thundering herd.** Uma chave popular expira, e nesse instante todas as requisições que a queriam dão miss simultaneamente e vão todas ao banco de uma vez. O cache, que existia para proteger o banco, acabou de concentrar um pico nele. As defesas: um lock para que apenas a primeira requisição vá ao banco enquanto as outras esperam o resultado dela, ou TTL com jitter aleatório para as chaves não expirarem todas juntas.

**O cache do DICT — e por que ele é diferente de todos os outros.** Aqui está o ponto mais interessante desta camada, e ele é específico de fintech. Tecnicamente, cachear resposta do DICT seria ótimo: reduziria latência e economizaria tokens daquele balde que a gente estudou na Aula 1. Mas a informação do DICT é **dado pessoal**, e as regras do arranjo Pix impõem limites sobre retenção e reuso dessa informação. Ou seja: **o limite do seu cache aqui não é técnico, é regulatório.** Vocês não decidem o TTL pela taxa de acerto que querem; vocês decidem pelo que a norma permite, e otimizam dentro disso.

Isso é uma lição de System Design que vale além do Pix: em domínios regulados, a norma é uma restrição de projeto de primeira classe, no mesmo nível de CPU e latência. Um arquiteto que otimiza taxa de acerto de cache ignorando a regra de retenção não fez uma otimização — criou um problema de compliance.

**O que fazer, então, dado esse limite:** validar localmente antes de consultar (evitando o 404 que custa 20 tokens), consolidar consultas duplicadas da mesma requisição, e — o mais importante — tratar a resposta do DICT como algo caro e finito no seu desenho de fluxo.

---

## Camada 7 — O caminho assíncrono

**Gatilho:** o Outbox da Aula 2 mencionava "um relay que publica os eventos". Publica **para onde**, exatamente? Essa caixa merece nome e trade-off.

**O broker.** É a infraestrutura que recebe eventos de quem produz e entrega a quem consome, desacoplando os dois no tempo. A escolha real, em termos de família de tecnologia:

- Um **log distribuído** (Kafka é o exemplo dominante) guarda os eventos como um log ordenado e retido por tempo, e os consumidores leem em seu próprio ritmo, mantendo sua própria posição. Isso te dá reprocessamento — se um consumidor tinha bug, você corrige e reprocessa desde o começo, porque os eventos ainda estão lá. Para um sistema financeiro, essa propriedade é ouro: ela é a mesma ideia do ledger append-only, aplicada à integração.
- Uma **fila tradicional** (RabbitMQ, SQS) entrega e remove a mensagem. É mais simples de operar, tem roteamento mais flexível, mas você perde o histórico — mensagem consumida não volta.

Para o núcleo transacional do TechPix, o log distribuído se alinha melhor com a natureza append-only do domínio.

**Ordenação — e a nuance que quase todo mundo erra.** Um log distribuído garante ordem **dentro de uma partição**, não globalmente. Isso significa que a escolha da **chave de partição** é uma decisão de correção, não de performance: se vocês particionam os eventos por `conta_id`, todos os eventos da mesma conta caem na mesma partição e são processados em ordem — o que importa muito, porque processar "conta encerrada" antes de "crédito recebido" produz resultado errado. Se vocês particionam aleatoriamente para distribuir melhor a carga, ganham paralelismo e perdem a garantia de ordem por conta. Ordem por entidade quase sempre vence.

**Paralelismo de consumo.** O número de partições é o teto do seu paralelismo: com 12 partições, no máximo 12 consumidores trabalham em paralelo naquele tópico — o décimo terceiro fica ocioso. E como aumentar partições depois embaralha a distribuição das chaves, isso é uma decisão para tomar com folga desde o início.

**Dead letter queue (DLQ).** Uma mensagem que falha ao ser processada não pode ser tentada infinitamente (isso bloqueia a partição e trava tudo atrás dela) nem descartada silenciosamente (num sistema financeiro, mensagem perdida é dinheiro ou informação perdida). A DLQ é o destino de quarentena: depois de N tentativas, a mensagem vai para lá, um alerta dispara, e um humano investiga. **Uma DLQ sem alarme é um cemitério** — nomeie isso para a turma. Já vi DLQ com meses de mensagens que ninguém sabia que existiam.

**Como o Outbox chega no broker — duas implementações reais.** Isso é o detalhe que a Aula 2 deixou aberto:

- **Poller transacional:** um processo consulta periodicamente a tabela de outbox procurando eventos não publicados, publica e marca como publicado. Simples de entender e depurar, funciona em qualquer banco, mas adiciona latência (o intervalo do poll) e carga de consulta.
- **CDC — Change Data Capture:** um componente lê o **log de replicação** do próprio banco (o WAL, no Postgres) e transforma cada mudança commitada em evento, sem consultar tabela nenhuma. O Debezium é a implementação de referência. Latência muito menor, sem carga de consulta adicional, mas é mais um componente de infraestrutura para operar, e acopla você ao formato de log do banco.

O trade-off honesto: comecem com o poller (é mais simples e resolve), migrem para CDC quando a latência de propagação ou a carga de consulta virarem problema medido — não antes.

**Consumidores idempotentes.** Uma última coisa, e é a mais importante desta camada: como o broker entrega **at-least-once** (aquela semântica da Aula 1), o mesmo evento pode chegar duas vezes ao consumidor. Portanto **todo consumidor precisa ser idempotente**. É a mesma disciplina do começo do curso, agora aplicada ao consumo de eventos: guardar qual evento já foi processado, e ignorar repetição. Se vocês entenderam idempotência na Aula 1, vocês já sabem construir isso — é o mesmo padrão, outro lugar.

---

## Camada 8 — Continuidade

**Gatilho:** tudo que a gente desenhou até aqui está, implicitamente, num único datacenter. Se aquele datacenter tem um problema, o TechPix para — e "parar" para um PSP não é só perda de receita, é descumprimento de índice de disponibilidade regulado, com consequência formal.

**Multi-AZ como padrão mínimo.** Uma zona de disponibilidade é um domínio de falha isolado — energia, rede e refrigeração independentes — dentro de uma mesma região geográfica. Distribuir as instâncias de aplicação por múltiplas zonas é o padrão mínimo, e é relativamente barato: as zonas de uma mesma região têm latência entre si de poucos milissegundos, então a replicação **síncrona** do banco entre zonas é viável. Isso é o que permite um failover sem perda de dado.

**Multi-região é uma decisão qualitativamente diferente.** Entre regiões geográficas, a latência é de dezenas a centenas de milissegundos, o que torna a replicação síncrona incompatível com o seu orçamento de latência. Então a replicação passa a ser **assíncrona** — e replicação assíncrona significa que, num failover, vocês podem perder as últimas transações que não chegaram a replicar. Para um ledger, "perder as últimas transações" é inaceitável, o que faz multi-região ativo-ativo para escrita ser um problema genuinamente difícil, resolvido normalmente por particionamento geográfico (cada região é dona de um conjunto de contas) em vez de replicação total.

**RTO e RPO — os dois números que precisam ser explícitos.** O **RTO** (Recovery Time Objective) é quanto tempo vocês aceitam ficar fora do ar; o **RPO** (Recovery Point Objective) é quanto dado vocês aceitam perder. Eles não são a mesma coisa e são frequentemente confundidos. Para o núcleo de um ledger financeiro, o RPO defensável é **zero** — nenhuma transação liquidada pode desaparecer — e é justamente isso que exige replicação síncrona e, portanto, limita você a distâncias curtas. Para sistemas de borda, como o feed ou a análise histórica, um RPO de minutos é perfeitamente aceitável.

O ponto de System Design aqui: **RTO e RPO não são números iguais para todo o sistema.** Eles são definidos por componente, e essa diferenciação é exatamente a mesma lógica de "forte no núcleo, eventual na borda" que a gente estabeleceu na Aula 1 — agora aplicada a continuidade em vez de consistência. Se vocês entenderam aquela distinção, esta é a mesma ideia num eixo diferente.

**Degradação graciosa — o que fazer quando algo cai e você não pode simplesmente parar.** Esta é a parte mais madura desta camada, e vale bastante tempo no Excalidraw, porque é o que separa um sistema que "cai" de um sistema que "diminui".

Pensem por dependência, com a turma:
- **O DICT ficou lento ou indisponível.** Vocês conseguem seguir? Pix por chave, não — a resolução é indispensável. Mas Pix por dados de conta (agência e conta, sem chave) não precisa do DICT. Então a degradação correta não é "Pix indisponível"; é "pagamento por chave temporariamente indisponível, use dados da conta" — funcionalidade reduzida, não sistema fora.
- **O SPI ficou indisponível.** Vocês não podem liquidar, e liquidação é o SPI. A degradação aqui é aceitar a ordem, enfileirar com estado explícito, comunicar honestamente ao cliente que o pagamento está em processamento, e liquidar quando o SPI voltar — jamais dizer "concluído" para algo que não liquidou.
- **Uma réplica de leitura caiu.** O extrato pode ser servido por outra réplica, ou, em último caso, pelo primary com risco de carga. Isso é quase invisível para o cliente, se bem desenhado.
- **O broker caiu.** As escritas no ledger continuam funcionando — reparem que é exatamente por causa do Outbox: o evento fica gravado na tabela, na mesma transação, e o relay publica quando o broker voltar. Nenhum evento se perde. Este é o payoff do padrão da Aula 2, visível na topologia.

**Load shedding — a decisão desconfortável.** Quando a carga excede a capacidade, vocês têm duas opções: degradar para todos (todo mundo fica lento, e sob a Lei de Little, filas crescem até o sistema colapsar) ou **rejeitar parte do tráfego rápido e explicitamente**, preservando qualidade para o resto. A segunda é quase sempre a escolha certa, e é contraintuitiva o suficiente para valer uma discussão em sala: recusar 5% das requisições com um erro claro e imediato é melhor do que aceitar 100% e entregar timeout para todas. E numa fintech há uma priorização natural a fazer: se é preciso escolher, uma liquidação em andamento tem prioridade sobre uma consulta de extrato.

---

## O desenho final — e a pergunta que fecha

Ao final, o Excalidraw tem algo assim, da esquerda para a direita: cliente, DNS, WAF, balanceador L7 distribuindo por múltiplas zonas, gateway, serviços stateless por bounded context, cache, pooler, primary e réplicas particionados, broker com DLQ, o adaptador ACL com mTLS, e a RSFN levando ao SPI e ao DICT — com um bloco transversal de observabilidade e as marcações de RTO/RPO por componente.

São mais de vinte caixas. E eu quero fechar com a pergunta certa, que é a mesma que abriu:

**Cada uma dessas caixas está aí porque uma falha concreta a justificou.** Se vocês desenharem essa topologia inteira no dia 1 de uma fintech nova, vocês construíram um sistema que ninguém no time entende e que a operação não sustenta. O guardanapo de quatro caixas era **certo** para o dia 1. Esta topologia é certa para o dia em que o volume, o regulador e as falhas reais exigiram cada peça.

A habilidade que eu quero deixar com vocês não é "sei desenhar essa arquitetura". É **saber em que ordem essas caixas aparecem, e o que precisa doer antes de cada uma se justificar.** Arquitetura não é o desenho final; é a sequência de decisões que levou até ele — e é por isso que a gente escreveu um ADR para cada uma.

---

## Apêndice — Termos desta topologia

| Termo | O que é |
|---|---|
| **L4 / L7 (balanceador)** | Camada de transporte (IP/porta, rápido, cego a HTTP) vs. camada de aplicação (entende HTTP, roteia por rota, permite retry). |
| **WAF** | Web Application Firewall — inspeciona e filtra requisições antes da aplicação. |
| **Terminação TLS** | Ponto onde a conexão criptografada do cliente termina; o tráfego interno depois dela precisa de criptografia própria em fintech. |
| **mTLS** | TLS mútuo — as duas pontas se autenticam por certificado. Padrão na comunicação com o BACEN. |
| **RSFN** | Rede do Sistema Financeiro Nacional — conectividade dedicada, não internet pública. |
| **BFF** | Backend For Frontend — camada que adapta respostas por tipo de cliente. |
| **Stateless** | Serviço sem estado local; pode ser replicado/morto/recriado livremente. Habilita autoscaling. |
| **Replica lag** | Atraso entre primary e réplica (tipicamente 100-300 ms; cresce sob carga de escrita). |
| **Read-your-own-writes** | Garantia de que quem escreveu vê sua própria escrita na leitura seguinte. |
| **Pooler de conexões** | Camada (ex.: PgBouncer) que multiplexa muitas conexões de aplicação sobre poucas conexões reais de banco. |
| **Cache-aside** | Padrão: consulta cache, em caso de miss busca na origem e popula o cache. |
| **Thundering herd** | Chave popular expira e todas as requisições vão à origem simultaneamente. |
| **CDC (Change Data Capture)** | Ler o log de replicação do banco (WAL) para gerar eventos, sem consultar tabelas. Ex.: Debezium. |
| **Partition key** | Chave que decide a partição do evento; define a garantia de ordenação (decisão de correção, não de performance). |
| **DLQ (Dead Letter Queue)** | Quarentena para mensagens que falharam N vezes. Sem alarme, é um cemitério. |
| **AZ (Availability Zone)** | Domínio de falha isolado dentro de uma região; latência de poucos ms entre zonas permite replicação síncrona. |
| **RTO** | Recovery Time Objective — quanto tempo de indisponibilidade se aceita. |
| **RPO** | Recovery Point Objective — quanto dado se aceita perder. Para ledger, o defensável é zero. |
| **Degradação graciosa** | Reduzir funcionalidade em vez de cair por completo quando uma dependência falha. |
| **Load shedding** | Rejeitar parte do tráfego rápido e explicitamente para preservar qualidade do resto. |
