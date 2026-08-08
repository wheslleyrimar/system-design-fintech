---
layout: default
title: "Aula 3 — Modelagem de Domínio e Decisões Arquiteturais"
---

# Aula 3 — Modelagem de Domínio e Decisões Arquiteturais (SDD na prática)
*Curso de Arquitetura de Sistemas Financeiros com IA*

Eu terminei a última aula com uma confissão: desenhei as fronteiras do monólito do TechPix meio no olho. "Tem um módulo de Contas, tem um de Pagamentos, tem um de Antifraude" — e apontei essas divisões como se fossem óbvias. Hoje eu quero mostrar por que isso é perigoso, e dar para vocês uma técnica sistemática para nunca mais precisarem confiar só no palpite.

Deixa eu contar uma história — dessa vez, não é um pico de tráfego. É pior, porque é mais silenciosa.

No TechPix, o time de Antifraude construiu uma regra de limite diário: nenhuma conta pode movimentar mais que um certo valor por dia, sem passar por verificação extra. O Diego, que trabalhava nesse time, implementou a regra olhando para o que ele chamava de "conta" — no vocabulário dele, isso significava a identidade do cliente, o cadastro, o CPF verificado no onboarding. Enquanto isso, do outro lado do prédio, a Marina, no time de Pagamentos, também usava a palavra "conta" — só que para ela, "conta" significava uma sub-carteira dentro do ledger, porque o TechPix permitia que um mesmo cliente tivesse mais de uma carteira interna, uma para uso pessoal e outra para um pequeno negócio.

Ninguém mentiu. Ninguém foi descuidado. Os dois times escreveram código correto, testado, revisado — cada um dentro da sua própria definição de "conta". Só que um cliente esperto, com duas carteiras, conseguia dobrar o limite diário sem disparar nenhum alerta, porque a regra do Diego olhava a identidade (uma só), e o sistema de Pagamentos da Marina operava por carteira (duas). O bug não morava em nenhuma linha de código. Ele morava **entre** os dois times, no espaço onde a mesma palavra significava duas coisas diferentes, e ninguém tinha percebido.

Essa é a aula de hoje: **todo desastre de arquitetura que eu já vi começou com um substantivo errado.** E a solução não é "todo mundo usar a mesma palavra para tudo" — isso é impossível e, na verdade, indesejável. A solução é saber exatamente **onde** uma palavra pode mudar de significado, e desenhar uma fronteira explícita bem naquele ponto.

---

## 1. Domain-Driven Design, o essencial

A disciplina que dá nome a esse problema, e ferramentas para resolvê-lo, chama-se **Domain-Driven Design**, ou DDD — sistematizada por Eric Evans, e depois expandida por autores como Vaughn Vernon. Eu não vou dar o curso de DDD inteiro para vocês hoje; vou pegar só as quatro ideias que realmente mudam a arquitetura de uma fintech.

### 1.1 Linguagem ubíqua

A primeira ideia é a **linguagem ubíqua**: dentro de um contexto específico — e "contexto" aqui já é o segundo conceito, eu chego lá — todo mundo, do engenheiro ao especialista de negócio, usa exatamente as mesmas palavras, com exatamente o mesmo significado, para as mesmas coisas. Se o time de negócio chama uma coisa de "transferência" e o código chama a mesma coisa de "transfer_operation", vocês já perderam a linguagem ubíqua — e cada tradução mental que alguém precisa fazer entre "o que o negócio fala" e "o que o código diz" é um lugar onde um bug se esconde.

Mas reparem numa nuance importante, porque é exatamente o que pegou o Diego e a Marina: a linguagem ubíqua **não é global**. Ela vale dentro de um contexto. Fora dele, a mesma palavra pode — e frequentemente deve — significar outra coisa. O erro do TechPix não foi ter duas definições de "conta". O erro foi não saber que existiam duas definições, e não ter uma fronteira nomeada e explícita separando as duas.

### 1.2 Bounded context

Isso me leva à segunda ideia, a mais importante da aula: **bounded context**, contexto delimitado. Um bounded context é uma fronteira explícita dentro da qual um modelo de domínio, e a linguagem ubíqua que o descreve, valem sem ambiguidade. Dentro do contexto de Identidade, "conta" quer dizer uma coisa — a identidade verificada de um cliente. Dentro do contexto de Ledger, "conta" quer dizer outra — um livro contábil que registra lançamentos. Os dois estão certos, **dentro dos seus próprios limites**. O que não pode acontecer é alguém atravessar essa fronteira sem perceber que atravessou.

### 1.3 Agregados e invariantes

A terceira ideia formaliza algo que vocês já usam desde a Aula 1, só que sem esse nome: o **agregado**. Um agregado é um conjunto de objetos que forma uma fronteira de consistência — tudo dentro do agregado é protegido, transacionalmente, por uma invariante que nunca pode ser violada. Lembram da regra sagrada do ledger, Σ débitos igual Σ créditos, e do saldo que nunca pode ficar negativo? Isso é, literalmente, a invariante de um agregado — o agregado **Ledger**. Tudo que precisa ser atualizado junto, na mesma transação, para essa invariante se manter, mora dentro do mesmo agregado. Tudo que pode esperar, que pode ser atualizado um instante depois, mora fora dele, e se comunica por evento.

### 1.4 Eventos de domínio

E a quarta ideia é o **evento de domínio**: um fato que aconteceu no negócio e que importa registrar — não um detalhe técnico como "linha inserida na tabela X", mas algo que um especialista de negócio reconheceria e nomearia, como "Pix Liquidado" ou "Chave Resolvida". Vocês já viram esses eventos aparecerem informalmente nas duas aulas passadas. Hoje, a gente vai usá-los como matéria-prima para descobrir as fronteiras de contexto — não impostas de cima para baixo, mas emergindo de baixo para cima, a partir dos próprios fatos do domínio.

---

## 2. Event Storming: descobrindo fronteiras ao vivo

A técnica que eu quero ensinar para vocês hoje chama-se **event storming**, criada por Alberto Brandolini. A mecânica é simples de descrever e poderosa na prática: numa sala — ou, aqui na aula, no nosso Excalidraw — vocês colam post-its laranjas, cada um descrevendo um evento de domínio, no passado, com o verbo conjugado — "Pix Iniciado", não "Iniciar Pix". Colam esses eventos numa linha do tempo, da esquerda para a direita, na ordem em que eles acontecem. E o mais importante: fazem isso **coletivamente**, com pessoas de áreas diferentes, porque é exatamente no atrito entre visões diferentes que os pontos cegos — como o do Diego e da Marina — aparecem.

Vamos fazer isso agora, ao vivo, com o fluxo do Pix que a gente já conhece desde a Aula 1.

### 2.1 O rio de eventos do Pix

Deixa eu escrever a sequência, na ordem:

```
PixIniciado → ChaveResolvida → LimitesValidados → FundosReservados →
OrdemEnviadaAoSPI → PixLiquidado → (ramificação:) PixDevolvido
```

Reparem que cada um desses nomes é reconhecível por um especialista de negócio, não só por um engenheiro. "PixIniciado" é quando a Ana toca em pagar. "ChaveResolvida" é quando o DICT devolve a instituição e a conta do Bruno — aquela consulta síncrona que quase derrubou o sistema na Aula 2. "LimitesValidados" é a checagem de antifraude e PLD-FT que a gente viu na Aula 1. "FundosReservados" é o lançamento no ledger. "OrdemEnviadaAoSPI" é a mensagem `pacs.008`. "PixLiquidado" é a confirmação `pacs.002`. E, como ramificação possível, "PixDevolvido" — a mensagem `pacs.004`, ou o trilho do MED, quando algo dá errado.

### 2.2 Os contextos emergem dos eventos

Agora vem a parte mágica do event storming: em vez de eu chegar com uma divisão pronta, a gente **agrupa** esses eventos por quem cuida deles, e as fronteiras aparecem sozinhas.

- "PixIniciado" e "LimitesValidados" dependem de saber quem é o cliente e se ele pode operar — isso puxa para um contexto de **Identidade e Onboarding**, que na verdade nem aparece diretamente no fluxo do Pix, mas é usado por ele o tempo inteiro, por trás.
- "FundosReservados" e a confirmação de liquidação vivem, sem dúvida, no contexto de **Contas e Ledger** — a verdade do dinheiro, que a gente construiu na Aula 1.
- "ChaveResolvida", "OrdemEnviadaAoSPI" e "PixLiquidado" formam o núcleo de um contexto de **Pagamentos**, que orquestra a conversa com o mundo externo — DICT e SPI.
- "LimitesValidados", olhando mais de perto, na verdade tem uma parte que pertence a um contexto separado: **Antifraude e Limites** — que decide, com sua própria lógica, se uma operação é suspeita.
- E "PixDevolvido" puxa para um contexto de **Devoluções e Disputas**, que lida com o MED e com reclamações.

Reparem que eu não impus essa divisão no início da aula. Ela **emergiu** dos próprios eventos, porque eventos que mudam junto, que são cuidados pela mesma equipe, com a mesma linguagem, naturalmente se agrupam. É isso que faz o event storming ser tão mais confiável que um palpite educado como o que eu dei na Aula 2.

E aqui está o ponto que eu quero que vocês levem: se o Diego e a Marina tivessem feito esse exercício juntos, na mesma sala, com os post-its na mesma mesa, o momento em que "conta" aparecesse duas vezes, com dois significados, teria sido visível na hora — porque um post-it do contexto de Identidade e um post-it do contexto de Ledger, os dois dizendo "conta", ficariam lado a lado, forçando a pergunta: "espera, essa é a mesma conta?"

---

## 3. O mapa de contexto: como os contextos conversam

Descobrir os contextos é só metade do trabalho. A outra metade é desenhar como eles **se relacionam** — porque contextos isolados de verdade, que nunca trocam informação, não existem numa fintech. O artefato que registra isso chama-se **context map**, o mapa de contexto, e ele usa um vocabulário específico para descrever cada tipo de relação.

### 3.1 Upstream e downstream

A relação mais comum é **upstream/downstream**: um contexto upstream toma decisões que o contexto downstream precisa respeitar, sem poder negociar de volta. No TechPix, o contexto de **Contas e Ledger** é upstream em relação a quase todo mundo — Pagamentos, Cartões, Antifraude, todos dependem da verdade que o Ledger define, mas o Ledger não muda seu modelo para agradar nenhum deles.

### 3.2 A camada anticorrupção — o ACL

E aqui está a relação mais importante para uma fintech: o **ACL**, a Anti-Corruption Layer, a camada anticorrupção. Ela existe quando o contexto de vocês precisa conversar com um sistema externo — cuja linguagem vocês não controlam — sem deixar essa linguagem externa **vazar** para dentro do domínio de vocês. E o TechPix já tem um ACL, desde a Aula 1, só que sem esse nome: é exatamente a camada que traduz a mensagem `pacs.008` do padrão ISO 20022, do jeito que o Banco Central define, para o evento de domínio "PixIniciado", do jeito que o TechPix entende. Se amanhã o Banco Central mudar o formato de uma mensagem — coisa que acontece, como vimos com o Pix Automático na Aula 1 —, o ACL absorve essa mudança sozinho, e o resto do domínio de vocês nem precisa saber que algo mudou do lado de fora.

### 3.3 Outras relações do vocabulário

Vale conhecer mais duas: o **conformista** — quando um contexto simplesmente aceita o modelo de outro, sem tradução nenhuma, porque não vale a pena o esforço de traduzir (às vezes o time de Cartões simplesmente aceita o vocabulário do Ledger tal como é, sem um ACL) — e o **shared kernel**, o núcleo compartilhado — quando dois contextos deliberadamente compartilham uma fatia pequena e bem definida de modelo, porque separar completamente custaria mais do que vale a pena (talvez o conceito de "moeda" e "valor monetário" seja um shared kernel entre Ledger e Pagamentos, porque seria estranho cada um ter sua própria definição de como representar um valor em reais).

### 3.4 O context map do TechPix

Juntando tudo: no centro, o contexto de **Contas e Ledger**, upstream de quase tudo. Ao lado, **Pagamentos**, que orquestra o Pix e fala com o mundo externo através de um **ACL** — e é exatamente aqui, nessa fronteira, que moram as mensagens `pacs.008`, `pacs.002`, `pacs.004`, e a consulta ao DICT. **Antifraude** conversa com Pagamentos de forma síncrona, no meio do fluxo, mas tem sua própria linguagem e seus próprios modelos de risco. **Identidade** é upstream de todo mundo que precisa saber quem é o cliente. E **Devoluções** cuida do que acontece quando o MED entra em cena, conversando tanto com Pagamentos quanto, de novo, com um ACL para o próprio DICT — porque o relato de infração, como vimos na Aula 1, também passa por lá.

---

## 4. A fronteira de consistência, revisitada

Agora eu quero voltar numa ideia da Aula 1 e mostrar que ela sempre foi, secretamente, sobre bounded context.

Lá atrás, eu disse: "forte no núcleo, eventual na borda" — o ledger é consistente na hora, o extrato pode esperar. Hoje, com o vocabulário de DDD na mão, dá para dizer isso de um jeito mais preciso: **a fronteira de consistência transacional coincide com a fronteira do agregado — e, tipicamente, com a fronteira do bounded context central daquele agregado.** Dentro do agregado Ledger, tudo acontece dentro da mesma transação, protegido pela mesma invariante. Fora dele — quando Pagamentos quer avisar Antifraude, ou quando o extrato precisa ser atualizado —, a comunicação acontece por **evento de domínio**, de forma assíncrona, aceitando um atraso.

E isso explica uma coisa que talvez tenha incomodado vocês desde a Aula 2: por que o Outbox publica eventos **depois** da transação, de forma assíncrona, em vez de tudo acontecer junto? Porque tudo que precisava acontecer **junto**, na mesma transação, já aconteceu dentro do agregado. O que sai pelo Outbox é, por definição, informação que **pode** esperar — porque já cruzou a fronteira do contexto.

### 4.1 As quatro regras de design de agregado

Vaughn Vernon, que expandiu bastante o trabalho original do Eric Evans, formulou um conjunto de regras práticas para desenhar agregados. Eu vou dar as quatro que mais importam, porque elas transformam "agregado" de conceito vago em critério de decisão.

**Regra 1 — proteja invariantes de negócio dentro da fronteira.** O agregado existe para uma coisa: garantir que uma regra que envolve múltiplos dados nunca seja violada. Se a regra é "saldo nunca negativo", então tudo que é necessário para verificar essa regra — o saldo e o lançamento sendo aplicado — precisa estar dentro do mesmo agregado, na mesma transação. **A invariante define a fronteira**, não o contrário. Comecem sempre pela pergunta "que regra eu não posso violar nunca?" e a fronteira se desenha a partir dela.

**Regra 2 — projete agregados pequenos.** Essa é a regra que a maioria dos times viola, e é a mais caras de violar. Um agregado grande — digamos, "Cliente", contendo todas as contas, todos os cartões, todo o histórico — parece conveniente para navegar no código. Mas ele significa que **qualquer** alteração em **qualquer** parte dele trava o agregado inteiro. Dois usos completamente independentes passam a competir pelo mesmo lock. Guardem: agregado grande é contenção disfarçada de conveniência.

**Regra 3 — referencie outros agregados por identidade, não por objeto.** Se o agregado de Pagamento precisa saber de qual conta o dinheiro sai, ele guarda o **identificador** da conta, não uma referência ao objeto Conta inteiro. Isso parece detalhe de implementação, mas é a regra que impede o agregado de crescer sem controle — porque, sem ela, "carregar um Pagamento" acaba carregando meio banco de dados, e mais grave: acaba permitindo que alguém modifique dois agregados na mesma transação sem perceber.

**Regra 4 — fora da fronteira, use consistência eventual.** Se uma operação precisa alterar dois agregados, a resposta correta quase nunca é "coloque os dois na mesma transação". A resposta é: altere um, emita um evento de domínio, e deixe o outro reagir. Isso é, literalmente, o Outbox da Aula 2 — só que agora vocês entendem que ele não é um truque de infraestrutura, é a **consequência direta** de ter desenhado agregados pequenos.

### 4.2 O trade-off que conecta esta aula à Aula 2

Aqui está, para mim, o insight mais valioso das três aulas juntas — e eu quero que vocês parem para absorver, porque ele amarra tudo.

Reparem no que acabou de acontecer: as regras 2 e 4 estão em **tensão direta** uma com a outra.

- **Agregado grande:** mais coisas protegidas transacionalmente, mais fácil de garantir invariantes complexas — mas **mais contenção**, porque tudo compete pelo mesmo lock.
- **Agregado pequeno:** menos contenção, escala muito melhor — mas **mais consistência eventual** para gerenciar, mais eventos, mais compensação, mais complexidade de raciocínio sobre estados intermediários.

E agora conectem com a Aula 2: **o ponto quente do ledger, que derrubou o TechPix no dia 5, era um problema de agregado grande demais.** A conta de liquidação `pix_a_liquidar` estava, efetivamente, dentro da fronteira transacional de todas as transações do sistema ao mesmo tempo. Não era um problema de banco de dados; era um problema de **modelagem de domínio** que se manifestou como problema de banco de dados.

Deixem isso decantar, porque a implicação é forte: quando a gente falou de "reparticionar a escrita do ledger" na Aula 2, a gente estava falando, em vocabulário de DDD, de **redesenhar a fronteira do agregado**. O `hash(conta_id) mod N` da Aula 1 e a decisão de "que dados vivem dentro deste agregado" são a mesma decisão, vista de dois ângulos — um de infraestrutura, um de domínio.

E é por isso que eu insisto que essas três aulas são uma só: a contenção que vocês medem em produção é, na maioria das vezes, uma fronteira de domínio mal desenhada cobrando o preço.

### 4.3 O problema do agregado grande na prática do Pix

Vamos aterrissar isso no TechPix com um exemplo concreto e discutível — do tipo que dá boa discussão em sala.

Pergunta: **o limite diário de transferência do cliente pertence ao agregado da Conta?**

O argumento a favor: o limite é uma invariante — "a soma das transferências do dia não pode passar de X" — e invariante define fronteira, pela Regra 1. Colocar dentro é o instinto correto.

O argumento contra: se o limite diário vive dentro do agregado Conta, então **toda** transferência precisa travar o agregado Conta para verificar e atualizar o acumulado do dia. Numa conta de alto volume — o marketplace da Aula 2 — isso serializa todas as transferências daquele cliente. Vocês acabaram de criar um ponto quente por decisão de modelagem.

E a resposta honesta é: **depende do rigor exigido.** Se o limite precisa ser garantido com precisão absoluta, sem nunca ultrapassar nem por um centavo, ele tem que estar dentro da fronteira, e vocês pagam a contenção. Se um pequeno excesso momentâneo é tolerável — e para limite de antifraude, frequentemente é, porque a defesa não depende de precisão ao centavo — vocês podem manter o acumulado **fora** do agregado, atualizado por evento, aceitando uma janela de imprecisão de milissegundos em troca de escala.

Reparem que essa é uma decisão de **negócio**, não de engenharia. E é exatamente o tipo de decisão que merece um ADR, porque a escolha errada aqui só aparece em produção, num dia 5.

### 4.4 Versionamento de eventos: o problema que aparece no mês seis

Uma última coisa nesta seção, e é a que mais gente esquece de planejar: **eventos de domínio publicados são contratos públicos.** No momento em que o Outbox publica `PixLiquidado` e três serviços passam a consumir esse evento, o formato dele deixou de ser detalhe interno de Pagamentos — virou uma interface com três clientes.

E então, no mês seis, vocês precisam adicionar um campo. Ou pior: renomear um. O que acontece com os consumidores que ainda esperam o formato antigo? E com os eventos **antigos**, que estão retidos no broker e podem ser reprocessados, no formato velho?

As estratégias reais, com trade-off:

- **Só adicione, nunca remova nem renomeie** (compatibilidade retroativa). É a regra mais simples e a mais defensável: campos novos são opcionais, campos velhos permanecem para sempre, mesmo depois de virarem inúteis. O custo é acúmulo de lixo no schema ao longo dos anos.
- **Versione o tipo do evento** — `PixLiquidado.v2` conviva com `PixLiquidado.v1` — e mantenha os dois publicados durante uma janela de migração, até todos os consumidores migrarem. Mais trabalho, mas honesto e explícito.
- **Registro de schema** (o *schema registry*, como o do ecossistema Kafka): um serviço central que valida, no momento da publicação, se o novo formato é compatível com o anterior, e **rejeita** publicação incompatível. Isso transforma "acordo de cavalheiros" em checagem automática — reparem que é a mesma ideia da fitness function da Aula 2, aplicada a contrato de evento.

E o alerta prático que vale dar: em sistema financeiro, com retenção de eventos por anos por exigência de auditoria, vocês vão, inevitavelmente, precisar ler eventos escritos por uma versão do código que não existe mais. Planejem para isso desde o primeiro evento — porque retrofitar versionamento depois é doloroso.

---

## 5. SDD na prática: escrevendo a spec do contexto Pagamentos

Chegou a hora de juntar tudo isso com o que eu comentei na Aula 1 sobre Spec-Driven Development. Se um bounded context é uma fronteira explícita, com sua própria linguagem, seus próprios eventos e sua própria invariante — então ele é, naturalmente, a unidade certa para escrever uma especificação executável. Vamos escrever, juntos, a spec do contexto **Pagamentos**:

```
Contexto      pagamentos

Linguagem     "Pagamento" = uma ordem de movimentação de valor, iniciada
              pelo usuário pagador. Não confundir com "Transferência"
              (termo do contexto Contas, para movimento interno entre
              carteiras do mesmo cliente).

Invariantes   - Todo pagamento tem um EndToEndId único (idempotência).
              - Nenhum pagamento é enviado ao SPI sem FundosReservados
                confirmado pelo contexto Ledger.
              - A resolução de chave respeita o rate limit do DICT
                (Aula 1, Seção 5.4).

Eventos       PixIniciado, ChaveResolvida, OrdemEnviadaAoSPI,
              PixLiquidado, PixDevolvido

Depende de    Contas e Ledger (upstream) — via evento FundosReservados
              Antifraude (síncrono) — via LimitesValidados
              BACEN (via ACL) — DICT e SPI, nunca direto

SLA herdado   Teto de 40s (BACEN); orçamento interno definido no ADR-001
```

Reparem que essa spec não é decoração — ela é o mesmo tipo de artefato que o ADR-001 e o ADR-002, só que com um escopo diferente: em vez de registrar uma decisão pontual, ela registra a **fronteira e o contrato** de um contexto inteiro. E, exatamente como uma invariante do ledger virou uma fitness function na Aula 2, a linha "Invariantes" dessa spec vira, diretamente, testes automáticos que protegem o contexto de Pagamentos contra violação — inclusive contra a violação sutil do tipo Diego-e-Marina, porque a linha "Linguagem" agora torna **explícito e testável** que "Pagamento" e "Transferência" não são a mesma coisa.

### 5.1 Context Engineering, agora concreto

E aqui eu quero fechar um círculo que abri na Aula 1, quando falei de Context Engineering de um jeito ainda abstrato. Hoje dá para ser preciso: **se um agente de inteligência artificial for implementar ou modificar alguma coisa dentro do contexto de Pagamentos, o contexto que ele recebe — no sentido de "context window" — deveria ser, literalmente, o bounded context que a gente acabou de desenhar.** A spec de Pagamentos, o glossário da linguagem ubíqua daquele contexto especificamente, os ADRs relevantes — ADR-001 e ADR-002 —, e os eventos que ele emite e consome. E, tão importante quanto o que entra: o que fica de fora. O agente **não** deveria receber os detalhes internos do contexto de Antifraude, ou do contexto de Identidade — só o contrato de evento que os conecta. Isso não é só higiene de prompt; é a mesma disciplina de fronteira que vocês aplicariam a um engenheiro novo entrando no time de Pagamentos: ele aprende a linguagem daquele contexto, e conversa com os outros contextos só pelos contratos publicados, nunca abrindo o capô alheio.

Guardem essa frase, porque ela é, para mim, a ponte mais importante do curso inteiro: **o bounded context de vocês é, literalmente, a unidade de contexto que um agente deveria receber.** DDD não é só uma técnica para humanos se organizarem — é, também, o desenho de como fatiar o conhecimento de um sistema para que um agente raciocine dentro de fronteiras seguras.

---

## 6. Bounded context = microsserviço? (a pergunta que sempre aparece)

Essa pergunta vem em toda turma, e ela merece uma resposta cuidadosa porque a resposta simplista causa dano real.

A resposta curta: **um bounded context é um bom *candidato* a serviço, mas não uma obrigação.** A relação correta é: um serviço nunca deve conter mais de um bounded context (senão vocês voltaram à bola de lama, só que distribuída); mas um bounded context pode perfeitamente permanecer como módulo dentro de um monólito modular — e frequentemente **deve**.

Reparem que isso é exatamente a recomendação da Aula 2, agora com vocabulário melhor: as fronteiras que a gente descobriu hoje por event storming são as fronteiras de módulo do monólito modular. Extrair para serviço separado é uma **decisão posterior e independente**, tomada por critérios operacionais, não de modelagem.

E quais são esses critérios? Extrair um contexto para serviço próprio se justifica quando pelo menos um destes for verdadeiro:

- O contexto precisa **escalar de forma diferente** do resto. O Antifraude do TechPix, por exemplo, pode precisar de máquinas com muito mais CPU (ou GPU, se usar modelo de risco) do que o resto do sistema. Escalar junto significa pagar por capacidade que só uma parte precisa.
- O contexto tem um **ciclo de vida de deploy diferente** — muda várias vezes por dia enquanto o resto muda por semana, ou o contrário.
- O contexto pertence a um **time diferente**, e o acoplamento de deploy está causando fila de espera entre times. (Este é, na prática, o motivo mais comum e mais legítimo.)
- O contexto tem **requisito de disponibilidade ou de isolamento de falha** distinto — e aí é o bulkhead da Aula 2, aplicado no nível de serviço.

E o alerta que fecha o assunto: se nenhum desses critérios se aplica, extrair o serviço só compra os **custos** de sistema distribuído — latência de rede, falha parcial, consistência eventual entre serviços, complexidade de observabilidade — sem comprar nenhum dos benefícios. Vocês pagaram o preço e não levaram o produto.

Guardem a formulação: **bounded context é decisão de modelagem; microsserviço é decisão de topologia.** Elas se relacionam, mas não são a mesma decisão, e confundi-las é a origem de boa parte dos projetos de microsserviços que dão errado.

---

## 7. Fecho: linguagem é arquitetura

Deixa eu recapitular o que a gente construiu hoje.

Primeiro: **a linguagem ubíqua vale dentro de um contexto, não globalmente** — e o erro do Diego e da Marina não foi ter duas definições de "conta"; foi não saber que existiam duas.

Segundo: **bounded contexts emergem dos eventos do domínio**, de baixo para cima, através do event storming — não são impostos de cima para baixo por um palpite, por melhor que ele seja.

Terceiro: **a fronteira de consistência transacional é a fronteira do agregado**, e ela geralmente coincide com o núcleo do bounded context — é isso que separa o que precisa ser forte na hora do que pode esperar um instante.

Quarto: **a camada anticorrupção protege a linguagem de vocês do mundo externo** — é o que já estava acontecendo, sem nome, toda vez que o TechPix traduzia uma mensagem do BACEN para um evento de domínio.

E quinto — o fio que amarra tudo com o eixo de inteligência artificial: **a spec de um bounded context é executável, e é, ao mesmo tempo, a unidade certa de contexto para um agente trabalhar com segurança.**

Eu não vou mais lecionar as próximas aulas com vocês — quem assume daqui é outro professor, que vai construir comunicação entre esses contextos, extrair alguns deles para microsserviços de verdade, e colocar tudo isso para rodar com observabilidade e deploy contínuo. Mas eu volto na Aula 8, no fim do curso, para fechar o círculo que a gente abriu junto: nessa altura, o sistema já vai estar em produção, com dados reais — e um agente, olhando exatamente para os contextos e as specs que a gente desenhou hoje, vai propor a próxima evolução da arquitetura. Da fé, na Aula 1, para a evidência, na Aula 8 — e a linguagem que vocês vão desenhar hoje é o que vai tornar essa evolução segura de fazer, com humano ou com agente.

---

## Apêndice — Termos novos desta aula

| Termo | O que é |
|---|---|
| **DDD (Domain-Driven Design)** | Disciplina (Eric Evans) de modelar software a partir da linguagem e das regras reais do domínio de negócio. |
| **Linguagem ubíqua** | Vocabulário compartilhado, sem ambiguidade, entre negócio e código — válido dentro de um bounded context. |
| **Bounded context** | Fronteira explícita dentro da qual um modelo e sua linguagem valem sem ambiguidade. |
| **Agregado** | Conjunto de objetos protegido por uma invariante transacional única — a fronteira de consistência forte. |
| **Evento de domínio** | Um fato de negócio que aconteceu e importa registrar, nomeado no passado (ex.: "PixLiquidado"). |
| **Event storming** | Técnica (Alberto Brandolini) de descobrir eventos e fronteiras de domínio colaborativamente, com post-its numa linha do tempo. |
| **Context map** | Diagrama que registra como os bounded contexts de um sistema se relacionam entre si. |
| **Upstream / downstream** | Relação em que um contexto (upstream) decide, e o outro (downstream) se adapta, sem poder negociar de volta. |
| **ACL (Anti-Corruption Layer)** | Camada que traduz a linguagem de um sistema externo para a linguagem do seu domínio, sem deixar a externa vazar para dentro. |
| **Conformista** | Relação em que um contexto aceita o modelo de outro sem tradução, por não valer a pena o custo do ACL. |
| **Shared kernel** | Fatia pequena e deliberada de modelo compartilhada entre dois contextos, quando separar custa mais do que compartilhar. |
| **As 4 regras de agregado (Vernon)** | (1) a invariante define a fronteira; (2) projete agregados pequenos; (3) referencie outros agregados por identidade; (4) fora da fronteira, consistência eventual. |
| **Trade-off do tamanho do agregado** | Grande = mais invariantes protegidas, mais contenção. Pequeno = escala melhor, mais consistência eventual para gerenciar. **A contenção da Aula 2 era um agregado grande demais.** |
| **Versionamento de evento** | Evento publicado é contrato público. Estratégias: só adicionar (retrocompatível), versionar o tipo (`v1`/`v2`), ou registro de schema que rejeita mudança incompatível. |
| **Schema registry** | Serviço que valida compatibilidade do formato do evento na publicação — a fitness function da Aula 2 aplicada a contrato de evento. |
| **Bounded context ≠ microsserviço** | Contexto é decisão de modelagem; serviço é decisão de topologia. Um serviço nunca deve ter mais de um contexto; um contexto pode ser só um módulo. |
