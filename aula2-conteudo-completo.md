---
layout: default
title: "Aula 2 — Fundamentos da Evolução Arquitetural em Fintech"
---

# Aula 2 — Fundamentos da Evolução Arquitetural em Fintech
*Curso de Arquitetura de Sistemas Financeiros com IA*

> **Navegação:** [Índice](index.md) · [Aula 1](aula1-conteudo-completo.md) · **Aula 2 (você está aqui)** · [Aula 3](aula3-conteudo-completo.md) · [Aula 4](aula4-conteudo-completo.md) · [Aula 5](aula5-conteudo-completo.md) · [Aula 6](aula6-conteudo-completo.md) · [Aula 7](aula7-conteudo-completo.md) · [Aula 8](aula8-conteudo-completo.md)

Na aula passada, a gente decidiu, na fé, que o ledger do TechPix ia ter consistência forte — síncrono, ACID, linearizável. Eu disse uma coisa lá no final que eu quero que vocês lembrem: guardem o ADR-001, porque um dia a produção vai ter opinião sobre ele. Hoje é o dia em que a produção fala.

Deixa eu contar o que aconteceu.

O TechPix decolou. Cresceu rápido — desses crescimentos que todo fundador sonha e todo arquiteto teme. E chegou um dia comum, um dia 5 do mês, hora do almoço, quando salário cai na conta de meio Brasil e todo mundo decide pagar boleto, mandar dinheiro pro aluguel e comprar o almoço ao mesmo tempo. O tráfego do TechPix triplicou em vinte minutos. E o sistema, que vinha rodando liso havia meses, começou a devolver erro. Não caiu de vez — foi pior que isso: começou a ficar **lento**, cada vez mais lento, até parecer travado. Os pagamentos que ainda passavam demoravam segundos a mais para confirmar. Alguns clientes tocaram duas, três vezes — vocês já sabem o que isso significa, a gente resolveu isso na Aula 1. Mas o sintoma novo, o que ninguém tinha visto antes, foi esse: o sistema inteiro andando em câmera lenta, como se estivesse com os pés na areia.

Essa é a aula de hoje. Eu quero mostrar exatamente **onde** um sistema bem arquitetado — porque o TechPix, com o ADR-001, foi bem arquitetado — ainda assim racha quando a escala aperta. E, mais importante, quero te ensinar a pensar em arquitetura não como uma foto que você tira uma vez, mas como um filme que não para de rodar.

---

## 1. O monólito não é o vilão

Antes de eu desenhar qualquer coisa, eu preciso desfazer um mito que atrapalha muita gente boa: **monólito não é sinônimo de sistema ruim.** O vilão de verdade tem nome, e é feio de propósito: **Big Ball of Mud**, a bola de lama grande — um sistema onde não existe fronteira nenhuma, onde qualquer módulo pode chamar qualquer tabela, onde ninguém sabe mais o que depende do quê. Isso, sim, é o inimigo. Um monólito bem estruturado é outra coisa completamente diferente, e é exatamente isso que o TechPix tinha até hoje de manhã.

Deixa eu mostrar como era o TechPix: um único artefato de deploy — um monólito, sim — mas por dentro, organizado em módulos com fronteiras de verdade. Tinha um módulo de **Identidade e KYC/PLD**, cuidando de quem é o cliente e se ele pode operar. Tinha o módulo de **Contas**, o módulo do **Ledger** que a gente construiu na Aula 1, o módulo de **Pagamentos**, que orquestra o Pix, o módulo de **Cartões**, e o módulo de **Antifraude**. Cada um desses módulos tinha seu próprio espaço de tabelas, sua própria API interna, e a regra de ouro era clara: nenhum módulo lê a tabela de outro módulo direto — toda comunicação passa por uma interface explícita, mesmo que os dois módulos rodem no mesmo processo, no mesmo binário, no mesmo deploy.

E por que eu insisto tanto nisso? Porque as fronteiras de um monólito modular bem-feito não são decoração. Elas são, literalmente, um **ensaio** para as fronteiras de serviço que talvez, um dia, vocês precisem extrair. Se o módulo de Cartões nunca vazou uma consulta direta na tabela do Ledger, então no dia que vocês decidirem tirar Cartões do monólito e colocar num serviço separado, a cirurgia é limpa — porque a fronteira já existia, só que dentro do mesmo processo. Se, ao contrário, o módulo de Cartões faz um `JOIN` direto na tabela de lançamentos do Ledger porque "era mais rápido assim", vocês não têm um monólito modular — vocês têm uma bola de lama com um nome bonito.

Minha recomendação, e isso vem de gente que já bateu a cabeça nisso — Martin Fowler chama essa estratégia de "monolith first" —: comecem com o monólito modular. Não é fase intermediária vergonhosa; é a decisão mais defensável no dia 1, porque vocês ainda não sabem exatamente onde as fronteiras de verdade do domínio de vocês vão cair. Extrair serviço cedo demais, antes de entender o domínio, é pagar o preço de operar sistemas distribuídos sem ter comprado ainda o benefício de escalar de forma independente. E tem uma regra prática que eu gosto de usar: só extraiam um módulo para um serviço separado depois que a fronteira dele ficar **estável por meses** — depois que vocês tiverem certeza de que aquela linha não vai se mover. Extrair cedo demais é caro; extrair tarde demais só custa um refactor. A assimetria favorece esperar.

---

## 2. Arquitetura evolutiva: o filme, não a foto

Só que "comece com o monólito" não quer dizer "pare de pensar em arquitetura depois do dia 1". E é aqui que eu quero apresentar para vocês uma ideia que muda a postura de qualquer arquiteto: **arquitetura evolutiva**.

A ideia, que autores como Neal Ford, Rebecca Parsons e Patrick Kua sistematizaram, é simples de enunciar e difícil de praticar: a arquitetura de um sistema não é um documento que vocês escrevem uma vez e pendura na parede. Ela é um organismo vivo, que muda continuamente em resposta a coisas que vocês não conseguiam prever no dia 1 — volume real de tráfego, comportamento real dos usuários, mudanças no próprio trilho regulatório, como a gente viu na Aula 1 com o Pix Automático. Eu gosto de resumir assim: **pensem em arquitetura como um filme, não como uma fotografia.** A foto captura um instante e mente sobre tudo que vem depois; o filme aceita que a cena muda.

E a ferramenta central da arquitetura evolutiva é a **fitness function** — termo que eu já usei na Aula 1, quando falei da invariante do ledger. Agora eu quero formalizar. Uma fitness function é qualquer mecanismo que dá a vocês uma avaliação objetiva de uma característica arquitetural que importa: performance, segurança, escalabilidade, a fronteira entre módulos. Existem fitness functions **atômicas**, que testam uma coisa isolada — "o p99 do caminho de escrita do Pix é menor que X milissegundos?" — e fitness functions **holísticas**, que testam a interação entre várias características ao mesmo tempo. Existem fitness functions **disparadas**, que rodam quando alguém propõe uma mudança — tipicamente no pipeline de CI —, e fitness functions **contínuas**, que ficam rodando o tempo todo em produção, como um monitor.

Deixa eu dar exemplos concretos, do próprio TechPix, para isso não ficar abstrato. Uma fitness function disparada, que roda a cada pull request: um teste de dependência de arquitetura — ferramentas como o ArchUnit fazem isso — que **quebra o build** se alguém, sem querer, introduzir uma chamada direta do módulo de Cartões para uma tabela interna do Ledger. Isso transforma a regra "nenhum módulo lê a tabela de outro" de um acordo de cavalheiros, que todo mundo esquece sob pressão de prazo, numa checagem automática que ninguém consegue burlar sem perceber. Uma fitness function contínua: um monitor que observa o p99 de latência do caminho de pagamento em produção, o tempo inteiro, e dispara alerta se ele passar de um limite que vocês definiram como seguro dentro do orçamento de 40 segundos que a gente viu na Aula 1. E uma fitness function holística: um teste de carga, um "game day", onde vocês simulam artificialmente um pico de tráfego — o próprio cenário do dia 5 que eu contei no começo — antes que ele aconteça de verdade, e medem se o sistema se comporta como esperado sob pressão.

E aqui eu quero fazer uma ponte que vai voltar com força lá na Aula 8: uma fitness function que trava um deploy porque uma característica do sistema não está sendo respeitada tem exatamente o mesmo formato de uma avaliação automática — um *eval* — que trava a proposta de um agente de inteligência artificial porque ela violaria uma invariante. Vocês, hoje, sem saber, já estão construindo o esqueleto do que mais para frente eu vou chamar de Harness. A disciplina é a mesma; só muda quem está propondo a mudança — um humano ou um agente.

---

## 3. A matemática do dia 5: por que o sistema não degradou, ele despencou

Antes de eu abrir o capô do incidente, eu preciso responder uma pergunta que talvez esteja incomodando vocês: **por que o tráfego triplicou e o sistema não ficou "três vezes mais lento"?** Ele ficou muito, muito pior que três vezes. Isso não é bug misterioso — é matemática, e é a matemática mais útil que eu vou ensinar nesse curso.

### 3.1 A curva que todo arquiteto precisa ter na cabeça

Existe uma relação, que vem da teoria de filas, entre o quanto um recurso está ocupado e quanto tempo você espera por ele. A forma mais simples dela — para uma fila com um servidor e chegadas aleatórias, o que a literatura chama de M/M/1 — é esta:

```
tempo de espera ∝ ρ / (1 − ρ)      onde ρ (rô) = utilização, de 0 a 1
```

Leiam essa fórmula com atenção no denominador, porque é ali que mora o drama: **quando a utilização se aproxima de 100%, o denominador se aproxima de zero, e o tempo de espera vai para o infinito.** Não é uma reta. É uma curva que fica quase plana e depois sobe verticalmente, e por isso ela costuma ser chamada de "cotovelo" ou "hockey stick".

Vamos colocar números, porque é aqui que a turma sente:

| Utilização (ρ) | Fator de espera ρ/(1−ρ) | O que isso significa |
|---|---|---|
| 50% | 1,0 | espera ≈ o tempo de serviço. Tranquilo. |
| 70% | 2,3 | começou a doer, mas ainda operável |
| 80% | 4,0 | **o dobro** da espera de 70% |
| 90% | 9,0 | 4× a espera de 80% |
| 95% | 19,0 | o sistema "parece travado" |
| 99% | 99,0 | colapso |

Reparem no que acontece entre 80% e 95%: a utilização subiu 15 pontos, e a espera **quintuplicou**. É por isso que a intuição linear falha tão feio. Um sistema rodando a 30% de utilização pode absorver o triplo do tráfego e ficar em 90% — e a experiência do usuário não piora três vezes, piora **nove vezes**. Foi exatamente isso que aconteceu no dia 5.

E aqui está o conselho operacional que cai direto dessa tabela, e que eu quero que vocês levem para a vida: **nunca dimensionem um sistema financeiro para operar acima de 70% de utilização no pico.** Aquela folga que parece desperdício de dinheiro é literalmente o que separa "lento" de "fora do ar". Quando alguém na sua empresa disser "esses servidores estão a 40%, dá para cortar metade", vocês agora têm a tabela para responder.

### 3.2 O efeito composto com a Lei de Little

Agora juntem isso com a Lei de Little da Aula 1, porque o combo é o que explica o colapso completo. Lembram: `L = λ × W`. A concorrência necessária é a taxa de chegada vezes o tempo no sistema.

Sigam o encadeamento comigo, porque ele é vicioso:

1. O tráfego triplica, então a utilização do lock do ledger sai de ~30% e vai para ~90%.
2. Pela curva de filas, o tempo de espera não triplica — ele salta de um fator 0,4 para um fator 9. O `W` da Lei de Little explode.
3. Pela Lei de Little, se o `W` explode e o `λ` também subiu, o `L` — a concorrência necessária — explode ao quadrado, digamos assim. Foi o cálculo que a gente fez na Aula 1: de 45 conexões para 450.
4. O pool tem 100. Ele esgota.
5. E agora vem a parte que fecha o círculo perverso: **quando o pool esgota, as requisições começam a dar timeout. Timeout faz o cliente tentar de novo. Retry aumenta o λ.** Volta para o passo 1, pior.

Esse último passo tem nome — **retry storm**, ou tempestade de retentativas — e é o mecanismo pelo qual um sistema que estava só lento vira um sistema completamente fora do ar. O tráfego que ele está recebendo agora não é mais a demanda real dos usuários; é a demanda real **mais** todas as retentativas que ele próprio causou. O sistema está se atacando.

E reparem na ironia cruel, porque ela é uma ótima pergunta para a turma: **a idempotência que a gente construiu na Aula 1 protegeu a correção — o cliente não foi cobrado três vezes — mas ela não protegeu a disponibilidade.** As três tentativas do cliente produziram um débito só, corretamente. Mas as três tentativas **consumiram recurso três vezes**. Idempotência resolve duplicação de efeito; ela não resolve amplificação de carga. São dois problemas diferentes, e o segundo precisa de defesa própria.

### 3.3 As defesas contra retry storm

Três, e todas valem nomear porque são padrões de indústria:

**Backoff exponencial com jitter.** Se uma requisição falha, o cliente não deve tentar de novo imediatamente, nem em intervalo fixo. Deve esperar um intervalo que **cresce exponencialmente** a cada tentativa (100 ms, 200 ms, 400 ms, 800 ms...) e — esta é a parte que quase todo mundo esquece — com um componente **aleatório** somado, o *jitter*. Por que o jitter importa tanto? Porque sem ele, mil clientes que falharam no mesmo instante vão tentar de novo exatamente no mesmo instante seguinte, e vocês transformaram uma tempestade em uma sequência de tempestades sincronizadas. O jitter espalha as retentativas no tempo. É uma linha de código que salva sistemas.

**Orçamento de retentativa (retry budget).** Uma regra global: as retentativas não podem passar de, digamos, 10% do tráfego total. Se passarem, o sistema **para de tentar** — porque acima disso, as retentativas estão claramente causando mais dano do que resolvendo. Isso é contraintuitivo e importante: existe um ponto em que insistir é pior do que desistir.

**Load shedding, de novo.** Já vimos isso na topologia, e aqui reaparece como defesa direta: rejeitar rápido e explicitamente parte do tráfego mantém a utilização abaixo do cotovelo da curva. Rejeitar 10% com erro imediato mantém os outros 90% rápidos; aceitar 100% deixa todos na fila e derruba tudo. Sob a curva de filas, **recusar tráfego é uma forma de proteger tráfego.**

---

## 4. Anatomia da fratura: onde o TechPix racha de verdade

Agora sim, com a matemática na mão, deixa eu abrir o capô e mostrar exatamente **onde** ele quebrou. São dois pontos, e os dois já estavam plantados desde a Aula 1 — eu até avisei, lembram? "Racha na Aula 2: ledger e DICT síncrono." Chegou a hora.

### 4.1 O ponto quente do ledger

Relembrando a Aula 1: o ledger do TechPix tem consistência forte, porque conservação de dinheiro exige isso. Mas "consistência forte" tem um custo que eu não detalhei até agora: para garantir que Σ débitos sempre seja igual a Σ créditos, cada escrita no ledger precisa coordenar com as outras escritas que tocam a mesma conta, ou o mesmo recurso compartilhado. Se a implementação usa, por exemplo, um contador sequencial único para gerar o identificador de cada lançamento, ou se duas transações concorrentes tentam debitar a mesma conta de liquidação ao mesmo tempo — lembra da conta `pix_a_liquidar` que eu usei como exemplo? — elas competem pelo mesmo lock. Isso se chama **ponto quente**, ou *hot partition*: um recurso que deveria ser só mais um entre milhares, mas que na prática concentra uma fração desproporcional do tráfego, e vira gargalo.

No dia 5, o volume de Pix simultâneos que passavam pela mesma conta de liquidação disparou. Cada transação precisava esperar sua vez para adquirir o lock daquela conta. A fila cresceu. E cada milissegundo de espera na fila é, literalmente, uma fatia a mais consumida do orçamento de latência que a gente desenhou na Aula 1 — aquele orçamento de 40 segundos, com a experiência-alvo de poucos segundos. Só que dessa vez, quem estava comendo o orçamento não era o SPI, nem o DICT — era o **próprio sistema do TechPix**, brigando consigo mesmo por um recurso compartilhado.

Reparem numa coisa importante: essa dor **não** significa que o ADR-001 estava errado. O ledger continua precisando de consistência forte — isso não mudou, e não vai mudar. O problema não é a decisão de ser forte; é a **implementação ingênua** dessa decisão, que concentrou contenção onde não precisava. A correção aqui não é enfraquecer o ledger — é redesenhar como o ledger particiona o trabalho, para que a consistência forte aconteça em paralelo, em vez de em fila única.

### 4.2 O DICT síncrono e o pool de threads

O segundo ponto de fratura é ainda mais traiçoeiro, porque ele não mora dentro do TechPix — mora na dependência de um sistema externo que a gente não controla. Relembrando a Aula 1: toda transação por chave Pix precisa consultar o **DICT**, e essa chamada é síncrona. Num dia normal, o DICT responde rápido — p99 de 1 segundo, como o próprio Banco Central publica. Mas no dia 5, com o volume triplicado, cada requisição do TechPix ficava esperando essa resposta síncrona chegar, e enquanto espera, ela **segura uma thread** — ou uma conexão do pool de banco, ou um slot de conexão HTTP, dependendo de como o sistema foi implementado.

E aqui está a parte traiçoeira: se o número de requisições simultâneas esperando o DICT ultrapassa o tamanho do pool de threads disponível, **todas as outras operações** que dependeriam dessa mesma pool — inclusive operações que não têm nada a ver com o DICT — começam a esperar também. Isso é o que se chama de **esgotamento de pool**, e o efeito colateral se chama **falha em cascata**: um componente lento, ou um sistema externo lento, contamina o sistema inteiro através de um recurso compartilhado que ele nem deveria estar disputando. É exatamente esse mecanismo que fez o TechPix parecer "andando na areia" — não é que tudo tenha ficado lento por igual; é que uma dependência específica, o DICT, consumiu o recurso que todo o resto também precisava.

A defesa clássica contra esse tipo de fratura tem nome, e vem da literatura de sistemas resilientes: **bulkhead**, o mesmo princípio dos compartimentos estanques de um navio — se um compartimento alaga, os outros continuam secos. Na prática, isso significa isolar o pool de conexões usado para chamar o DICT do pool usado para o resto do sistema, para que uma lentidão no DICT nunca sequestre a capacidade de processar, por exemplo, uma consulta de saldo. Junto disso vem o **circuit breaker**: um interruptor que, depois de detectar falhas ou lentidão repetida numa dependência, **para de tentar** por um tempo, falhando rápido em vez de deixar a fila crescer sem controle — e voltando a tentar aos poucos, quando a dependência dá sinal de que se recuperou. E, claro, o **timeout bem calibrado**: se o DICT normalmente responde em até 1 segundo no p99, esperar 10 segundos por uma resposta dele não é paciência, é desperdício do orçamento inteiro do Pix.

Reparem que essas três táticas — bulkhead, circuit breaker, timeout calibrado — não mudam a decisão de que o DICT é uma consulta síncrona necessária. Elas mudam como o sistema se **comporta** quando essa dependência atrasa, para que o atraso fique contido, em vez de se espalhar.

---

## 5. Desacoplamento incremental: cortando sem parar de operar

Agora que a gente sabe onde dói, vamos falar de como tratar — sem, no processo, criar um novo incidente pior que o primeiro. Porque um erro comum, depois de um susto desses, é a reação de pânico: "vamos reescrever tudo do zero em microsserviços". Isso quase sempre piora as coisas. O caminho certo é o **desacoplamento incremental**.

### 5.1 Strangler Fig

A primeira estratégia tem um nome bonito e uma imagem melhor ainda: **Strangler Fig**, a figueira estranguladora — uma planta que cresce em volta de uma árvore hospedeira, aos poucos, até que a árvore original desaparece e só resta a nova estrutura. Martin Fowler emprestou essa imagem para descrever como migrar um sistema sem um corte único e arriscado: vocês colocam uma fachada, um roteador, na frente do monólito, e começam a desviar uma fatia do tráfego — digamos, uma rota específica, ou um conjunto específico de clientes — para uma nova implementação, enquanto o resto continua batendo no monólito antigo. Aos poucos, mais tráfego migra, até que o monólito, naquele pedaço específico, para de receber chamada nenhuma — e pode ser desligado sem drama.

No TechPix, a estratégia seria: colocar uma fachada na frente do módulo de Pagamentos, e migrar gradualmente a lógica de resolução de chave — que hoje mora dentro do monólito e sofre com o esgotamento de pool que eu descrevi — para um componente isolado, com seu próprio pool de conexões, suas próprias réplicas, dedicado só a essa responsabilidade. Se esse componente ficar sobrecarregado, ele fica sobrecarregado sozinho — não arrasta o resto do sistema junto.

### 5.2 Branch by Abstraction

Às vezes, um corte limpo por fachada não é possível — a lógica está espalhada demais, ou o corte teria que ser feito de uma vez. Para esses casos existe uma segunda tática: **Branch by Abstraction**. A ideia é introduzir, primeiro, uma camada de abstração **dentro do próprio monólito**, por trás da qual a implementação antiga continua existindo. Só depois, com a abstração já no lugar e todo o resto do sistema já falando com ela — e não diretamente com a implementação concreta —, vocês trocam o que está atrás da abstração, seja por uma nova implementação interna, seja por uma chamada para um serviço externo. O ponto central é: **a abstração desacopla o "quem chama" do "quem implementa"**, e essa troca de implementação vira um detalhe interno, sem precisar de uma reescrita coordenada em todos os pontos de chamada de uma vez.

### 5.3 O problema da escrita dupla, e o Outbox Pattern

Agora, o ponto mais sutil e, para mim, o mais bonito dessa aula: o que acontece quando o TechPix precisa, na mesma operação, gravar um lançamento no ledger **e** avisar o resto do sistema que aquilo aconteceu — para atualizar o extrato, disparar uma notificação, alimentar o feed? Se vocês gravam no banco e, logo em seguida, publicam um evento numa fila de mensagens como duas operações separadas, existe uma janela de falha real: e se o sistema gravar no banco e cair exatamente antes de publicar o evento? O lançamento existe, mas ninguém nunca soube. Isso se chama **problema da escrita dupla**, o *dual write problem*, e é um dos jeitos mais silenciosos de um sistema ficar inconsistente sem ninguém perceber por semanas.

A solução elegante chama-se **Outbox Pattern**. Em vez de escrever no banco e publicar na fila como duas operações, vocês escrevem **duas coisas na mesma transação, no mesmo banco**: o lançamento do ledger, e um registro numa tabela de "outbox" — uma caixa de saída — descrevendo o evento que precisa ser publicado. Como as duas escritas acontecem dentro da mesma transação ACID, ou as duas acontecem, ou nenhuma acontece — nunca existe o estado intermediário perigoso. Depois, um processo separado — um relay — lê a tabela de outbox e publica os eventos, de forma assíncrona, para quem precisar consumir: o serviço de extrato, o de notificações, o de feed.

E aqui eu quero que vocês enxerguem uma coisa linda: a tabela de outbox é, estruturalmente, **a mesma ideia do ledger** que a gente construiu na Aula 1 — um log append-only, que registra fatos, um por um, sem nunca sobrescrever. Vocês não estão aprendendo um padrão novo do zero; estão reaplicando o mesmo princípio — log imutável como fonte da verdade — numa nova camada do sistema.

### 5.4 CQRS, agora de verdade

Isso fecha o círculo que eu abri na Aula 1, quando falei que write model e read model são coisas diferentes. Agora, com o Outbox publicando eventos de forma confiável, dá para materializar isso de verdade: o **caminho de escrita** continua sendo o ledger, forte, síncrono, protegido pelo ADR-001. O **caminho de leitura** — extrato, saldo exibido, feed — passa a ser alimentado, de forma assíncrona, pelos eventos que saem do Outbox, numa base de dados otimizada só para consulta, que pode escalar de forma completamente independente da escrita. Essa separação, que vocês já intuíam desde a Aula 1, agora tem um mecanismo concreto de sustentação: o Outbox é a ponte confiável entre os dois mundos.

---

## 6. Quanto o particionamento realmente compra? (a conta que ninguém faz)

Antes de escrever o ADR, eu quero fazer uma conta com vocês que a maioria dos times esquece de fazer — e que evita uma decepção caríssima.

A promessa intuitiva do particionamento é linear: "vou dividir a escrita em 8 partições, então tenho 8 vezes mais capacidade de escrita." **Isso só é verdade se o tráfego se distribuir uniformemente entre as partições.** E tráfego financeiro real quase nunca é uniforme.

Vamos supor o cenário realista do TechPix. Vocês particionam por `hash(conta_id)` em 8 partições. Mas o TechPix tem uma conta de marketplace que concentra, sozinha, 15% de todo o volume de recebimento — coisa comum em qualquer PSP que atenda um grande vendedor. O que acontece?

Sete partições ficam com aproximadamente 12% do tráfego cada — tranquilas. E a partição que abriga a conta do marketplace fica com os 12% dela **mais** os 15% do marketplace, ou seja, ~27% do tráfego total. Ela recebe mais que o dobro da carga das outras.

Agora apliquem a curva de filas da Seção 3. Se o sistema como um todo está a 60% de utilização média — o que parece confortável —, aquela partição específica está a algo perto de 100%, e ela sozinha está no colapso. **O sistema tem 8 partições, mas o gargalo é 1.** A capacidade efetiva do conjunto não é 8×; ela é limitada pela partição mais quente.

Existe até uma formulação disso que vale mencionar, porque ela dá autoridade ao argumento: a **Lei de Amdahl**, que diz que o ganho de paralelizar um sistema é limitado pela fração dele que **não** pode ser paralelizada. Aqui, a conta quente é a fração não-paralelizável. Vocês podem colocar 100 partições; a conta do marketplace continua sendo uma conta, num lugar, com um lock.

**Como se resolve, na prática — três caminhos, todos com custo:**

O primeiro é **sub-particionar a conta quente**: em vez de uma única linha de saldo para o marketplace, vocês mantêm N sub-saldos (digamos, 20 "baldes"), distribuem as escritas entre eles aleatoriamente, e o saldo real é a soma dos baldes. Isso resolve a contenção de escrita brilhantemente — e o custo é que agora a leitura do saldo precisa somar 20 linhas, e a invariante fica mais difícil de verificar. É a troca clássica: escrita rápida, leitura mais caras.

O segundo é **agregar antes de escrever**: em vez de gravar cada crédito individual do marketplace, vocês acumulam os créditos numa janela curta — digamos, um segundo — e gravam um lançamento agregado. Reduz drasticamente o número de escritas, e o custo é que o saldo daquela conta passa a ter granularidade de um segundo, e vocês precisam de um mecanismo confiável para não perder o acumulado se o processo cair no meio da janela. (Reparem que isso é, de novo, o Outbox aparecendo: o acumulado precisa estar em algum lugar durável.)

O terceiro é **isolar a conta quente inteiramente**: dar a ela sua própria partição dedicada, com recursos próprios. Não elimina a contenção interna daquela conta, mas garante que ela não afete ninguém mais — é o bulkhead da Seção 4, aplicado a dados em vez de a conexões.

E o ponto pedagógico, que é o que eu quero que fique: **antes de particionar, meçam a distribuição real das suas chaves.** Se 15% do volume está numa chave, o particionamento sozinho não vai te salvar, e descobrir isso depois de uma migração de dados de meses é uma das formas mais caras de aprender essa lição.

---

## 7. As ferramentas reais — nomes, não conceitos

Tudo que a gente discutiu tem implementação de indústria. Vale vocês saírem daqui com os nomes, porque é isso que transforma "eu entendi o conceito" em "eu sei o que pesquisar na segunda-feira".

**Fitness functions de arquitetura.** O **ArchUnit** (Java/Kotlin) permite escrever, como teste de unidade comum, regras do tipo "nenhuma classe do pacote `cartoes` pode depender de `ledger.internal`" — e o build quebra se alguém violar. Existem equivalentes em outras linguagens (`import-linter` no Python, `dependency-cruiser` no JavaScript/TypeScript, `go-arch-lint` no Go). Isso é o que transforma a regra de ouro do monólito modular numa checagem que ninguém consegue burlar distraidamente.

**Circuit breaker e bulkhead.** No mundo Java, o **Resilience4j** é o padrão atual (sucessor do Hystrix, que a Netflix descontinuou), e implementa circuit breaker, bulkhead, rate limiter, retry com backoff e timeout como decoradores componíveis. Em arquiteturas com service mesh, o **Envoy** (base do Istio e do Linkerd) faz circuit breaking e outlier detection na camada de rede, sem tocar no código da aplicação — o que é uma decisão arquitetural interessante: resiliência como infraestrutura em vez de como biblioteca. O trade-off é o de sempre: a biblioteca conhece a semântica do seu domínio, a malha de serviço é transparente mas genérica.

**CDC para o Outbox.** O **Debezium** é a implementação de referência: ele lê o log de replicação do banco — o WAL, no Postgres — e publica cada mudança commitada como evento, sem consultar tabela nenhuma. A alternativa mais simples é o poller, que a gente já discutiu. Recomendação honesta: comecem com poller, migrem para CDC quando a latência de propagação ou a carga de consulta virarem problema **medido**.

**Broker.** O **Kafka** é o log distribuído dominante, com a propriedade de retenção e reprocessamento que combina com a natureza append-only de um ledger. Alternativas gerenciadas com semântica parecida existem em todas as nuvens. Para filas tradicionais, **RabbitMQ** e **SQS**. A escolha real, como vimos na topologia, é log vs fila — retenção e reprocessamento vs simplicidade operacional.

**Feature flags para o Strangler Fig.** O **Unleash** é a opção open source madura; o **LaunchDarkly** é a comercial mais conhecida. E vale dizer para a turma: começar com um sistema próprio de flags é tentador e quase sempre subestimado — o difícil não é o `if`, é a propagação de mudança de configuração em segundos para centenas de instâncias, com auditoria de quem mudou o quê. Isso importa muito na Aula 8, porque é o mecanismo do canary.

**Teste de carga.** O **k6** (script em JavaScript, roda em CI), o **Gatling** e o **JMeter** são as opções conhecidas. Aqui vai a dica que a maioria erra: um teste de carga que sobe o tráfego suavemente até o alvo **não** reproduz o dia 5. Vocês precisam de um teste de **degrau** — salta de 30% para 300% instantaneamente — porque é o degrau que expõe o comportamento do pool, do autoscaling lento e do retry storm. Teste suave mede capacidade; teste de degrau mede sobrevivência.

---

## 8. Registrando a decisão: ADR-002

Chegou a hora de formalizar. Vamos escrever, juntos, o segundo registro de decisão do TechPix — e reparem que ele **não contradiz** o ADR-001. Ele o complementa, resolvendo exatamente o ponto de fratura que a gente diagnosticou hoje, sem tocar na consistência forte do núcleo.

```
ADR-002 · Outbox + CQRS para o caminho de leitura          Status: Aceito (2025-08-06)

Contexto      No incidente do dia 5, o caminho de escrita do ledger sofreu
              contenção sob pico de tráfego, e a leitura (extrato, feed)
              competia pelos mesmos recursos da escrita. O ADR-001
              permanece válido: o ledger continua ACID e fortemente
              consistente no núcleo.
Decisão       Toda escrita no ledger grava, na mesma transação, um evento
              na tabela de outbox. Um processo de relay publica esses
              eventos de forma assíncrona. O caminho de leitura (extrato,
              saldo exibido, feed) passa a ser alimentado por esses
              eventos, em um armazenamento de leitura separado.
Consequências (+) Escrita e leitura escalam de forma independente.
              (+) Nenhuma perda de evento: a escrita do fato e do evento
                  são atômicas (mesma transação).
              (−) O extrato passa a ter atraso eventual (100-300 ms) em
                  relação ao ledger — trade-off já previsto no ADR-001.
              (−) Um novo componente (o relay) precisa ser operado e
                  monitorado.
Alternativas  Publicar evento fora da transação (REJEITADO: janela de
              escrita dupla, risco de evento perdido).
              Ler direto do ledger para tudo (REJEITADO: é a causa raiz
              do incidente do dia 5).
Revisão       Medir, em produção, se a contenção no ponto quente do
              ledger cai depois que a leitura para de competir pelo
              mesmo recurso. Se persistir, o próximo passo é reparticionar
              a própria escrita do ledger — tema para revisitar.
```

Reparem que a linha "Revisão" deixa uma porta aberta, de propósito: talvez o Outbox e o CQRS não sejam suficientes sozinhos, e a própria escrita do ledger precise ser reparticionada — por exemplo, distribuindo o lock por uma chave de partição melhor escolhida, em vez de concentrar tudo numa única conta de liquidação. Eu vou deixar isso como um convite para vocês pensarem: **como vocês reparticionariam a escrita do ledger, sem abrir mão da invariante Σ débitos = Σ créditos?** Essa pergunta, aliás, dá um ótimo ADR-003 para quem quiser se aventurar.

---

## 9. Fecho: fronteiras eu desenhei no olho — e isso é um problema

Eu quero terminar essa aula com uma confissão. Reparem que, hoje, eu desenhei as fronteiras do monólito modular do TechPix meio de improviso: "tem um módulo de Contas, tem um módulo de Pagamentos, tem um módulo de Antifraude". Eu apontei essas fronteiras como se fossem óbvias. **Elas não são.** Eu as escolhi com a experiência de quem já viu esse tipo de sistema antes — mas isso não é uma técnica, é um palpite educado.

E um palpite educado, por melhor que seja, não escala para um time inteiro, nem sobrevive ao primeiro desacordo sério entre dois engenheiros que discordam sobre onde uma fronteira deveria estar. Vocês precisam de um jeito **sistemático** de descobrir essas fronteiras, a partir da própria linguagem do domínio — não do meu palpite, nem do gráfico da estrutura organizacional da empresa.

É exatamente isso que a gente vai fazer na próxima aula. A gente vai pegar o próprio fluxo do Pix — evento por evento — e usar uma técnica chamada event storming para deixar as fronteiras **emergirem** dos fatos do domínio, ao vivo, na frente de vocês. E vamos descobrir, entre outras coisas, por que a palavra "conta" — que eu já usei um punhado de vezes hoje, sem me preocupar — pode significar coisas completamente diferentes dependendo de quem está falando, e por que isso, se não for tratado direito, quebra sistemas de um jeito muito mais sutil do que um pico de tráfego num dia 5.

---

## Apêndice — Termos novos desta aula

| Termo | O que é |
|---|---|
| **Big Ball of Mud** | Sistema sem fronteiras internas reais; qualquer parte pode acoplar em qualquer outra. O oposto de um monólito modular bem-feito. |
| **Monolith first** | Recomendação (Martin Fowler) de começar um sistema novo como monólito modular, extraindo serviços só depois que as fronteiras se provarem estáveis. |
| **Fitness function** | Verificação objetiva e automatizável de uma característica arquitetural desejada. Pode ser atômica ou holística; disparada (CI) ou contínua (produção). |
| **Hot partition / ponto quente** | Um recurso (conta, partição, chave de lock) que concentra tráfego desproporcional e vira gargalo de contenção. |
| **Esgotamento de pool** | Quando requisições lentas seguram recursos compartilhados (threads, conexões) até não sobrar nenhum para o resto do sistema. |
| **Falha em cascata** | Uma dependência lenta ou com falha contamina, por recurso compartilhado, partes do sistema que não deveriam ser afetadas. |
| **Bulkhead** | Isolar pools de recursos por dependência, para que a lentidão de uma não sequestre a capacidade das outras. |
| **Circuit breaker** | Mecanismo que para de chamar uma dependência com falha repetida, falhando rápido, e volta a tentar aos poucos depois. |
| **Strangler Fig** | Migrar um sistema desviando tráfego gradualmente do antigo para o novo através de uma fachada, até o antigo poder ser desligado. |
| **Branch by Abstraction** | Introduzir uma camada de abstração dentro do sistema atual antes de trocar a implementação por trás dela. |
| **Dual write problem** | O risco de inconsistência quando uma operação escreve em dois lugares (ex.: banco + fila) como passos separados e não atômicos. |
| **Outbox Pattern** | Gravar o evento a publicar na mesma transação do dado de negócio; um processo separado publica o evento depois, de forma confiável. |
| **CQRS** | Command Query Responsibility Segregation — separar o modelo de escrita do modelo de leitura (já visto na Aula 1; aqui, materializado via Outbox). |
| **Utilização (ρ)** | Fração do tempo em que um recurso está ocupado. O tempo de espera cresce com ρ/(1−ρ) — explode perto de 100%. |
| **Curva de filas / cotovelo** | A relação não-linear entre utilização e latência. Entre 80% e 95% de utilização, a espera quintuplica. |
| **Retry storm** | Timeouts geram retentativas, que aumentam a carga, que geram mais timeouts. O sistema se ataca. |
| **Backoff exponencial com jitter** | Esperar intervalos crescentes **mais** um componente aleatório entre retentativas — o jitter evita retentativas sincronizadas. |
| **Retry budget** | Limite global (ex.: 10% do tráfego) acima do qual o sistema para de retentar, porque insistir passou a causar mais dano. |
| **Lei de Amdahl** | O ganho de paralelizar é limitado pela fração que não pode ser paralelizada — no ledger, a conta quente. |
| **Sub-particionamento de conta quente** | Dividir o saldo de uma conta de altíssimo volume em N baldes somados na leitura. Escrita rápida, leitura mais caras. |
| **Teste de degrau** | Teste de carga que salta instantaneamente para o pico, em vez de subir suave. Mede sobrevivência, não capacidade. |
| **ArchUnit** | Testa regras de dependência de arquitetura como teste de unidade; quebra o build ao violar fronteira de módulo. |
| **Resilience4j** | Biblioteca Java com circuit breaker, bulkhead, rate limiter, retry e timeout componíveis (sucessor do Hystrix). |
| **Debezium** | Implementação de referência de CDC: lê o WAL do banco e publica mudanças como eventos. |
| **Unleash / LaunchDarkly** | Plataformas de feature flag — o mecanismo que a Aula 8 usa para canary. |

---

[← Aula 1](aula1-conteudo-completo.md) · [Índice](index.md) · [Aula 3 →](aula3-conteudo-completo.md)
