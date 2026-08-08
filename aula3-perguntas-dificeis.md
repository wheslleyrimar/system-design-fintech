---
layout: default
title: "Aula 3 — Guia de perguntas difíceis"
---

# Aula 3 — Guia de perguntas difíceis
*Munição de embasamento para quando a plateia técnica empurrar.*

---

## Sobre DDD em geral

**"DDD não é aquela coisa cheia de cerimônia que atrasa entrega? A gente tentou e abandonou."**

A objeção é legítima e comum, e a resposta honesta é: a maior parte do que se chama de "DDD" na prática é o **DDD tático** — repositórios, factories, value objects, uma pasta chamada `domain` — e essa parte é, de fato, cerimônia opcional que frequentemente não paga o custo. O que paga, e é o que essa aula ensina, é o **DDD estratégico**: linguagem ubíqua, bounded context, context map. Essa parte não adiciona código nenhum; ela adiciona **clareza sobre onde as fronteiras estão** — e o bug do Diego e da Marina é a demonstração de que a ausência dessa clareza tem custo real. Se vocês abandonaram o DDD tático, ótimo. Não confundam com abandonar o estratégico.

**"Event storming exige juntar dez pessoas numa sala por um dia. Quem tem esse tempo?"**

Duas respostas. A primeira: comparem com o custo do bug do Diego e da Marina — um limite diário burlado, descoberto meses depois, com exposição a fraude no meio. Um dia de sala é barato. A segunda, mais prática: event storming não precisa ser um evento de um dia com dez pessoas. Uma sessão de noventa minutos com quatro pessoas certas — alguém que conhece o negócio, alguém de cada time que vai integrar — sobre **um** fluxo específico já produz a maior parte do valor. O formato monumental é como a técnica é vendida em consultoria; a versão útil é bem mais leve.

## Sobre agregados

**"Como eu sei se meu agregado está grande demais, na prática, antes de o incidente acontecer?"**

Três sinais mensuráveis, todos disponíveis antes do incidente. Primeiro: **taxa de conflito de transação** — se vocês usam controle otimista, a taxa de retentativa por conflito é a medida direta de contenção no agregado; se ela está subindo com o volume, o agregado é grande demais. Segundo: **quantas coisas não relacionadas você trava junto** — se um teste de carga que só cria cartões degrada a latência de pagamentos, os dois estão no mesmo agregado sem precisar. Terceiro, o mais simples: **o agregado tem mais de uma invariante que não se relacionam entre si?** Se sim, provavelmente são dois agregados fundidos por conveniência.

**"Se agregados pequenos exigem consistência eventual entre eles, como eu explico para o time de negócio que o dado pode estar 'errado' por um instante?"**

Não explique como "errado" — explique como **"correto com atraso limitado"**, que é o vocabulário da Aula 1. E, mais importante, faça a pergunta de negócio explicitamente, com número: "se o acumulado do limite diário estiver 200 milissegundos atrasado, qual é o dano real?" Na maioria dos casos, a resposta honesta do negócio é "nenhum" — e aí vocês têm autorização para o agregado pequeno. Nos casos em que a resposta é "dano inaceitável", vocês têm a justificativa para pagar a contenção. O erro é o engenheiro decidir isso sozinho, num sentido ou no outro.

## Sobre o insight que liga à Aula 2

**"Você diz que o ponto quente era um agregado grande demais. Mas a conta de liquidação existe por razão contábil, não de modelagem. Não dá para simplesmente 'reduzir o agregado'."**

Essa é a melhor objeção possível a esse ponto, e ela está certa — vale reconhecer explicitamente. A conta de liquidação existe porque a contabilidade de partida dobrada exige uma contrapartida, e isso é uma restrição de domínio real, não um erro de modelagem. O que se reduz não é a **existência** da conta, é a **granularidade** dela: em vez de uma conta de liquidação única, várias (por partição, por janela de tempo, por trilho), com uma agregação contábil que reconcilia. A invariante contábil continua satisfeita — a soma continua batendo — e a contenção se distribui. É exatamente a técnica de sub-particionamento da Aula 2, e a razão de ela ser aceitável aqui é que **a contabilidade exige que a soma bata, não que ela more numa única linha.**

## Sobre versionamento de eventos

**"Se eu nunca posso remover campo de evento, em cinco anos meu schema vira um monstro. Isso é sustentável?"**

Não indefinidamente, e é por isso que existe a estratégia de versionar o tipo. O padrão sustentável na prática é: adicione livremente durante a vida de uma versão; quando o acúmulo incomodar, crie a `v2` com o schema limpo, publique as duas em paralelo por uma janela de migração, e **retire a v1 quando o último consumidor migrar** — o que exige saber quem são seus consumidores, e é justamente por isso que um registro de schema (ou pelo menos um catálogo de quem consome o quê) deixa de ser luxo. O monstro só se forma quando ninguém nunca faz a v2 por medo de coordenar a migração.

**"E os eventos antigos, já gravados no formato v1, que precisam ser reprocessados anos depois?"**

Duas abordagens. A primeira, mais comum: manter no código o **leitor** da v1 para sempre, mesmo depois de parar de escrever nela — o custo é código morto que precisa continuar funcionando, e o benefício é que qualquer evento histórico continua legível. A segunda: **migração de evento** (upcasting) — ao ler um evento v1, um transformador o converte para v2 em memória, e o resto do sistema só conhece a v2. Essa segunda é mais limpa a longo prazo e é o que sistemas de event sourcing maduros fazem. Em fintech, com retenção de anos por auditoria, planejar isso desde o começo é o que evita a situação em que ninguém consegue mais ler os próprios registros de três anos atrás.

## Sobre bounded context e microsserviços

**"Nosso organograma define nossos serviços — um time, um serviço. Isso é errado?"**

Não necessariamente, e existe uma razão teórica para isso funcionar: a **Lei de Conway** diz que a arquitetura de um sistema tende a espelhar a estrutura de comunicação da organização que o constrói. A versão prática, o "Inverse Conway Maneuver", é usar isso deliberadamente — organizar os times de acordo com as fronteiras de domínio que vocês querem. O problema não é alinhar serviço com time; é alinhar serviço com time **quando o time foi formado por razão histórica que não corresponde a nenhuma fronteira de domínio**. Aí vocês têm serviços que precisam conversar constantemente porque a fronteira está no lugar errado, e nenhuma quantidade de boa engenharia resolve isso — só remover a fronteira ou mover o time.

**"Se um contexto pode ser só um módulo, como eu impeço que alguém o viole com um import direto, sem a barreira física do serviço separado?"**

Com a fitness function da Aula 2 — e essa conexão vale fazer explicitamente em sala. O ArchUnit (ou equivalente) transforma a fronteira lógica em barreira **verificada automaticamente**: qualquer import que atravesse a fronteira quebra o build. A diferença em relação ao serviço separado é que a barreira é de tempo de compilação em vez de rede — o que, aliás, é uma barreira mais rápida e mais barata de operar. A fronteira física do serviço é uma forma caras de conseguir uma garantia que um teste de arquitetura te dá de graça.

## Sobre a spec / SDD

**"Escrever spec para cada contexto não é documentação que vai apodrecer, como toda documentação apodrece?"**

A diferença é o mecanismo de verificação. Documentação tradicional apodrece porque nada acusa quando ela fica errada. Uma spec cujas invariantes viraram testes **acusa** — se o comportamento divergir da spec, o teste quebra, e alguém precisa decidir: o código está errado, ou a spec está desatualizada e precisa de novo ADR. É a mesma lógica da fitness function. E o corolário prático: a parte da spec que **não** vira teste (a prosa explicativa) vai apodrecer, sim, e é honesto assumir isso — por isso a spec deve ser curta, com o máximo possível em invariantes verificáveis e o mínimo em prosa.
