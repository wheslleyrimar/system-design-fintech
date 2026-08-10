---
layout: default
title: "Aula 5 — Núcleo da Fintech com IA e Agentes"
---

# Aula 5 — Núcleo da Fintech com IA e Agentes
*Curso de Arquitetura de Sistemas Financeiros com IA*

> **Navegação:** [Índice](index.md) · [Aula 1](aula1-conteudo-completo.md) · [Aula 2](aula2-conteudo-completo.md) · [Aula 3](aula3-conteudo-completo.md) · [Aula 4](aula4-conteudo-completo.md) · **Aula 5 (você está aqui)** · [Aula 6](aula6-conteudo-completo.md) · [Aula 7](aula7-conteudo-completo.md) · [Aula 8](aula8-conteudo-completo.md)

Semana passada eu terminei a aula com uma promessa: a chamada síncrona de Pagamentos para Antifraude, aquela que a gente colocou no caminho crítico com um orçamento de ~100 milissegundos no p99, ia ganhar um inquilino novo. Hoje eu pago essa promessa. Mas antes, como sempre, deixa eu contar o que aconteceu — porque dessa vez o sistema não ficou lento, não caiu, não congelou extrato nenhum. Dessa vez o sistema funcionou perfeitamente. E foi exatamente assim que ele falhou.

Madrugada de 3 de outubro de 2025, 2h31 da manhã. Se esse horário soa familiar, é de propósito: foi mais ou menos nessa hora que a Ana, lá na Aula 1, tocou três vezes em "pagar". Só que dessa vez não é a Ana. São dezenas de contas — abertas semanas antes, com documentos válidos, movimentação inocente — que começam, quase ao mesmo tempo, a receber Pix. Muitos Pix. Centenas de transferências de **R$ 49,90** cada uma, vindas de contas de vítimas espalhadas pelo país, todas abaixo de qualquer limite que dispare alerta.

Reparem no desenho do golpe, porque ele é quase elegante: nenhuma transação individual viola regra nenhuma. R$ 49,90 está abaixo do limite noturno. Está abaixo do limiar de valor suspeito. As contas recebedoras têm KYC válido — o time de Identidade e Onboarding fez o trabalho direito. As regras do Antifraude — limiares de valor, listas de contas marcadas, contagem de tentativas — olham cada Pix isoladamente e dizem: "inocente, inocente, inocente", centenas de vezes seguidas.

O fraudador não quebrou nenhuma regra. **Ele explorou o espaço entre as regras.** O padrão — dezenas de contas novas recebendo rajadas coordenadas de valores pequenos e idênticos, na madrugada, com saque na sequência — grita fraude para qualquer analista humano que olhe o conjunto. Mas nenhuma regra olhava o conjunto. Cada uma olhava a sua fatia.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 340" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a5golpe-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
    <marker id="a5golpe-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <text x="20" y="24" font-family="sans-serif" font-size="12" fill="#666">2h31 · centenas de Pix de R$ 49,90 — cada um, isolado, abaixo de todo limiar</text>
  <!-- vítimas -->
  <g font-family="sans-serif" font-size="11" fill="#333">
    <rect x="20" y="45" width="90" height="28" rx="6" fill="#fff" stroke="#999"/><text x="65" y="63" text-anchor="middle">vítima 1</text>
    <rect x="20" y="83" width="90" height="28" rx="6" fill="#fff" stroke="#999"/><text x="65" y="101" text-anchor="middle">vítima 2</text>
    <rect x="20" y="121" width="90" height="28" rx="6" fill="#fff" stroke="#999"/><text x="65" y="139" text-anchor="middle">vítima 3</text>
    <rect x="20" y="159" width="90" height="28" rx="6" fill="#fff" stroke="#999"/><text x="65" y="177" text-anchor="middle">vítima 4</text>
    <text x="65" y="205" text-anchor="middle" fill="#888">⋮ centenas</text>
  </g>
  <!-- setas R$49,90 -->
  <line x1="110" y1="59" x2="330" y2="85" stroke="#888" stroke-width="1.5" marker-end="url(#a5golpe-arrow)"/>
  <line x1="110" y1="97" x2="330" y2="95" stroke="#888" stroke-width="1.5" marker-end="url(#a5golpe-arrow)"/>
  <line x1="110" y1="135" x2="330" y2="150" stroke="#888" stroke-width="1.5" marker-end="url(#a5golpe-arrow)"/>
  <line x1="110" y1="173" x2="330" y2="160" stroke="#888" stroke-width="1.5" marker-end="url(#a5golpe-arrow)"/>
  <text x="220" y="78" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b45309">R$ 49,90 ×N</text>
  <!-- laranjas -->
  <circle cx="380" cy="90" r="38" fill="#fff7ed" stroke="#c2410c" stroke-width="2.5"/>
  <text x="380" y="86" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">laranja A</text>
  <text x="380" y="101" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#7c2d12">conta nova, KYC ok</text>
  <circle cx="380" cy="175" r="38" fill="#fff7ed" stroke="#c2410c" stroke-width="2.5"/>
  <text x="380" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">laranja B</text>
  <text x="380" y="186" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#7c2d12">conta nova, KYC ok</text>
  <!-- saque -->
  <line x1="418" y1="90" x2="530" y2="120" stroke="#b91c1c" stroke-width="2" marker-end="url(#a5golpe-red)"/>
  <line x1="418" y1="175" x2="530" y2="145" stroke="#b91c1c" stroke-width="2" marker-end="url(#a5golpe-red)"/>
  <rect x="535" y="112" width="110" height="40" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="590" y="137" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">saque em sequência</text>
  <!-- duas lentes -->
  <rect x="20" y="235" width="400" height="80" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="220" y="258" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">A lente da regra: 1 transação por vez</text>
  <text x="220" y="278" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">R$ 49,90 &lt; limite noturno · KYC válido · sem lista</text>
  <text x="220" y="298" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">→ "inocente" ✓ (centenas de vezes)</text>
  <rect x="450" y="235" width="410" height="80" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="655" y="258" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">A lente do padrão: o conjunto</text>
  <text x="655" y="278" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">contas novas + rajada coordenada + valor idêntico</text>
  <text x="655" y="298" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">+ madrugada + saque → fraude ⚠</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O golpe dos R$ 49,90: nenhuma transação viola regra alguma — o sinal só existe no conjunto, que nenhuma regra olhava.</p>
</div>

O prejuízo foi contido: o MED — o trilho de devolução que vocês conhecem desde a Aula 1, com a Recuperação de Valores rastreando o grafo de contas — recuperou boa parte, e o bloqueio cautelar de 72 horas congelou o resto antes do saque completo. Mas o recado ficou na parede da sala do time, escrito pelo Diego, do Antifraude, no dia seguinte: **"regra pega o golpe de ontem; padrão pega o golpe de hoje."**

Essa frase é o tema da aula. Hoje a gente coloca um modelo de machine learning no núcleo do TechPix — dentro do caminho crítico do Pix, dentro daquele orçamento de 100 milissegundos — sem abrir mão de nada do que esse curso construiu até aqui: correção acima de disponibilidade, auditabilidade, falhar fechado. E no fim, eu vou mostrar como a mesma tecnologia entra do outro lado do balcão: não decidindo sobre transações, mas ajudando um humano a decidir melhor.

---

## 1. Por que IA no núcleo — e o que ela nunca pode fazer

### 1.1 O problema que regra nenhuma resolve

Deixa eu formalizar o que o golpe dos R$ 49,90 expôs. Uma regra determinística é uma função simples: recebe uma transação, compara com limiares fixos, devolve sim ou não. Ela tem três virtudes que a gente não vai abrir mão nunca: é **explicável** (qualquer auditor entende "bloqueou porque valor > X"), é **rápida** (microssegundos) e é **determinística** (a mesma entrada dá sempre a mesma saída — auditoria e reprodução de incidente agradecem).

Mas ela tem um limite estrutural: regra enxerga o que o autor da regra previu. O espaço de fraudes possíveis é combinatório — valor, horário, grafo de relacionamento entre contas, idade da conta, padrão de digitação, sequência de eventos — e o fraudador profissional testa esse espaço sistematicamente, como quem procura um vão na cerca. Cada regra nova que o Diego escreve fecha um vão e ilumina, para o fraudador, onde ficam os outros. É uma corrida em que a defesa se move por deploy e o ataque se move por tentativa.

Um modelo de classificação treinado sobre o histórico faz outra coisa: ele aprende a **superfície** que separa comportamento legítimo de fraudulento, em dezenas ou centenas de dimensões ao mesmo tempo. Ele não precisa que alguém tenha previsto "rajadas de R$ 49,90 na madrugada em contas novas" — ele aprende que aquela *combinação* de sinais (conta nova + rajada + valor repetido + horário + saque em sequência) está numa região do espaço onde fraude mora, mesmo que essa combinação exata nunca tenha aparecido no treino.

### 1.2 A regra de ouro: o modelo sugere, a regra decide

Agora, o ponto mais importante da aula inteira, e eu quero que vocês guardem antes de qualquer diagrama: **o modelo não decide nada. Nunca.** O modelo produz um número — um **score de risco**, digamos de 0 a 1000. Quem converte esse número em ação é uma **política de decisão**: uma tabela determinística, versionada, auditável, escrita por humanos e aprovada por humanos.

| Score | Valor da transação | Ação |
|---|---|---|
| 0–600 | qualquer | Segue o fluxo normal |
| 601–850 | até R$ 200 | Segue, marcada para revisão posterior |
| 601–850 | acima de R$ 200 | Desafio adicional (confirmação no app) |
| 851–1000 | qualquer | Bloqueia e abre caso para analista |
| *score indisponível* | até R$ 200 | Segue (fail-open com teto baixo) |
| *score indisponível* | acima de R$ 200 | Bloqueia (fail-closed) |

Reparem em três coisas nessa tabela. Primeiro, **as duas últimas linhas são as mais importantes** — elas dizem o que acontece quando o modelo *não responde*. Isso é o fallback fail-open/fail-closed que a gente desenhou na aula passada como decisão de negócio, e ele continua valendo com modelo no lugar: valor pequeno, o custo de errar é pequeno, deixa passar; valor grande, na dúvida, a regra do curso desde a Aula 1 — **falhar fechado**. Segundo, a tabela é *determinística*: dado o score e o valor, a ação é uma só. O componente não-determinístico do sistema fica cercado por componentes determinísticos dos dois lados — features determinísticas entram, política determinística sai. Terceiro, a tabela é um artefato versionado, como um ADR: quando o compliance perguntar "por que essa transação foi bloqueada em 3 de outubro?", a resposta é "score 912, política v14, linha 4" — e não "o modelo achou".

E aqui entra o motivo regulatório, que em fintech nunca é rodapé: a LGPD dá ao titular o direito de solicitar revisão de decisões tomadas unicamente com base em tratamento automatizado, e o BACEN espera que a instituição *explique* suas decisões de bloqueio. Reparem na palavra: explicar a **decisão**, não os pesos do modelo. Ninguém precisa explicar por que o neurônio 4.217 ativou. Precisa explicar "a política diz que score acima de 850 bloqueia, e o score veio de um modelo documentado, treinado sobre estes dados, com estas features". A separação modelo/política é o que torna isso possível. **Explicabilidade mora na política, não no modelo** — e é por isso que a política tem que existir como artefato separado.

### 1.3 Regra e modelo: camadas, não rivais

Fica a pergunta: então jogamos as regras fora? Não — e essa é a segunda coisa para guardar. O Antifraude do TechPix depois desta aula tem **três camadas**, na ordem em que uma transação as atravessa:

1. **Regras duras** (microssegundos): lista de bloqueio, conta encerrada, limite regulatório estourado. Coisas que são proibidas por definição, onde não existe "score" — existe não. Rodam primeiro justamente porque são baratas: transação barrada aqui nem chega ao modelo.
2. **Modelo** (dezenas de milissegundos): o score de risco sobre tudo que passou pelas regras duras.
3. **Política de decisão** (microssegundos): a tabela que converte score + contexto em ação.

Regra pega o proibido; modelo pega o suspeito; política decide o que fazer com a suspeita. Cada camada faz o que faz melhor, e a auditoria atravessa as três.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a5cam-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a5cam-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <rect x="15" y="95" width="90" height="44" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="60" y="121" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">transação</text>
  <line x1="105" y1="117" x2="140" y2="117" stroke="#4338ca" stroke-width="2" marker-end="url(#a5cam-arrow)"/>
  <!-- camada 1 -->
  <rect x="145" y="85" width="160" height="66" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="225" y="107" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">1 · Regras duras</text>
  <text x="225" y="124" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">listas, limites regulatórios</text>
  <text x="225" y="140" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">determinística · ~1 ms</text>
  <line x1="225" y1="151" x2="225" y2="185" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="225" y="203" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">proibido → barra aqui,</text>
  <text x="225" y="217" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">nem chega ao modelo</text>
  <line x1="305" y1="117" x2="340" y2="117" stroke="#4338ca" stroke-width="2" marker-end="url(#a5cam-arrow)"/>
  <!-- camada 2 -->
  <rect x="345" y="85" width="170" height="66" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="430" y="107" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">2 · Modelo</text>
  <text x="430" y="124" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">não-determinístico</text>
  <text x="430" y="140" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">score 0–1000 · 10–20 ms</text>
  <line x1="515" y1="117" x2="550" y2="117" stroke="#4338ca" stroke-width="2" marker-end="url(#a5cam-arrow)"/>
  <text x="532" y="105" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">score</text>
  <!-- camada 3 -->
  <rect x="555" y="85" width="180" height="66" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="645" y="107" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">3 · Política de decisão</text>
  <text x="645" y="124" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">tabela score × valor → ação</text>
  <text x="645" y="140" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">determinística, versionada (v14)</text>
  <!-- ações -->
  <line x1="735" y1="100" x2="775" y2="60" stroke="#166534" stroke-width="2" marker-end="url(#a5cam-g)"/>
  <rect x="780" y="42" width="105" height="32" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="832" y="62" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">segue ✓</text>
  <line x1="735" y1="117" x2="775" y2="117" stroke="#d4a017" stroke-width="2" marker-end="url(#a5cam-arrow)"/>
  <rect x="780" y="101" width="105" height="32" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="832" y="121" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">desafio no app</text>
  <line x1="735" y1="135" x2="775" y2="175" stroke="#b91c1c" stroke-width="2" marker-end="url(#a5cam-g)"/>
  <rect x="780" y="160" width="105" height="32" rx="6" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="832" y="180" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">bloqueia + caso</text>
  <!-- trilha de auditoria -->
  <rect x="145" y="240" width="590" height="40" rx="8" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="440" y="258" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Trilha de auditoria atravessa as três camadas: versão do modelo + versão da política + score + ação + EndToEndId</text>
  <text x="440" y="274" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">"Por que bloqueou?" → "score 912, política v14, linha 4" — nunca "o modelo achou"</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O modelo sugere, a regra decide: o componente não-determinístico fica cercado por camadas determinísticas dos dois lados.</p>
</div>

---

## 2. A arquitetura da inferência em tempo real

### 2.1 O orçamento: 100 milissegundos, e ninguém rouba fatia

Vamos voltar ao orçamento, porque em fintech tudo começa e termina nele. Desde a Aula 1 a gente sabe: teto normativo de 40 segundos, experiência-alvo de poucos segundos, SPI consumindo p50 de 2,8s e p99 de 4,6s, DICT com p99 de 1s. Na aula passada, quando a gente escreveu o Contrato de Integração, a aresta Pagamentos→Antifraude ficou com **~100 ms de orçamento no p99**, chamada síncrona, porque a decisão de risco tem que acontecer *antes* de reservar fundos — depois que o SPI liquidou, é irrevogável, e aí só resta o MED.

Cem milissegundos. Dentro disso precisa caber: a chamada de rede (ida e volta), a montagem das features, a inferência do modelo, a avaliação da política. Vamos fazer a conta de guardanapo que esse curso adora:

```
Orçamento p99 da aresta Pagamentos → Antifraude ≈ 100 ms
  ├─ rede (gRPC interno, ida+volta)        ~5 ms
  ├─ regras duras                          ~1 ms
  ├─ busca de features (online store)      ~10–15 ms   ← o vilão silencioso
  ├─ inferência do modelo                  ~10–20 ms
  ├─ política de decisão                   ~1 ms
  └─ folga para p99 (GC, fila, azar)       ~60 ms
```

Duas observações de quem já carregou pager. Primeira: a folga não é gordura — é o que separa o p50 do p99. Um sistema que gasta 40 ms no caso típico estoura 100 ms no p99 com facilidade assustadora: uma pausa de garbage collector, um pico de fila, um cache frio. Se o seu caso típico já come 80 do orçamento de 100, o seu p99 mora em violação. Segunda: reparem que **a inferência não é a fatia maior**. O modelo de score de fraude do TechPix não é um modelo de linguagem gigante — é um classificador especializado (pensem numa floresta de árvores de decisão turbinada, ou numa rede pequena), treinado em casa, que roda em 10–20 ms numa CPU ou numa GPU modesta. A fatia perigosa é a de cima: **as features**.

### 2.2 Feature store: o rio de eventos vira alimento do modelo

Uma feature é um sinal que o modelo consome: "quantos Pix essa conta recebeu na última hora", "idade da conta em dias", "valor médio recebido nos últimos 30 dias", "quantas contas distintas enviaram para ela hoje". E aqui mora a decisão de arquitetura mais bonita da aula, porque ela amarra tudo que o curso construiu.

Pensem no que a feature "número de Pix recebidos na última hora" exige: ela precisa estar **pronta** — pré-calculada, atualizada, a uma consulta de milissegundos — no momento em que a transação chega. Não dá para varrer o ledger contando lançamentos com a transação esperando: isso é exatamente o tipo de leitura pesada no caminho de escrita que causou o incidente do dia 5 na Aula 2. A resposta tem nome: **feature store**, um armazenamento de duas caras.

- A **loja offline** guarda o histórico profundo — meses de features, com carimbo de tempo — e serve o *treinamento* do modelo. Latência de minutos? Irrelevante. Volume? Enorme.
- A **loja online** guarda só o valor *atual* de cada feature por conta — num armazenamento chave-valor rápido — e serve a *inferência*. Latência exigida: poucos milissegundos no p99. Volume por consulta: minúsculo.

E quem alimenta as duas? Reparem: **os mesmos eventos do Outbox da Aula 2.** `PixLiquidado` sai do ledger pela outbox, e um consumidor — idempotente, com dedup por EndToEndId, exatamente como a gente especificou na Aula 4 — incrementa os agregados da loja online ("recebidos na última hora +1") e apenda o registro na loja offline. O rio de eventos que o professor anterior desenhou com vocês no event storming da Aula 3 virou, literalmente, o alimento do modelo. Nenhuma peça nova de infraestrutura conceitual: é CQRS de novo — a loja online é mais um *read model*, só que quem lê não é o extrato da Ana, é o modelo do Diego.

Isso traz junto uma consequência honesta que eu não vou esconder: a loja online tem **atraso eventual**, como todo read model — os mesmos 100 a 300 ms de sempre, às vezes mais se o consumer lag crescer (e vocês lembram da aula passada: consumer lag é métrica de primeira classe). O modelo pode decidir sobre uma foto das features com algumas centenas de milissegundos de idade. Para contagem de "última hora", irrelevante. Mas guardem a implicação: **quem ataca em rajada de segundos explora exatamente essa janela** — e é por isso que as regras duras da camada 1, que consultam contadores transacionais simples, continuam existindo na frente do modelo. Camada rápida e burra na frente; camada lenta e esperta atrás. Defesa em profundidade não é só para segurança de rede.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 430" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a5inf-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a5inf-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <!-- caminho crítico -->
  <text x="20" y="24" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Caminho crítico (síncrono) — orçamento da aresta: 100 ms p99</text>
  <rect x="20" y="40" width="130" height="50" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="85" y="70" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Pagamentos</text>
  <line x1="150" y1="65" x2="205" y2="65" stroke="#4338ca" stroke-width="2" marker-end="url(#a5inf-arrow)"/>
  <text x="177" y="55" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">gRPC ~5ms</text>
  <!-- antifraude -->
  <rect x="210" y="35" width="560" height="115" rx="10" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="490" y="55" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Antifraude e Limites</text>
  <rect x="225" y="70" width="110" height="60" rx="6" fill="#f3f4f6" stroke="#999"/>
  <text x="280" y="96" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">regras duras</text>
  <text x="280" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">~1 ms</text>
  <line x1="335" y1="100" x2="360" y2="100" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a5inf-arrow)"/>
  <rect x="365" y="70" width="130" height="60" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="430" y="90" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">busca de features</text>
  <text x="430" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">loja online · 10–15 ms</text>
  <text x="430" y="122" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#b45309">← o vilão silencioso</text>
  <line x1="495" y1="100" x2="520" y2="100" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a5inf-arrow)"/>
  <rect x="525" y="70" width="120" height="60" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="585" y="90" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">inferência (GPU)</text>
  <text x="585" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">modelo v3 · 10–20 ms</text>
  <line x1="645" y1="100" x2="670" y2="100" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a5inf-arrow)"/>
  <rect x="675" y="70" width="80" height="60" rx="6" fill="#f3f4f6" stroke="#999"/>
  <text x="715" y="96" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">política</text>
  <text x="715" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">~1 ms</text>
  <text x="815" y="100" font-family="sans-serif" font-size="11" fill="#666">+ ~60 ms de</text>
  <text x="815" y="115" font-family="sans-serif" font-size="11" fill="#666">folga p/ p99</text>
  <!-- rio de eventos -->
  <text x="20" y="195" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Quem alimenta as features: o rio de eventos (assíncrono)</text>
  <rect x="20" y="210" width="150" height="54" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="95" y="232" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Ledger + Outbox</text>
  <text x="95" y="250" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">PixLiquidado (Aula 2)</text>
  <line x1="170" y1="237" x2="230" y2="237" stroke="#888" stroke-width="2" marker-end="url(#a5inf-gray)"/>
  <rect x="235" y="210" width="170" height="54" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="320" y="232" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">consumidor idempotente</text>
  <text x="320" y="250" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">dedup por E2E ID (Aula 4)</text>
  <line x1="405" y1="225" x2="465" y2="225" stroke="#888" stroke-width="2" marker-end="url(#a5inf-gray)"/>
  <line x1="405" y1="252" x2="465" y2="290" stroke="#888" stroke-width="2" marker-end="url(#a5inf-gray)"/>
  <!-- loja online -->
  <rect x="470" y="200" width="180" height="54" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="560" y="222" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7a5c00">loja ONLINE (chave-valor)</text>
  <text x="560" y="240" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">valor atual · leitura em ms</text>
  <line x1="560" y1="200" x2="450" y2="135" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a5inf-gray)"/>
  <text x="530" y="168" font-family="sans-serif" font-size="10" fill="#b45309">serve a inferência</text>
  <!-- loja offline -->
  <rect x="470" y="272" width="180" height="54" rx="8" fill="#f3f4f6" stroke="#999" stroke-width="2"/>
  <text x="560" y="294" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">loja OFFLINE (histórico)</text>
  <text x="560" y="312" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">meses de features · serve o treino</text>
  <line x1="650" y1="299" x2="700" y2="299" stroke="#888" stroke-width="2" marker-end="url(#a5inf-gray)"/>
  <rect x="705" y="272" width="175" height="54" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="792" y="294" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">treino (GPU elástica)</text>
  <text x="792" y="312" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">semanal/mensal · horas</text>
  <line x1="792" y1="272" x2="792" y2="245" stroke="#888" stroke-width="1.5" marker-end="url(#a5inf-gray)"/>
  <rect x="705" y="200" width="175" height="44" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="792" y="218" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">registro de modelos</text>
  <text x="792" y="234" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">pesos congelados, versionados</text>
  <line x1="705" y1="215" x2="620" y2="140" stroke="#4338ca" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a5inf-arrow)"/>
  <text x="690" y="170" font-family="sans-serif" font-size="10" fill="#4338ca">promove v3 →</text>
  <!-- nota -->
  <rect x="20" y="370" width="860" height="40" rx="8" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="450" y="388" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">CQRS de novo: a loja online é mais um read model (atraso eventual de 100–300 ms) — quem lê não é o extrato da Ana, é o modelo do Diego.</text>
  <text x="450" y="404" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Treino e inferência: mundos separados, ligados por um artefato versionado.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Inferência em tempo real: o caminho crítico de 100 ms em cima, alimentado pelo rio de eventos assíncrono embaixo.</p>
</div>

### 2.3 Treino e inferência: dois mundos, um artefato

Uma confusão que eu quero desfazer agora, porque ela custa caro em reunião de planejamento: **treinar** um modelo e **servir** um modelo são workloads tão diferentes quanto relatório mensal e caminho crítico do Pix.

| | Treinamento | Inferência online |
|---|---|---|
| Quando | De tempos em tempos (semanal, mensal, sob demanda) | 24/7, a cada transação |
| Dados | Meses de histórico (loja offline) | Uma transação + features online |
| Latência | Horas — ninguém espera | ~10–20 ms dentro de orçamento de 100 |
| Hardware | GPU parruda, elástica, pode ser spot | CPU/GPU dedicada, dimensionada para o pico de 900 TPS |
| Falha | Refaz amanhã | Fallback fail-closed AGORA |

O que liga os dois mundos é um artefato: o modelo versionado — os pesos, congelados, com um número de versão, guardados num registro de modelos. O treino *produz* versões; a inferência *serve exatamente uma* versão, conhecida, auditável. "Qual modelo decidiu essa transação?" tem que ter resposta tão precisa quanto "qual versão do código estava em produção?" — porque para o auditor é a mesma pergunta.

E um aviso de arquiteto: essa separação é o motivo pelo qual o Antifraude está virando um serviço com **perfil de escala próprio** — GPU, dimensionamento pelo pico de TPS, ciclo de deploy do modelo separado do ciclo do código. O professor da Aula 3 já tinha apontado o Antifraude como candidato a escala diferente. Segurem essa: na aula que vem, ela decide quem sai do monólito primeiro.

---

## 3. Modelos abertos vs. API: onde o peso mora importa

Até aqui, o modelo de score é pequeno, especializado, treinado em casa — essa questão nem se coloca. Mas o TechPix quer mais: resumir o histórico de um caso de fraude em linguagem natural, analisar a narrativa de uma comunicação de PLD-FT, montar dossiês. Isso pede modelo de linguagem — e aí surge a pergunta que hoje toda fintech enfrenta: **usar um modelo por API (pesos na nuvem de terceiro) ou rodar um modelo aberto (pesos na sua infra)?**

"Modelo aberto" — ou de **pesos abertos** — é um modelo cujos pesos você baixa e executa onde quiser: a família Llama e afins. A decisão entre ele e uma API não é ideológica; é uma tabela de trade-offs, e como sempre nesse curso, a resposta depende de *qual pedaço do sistema* está perguntando:

| Critério | Modelo aberto, na sua infra | API de terceiro |
|---|---|---|
| **Dado sensível (LGPD)** | Não sai de casa. CPF, chave Pix, grafo de contas — tudo dentro do seu perímetro | Dado trafega para fora; exige contrato, anonimização, base legal — e ainda assim é superfície de risco |
| **Latência** | Previsível; você controla a fila e o hardware | Boa na média; o p99 depende de rede e da fila *dos outros* |
| **Custo em escala** | Custo fixo alto (GPU, operação), custo marginal baixo — a 900 TPS de pico, escala a favor | Custo por chamada; em volume de núcleo, a conta explode |
| **Capacidade bruta** | Menor que os melhores modelos de fronteira | Estado da arte |
| **Operação** | Sua: deploy, monitoramento, atualização de versão | Deles: você herda as mudanças, inclusive as que não pediu |

A política do TechPix, que eu recomendo como padrão de mercado para fintech: **núcleo com dado sensível → modelo aberto, dentro de casa; borda sem dado sensível → API pode.** O copiloto que resume casos de fraude lê CPF, chave, extrato — roda dentro. Um assistente que reescreve texto de notificação genérica — pode ser API. É a mesma lógica de "forte no núcleo, eventual na borda" da Aula 1, transplantada: a fronteira não é técnica, é de *sensibilidade do dado e criticidade da decisão*.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a5peso-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
    <marker id="a5peso-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <!-- dentro de casa -->
  <rect x="20" y="30" width="400" height="230" rx="12" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="220" y="55" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">Modelo aberto — dentro do perímetro</text>
  <rect x="45" y="75" width="160" height="70" rx="8" fill="#fff" stroke="#166534" stroke-width="1.5"/>
  <text x="125" y="97" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">dado sensível</text>
  <text x="125" y="113" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">CPF · chave Pix · grafo</text>
  <text x="125" y="129" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">não sai de casa ✓ (LGPD)</text>
  <line x1="205" y1="110" x2="245" y2="110" stroke="#166534" stroke-width="2" marker-end="url(#a5peso-g)"/>
  <rect x="250" y="75" width="145" height="70" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="322" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">pesos abertos</text>
  <text x="322" y="116" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">(Llama e afins) na sua GPU</text>
  <text x="322" y="132" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">quantizado/destilado</text>
  <g font-family="sans-serif" font-size="11" fill="#166534">
    <text x="45" y="180">✓ latência previsível (a fila é sua)</text>
    <text x="45" y="202">✓ custo fixo alto, marginal baixo — a 900 TPS, escala a favor</text>
    <text x="45" y="224">− capacidade menor que a fronteira · operação é sua</text>
  </g>
  <!-- fora -->
  <rect x="460" y="30" width="400" height="230" rx="12" fill="#fff" stroke="#999" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="660" y="55" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">API de terceiro — fora do perímetro</text>
  <rect x="485" y="75" width="150" height="70" rx="8" fill="#fff" stroke="#999" stroke-width="1.5"/>
  <text x="560" y="102" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">dado da requisição</text>
  <text x="560" y="120" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">trafega para fora</text>
  <line x1="635" y1="110" x2="690" y2="110" stroke="#b91c1c" stroke-width="2" marker-end="url(#a5peso-red)"/>
  <text x="662" y="98" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">⚠</text>
  <rect x="695" y="75" width="140" height="70" rx="8" fill="#f3f4f6" stroke="#999" stroke-width="1.5"/>
  <text x="765" y="102" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">nuvem do fornecedor</text>
  <text x="765" y="120" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">estado da arte</text>
  <g font-family="sans-serif" font-size="11" fill="#555">
    <text x="485" y="180">− p99 depende da rede e da fila dos outros</text>
    <text x="485" y="202">− custo por chamada: em volume de núcleo, a conta explode</text>
    <text x="485" y="224">− contrato, anonimização, base legal — superfície de risco</text>
  </g>
  <!-- regra -->
  <rect x="20" y="280" width="840" height="34" rx="8" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="440" y="302" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#3730a3">A política do TechPix: núcleo com dado sensível → modelo aberto, dentro de casa · borda sem dado sensível → API pode. "Forte no núcleo, eventual na borda", transplantado.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Onde o peso mora importa: a fronteira se decide pela sensibilidade do dado e pela criticidade da decisão, não pela moda.</p>
</div>

Dois termos de engenharia para o glossário, porque vocês vão esbarrar neles na primeira conversa de infra: **quantização** — representar os pesos do modelo com menos bits, trocando um pouco de qualidade por muito menos memória e mais velocidade — e **destilação** — treinar um modelo pequeno para imitar um grande, ficando com um especialista barato no lugar de um generalista caro. São os dois botões que fazem um modelo aberto caber no seu orçamento de latência e de GPU. O detalhe de como treinar não é assunto deste curso; *saber que esses botões existem* é, porque eles mudam a conta de capacidade.

---

## 4. Shadow mode: o medo certo, na dose certa

### 4.1 Como se coloca um modelo em produção sem coragem

Agora a pergunta que separa quem já operou sistema financeiro de quem não: o modelo do Diego está treinado, os testes offline mostram métricas bonitas. A gente liga ele na política de decisão amanhã?

Não. E a resposta tem método, não é só medo. O modelo entra em **shadow mode** — modo sombra: ele recebe **tráfego real**, calcula o score **de verdade**, e a decisão dele é... **ignorada**. Registrada, carimbada, guardada — e ignorada. Quem continua decidindo é o sistema anterior (as regras). Durante semanas, cada transação gera dois vereditos: o real (regras) e o hipotético (modelo). E aí a comparação vira o instrumento mais poderoso da aula:

- Onde o modelo **concorda** com as regras: ótimo, confiança acumulando.
- Onde o modelo bloquearia e a regra deixou passar: cada caso vai para análise humana. Era fraude que escapou? Ponto para o modelo. Era cliente legítimo? **Falso positivo** — e falso positivo em pagamento é cliente com Pix travado às 2h da manhã, ligando furioso; em fintech, falso positivo é incidente de confiança, não é estatística.
- Onde a regra bloquearia e o modelo deixaria passar: o modelo está cego para algo que a regra enxerga? Ou a regra está ultrapassada?

E aqui a história fecha o círculo com uma ironia que eu fiz questão de trazer: quando o time rodou o modelo em sombra sobre o histórico de setembro, **o golpe dos R$ 49,90 acendeu vermelho retroativamente**. As contas laranja daquela madrugada apareceram com scores altíssimos — a combinação conta-nova + rajada + valor-repetido + madrugada estava exatamente na região do espaço que o modelo aprendeu a temer. O golpe que atravessou todas as regras não teria atravessado o modelo. Isso não prova que o modelo pega o *próximo* golpe — guardem essa honestidade — mas prova que ele enxerga uma classe de padrão que regra nenhuma cobria.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 320" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a5sh-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a5sh-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <rect x="20" y="105" width="130" height="50" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="85" y="135" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">tráfego real</text>
  <!-- split -->
  <line x1="150" y1="120" x2="230" y2="70" stroke="#4338ca" stroke-width="2" marker-end="url(#a5sh-arrow)"/>
  <line x1="150" y1="140" x2="230" y2="205" stroke="#888" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#a5sh-gray)"/>
  <text x="185" y="180" font-family="sans-serif" font-size="10" fill="#888">cópia</text>
  <!-- caminho real -->
  <rect x="235" y="40" width="170" height="60" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="320" y="63" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Regras (ativo)</text>
  <text x="320" y="82" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">decide DE VERDADE</text>
  <line x1="405" y1="70" x2="480" y2="70" stroke="#166534" stroke-width="2" marker-end="url(#a5sh-arrow)"/>
  <rect x="485" y="45" width="120" height="50" rx="8" fill="#fff" stroke="#166534" stroke-width="1.5"/>
  <text x="545" y="75" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">ação executada</text>
  <!-- caminho sombra -->
  <rect x="235" y="175" width="170" height="60" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="320" y="198" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Modelo (sombra)</text>
  <text x="320" y="217" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">decide "de mentira"</text>
  <line x1="405" y1="205" x2="480" y2="205" stroke="#888" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#a5sh-gray)"/>
  <rect x="485" y="180" width="120" height="50" rx="8" fill="#fff" stroke="#999" stroke-width="1.5" stroke-dasharray="6 4"/>
  <text x="545" y="200" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">score logado,</text>
  <text x="545" y="217" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">decisão IGNORADA</text>
  <!-- comparação -->
  <line x1="605" y1="70" x2="660" y2="130" stroke="#166534" stroke-width="1.5" marker-end="url(#a5sh-arrow)"/>
  <line x1="605" y1="205" x2="660" y2="150" stroke="#888" stroke-width="1.5" marker-end="url(#a5sh-gray)"/>
  <rect x="655" y="105" width="205" height="120" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="757" y="128" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Comparação (semanas)</text>
  <g font-family="sans-serif" font-size="10" fill="#7a5c00">
    <text x="668" y="150">concordam → confiança ✓</text>
    <text x="668" y="170">só o modelo bloquearia →</text>
    <text x="678" y="185">fraude nova ou falso positivo?</text>
    <text x="668" y="205">só a regra bloquearia →</text>
    <text x="678" y="220">modelo cego ou regra velha?</text>
  </g>
  <line x1="757" y1="225" x2="757" y2="255" stroke="#d4a017" stroke-width="1.5" marker-end="url(#a5sh-gray)"/>
  <rect x="672" y="258" width="170" height="34" rx="8" fill="#fff" stroke="#d4a017" stroke-width="1.5"/>
  <text x="757" y="280" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">análise humana caso a caso</text>
  <text x="230" y="290" font-family="sans-serif" font-size="11" fill="#666">Promoção gradual: primeiro só valores baixos, depois subindo — regras duras sempre na frente, política sempre no comando.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Shadow mode: o modelo paga o aluguel da confiança — tráfego real, decisão registrada e ignorada, comparação antes da promoção.</p>
</div>

### 4.2 Sombra é o ensaio geral da entrega progressiva

Reparem no desenho geral, porque ele vai reaparecer: rodar a mudança nova **ao lado** da antiga, com tráfego real, comparando resultados, antes de dar a ela o poder de decidir. Semana que vem, quando a gente for extrair serviços do monólito e falar de canary — a mudança nova recebendo primeiro 1% do tráfego, depois 5%, depois mais — vocês vão reconhecer o parentesco na hora. Shadow mode é o canary do componente não-determinístico: como não dá para ler o código do modelo num code review, a única revisão possível é **comportamental** — observar o que ele faz com a realidade, em volume, antes de deixá-lo tocar a realidade. Eu chamo isso de pagar o aluguel da confiança: modelo não entra no caminho crítico por ter métricas bonitas em laboratório; entra por ter semanas de comportamento observado em produção.

A transição final no TechPix foi gradual até o fim: o modelo começou decidindo só a faixa de valores baixos (onde errar é barato), depois foi subindo, com as regras duras sempre na frente e a política sempre no comando. Em nenhum momento existiu um dia "liguem o modelo". Existiu um processo de semanas em que a confiança migrou, medida a medida.

E fica uma pergunta armada para daqui a duas aulas: em sombra, comparando com as regras, a gente sabia se o modelo estava bom. E *depois*, quando ele é quem decide e as semanas passam e o mundo muda — o fraudador se adapta, o perfil de cliente muda, chega o 13º salário — **como saber se o modelo continua bom?** Um modelo não quebra com stack trace. Guardem essa inquietação; ela tem nome, e a Aula 7 vai dar o nome e o instrumento.

---

## 5. O outro lado do balcão: MCP e o suporte à decisão humana

### 5.1 A manhã da Carla

Até aqui, IA decidindo *sob* uma política, em milissegundos, sobre transações. Agora deixa eu apresentar a **Carla**, analista sênior de fraude do TechPix, porque o dia dela mostra o outro lugar — talvez o mais imediatamente valioso — onde essa tecnologia entra numa fintech.

Quando o modelo (ou uma regra, ou o MED) abre um caso, é a Carla quem decide: bloqueia a conta? Devolve o dinheiro? Reporta às autoridades? E para decidir *um* caso, a Carla de setembro abria seis telas: o histórico de transações da conta, o cadastro no Identidade e Onboarding, o grafo de contas relacionadas (quem mandou para quem — o mesmo grafo da Recuperação de Valores da Aula 1), os casos anteriores parecidos, a fila do MED, a tela de marcações do DICT. Vinte minutos juntando contexto, cinco decidindo. A Carla não tem um problema de julgamento — tem um problema de *montagem de contexto*. E montagem de contexto é exatamente o que um modelo de linguagem com acesso a ferramentas faz bem.

### 5.2 O copiloto, e por que o MCP importa aqui

O TechPix montou para a Carla um **copiloto**: um assistente baseado num modelo de linguagem (aberto, rodando dentro de casa — seção 3 aplicada) que, quando um caso abre, consulta os sistemas, monta o dossiê — "conta aberta há 23 dias, recebeu 340 Pix de R$ 49,90 entre 2h31 e 2h58, padrão compatível com os 3 casos do lote de outubro, grafo liga a 2 contas já marcadas no DICT" — e **sugere** uma classificação, com as evidências citadas uma a uma.

Como o copiloto se conecta aos sistemas? Aqui volta uma sigla que o professor da Aula 1 plantou: **MCP, o Model Context Protocol** — o protocolo aberto, criado pela Anthropic, que padroniza como um modelo acessa ferramentas e dados. Em vez de N integrações artesanais entre o copiloto e cada sistema interno, cada contexto expõe um servidor MCP com ferramentas nomeadas: o Contas e Ledger expõe `consultar_historico`, o Antifraude expõe `casos_similares` e `grafo_de_contas`, o Devoluções e Disputas expõe `status_med`. O copiloto enxerga um cardápio de ferramentas tipadas — e o cardápio é a fronteira.

E agora a frase mais importante desta seção, que é a aplicação direta da regra de ouro da Aula 1 — "o agente lê, propõe, mas nunca move dinheiro": **no cardápio do copiloto da Carla, não existe ferramenta de escrita.** Não existe `bloquear_conta`. Não existe `devolver_pix`. Não é que o copiloto foi *instruído* a não bloquear — é que a ferramenta **não existe** no conjunto que os servidores MCP expõem a ele. A fronteira de permissão não é um pedido educado no prompt; é **ausência estrutural de capacidade**. Eu chamo isso de fronteira de permissão por ausência, e quero que vocês levem como princípio de projeto: a maneira mais confiável de garantir que um sistema não-determinístico não faça X é não dar a ele o instrumento de fazer X. Quem clica em "bloquear" é a Carla — no sistema dela, autenticada como ela, auditada como ela.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 360" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a5mcp-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a5mcp-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <text x="20" y="24" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Servidores MCP — só ferramentas de LEITURA</text>
  <g font-family="sans-serif">
    <rect x="20" y="40" width="200" height="52" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
    <text x="120" y="61" text-anchor="middle" font-size="11" fill="#333">Contas e Ledger</text>
    <text x="120" y="79" text-anchor="middle" font-size="10" fill="#4338ca">consultar_historico()</text>
    <rect x="20" y="104" width="200" height="66" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
    <text x="120" y="125" text-anchor="middle" font-size="11" fill="#333">Antifraude</text>
    <text x="120" y="143" text-anchor="middle" font-size="10" fill="#4338ca">casos_similares()</text>
    <text x="120" y="159" text-anchor="middle" font-size="10" fill="#4338ca">grafo_de_contas()</text>
    <rect x="20" y="182" width="200" height="52" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
    <text x="120" y="203" text-anchor="middle" font-size="11" fill="#333">Devoluções e Disputas</text>
    <text x="120" y="221" text-anchor="middle" font-size="10" fill="#4338ca">status_med()</text>
  </g>
  <line x1="220" y1="66" x2="330" y2="120" stroke="#4338ca" stroke-width="2" marker-end="url(#a5mcp-arrow)"/>
  <line x1="220" y1="137" x2="330" y2="137" stroke="#4338ca" stroke-width="2" marker-end="url(#a5mcp-arrow)"/>
  <line x1="220" y1="208" x2="330" y2="155" stroke="#4338ca" stroke-width="2" marker-end="url(#a5mcp-arrow)"/>
  <text x="275" y="115" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">leitura</text>
  <!-- copiloto -->
  <rect x="335" y="95" width="200" height="90" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="435" y="120" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Copiloto</text>
  <text x="435" y="139" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">modelo aberto, roda dentro</text>
  <text x="435" y="155" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">monta o dossiê do caso</text>
  <text x="435" y="171" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">com evidências linkadas</text>
  <!-- ferramenta inexistente -->
  <rect x="345" y="215" width="180" height="44" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="5 4"/>
  <text x="435" y="234" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">bloquear_conta()</text>
  <text x="435" y="250" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">NÃO EXISTE no cardápio</text>
  <line x1="360" y1="222" x2="510" y2="252" stroke="#b91c1c" stroke-width="2"/>
  <line x1="360" y1="252" x2="510" y2="222" stroke="#b91c1c" stroke-width="2"/>
  <!-- sugestão → Carla -->
  <line x1="535" y1="140" x2="620" y2="140" stroke="#4338ca" stroke-width="2" marker-end="url(#a5mcp-arrow)"/>
  <text x="577" y="128" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">sugere + evidências</text>
  <rect x="625" y="100" width="150" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="700" y="130" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">Carla</text>
  <text x="700" y="150" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">analista sênior</text>
  <text x="700" y="166" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">DECIDE</text>
  <line x1="775" y1="140" x2="835" y2="140" stroke="#166534" stroke-width="2" marker-end="url(#a5mcp-g)"/>
  <rect x="790" y="180" width="105" height="0" fill="none"/>
  <rect x="800" y="105" width="0" height="0" fill="none"/>
  <rect x="838" y="112" width="55" height="56" rx="8" fill="#fff" stroke="#166534" stroke-width="1.5"/>
  <text x="865" y="135" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">bloqueia</text>
  <text x="865" y="150" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">no sistema</text>
  <text x="865" y="162" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">DELA</text>
  <!-- nota -->
  <rect x="20" y="290" width="860" height="52" rx="8" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="450" y="311" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Fronteira de permissão por ausência: o copiloto não foi "instruído" a não bloquear — a ferramenta de escrita não existe no conjunto exposto a ele.</text>
  <text x="450" y="330" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Montagem de contexto: 20 min → 2 min. A decisão continua da Carla — LGPD, regulador e qualidade agradecem. (Agente sobre a arquitetura: Aula 8.)</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O copiloto da Carla via MCP: lê tudo, sugere com evidências, não executa nada — quem clica em "bloquear" é a humana, auditada como ela.</p>
</div>

O resultado operacional: a montagem de contexto caiu de vinte minutos para dois. A decisão continua custando os mesmos cinco — e continua sendo da Carla, o que importa para o regulador, para a LGPD (revisão humana em decisão que afeta o titular) e, francamente, para a qualidade: a Carla pega alucinação do copiloto do mesmo jeito que revisor pega erro em code review. O copiloto errar uma citação de evidência é um constrangimento; a Carla poder verificar cada citação — porque o dossiê linka as fontes — é o que torna o constrangimento inofensivo.

### 5.3 A porta que eu não vou abrir hoje

Antes de fechar, deixa eu marcar explicitamente uma fronteira do curso, porque eu sei que alguns de vocês já estão fazendo a extrapolação: "se o copiloto lê os sistemas e sugere decisões sobre *casos*... por que não um agente que lê as *métricas de produção* e as *specs* e sugere decisões sobre a *arquitetura*?"

Essa extrapolação está certa — e ela é exatamente o destino final deste curso. Um agente participando da evolução da arquitetura, lendo produção e propondo mudanças estruturais sob validação, é a matéria da **Aula 8**, quando o professor das primeiras aulas volta para fechar o círculo que abriu ("da fé à evidência", lembram?). O que eu quero que vocês levem de hoje é que os fundamentos já estão todos na mesa: fronteira de permissão por ausência, leitura sem escrita, humano decidindo o irreversível, comportamento observado antes de confiança concedida. A Aula 8 não vai inventar princípios novos — vai aplicar estes, num alvo mais ambicioso.

---

## 6. O artefato: Model Card + Política de Decisão

Toda aula deste curso termina registrando a decisão num artefato — o professor anterior deixou vocês treinados nisso com os ADRs e com a spec de Pagamentos da Aula 3. Hoje o artefato é o par que governa o componente não-determinístico: o **Model Card**, que documenta o modelo, e a **Política de Decisão**, que documenta o que se faz com a saída dele. Não é um ADR numerado — o próximo ADR numerado, o 003, só nasce quando alguém decidir mexer na escrita do ledger, e hoje não é esse dia. É o irmão não-determinístico da spec da Aula 3:

```
MODEL CARD — modelo-risco-pix                    versão 3 · out/2025
Propósito       Score de risco de fraude (0–1000) por transação Pix,
                consumido exclusivamente pela Política de Decisão v14.
O que o modelo  Features de comportamento transacional (valor, frequência,
vê              horários, grafo de contas, idade e histórico da conta) —
                lista completa e versionada no anexo A.
O que o modelo  Raça, gênero, e QUALQUER proxy geográfico fino (CEP) —
NUNCA vê        vetado por política de não-discriminação; auditado a cada
                versão por checagem automática da lista de features.
Treinamento     Histórico rotulado da loja offline; janela de 18 meses;
                retreino mensal ou sob incidente.
Desempenho      Latência de inferência p99 ≤ 20 ms; avaliação de qualidade
                comparada em sombra antes de cada promoção de versão.
Fallback        Score indisponível → Política de Decisão, linhas 5–6
                (fail-open ≤ R$200; fail-closed acima).
Auditoria       Toda inferência loga: versão do modelo, versão da política,
                score, ação, EndToEndId. Retenção conforme BACEN/LGPD.
Limites         O modelo NÃO decide; NÃO bloqueia; NÃO enxerga transações
conhecidos      fora do Pix; degrada sob mudança de comportamento do
                tráfego (monitoramento: Aula 7).
Donos           Modelo: time Antifraude (Diego) · Política: risco + negócio
                · Revisão humana de casos: equipe da Carla.
```

Reparem na linha "O que o modelo NUNCA vê", porque ela é a mais fácil de esquecer e a mais cara de esquecer. Um modelo treinado sobre dados históricos aprende os vieses dos dados históricos — e CEP, no Brasil, é um proxy social afiadíssimo. Vetar a feature na entrada, com checagem automática na lista de features a cada versão (uma fitness function, no vocabulário da Aula 2 — a mesma ideia, apontada para um alvo novo), é mais barato e mais auditável do que tentar provar estatisticamente, depois, que o modelo não discrimina. Não resolve o problema inteiro — proxy de proxy existe, e auditoria de viés é disciplina própria — mas estabelece o princípio: **a lista de features é uma decisão de governança, não um detalhe de engenharia.**

---

## 7. Para fechar: as três âncoras

Recapitulando o que não pode sair da cabeça de vocês:

Primeiro: **o modelo sugere, a regra decide.** O componente não-determinístico produz um número; quem converte número em ação é uma política determinística, versionada, auditável. Explicabilidade mora na política. Fail-closed continua sendo a lei do valor alto — com modelo ou sem.

Segundo: **inferência em tempo real é um problema de orçamento, e a feature store é o coração dele.** O modelo cabe em 100 ms porque as features já estão prontas — alimentadas pelo mesmo rio de eventos que este curso vem construindo desde o Outbox da Aula 2. Treino e inferência são mundos separados ligados por um artefato versionado. E onde o peso do modelo mora — dentro de casa ou numa API — se decide pela sensibilidade do dado, não pela moda.

Terceiro: **confiança em componente não-determinístico se constrói por observação, não por revisão.** Shadow mode antes de decidir; fronteira de permissão por ausência quando um modelo ganha ferramentas; humano no comando do irreversível. A Carla decide; o copiloto monta o palco.

E antes do gancho, o retrato de plantão que eu tiro no fim de todo turno: o que está de pé, e o que subiu hoje. Reparem que tudo que esta aula construiu se apoia no rio de eventos que já corria — a feature store bebe do Outbox da Aula 2, e o copiloto respeita as fronteiras da Aula 3.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 280" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="440" y="22" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333">O TechPix ao fim da Aula 5</text>

  <text x="20" y="44" font-family="sans-serif" font-size="10" font-weight="bold" fill="#a8a29e">JÁ EXISTIA — AULAS 1 A 4</text>
  <g font-family="sans-serif">
    <rect x="20" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="122" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Monólito TechPix</text>
    <text x="122" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">Postgres · ledger partida dobrada · [A1]</text>
    <rect x="232" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="334" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Idempotência · DICT · SPI</text>
    <text x="334" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">E2E ID · cache · rate limit · [A1]</text>
    <rect x="444" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="546" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Outbox → relay → Kafka</text>
    <text x="546" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">+ read models Redis/réplica · [A2]</text>
    <rect x="656" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="758" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">5 bounded contexts</text>
    <text x="758" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">context map · specs · constituição · [A3]</text>

    <rect x="20" y="104" width="416" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="228" y="123" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Contratos por aresta (Contrato de Integração)</text>
    <text x="228" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">gRPC/.proto · schema registry · DLQ · deadline propagation · [A4]</text>
    <rect x="444" y="104" width="416" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="652" y="123" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Defesas de resiliência + orçamento de 100 ms</text>
    <text x="652" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">circuit breaker · bulkhead · fail-open/closed por valor · [A2·A4]</text>
  </g>

  <text x="20" y="172" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">CONSTRUÍDO NESTA AULA</text>
  <g font-family="sans-serif">
    <rect x="20" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="101" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Modelo ML em GPU</text>
    <text x="101" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">score no Antifraude · &lt;100 ms</text>
    <rect x="192" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="273" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Feature store</text>
    <text x="273" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">Redis online · warehouse offline</text>
    <rect x="364" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="445" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Shadow mode</text>
    <text x="445" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">decide "de mentira", loga tudo</text>
    <rect x="536" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="617" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Copiloto MCP (leitura)</text>
    <text x="617" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">dossiê p/ Carla · sem escrita</text>
    <rect x="708" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="789" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Model Card + Política</text>
    <text x="789" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">modelo sugere, regra decide</text>
  </g>

  <text x="440" y="266" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">cinza = já existia · verde = construído nesta aula</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A régua de evolução do TechPix: a Aula 5 coloca inteligência dentro do orçamento de latência — sem tocar no ledger, sem tirar o humano do comando.</p>
</div>

E o gancho, porque este curso não anda sem: o Antifraude agora tem GPU, retreino mensal, perfil de tráfego próprio, um contrato de integração maduro na frente e um time dono. Ele não cabe mais confortavelmente dentro do monólito — os critérios de extração que o professor da Aula 3 listou estão, um a um, ficando verdes. Na próxima aula, a gente tira ele de lá. Ao vivo, com rede embaixo: canary, feature flag, rollback automático. E eu já aviso: a primeira tentativa vai dar errado — e vai dar errado *do jeito certo*.

---

## Apêndice — Termos novos desta aula

| Termo | O que é |
|---|---|
| **Score de risco** | Saída numérica do modelo (0–1000) estimando probabilidade de fraude; insumo da política, nunca decisão final. |
| **Política de decisão** | Tabela determinística, versionada e auditável que converte score + contexto em ação (seguir, desafiar, bloquear). |
| **Regras duras** | Camada determinística pré-modelo: proibições absolutas (listas, limites regulatórios), em microssegundos. |
| **Feature** | Sinal de entrada do modelo (ex.: "Pix recebidos na última hora"). A lista de features é decisão de governança. |
| **Feature store** | Armazenamento de duas caras: loja *offline* (histórico, serve treino) e loja *online* (valor atual, serve inferência em ms). |
| **Inferência online** | Execução do modelo no caminho crítico, por transação, dentro de orçamento de latência. |
| **Registro de modelos** | Catálogo de versões de modelo (pesos congelados + metadados); responde "qual modelo decidiu?" |
| **Modelo aberto / pesos abertos** | Modelo cujos pesos você baixa e executa na própria infra (família Llama e afins); dado sensível não sai de casa. |
| **Quantização** | Pesos com menos bits: menos memória e mais velocidade, ao custo de um pouco de qualidade. |
| **Destilação** | Treinar um modelo pequeno para imitar um grande: especialista barato no lugar de generalista caro. |
| **Shadow mode (modo sombra)** | Modelo roda com tráfego real, score registrado, decisão ignorada — confiança construída por comparação antes da promoção. |
| **Falso positivo** | Transação legítima tratada como fraude; em fintech, incidente de confiança do cliente, não estatística. |
| **Copiloto** | Assistente de IA que monta contexto e sugere; o humano decide. |
| **Fronteira de permissão por ausência** | O sistema não-determinístico não faz X porque a ferramenta de fazer X não existe no conjunto exposto a ele. |
| **Servidor MCP (aplicado)** | Ponto de acesso padronizado (Model Context Protocol) expondo ferramentas nomeadas e tipadas de um contexto a um modelo. |
| **Model Card** | Documento de governança do modelo: o que vê, o que nunca vê, desempenho, fallback, donos, limites conhecidos. |
| **Drift (semente)** | A degradação silenciosa de um modelo quando o mundo muda; nomeado e instrumentado na Aula 7. |

---

[← Aula 4](aula4-conteudo-completo.md) · [Índice](index.md) · [Aula 6 →](aula6-conteudo-completo.md)
