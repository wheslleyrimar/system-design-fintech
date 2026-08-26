---
layout: default
title: "Aula 3 — Modelagem de Domínio e Decisões Arquiteturais"
---

# Aula 3 — Modelagem de Domínio e Decisões Arquiteturais (SDD na prática)
*Curso de Arquitetura de Sistemas Financeiros com IA*

> **Navegação:** [Índice](index.md) · [Aula 1](aula1-conteudo-completo.md) · [Aula 2](aula2-conteudo-completo.md) · **Aula 3 (você está aqui)** · [Aula 4](aula4-conteudo-completo.md) · [Aula 5](aula5-conteudo-completo.md) · [Aula 6](aula6-conteudo-completo.md) · [Aula 7](aula7-conteudo-completo.md) · [Aula 8](aula8-conteudo-completo.md)

Eu terminei a última aula com uma confissão: desenhei as fronteiras do monólito da TechPix meio no olho. "Tem um módulo de Contas, tem um de Pagamentos, tem um de Antifraude" — e apontei essas divisões como se fossem óbvias. Hoje eu quero mostrar por que isso é perigoso, e dar para vocês uma técnica sistemática para nunca mais precisarem confiar só no palpite.

Deixa eu contar uma história — dessa vez, não é um pico de tráfego. É pior, porque é mais silenciosa.

No TechPix, o time de Antifraude construiu uma regra de limite diário: nenhuma conta pode movimentar mais que um certo valor por dia, sem passar por verificação extra. O Diego, que trabalhava nesse time, implementou a regra olhando para o que ele chamava de "conta" — no vocabulário dele, isso significava a identidade do cliente, o cadastro, o CPF verificado no onboarding. Enquanto isso, do outro lado do prédio, a Marina, no time de Pagamentos, também usava a palavra "conta" — só que para ela, "conta" significava uma sub-carteira dentro do ledger, porque a TechPix permitia que um mesmo cliente tivesse mais de uma carteira interna, uma para uso pessoal e outra para um pequeno negócio.

Ninguém mentiu. Ninguém foi descuidado. Os dois times escreveram código correto, testado, revisado — cada um dentro da sua própria definição de "conta". Só que um cliente esperto, com duas carteiras, conseguia dobrar o limite diário sem disparar nenhum alerta, porque a regra do Diego olhava a identidade (uma só), e o sistema de Pagamentos da Marina operava por carteira (duas). O bug não morava em nenhuma linha de código. Ele morava **entre** os dois times, no espaço onde a mesma palavra significava duas coisas diferentes, e ninguém tinha percebido.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 840 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3dm-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
    <marker id="a3dm-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- The word "conta" -->
  <rect x="345" y="15" width="150" height="40" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="420" y="41" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="bold" fill="#7a5c00">"conta"</text>
  <line x1="375" y1="55" x2="220" y2="95" stroke="#888" stroke-width="2" marker-end="url(#a3dm-arrow)"/>
  <line x1="465" y1="55" x2="620" y2="95" stroke="#888" stroke-width="2" marker-end="url(#a3dm-arrow)"/>
  <!-- Diego -->
  <rect x="60" y="100" width="320" height="70" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="220" y="123" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d">Diego · Antifraude</text>
  <text x="220" y="143" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7f1d1d">conta = identidade do cliente</text>
  <text x="220" y="160" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#a05252">(CPF verificado — 1 por pessoa)</text>
  <!-- Marina -->
  <rect x="460" y="100" width="320" height="70" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="620" y="123" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#26215C">Marina · Pagamentos</text>
  <text x="620" y="143" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#26215C">conta = sub-carteira do ledger</text>
  <text x="620" y="160" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">(N por cliente: pessoal, negócio…)</text>
  <!-- Exploit -->
  <text x="90" y="205" font-family="sans-serif" font-size="12" fill="#666">O cliente com 2 carteiras:</text>
  <rect x="60" y="215" width="180" height="46" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="150" y="234" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Carteira pessoal</text>
  <text x="150" y="252" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">movimenta R$ X (limite)</text>
  <rect x="270" y="215" width="180" height="46" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="360" y="234" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Carteira negócio</text>
  <text x="360" y="252" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">movimenta R$ X (limite)</text>
  <line x1="450" y1="238" x2="540" y2="238" stroke="#b91c1c" stroke-width="2" marker-end="url(#a3dm-red)"/>
  <rect x="545" y="215" width="235" height="46" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2" stroke-dasharray="5 3"/>
  <text x="662" y="234" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">2× o limite diário</text>
  <text x="662" y="252" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">nenhum alerta dispara</text>
  <text x="420" y="300" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">A regra do Diego conta por identidade (1); o fluxo da Marina opera por carteira (2). O bug mora ENTRE os times.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A mesma palavra, dois significados, nenhuma fronteira explícita — o bug que nenhum teste unitário pega.</p>
</div>

Essa é a aula de hoje: **todo desastre de arquitetura que eu já vi começou com um substantivo errado.** E a solução não é "todo mundo usar a mesma palavra para tudo" — isso é impossível e, na verdade, indesejável. A solução é saber exatamente **onde** uma palavra pode mudar de significado, e desenhar uma fronteira explícita bem naquele ponto.

---

## 1. Domain-Driven Design, o essencial

A disciplina que dá nome a esse problema, e ferramentas para resolvê-lo, chama-se **Domain-Driven Design**, ou DDD — sistematizada por Eric Evans, e depois expandida por autores como Vaughn Vernon. Eu não vou dar o curso de DDD inteiro para vocês hoje; vou pegar só as quatro ideias que realmente mudam a arquitetura de uma fintech.

### 1.1 Linguagem ubíqua

A primeira ideia é a **linguagem ubíqua**: dentro de um contexto específico — e "contexto" aqui já é o segundo conceito, eu chego lá — todo mundo, do engenheiro ao especialista de negócio, usa exatamente as mesmas palavras, com exatamente o mesmo significado, para as mesmas coisas. Se o time de negócio chama uma coisa de "transferência" e o código chama a mesma coisa de "transfer_operation", vocês já perderam a linguagem ubíqua — e cada tradução mental que alguém precisa fazer entre "o que o negócio fala" e "o que o código diz" é um lugar onde um bug se esconde.

Mas reparem numa nuance importante, porque é exatamente o que pegou o Diego e a Marina: a linguagem ubíqua **não é global**. Ela vale dentro de um contexto. Fora dele, a mesma palavra pode — e frequentemente deve — significar outra coisa. O erro da TechPix não foi ter duas definições de "conta". O erro foi não saber que existiam duas definições, e não ter uma fronteira nomeada e explícita separando as duas.

### 1.2 Bounded context

Isso me leva à segunda ideia, a mais importante da aula: **bounded context**, contexto delimitado. Um bounded context é uma fronteira explícita dentro da qual um modelo de domínio, e a linguagem ubíqua que o descreve, valem sem ambiguidade. Dentro do contexto de Identidade, "conta" quer dizer uma coisa — a identidade verificada de um cliente. Dentro do contexto de Ledger, "conta" quer dizer outra — um livro contábil que registra lançamentos. Os dois estão certos, **dentro dos seus próprios limites**. O que não pode acontecer é alguém atravessar essa fronteira sem perceber que atravessou.

### 1.3 Agregados e invariantes

A terceira ideia formaliza algo que vocês já usam desde a Aula 1, só que sem esse nome: o **agregado**. Um agregado é um conjunto de objetos que forma uma fronteira de consistência — tudo dentro do agregado é protegido, transacionalmente, por uma invariante que nunca pode ser violada. Lembram da regra sagrada do ledger, Σ débitos igual Σ créditos, e do saldo que nunca pode ficar negativo? Isso é, literalmente, a invariante de um agregado — o agregado **Ledger**. Tudo que precisa ser atualizado junto, na mesma transação, para essa invariante se manter, mora dentro do mesmo agregado. Tudo que pode esperar, que pode ser atualizado um instante depois, mora fora dele, e se comunica por evento.

### 1.4 Eventos de domínio

E a quarta ideia é o **evento de domínio**: um fato que aconteceu no negócio e que importa registrar — não um detalhe técnico como "linha inserida na tabela X", mas algo que um especialista de negócio reconheceria e nomearia, como "Pix Liquidado" ou "Chave Resolvida". Vocês já viram esses eventos aparecerem informalmente nas duas aulas passadas. Hoje, a gente vai usá-los como matéria-prima para descobrir as fronteiras de contexto — não impostas de cima para baixo, mas emergindo de baixo para cima, a partir dos próprios fatos do domínio.

### 1.5 Nem todo pedaço do domínio vale o mesmo: core, supporting e generic

Antes de sair descobrindo fronteiras, tem uma pergunta que muda mais decisões de engenharia do que qualquer diagrama: **este pedaço do domínio é a razão de a empresa existir, ou é só o custo de estar no ramo?**

O DDD estratégico separa os subdomínios em três tipos, e cada tipo pede uma decisão de investimento diferente:

- **Core** — é onde mora a vantagem competitiva. Se um concorrente copiar isso, vocês perdem o negócio. Aqui vai o melhor time, o código próprio, o cuidado com invariante, o teste mais rigoroso. **Core não se compra, e não se terceiriza.**
- **Supporting** — é específico do negócio de vocês, precisa existir, mas não diferencia ninguém. Aqui a ordem é: construir **simples**, resistir à tentação de sofisticar, e aceitar que "bom o bastante" é o alvo certo.
- **Generic** — é um problema já resolvido, igual para todo mundo do mercado. Aqui a decisão default é **comprar**, e a pergunta a fazer não é "conseguimos construir?" — quase sempre a resposta é sim — mas "por que gastaríamos o nosso tempo escasso reconstruindo isso?"

Aplicando na TechPix, e reparem que algumas classificações são discutíveis de propósito, porque é justamente essa discussão que vale a sala:

| Subdomínio | Tipo | Por quê | Decisão que decorre |
|---|---|---|---|
| **Contas e Ledger** | Core | É literalmente o produto: a promessa de que o dinheiro está certo. Um erro aqui não é bug, é dano patrimonial. | Construir, com o melhor time. Invariantes viram teste. Nada de framework mágico no meio. |
| **Antifraude e Limites** | Core | Aprovar mais transações legítimas com menos fraude **é** a margem da fintech. Dois PSPs com o mesmo Pix e antifraudes diferentes têm negócios diferentes. | Construir e evoluir sempre — é aqui que a Aula 5 vai colocar modelo de risco. |
| **Pagamentos (orquestração Pix)** | Supporting | Aqui está a armadilha favorita da sala: parece core porque é o fluxo mais visível, mas o `pacs.008` é **igual para todos os participantes** — o Banco Central dita o formato, o prazo e a semântica. Ninguém ganha mercado por orquestrar o Pix melhor. | Construir robusto e chato. A diferenciação está no que acontece **em volta** dele, não nele. |
| **Devoluções e Disputas** | Supporting | Específico, regulado, necessário — mas é raro alguém escolher uma fintech pela qualidade do fluxo de MED. | Construir simples. Não sofisticar antes de o volume exigir. |
| **Identidade e Onboarding (KYC)** | Generic (com tempero) | Validar documento, prova de vida, consultar listas restritivas — isso é comprado de fornecedor por praticamente todo o mercado. | Comprar o motor, **construir apenas a política** de aceite (que aí é de vocês). |
| **Notificações** | Generic | Ninguém abre conta por causa do push. | Comprar. E nunca colocar o melhor engenheiro aqui. |

E o erro clássico, que eu já vi custar anos de roadmap, é **exatamente o inverso disso**: o time investe a melhor engenharia construindo do zero um motor de KYC — genérico, caro, sem diferencial nenhum — e ao mesmo tempo compra uma caixa-preta de antifraude, entregando para um fornecedor a única peça que realmente decidia se a empresa ganhava ou perdia dinheiro. O sistema fica "moderno" e a empresa fica sem vantagem.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 470" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3sd-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <text x="450" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Onde investir engenharia: os subdomínios da TechPix</text>

  <!-- quadrants -->
  <rect x="120" y="46" width="330" height="170" fill="#faf6ff" stroke="#ddd" stroke-width="1"/>
  <rect x="450" y="46" width="330" height="170" fill="#f0fdf4" stroke="#ddd" stroke-width="1"/>
  <rect x="120" y="216" width="330" height="160" fill="#f5f5f4" stroke="#ddd" stroke-width="1"/>
  <rect x="450" y="216" width="330" height="160" fill="#fffdf3" stroke="#ddd" stroke-width="1"/>

  <text x="132" y="66" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7c3aed">SUPPORTING caro</text>
  <text x="132" y="80" font-family="sans-serif" font-size="10" fill="#7c3aed">complexo e não diferencia → construir chato, nunca sofisticar</text>
  <text x="768" y="66" text-anchor="end" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">CORE</text>
  <text x="768" y="80" text-anchor="end" font-family="sans-serif" font-size="10" fill="#166534">o melhor time · código próprio · invariante virando teste</text>
  <text x="132" y="236" font-family="sans-serif" font-size="11" font-weight="bold" fill="#57534e">GENERIC</text>
  <text x="132" y="250" font-family="sans-serif" font-size="10" fill="#78716c">problema resolvido → comprar</text>
  <text x="768" y="236" text-anchor="end" font-family="sans-serif" font-size="11" font-weight="bold" fill="#a16207">RARO E ÓTIMO</text>
  <text x="768" y="250" text-anchor="end" font-family="sans-serif" font-size="10" fill="#a16207">barato de construir e diferencia → faça já</text>

  <!-- axes -->
  <line x1="120" y1="376" x2="800" y2="376" stroke="#1a1a1a" stroke-width="1.5" marker-end="url(#a3sd-arrow)"/>
  <line x1="120" y1="376" x2="120" y2="40" stroke="#1a1a1a" stroke-width="1.5" marker-end="url(#a3sd-arrow)"/>
  <text x="460" y="398" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">diferenciação competitiva  →</text>
  <text x="0" y="0" transform="translate(104,210) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">complexidade do modelo  →</text>

  <!-- plotted contexts -->
  <g font-family="sans-serif">
    <rect x="600" y="88" width="165" height="44" rx="8" fill="#fff" stroke="#166534" stroke-width="2"/>
    <text x="682" y="107" text-anchor="middle" font-size="12" font-weight="bold" fill="#166534">Contas e Ledger</text>
    <text x="682" y="123" text-anchor="middle" font-size="10" fill="#3f7a52">a verdade do dinheiro</text>

    <rect x="600" y="146" width="165" height="44" rx="8" fill="#fff" stroke="#166534" stroke-width="2"/>
    <text x="682" y="165" text-anchor="middle" font-size="12" font-weight="bold" fill="#166534">Antifraude e Limites</text>
    <text x="682" y="181" text-anchor="middle" font-size="10" fill="#3f7a52">a margem da fintech (Aula 5)</text>

    <rect x="175" y="100" width="185" height="44" rx="8" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
    <text x="267" y="119" text-anchor="middle" font-size="12" font-weight="bold" fill="#5b21b6">Pagamentos (Pix)</text>
    <text x="267" y="135" text-anchor="middle" font-size="10" fill="#7c3aed">complexo, mas o BACEN dita</text>

    <rect x="175" y="158" width="185" height="44" rx="8" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
    <text x="267" y="177" text-anchor="middle" font-size="12" font-weight="bold" fill="#5b21b6">Devoluções / MED</text>
    <text x="267" y="193" text-anchor="middle" font-size="10" fill="#7c3aed">regulado, não vende</text>

    <rect x="175" y="270" width="185" height="44" rx="8" fill="#fff" stroke="#57534e" stroke-width="2"/>
    <text x="267" y="289" text-anchor="middle" font-size="12" font-weight="bold" fill="#44403c">Identidade / KYC</text>
    <text x="267" y="305" text-anchor="middle" font-size="10" fill="#78716c">comprar o motor, fazer a política</text>

    <rect x="175" y="322" width="185" height="40" rx="8" fill="#fff" stroke="#57534e" stroke-width="2"/>
    <text x="267" y="347" text-anchor="middle" font-size="12" font-weight="bold" fill="#44403c">Notificações</text>
  </g>

  <!-- the classic mistake -->
  <rect x="450" y="412" width="350" height="46" rx="9" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="625" y="431" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">O erro clássico: construir o genérico, comprar o core</text>
  <text x="625" y="448" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">KYC próprio do zero + antifraude caixa-preta de fornecedor</text>
  <rect x="120" y="412" width="310" height="46" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="275" y="431" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">A regra: engenharia escassa vai para a direita</text>
  <text x="275" y="448" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3f7a52">quanto mais à esquerda, mais "comprar" é a resposta certa</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Nem todo contexto merece o mesmo investimento: a classificação em core, supporting e generic é uma decisão de alocação de engenharia, não um rótulo acadêmico.</p>
</div>

Duas ressalvas honestas antes de seguir. A primeira: **essa classificação muda com o tempo.** O que hoje é core pode virar commodity quando o mercado inteiro alcançar vocês — e o contrário também acontece, e é a origem de várias empresas de infraestrutura: alguém construiu tão bem um pedaço genérico que ele virou produto. Revisitem a classificação uma vez por ano, não uma vez na vida. A segunda: **"comprar" não elimina a fronteira, ela a torna mais importante.** Todo fornecedor que entra pelo lado generic entra atrás de um ACL — o mesmo padrão da Seção 3.2 — porque trocar de fornecedor de KYC daqui a dois anos precisa ser um projeto de duas semanas, não uma reescrita.

---

---

## 2. Event Storming: descobrindo fronteiras ao vivo

A técnica que eu quero ensinar para vocês hoje chama-se **event storming**, criada por Alberto Brandolini. A mecânica é simples de descrever e poderosa na prática: numa sala — ou, aqui na aula, no nosso Excalidraw — vocês colam post-its laranjas, cada um descrevendo um evento de domínio, no passado, com o verbo conjugado — "Pix Iniciado", não "Iniciar Pix". Colam esses eventos numa linha do tempo, da esquerda para a direita, na ordem em que eles acontecem. E o mais importante: fazem isso **coletivamente**, com pessoas de áreas diferentes, porque é exatamente no atrito entre visões diferentes que os pontos cegos — como o do Diego e da Marina — aparecem.

Antes de fazer isso ao vivo com o fluxo do Pix, porém, eu preciso dar para vocês a notação completa — porque o laranja é só a primeira das cores, e as outras é que fazem a técnica funcionar.

### 2.1 A gramática do event storming: as cores e a frase que elas formam

Antes de colar o primeiro post-it, vocês precisam da notação — e ela é mais do que decoração. Cada cor representa um **tipo de coisa** diferente no domínio, e a sequência das cores forma uma frase que se repete o tempo todo. Aprender essa frase é aprender a técnica.

| Cor | O que representa | Como se nomeia | O que vira no código |
|---|---|---|---|
| 🟧 **Laranja** | **Evento de domínio** — um fato que aconteceu | verbo no passado: `PixLiquidado` | a mensagem publicada no Outbox (Aula 2) |
| 🟦 **Azul** | **Comando** — uma intenção, um pedido que pode ser recusado | verbo no imperativo: `IniciarPix` | o endpoint, o caso de uso, o handler |
| 🟨 **Amarelo pequeno** | **Ator** — quem dispara o comando | o papel: "Ana, pagadora" | o usuário autenticado, o job, o sistema |
| 🟪 **Amarelo grande / lilás** | **Agregado** — onde a regra decide se o comando vira evento | substantivo: `Pagamento` | a fronteira transacional (Seção 4) |
| 🟣 **Roxo** | **Política** — "sempre que *tal evento*, então *tal comando*" | frase condicional | o consumidor do evento, a saga |
| 🟩 **Verde** | **Read model** — a informação que alguém olha antes de decidir | substantivo: "saldo exibido" | a projeção do CQRS (Aula 2) |
| 🟥 **Rosa** | **Sistema externo** — o que vocês não controlam | o nome real: DICT, SPI | o que fica atrás de um ACL (Seção 3.2) |
| 🔴 **Vermelho** | **Hotspot** — dúvida, conflito, discordância | uma pergunta | nada — e é justamente por isso que importa |

E agora a frase, que é o coração da técnica:

> **Um ator, olhando um read model, dispara um comando. O comando chega a um agregado, que decide segundo suas invariantes e produz um evento. O evento aciona uma política, que dispara o próximo comando.**

Reparem no que essa frase resolve: vocês não precisam **decidir** onde estão os agregados. Eles aparecem sozinhos, como o lugar onde os comandos aterrissam e uma regra decide. E as políticas roxas — que numa sala de post-its parecem o pedaço mais burocrático — são, literalmente, os consumidores de evento que vocês vão escrever depois. O post-it roxo de hoje é o `@KafkaListener` de daqui a três semanas.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 970 452" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3gr-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#666"/>
    </marker>
    <marker id="a3gr-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <text x="485" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">A gramática: ator → comando → agregado → evento → política → comando</text>

  <!-- legenda -->
  <g font-family="sans-serif" font-size="10">
    <rect x="20" y="36" width="14" height="14" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5"/><text x="40" y="47" fill="#555">evento (fato, passado)</text>
    <rect x="200" y="36" width="14" height="14" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/><text x="220" y="47" fill="#555">comando (intenção)</text>
    <rect x="370" y="36" width="14" height="14" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/><text x="390" y="47" fill="#555">ator / agregado</text>
    <rect x="520" y="36" width="14" height="14" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.5"/><text x="540" y="47" fill="#555">política (sempre que…)</text>
    <rect x="700" y="36" width="14" height="14" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/><text x="720" y="47" fill="#555">read model</text>
    <rect x="820" y="36" width="14" height="14" fill="#fdf2f8" stroke="#db2777" stroke-width="1.5"/><text x="840" y="47" fill="#555">sistema externo</text>
  </g>

  <!-- LINHA A -->
  <g font-family="sans-serif">
    <rect x="20" y="80" width="150" height="56" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
    <text x="95" y="104" text-anchor="middle" font-size="12" font-weight="bold" fill="#7a5c00">Ana</text>
    <text x="95" y="121" text-anchor="middle" font-size="10" fill="#8a6d1a">ator · pagadora</text>

    <line x1="170" y1="108" x2="212" y2="108" stroke="#666" stroke-width="2" marker-end="url(#a3gr-arrow)"/>

    <rect x="215" y="80" width="150" height="56" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="290" y="104" text-anchor="middle" font-size="12" font-weight="bold" fill="#166534">Saldo exibido</text>
    <text x="290" y="121" text-anchor="middle" font-size="10" fill="#3f7a52">read model · projeção CQRS</text>

    <line x1="365" y1="108" x2="407" y2="108" stroke="#666" stroke-width="2" marker-end="url(#a3gr-arrow)"/>

    <rect x="410" y="80" width="150" height="56" rx="6" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
    <text x="485" y="104" text-anchor="middle" font-size="12" font-weight="bold" fill="#1e3a8a">IniciarPix</text>
    <text x="485" y="121" text-anchor="middle" font-size="10" fill="#1d4ed8">comando · pode ser recusado</text>

    <line x1="560" y1="108" x2="602" y2="108" stroke="#666" stroke-width="2" marker-end="url(#a3gr-arrow)"/>

    <rect x="605" y="80" width="150" height="56" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="3"/>
    <text x="680" y="104" text-anchor="middle" font-size="12" font-weight="bold" fill="#7a5c00">Pagamento</text>
    <text x="680" y="121" text-anchor="middle" font-size="10" fill="#8a6d1a">agregado · decide</text>

    <line x1="755" y1="108" x2="797" y2="108" stroke="#666" stroke-width="2" marker-end="url(#a3gr-arrow)"/>

    <rect x="800" y="80" width="150" height="56" rx="6" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
    <text x="875" y="104" text-anchor="middle" font-size="12" font-weight="bold" fill="#7c2d12">PixIniciado</text>
    <text x="875" y="121" text-anchor="middle" font-size="10" fill="#9a3412">evento · fato consumado</text>
  </g>

  <!-- hotspot -->
  <g transform="rotate(-2 700 190)">
    <rect x="600" y="158" width="200" height="60" rx="4" fill="#fef2f2" stroke="#b91c1c" stroke-width="2.5"/>
    <text x="700" y="180" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#b91c1c">🔴 HOTSPOT</text>
    <text x="700" y="197" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#991b1b">"conta" aqui é identidade</text>
    <text x="700" y="211" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#991b1b">ou sub-carteira do ledger?</text>
  </g>
  <line x1="680" y1="138" x2="690" y2="156" stroke="#b91c1c" stroke-width="2" marker-end="url(#a3gr-red)"/>

  <!-- conector A -> B -->
  <polyline points="875,138 875,250 95,250 95,282" fill="none" stroke="#666" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#a3gr-arrow)"/>
  <text x="480" y="243" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">o evento não termina a história — ele aciona a próxima política</text>

  <!-- LINHA B -->
  <g font-family="sans-serif">
    <rect x="20" y="286" width="205" height="56" rx="6" fill="#f5f3ff" stroke="#7c3aed" stroke-width="2"/>
    <text x="122" y="308" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#5b21b6">Sempre que PixIniciado,</text>
    <text x="122" y="324" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#5b21b6">resolver a chave</text>
    <text x="122" y="337" text-anchor="middle" font-size="9.5" fill="#7c3aed">política · vira consumidor de evento</text>

    <line x1="225" y1="314" x2="262" y2="314" stroke="#666" stroke-width="2" marker-end="url(#a3gr-arrow)"/>

    <rect x="265" y="286" width="150" height="56" rx="6" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
    <text x="340" y="312" text-anchor="middle" font-size="12" font-weight="bold" fill="#1e3a8a">ResolverChave</text>
    <text x="340" y="328" text-anchor="middle" font-size="10" fill="#1d4ed8">comando</text>

    <line x1="415" y1="314" x2="452" y2="314" stroke="#666" stroke-width="2" marker-end="url(#a3gr-arrow)"/>

    <rect x="455" y="286" width="150" height="56" rx="6" fill="#fdf2f8" stroke="#db2777" stroke-width="2"/>
    <text x="530" y="312" text-anchor="middle" font-size="12" font-weight="bold" fill="#9d174d">DICT (BACEN)</text>
    <text x="530" y="328" text-anchor="middle" font-size="10" fill="#be185d">externo · sempre atrás de ACL</text>

    <line x1="605" y1="314" x2="642" y2="314" stroke="#666" stroke-width="2" marker-end="url(#a3gr-arrow)"/>

    <rect x="645" y="286" width="150" height="56" rx="6" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
    <text x="720" y="312" text-anchor="middle" font-size="12" font-weight="bold" fill="#7c2d12">ChaveResolvida</text>
    <text x="720" y="328" text-anchor="middle" font-size="10" fill="#9a3412">evento</text>

    <line x1="795" y1="314" x2="832" y2="314" stroke="#666" stroke-width="2" stroke-dasharray="4 3" marker-end="url(#a3gr-arrow)"/>
    <text x="895" y="310" text-anchor="middle" font-size="11" font-style="italic" fill="#666">…e a frase</text>
    <text x="895" y="326" text-anchor="middle" font-size="11" font-style="italic" fill="#666">recomeça</text>
  </g>

  <rect x="20" y="368" width="930" height="66" rx="9" fill="#fff" stroke="#d4a017" stroke-width="1.5"/>
  <text x="485" y="390" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Vocês não <tspan font-style="italic">decidem</tspan> onde ficam os agregados — eles aparecem como o lugar onde os comandos aterrissam e uma invariante decide.</text>
  <text x="485" y="410" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">E o post-it vermelho é o artefato mais valioso da sessão: ele marca, no papel, o bug que ainda não aconteceu.</text>
  <text x="485" y="428" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">post-it roxo de hoje = consumidor de evento de daqui a três semanas · post-it rosa = a fronteira onde mora o ACL</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A gramática do event storming aplicada ao Pix — e o hotspot vermelho marcando, na hora, a ambiguidade que gerou o bug do Diego e da Marina.</p>
</div>

Uma regra de facilitação que vale mais que qualquer diagrama: **quando a sala discorda, não resolva a discordância — cole um post-it vermelho.** A tentação de fechar a discussão na hora é enorme, e é justamente ela que apaga o sinal. O hotspot é o registro de que existe ambiguidade ali; ele vira, depois, uma pergunta para um especialista, um item de spec, ou — como vocês vão ver na Seção 5 — uma pergunta do `/speckit.clarify`.

### 2.2 O rio de eventos do Pix

Com a notação na mão, vamos fazer o exercício ao vivo, com o fluxo do Pix que a gente já conhece desde a Aula 1. Deixa eu escrever a sequência de eventos, na ordem:

```
PixIniciado → ChaveResolvida → LimitesValidados → FundosReservados →
OrdemEnviadaAoSPI → PixLiquidado → (ramificação:) PixDevolvido
```

Reparem que cada um desses nomes é reconhecível por um especialista de negócio, não só por um engenheiro. "PixIniciado" é quando a Ana toca em pagar. "ChaveResolvida" é quando o DICT devolve a instituição e a conta do Bruno — aquela consulta síncrona que quase derrubou o sistema na Aula 2. "LimitesValidados" é a checagem de antifraude e PLD-FT que a gente viu na Aula 1. "FundosReservados" é o lançamento no ledger. "OrdemEnviadaAoSPI" é a mensagem `pacs.008`. "PixLiquidado" é a confirmação `pacs.002`. E, como ramificação possível, "PixDevolvido" — a mensagem `pacs.004`, ou o trilho do MED, quando algo dá errado.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 940 240" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3rio-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
    <marker id="a3rio-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <text x="20" y="26" font-family="sans-serif" font-size="12" fill="#666">tempo →   (post-its laranja, verbo no passado)</text>
  <!-- Post-its: 6 in a row -->
  <g transform="rotate(-1 90 85)">
    <rect x="25" y="50" width="125" height="62" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
    <text x="87" y="86" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7c2d12">PixIniciado</text>
  </g>
  <line x1="152" y1="81" x2="172" y2="81" stroke="#888" stroke-width="2" marker-end="url(#a3rio-arrow)"/>
  <g transform="rotate(1 240 85)">
    <rect x="177" y="50" width="125" height="62" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
    <text x="239" y="86" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7c2d12">ChaveResolvida</text>
  </g>
  <line x1="304" y1="81" x2="324" y2="81" stroke="#888" stroke-width="2" marker-end="url(#a3rio-arrow)"/>
  <g transform="rotate(-1 392 85)">
    <rect x="329" y="50" width="127" height="62" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
    <text x="392" y="86" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#7c2d12">LimitesValidados</text>
  </g>
  <line x1="458" y1="81" x2="478" y2="81" stroke="#888" stroke-width="2" marker-end="url(#a3rio-arrow)"/>
  <g transform="rotate(1 546 85)">
    <rect x="483" y="50" width="127" height="62" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
    <text x="546" y="86" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#7c2d12">FundosReservados</text>
  </g>
  <line x1="612" y1="81" x2="632" y2="81" stroke="#888" stroke-width="2" marker-end="url(#a3rio-arrow)"/>
  <g transform="rotate(-1 702 85)">
    <rect x="637" y="50" width="130" height="62" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
    <text x="702" y="80" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#7c2d12">OrdemEnviada</text>
    <text x="702" y="96" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#7c2d12">AoSPI</text>
  </g>
  <line x1="769" y1="81" x2="789" y2="81" stroke="#888" stroke-width="2" marker-end="url(#a3rio-arrow)"/>
  <g transform="rotate(1 855 85)">
    <rect x="794" y="50" width="125" height="62" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
    <text x="856" y="86" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7c2d12">PixLiquidado</text>
  </g>
  <!-- Branch: PixDevolvido -->
  <line x1="856" y1="114" x2="770" y2="165" stroke="#b91c1c" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#a3rio-red)"/>
  <text x="850" y="150" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">se algo der errado</text>
  <g transform="rotate(-2 700 195)">
    <rect x="635" y="168" width="130" height="56" rx="3" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
    <text x="700" y="200" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">PixDevolvido</text>
  </g>
  <text x="615" y="200" text-anchor="end" font-family="sans-serif" font-size="12" fill="#666">pacs.004 / trilho do MED — a ramificação de exceção também é um fato de negócio</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O rio de eventos do Pix: fatos do domínio no passado, na ordem em que acontecem — a matéria-prima do event storming.</p>
</div>

### 2.3 Os contextos emergem dos eventos

Agora vem a parte mágica do event storming: em vez de eu chegar com uma divisão pronta, a gente **agrupa** esses eventos por quem cuida deles, e as fronteiras aparecem sozinhas.

- "PixIniciado" e "LimitesValidados" dependem de saber quem é o cliente e se ele pode operar — isso puxa para um contexto de **Identidade e Onboarding**, que na verdade nem aparece diretamente no fluxo do Pix, mas é usado por ele o tempo inteiro, por trás.
- "FundosReservados" e a confirmação de liquidação vivem, sem dúvida, no contexto de **Contas e Ledger** — a verdade do dinheiro, que a gente construiu na Aula 1.
- "ChaveResolvida", "OrdemEnviadaAoSPI" e "PixLiquidado" formam o núcleo de um contexto de **Pagamentos**, que orquestra a conversa com o mundo externo — DICT e SPI.
- "LimitesValidados", olhando mais de perto, na verdade tem uma parte que pertence a um contexto separado: **Antifraude e Limites** — que decide, com sua própria lógica, se uma operação é suspeita.
- E "PixDevolvido" puxa para um contexto de **Devoluções e Disputas**, que lida com o MED e com reclamações.

Reparem que eu não impus essa divisão no início da aula. Ela **emergiu** dos próprios eventos, porque eventos que mudam junto, que são cuidados pela mesma equipe, com a mesma linguagem, naturalmente se agrupam. É isso que faz o event storming ser tão mais confiável que um palpite educado como o que eu dei na Aula 2.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 940 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="24" font-family="sans-serif" font-size="12" fill="#666">os mesmos post-its, agora agrupados por quem cuida deles — as fronteiras aparecem sozinhas</text>
  <!-- Pagamentos -->
  <rect x="20" y="40" width="300" height="130" rx="12" fill="#eef2ff" stroke="#4338ca" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="170" y="62" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#26215C">Pagamentos</text>
  <rect x="35" y="75" width="125" height="38" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5"/>
  <text x="97" y="98" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">ChaveResolvida</text>
  <rect x="172" y="75" width="132" height="38" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5"/>
  <text x="238" y="98" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">OrdemEnviadaAoSPI</text>
  <rect x="35" y="122" width="125" height="38" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5"/>
  <text x="97" y="145" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">PixLiquidado</text>
  <text x="238" y="145" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">orquestra DICT + SPI</text>
  <!-- Contas e Ledger -->
  <rect x="340" y="40" width="280" height="130" rx="12" fill="#f0fdf4" stroke="#166534" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="480" y="62" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">Contas e Ledger</text>
  <rect x="355" y="75" width="140" height="38" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5"/>
  <text x="425" y="98" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">FundosReservados</text>
  <text x="480" y="145" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3f7a52">a verdade do dinheiro (Aula 1)</text>
  <!-- Antifraude -->
  <rect x="640" y="40" width="280" height="130" rx="12" fill="#fef2f2" stroke="#b91c1c" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="780" y="62" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d">Antifraude e Limites</text>
  <rect x="655" y="75" width="140" height="38" rx="3" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5"/>
  <text x="725" y="98" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">LimitesValidados</text>
  <text x="780" y="145" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#a05252">lógica própria de risco</text>
  <!-- Identidade -->
  <rect x="20" y="190" width="440" height="80" rx="12" fill="#fef9e7" stroke="#d4a017" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="240" y="214" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">Identidade e Onboarding</text>
  <text x="240" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#8a6d1a">não aparece no rio — mas é usado por trás o tempo inteiro (quem é o cliente? pode operar?)</text>
  <!-- Devoluções -->
  <rect x="480" y="190" width="440" height="80" rx="12" fill="#f5f5f4" stroke="#57534e" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="700" y="214" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#44403c">Devoluções e Disputas</text>
  <rect x="530" y="224" width="120" height="36" rx="3" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="590" y="246" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">PixDevolvido</text>
  <text x="790" y="246" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">MED, reclamações, disputas</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Os 5 bounded contexts da TechPix emergindo do agrupamento dos eventos — de baixo para cima, não por palpite.</p>
</div>

E aqui está o ponto que eu quero que vocês levem: se o Diego e a Marina tivessem feito esse exercício juntos, na mesma sala, com os post-its na mesma mesa, o momento em que "conta" aparecesse duas vezes, com dois significados, teria sido visível na hora — porque um post-it do contexto de Identidade e um post-it do contexto de Ledger, os dois dizendo "conta", ficariam lado a lado, forçando a pergunta: "espera, essa é a mesma conta?"

### 2.4 Os três níveis: a mesma técnica, três profundidades

Uma confusão comum é achar que event storming é uma coisa só. São três, com objetivos, participantes e durações diferentes — e misturá-los é a causa número um de sessão frustrada.

| Nível | Objetivo | Quem participa | Notação usada | Duração típica |
|---|---|---|---|---|
| **Big Picture** | Descobrir o mapa: quais fluxos existem e onde estão as fronteiras | O máximo de áreas possível — negócio, produto, operação, engenharia, compliance | Só eventos 🟧 e hotspots 🔴 | meio dia a um dia |
| **Process Level** | Entender **um** fluxo de ponta a ponta | Quem opera aquele fluxo + quem vai construir | + comandos 🟦, atores 🟨, políticas 🟣, read models 🟩, externos 🟥 | 2 a 4 horas por fluxo |
| **Design Level** | Chegar em agregados, invariantes e contratos | Só o time que vai escrever o código | + agregados e as invariantes de cada um | 2 a 3 horas, já perto do código |

O que a gente fez agora, ao vivo, foi um **Big Picture** curto seguido de um **Process Level** do Pix. A Seção 4 desta aula é, na prática, o Design Level: é lá que a gente pergunta "que regra este agregado não pode violar nunca?".

E o erro clássico, que vale nomear: **começar pelo Design Level.** É o instinto do engenheiro — pular direto para "quais são as entidades?" — e é o caminho mais rápido para reproduzir em post-it exatamente as fronteiras erradas que já estavam no código. O valor do Big Picture é justamente ele **não** deixar você desenhar entidade nenhuma antes de ter visto o fluxo inteiro pelos olhos de quem não é engenheiro.

### 2.5 Como saber se a fronteira está no lugar certo (quatro testes que dão para medir)

O event storming produz uma hipótese de fronteira, não uma verdade revelada. E como isso é System Design, e não fé, a hipótese precisa passar por teste. Eu uso quatro — e os três primeiros dão para rodar **em cima do repositório que vocês já têm**, hoje à tarde.

**Teste 1 — a palavra muda de significado ao atravessar?** Este é o teste semântico, e é o único que não é automatizável. Se "conta" quer dizer uma coisa de um lado e outra do outro lado, a fronteira está no lugar certo — é exatamente ali que precisa existir tradução. O sinal de alarme é o inverso: se a mesma palavra atravessa a fronteira **sem mudar nada**, é bem provável que vocês tenham cortado um conceito no meio.

**Teste 2 — a co-mudança.** Se dois módulos aparecem quase sempre no mesmo commit, a fronteira entre eles é decorativa: o código está dizendo, no histórico, que os dois são a mesma coisa. E isso é mensurável direto no Git:

```bash
# pares de módulos que mudam no mesmo commit, últimos 6 meses
git log --since='6 months ago' --pretty=format:'---' --name-only \
| awk '
  function flush(){ for(i=1;i<=n;i++) for(j=i+1;j<=n;j++)
                      print (m[i]<m[j] ? m[i]" ~ "m[j] : m[j]" ~ "m[i]);
                    n=0; split("",seen) }
  /^---/ { flush(); next }
  NF     { split($0,p,"/"); k=p[1]"/"p[2];
           if (!(k in seen)) { seen[k]=1; m[++n]=k } }
  END    { flush() }
' | sort | uniq -c | sort -rn | head -20
```

A leitura é simples: divida a contagem de cada par pelo número de commits que tocaram o módulo mais ativo dos dois. Abaixo de ~15%, a fronteira está saudável. Acima de ~40%, vocês têm dois módulos que são, na prática, um só — e nenhum diagrama bonito vai mudar esse fato. (Para fazer isso a sério, os nomes são **code-maat** e **CodeScene**, do Adam Tornhill, que transformam o histórico do Git em mapa de acoplamento.)

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 920 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="460" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Matriz de co-mudança: quantos % dos commits de A também tocam B</text>

  <g font-family="sans-serif" font-size="10.5" fill="#555">
    <text x="235" y="62" text-anchor="middle">pagamentos</text>
    <text x="345" y="62" text-anchor="middle">ledger</text>
    <text x="455" y="62" text-anchor="middle">antifraude</text>
    <text x="565" y="62" text-anchor="middle">identidade</text>
    <text x="675" y="62" text-anchor="middle">devoluções</text>
  </g>

  <g font-family="sans-serif" font-size="10.5" fill="#555">
    <text x="170" y="95" text-anchor="end">pagamentos</text>
    <text x="170" y="141" text-anchor="end">ledger</text>
    <text x="170" y="187" text-anchor="end">antifraude</text>
    <text x="170" y="233" text-anchor="end">identidade</text>
    <text x="170" y="279" text-anchor="end">devoluções</text>
  </g>

  <!-- linha pagamentos -->
  <rect x="180" y="72" width="110" height="40" fill="#eee" stroke="#fff" stroke-width="2"/><text x="235" y="97" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#999">—</text>
  <rect x="290" y="72" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="345" y="97" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">12%</text>
  <rect x="400" y="72" width="110" height="40" fill="#fecaca" stroke="#b91c1c" stroke-width="2.5"/><text x="455" y="97" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d">48%</text>
  <rect x="510" y="72" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="565" y="97" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">4%</text>
  <rect x="620" y="72" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="675" y="97" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">9%</text>
  <!-- linha ledger -->
  <rect x="180" y="118" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="235" y="143" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">12%</text>
  <rect x="290" y="118" width="110" height="40" fill="#eee" stroke="#fff" stroke-width="2"/><text x="345" y="143" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#999">—</text>
  <rect x="400" y="118" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="455" y="143" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">6%</text>
  <rect x="510" y="118" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="565" y="143" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">3%</text>
  <rect x="620" y="118" width="110" height="40" fill="#fef9c3" stroke="#fff" stroke-width="2"/><text x="675" y="143" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#854d0e">18%</text>
  <!-- linha antifraude -->
  <rect x="180" y="164" width="110" height="40" fill="#fecaca" stroke="#b91c1c" stroke-width="2.5"/><text x="235" y="189" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d">48%</text>
  <rect x="290" y="164" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="345" y="189" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">6%</text>
  <rect x="400" y="164" width="110" height="40" fill="#eee" stroke="#fff" stroke-width="2"/><text x="455" y="189" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#999">—</text>
  <rect x="510" y="164" width="110" height="40" fill="#fef9c3" stroke="#fff" stroke-width="2"/><text x="565" y="189" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#854d0e">21%</text>
  <rect x="620" y="164" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="675" y="189" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">5%</text>
  <!-- linha identidade -->
  <rect x="180" y="210" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="235" y="235" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">4%</text>
  <rect x="290" y="210" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="345" y="235" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">3%</text>
  <rect x="400" y="210" width="110" height="40" fill="#fef9c3" stroke="#fff" stroke-width="2"/><text x="455" y="235" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#854d0e">21%</text>
  <rect x="510" y="210" width="110" height="40" fill="#eee" stroke="#fff" stroke-width="2"/><text x="565" y="235" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#999">—</text>
  <rect x="620" y="210" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="675" y="235" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">2%</text>
  <!-- linha devoluções -->
  <rect x="180" y="256" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="235" y="281" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">9%</text>
  <rect x="290" y="256" width="110" height="40" fill="#fef9c3" stroke="#fff" stroke-width="2"/><text x="345" y="281" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#854d0e">18%</text>
  <rect x="400" y="256" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="455" y="281" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">5%</text>
  <rect x="510" y="256" width="110" height="40" fill="#dcfce7" stroke="#fff" stroke-width="2"/><text x="565" y="281" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">2%</text>
  <rect x="620" y="256" width="110" height="40" fill="#eee" stroke="#fff" stroke-width="2"/><text x="675" y="281" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#999">—</text>

  <!-- legenda -->
  <rect x="760" y="72" width="20" height="16" fill="#dcfce7" stroke="#ccc"/><text x="788" y="85" font-family="sans-serif" font-size="10.5" fill="#555">&lt; 15% — saudável</text>
  <rect x="760" y="98" width="20" height="16" fill="#fef9c3" stroke="#ccc"/><text x="788" y="111" font-family="sans-serif" font-size="10.5" fill="#555">15–40% — observar</text>
  <rect x="760" y="124" width="20" height="16" fill="#fecaca" stroke="#ccc"/><text x="788" y="137" font-family="sans-serif" font-size="10.5" fill="#555">&gt; 40% — fronteira</text>
  <text x="788" y="151" font-family="sans-serif" font-size="10.5" fill="#555">decorativa</text>

  <rect x="180" y="320" width="550" height="60" rx="9" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="455" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">Pagamentos ~ Antifraude: 48% dos commits tocam os dois</text>
  <text x="455" y="360" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#991b1b">o histórico do Git está dizendo que a regra de limite mora nos dois lugares —</text>
  <text x="455" y="374" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#991b1b">é exatamente o rastro que o bug do Diego e da Marina deixa no repositório</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A fronteira de verdade não está no diagrama — está no histórico de commits. Co-mudança alta é fronteira que só existe no PowerPoint.</p>
</div>

**Teste 3 — o tráfego que atravessa (a "conversa fiada" entre contextos).** Contem quantas idas e vindas entre dois contextos são necessárias para completar **uma** operação de negócio. Uma fronteira boa tem tráfego baixo e de granularidade grossa: um Pix deveria precisar de **uma** consulta a Antifraude, não de doze. Se vocês precisam de várias chamadas encadeadas para montar uma decisão, o dado e a decisão estão em lados opostos da fronteira — e o conserto não é cache, é mover a fronteira. (Na Aula 4, esse mesmo sintoma volta com o nome de aresta mal desenhada, e lá ele custa latência de rede.)

**Teste 4 — a invariante atravessada.** Existe alguma regra de negócio que precisa **ler e escrever dos dois lados na mesma transação**? Se existe, vocês cortaram um agregado ao meio, e o preço vai ser pago em saga, compensação e noite mal dormida. Esse teste é o mais severo dos quatro, e é o único que, quando falha, obriga a redesenhar — os outros três admitem convivência.

Uma nota de honestidade sobre os quatro: eles medem se a fronteira está **errada**, não provam que está certa. Fronteira é hipótese revisável — e é exatamente por isso que ela merece ADR, e não decreto.

---

## 3. O mapa de contexto: como os contextos conversam

Descobrir os contextos é só metade do trabalho. A outra metade é desenhar como eles **se relacionam** — porque contextos isolados de verdade, que nunca trocam informação, não existem numa fintech. O artefato que registra isso chama-se **context map**, o mapa de contexto, e ele usa um vocabulário específico para descrever cada tipo de relação.

### 3.1 Upstream e downstream

A relação mais comum é **upstream/downstream**: um contexto upstream toma decisões que o contexto downstream precisa respeitar, sem poder negociar de volta. No TechPix, o contexto de **Contas e Ledger** é upstream em relação a quase todo mundo — Pagamentos, Cartões, Antifraude, todos dependem da verdade que o Ledger define, mas o Ledger não muda seu modelo para agradar nenhum deles.

### 3.2 A camada anticorrupção — o ACL

E aqui está a relação mais importante para uma fintech: o **ACL**, a Anti-Corruption Layer, a camada anticorrupção. Ela existe quando o contexto de vocês precisa conversar com um sistema externo — cuja linguagem vocês não controlam — sem deixar essa linguagem externa **vazar** para dentro do domínio de vocês. E a TechPix já tem um ACL, desde a Aula 1, só que sem esse nome: é exatamente a camada que traduz a mensagem `pacs.008` do padrão ISO 20022, do jeito que o Banco Central define, para o evento de domínio "PixIniciado", do jeito que a TechPix entende. Se amanhã o Banco Central mudar o formato de uma mensagem — coisa que acontece, como vimos com o Pix Automático na Aula 1 —, o ACL absorve essa mudança sozinho, e o resto do domínio de vocês nem precisa saber que algo mudou do lado de fora.

### 3.3 Outras relações do vocabulário

Vale conhecer mais duas: o **conformista** — quando um contexto simplesmente aceita o modelo de outro, sem tradução nenhuma, porque não vale a pena o esforço de traduzir (às vezes o time de Cartões simplesmente aceita o vocabulário do Ledger tal como é, sem um ACL) — e o **shared kernel**, o núcleo compartilhado — quando dois contextos deliberadamente compartilham uma fatia pequena e bem definida de modelo, porque separar completamente custaria mais do que vale a pena (talvez o conceito de "moeda" e "valor monetário" seja um shared kernel entre Ledger e Pagamentos, porque seria estranho cada um ter sua própria definição de como representar um valor em reais).

### 3.4 O catálogo completo: os nove padrões, e como escolher

As três relações acima são as que mais aparecem, mas o DDD clássico cataloga nove. Eu não quero que vocês decorem — quero que vocês reconheçam, porque **a maioria dos times já está usando um desses padrões sem saber, e sofrendo justamente por não ter escolhido conscientemente**.

| Padrão | O que é | Quando faz sentido | Na TechPix |
|---|---|---|---|
| **Partnership** | Dois contextos evoluem juntos, com sucesso ou fracasso compartilhados; mudança de um exige coordenação com o outro | Dois times com objetivo comum e prazo comum — e disposição real de coordenar | Pagamentos e Antifraude, durante o projeto de um novo trilho |
| **Shared Kernel** | Uma fatia pequena de modelo compartilhada deliberadamente, com governança explícita | Quando duplicar sairia mais caro que coordenar — e **só** quando a fatia é pequena e estável | `Moeda`, `ValorMonetário`, `EndToEndId` |
| **Customer / Supplier** | Downstream é cliente com voz: pode negociar prioridade no backlog do upstream | Times na mesma empresa, com processo de priorização real | Cartões pedindo campos novos ao Ledger |
| **Conformista** | Downstream aceita o modelo do upstream tal como é, sem tradução | Quando o custo de traduzir supera o de se adaptar — e o upstream é estável | Cartões consumindo o modelo do Ledger |
| **ACL (Anti-Corruption Layer)** | Downstream traduz o modelo do upstream para o seu, e protege o próprio domínio | Sempre que o upstream é externo, instável, ou fala uma linguagem que vocês não escolheram | `pacs.008` → `PixIniciado` |
| **Open Host Service** | Upstream publica um protocolo de serviço estável, pensado para muitos consumidores | Quando um contexto tem muitos clientes e não dá para atender cada um sob medida | O SPI e o DICT, para os milhares de participantes |
| **Published Language** | Uma linguagem de intercâmbio bem documentada, compartilhada por todo um ecossistema | Quando a integração transcende duas partes | **ISO 20022** — literalmente uma published language |
| **Separate Ways** | Nenhuma integração: cada lado resolve por conta própria, aceitando duplicação | Quando integrar custa mais que duplicar, e a duplicação é tolerável | Um relatório interno que recalcula o próprio agregado |
| **Big Ball of Mud** | Ausência de fronteira — tudo acoplado a tudo | Nunca por escolha; sempre por omissão | O que o monólito da TechPix vira, se ninguém fizer esta aula |

E aqui está uma leitura que eu adoro fazer em sala, porque ela reorganiza tudo que a gente viu até agora: **o Banco Central é um Open Host Service com uma Published Language.** Ele não negocia formato com nenhum participante — publica o protocolo (o SPI, o DICT) e uma linguagem de intercâmbio (o ISO 20022) que vale para o ecossistema inteiro. E do lado da TechPix, a única resposta arquitetural sensata a um Open Host Service que vocês não controlam é: **ser conformista na borda e traduzir na entrada.** Ou seja — ACL. Não é coincidência que a mesma fronteira apareça sempre nesse desenho: ela é a consequência lógica do tipo de relação, não uma preferência de estilo.

Duas armadilhas para levar:

- **Shared kernel é o padrão mais perigoso da lista.** Ele parece o mais econômico ("por que duplicar `Moeda`?") e é o que mais silenciosamente recria o acoplamento que vocês acabaram de desfazer, porque cada mudança nele exige coordenação entre todos os contextos que o compartilham. A regra prática: shared kernel só para conceitos **estáveis, pequenos e sem regra de negócio** — tipos de valor, basicamente. No momento em que alguém quiser colocar uma política dentro do kernel, ele deixou de ser kernel.
- **Conformista não é derrota, é economia consciente.** A pergunta é sempre a mesma: quanto custa o dia em que o upstream mudar? Se a resposta for "meia hora", seja conformista. Se for "reescrevemos o contexto inteiro", pague o ACL.

### 3.5 O context map da TechPix

Juntando tudo: no centro, o contexto de **Contas e Ledger**, upstream de quase tudo. Ao lado, **Pagamentos**, que orquestra o Pix e fala com o mundo externo através de um **ACL** — e é exatamente aqui, nessa fronteira, que moram as mensagens `pacs.008`, `pacs.002`, `pacs.004`, e a consulta ao DICT. **Antifraude** conversa com Pagamentos de forma síncrona, no meio do fluxo, mas tem sua própria linguagem e seus próprios modelos de risco. **Identidade** é upstream de todo mundo que precisa saber quem é o cliente. E **Devoluções** cuida do que acontece quando o MED entra em cena, conversando tanto com Pagamentos quanto, de novo, com um ACL para o próprio DICT — porque o relato de infração, como vimos na Aula 1, também passa por lá.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 940 460" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3cm-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a3cm-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <!-- Identidade (top, upstream de todos) -->
  <rect x="330" y="20" width="280" height="56" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="470" y="44" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">Identidade e Onboarding</text>
  <text x="470" y="62" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#8a6d1a">upstream de todos (quem é o cliente)</text>
  <line x1="400" y1="76" x2="210" y2="140" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a3cm-gray)"/>
  <line x1="470" y1="76" x2="470" y2="140" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a3cm-gray)"/>
  <line x1="540" y1="76" x2="720" y2="140" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a3cm-gray)"/>
  <!-- Ledger (center) -->
  <rect x="360" y="145" width="220" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="470" y="172" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">Contas e Ledger</text>
  <text x="470" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3f7a52">UPSTREAM — a verdade do dinheiro</text>
  <text x="470" y="210" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3f7a52">Σ débitos = Σ créditos</text>
  <!-- Pagamentos (left) -->
  <rect x="60" y="145" width="230" height="80" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="175" y="172" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#26215C">Pagamentos</text>
  <text x="175" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">orquestra o Pix</text>
  <text x="175" y="210" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">downstream do Ledger</text>
  <line x1="360" y1="185" x2="290" y2="185" stroke="#4338ca" stroke-width="2" marker-end="url(#a3cm-arrow)"/>
  <text x="325" y="175" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">U → D</text>
  <text x="325" y="202" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">FundosReservados</text>
  <!-- shared kernel -->
  <rect x="290" y="238" width="180" height="34" rx="8" fill="#fff" stroke="#888" stroke-width="1.5" stroke-dasharray="3 3"/>
  <text x="380" y="259" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">shared kernel: "moeda / valor"</text>
  <line x1="330" y1="238" x2="230" y2="225" stroke="#888" stroke-width="1.2" stroke-dasharray="3 3"/>
  <line x1="430" y1="238" x2="460" y2="225" stroke="#888" stroke-width="1.2" stroke-dasharray="3 3"/>
  <!-- Antifraude (right) -->
  <rect x="650" y="145" width="230" height="80" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="765" y="172" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d">Antifraude e Limites</text>
  <text x="765" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#a05252">modelos de risco próprios</text>
  <text x="765" y="210" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#a05252">downstream do Ledger</text>
  <line x1="580" y1="185" x2="650" y2="185" stroke="#4338ca" stroke-width="2" marker-end="url(#a3cm-arrow)"/>
  <text x="615" y="175" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">U → D</text>
  <!-- Pagamentos <-> Antifraude sync (curved) -->
  <path d="M 175 145 Q 470 90 765 145" fill="none" stroke="#b91c1c" stroke-width="2"/>
  <text x="470" y="105" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">↔ síncrono no fluxo (LimitesValidados)</text>
  <!-- Cartões conformista -->
  <rect x="650" y="250" width="230" height="56" rx="10" fill="#f5f5f4" stroke="#57534e" stroke-width="2"/>
  <text x="765" y="274" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#44403c">Cartões</text>
  <text x="765" y="292" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">conformista: aceita o modelo do Ledger</text>
  <line x1="580" y1="215" x2="650" y2="262" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a3cm-gray)"/>
  <!-- Devoluções -->
  <rect x="60" y="250" width="230" height="56" rx="10" fill="#f5f5f4" stroke="#57534e" stroke-width="2"/>
  <text x="175" y="274" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#44403c">Devoluções e Disputas</text>
  <text x="175" y="292" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">MED · pacs.004 · reclamações</text>
  <line x1="175" y1="225" x2="175" y2="250" stroke="#888" stroke-width="1.5" marker-end="url(#a3cm-gray)"/>
  <!-- ACLs and external world -->
  <rect x="60" y="340" width="120" height="40" rx="8" fill="#fff" stroke="#4338ca" stroke-width="2" stroke-dasharray="5 3"/>
  <text x="120" y="365" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#4338ca">ACL</text>
  <line x1="140" y1="306" x2="125" y2="340" stroke="#888" stroke-width="1.5" marker-end="url(#a3cm-gray)"/>
  <line x1="175" y1="225" x2="120" y2="340" stroke="#888" stroke-width="0" />
  <rect x="210" y="340" width="120" height="40" rx="8" fill="#fff" stroke="#4338ca" stroke-width="2" stroke-dasharray="5 3"/>
  <text x="270" y="358" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#4338ca">ACL</text>
  <text x="270" y="374" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">pacs.008 → PixIniciado</text>
  <line x1="200" y1="225" x2="255 " y2="340" stroke="#888" stroke-width="1.5" marker-end="url(#a3cm-gray)"/>
  <!-- BACEN -->
  <rect x="390" y="400" width="360" height="44" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="570" y="419" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Mundo externo: BACEN — DICT · SPI (ISO 20022)</text>
  <text x="570" y="436" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#8a6d1a">linguagem que a TechPix NÃO controla — só entra traduzida pelo ACL</text>
  <line x1="180" y1="380" x2="390" y2="415" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>
  <line x1="330" y1="380" x2="395" y2="405" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O context map da TechPix: upstream/downstream, a conversa síncrona Pagamentos↔Antifraude, o conformista, o shared kernel — e os ACLs blindando o domínio da linguagem do BACEN.</p>
</div>

---

## 4. A fronteira de consistência, revisitada

Agora eu quero voltar numa ideia da Aula 1 e mostrar que ela sempre foi, secretamente, sobre bounded context.

Lá atrás, eu disse: "forte no núcleo, eventual na borda" — o ledger é consistente na hora, o extrato pode esperar. Hoje, com o vocabulário de DDD na mão, dá para dizer isso de um jeito mais preciso: **a fronteira de consistência transacional coincide com a fronteira do agregado — e, tipicamente, com a fronteira do bounded context central daquele agregado.** Dentro do agregado Ledger, tudo acontece dentro da mesma transação, protegido pela mesma invariante. Fora dele — quando Pagamentos quer avisar Antifraude, ou quando o extrato precisa ser atualizado —, a comunicação acontece por **evento de domínio**, de forma assíncrona, aceitando um atraso.

E isso explica uma coisa que talvez tenha incomodado vocês desde a Aula 2: por que o Outbox publica eventos **depois** da transação, de forma assíncrona, em vez de tudo acontecer junto? Porque tudo que precisava acontecer **junto**, na mesma transação, já aconteceu dentro do agregado. O que sai pelo Outbox é, por definição, informação que **pode** esperar — porque já cruzou a fronteira do contexto.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3ag-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <!-- Aggregate boundary -->
  <rect x="30" y="30" width="400" height="220" rx="14" fill="#f0fdf4" stroke="#166534" stroke-width="3"/>
  <text x="230" y="58" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">Agregado Ledger</text>
  <text x="230" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#3f7a52">fronteira de consistência FORTE — uma transação ACID</text>
  <rect x="60" y="95" width="160" height="50" rx="8" fill="#fff" stroke="#166534" stroke-width="1.5"/>
  <text x="140" y="116" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">lançamento (débito)</text>
  <text x="140" y="134" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">carteira_ana</text>
  <rect x="240" y="95" width="160" height="50" rx="8" fill="#fff" stroke="#166534" stroke-width="1.5"/>
  <text x="320" y="116" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">lançamento (crédito)</text>
  <text x="320" y="134" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">pix_a_liquidar</text>
  <rect x="60" y="165" width="340" height="40" rx="8" fill="#dcfce7" stroke="#166534" stroke-width="2"/>
  <text x="230" y="190" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">invariante: Σ débitos = Σ créditos · saldo ≥ 0</text>
  <text x="230" y="232" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3f7a52">tudo aqui dentro muda JUNTO, ou não muda</text>
  <!-- Outbox arrow -->
  <line x1="430" y1="140" x2="530" y2="140" stroke="#888" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#a3ag-arrow)"/>
  <text x="480" y="128" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">evento de domínio</text>
  <text x="480" y="158" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">(Outbox, Aula 2)</text>
  <!-- Outside -->
  <rect x="535" y="40" width="310" height="60" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text x="690" y="65" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#26215C">Extrato / saldo exibido / feed</text>
  <text x="690" y="85" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">eventual — atraso de 100–300 ms</text>
  <rect x="535" y="115" width="310" height="60" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text x="690" y="140" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">Antifraude (acumulado do dia)</text>
  <text x="690" y="160" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#a05252">eventual — janela de ms tolerada</text>
  <rect x="535" y="190" width="310" height="60" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text x="690" y="215" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Notificações</text>
  <text x="690" y="235" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#8a6d1a">eventual — pode esperar</text>
  <text x="440" y="282" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">"Forte no núcleo, eventual na borda" (Aula 1) = a fronteira transacional É a fronteira do agregado</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O que precisa acontecer junto mora dentro do agregado; o que pode esperar cruza a fronteira por evento.</p>
</div>

### 4.1 As quatro regras de design de agregado

Vaughn Vernon, que expandiu bastante o trabalho original do Eric Evans, formulou um conjunto de regras práticas para desenhar agregados. Eu vou dar as quatro que mais importam, porque elas transformam "agregado" de conceito vago em critério de decisão.

**Regra 1 — proteja invariantes de negócio dentro da fronteira.** O agregado existe para uma coisa: garantir que uma regra que envolve múltiplos dados nunca seja violada. Se a regra é "saldo nunca negativo", então tudo que é necessário para verificar essa regra — o saldo e o lançamento sendo aplicado — precisa estar dentro do mesmo agregado, na mesma transação. **A invariante define a fronteira**, não o contrário. Comecem sempre pela pergunta "que regra eu não posso violar nunca?" e a fronteira se desenha a partir dela.

**Regra 2 — projete agregados pequenos.** Essa é a regra que a maioria dos times viola, e é a mais caras de violar. Um agregado grande — digamos, "Cliente", contendo todas as contas, todos os cartões, todo o histórico — parece conveniente para navegar no código. Mas ele significa que **qualquer** alteração em **qualquer** parte dele trava o agregado inteiro. Dois usos completamente independentes passam a competir pelo mesmo lock. Guardem: agregado grande é contenção disfarçada de conveniência.

**Regra 3 — referencie outros agregados por identidade, não por objeto.** Se o agregado de Pagamento precisa saber de qual conta o dinheiro sai, ele guarda o **identificador** da conta, não uma referência ao objeto Conta inteiro. Isso parece detalhe de implementação, mas é a regra que impede o agregado de crescer sem controle — porque, sem ela, "carregar um Pagamento" acaba carregando meio banco de dados, e mais grave: acaba permitindo que alguém modifique dois agregados na mesma transação sem perceber.

**Regra 4 — fora da fronteira, use consistência eventual.** Se uma operação precisa alterar dois agregados, a resposta correta quase nunca é "coloque os dois na mesma transação". A resposta é: altere um, emita um evento de domínio, e deixe o outro reagir. Isso é, literalmente, o Outbox da Aula 2 — só que agora vocês entendem que ele não é um truque de infraestrutura, é a **consequência direta** de ter desenhado agregados pequenos.

### 4.2 A matemática da contenção: quanto custa, em transações por segundo, um agregado grande

Até aqui, "agregado grande é ruim" foi uma afirmação de gosto. Eu quero transformar isso em número, porque é assim que a gente decide as coisas neste curso — e porque a conta é curta o suficiente para vocês fazerem no guardanapo, na reunião, antes de a decisão virar migração de dados.

Comecem por uma tradução: **um agregado é, na prática de execução, um lock.** Enquanto uma transação segura a fronteira do agregado, nenhuma outra transação que toque o mesmo agregado avança — ela espera na fila. Disso sai a fórmula mais simples e mais ignorada de System Design de dados:

> **vazão máxima de um agregado = 1 ÷ tempo em que o lock fica segurado**

Só isso. Se o lock fica segurado por 4 milissegundos, aquele agregado sustenta, no limite teórico, 250 transações por segundo. Não 251. E — esta é a parte que costuma incomodar a sala, no bom sentido — **esse número não muda se vocês trocarem a máquina.** Dobrar a CPU não dobra o teto; ele é fixado pela duração do trecho serializado, não pela capacidade da máquina.

Vamos aplicar isso à conta de liquidação `pix_a_liquidar` da TechPix, com os números que a gente já carrega desde a Aula 1: o pico da TechPix é de **~900 transações por segundo**, e cada uma delas toca a conta de liquidação — ou seja, as 900 disputam a mesma fronteira. No dia 5, com o tráfego triplicado, foram **~2.700** disputando.

| O que fica dentro da seção crítica | Tempo de lock | Teto teórico | Cabe os 900 TPS do pico? |
|---|---|---|---|
| Transação inteira, **com a consulta síncrona ao DICT dentro** (p99 do DICT ≈ 1 s) | ~1.000 ms | **~1 tx/s** | catastrófico |
| Transação inteira do jeito da Aula 1 (50 ms da ponta à ponta) | 50 ms | **20 tx/s** | não — falta 45× |
| Só validação + escrita + commit, sem I/O externo | 8 ms | **125 tx/s** | não — falta 7× |
| Só escrita + commit, com a validação feita antes de abrir a transação | 4 ms | **250 tx/s** | não — falta 3,6× |
| O mesmo, com a conta quente dividida em **20 baldes** (Aula 2) | 4 ms | **5.000 tx/s** | sim, com folga real |

Três leituras dessa tabela, e cada uma vale um pedaço da aula:

**Primeira: a coluna da esquerda não tem nada de banco de dados.** Ela tem *o que vocês decidiram colocar dentro da fronteira*. O teto de vazão da TechPix foi definido numa reunião de modelagem, meses antes de alguém abrir o `EXPLAIN ANALYZE`.

**Segunda: a primeira linha é o erro mais caro desta aula inteira.** Uma chamada de rede dentro da fronteira do agregado multiplica o tempo de lock pelo **p99 do mundo externo** — e o p99, não a média, porque é a cauda que decide a fila. Uma dependência externa com p99 de 1 segundo, chamada de dentro da transação, derruba o teto de 250 para 1. Guardem a regra na forma mais dura possível: **nunca segure um lock de domínio enquanto espera a rede.** Resolva a chave antes, valide o limite antes, e só então abra a transação que toca o ledger.

**Terceira: nem 250 tx/s são 250 tx/s.** A curva de filas da Aula 2 cobra sua parte: a partir de ~70–80% de utilização, o tempo de espera explode. O teto *utilizável* de um agregado com lock de 4 ms não é 250 — é algo perto de **175 tx/s** antes de a latência começar a subir de forma visível para a Ana. Sempre dimensionem contra o teto utilizável, nunca contra o teórico.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 960 486" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3ag2-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#7c3aed"/>
    </marker>
  </defs>
  <text x="480" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">O mesmo trabalho, duas fronteiras — e dois tetos de vazão</text>

  <!-- ===== ESQUERDA ===== -->
  <rect x="16" y="40" width="452" height="392" rx="12" fill="#fff7f7" stroke="#b91c1c" stroke-width="2"/>
  <text x="242" y="64" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d">Agregado grande: "Cliente"</text>
  <text x="242" y="81" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#a05252">tudo do cliente atrás de uma fronteira só</text>

  <rect x="36" y="92" width="412" height="112" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2.5"/>
  <g font-family="sans-serif" font-size="10.5" fill="#7f1d1d">
    <rect x="50" y="106" width="124" height="40" rx="6" fill="#fff" stroke="#b91c1c" stroke-width="1.2"/><text x="112" y="130" text-anchor="middle">identidade</text>
    <rect x="182" y="106" width="124" height="40" rx="6" fill="#fff" stroke="#b91c1c" stroke-width="1.2"/><text x="244" y="130" text-anchor="middle">carteira pessoal</text>
    <rect x="314" y="106" width="124" height="40" rx="6" fill="#fff" stroke="#b91c1c" stroke-width="1.2"/><text x="376" y="130" text-anchor="middle">carteira negócio</text>
    <rect x="50" y="152" width="124" height="40" rx="6" fill="#fff" stroke="#b91c1c" stroke-width="1.2"/><text x="112" y="176" text-anchor="middle">cartões</text>
    <rect x="182" y="152" width="124" height="40" rx="6" fill="#fff" stroke="#b91c1c" stroke-width="1.2"/><text x="244" y="176" text-anchor="middle">limite diário</text>
    <rect x="314" y="152" width="124" height="40" rx="6" fill="#fff" stroke="#b91c1c" stroke-width="1.2"/><text x="376" y="176" text-anchor="middle">histórico</text>
  </g>
  <text x="242" y="224" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">1 fronteira = 1 lock</text>

  <text x="36" y="252" font-family="sans-serif" font-size="11" fill="#666">5 operações independentes chegam juntas → uma fila só:</text>
  <rect x="36" y="262" width="412" height="30" rx="4" fill="#fff" stroke="#a8a29e"/>
  <g font-family="sans-serif" font-size="10" fill="#fff" text-anchor="middle">
    <rect x="38" y="264" width="80" height="26" fill="#b91c1c"/><text x="78" y="281">pagar</text>
    <rect x="120" y="264" width="80" height="26" fill="#b91c1c"/><text x="160" y="281">cartão</text>
    <rect x="202" y="264" width="80" height="26" fill="#b91c1c"/><text x="242" y="281">receber</text>
    <rect x="284" y="264" width="80" height="26" fill="#b91c1c"/><text x="324" y="281">ajuste</text>
    <rect x="366" y="264" width="80" height="26" fill="#b91c1c"/><text x="406" y="281">tarifa</text>
  </g>
  <text x="242" y="308" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#666">tempo →  cada uma espera a anterior, mesmo sem relação nenhuma entre elas</text>

  <rect x="36" y="322" width="412" height="94" rx="9" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="242" y="345" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">lock de 4 ms → teto = 1 ÷ 0,004 = 250 tx/s</text>
  <text x="242" y="364" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#991b1b">e esses 250 são divididos entre TODOS os usos do cliente</text>
  <text x="242" y="383" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#991b1b">teto utilizável (ρ ≈ 0,7): ~175 tx/s</text>
  <text x="242" y="404" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#b91c1c">✅ invariantes fáceis · ❌ contenção disfarçada de conveniência</text>

  <!-- ===== DIREITA ===== -->
  <rect x="492" y="40" width="452" height="392" rx="12" fill="#f7fdf9" stroke="#166534" stroke-width="2"/>
  <text x="718" y="64" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">Agregados pequenos</text>
  <text x="718" y="81" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3f7a52">uma fronteira por invariante que precisa ser protegida</text>

  <g font-family="sans-serif">
    <rect x="510" y="92" width="132" height="66" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
    <text x="576" y="118" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Conta</text>
    <text x="576" y="136" text-anchor="middle" font-size="9.5" fill="#3f7a52">saldo ≥ 0</text>
    <rect x="652" y="92" width="132" height="66" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
    <text x="718" y="118" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Cartão</text>
    <text x="718" y="136" text-anchor="middle" font-size="9.5" fill="#3f7a52">limite do cartão</text>
    <rect x="794" y="92" width="132" height="66" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
    <text x="860" y="118" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">LimiteDiário</text>
    <text x="860" y="136" text-anchor="middle" font-size="9.5" fill="#3f7a52">acumulado do dia</text>
  </g>
  <path d="M 576 158 Q 647 196 718 158" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#a3ag2-arrow)"/>
  <path d="M 718 158 Q 789 196 860 158" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#a3ag2-arrow)"/>
  <text x="718" y="212" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c3aed">entre eles: evento de domínio (Outbox) — consistência eventual</text>

  <text x="512" y="252" font-family="sans-serif" font-size="11" fill="#666">as mesmas 5 operações → três filas independentes:</text>
  <g font-family="sans-serif" font-size="10" fill="#fff" text-anchor="middle">
    <rect x="512" y="260" width="414" height="18" rx="3" fill="#fff" stroke="#a8a29e"/>
    <rect x="514" y="261" width="100" height="16" fill="#166534"/><text x="564" y="273">pagar</text>
    <rect x="616" y="261" width="100" height="16" fill="#166534"/><text x="666" y="273">receber</text>
    <rect x="512" y="282" width="414" height="18" rx="3" fill="#fff" stroke="#a8a29e"/>
    <rect x="514" y="283" width="100" height="16" fill="#166534"/><text x="564" y="295">cartão</text>
    <rect x="512" y="304" width="414" height="18" rx="3" fill="#fff" stroke="#a8a29e"/>
    <rect x="514" y="305" width="100" height="16" fill="#166534"/><text x="564" y="317">ajuste</text>
    <rect x="616" y="305" width="100" height="16" fill="#166534"/><text x="666" y="317">tarifa</text>
  </g>
  <text x="718" y="338" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#666">tempo →  quem não compartilha invariante não compartilha fila</text>

  <rect x="510" y="348" width="416" height="68" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="718" y="371" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">3 fronteiras → teto = 3 × 250 = 750 tx/s</text>
  <text x="718" y="390" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#3f7a52">(e a conta quente sub-particionada em 20 baldes: 5.000 tx/s)</text>
  <text x="718" y="409" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#166534">✅ escala · ❌ estados intermediários para raciocinar</text>

  <text x="480" y="456" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#333">O teto de vazão do sistema foi decidido na reunião de modelagem, não na escolha do banco.</text>
  <text x="480" y="476" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#666">Pico da TechPix: ~900 tx/s · dia 5: ~2.700 tx/s — só a coluna da direita chega lá.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Agregado grande × agregados pequenos: o mesmo trabalho, a mesma máquina, tetos de vazão que diferem por uma ordem de grandeza.</p>
</div>

E vale conectar com a Lei de Amdahl, que apareceu na Aula 2: aquela conta dizia que o ganho de paralelizar é limitado pela fração que **não** paraleliza. Agora vocês têm o nome de domínio dessa fração: **ela é o agregado**. Toda vez que alguém colocar mais uma coisa dentro da fronteira "porque fica mais fácil de garantir", essa fração serial cresce — e o teto do sistema inteiro cai junto, mesmo que nenhuma linha de infraestrutura tenha mudado.

E reparem que a TechPix **ainda não fez** esse conserto: a conta `pix_a_liquidar` continua única, e a linha de revisão do ADR-002 — “se a contenção persistir, reparticionar a própria escrita do ledger” — segue aberta. O que esta seção acrescenta é a **conta que justifica** essa decisão quando ela for tomada, e o vocabulário para nomeá-la: não é “otimizar o banco”, é redesenhar a fronteira de um agregado.

### 4.3 O trade-off que conecta esta aula à Aula 2

Aqui está, para mim, o insight mais valioso das três aulas juntas — e eu quero que vocês parem para absorver, porque ele amarra tudo.

Reparem no que acabou de acontecer: as regras 2 e 4 estão em **tensão direta** uma com a outra.

- **Agregado grande:** mais coisas protegidas transacionalmente, mais fácil de garantir invariantes complexas — mas **mais contenção**, porque tudo compete pelo mesmo lock.
- **Agregado pequeno:** menos contenção, escala muito melhor — mas **mais consistência eventual** para gerenciar, mais eventos, mais compensação, mais complexidade de raciocínio sobre estados intermediários.

E agora conectem com a Aula 2: **o ponto quente do ledger, que derrubou a TechPix no dia 5, era um problema de agregado grande demais.** A conta de liquidação `pix_a_liquidar` estava, efetivamente, dentro da fronteira transacional de todas as transações do sistema ao mesmo tempo. Não era um problema de banco de dados; era um problema de **modelagem de domínio** que se manifestou como problema de banco de dados.

Deixem isso decantar, porque a implicação é forte: quando a gente falou de "reparticionar a escrita do ledger" na Aula 2, a gente estava falando, em vocabulário de DDD, de **redesenhar a fronteira do agregado**. O `hash(conta_id) mod N` da Aula 1 e a decisão de "que dados vivem dentro deste agregado" são a mesma decisão, vista de dois ângulos — um de infraestrutura, um de domínio.

E é por isso que eu insisto que essas três aulas são uma só: a contenção que vocês medem em produção é, na maioria das vezes, uma fronteira de domínio mal desenhada cobrando o preço.

### 4.4 O problema do agregado grande na prática do Pix

Vamos aterrissar isso na TechPix com um exemplo concreto e discutível — do tipo que dá boa discussão em sala.

Pergunta: **o limite diário de transferência do cliente pertence ao agregado da Conta?**

O argumento a favor: o limite é uma invariante — "a soma das transferências do dia não pode passar de X" — e invariante define fronteira, pela Regra 1. Colocar dentro é o instinto correto.

O argumento contra: se o limite diário vive dentro do agregado Conta, então **toda** transferência precisa travar o agregado Conta para verificar e atualizar o acumulado do dia. Numa conta de alto volume — o marketplace da Aula 2 — isso serializa todas as transferências daquele cliente. Vocês acabaram de criar um ponto quente por decisão de modelagem.

E a resposta honesta é: **depende do rigor exigido.** Se o limite precisa ser garantido com precisão absoluta, sem nunca ultrapassar nem por um centavo, ele tem que estar dentro da fronteira, e vocês pagam a contenção. Se um pequeno excesso momentâneo é tolerável — e para limite de antifraude, frequentemente é, porque a defesa não depende de precisão ao centavo — vocês podem manter o acumulado **fora** do agregado, atualizado por evento, aceitando uma janela de imprecisão de milissegundos em troca de escala.

Reparem que essa é uma decisão de **negócio**, não de engenharia. E é exatamente o tipo de decisão que merece um ADR, porque a escolha errada aqui só aparece em produção, num dia 5.

### 4.5 Como a fronteira do agregado vira código, transação e esquema de banco

Fronteira que só existe no diagrama não protege ninguém. Deixa eu mostrar as três formas concretas em que ela aparece — e as três são verificáveis.

**Primeira: a regra operacional que resume tudo — uma transação, um agregado.** Se uma operação precisa abrir uma transação que altera dois agregados, ou a fronteira está errada, ou a operação está errada. Não há terceira hipótese. Essa regra é o que transforma a Regra 4 do Vernon de conselho em disciplina executável, e é a checagem mais rápida que existe numa revisão de código: *quantos agregados esta transação escreve?*

**Segunda: referência por identidade, no código.** A Regra 3 parece detalhe de estilo até vocês verem o que ela impede:

```python
# ❌ referência por objeto — o agregado cresce sem ninguém decidir que ele deveria crescer
class Pagamento:
    conta_origem: Conta            # o agregado Conta inteiro, carregado junto

    def executar(self):
        self.conta_origem.debitar(self.valor)   # ⚠️ alterando OUTRO agregado aqui dentro
        self.status = "EXECUTADO"               # …e este, na mesma transação

# ✅ referência por identidade — a fronteira fica visível a olho nu
class Pagamento:
    conta_origem_id: ContaId       # só o identificador atravessa a fronteira

    def executar(self):
        self.status = "AGUARDANDO_RESERVA"
        self.eventos.append(ReservaSolicitada(self.id, self.conta_origem_id, self.valor))
        # o débito acontece no agregado Conta, em outra transação, reagindo ao evento
```

Na versão de cima, ninguém **decidiu** juntar `Pagamento` e `Conta` no mesmo agregado — o campo tipado fez isso sozinho, e a contenção da Seção 4.2 entrou de carona. Na versão de baixo, atravessar a fronteira exige escrever um evento, o que é justamente trabalho suficiente para alguém parar e perguntar se é mesmo necessário. **Boa fronteira é aquela que cobra um pequeno pedágio para ser atravessada.**

**Terceira: a invariante dentro do próprio `WHERE`.** No banco, a fronteira do agregado vira controle de concorrência — e o jeito mais barato de expressá-la é o bloqueio otimista, com a regra de negócio embutida na condição:

```sql
UPDATE ledger.conta
   SET saldo  = saldo - :valor,
       versao = versao + 1
 WHERE id      = :conta_id
   AND versao  = :versao_lida     -- ninguém mexeu desde que eu li (bloqueio otimista)
   AND saldo  >= :valor;          -- a invariante, verificada pelo próprio banco

-- 0 linhas afetadas = conflito de concorrência OU saldo insuficiente
--                     → aborta a transação, não "corrige" nada
```

Duas coisas boas acontecem aqui. A primeira é que o banco vira o guardião da invariante, e não a boa vontade do código de aplicação. A segunda é que **a taxa de "0 linhas afetadas" vira uma métrica de contenção** — a mesma que a Seção 4.2 calculou no papel, agora medida em produção. Se essa taxa sobe junto com o volume, o agregado está grande demais, e vocês souberam **antes** do incidente. Anotem essa métrica; ela é o sinal mais barato de agregado mal desenhado que existe.

**E a fronteira do contexto, no banco: um esquema por contexto, sem chave estrangeira atravessando.** Num monólito modular — que é onde a TechPix está hoje —, os contextos convivem no mesmo Postgres, mas cada um com seu **schema**:

```sql
-- cada contexto é dono do seu esquema; ninguém escreve no esquema alheio
CREATE SCHEMA ledger;       CREATE SCHEMA pagamentos;
CREATE SCHEMA antifraude;   CREATE SCHEMA identidade;

-- ✅ dentro do contexto: integridade referencial normal
ALTER TABLE ledger.lancamento
  ADD CONSTRAINT fk_conta FOREIGN KEY (conta_id) REFERENCES ledger.conta(id);

-- ❌ atravessando o contexto: proibido, mesmo sendo tecnicamente possível
-- ALTER TABLE pagamentos.pagamento
--   ADD CONSTRAINT fk_conta FOREIGN KEY (conta_id) REFERENCES ledger.conta(id);
```

Essa última linha comentada é a mais importante das quatro. **A ausência daquela chave estrangeira é a fronteira.** Quando `pagamentos.pagamento` guarda um `conta_id` sem constraint, vocês estão dizendo, no esquema: "isto aqui é uma referência a outro contexto, cuja consistência é eventual, e cuja integridade é responsabilidade do dono de lá". Colocar a chave estrangeira parece um ganho de rigor gratuito — e é, na verdade, três coisas ruins de uma vez: acopla o ciclo de deploy dos dois contextos, impede que um deles seja extraído para banco próprio no dia em que a Aula 6 chegar, e transforma toda escrita de um contexto num lock que o outro sente.

Guardem a formulação, porque ela é contraintuitiva e verdadeira: **em modelagem de contexto, a chave estrangeira que vocês não criam vale mais que as que vocês criam.**

### 4.6 Quanto de estado o evento carrega? A decisão que ninguém percebe estar tomando

Antes de falar de versionar evento, tem uma decisão anterior — e mais consequente — que a maioria dos times toma por acidente, no primeiro evento que publica: **quanto de informação o evento leva junto?**

Existem dois extremos, e os dois têm nome.

O **evento-notificação** (o "evento magro") carrega quase nada — um identificador e pouco mais:

```json
{ "tipo": "PixLiquidado", "e2e_id": "E12345678202608221200abcdef012345" }
```

É econômico e o contrato é minúsculo. O problema é que **todo consumidor precisa ligar de volta** para saber o que aconteceu — e aí vocês compraram três coisas ruins: carga extra no contexto que publicou (exatamente aquele que já era o gargalo), acoplamento em tempo de execução (se o Ledger estiver fora do ar, nenhum consumidor consegue processar nada), e — o pior — **a resposta que volta é o estado de agora, não o do instante do fato.** Se o consumidor processa o evento três segundos depois, ele consulta e recebe um saldo que já mudou. O evento diz "isto aconteceu"; a consulta responde "isto é verdade agora". São coisas diferentes, e confundi-las produz bugs de reconciliação que ninguém consegue reproduzir.

O **evento de transferência de estado** (o "evento gordo", ou *event-carried state transfer*) carrega o que o consumidor precisa para decidir sozinho:

```json
{
  "tipo": "PixLiquidado",
  "versao": 2,
  "e2e_id": "E12345678202608221200abcdef012345",
  "ocorrido_em": "2026-08-22T12:00:03.412Z",
  "conta_debitada_id": "ct_8f21…",
  "valor": { "moeda": "BRL", "centavos": 10000 },
  "saldo_apos_centavos": 4230011,
  "canal": "PIX_CHAVE"
}
```

Agora o consumidor é autônomo: o Antifraude atualiza o acumulado do dia sem falar com o Ledger, e o extrato se materializa sem consultar ninguém. O custo é que o contrato ficou maior — e contrato maior é superfície maior para quebrar, que é exatamente o assunto da próxima seção.

| | Evento magro (notificação) | Evento gordo (transferência de estado) |
|---|---|---|
| Contrato | mínimo, quase nunca muda | maior, versiona com mais frequência |
| Acoplamento em runtime | **alto** — consumidor liga de volta | **baixo** — consumidor decide sozinho |
| Carga no publicador | cresce com o nº de consumidores | constante |
| Fidelidade temporal | ruim — lê o estado de agora | **boa** — carrega o estado do instante do fato |
| Dado sensível | fica onde está | **atravessa a fronteira** — cuidado com LGPD |

A recomendação para fintech, e ela é bem direta: **evento gordo, com o valor do instante do fato, e o mínimo de dado pessoal possível.** Carreguem identificadores e valores monetários; não carreguem CPF, nome, endereço ou qualquer coisa que vocês não gostariam de ver retida por anos em cinco tópicos diferentes — porque, num sistema com retenção de auditoria, um campo sensível publicado uma vez fica publicado para sempre, em todo lugar que consumiu. A Aula 7 volta nesse assunto pelo lado do log; a regra é a mesma, e vale já no primeiro evento.

### 4.7 Versionamento de eventos: o problema que aparece no mês seis

Uma última coisa nesta seção, e é a que mais gente esquece de planejar: **eventos de domínio publicados são contratos públicos.** No momento em que o Outbox publica `PixLiquidado` e três serviços passam a consumir esse evento, o formato dele deixou de ser detalhe interno de Pagamentos — virou uma interface com três clientes.

E então, no mês seis, vocês precisam adicionar um campo. Ou pior: renomear um. O que acontece com os consumidores que ainda esperam o formato antigo? E com os eventos **antigos**, que estão retidos no broker e podem ser reprocessados, no formato velho?

As estratégias reais, com trade-off:

- **Só adicione, nunca remova nem renomeie** (compatibilidade retroativa). É a regra mais simples e a mais defensável: campos novos são opcionais, campos velhos permanecem para sempre, mesmo depois de virarem inúteis. O custo é acúmulo de lixo no schema ao longo dos anos.
- **Versione o tipo do evento** — `PixLiquidado.v2` conviva com `PixLiquidado.v1` — e mantenha os dois publicados durante uma janela de migração, até todos os consumidores migrarem. Mais trabalho, mas honesto e explícito.
- **Registro de schema** (o *schema registry*, como o do ecossistema Kafka): um serviço central que valida, no momento da publicação, se o novo formato é compatível com o anterior, e **rejeita** publicação incompatível. Isso transforma "acordo de cavalheiros" em checagem automática — reparem que é a mesma ideia da fitness function da Aula 2, aplicada a contrato de evento.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 960 452" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3ev-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#666"/>
    </marker>
    <marker id="a3ev-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <text x="480" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Três estratégias para evoluir um contrato de evento — e o que cada uma custa</text>

  <!-- ===== 1. só adicionar ===== -->
  <rect x="16" y="40" width="300" height="300" rx="11" fill="#f7fdf9" stroke="#166534" stroke-width="2"/>
  <text x="166" y="64" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">1. Só adicionar</text>
  <text x="166" y="81" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#3f7a52">campo novo é opcional · nada some, nada é renomeado</text>

  <rect x="36" y="94" width="120" height="86" rx="6" fill="#fff" stroke="#a8a29e" stroke-width="1.5"/>
  <text x="96" y="112" text-anchor="middle" font-family="monospace" font-size="10" fill="#555">PixLiquidado</text>
  <text x="48" y="132" font-family="monospace" font-size="9.5" fill="#555">e2e_id</text>
  <text x="48" y="148" font-family="monospace" font-size="9.5" fill="#555">valor</text>
  <text x="48" y="164" font-family="monospace" font-size="9.5" fill="#555">ocorrido_em</text>

  <line x1="156" y1="137" x2="180" y2="137" stroke="#666" stroke-width="2" marker-end="url(#a3ev-arrow)"/>

  <rect x="184" y="94" width="120" height="86" rx="6" fill="#fff" stroke="#166534" stroke-width="2"/>
  <text x="244" y="112" text-anchor="middle" font-family="monospace" font-size="10" fill="#555">PixLiquidado</text>
  <text x="196" y="132" font-family="monospace" font-size="9.5" fill="#555">e2e_id</text>
  <text x="196" y="148" font-family="monospace" font-size="9.5" fill="#555">valor</text>
  <text x="196" y="164" font-family="monospace" font-size="9.5" fill="#555">ocorrido_em</text>
  <text x="196" y="176" font-family="monospace" font-size="9.5" font-weight="bold" fill="#166534">+ canal (opc.)</text>

  <rect x="36" y="196" width="268" height="46" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="170" y="214" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#166534">consumidor antigo simplesmente ignora</text>
  <text x="170" y="230" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#166534">o campo que ele não conhece → nada quebra</text>

  <rect x="36" y="252" width="268" height="72" rx="7" fill="#fff" stroke="#d4a017" stroke-width="1.5"/>
  <text x="170" y="271" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7a5c00">custo</text>
  <text x="170" y="290" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#8a6d1a">campos inúteis ficam para sempre;</text>
  <text x="170" y="306" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#8a6d1a">em 5 anos o schema vira um sótão</text>

  <!-- ===== 2. versionar o tipo ===== -->
  <rect x="332" y="40" width="300" height="300" rx="11" fill="#f8f8ff" stroke="#4338ca" stroke-width="2"/>
  <text x="482" y="64" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#26215C">2. Versionar o tipo</text>
  <text x="482" y="81" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#5a55a0">v1 e v2 convivem durante uma janela de migração</text>

  <line x1="356" y1="180" x2="612" y2="180" stroke="#999" stroke-width="1.5"/>
  <text x="356" y="198" font-family="sans-serif" font-size="9.5" fill="#888">tempo →</text>

  <rect x="356" y="104" width="150" height="26" rx="4" fill="#e0e7ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="431" y="122" text-anchor="middle" font-family="monospace" font-size="10" fill="#26215C">PixLiquidado.v1</text>
  <rect x="430" y="136" width="182" height="26" rx="4" fill="#c7d2fe" stroke="#4338ca" stroke-width="1.5"/>
  <text x="521" y="154" text-anchor="middle" font-family="monospace" font-size="10" fill="#26215C">PixLiquidado.v2</text>

  <rect x="430" y="164" width="76" height="12" fill="#4338ca" opacity="0.18"/>
  <text x="440" y="212" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#4338ca">janela em que</text>
  <text x="440" y="224" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#4338ca">os dois são publicados</text>

  <text x="592" y="212" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#166534">v1 retirada quando</text>
  <text x="592" y="224" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#166534">o último consumidor migra</text>

  <rect x="352" y="240" width="264" height="84" rx="7" fill="#fff" stroke="#d4a017" stroke-width="1.5"/>
  <text x="484" y="259" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7a5c00">custo</text>
  <text x="484" y="278" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#8a6d1a">publicar duas vezes, e — o difícil —</text>
  <text x="484" y="294" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#8a6d1a"><tspan font-weight="bold">saber quem são seus consumidores</tspan></text>
  <text x="484" y="312" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#8a6d1a">para poder desligar a v1 um dia</text>

  <!-- ===== 3. schema registry ===== -->
  <rect x="648" y="40" width="300" height="300" rx="11" fill="#fff7f7" stroke="#b91c1c" stroke-width="2"/>
  <text x="798" y="64" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d">3. Registro de schema</text>
  <text x="798" y="81" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#a05252">a compatibilidade deixa de ser acordo de cavalheiros</text>

  <rect x="666" y="100" width="96" height="44" rx="7" fill="#fff" stroke="#57534e" stroke-width="1.5"/>
  <text x="714" y="120" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#44403c">produtor</text>
  <text x="714" y="135" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#78716c">publica v2</text>

  <line x1="762" y1="122" x2="786" y2="122" stroke="#666" stroke-width="2" marker-end="url(#a3ev-arrow)"/>

  <rect x="790" y="94" width="140" height="56" rx="7" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="860" y="115" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7a5c00">registry</text>
  <text x="860" y="132" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#8a6d1a">v2 é compatível com v1?</text>
  <text x="860" y="145" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#8a6d1a">(checa na publicação)</text>

  <line x1="860" y1="150" x2="860" y2="176" stroke="#166534" stroke-width="2" marker-end="url(#a3ev-arrow)"/>
  <rect x="792" y="180" width="136" height="34" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="860" y="202" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#166534">✔ compatível → publica</text>

  <line x1="790" y1="122" x2="756" y2="176" stroke="#b91c1c" stroke-width="2" marker-end="url(#a3ev-red)"/>
  <rect x="664" y="180" width="120" height="34" rx="6" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="724" y="202" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#b91c1c">✘ rejeita a publicação</text>

  <rect x="666" y="230" width="264" height="94" rx="7" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="798" y="249" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#26215C">o que isto realmente é</text>
  <text x="798" y="268" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#5a55a0">a fitness function da Aula 2,</text>
  <text x="798" y="284" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#5a55a0">aplicada a contrato de evento —</text>
  <text x="798" y="300" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#5a55a0">a fronteira vira checagem automática,</text>
  <text x="798" y="316" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#5a55a0">e não confiança na revisão de código</text>

  <!-- faixa inferior -->
  <rect x="16" y="356" width="932" height="80" rx="10" fill="#fff" stroke="#57534e" stroke-width="1.5"/>
  <text x="482" y="378" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">As três não são alternativas: são camadas. Adicione sempre que der; versione quando não der; e deixe o registry impedir o resto.</text>
  <text x="482" y="400" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#666">Em fintech, com retenção de anos por auditoria, um quarto item é obrigatório: <tspan font-weight="bold" fill="#b91c1c">saber ler o evento antigo para sempre</tspan></text>
  <text x="482" y="422" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#666">— seja mantendo o leitor da v1 vivo, seja convertendo v1 → v2 na leitura (<tspan font-style="italic">upcasting</tspan>).</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Evoluir contrato de evento em camadas: adicionar, versionar, e impedir automaticamente o que não é compatível.</p>
</div>

**E "compatível" tem mais de um significado — que é onde quase todo mundo tropeça.** Um registro de schema não pergunta apenas "mudou?"; ele pergunta "mudou **em que direção**?". Vale conhecer os três modos, porque escolher o errado dá uma falsa sensação de segurança:

| Modo | O que ele garante | Quando vocês precisam dele |
|---|---|---|
| **BACKWARD** | O consumidor **novo** consegue ler os eventos **antigos** | Sempre que houver reprocessamento de histórico — ou seja, sempre, em fintech |
| **FORWARD** | O consumidor **antigo** consegue ler os eventos **novos** | Durante deploy gradual: o produtor sobe antes de todos os consumidores |
| **FULL** | As duas coisas ao mesmo tempo | O padrão sensato para evento financeiro publicado a terceiros |

Repare que os dois primeiros resolvem problemas diferentes, e o segundo é o esquecido: se vocês fazem canary release — e a Aula 6 vai fazer — vai existir, por alguns minutos, um produtor novo publicando para consumidores velhos. Sem compatibilidade **forward**, esses minutos são um incidente.

**E o histórico, que é o problema que fintech tem e outros setores não.** Um evento gravado em 2026 vai precisar ser lido em 2031, por um código que ninguém escreveu ainda. Duas saídas, e a segunda é a que envelhece melhor:

```python
# upcasting: o evento antigo é convertido na LEITURA, e o resto do sistema só conhece a v2
def upcast(evento: dict) -> dict:
    if evento["tipo"] == "PixLiquidado" and evento.get("versao", 1) == 1:
        evento = {**evento,
                  "versao": 2,
                  "canal": "PIX_CHAVE",              # default explícito para o que a v1 não tinha
                  "valor": {"moeda": "BRL",           # v1 guardava só o inteiro em centavos
                            "centavos": evento["valor_centavos"]}}
        evento.pop("valor_centavos", None)
    return evento
```

A primeira saída — manter o leitor da v1 vivo para sempre — funciona, e o custo é código morto que precisa continuar correto por anos. A segunda — o *upcasting* acima — concentra o conhecimento do passado num lugar só, e é o que sistemas maduros de event sourcing fazem. Em ambos os casos, o que **não** funciona é migrar os eventos já gravados: evento é fato histórico, e reescrever fato histórico num sistema financeiro é, em vários sentidos, exatamente o que a auditoria existe para impedir.

Uma nota de fronteira entre aulas, para não estragar a surpresa da próxima: aqui a gente tratou o versionamento como **consequência da modelagem** — o evento virou contrato porque cruzou uma fronteira de contexto. A mecânica de fazer uma mudança quebra-contrato entrar em produção sem parar ninguém — o *expand/contract*, os contratos dirigidos pelo consumidor — é assunto da Aula 4, que trata cada aresta desse mapa como uma decisão própria.

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

### 5.1 O Spec Kit: o fluxo do SDD com ferramenta de verdade

Na Aula 1 eu citei o **GitHub Spec Kit** de passagem, como uma das ferramentas que materializam o SDD. Hoje eu quero abrir ele de verdade, porque a spec que a gente acabou de escrever no quadro não vai viver num slide — ela vai viver num repositório, num formato que um agente de IA consegue ler, verificar e implementar. O Spec Kit é um kit de código aberto, do próprio GitHub, que estrutura exatamente o fluxo que eu descrevi lá atrás — especificação, plano, tarefas, implementação — como comandos que vocês rodam **dentro do próprio agente de código**: Claude Code, GitHub Copilot, Gemini CLI, Cursor — a lista passa de trinta integrações.

A instalação é uma linha — a ferramenta `specify` (via `uv tool install specify-cli`), e depois `specify init techpix --integration claude` para preparar o repositório. O que ela cria é mais interessante do que o que ela instala:

```
techpix/
├── .specify/
│   └── memory/
│       └── constitution.md      ← o núcleo duro: o que NENHUMA feature pode violar
├── specs/
│   └── 001-iniciacao-pagamento/ ← um diretório por feature
│       ├── spec.md              ← o QUÊ (requisitos, histórias, critérios de aceite)
│       ├── plan.md              ← o COMO (stack, arquitetura, decisões técnicas)
│       ├── data-model.md        ← entidades e esquema
│       ├── contracts/           ← contratos de API e de evento
│       └── tasks.md             ← a quebra em tarefas executáveis
└── (o código, derivado de tudo isso)
```

E o fluxo é uma sequência de comandos de barra, cada um produzindo um artefato que alimenta o próximo. Deixa eu passar por eles mapeando na nossa TechPix, porque é aqui que a aula inteira se encaixa na ferramenta:

**`/speckit.constitution`** — estabelece os princípios inegociáveis do projeto, em `.specify/memory/constitution.md`. E reparem no encaixe: a constituição da TechPix já está escrita, a gente só não sabia o nome. São as invariantes que atravessam o curso desde a Aula 1 — Σ débitos = Σ créditos, todo pagamento tem EndToEndId único, saldo nunca fica negativo, consistência forte no núcleo e eventual na borda, na dúvida falhar fechado, respeitar o rate limit do DICT e o teto de 40 segundos. O ADR registra a decisão e o porquê dela; a constituição **destila o que ficou decidido** em regra que o agente consulta a cada feature nova. São artefatos irmãos: o ADR é a jurisprudência, a constituição é a lei consolidada.

**`/speckit.specify`** — transforma a intenção em `spec.md`, dentro de `specs/001-iniciacao-pagamento/`: o **quê**, sem tecnologia. É exatamente aqui que mora a spec do contexto Pagamentos que a gente escreveu — a linguagem ("Pagamento" ≠ "Transferência"), as invariantes, os eventos emitidos e consumidos, as dependências declaradas. Reparem no detalhe de organização: a spec é **por feature**, dentro do bounded context; a constituição é **global**. A fronteira da Aula 3 diz onde cada uma mora.

**`/speckit.clarify`** — o comando que eu mais gosto de mostrar, porque ele é o interrogatório estruturado que acha ambiguidade **antes** do código existir. O agente varre a spec procurando o que está subespecificado e pergunta. E eu quero que vocês façam o exercício mental: rodem esse comando, em pensamento, sobre a spec do limite diário do Diego. A primeira pergunta que sai é — *"quando você escreve 'conta', você quer dizer a identidade do cliente ou a sub-carteira do ledger?"* O bug que abriu essa aula não sobrevive a um `/speckit.clarify` bem respondido. Ambiguidade de linguagem é exatamente o que esse passo existe para matar.

**`/speckit.plan`** — só agora entra o **como**: `plan.md`, `data-model.md`, `contracts/`. É aqui que as decisões técnicas aparecem — Postgres com serializable para o agregado do ledger, Outbox para publicar os eventos, a ACL traduzindo `pacs.008` para `PixIniciado` — sempre referenciando os ADRs que as justificam. Reparem na disciplina que a ferramenta impõe pela ordem dos comandos: quem tenta escolher banco de dados antes de ter spec clara está usando o fluxo ao contrário — e agora isso fica visível, porque o artefato do "como" simplesmente não existe ainda.

**`/speckit.tasks`** — quebra o plano em `tasks.md`: tarefas pequenas, ordenadas, com dependências explícitas — o formato que tanto um humano quanto um agente conseguem executar e verificar uma a uma.

**`/speckit.analyze`** — a verificação cruzada: a spec, o plano e as tarefas estão consistentes entre si? Alguma tarefa viola a constituição? Algum requisito ficou sem tarefa que o implemente? Vocês já conhecem esse padrão de outro lugar: é a **fitness function da Aula 2, aplicada aos artefatos de especificação** em vez de ao código. O mesmo espírito, um degrau acima.

**`/speckit.implement`** — por fim, o agente executa as tarefas, uma a uma, com a spec e a constituição na janela de contexto. E existem apoios ao redor: `/speckit.checklist` gera listas de verificação de qualidade sob medida, e `/speckit.taskstoissues` converte as tarefas em issues do GitHub para o fluxo do time.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 320" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3sk-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <!-- Constitution: foundation bar -->
  <rect x="30" y="20" width="820" height="52" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="440" y="42" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">/speckit.constitution → .specify/memory/constitution.md</text>
  <text x="440" y="61" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">Σ débitos = Σ créditos · E2E ID único · saldo nunca negativo · falhar fechado · teto 40s — o que NENHUMA feature pode violar</text>

  <!-- Pipeline -->
  <g font-family="sans-serif">
    <rect x="30" y="105" width="150" height="70" rx="9" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
    <text x="105" y="130" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">/speckit.specify</text>
    <text x="105" y="148" text-anchor="middle" font-size="10" fill="#5a55a0">spec.md — o QUÊ</text>
    <text x="105" y="163" text-anchor="middle" font-size="10" fill="#5a55a0">linguagem, invariantes</text>

    <line x1="180" y1="140" x2="205" y2="140" stroke="#4338ca" stroke-width="2" marker-end="url(#a3sk-arrow)"/>

    <rect x="207" y="105" width="150" height="70" rx="9" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
    <text x="282" y="130" text-anchor="middle" font-size="12" font-weight="bold" fill="#7f1d1d">/speckit.clarify</text>
    <text x="282" y="148" text-anchor="middle" font-size="10" fill="#991b1b">"'conta' = identidade</text>
    <text x="282" y="163" text-anchor="middle" font-size="10" fill="#991b1b">ou sub-carteira?"</text>

    <line x1="357" y1="140" x2="382" y2="140" stroke="#4338ca" stroke-width="2" marker-end="url(#a3sk-arrow)"/>

    <rect x="384" y="105" width="150" height="70" rx="9" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
    <text x="459" y="130" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">/speckit.plan</text>
    <text x="459" y="148" text-anchor="middle" font-size="10" fill="#5a55a0">plan.md, data-model.md,</text>
    <text x="459" y="163" text-anchor="middle" font-size="10" fill="#5a55a0">contracts/ — o COMO</text>

    <line x1="534" y1="140" x2="559" y2="140" stroke="#4338ca" stroke-width="2" marker-end="url(#a3sk-arrow)"/>

    <rect x="561" y="105" width="140" height="70" rx="9" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
    <text x="631" y="130" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">/speckit.tasks</text>
    <text x="631" y="148" text-anchor="middle" font-size="10" fill="#5a55a0">tasks.md — quebra</text>
    <text x="631" y="163" text-anchor="middle" font-size="10" fill="#5a55a0">executável, ordenada</text>

    <line x1="701" y1="140" x2="726" y2="140" stroke="#4338ca" stroke-width="2" marker-end="url(#a3sk-arrow)"/>

    <rect x="728" y="105" width="122" height="70" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="789" y="130" text-anchor="middle" font-size="11" font-weight="bold" fill="#166534">/speckit.implement</text>
    <text x="789" y="148" text-anchor="middle" font-size="10" fill="#166534">agente executa,</text>
    <text x="789" y="163" text-anchor="middle" font-size="10" fill="#166534">tarefa a tarefa</text>
  </g>

  <!-- Analyze: cross-check -->
  <rect x="207" y="215" width="494" height="52" rx="9" fill="#fff" stroke="#4338ca" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="454" y="237" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#26215C">/speckit.analyze — consistência spec × plan × tasks × constituição</text>
  <text x="454" y="255" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">a fitness function da Aula 2, aplicada aos artefatos de especificação</text>
  <line x1="282" y1="215" x2="282" y2="178" stroke="#8a89a0" stroke-width="1.5" stroke-dasharray="3 3"/>
  <line x1="459" y1="215" x2="459" y2="178" stroke="#8a89a0" stroke-width="1.5" stroke-dasharray="3 3"/>
  <line x1="631" y1="215" x2="631" y2="178" stroke="#8a89a0" stroke-width="1.5" stroke-dasharray="3 3"/>

  <text x="440" y="300" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">A constituição paira sobre todos os passos: cada artefato é verificado contra ela — e o clarify mata o bug Diego-e-Marina antes do código nascer</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O fluxo do Spec Kit aplicado à TechPix: constituição global, spec por feature, verificação cruzada antes da implementação.</p>
</div>

Para fechar, a tabela que amarra o vocabulário do curso ao artefato da ferramenta:

| Conceito do curso | Artefato no Spec Kit |
|---|---|
| Invariantes de domínio + "falhar fechado" (Aula 1) | `constitution.md` — a lei consolidada, global |
| ADR-001, ADR-002 | Jurisprudência referenciada pela constituição e pelo `plan.md` |
| Spec do bounded context (esta aula) | `spec.md` da feature, dentro de `specs/NNN-…/` |
| Linguagem ubíqua / glossário do contexto | Seção de linguagem do `spec.md` — e alvo do `/speckit.clarify` |
| Contratos de evento (Seção 4.4) | `contracts/` — versionados junto da spec |
| Fitness function (Aula 2) | `/speckit.analyze` — aplicada aos artefatos, antes do código |

E uma nota de honestidade, porque ferramenta é moda e disciplina é fundamento: o Spec Kit é jovem, e os nomes dos comandos podem mudar de versão para versão. O que eu quero que vocês levem não é a sintaxe — é a **ordem imposta**: princípios antes da spec, spec antes do plano, plano antes das tarefas, verificação cruzada antes da implementação. Se amanhã a ferramenta se chamar outra coisa, essa ordem continua sendo o SDD. A ferramenta passa; o fluxo fica.

### 5.2 Context Engineering, agora concreto

E aqui eu quero fechar um círculo que abri na Aula 1, quando falei de Context Engineering de um jeito ainda abstrato. Hoje dá para ser preciso: **se um agente de inteligência artificial for implementar ou modificar alguma coisa dentro do contexto de Pagamentos, o contexto que ele recebe — no sentido de "context window" — deveria ser, literalmente, o bounded context que a gente acabou de desenhar.** A spec de Pagamentos, o glossário da linguagem ubíqua daquele contexto especificamente, os ADRs relevantes — ADR-001 e ADR-002 —, e os eventos que ele emite e consome. E, tão importante quanto o que entra: o que fica de fora. O agente **não** deveria receber os detalhes internos do contexto de Antifraude, ou do contexto de Identidade — só o contrato de evento que os conecta. Isso não é só higiene de prompt; é a mesma disciplina de fronteira que vocês aplicariam a um engenheiro novo entrando no time de Pagamentos: ele aprende a linguagem daquele contexto, e conversa com os outros contextos só pelos contratos publicados, nunca abrindo o capô alheio.

Guardem essa frase, porque ela é, para mim, a ponte mais importante do curso inteiro: **o bounded context de vocês é, literalmente, a unidade de contexto que um agente deveria receber.** DDD não é só uma técnica para humanos se organizarem — é, também, o desenho de como fatiar o conhecimento de um sistema para que um agente raciocine dentro de fronteiras seguras.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3cw-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <!-- Context window -->
  <rect x="30" y="30" width="480" height="240" rx="14" fill="#eef2ff" stroke="#4338ca" stroke-width="3"/>
  <text x="270" y="58" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#26215C">Context window do agente</text>
  <text x="270" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#5a55a0">= o bounded context de Pagamentos, fatiado com disciplina</text>
  <rect x="55" y="95" width="200" height="44" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="155" y="113" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#26215C">Spec de Pagamentos</text>
  <text x="155" y="130" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">linguagem + invariantes + SLA</text>
  <rect x="285" y="95" width="200" height="44" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="385" y="113" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#26215C">Glossário do contexto</text>
  <text x="385" y="130" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">"Pagamento" ≠ "Transferência"</text>
  <rect x="55" y="155" width="200" height="44" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="155" y="173" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#26215C">ADR-001 · ADR-002</text>
  <text x="155" y="190" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">por que o ledger é forte</text>
  <rect x="285" y="155" width="200" height="44" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="385" y="173" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#26215C">Contratos de evento</text>
  <text x="385" y="190" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">FundosReservados, PixLiquidado…</text>
  <text x="270" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">o mesmo pacote que um engenheiro novo receberia ao entrar no time</text>
  <!-- Outside: excluded -->
  <rect x="560" y="55" width="290" height="70" rx="10" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5" stroke-dasharray="6 4"/>
  <text x="705" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#78716c">Internos de Antifraude</text>
  <text x="705" y="102" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#a8a29e">FICA FORA — só o contrato de evento entra</text>
  <rect x="560" y="145" width="290" height="70" rx="10" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5" stroke-dasharray="6 4"/>
  <text x="705" y="172" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#78716c">Internos de Identidade</text>
  <text x="705" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#a8a29e">FICA FORA — ninguém abre o capô alheio</text>
  <line x1="560" y1="90" x2="515" y2="110" stroke="#b91c1c" stroke-width="2"/>
  <line x1="515" y1="90" x2="560" y2="110" stroke="#b91c1c" stroke-width="2"/>
  <line x1="560" y1="170" x2="515" y2="190" stroke="#b91c1c" stroke-width="2"/>
  <line x1="515" y1="170" x2="560" y2="190" stroke="#b91c1c" stroke-width="2"/>
  <text x="440" y="290" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">Context Engineering = a disciplina de fronteira do DDD aplicada à janela de contexto (encher de lixo degrada; faltar o essencial alucina)</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O bounded context como unidade de contexto do agente: o que entra na janela — e, tão importante quanto, o que fica fora.</p>
</div>

---

## 6. Fronteira que ninguém verifica não existe

Eu preciso dizer uma coisa desconfortável sobre tudo que a gente desenhou até aqui: **um bounded context que existe só no diagrama tem prazo de validade de mais ou menos seis semanas.** Basta uma sexta-feira apertada, um `import` conveniente, e a fronteira que custou um dia de event storming vira ficção — e ninguém percebe, porque nada quebra na hora. O acoplamento é uma dívida que só cobra juros no futuro.

Então a pergunta que fecha a modelagem é operacional: **como uma fronteira lógica vira uma barreira que não dá para atravessar por distração?** Três camadas, com tempos de resposta bem diferentes.

**Camada 1 — na compilação, em segundos.** É a fitness function da Aula 2, agora protegendo a fronteira de contexto em vez do desempenho:

```java
@AnalyzeClasses(packages = "br.com.techpix")
class FronteirasDeContextoTest {

    // 1. contexto só conversa pelo contrato publicado — nunca pelo miolo do vizinho
    @ArchTest
    static final ArchRule pagamentos_nao_enxerga_o_miolo_do_ledger =
        noClasses().that().resideInAPackage("..pagamentos..")
            .should().dependOnClassesThat().resideInAPackage("..ledger.internal..");

    // 2. a LINGUAGEM UBÍQUA vira regra executável
    @ArchTest
    static final ArchRule no_contexto_pagamentos_nao_existe_transferencia =
        noClasses().that().resideInAPackage("..pagamentos..")
            .should().haveSimpleNameContaining("Transferencia")
            .because("na spec de Pagamentos, o termo é 'Pagamento'; "
                   + "'Transferência' é vocabulário do contexto Contas");

    // 3. contextos não podem formar ciclo — ciclo é fronteira que não existe
    @ArchTest
    static final ArchRule contextos_sem_ciclo =
        slices().matching("br.com.techpix.(*)..").should().beFreeOfCycles();
}
```

Parem na regra número 2, porque ela é a resposta direta ao bug que abriu a aula. **Ela transforma o glossário do contexto em teste de build.** No dia em que alguém, no contexto de Pagamentos, criar uma classe com "Transferencia" no nome, o build reprova com uma mensagem que explica *por quê* — citando a spec. Não é burocracia: é a linguagem ubíqua deixando de ser uma boa intenção de wiki e virando uma coisa que o repositório defende sozinho. Se houvesse uma regra dessas para a palavra "conta" na TechPix, o Diego e a Marina teriam se encontrado num pull request, e não num relatório de fraude.

**Camada 2 — no banco e nas migrações, em minutos.** É o que a Seção 4.5 mostrou: um esquema por contexto, nenhuma chave estrangeira atravessando a fronteira, nenhum `JOIN` entre esquemas de contextos diferentes. E isso também é verificável — uma consulta no catálogo do Postgres que reprova a migração se alguém criar uma constraint cruzando contextos vale mais do que qualquer combinado verbal.

**Camada 3 — na publicação, no deploy.** É o registro de schema da Seção 4.7: o contrato de evento não passa se for incompatível. Aqui a barreira já está bem tarde no caminho, mas ainda antes do usuário.

E a invariante do agregado, que é a fronteira mais importante de todas, merece um teste de um tipo diferente. Testar com exemplos prova que **um** caso funciona; a invariante do ledger precisa de algo mais agressivo — **teste de propriedade**, que gera milhares de sequências de operações aleatórias e tenta quebrar a regra:

```python
@given(operacoes=lists(operacao_valida(), min_size=1, max_size=200))
def test_invariante_do_ledger_resiste_a_qualquer_sequencia(operacoes):
    ledger = Ledger.novo()
    for op in operacoes:
        try:
            ledger.aplicar(op)
        except SaldoInsuficiente:
            pass                       # recusar é comportamento correto, não falha
    assert ledger.soma_debitos() == ledger.soma_creditos()
    assert all(conta.saldo >= 0 for conta in ledger.contas())
```

A diferença prática é grande: quando esse teste falha, ele não diz só "quebrou" — ele reduz o caso ao **menor contraexemplo possível** e entrega a sequência exata de operações que viola a invariante. É a ferramenta certa para regra de dinheiro. Os nomes, por linguagem: **Hypothesis** (Python), **jqwik** (Java), **fast-check** (TypeScript), **PropEr** (Erlang/Elixir).

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 920 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="460" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">As três camadas que transformam fronteira desenhada em fronteira defendida</text>
  <text x="20" y="52" font-family="sans-serif" font-size="10.5" fill="#888">quanto mais acima, mais barato o erro — o mesmo princípio do "falhar cedo"</text>

  <!-- camada 1 -->
  <rect x="20" y="62" width="880" height="76" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="40" y="88" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#166534">1 · COMPILAÇÃO / CI</text>
  <text x="40" y="107" font-family="sans-serif" font-size="11" fill="#3f7a52">ArchUnit · import-linter · dependency-cruiser · Spring Modulith</text>
  <text x="40" y="125" font-family="sans-serif" font-size="11" fill="#3f7a52">pega: import cruzando fronteira · ciclo entre contextos · palavra proibida pela linguagem ubíqua</text>
  <rect x="700" y="76" width="182" height="48" rx="8" fill="#fff" stroke="#166534" stroke-width="1.5"/>
  <text x="791" y="96" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">resposta em</text>
  <text x="791" y="115" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">segundos</text>

  <!-- camada 2 -->
  <rect x="20" y="148" width="880" height="76" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="40" y="174" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#7a5c00">2 · BANCO / MIGRAÇÃO</text>
  <text x="40" y="193" font-family="sans-serif" font-size="11" fill="#8a6d1a">um schema por contexto · nenhuma FK atravessando · nenhum JOIN entre contextos</text>
  <text x="40" y="211" font-family="sans-serif" font-size="11" fill="#8a6d1a">pega: acoplamento de dados — o mais difícil de desfazer depois (é o que a Aula 6 vai pagar caro)</text>
  <rect x="700" y="162" width="182" height="48" rx="8" fill="#fff" stroke="#d4a017" stroke-width="1.5"/>
  <text x="791" y="182" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">resposta em</text>
  <text x="791" y="201" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#7a5c00">minutos</text>

  <!-- camada 3 -->
  <rect x="20" y="234" width="880" height="76" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="40" y="260" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#26215C">3 · PUBLICAÇÃO / DEPLOY</text>
  <text x="40" y="279" font-family="sans-serif" font-size="11" fill="#5a55a0">schema registry (BACKWARD/FORWARD/FULL) · testes de contrato</text>
  <text x="40" y="297" font-family="sans-serif" font-size="11" fill="#5a55a0">pega: contrato de evento incompatível — a última barreira antes do consumidor</text>
  <rect x="700" y="248" width="182" height="48" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="791" y="268" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#26215C">resposta no</text>
  <text x="791" y="287" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#26215C">deploy</text>

  <!-- o que nenhuma pega -->
  <rect x="20" y="324" width="880" height="62" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="460" y="347" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#b91c1c">O que nenhuma das três pega: a palavra que muda de significado sem mudar de nome</text>
  <text x="460" y="367" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#991b1b">nenhum linter vê que a "conta" do Diego e a "conta" da Marina são coisas diferentes —</text>
  <text x="460" y="381" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#991b1b">isso só a sala pega, no event storming, ou o interrogatório do /speckit.clarify</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Automatize o que dá para automatizar — e reconheça, com honestidade, a única falha que só uma conversa entre pessoas detecta.</p>
</div>

E a conclusão prática, que é a mesma da Aula 2 num contexto novo: **a diferença entre um monólito modular e uma bola de lama não é a intenção do arquiteto — é a existência dessas checagens.** Sem elas, os dois são exatamente o mesmo sistema, e a diferença é apenas o tempo que falta para descobrir.

---

## 7. A Lei de Conway: por que o organograma sempre ganha do diagrama

Tem uma força agindo sobre tudo que a gente desenhou hoje, e ignorá-la é o que faz belíssimos context maps morrerem em seis meses.

Em 1968, Melvin Conway publicou uma observação que virou lei:

> *"Organizações que projetam sistemas estão condenadas a produzir desenhos que são cópias das estruturas de comunicação dessas organizações."*

Não é uma metáfora. É uma consequência quase mecânica: duas pessoas que sentam juntas, conversam o dia inteiro e compartilham o mesmo objetivo vão produzir código acoplado — porque coordenar é barato para elas. Duas pessoas em times diferentes, com prioridades diferentes e reuniões diferentes, vão produzir uma interface — porque coordenar é caro, e a interface é justamente o jeito de coordenar menos. **A arquitetura acompanha o custo de comunicação, não a intenção do diagrama.**

Disso decorre a frase mais dura desta aula: **se a fronteira de domínio e a fronteira de time discordam, a fronteira de time ganha.** Sempre. Não porque as pessoas sejam indisciplinadas — mas porque a conversa diária é uma força contínua, e o diagrama é um evento isolado.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 940 420" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3cw2-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#57534e"/>
    </marker>
  </defs>
  <text x="470" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">A mesma empresa, dois organogramas — e duas arquiteturas inevitáveis</text>

  <!-- ESQUERDA: times por camada -->
  <rect x="16" y="42" width="440" height="330" rx="12" fill="#fff7f7" stroke="#b91c1c" stroke-width="2"/>
  <text x="236" y="66" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#7f1d1d">Times organizados por camada técnica</text>

  <g font-family="sans-serif" font-size="11">
    <rect x="40" y="80" width="392" height="34" rx="6" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
    <text x="236" y="102" text-anchor="middle" fill="#7f1d1d">time de Front-end</text>
    <rect x="40" y="120" width="392" height="34" rx="6" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
    <text x="236" y="142" text-anchor="middle" fill="#7f1d1d">time de Back-end</text>
    <rect x="40" y="160" width="392" height="34" rx="6" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
    <text x="236" y="182" text-anchor="middle" fill="#7f1d1d">time de Banco de Dados</text>
  </g>

  <text x="236" y="218" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">↓ a arquitetura que sai, inevitavelmente ↓</text>

  <rect x="40" y="228" width="392" height="90" rx="8" fill="#fff" stroke="#57534e" stroke-width="1.5"/>
  <text x="236" y="248" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#44403c">camadas horizontais — e todo fluxo de negócio</text>
  <text x="236" y="264" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#44403c">atravessa os três times para ser entregue</text>
  <line x1="90" y1="278" x2="382" y2="278" stroke="#b91c1c" stroke-width="2" stroke-dasharray="4 3"/>
  <line x1="90" y1="296" x2="382" y2="296" stroke="#b91c1c" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="236" y="292" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#b91c1c">"um Pix" = 3 backlogs, 3 prioridades, 3 filas</text>

  <rect x="40" y="328" width="392" height="34" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="236" y="350" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#b91c1c">nenhum time é dono de nenhum bounded context</text>

  <!-- DIREITA: times por fluxo -->
  <rect x="484" y="42" width="440" height="330" rx="12" fill="#f7fdf9" stroke="#166534" stroke-width="2"/>
  <text x="704" y="66" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#166534">Times organizados por fluxo de negócio</text>

  <g font-family="sans-serif" font-size="10.5">
    <rect x="504" y="80" width="126" height="114" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
    <text x="567" y="100" text-anchor="middle" font-weight="bold" fill="#166534">Pagamentos</text>
    <text x="567" y="120" text-anchor="middle" fill="#3f7a52">front + back</text>
    <text x="567" y="136" text-anchor="middle" fill="#3f7a52">+ dados</text>
    <text x="567" y="160" text-anchor="middle" fill="#3f7a52">entrega sozinho</text>
    <text x="567" y="176" text-anchor="middle" fill="#3f7a52">de ponta a ponta</text>

    <rect x="640" y="80" width="126" height="114" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
    <text x="703" y="100" text-anchor="middle" font-weight="bold" fill="#166534">Ledger</text>
    <text x="703" y="120" text-anchor="middle" fill="#3f7a52">front + back</text>
    <text x="703" y="136" text-anchor="middle" fill="#3f7a52">+ dados</text>
    <text x="703" y="160" text-anchor="middle" fill="#3f7a52">entrega sozinho</text>
    <text x="703" y="176" text-anchor="middle" fill="#3f7a52">de ponta a ponta</text>

    <rect x="776" y="80" width="126" height="114" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
    <text x="839" y="100" text-anchor="middle" font-weight="bold" fill="#166534">Antifraude</text>
    <text x="839" y="120" text-anchor="middle" fill="#3f7a52">front + back</text>
    <text x="839" y="136" text-anchor="middle" fill="#3f7a52">+ dados</text>
    <text x="839" y="160" text-anchor="middle" fill="#3f7a52">entrega sozinho</text>
    <text x="839" y="176" text-anchor="middle" fill="#3f7a52">de ponta a ponta</text>
  </g>

  <text x="704" y="218" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">↓ a arquitetura que sai, inevitavelmente ↓</text>

  <rect x="504" y="228" width="398" height="90" rx="8" fill="#fff" stroke="#166534" stroke-width="1.5"/>
  <text x="704" y="248" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">fronteiras verticais, alinhadas com o domínio —</text>
  <text x="704" y="264" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">e contratos onde os times se encontram</text>
  <line x1="620" y1="276" x2="620" y2="308" stroke="#166534" stroke-width="2" stroke-dasharray="4 3"/>
  <line x1="788" y1="276" x2="788" y2="308" stroke="#166534" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="704" y="302" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#166534">"um Pix" = 1 backlog, 1 prioridade</text>

  <rect x="504" y="328" width="398" height="34" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="704" y="350" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#166534">cada bounded context tem um dono claro</text>

  <text x="470" y="398" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#333">Manobra reversa de Conway: em vez de brigar contra o organograma, mude o organograma para produzir a arquitetura que vocês querem.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A Lei de Conway não é uma opinião sobre gestão: é uma restrição de projeto tão real quanto a latência da rede.</p>
</div>

### 7.1 A manobra reversa, e como ela conversa com o context map

Se a arquitetura espelha a organização, existe uma alavanca óbvia — e ela se chama **Inverse Conway Maneuver**: em vez de desenhar a arquitetura desejada e torcer para os times cooperarem, **reorganize os times no formato da arquitetura que vocês querem**, e deixe a Lei de Conway trabalhar a favor. É uma das poucas intervenções de arquitetura que não escreve uma linha de código e mesmo assim muda o sistema.

O vocabulário mais útil para isso hoje vem do *Team Topologies*, de Matthew Skelton e Manuel Pais, e ele encaixa quase perfeitamente no context map da Seção 3:

| Time (Team Topologies) | Papel | No context map da TechPix |
|---|---|---|
| **Stream-aligned** | Entrega valor de ponta a ponta num fluxo de negócio | Pagamentos, Antifraude, Devoluções |
| **Complicated-subsystem** | Cuida de uma parte que exige conhecimento especializado profundo | Contas e Ledger — invariante contábil, concorrência, particionamento |
| **Platform** | Oferece serviços internos como produto, para os outros irem mais rápido | Identidade, e a infraestrutura da Aula 6 |
| **Enabling** | Ensina e capacita os outros times, temporariamente | Quem estiver conduzindo o event storming — inclusive vocês |

E os três **modos de interação** entre times mapeiam, com uma fidelidade que sempre me surpreende, nos padrões de relação entre contextos:

- **Collaboration** (dois times trabalham juntos, alta banda, muito atrito) ↔ **Partnership**. Caro por definição. Serve para descobrir uma fronteira nova — e deve ser **temporário**. Colaboração que virou regime permanente é sinal de fronteira no lugar errado.
- **X-as-a-Service** (um time consome o serviço do outro, banda baixa, contrato claro) ↔ **Open Host Service** / **Customer-Supplier**. É o modo de regime, o alvo. É para onde uma colaboração bem-sucedida deve evoluir.
- **Facilitating** (um time ajuda o outro a ganhar autonomia) ↔ o papel de um time **enabling**.

O diagnóstico prático que sai daí é imediato: **se dois times estão em modo de colaboração permanente, a fronteira entre os contextos deles está errada** — ou eles deveriam ser um time só, ou a fronteira deveria estar em outro lugar. Vocês vão notar que isso é exatamente o Teste 2 da Seção 2.5, o da co-mudança, visto pelo lado das pessoas em vez do lado do repositório. Os dois medem a mesma coisa: quanta coordenação a fronteira exige. E é uma boa hora para revisitar aquela matriz — os 48% de co-mudança entre Pagamentos e Antifraude não são um problema de código. São o retrato de duas equipes que precisam se falar o tempo todo porque a regra de limite mora nas duas.

E fecho essa seção com o aviso que eu daria a mim mesmo dez anos atrás: **não desenhe uma arquitetura que o seu organograma não suporta.** Se vocês têm quatro times e desenharam onze contextos com donos distintos, o desenho está errado — não porque os contextos estejam mal identificados, mas porque não existe quem os defenda. Contexto sem dono não sobrevive ao segundo trimestre.

---

## 8. Bounded context = microsserviço? (a pergunta que sempre aparece)

Essa pergunta vem em toda turma, e ela merece uma resposta cuidadosa porque a resposta simplista causa dano real.

A resposta curta: **um bounded context é um bom *candidato* a serviço, mas não uma obrigação.** A relação correta é: um serviço nunca deve conter mais de um bounded context (senão vocês voltaram à bola de lama, só que distribuída); mas um bounded context pode perfeitamente permanecer como módulo dentro de um monólito modular — e frequentemente **deve**.

Reparem que isso é exatamente a recomendação da Aula 2, agora com vocabulário melhor: as fronteiras que a gente descobriu hoje por event storming são as fronteiras de módulo do monólito modular. Extrair para serviço separado é uma **decisão posterior e independente**, tomada por critérios operacionais, não de modelagem.

E quais são esses critérios? Extrair um contexto para serviço próprio se justifica quando pelo menos um destes for verdadeiro:

- O contexto precisa **escalar de forma diferente** do resto. O Antifraude da TechPix, por exemplo, pode precisar de máquinas com muito mais CPU (ou GPU, se usar modelo de risco) do que o resto do sistema. Escalar junto significa pagar por capacidade que só uma parte precisa.
- O contexto tem um **ciclo de vida de deploy diferente** — muda várias vezes por dia enquanto o resto muda por semana, ou o contrário.
- O contexto pertence a um **time diferente**, e o acoplamento de deploy está causando fila de espera entre times. (Este é, na prática, o motivo mais comum e mais legítimo.)
- O contexto tem **requisito de disponibilidade ou de isolamento de falha** distinto — e aí é o bulkhead da Aula 2, aplicado no nível de serviço.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 930 452" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a3ms-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
    <marker id="a3ms-k" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#57534e"/>
    </marker>
  </defs>
  <text x="465" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Extrair este contexto para um serviço próprio? Quatro portões, e o default é "não"</text>

  <!-- barra sim -->
  <rect x="20" y="38" width="890" height="50" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="465" y="60" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">SIM em qualquer um → extrair para serviço próprio se justifica</text>
  <text x="465" y="78" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3f7a52">(justifica avaliar — e ainda assim, com os custos da tabela abaixo na mão)</text>

  <!-- portões -->
  <g font-family="sans-serif">
    <rect x="20" y="122" width="200" height="80" rx="9" fill="#fff" stroke="#4338ca" stroke-width="2"/>
    <text x="120" y="144" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#26215C">1 · escala diferente?</text>
    <text x="120" y="164" text-anchor="middle" font-size="10.5" fill="#5a55a0">Antifraude precisa de CPU/GPU</text>
    <text x="120" y="179" text-anchor="middle" font-size="10.5" fill="#5a55a0">que o resto não precisa</text>
    <text x="120" y="195" text-anchor="middle" font-size="10" fill="#888">escalar junto = pagar por todos</text>

    <rect x="250" y="122" width="200" height="80" rx="9" fill="#fff" stroke="#4338ca" stroke-width="2"/>
    <text x="350" y="144" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#26215C">2 · deploy diferente?</text>
    <text x="350" y="164" text-anchor="middle" font-size="10.5" fill="#5a55a0">um muda 10× por dia,</text>
    <text x="350" y="179" text-anchor="middle" font-size="10.5" fill="#5a55a0">o outro 1× por semana</text>
    <text x="350" y="195" text-anchor="middle" font-size="10" fill="#888">o lento segura o rápido</text>

    <rect x="480" y="122" width="200" height="80" rx="9" fill="#fff" stroke="#166534" stroke-width="2.5"/>
    <text x="580" y="144" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">3 · time diferente?</text>
    <text x="580" y="164" text-anchor="middle" font-size="10.5" fill="#3f7a52">o acoplamento de deploy</text>
    <text x="580" y="179" text-anchor="middle" font-size="10.5" fill="#3f7a52">virou fila entre times</text>
    <text x="580" y="195" text-anchor="middle" font-size="10" font-weight="bold" fill="#166534">o mais comum e legítimo</text>

    <rect x="710" y="122" width="200" height="80" rx="9" fill="#fff" stroke="#4338ca" stroke-width="2"/>
    <text x="810" y="144" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#26215C">4 · isolamento de falha?</text>
    <text x="810" y="164" text-anchor="middle" font-size="10.5" fill="#5a55a0">disponibilidade exigida</text>
    <text x="810" y="179" text-anchor="middle" font-size="10.5" fill="#5a55a0">é diferente do resto</text>
    <text x="810" y="195" text-anchor="middle" font-size="10" fill="#888">é o bulkhead da Aula 2, no nível de serviço</text>
  </g>

  <!-- setas sim (para cima) -->
  <line x1="120" y1="122" x2="120" y2="92" stroke="#166534" stroke-width="2" marker-end="url(#a3ms-g)"/>
  <line x1="350" y1="122" x2="350" y2="92" stroke="#166534" stroke-width="2" marker-end="url(#a3ms-g)"/>
  <line x1="580" y1="122" x2="580" y2="92" stroke="#166534" stroke-width="2" marker-end="url(#a3ms-g)"/>
  <line x1="810" y1="122" x2="810" y2="92" stroke="#166534" stroke-width="2" marker-end="url(#a3ms-g)"/>
  <text x="136" y="112" font-family="sans-serif" font-size="10" fill="#166534">sim</text>
  <text x="366" y="112" font-family="sans-serif" font-size="10" fill="#166534">sim</text>
  <text x="596" y="112" font-family="sans-serif" font-size="10" fill="#166534">sim</text>
  <text x="826" y="112" font-family="sans-serif" font-size="10" fill="#166534">sim</text>

  <!-- setas não (encadeadas) -->
  <line x1="220" y1="162" x2="246" y2="162" stroke="#57534e" stroke-width="2" marker-end="url(#a3ms-k)"/>
  <line x1="450" y1="162" x2="476" y2="162" stroke="#57534e" stroke-width="2" marker-end="url(#a3ms-k)"/>
  <line x1="680" y1="162" x2="706" y2="162" stroke="#57534e" stroke-width="2" marker-end="url(#a3ms-k)"/>
  <text x="233" y="155" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#57534e">não</text>
  <text x="463" y="155" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#57534e">não</text>
  <text x="693" y="155" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#57534e">não</text>

  <!-- não final -->
  <polyline points="910,162 924,162 924,232 620,232" fill="none" stroke="#57534e" stroke-width="2" marker-end="url(#a3ms-k)"/>
  <rect x="150" y="212" width="460" height="60" rx="10" fill="#f5f5f4" stroke="#57534e" stroke-width="2.5"/>
  <text x="380" y="235" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#44403c">NÃO em todos → permanece módulo do monólito modular</text>
  <text x="380" y="256" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">com a fronteira defendida pelas três camadas da Seção 6 — e isso é sucesso, não adiamento</text>

  <!-- custos -->
  <rect x="20" y="292" width="890" height="146" rx="11" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="465" y="316" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#b91c1c">O que a extração cobra, mesmo quando é a decisão certa</text>
  <g font-family="sans-serif" font-size="11" fill="#7f1d1d">
    <text x="44" y="342">• a chamada em memória vira rede: latência nova, e uma cauda p99 muito pior (Aula 4)</text>
    <text x="44" y="364">• falha parcial: o vizinho pode estar fora do ar enquanto vocês estão de pé (Aulas 2 e 4)</text>
    <text x="44" y="386">• a transação vira saga, com compensação em vez de rollback (Aula 4)</text>
    <text x="490" y="342">• banco por serviço: dual-run, backfill, reconciliação (Aula 6)</text>
    <text x="490" y="364">• só se enxerga o fluxo com tracing distribuído (Aula 7)</text>
    <text x="490" y="386">• contrato versionado, deploy independente, plantão próprio</text>
  </g>
  <text x="465" y="416" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#b91c1c">Extrair é fácil; voltar atrás é um projeto. Por isso o default é permanecer módulo.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Os quatro portões da extração — e a conta que precisa estar na mesa antes de qualquer um deles ser respondido com "sim".</p>
</div>

Reparem numa assimetria que vale ouro na hora de decidir: **transformar um módulo em serviço é um sprint; transformar um serviço de volta em módulo é um projeto.** As duas direções não custam o mesmo, e por isso as duas não merecem o mesmo grau de certeza. Quando estiverem em dúvida, a decisão reversível é ficar no monólito modular — porque ela mantém a opção aberta, e a opção tem valor.

E o alerta que fecha o assunto: se nenhum desses critérios se aplica, extrair o serviço só compra os **custos** de sistema distribuído — latência de rede, falha parcial, consistência eventual entre serviços, complexidade de observabilidade — sem comprar nenhum dos benefícios. Vocês pagaram o preço e não levaram o produto.

Guardem a formulação: **bounded context é decisão de modelagem; microsserviço é decisão de topologia.** Elas se relacionam, mas não são a mesma decisão, e confundi-las é a origem de boa parte dos projetos de microsserviços que dão errado.

---

## 9. As ferramentas reais — nomes, não conceitos

Do mesmo jeito que a Aula 2 fez com resiliência, eu quero que vocês saiam daqui com nomes pesquisáveis. Modelagem de domínio tem fama de ser só conversa e post-it; tem bem mais ferramenta do que parece.

**Para facilitar a descoberta.** O event storming em si roda em qualquer superfície — **Miro**, **Excalidraw** (o nosso), **FigJam** —, e o que importa é a disciplina de cores da Seção 2.1, não a ferramenta. Para registrar o resultado de forma durável, existem duas famílias: o **Context Mapper**, uma DSL de código aberto em que vocês escrevem os contextos e as relações em texto (`ContextMap { contains Pagamentos, Ledger; Pagamentos [D]<-[U] Ledger }`) e obtêm diagramas gerados e versionados no Git; e o **egon.io**, para *domain storytelling*, que é uma técnica-irmã, útil quando o problema é entender um fluxo com muitos atores.

**Para defender a fronteira no build.** O **ArchUnit** (Java/Kotlin) é o mais completo, e tem primos em praticamente toda linguagem: **ArchUnitNET** e **NetArchTest** (.NET), **import-linter** (Python), **dependency-cruiser** e **eslint-plugin-boundaries** (JavaScript/TypeScript), **deptrac** e **phpat** (PHP), **go-arch-lint** (Go). Em Java há ainda dois que vale conhecer por resolverem o problema num nível acima: o **Spring Modulith**, que reconhece módulos por convenção, verifica as dependências entre eles, gera documentação e ainda oferece publicação de eventos de domínio com Outbox embutido — é, literalmente, um monólito modular com as regras desta aula implementadas; e o **jMolecules**, que deixa vocês anotarem `@AggregateRoot`, `@Entity`, `@ValueObject` e validarem as regras de agregado no build.

**Para governar contratos de evento.** A especificação é o **AsyncAPI** — pensem nele como o OpenAPI do mundo assíncrono: descreve canais, mensagens e schemas de forma legível por humano e por ferramenta. Para a checagem automática, os registros: **Confluent Schema Registry** (o mais difundido), **Apicurio Registry** (open source, agnóstico), o registry do **Redpanda**, e o **Buf**, que para Protobuf faz detecção de mudança quebra-contrato direto no pull request — que é onde essa checagem deveria estar. Para documentar quem publica e quem consome o quê, o **EventCatalog** monta um portal navegável a partir dos seus schemas; e é ele que responde a pergunta que trava toda migração de versão: *quem ainda consome a v1?*

**Para os agregados, quando o domínio pede mais.** Se vocês forem para event sourcing — que esta aula não recomenda como default, mas que aparece com frequência em ledger —, os nomes são **EventStoreDB**, **Axon Framework** (Java), **Marten** (.NET sobre Postgres) e **Eventuate**. Todos implementam versionamento de evento e *upcasting* de fábrica, o que é um bom argumento a favor deles: vocês não vão reinventar a Seção 4.7.

**Para medir a fronteira.** O **code-maat** e o **CodeScene**, do Adam Tornhill, transformam o histórico do Git na matriz de co-mudança da Seção 2.5 — e o segundo faz isso continuamente, mostrando as fronteiras apodrecendo ao longo do tempo, em vez de num retrato único.

**E para o fluxo de spec.** O **GitHub Spec Kit** da Seção 5.1, e o **Kiro**, a IDE da AWS orientada a especificação.

| Preciso de… | Ferramenta |
|---|---|
| Registrar o context map como código versionado | **Context Mapper** (DSL) |
| Quebrar o build quando alguém atravessa a fronteira | **ArchUnit** · import-linter · dependency-cruiser · deptrac · go-arch-lint |
| Monólito modular com módulos verificados e eventos | **Spring Modulith** · jMolecules |
| Descrever o contrato de evento | **AsyncAPI** |
| Impedir publicação de schema incompatível | **Confluent Schema Registry** · Apicurio · Buf |
| Saber quem consome cada evento | **EventCatalog** |
| Testar a invariante do agregado a sério | **Hypothesis** · jqwik · fast-check |
| Ver a fronteira apodrecendo no histórico | **code-maat** · CodeScene |
| Rodar o fluxo de SDD dentro do agente | **GitHub Spec Kit** · Kiro |

Uma advertência para fechar, no mesmo espírito da que eu dei sobre o Spec Kit: **nenhuma dessas ferramentas descobre uma fronteira.** Todas elas defendem, documentam ou medem uma fronteira que vocês já decidiram. A descoberta continua sendo um exercício humano, numa sala, com pessoas que discordam — e é por isso que ele abre esta aula, e não fecha.

---

## 10. Fecho: linguagem é arquitetura

Deixa eu recapitular o que a gente construiu hoje.

Primeiro: **a linguagem ubíqua vale dentro de um contexto, não globalmente** — e o erro do Diego e da Marina não foi ter duas definições de "conta"; foi não saber que existiam duas.

Segundo: **bounded contexts emergem dos eventos do domínio**, de baixo para cima, através do event storming — não são impostos de cima para baixo por um palpite, por melhor que ele seja.

Terceiro: **a fronteira de consistência transacional é a fronteira do agregado**, e ela geralmente coincide com o núcleo do bounded context — é isso que separa o que precisa ser forte na hora do que pode esperar um instante.

Quarto: **a camada anticorrupção protege a linguagem de vocês do mundo externo** — é o que já estava acontecendo, sem nome, toda vez que a TechPix traduzia uma mensagem do BACEN para um evento de domínio.

E quinto — o fio que amarra tudo com o eixo de inteligência artificial: **a spec de um bounded context é executável, e é, ao mesmo tempo, a unidade certa de contexto para um agente trabalhar com segurança.**

Sexto: **o tamanho do agregado é uma decisão de capacidade, e dá para calculá-la** — vazão máxima é um dividido pelo tempo de lock. O ponto quente que derrubou a TechPix no dia 5 tinha um teto de vinte transações por segundo escrito numa reunião de modelagem, meses antes de o incidente acontecer.

Sétimo: **fronteira que ninguém verifica não existe** — e as três camadas que a defendem (compilação, banco, publicação) são o que separa um monólito modular de uma bola de lama.

E oitavo, o que eu deixaria por último se só pudesse deixar um: **a Lei de Conway não negocia.** Se a fronteira que vocês desenharam hoje não tiver um time dono, ela não sobrevive ao trimestre — e o conserto, nesse caso, não é no código.

E antes de eu passar o bastão, deixa eu fazer o que eu sempre peço a vocês: parar e olhar o que já está de pé. Reparem numa coisa curiosa no retrato de hoje — nenhuma caixa nova é infraestrutura. O que esta aula acrescentou foi **nome, fronteira e contrato** em cima do que as Aulas 1 e 2 construíram. Modelagem não sobe servidor; ela decide onde os próximos servidores vão poder nascer.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 336" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="440" y="22" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333">A TechPix ao fim da Aula 3</text>

  <text x="20" y="44" font-family="sans-serif" font-size="10" font-weight="bold" fill="#a8a29e">JÁ EXISTIA — AULAS 1 E 2</text>
  <g font-family="sans-serif">
    <rect x="20" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="122" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Monólito TechPix</text>
    <text x="122" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">Postgres · ledger partida dobrada · [A1]</text>
    <rect x="232" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="334" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Idempotência</text>
    <text x="334" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">chave E2E ID · [A1]</text>
    <rect x="444" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="546" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">DICT · SPI (BACEN)</text>
    <text x="546" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">cache disciplinado · rate limit · [A1]</text>
    <rect x="656" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="758" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Outbox → relay → Kafka</text>
    <text x="758" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">eventos do domínio · [A2]</text>

    <rect x="20" y="104" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="122" y="123" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Read models CQRS</text>
    <text x="122" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">Redis (saldo) · réplica (extrato) · [A2]</text>
    <rect x="232" y="104" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="334" y="123" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Defesas de resiliência</text>
    <text x="334" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">circuit breaker · bulkhead · backoff · [A2]</text>
    <rect x="444" y="104" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="546" y="123" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Partições hash(conta_id)</text>
    <text x="546" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">8 partições · ~20 baldes · [A2]</text>
    <rect x="656" y="104" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="758" y="123" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">ADR-001 · ADR-002</text>
    <text x="758" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">decisões registradas · [A1·A2]</text>
  </g>

  <text x="20" y="172" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">CONSTRUÍDO NESTA AULA</text>
  <g font-family="sans-serif">
    <rect x="20" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="101" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">5 bounded contexts</text>
    <text x="101" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">fronteiras nomeadas</text>
    <rect x="192" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="273" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Context map</text>
    <text x="273" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">upstream · downstream</text>
    <rect x="364" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="445" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">ACL BACEN</text>
    <text x="445" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">pacs.008 → PixIniciado</text>
    <rect x="536" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="617" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Spec de Pagamentos</text>
    <text x="617" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">specs/001-…/spec.md</text>
    <rect x="708" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="789" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Constituição</text>
    <text x="789" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">.specify/memory (Spec Kit)</text>
  </g>

  <g font-family="sans-serif">
    <rect x="20" y="236" width="208" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="124" y="256" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Subdomínios classificados</text>
    <text x="124" y="273" text-anchor="middle" font-size="9.5" fill="#15803d">core · supporting · generic</text>
    <rect x="236" y="236" width="208" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="340" y="256" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Fronteira verificada</text>
    <text x="340" y="273" text-anchor="middle" font-size="9.5" fill="#15803d">ArchUnit · schema por contexto</text>
    <rect x="452" y="236" width="208" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="556" y="256" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Contrato de evento</text>
    <text x="556" y="273" text-anchor="middle" font-size="9.5" fill="#15803d">gordo · versionado · registry</text>
    <rect x="668" y="236" width="208" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="772" y="256" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Times alinhados</text>
    <text x="772" y="273" text-anchor="middle" font-size="9.5" fill="#15803d">um dono por contexto (Conway)</text>
  </g>

  <text x="440" y="312" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">cinza = já existia · verde = construído nesta aula · e nenhuma caixa verde é infraestrutura</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A régua de evolução da TechPix: a Aula 3 não sobe infraestrutura — ela dá nome, fronteira e contrato ao que as Aulas 1 e 2 construíram.</p>
</div>

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
| **Spec Kit** | Kit de código aberto do GitHub que estrutura o SDD como comandos dentro do agente de código (Claude Code, Copilot, Gemini CLI, Cursor…): `/speckit.constitution` → `specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`. |
| **constitution.md** | O núcleo duro do projeto no Spec Kit (`.specify/memory/`): princípios que nenhuma feature pode violar. ADR é a jurisprudência; a constituição é a lei consolidada. |
| **spec.md / plan.md / tasks.md** | Os artefatos por feature (`specs/NNN-…/`): o quê (requisitos, linguagem, invariantes), o como (stack, decisões, `data-model.md`, `contracts/`) e a quebra executável. |
| **/speckit.clarify** | Interrogatório estruturado que caça ambiguidade na spec antes do código — o comando que teria matado o bug Diego-e-Marina ("'conta' = identidade ou sub-carteira?"). |
| **/speckit.analyze** | Verificação cruzada spec × plan × tasks × constituição — a fitness function aplicada aos artefatos de especificação. |
| **Subdomínio core / supporting / generic** | Classificação estratégica que decide onde investir engenharia: core se constrói com o melhor time, supporting se constrói simples, generic se compra. O erro clássico é o inverso. |
| **Gramática do event storming** | Ator → comando → agregado → evento → política → comando. As cores dos post-its não são decoração: cada uma vira uma coisa diferente no código. |
| **Hotspot (post-it vermelho)** | Marcação de dúvida ou discordância na sessão. O artefato mais valioso do event storming — é o bug que ainda não aconteceu, registrado no papel. |
| **Política (post-it roxo)** | "Sempre que *tal evento*, então *tal comando*". Vira, no código, o consumidor de evento — o `@KafkaListener` de daqui a três semanas. |
| **Níveis do event storming** | Big Picture (descobrir contextos) → Process Level (um fluxo) → Design Level (agregados e invariantes). Começar pelo último reproduz as fronteiras erradas que já existiam. |
| **Teste de co-mudança** | Se dois módulos aparecem no mesmo commit em mais de ~40% das vezes, a fronteira entre eles é decorativa. Mede-se no histórico do Git (code-maat, CodeScene). |
| **Open Host Service** | Upstream publica um protocolo estável para muitos consumidores. O SPI e o DICT são exatamente isso. |
| **Published Language** | Linguagem de intercâmbio compartilhada por um ecossistema inteiro. O **ISO 20022** é o exemplo canônico — e é por isso que a resposta certa a ele é ACL. |
| **Separate Ways** | Não integrar, e aceitar a duplicação, quando integrar custa mais do que duplicar. |
| **Teto de vazão do agregado** | **1 ÷ tempo em que o lock fica segurado.** Lock de 4 ms = 250 tx/s, independentemente do hardware. Chamada de rede dentro da fronteira derruba esse teto para o p99 do mundo externo. |
| **Uma transação, um agregado** | Regra operacional que resume a Regra 4 de Vernon. Se a transação escreve dois agregados, ou a fronteira está errada, ou a operação está. |
| **Bloqueio otimista** | `WHERE versao = :versao_lida AND saldo >= :valor`: a invariante mora no próprio banco, e a taxa de "0 linhas afetadas" vira a métrica de contenção do agregado. |
| **Um esquema por contexto** | Cada contexto dono do seu schema no banco, **sem chave estrangeira atravessando a fronteira**. A FK que vocês não criam vale mais que as que criam. |
| **Evento magro × evento gordo** | Notificação (só o id, consumidor liga de volta, lê o estado de *agora*) versus *event-carried state transfer* (carrega o estado do instante do fato, consumidor autônomo). Em fintech: gordo, com o mínimo de dado pessoal. |
| **BACKWARD / FORWARD / FULL** | Modos de compatibilidade de schema. BACKWARD: consumidor novo lê evento velho (reprocessamento). FORWARD: consumidor velho lê evento novo (deploy gradual). FULL: os dois. |
| **Upcasting** | Converter o evento antigo para o formato novo **na leitura**, concentrando num lugar só o conhecimento do passado. Evento é fato histórico: não se reescreve. |
| **Teste de propriedade** | Gerar milhares de sequências aleatórias para tentar quebrar a invariante, e receber o menor contraexemplo quando ela quebra. Hypothesis, jqwik, fast-check. |
| **Lei de Conway** | A arquitetura espelha a estrutura de comunicação da organização. Corolário duro: quando a fronteira de domínio e a de time discordam, a de time ganha. |
| **Inverse Conway Maneuver** | Reorganizar os times no formato da arquitetura desejada, e deixar a Lei de Conway trabalhar a favor. |
| **Modos de interação (Team Topologies)** | Collaboration ↔ partnership (caro, temporário) · X-as-a-Service ↔ open host service (o regime desejado) · Facilitating ↔ time enabling. Colaboração permanente = fronteira errada. |
| **Assimetria da extração** | Virar serviço é um sprint; voltar a ser módulo é um projeto. Por isso o default é permanecer módulo do monólito modular. |

---

## Apêndice — Para aprofundar

<details markdown="1" style="margin:16px 0;border:1px solid #d0d7de;border-radius:6px;padding:12px 16px;background:#f6f8fa;">
<summary style="cursor:pointer;font-weight:600;list-style:none;">📚 Leituras que sustentam esta aula</summary>

**Sobre DDD estratégico**

- Eric Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003) — o "livro azul", onde bounded context, linguagem ubíqua e os padrões de context map foram formulados. A Parte IV é a que importa para esta aula.
- Vaughn Vernon, *Implementing Domain-Driven Design* (2013) — de onde vêm as quatro regras de agregado da Seção 4.1. Se o tempo for curto, o *Domain-Driven Design Distilled* (2016) do mesmo autor cobre o essencial em um terço das páginas.
- Vlad Khononov, *Learning Domain-Driven Design* (2021) — o mais prático dos três, e o que melhor trata a classificação de subdomínios da Seção 1.5.
- Martin Fowler, verbetes *BoundedContext*, *UbiquitousLanguage* e *EventCollaboration* no bliki — leitura de vinte minutos que cobre o vocabulário.

**Sobre event storming**

- Alberto Brandolini, *Introducing EventStorming* — do criador da técnica; a fonte da gramática e dos três níveis da Seção 2.
- *EventStorming Glossary & Cheat Sheet*, de Paul Rayner — referência rápida de cores e notação para levar para a sala.

**Sobre agregados, consistência e contratos**

- Pat Helland, *Life Beyond Distributed Transactions: An Apostate's Opinion* (2007) — o artigo que antecipou, em vocabulário de banco de dados, quase tudo que esta aula chama de agregado e consistência eventual entre fronteiras.
- Martin Kleppmann, *Designing Data-Intensive Applications* — Capítulos 7 e 11, para contenção, isolamento e evolução de schema de evento.
- Greg Young, *Versioning in an Event Sourced System* — o tratamento mais completo de versionamento e *upcasting*.

**Sobre organização e fronteiras**

- Melvin Conway, *How Do Committees Invent?* (1968) — o artigo original, e ele é curto.
- Matthew Skelton e Manuel Pais, *Team Topologies* (2019) — os quatro tipos de time e os três modos de interação da Seção 7.1.
- Adam Tornhill, *Your Code as a Crime Scene* e *Software Design X-Rays* — a base da análise de co-mudança da Seção 2.5.
- Neal Ford, Rebecca Parsons e Patrick Kua, *Building Evolutionary Architectures* — fitness functions, que a Aula 2 apresentou e a Seção 6 aplica a fronteiras.

**Documentação de ferramenta**

- Context Mapper (`contextmapper.org`) · ArchUnit (`archunit.org`) · Spring Modulith · AsyncAPI (`asyncapi.com`) · EventCatalog (`eventcatalog.dev`) · GitHub Spec Kit.

</details>


---

[← Aula 2](aula2-conteudo-completo.md) · [Índice](index.md) · [Aula 4 →](aula4-conteudo-completo.md)
