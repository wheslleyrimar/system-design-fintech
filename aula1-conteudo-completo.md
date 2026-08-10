---
layout: default
title: "Aula 1 — Fundamentos de Arquitetura em Fintech"
---

# Aula 1 — Fundamentos de Arquitetura em Fintech
*Curso de Arquitetura de Sistemas Financeiros com IA*

> **Navegação:** [Índice](index.md) · **Aula 1 (você está aqui)** · [Aula 2](aula2-conteudo-completo.md) · [Aula 3](aula3-conteudo-completo.md) · [Aula 4](aula4-conteudo-completo.md) · [Aula 5](aula5-conteudo-completo.md) · [Aula 6](aula6-conteudo-completo.md) · [Aula 7](aula7-conteudo-completo.md) · [Aula 8](aula8-conteudo-completo.md)

Bom, vamos começar. Antes de eu explicar qualquer conceito, deixa eu contar uma coisa que aconteceu — ou que poderia ter acontecido — com qualquer um de vocês.

São 2h47 da manhã de uma Black Friday. A Ana pega o celular, abre o aplicativo do banco, digita a chave Pix de um vendedor e toca em "pagar" — são R$5.000. A tela gira. Nada acontece. Ela espera, não aparece confirmação nenhuma, e toca de novo. Espera mais um pouco, ainda nada, e toca uma terceira vez.

E aqui está a pergunta que eu quero que vocês carreguem durante toda essa aula: **a Ana pagou uma vez, três vezes, ou nenhuma?**

Vou escrever isso bem grande no Excalidraw, porque essa pergunta não sai daqui até a gente ter resposta: *Pagou 1×, 3× ou 0×?*

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 820 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="ana-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <!-- Phone 1 -->
  <g>
    <rect x="30" y="20" width="170" height="220" rx="20" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
    <rect x="45" y="40" width="140" height="170" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
    <text x="115" y="90" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">Pix para Bruno</text>
    <text x="115" y="115" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="bold" fill="#1a1a1a">R$ 5.000,00</text>
    <rect x="65" y="150" width="100" height="30" rx="6" fill="#4338ca"/>
    <text x="115" y="170" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#fff">PAGAR</text>
    <circle cx="185" cy="30" r="14" fill="#dc2626"/>
    <text x="185" y="35" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#fff" font-weight="bold">1</text>
    <text x="115" y="260" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">02:47:00 · tela gira, nada volta</text>
  </g>
  <!-- Arrow 1 -->
  <line x1="205" y1="130" x2="290" y2="130" stroke="#888" stroke-width="2" marker-end="url(#ana-arrow)"/>
  <text x="247" y="118" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">~12s sem resposta</text>
  <!-- Phone 2 -->
  <g>
    <rect x="295" y="20" width="170" height="220" rx="20" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
    <rect x="310" y="40" width="140" height="170" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
    <text x="380" y="90" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">Pix para Bruno</text>
    <text x="380" y="115" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="bold" fill="#1a1a1a">R$ 5.000,00</text>
    <rect x="330" y="150" width="100" height="30" rx="6" fill="#4338ca"/>
    <text x="380" y="170" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#fff">PAGAR</text>
    <circle cx="450" cy="30" r="14" fill="#dc2626"/>
    <text x="450" y="35" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#fff" font-weight="bold">2</text>
    <text x="380" y="260" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">02:47:12 · toca de novo</text>
  </g>
  <!-- Arrow 2 -->
  <line x1="470" y1="130" x2="555" y2="130" stroke="#888" stroke-width="2" marker-end="url(#ana-arrow)"/>
  <text x="512" y="118" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">~12s sem resposta</text>
  <!-- Phone 3 -->
  <g>
    <rect x="560" y="20" width="170" height="220" rx="20" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
    <rect x="575" y="40" width="140" height="170" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
    <text x="645" y="90" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">Pix para Bruno</text>
    <text x="645" y="115" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="bold" fill="#1a1a1a">R$ 5.000,00</text>
    <rect x="595" y="150" width="100" height="30" rx="6" fill="#4338ca"/>
    <text x="645" y="170" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#fff">PAGAR</text>
    <circle cx="715" cy="30" r="14" fill="#dc2626"/>
    <text x="715" y="35" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#fff" font-weight="bold">3</text>
    <text x="645" y="260" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">02:47:24 · terceira tentativa</text>
  </g>
  <!-- Question box -->
  <rect x="180" y="270" width="460" height="26" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="410" y="288" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#b91c1c">A Ana pagou 1×, 3× ou 0×?</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A Ana toca três vezes no mesmo botão "pagar" — para ela, cada toque é a mesma intenção, não três pagamentos diferentes.</p>
</div>

A resposta não está em nenhuma linha de código da tela do celular. Ela está na **arquitetura** — nas decisões sobre como o dinheiro se move quando existe incerteza, concorrência e falha. E é exatamente isso que a gente vai construir juntos hoje.

Por que eu abro assim, com uma história e não com uma definição? Porque em System Design todo conceito abstrato precisa de um problema real puxando ele. "Idempotência", "consistência", "liquidação" são palavras vazias até virarem "a Ana não pode ser cobrada três vezes". A dor vem primeiro, o vocabulário vem depois — e cada vez que a gente nomear um conceito novo, eu vou voltar nessa cena.

Ao longo desse curso a gente vai construir, peça por peça, uma fintech fictícia que eu vou chamar de **TechPix**. E duas coisas vão atravessar tudo que a gente falar: primeiro, como o dinheiro de fato se move no Brasil — o Pix, o SPI, o DICT, o Banco Central, com números reais, não achismo; segundo, como a inteligência artificial está mudando o próprio trabalho de arquitetar sistemas. Guardem essas duas linhas, porque elas vão se cruzar o tempo inteiro, e no fim da aula elas vão se encontrar num único artefato.

---

## 1. Por que sistemas financeiros são diferentes

Antes de eu desenhar qualquer caixinha, eu preciso que vocês internalizem uma coisa: **arquitetura de fintech não é arquitetura de e-commerce com um cadeado.** Existem quatro propriedades do dinheiro que mudam as decisões que a gente vai tomar — e cada uma delas **força** uma decisão de arquitetura específica. Esse é o primeiro exercício de System Design que eu quero fazer com vocês: derivar a estrutura do sistema a partir das restrições do domínio, não a partir de modismo.

Reparem nessa tabela:

| Propriedade do dinheiro | O que significa | Decisão de arquitetura que ela força |
|---|---|---|
| **Conservação** | Não se cria nem se destrói dinheiro; só se move. Toda saída tem uma entrada igual. | **Ledger de partida dobrada** (eu explico daqui a pouco). Nunca "atualizar saldo"; sempre "registrar movimento". |
| **Irreversibilidade** | Liquidou, acabou. Reverter exige uma nova transação — ou o trilho regulatório de devolução, o **MED** (Mecanismo Especial de Devolução, que eu detalho mais para a frente). | **Idempotência** e **falhar fechado**. Prudência acima de otimismo. |
| **Auditabilidade** | Cada centavo precisa ser explicável anos depois — é exigência do BACEN e também da **LGPD** (a Lei Geral de Proteção de Dados, a nossa lei de privacidade). | **Imutabilidade**, ou **append-only**: um log que só recebe registros novos, nunca apaga nem sobrescreve. O passado não muda; só se acrescenta. |
| **Correção acima de disponibilidade** (no núcleo) | Melhor recusar uma operação do que debitar errado. | **Consistência forte** no núcleo do sistema; consistência eventual só na borda. |

E aqui está o insight que eu quero que fique: **as decisões grandes de arquitetura não são gosto pessoal — elas são deriváveis do domínio.** Um bom arquiteto de fintech não "escolhe" um ledger imutável porque está na moda. Ele consegue mostrar, com essas quatro propriedades na mão, que o domínio **exige** isso. Essa é a diferença entre montar uma stack porque alguém decidiu no boteco e efetivamente arquitetar um sistema.

Reparem que eu escrevi "no núcleo" ali na última linha, entre parênteses. Isso é de propósito: nem tudo no sistema precisa de correção máxima. O extrato, o feed de transações, as notificações — tudo isso tolera um pouco de atraso. Saber **onde** cada uma dessas quatro propriedades vale, e onde ela pode ser relaxada, é o trabalho central do arquiteto. É exatamente disso que eu vou falar daqui a pouco, quando a gente chegar em trade-offs.

---

## 2. O ledger como decisão de System Design

Vamos falar do ledger. Ele é o átomo de qualquer fintech — mas eu quero que vocês parem de pensar nele como uma tabela de banco de dados e comecem a pensar nele como uma **decisão de arquitetura**.

### 2.1 Uma ideia de 500 anos, e por que ela sobreviveu

Em 1494, um matemático italiano chamado Luca Pacioli documentou uma técnica que os mercadores já usavam havia séculos: as **partidas dobradas**. A regra é simples de enunciar: todo evento econômico é registrado em dois lados, que sempre se equilibram. Se eu escrever Σ para "soma", a regra fica: Σ dos débitos é sempre igual a Σ dos créditos.

Por que isso sobreviveu 500 anos? Porque resolve, de uma tacada só, três problemas que todo sistema financeiro enfrenta: **conservação** (nada some sem explicação), **auditoria** (a história inteira fica registrada, não só o resultado final) e **reconstrução** (o estado atual pode sempre ser recalculado a partir do histórico). E aqui vai uma provocação: toda vez que um engenheiro "inventa" um log append-only e balanceado — um log em que só se acrescenta informação, nunca se apaga nem se sobrescreve — ele está, sem saber, redescobrindo Pacioli.

### 2.2 O modelo conceitual

Quero que vocês guardem três conceitos e como eles se relacionam:

- **Conta contábil:** pensem nela como um "pote" de valor, com uma natureza — ativo ou passivo. E aqui vai um ponto contraintuitivo que eu quero que vocês registrem: **o saldo do cliente é um passivo da fintech**, não um ativo. Vocês devem aquele dinheiro a ele. Além das contas de cliente, existem contas de liquidação, de tarifa, de reserva no Banco Central, e por aí vai.
- **Lançamento:** um débito ou um crédito numa conta, com um valor. Ele nunca existe sozinho.
- **Transação:** um conjunto de lançamentos que se equilibra e representa um fato econômico — um Pix, uma tarifa, um estorno.

E a regra que nunca pode ser violada: **em toda transação, Σ débitos = Σ créditos.** Eu chamo isso de *fitness function* número um do sistema. Em arquitetura evolutiva, uma fitness function é uma verificação automática — um teste — que confirma se o sistema ainda respeita uma propriedade que vocês definiram como importante. Guardem esse termo, porque ele vai voltar lá na frente, quando a gente chegar na parte de inteligência artificial: essa mesma invariante vai virar um teste automático que um agente respeita.

### 2.3 A decisão central: o log é a verdade, o saldo é só uma projeção

Aqui está a decisão de System Design que define tudo o mais: **a fonte da verdade é o log imutável de lançamentos** — o que os engenheiros chamam de *write model*, o modelo de escrita. **O saldo é uma projeção derivada dele** — o *read model*, o modelo de leitura.

Por que não simplesmente guardar o saldo numa coluna e dar um update nela a cada transação? Porque essa coluna tem três problemas sérios:

- ela **não tem auditoria** — vocês sabem o "agora", mas não sabem "como chegou até aqui";
- ela **corre risco de corrida** — duas escritas concorrentes podem se sobrepor. Isso é o que se chama de *lost update*, uma atualização perdida: as duas escritas acontecem ao mesmo tempo, e uma apaga o efeito da outra sem que ninguém perceba. O resultado é que vocês criam ou destroem dinheiro, violando a conservação que a gente viu lá atrás;
- e ela **não é reconstruível** — se aquele número corromper, a verdade se perdeu de vez, porque a verdade *era* aquele número.

O log append-only resolve os três de uma vez: vocês só acrescentam um fato, nunca sobrescrevem nada, e o saldo é simplesmente a soma de todos os lançamentos daquela conta — recalculável a qualquer momento.

E já plantando uma semente para a Aula 2: se a verdade (a escrita) e a projeção (a leitura) têm modelos diferentes, vocês já estão no caminho de duas ideias importantes — **CQRS**, que significa Command Query Responsibility Segregation, ou seja, separar o "lado que escreve" do "lado que lê" em modelos distintos; e **event sourcing**, que é guardar o histórico de eventos como fonte da verdade, em vez de guardar só o estado atual. Na prática, vocês vão manter um saldo materializado — pré-calculado e guardado, para não somar tudo de novo a cada leitura — mas ele sempre pode ser reconstituído a partir do log. A verdade nunca mora no saldo.

Deixa eu colocar as duas alternativas lado a lado, porque esse é o desenho que eu quero que vocês carreguem na cabeça — e reparem que o da direita tem nome de catálogo: é o padrão **Event Sourcing**, documentado no microservices.io, do Chris Richardson. Pacioli chegou lá 500 anos antes do catálogo.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 340" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a1t-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a1t-arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- Left panel: UPDATE destrutivo -->
  <rect x="20" y="20" width="410" height="270" rx="12" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="225" y="46" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d">Saldo numa coluna — UPDATE destrutivo</text>
  <rect x="140" y="60" width="170" height="36" rx="6" fill="#fff" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="225" y="83" text-anchor="middle" font-family="monospace" font-size="12" fill="#333">saldo = R$ 900</text>
  <line x1="90" y1="130" x2="180" y2="102" stroke="#b91c1c" stroke-width="2" marker-end="url(#a1t-arrow-red)"/>
  <line x1="360" y1="130" x2="270" y2="102" stroke="#b91c1c" stroke-width="2" marker-end="url(#a1t-arrow-red)"/>
  <rect x="35" y="132" width="160" height="52" rx="6" fill="#fff" stroke="#999" stroke-width="1.5"/>
  <text x="115" y="152" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">T1 lê 900,</text>
  <text x="115" y="170" text-anchor="middle" font-family="monospace" font-size="11" fill="#7f1d1d">UPDATE saldo=800</text>
  <rect x="255" y="132" width="160" height="52" rx="6" fill="#fff" stroke="#999" stroke-width="1.5"/>
  <text x="335" y="152" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">T2 lê 900 (junto),</text>
  <text x="335" y="170" text-anchor="middle" font-family="monospace" font-size="11" fill="#7f1d1d">UPDATE saldo=850</text>
  <rect x="90" y="200" width="270" height="34" rx="6" fill="#b91c1c"/>
  <text x="225" y="222" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#fff" font-weight="bold">T2 apaga T1: lost update — dinheiro criado</text>
  <text x="225" y="256" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#991b1b">− sem auditoria · − não reconstruível · − corrida destrói conservação</text>
  <text x="225" y="276" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#991b1b">a verdade ERA o número; corrompeu, acabou</text>

  <!-- Right panel: Event Sourcing -->
  <rect x="450" y="20" width="410" height="270" rx="12" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="655" y="46" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">Log append-only + projeção — Event Sourcing</text>
  <rect x="470" y="60" width="185" height="130" rx="8" fill="#fff" stroke="#166534" stroke-width="1.5"/>
  <text x="562" y="80" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">Log de lançamentos (Postgres)</text>
  <text x="562" y="100" text-anchor="middle" font-family="monospace" font-size="11" fill="#333">+1.000 (depósito)</text>
  <text x="562" y="118" text-anchor="middle" font-family="monospace" font-size="11" fill="#333">−100 (Pix p/ Bruno)</text>
  <text x="562" y="136" text-anchor="middle" font-family="monospace" font-size="11" fill="#333">−50 (tarifa)</text>
  <text x="562" y="156" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">só INSERT — nunca UPDATE</text>
  <text x="562" y="172" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">write model · a verdade</text>
  <line x1="655" y1="125" x2="700" y2="125" stroke="#4338ca" stroke-width="2" marker-end="url(#a1t-arrow)"/>
  <text x="677" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">Σ</text>
  <rect x="702" y="95" width="140" height="60" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="772" y="118" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#26215C">Projeção: saldo</text>
  <text x="772" y="136" text-anchor="middle" font-family="monospace" font-size="12" fill="#26215C">R$ 850</text>
  <text x="772" y="172" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">read model · materializado,</text>
  <text x="772" y="186" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">sempre recalculável</text>
  <text x="655" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">+ auditoria completa · + reconstruível do zero · + append não sobrescreve</text>
  <text x="655" y="246" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">− saldo exige projeção (custo que a Aula 2 paga com CQRS)</text>
  <text x="655" y="272" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">padrão Event Sourcing — microservices.io (Chris Richardson)</text>

  <text x="440" y="322" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">A mesma pergunta — "quanto a Ana tem?" — respondida por um número frágil ou por uma história somável.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Coluna de saldo vs log-como-verdade: o trade-off que define o ledger — e que já é o embrião de CQRS e Event Sourcing.</p>
</div>

### 2.4 Um Pix de R$100, contado como movimento

Vamos ver como isso fica na prática. A Ana, no nosso TechPix, manda R$100 para o Bruno, que tem conta no Banco Beta. No nosso ledger, esse pagamento **não é** "saldo -= 100". São fatos encadeados:

```
Fato 1 (reserva):   DÉBITO carteira_ana 100  |  CRÉDITO pix_a_liquidar 100   (Σ=Σ ✓)
Fato 2 (liquidação  DÉBITO pix_a_liquidar 100 |  CRÉDITO reserva_no_BC 100    (após SPI confirmar)
        no SPI):
```

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 820 280" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="led-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <text x="20" y="24" font-family="sans-serif" font-size="13" fill="#666">Fato 1 — reserva</text>
  <rect x="20" y="35" width="200" height="60" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="120" y="58" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#b91c1c">DÉBITO</text>
  <text x="120" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">carteira_ana · R$100</text>
  <line x1="220" y1="65" x2="330" y2="65" stroke="#4338ca" stroke-width="2" marker-end="url(#led-arrow)"/>
  <rect x="330" y="35" width="220" height="60" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="440" y="58" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#166534">CRÉDITO</text>
  <text x="440" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">pix_a_liquidar · R$100</text>
  <text x="620" y="65" font-family="sans-serif" font-size="13" fill="#166534">Σ = Σ ✓</text>

  <text x="20" y="140" font-family="sans-serif" font-size="13" fill="#666">Fato 2 — liquidação no SPI (após confirmação)</text>
  <rect x="20" y="151" width="220" height="60" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="130" y="174" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#b91c1c">DÉBITO</text>
  <text x="130" y="194" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">pix_a_liquidar · R$100</text>
  <line x1="240" y1="181" x2="350" y2="181" stroke="#4338ca" stroke-width="2" marker-end="url(#led-arrow)"/>
  <rect x="350" y="151" width="220" height="60" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="460" y="174" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#166534">CRÉDITO</text>
  <text x="460" y="194" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">reserva_no_BC · R$100</text>
  <text x="620" y="181" font-family="sans-serif" font-size="13" fill="#166534">Σ = Σ ✓</text>

  <rect x="20" y="230" width="750" height="34" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="395" y="252" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#3730a3">Dois pares balanceados e imutáveis — nunca "saldo −= 100". O estado (reservado → liquidado) é o próprio log.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Cada estado do dinheiro é um fato encadeado, não uma atualização de coluna.</p>
</div>

O SPI, que é o Sistema de Pagamentos Instantâneos — a infraestrutura do Banco Central que efetivamente liquida o Pix —, eu vou detalhar com calma daqui a pouco. Por enquanto, pensem nele como "o sistema do Banco Central que confirma que o dinheiro chegou".

Reparem que o dinheiro caminha por **estados explícitos**: reservado, depois liquidado. Cada um desses estados é um par balanceado e imutável. Se alguma coisa falhar no meio do caminho, vocês sabem exatamente onde pararam — porque o estado é o próprio log, não uma flag frágil escondida numa coluna. Isso é resiliência de graça, só por causa da escolha de modelagem que a gente fez.

### 2.5 Ordem de grandeza, com números reais — o exercício de capacidade

System Design sempre exige uma estimativa de guardanapo. Mas eu não quero fazer isso com números chutados — vamos usar os números que o próprio Banco Central publicou, e fazer a conta juntos, passo a passo, do jeito que eu quero que vocês façam sempre que forem dimensionar um sistema.

O Banco Central divulgou que, entre janeiro e maio de 2026, o Pix movimentou R$16 trilhões, com **36,3 bilhões de transações em cinco meses** — um crescimento de mais de 26% sobre o mesmo período de 2025. E o próprio Banco Central já fez uma conta para vocês: isso dá **uma média de quase 3 mil operações por segundo em todo o país**. Vamos verificar essa conta e continuar a partir dela.

Primeiro passo, anualizar: 36,3 bilhões em 5 meses, no ritmo atual, projeta algo em torno de **87 bilhões de transações por ano** — bem mais que as "dezenas de bilhões" que cursos costumam citar de memória; o Pix cresce rápido demais para um número desatualizado continuar certo por muito tempo.

Segundo passo, diário: 87 bilhões dividido por 365 dá **cerca de 238 milhões de transações por dia**, na média do ano. Como conferência: o recorde diário registrado até agora foi em 5 de dezembro de 2025, com **313,3 milhões de transações num único dia** — a primeira vez que o Pix passou de 300 milhões em 24 horas. Reparem que o recorde é maior que a média, o que faz sentido: dia de recorde não é dia comum.

Terceiro passo, TPS médio: 238 milhões de transações dividido por 86.400 segundos no dia dá **cerca de 2.750 transações por segundo**, batendo — e isso é o que eu quero que vocês sintam na pele — com os "quase 3 mil por segundo" que o Banco Central divulgou. Quando a conta de vocês bate com o número oficial, é sinal de que o raciocínio está certo.

Quarto passo — e aqui é onde a estimativa de guardanapo de verdade começa, porque não existe número oficial de "TPS no pico do segundo mais carregado": o tráfego do Pix não é uniforme ao longo do dia. Ele se concentra em horários específicos — hora do almoço, início da noite, dia de pagamento de salário, exatamente o cenário que abre a Aula 2. Um **fator de pico** razoável para sistemas de pagamento no varejo, na hora mais carregada do dia, costuma ficar entre 3× e 8× a média diária. Se a gente aplicar um fator conservador de 5× sobre o TPS médio do dia de recorde — 313,3 milhões / 86.400 ≈ 3.626 TPS de média naquele dia —, chegamos a uma estimativa de **pico em torno de 18 mil transações por segundo**, somando todas as instituições do país. Um único participante grande — se ele tiver uma fatia relevante do mercado — pode ver uma fração considerável disso sozinho, na própria infraestrutura.

Guardem essa técnica, não só o número: **dado real da fonte oficial + fator de pico estimado com critério = uma capacidade de dimensionamento defensável**, mesmo sem um número de pico oficial publicado.

Quinto passo, o multiplicador de lançamentos: cada transação de Pix não vira um lançamento só — vira, no mínimo, o par débito/crédito da reserva, e depois o par da liquidação, como a gente viu na Seção 2.4. Em cenários com tarifa ou com múltiplas contas de reconciliação, esse número sobe ainda mais. Um multiplicador conservador de 3 lançamentos por transação, sobre 87 bilhões de transações por ano, dá **algo em torno de 260 bilhões de lançamentos por ano**.

Sexto passo, armazenamento: cada lançamento é imutável e precisa ficar retido por anos — exigência de auditoria, não capricho de engenheiro. Se cada registro, com seus índices, timestamps, o E2E ID e os metadados de reconciliação, ocupar algo da ordem de 300 a 500 bytes — um chute razoável de engenharia, não um número oficial —, 260 bilhões de lançamentos por ano dão algo entre **75 e 130 terabytes por ano**, só de ledger, antes de fator de replicação ou backup. Isso não é assustador para a infraestrutura de hoje, mas é grande o suficiente para que "vamos guardar tudo numa tabela só, sem particionar por tempo" pare de ser uma opção séria depois do segundo ou terceiro ano.

Sétimo passo — e esse é o que eu mais gosto de ensinar, porque é a ferramenta de capacidade mais subestimada em System Design: **a Lei de Little.** Ela diz o seguinte, de forma quase chocante de simples: **L = λ × W** — a concorrência média num sistema (L, quantas requisições estão "dentro" dele ao mesmo tempo) é igual à taxa de chegada (λ, o TPS) multiplicada pelo tempo médio que cada uma passa lá dentro (W, a latência). Essa lei vale para qualquer sistema em estado estacionário, não importa a distribuição de chegada — e ela é o jeito certo de responder "quantas conexões simultâneas de banco eu preciso?", em vez de chutar um número redondo.

Apliquem comigo ao caminho de escrita do ledger: se o pico nacional é ~18 mil TPS, e a fatia que cai na infraestrutura de vocês — digamos, um TechPix com 5% de participação de mercado — é ~900 TPS, e cada escrita no ledger, do início da transação até o commit, leva em média 50 milissegundos (aquisição de lock, gravação, confirmação), então: **L = 900 × 0,05 = 45 conexões simultâneas** precisam estar ativas, em média, só para sustentar a escrita no pico. Isso parece pouco — e é exatamente por isso que a Lei de Little é tão útil: ela mostra que o número de conexões necessário é muito menor do que o TPS bruto sugere, **contanto que a latência por operação se mantenha baixa**. E aqui mora o perigo, ligando direto com a Aula 2: se a latência por operação **sobe** — porque o lock está sob contenção e a transação espera na fila —, a concorrência necessária sobe na mesma proporção. Se aquela mesma operação passa a levar 500 ms em vez de 50 ms (10× mais lenta, por causa da fila do lock), a concorrência necessária pula para 450 conexões simultâneas. Se o pool de conexões do sistema foi dimensionado para 100, ele esgota, e é isso — exatamente isso, com números — que causa o esgotamento de pool que a Aula 2 investiga. A Lei de Little transforma "a fila cresceu" de observação vaga em número que vocês calculam antes do incidente acontecer.

Oitavo passo, uma checagem rápida de onde o gargalo realmente mora: 900 TPS de escrita, com 3 lançamentos por transação, dá 2.700 escritas por segundo no ledger. Um SSD NVMe moderno sustenta, sozinho, algo como 500 mil a 1 milhão de IOPS (operações de entrada/saída por segundo). Ou seja: **o disco não é o gargalo** — 2.700 escritas por segundo é uma fração pequena da capacidade de um único disco moderno. O gargalo real, quase sempre, é a **coordenação** — o lock, o consenso entre partições, a espera na fila —, não a capacidade bruta de gravação. Essa é uma das lições mais contraintuitivas de System Design: o hardware raramente é o limite; a forma como vocês coordenam acesso concorrente é.

Disso caem três consequências de design que eu quero que vocês levem: primeiro, a escrita no ledger é o **gargalo quente** do sistema — não por falta de IOPS, mas por coordenação sob contenção, que a Lei de Little acabou de quantificar —, e é exatamente aí que a Aula 2 vai bater; segundo, o armazenamento é append-only e mede dezenas de terabytes por ano, então vocês precisam pensar em particionamento por tempo, arquivamento, storage frio; terceiro, a leitura — extrato, saldo — é ordens de magnitude mais frequente que a escrita, então separar leitura de escrita não é luxo, é necessidade.

### 2.7 Tecnologias reais: quem faz isso, e como

Tudo que eu descrevi até aqui — isolamento, locking, particionamento — não é teoria solta. Bancos de dados reais implementam isso de formas específicas, e vale vocês conhecerem os nomes, porque é isso que separa "eu sei o conceito" de "eu sei escolher a ferramenta certa".

O **PostgreSQL**, no nível padrão, roda em read committed; mas oferece serializable através de um mecanismo chamado **SSI — Serializable Snapshot Isolation**, que não trava tudo de forma pessimista: ele deixa as transações rodarem em paralelo, sobre snapshots, e detecta, através de um rastro de dependências entre elas, quando existe uma "estrutura perigosa" que poderia violar serializabilidade — e aí aborta uma das transações envolvidas, para a aplicação tentar de novo. Isso é sofisticado o suficiente para que muitas fintechs rodem o núcleo do ledger inteiro num único Postgres bem ajustado, com particionamento nativo de tabela por tempo e por hash de conta, e réplicas de leitura para o lado de CQRS — só migrando para algo mais exótico quando o throughput de escrita realmente supera o que um primary bem dimensionado aguenta.

O **MySQL/InnoDB** por padrão já roda em repeatable read, mas usa um mecanismo diferente do Postgres para evitar leituras fantasmas: **next-key locking**, que trava não só as linhas existentes, mas também "lacunas" entre elas, para impedir que uma nova linha apareça no meio de um intervalo que uma transação já leu. É outro caminho para o mesmo destino, com implicações de performance diferentes sob contenção alta.

Bancos distribuídos "NewSQL" — **CockroachDB**, **YugabyteDB**, **TiDB** — resolvem o particionamento que eu descrevi manualmente (`hash(conta_id) mod N`) **dentro do próprio banco**: cada faixa de dados vira um grupo Raft (um protocolo de consenso distribuído), replicado automaticamente entre nós, com rebalanceamento automático quando uma faixa fica quente — o problema de "chave quente" que eu mencionei antes tem, nesses bancos, uma resposta de fábrica. E, diferente do Postgres, esses bancos costumam oferecer **só** serializable — não existe modo mais fraco para escolher, porque a arquitetura inteira já foi desenhada em cima da suposição de que a distribuição exige a garantia mais forte por padrão.

O **Google Spanner**, que eu já mencionei na Seção 4.4, vai um passo além: ele soma ao serializable distribuído a **consistência externa**, usando o TrueTime — ele garante uma ordem global de transações que respeita a ordem real no tempo físico, não só uma ordem logicamente equivalente. É a garantia mais forte que existe em produção, em escala global, hoje.

E vale mencionar um contraponto real, para quem só conhece bancos relacionais: sistemas como o **DynamoDB** dão consistência forte fácil **por item individual**, mas transações que tocam múltiplos itens (a operação `TransactWriteItems`) têm limites — um número máximo de itens por transação, sem consultas arbitrárias entre eles. Para um ledger, onde a invariante central atravessa múltiplas linhas por natureza, isso é uma limitação real: um banco de chave-valor puro empurra para vocês, na aplicação, uma responsabilidade que um banco relacional com serializable resolve de graça no motor.

Por fim, um exemplo concreto de "hash(conta_id) mod N" rodando em produção, em escala gigante: o **Vitess**, que nasceu no YouTube e hoje roda no Slack e em outras empresas de grande porte, faz exatamente esse tipo de particionamento manual sobre um cluster de instâncias MySQL comuns, com uma camada de roteamento (o `vtgate`) que decide para qual partição cada query vai. É a prova de que o esquema manual que eu descrevi na Seção 2.6 não é um exercício acadêmico — é como sistemas reais, em escala nacional, resolvem exatamente esse problema.

### 2.6 Isolamento e particionamento: como a consistência forte se implementa de verdade

Até aqui eu falei de "consistência forte" como uma propriedade abstrata. Deixa eu descer um nível e mostrar como ela se implementa de fato num banco de dados — porque é aqui que "forte" vira uma escolha técnica concreta, com um nome e um custo.

**Nível de isolamento.** A maioria dos bancos relacionais oferece, por padrão, o nível **read committed** — cada leitura enxerga só dados já commitados, mas duas transações concorrentes ainda podem produzir um resultado que viola uma invariante que envolve mais de uma linha. Para o ledger, isso não basta: a invariante Σ débitos = Σ créditos depende de múltiplas linhas se manterem coerentes entre si. O nível que protege isso de verdade é o **serializable** — o banco garante que o resultado de rodar várias transações concorrentes é equivalente a rodá-las uma de cada vez, em alguma ordem. Ele resolve o problema, mas ao custo de mais abortos e mais retentativas quando duas transações disputam os mesmos dados — que é, tecnicamente, a origem exata do "ponto quente" que a Aula 2 vai investigar. Existe um meio-termo comum, o **snapshot isolation** (ou repeatable read, dependendo do banco), que evita a maioria dos problemas práticos com menos contenção que o serializable puro — mas ainda pode permitir um fenômeno chamado *write skew*, onde duas transações, cada uma vendo um retrato consistente do mundo, tomam decisões que juntas violam uma invariante que nenhuma delas violaria sozinha. Para o núcleo do ledger, a escolha defensável é serializable, ou um mecanismo equivalente — o custo de contenção é o preço da correção.

**Controle de concorrência: pessimista ou otimista.** Existem duas famílias de mecanismo para garantir isso na prática. O **locking pessimista** — o equivalente a "trave a linha antes de mexer nela" — é simples de raciocinar, mas é exatamente o mecanismo por trás do ponto quente: toda transação que quer tocar a mesma conta de liquidação espera na fila do lock, uma de cada vez. O **controle de concorrência otimista** troca o lock por uma coluna de versão: a transação lê o valor atual e sua versão, calcula o novo estado, e só grava se a versão não mudou desde a leitura; se mudou, ela sabe que perdeu a corrida e tenta de novo. Sob baixa contenção, isso é mais rápido, porque ninguém fica esperando lock nenhum. Sob **alta** contenção — o cenário exato do dia 5 —, o controle otimista pode virar uma tempestade de retentativas, porque muita gente perde a corrida ao mesmo tempo e todo mundo tenta de novo junto. Nenhuma das duas famílias resolve sozinha um hotspot real; as duas só tornam explícito, de formas diferentes, o mesmo custo de coordenação que a consistência forte exige.

Deixa eu desenhar as duas famílias lado a lado, com a nossa conta quente no meio do desenho — porque é vendo a fila de um lado e a tempestade de retentativas do outro que o trade-off deixa de ser abstrato:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 340" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a1u-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a1u-arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
    <marker id="a1u-arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>

  <!-- LEFT: Pessimistic -->
  <rect x="15" y="15" width="425" height="255" rx="12" fill="#fff" stroke="#ccc" stroke-width="1.5"/>
  <text x="227" y="42" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Locking PESSIMISTA</text>
  <text x="227" y="60" text-anchor="middle" font-family="monospace" font-size="11" fill="#4338ca">SELECT … FOR UPDATE</text>

  <!-- Locked row -->
  <rect x="150" y="80" width="155" height="42" rx="7" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="227" y="98" text-anchor="middle" font-family="monospace" font-size="11" fill="#26215C">pix_a_liquidar</text>
  <text x="227" y="114" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">🔒 travada por T1</text>

  <!-- Queue -->
  <rect x="35" y="150" width="80" height="34" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="75" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">T2 espera</text>
  <rect x="135" y="150" width="80" height="34" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="175" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">T3 espera</text>
  <rect x="235" y="150" width="80" height="34" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="275" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">T4 espera</text>
  <line x1="335" y1="167" x2="227" y2="128" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a1u-arrow-red)"/>
  <text x="345" y="171" font-family="sans-serif" font-size="11" fill="#b91c1c">fila no lock</text>

  <text x="35" y="215" font-family="sans-serif" font-size="11" fill="#166534">+ simples de raciocinar; nenhum trabalho perdido</text>
  <text x="35" y="233" font-family="sans-serif" font-size="11" fill="#b91c1c">− sob contenção, vira fila: uma de cada vez</text>
  <text x="35" y="251" font-family="sans-serif" font-size="11" fill="#b91c1c">− é o mecanismo por trás do "ponto quente" (Aula 2)</text>

  <!-- RIGHT: Optimistic -->
  <rect x="460" y="15" width="425" height="255" rx="12" fill="#fff" stroke="#ccc" stroke-width="1.5"/>
  <text x="672" y="42" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Concorrência OTIMISTA</text>
  <text x="672" y="60" text-anchor="middle" font-family="monospace" font-size="11" fill="#4338ca">UPDATE … WHERE version = 41</text>

  <!-- Versioned row -->
  <rect x="595" y="80" width="155" height="42" rx="7" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="672" y="98" text-anchor="middle" font-family="monospace" font-size="11" fill="#26215C">pix_a_liquidar</text>
  <text x="672" y="114" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">version = 41 (sem lock)</text>

  <!-- Racers -->
  <rect x="480" y="150" width="90" height="34" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="525" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">T1 grava ✓ v42</text>
  <rect x="590" y="150" width="90" height="34" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="635" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">T2 perdeu ↻</text>
  <rect x="700" y="150" width="90" height="34" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="745" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">T3 perdeu ↻</text>
  <text x="810" y="171" font-family="sans-serif" font-size="11" fill="#b91c1c">retry…</text>

  <text x="480" y="215" font-family="sans-serif" font-size="11" fill="#166534">+ sob baixa contenção, ninguém espera lock nenhum</text>
  <text x="480" y="233" font-family="sans-serif" font-size="11" fill="#b91c1c">− sob ALTA contenção: tempestade de retentativas</text>
  <text x="480" y="251" font-family="sans-serif" font-size="11" fill="#b91c1c">− trabalho perdido: quem perde a corrida refaz tudo</text>

  <!-- Bottom banner -->
  <rect x="15" y="285" width="870" height="40" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="450" y="303" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Nenhuma das duas resolve o hotspot — as duas só expõem, de formas diferentes, o custo de coordenação da consistência forte.</text>
  <text x="450" y="319" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">A saída estrutural é particionar a escrita (abaixo) — e é isso que a Aula 8 fecha com o ADR-003.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">As duas famílias de controle de concorrência sobre a mesma conta quente: fila de um lado, corrida com retentativas do outro.</p>
</div>

**Particionamento do ledger — o desenho concreto.** A saída estrutural, que a Aula 2 só vai poder aplicar de verdade depois de identificar o problema, e que a Aula 8 fecha com o ADR-003, é particionar a escrita por uma chave que distribua o tráfego — tipicamente um hash da conta do cliente, `hash(conta_id) mod N`, ou um esquema de hashing consistente para facilitar rebalanceamento futuro. Isso faz com que a maioria das transações — as que envolvem só uma conta, ou duas contas na mesma partição — continue cabendo numa transação local, serializable, rápida. O caso difícil é a transação que atravessa partições — a Ana numa partição, o Bruno em outra —, porque agora vocês precisam de coordenação **entre** partições. Existem duas respostas clássicas: **two-phase commit**, que mantém a atomicidade forte entre partições ao custo de mais latência e mais fragilidade (se um participante trava no meio do protocolo, o sistema inteiro fica bloqueado esperando); ou o padrão **saga**, onde cada partição commita sua parte localmente, e uma ação compensatória desfaz o que for preciso se uma etapa posterior falhar — trocando atomicidade forte imediata por consistência eventual entre partições, com uma trilha explícita de compensação. Reparem que isso é, estruturalmente, a mesma ideia do Outbox que a Aula 2 vai apresentar: um registro imutável do que precisa acontecer depois, em vez de uma promessa implícita de que tudo vai dar certo na mesma transação.

---

## 3. Idempotência: projetando correção sob incerteza

Agora sim, chegou a hora de pagar a dívida que eu deixei lá no começo, com a história da Ana. Mas eu quero que o foco de vocês seja o **design da solução**, não os detalhes de implementação.

### 3.1 O problema fundamental: o timeout é ambíguo

Em qualquer sistema distribuído, quando vocês enviam uma requisição e não recebem resposta, existe uma ambiguidade fundamental: vocês não sabem se a operação **falhou antes de executar**, ou se ela **executou e só a resposta se perdeu no caminho**. Isso é conhecido como o "problema dos dois generais". O timeout, por si só, não distingue essas duas situações.

No caso da Ana: o celular dela mostrou "não aconteceu". Mas o servidor pode ter processado a transação perfeitamente — só a confirmação que não voltou. E se o cliente reenvia a requisição, e ele vai reenviar, existe o risco real de a transação executar de novo.

### 3.2 As três semânticas possíveis — e a única verdade que importa

Existem três formas de um sistema tratar uma mensagem que pode estar duplicada:

- **At-most-once** ("no máximo uma vez"): o sistema não repete a operação. É seguro contra duplicata, mas **pode perder** a operação de vez. Isso é inaceitável quando estamos falando de dinheiro.
- **At-least-once** ("pelo menos uma vez"): o sistema repete até ter certeza de que funcionou. Nunca perde a operação, mas **pode duplicá-la**. É isso, gente, que a rede real entrega — não tem almoço grátis aqui.
- **Exactly-once** ("exatamente uma vez"): o ideal que todo mundo quer.

E aqui vai uma verdade que muita gente não fala: **entregar uma mensagem exactly-once é impossível** numa rede assíncrona. O que de fato se consegue — e o que vocês realmente querem — é o **efeito exactly-once**: a mensagem pode chegar várias vezes, no modelo at-least-once, mas o efeito dela no ledger acontece uma única vez. A ponte entre "chegou duplicado" e "efeito único" tem nome: **idempotência**.

### 3.3 Como desenhar essa solução

Isso não é simplesmente colocar um `UNIQUE` numa coluna do banco. É desenhar um componente de idempotência com três propriedades.

Primeiro, **a chave identifica a intenção, não a tentativa**. Os três toques da Ana carregam a mesma chave, porque são a mesma intenção de pagamento. E isso implica que a chave precisa nascer no **cliente**, e sobreviver a todos os retries. Pensem comigo: se fosse o servidor a gerar essa chave, cada retry ganharia uma chave nova, e a deduplicação simplesmente não funcionaria.

Segundo, **o registro precisa ter estado**, não só existência: "em andamento" versus "concluído". Isso resolve o caso mais difícil de todos — uma segunda requisição concorrente chegando **antes** de a primeira terminar de gravar. Sem esse estado e sem serialização, as duas requisições veem "não existe" ao mesmo tempo, e ambas duplicam.

Terceiro, **o efeito precisa ser atômico** junto com o registro de idempotência: ou o sistema registra "concluído" **e** grava os lançamentos no mesmo golpe, ou não grava nada. É a mesma transação do ledger que a gente viu na seção anterior.

Deixa eu descrever o fluxo completo: se for um retry tardio, o sistema devolve o resultado que já tinha guardado. Se for um retry concorrente, ele fica esperando o primeiro terminar, e aí devolve o mesmo resultado. E na primeira vez, o sistema realmente executa e persiste. No fim, "tocou três vezes" vira "aconteceu uma vez, respondido três vezes" — que é exatamente a resposta que devemos à Ana.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 820 260" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="idem-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <text x="20" y="24" font-family="sans-serif" font-size="12" fill="#666">chave: mesma intenção, nascida no cliente (= E2E ID)</text>
  <rect x="20" y="40" width="180" height="44" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="110" y="66" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">Toque 1 (original)</text>
  <rect x="20" y="100" width="180" height="44" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="110" y="126" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">Toque 2 (retry)</text>
  <rect x="20" y="160" width="180" height="44" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="110" y="186" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">Toque 3 (retry)</text>

  <line x1="200" y1="62" x2="320" y2="62" stroke="#888" stroke-width="2" marker-end="url(#idem-arrow)"/>
  <line x1="200" y1="122" x2="320" y2="122" stroke="#888" stroke-width="2" marker-end="url(#idem-arrow)"/>
  <line x1="200" y1="182" x2="320" y2="182" stroke="#888" stroke-width="2" marker-end="url(#idem-arrow)"/>

  <rect x="320" y="70" width="220" height="110" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="430" y="95" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Registro de idempotência</text>
  <text x="430" y="118" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">estado: em andamento → concluído</text>
  <text x="430" y="138" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">1ª vez: executa e grava</text>
  <text x="430" y="158" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">2ª/3ª: devolve o mesmo resultado</text>

  <line x1="540" y1="125" x2="620" y2="125" stroke="#166534" stroke-width="2" marker-end="url(#idem-arrow)"/>
  <rect x="620" y="90" width="180" height="70" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="710" y="118" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">1 débito no ledger</text>
  <text x="710" y="138" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">3 respostas idênticas</text>

  <text x="410" y="230" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#666">"tocou 3×" → "aconteceu 1×, respondido 3×"</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A chave de idempotência colapsa três tentativas na mesma intenção — só a primeira executa de verdade.</p>
</div>

### 3.4 O Banco Central já projetou isso para vocês: o EndToEndId

Aqui vai uma boa notícia: o Pix já embute idempotência no próprio protocolo. Toda transação carrega um **EndToEndId**, ou **E2E ID** — um identificador único de 32 caracteres, formado pelo prefixo `E`, mais o **ISPB** do participante (o código de 8 dígitos que identifica cada instituição no Sistema de Pagamentos Brasileiro), mais um timestamp, mais um componente aleatório. Esse identificador acompanha a transação do pagador até o recebedor, atravessando o SPI inteiro. Ele é, naturalmente, a chave de deduplicação e de rastreamento.

Quando o regulador exige que o E2E ID seja único, ele está — e isso é bom — obrigando vocês a construir efeito exactly-once. Guardem essa frase: o pagamento fantasma foi proibido por desenho regulatório. Cabe a vocês, na implementação, honrar esse desenho.

### 3.5 Os modos de falha que todo arquiteto de pagamento carrega na cabeça

Deixa eu resumir numa tabela os cenários de falha e o que muda com o design certo:

| Falha | Sem projeto | Com o design certo |
|---|---|---|
| Timeout + retry do cliente | Débito duplicado | Mesmo resultado devolvido, 1 débito |
| Duas requisições concorrentes (mesma chave) | *Lost update*, duplicação | Serializadas pelo estado "em andamento" |
| Crash entre debitar e confirmar ao SPI | Dinheiro "reservado" preso | Estado explícito no log → retomável |
| Resposta do SPI se perde | Incerteza sobre a liquidação | Reconciliação por E2E ID resolve |

---

## 4. Trade-offs: CAP, PACELC, e o orçamento de latência

Se a seção anterior foi sobre correção, essa aqui é sobre o **ofício** do arquiteto: escolher, de olhos bem abertos, onde vocês vão pagar o custo. Isso, para mim, é o coração do System Design.

### 4.1 CAP — e o erro que quase todo mundo comete

Vocês provavelmente já ouviram falar do teorema CAP, formulado por Eric Brewer, um cientista da computação. Ele diz que, num sistema distribuído, entre **C**onsistência, **A**vailability — disponibilidade — e tolerância a **P**artição — a rede se dividir em pedaços que não conseguem se falar —, vocês só conseguem escolher duas.

O erro que quase todo mundo comete é tratar isso como um cardápio livre. Na prática, **partição não é opcional**: cabos se rompem, redes se dividem, isso vai acontecer, ponto final. Então P já está dado, queiram vocês ou não. O que o teorema realmente diz é: **quando existe uma partição, vocês escolhem entre C e A** — ou recusam operar, para não divergir, e aí escolhem C; ou continuam operando, aceitando uma divergência temporária, e aí escolhem A. Fora da situação de partição, o CAP simplesmente não fala nada. E é exatamente aí que ele fica insuficiente.

### 4.2 PACELC — o quadro que fintech realmente precisa

Um pesquisador de bancos de dados distribuídos chamado Daniel Abadi completou essa ideia com o que ele chamou de PACELC: *if Partition then Availability or Consistency, Else then Latency or Consistency*. Em português: se há partição, escolham entre disponibilidade e consistência; senão — "else" —, escolham entre latência e consistência.

Ou seja: **mesmo sem falha nenhuma**, existe um trade-off permanente entre latência e consistência. Manter réplicas fortemente consistentes custa coordenação, e coordenação custa milissegundos. E como uma fintech passa a maior parte do tempo **sem** nenhuma partição de rede, o PACELC é o quadro certo para vocês: na prática, é entre latência e consistência que vocês vão decidir o tempo inteiro.

### 4.3 Consistência é um espectro, não um interruptor liga-desliga

Do mais forte para o mais fraco: **linearizável**, onde tudo parece acontecer numa ordem global única; depois sequencial; depois **causal**; e por fim **eventual**, que converge desde que as escritas parem de acontecer. Quanto mais forte a consistência, mais coordenação ela exige, mais latência ela custa, e menos disponível o sistema fica quando algo falha.

E aqui eu quero desarmar um mito com vocês: **"eventual" não quer dizer "errado"**. Quer dizer "correto, com um atraso limitado". Ver o extrato com 200 milissegundos de atraso não machuca ninguém. Debitar a conta errada, sim.

### 4.4 Como os grandes sistemas escolheram

Para isso não ficar abstrato, olhem como sistemas reais se posicionaram nesse espectro:

| Sistema | Posição no PACELC | O que isso ensina |
|---|---|---|
| **Google Spanner** | PC / PC | Dá para ter consistência forte **global**, usando um sistema chamado TrueTime — relógios do Google sincronizados por GPS e relógios atômicos, que limitam o quanto os relógios de datacenters diferentes podem divergir —, pagando o preço em latência. |
| **DynamoDB / Cassandra** | PA / EL | Nascem disponíveis e rápidos; a consistência é ajustável quando vocês realmente precisam dela. |
| **PostgreSQL** (um nó só) | consistência forte, trivial | O desafio só aparece quando vocês começam a replicar. |

A lição aqui não é "qual banco é melhor". É: **qual trade-off este pedaço específico do meu sistema exige.**

### 4.5 Aplicando isso ao TechPix — a decisão que resolve 80% do problema

No nosso sistema, a decisão fica assim:

- **Ledger, o núcleo** → consistência **forte**, linearizável. A gente aceita pagar latência para nunca criar ou destruir dinheiro.
- **Extrato, feed, saldo exibido, notificações** → consistência **eventual**. A gente aceita 100 a 300 milissegundos de atraso para escalar as leituras — que são muito mais numerosas que as escritas — e ganhar disponibilidade.

Essa única linha — forte no núcleo, eventual na borda — resolve **80% da arquitetura de dados** de uma fintech. E ela é a justificativa para o CQRS, que a Aula 2 vai aprofundar, para as fronteiras de consistência por bounded context, que é assunto da Aula 3, e para a validação em produção, que fecha o curso na Aula 8.

### 4.6 O orçamento de latência e a tirania da cauda

Latência não é um número — é uma **distribuição**. Vocês vão ouvir falar de p50, que é a mediana, p99, e p99.9, que é a cauda extrema. Na fintech, quem manda é a cauda, porque é nela que o cliente desiste, o timeout dispara, e o retry nasce — voltando exatamente ao problema que a gente viu na seção de idempotência. Otimizar só a média e ignorar o p99 é otimizar para o dia bom e quebrar no dia ruim.

E aqui eu preciso corrigir um mito que todo mundo repete: o Pix **tem**, sim, um orçamento de latência explícito e normativo — mas ele não é de 10 segundos. O *Manual de Tempos do Pix*, na versão 7.0, publicado pelo Banco Central, fixa o limite máximo em **40 segundos** ponta a ponta — do que o manual chama de t0' até t4 — para um Pix que segue pelo canal primário do SPI. Se não liquidar dentro desses 40 segundos, a transação é rejeitada, conforme a Resolução BCB nº 195 de 2022.

O "10 segundos" que todo mundo repete por aí **não é normativo** — é um número arredondado, de comunicação. Os tempos reais que o próprio Banco Central publica são bem menores que isso: o SPI liquida com **p50 de 2,8 segundos e p99 de 4,6 segundos**, e a consulta ao DICT tem um SLA de **p99 menor ou igual a 1 segundo**. Então o teto de 40 segundos é bem folgado — a experiência-alvo real é de poucos segundos —, e cada componente do caminho gasta uma fatia desse orçamento.

O trabalho do arquiteto é **distribuir e defender** esse orçamento. E toda vez que alguém, no meio de uma reunião de arquitetura, propuser mais uma chamada síncrona no caminho crítico, a pergunta certa é: "de qual fatia do orçamento essa chamada vai sair — e o que acontece com essa fatia quando o sistema estiver no pico?" Guardem essa pergunta, porque é literalmente o enredo da Aula 2, quando o DICT — o diretório de chaves do Pix, que eu vou explicar em detalhe já já — síncrono estoura sob carga.

---

## 5. A infraestrutura real: o Pix e o Banco Central

A partir daqui, o curso deixa de ser genérico. Eu quero que vocês entendam o **encanamento de verdade** do sistema financeiro brasileiro — é isso que torna a arquitetura real, e não um exercício de faculdade. Tratem essa seção como um estudo de System Design de uma plataforma nacional que movimenta trilhões de reais.

### 5.1 O SPB, numa imagem só

Antes de mais nada, uma correção rápida: **Pix não é sigla** — é o nome da marca do sistema brasileiro de pagamentos instantâneos, criado pelo Banco Central.

O **SPB**, o Sistema de Pagamentos Brasileiro, é o conjunto de trilhos que move dinheiro no país, sob operação e regulação do próprio Banco Central. Para a arquitetura do Pix, quatro peças desse conjunto importam de verdade:

- o **SPI** — o motor de liquidação instantânea, o "trilho do Pix" propriamente dito;
- o **DICT** — o diretório de chaves;
- o **STR** — o trilho de alto valor, onde a TED liquida;
- e a **RSFN** — a rede segura que conecta as instituições ao Banco Central.

Guardem esse modelo mental: o Banco Central é, ao mesmo tempo, **operador de infraestrutura** — ele roda o SPI e o DICT —, **regulador** — impõe SLAs, limites, regras de segurança — e **liquidante final** — o dinheiro liquida em moeda de banco central. Poucos sistemas no mundo concentram tanto papel numa entidade só, e isso molda tudo que vocês vão construir em cima dele.

### 5.2 Quem é quem: a topologia de participantes

Nem toda instituição fala com o SPI da mesma forma, e essa distinção muda a arquitetura de verdade:

- **Participante direto**: liquida no SPI com a própria conta no Banco Central, chamada de **Conta PI**, ou Conta de Pagamentos Instantâneos. Ele precisa manter saldo nessa conta para conseguir pagar.
- **Participante indireto**: acessa o Pix através de um liquidante, que é um participante direto. Tem menos custo de infraestrutura, mas mais dependência de terceiros.
- O **PSP**, Prestador de Serviço de Pagamento, é o papel de negócio — quem efetivamente oferece o Pix para o usuário final: bancos, fintechs, instituições de pagamento.
- E existe também o **PSTI**, Provedor de Serviços de Tecnologia da Informação: uma empresa autorizada pelo Banco Central a operar a infraestrutura de rede, a RSFN, para outros participantes. Ele presta o "encanamento", sem nunca interagir diretamente com o usuário final.

E vejam a decisão de System Design que nasce exatamente daqui: **ser direto ou indireto** é um trade-off clássico — controle e custo unitário de um lado, investimento e obrigações regulatórias do outro. É exatamente o tipo de decisão que a gente formaliza num **ADR**, um Architecture Decision Record, um registro formal de decisão de arquitetura que eu vou explicar em detalhe no final da aula.

### 5.3 O SPI: a liquidação em moeda de banco central

O SPI liquida cada Pix **individualmente, em tempo real, de forma final, 24 horas por dia, 7 dias por semana**, em **moeda de banco central** — ou seja, no saldo das contas que os participantes mantêm no próprio Banco Central. "Moeda de banco central" é o detalhe que elimina o risco de crédito entre bancos: quem efetivamente move o valor é o Banco Central, então a liquidação é **irrevogável** no instante em que acontece.

E aqui vai um modelo mental crucial para vocês como arquitetos: **a fintech de vocês não tem o dinheiro do cliente circulando por aí.** O que vocês mantêm é saldo na Conta PI, dentro do Banco Central; o SPI debita e credita essa conta a cada Pix. O ledger interno de vocês precisa **espelhar e reconciliar** com o que acontece nessa conta — e reconciliação, ou seja, bater o livro de vocês contra o livro do Banco Central, é uma disciplina de engenharia por si só. Uma falha silenciosa aqui vira dinheiro divergente, e dinheiro divergente vira incidente regulatório.

### 5.4 O DICT: o diretório — e por que ele é um problema de arquitetura fascinante

O **DICT**, o Diretório de Identificadores de Contas Transacionais, mapeia uma chave — CPF, CNPJ, telefone, e-mail, ou a chave aleatória, também chamada de **EVP** — para os dados da conta e do titular. (E aqui uma nota de honestidade: o Banco Central não divulga publicamente o significado por extenso da sigla EVP; na prática, é só uma sequência de caracteres sem significado, gerada pelo próprio DICT.) O DICT é, essencialmente, a "agenda" do Pix.

Mas para nós, arquitetos, ele é três desafios ao mesmo tempo, e eu quero passar pelos três com vocês.

O primeiro: **ele está no caminho crítico, e é síncrono.** Toda transação feita por chave começa com uma consulta ao DICT. Isso consome parte do orçamento de latência, e ao mesmo tempo acopla vocês à disponibilidade de um sistema externo. A forma como vocês chamam esse serviço — timeout agressivo, circuit breaker, algum fallback — decide se um soluço no DICT derruba os pagamentos de vocês inteiros ou não.

O segundo: **ele é protegido contra varredura, por um mecanismo de token bucket.** O diretório contém dado pessoal — o nome por trás de cada chave —, e para impedir varredura em massa, o DICT aplica limitação de requisições usando o algoritmo de token bucket, com políticas documentadas oficialmente na API do DICT. No escopo de usuário final, uma pessoa física tem 2 tokens por minuto, com um balde de 100 tokens; uma pessoa jurídica tem 20 tokens por minuto, com balde de 1.000. No escopo de participante, o limite varia por categoria — vai de 25 mil tokens por minuto, com balde de 50 mil, na categoria A, até apenas 2 tokens por minuto, balde de 50, na categoria H.

E aqui está o detalhe que eu acho genial, e que eu quero que vocês guardem: uma consulta que **encontra** a chave, ou seja, retorna HTTP 200, custa **1 token**. Uma consulta que **não encontra**, retornando HTTP 404, custa **20 tokens**. Ou seja: procurar chaves que não existem — que é exatamente o padrão de quem está fazendo scraping — esvazia o balde vinte vezes mais rápido. Quando o balde zera, o sistema responde com HTTP 429, "requisições demais". Isso é design de segurança por incentivo: o custo assimétrico do 404 pune quem está varrendo o diretório, sem punir quem está usando normalmente.

A consequência de design para vocês é direta: não dá para consultar o DICT à vontade. Vocês precisam de cache disciplinado, respeitando as regras de retenção; precisam consolidar consultas; precisam tratar a chave como um recurso caro; e, principalmente, precisam validar localmente antes de consultar, para não gerar 404 à toa. Isso é resiliência e compliance na mesma decisão de design.

O terceiro desafio: **ele tem SLA regulatório, com números de verdade.** O manual oficial chama isso de **ANS**, Acordo de Nível de Serviço; eu vou usar "SLA" ao longo da aula, por ser o termo mais comum em engenharia, mas é a mesma ideia. O *Manual de Tempos* define que a consulta de chaves tem p99 de até 1 segundo, e a atualização, p99 de até 5 segundos. E impõe um índice de disponibilidade aos participantes, com meta de 100% e valores de referência entre 80% e 90% por categoria — sendo que a única função do DICT que conta para esse índice de disponibilidade é a consulta. Vocês herdam esses SLAs: o sistema de vocês também vai ser medido por eles.

E o DICT não para na consulta: ele também gerencia a **reivindicação de posse de chave** — o que se chama de *claim*, quando vocês portam um número e a chave migra de instituição — e o **relato de infração**, que é a base do MED, o trilho de devolução que eu já mencionei. Então o DICT não é só "consulta"; é um sistema completo de gestão de identidade transacional, com fluxos de posse, disputa e fraude.

### 5.5 A anatomia de um Pix, passo a passo

Agora deixa eu traçar com vocês o caminho completo de um Pix, usando o nosso exemplo: Ana, no TechPix, mandando dinheiro para Bruno, no Banco Beta. Esse é, para mim, o fluxo mais importante da aula inteira.

Primeiro, o app da Ana manda para o TechPix a ordem: chave e valor. Segundo, o TechPix consulta o **DICT** com a chave do Bruno, e recebe de volta a instituição, a conta e o titular — gastando parte do orçamento de latência, e sujeito ao rate limit que a gente acabou de ver. Terceiro, o TechPix faz as validações locais: saldo, limites — inclusive o limite noturno —, antifraude, e **PLD-FT**, que significa Prevenção à Lavagem de Dinheiro e ao Financiamento do Terrorismo. Na dúvida, a regra é falhar fechado.

Quarto, o TechPix reserva no ledger: débito na carteira da Ana, crédito numa conta de "a liquidar", com idempotência garantida pelo E2E ID que a gente já viu. Quinto, o TechPix envia ao **SPI** a mensagem `pacs.008` — a instrução de pagamento, no padrão ISO 20022 —, carregando esse mesmo E2E ID. Sexto, o SPI debita a Conta PI do TechPix e credita a Conta PI do Banco Beta, em moeda de banco central, de forma final e irrevogável. Sétimo, o SPI responde com a mensagem `pacs.002`, confirmando que liquidou; o TechPix reconcilia o próprio ledger, e o Banco Beta credita o Bruno. E, na borda, de forma assíncrona, saem as notificações, o extrato é atualizado, o feed é atualizado.

E se alguma coisa der errado — falha ou fraude —, entra em cena a mensagem `pacs.004`, de devolução, e possivelmente o trilho do MED.

Reparem: os seis primeiros passos precisam caber dentro do teto de 40 segundos, sendo que o próprio SPI roda com p99 de 4,6 segundos. E reparem também em quantos sistemas **externos** — o DICT, o SPI, o banco do recebedor — estão nesse caminho crítico. Cada um deles é, ao mesmo tempo, um ponto de falha e uma fatia de latência. Por isso eu digo: projetar o Pix é, em grande parte, projetar a resiliência contra dependências externas que vocês não controlam.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 380" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="pix-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <!-- Lanes -->
  <g font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">
    <text x="60" y="24" text-anchor="middle">App Ana</text>
    <text x="240" y="24" text-anchor="middle">TechPix</text>
    <text x="420" y="24" text-anchor="middle">DICT</text>
    <text x="600" y="24" text-anchor="middle">SPI</text>
    <text x="800" y="24" text-anchor="middle">Banco Beta / Bruno</text>
  </g>
  <line x1="60" y1="34" x2="60" y2="360" stroke="#ccc" stroke-width="1.5"/>
  <line x1="240" y1="34" x2="240" y2="360" stroke="#ccc" stroke-width="1.5"/>
  <line x1="420" y1="34" x2="420" y2="360" stroke="#ccc" stroke-width="1.5"/>
  <line x1="600" y1="34" x2="600" y2="360" stroke="#ccc" stroke-width="1.5"/>
  <line x1="800" y1="34" x2="800" y2="360" stroke="#ccc" stroke-width="1.5"/>

  <!-- Step 1 -->
  <line x1="60" y1="55" x2="240" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#pix-arrow)"/>
  <text x="150" y="48" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">1. chave + valor</text>

  <!-- Step 2 -->
  <line x1="240" y1="85" x2="420" y2="85" stroke="#4338ca" stroke-width="2" marker-end="url(#pix-arrow)"/>
  <text x="330" y="78" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">2. consulta chave (p99 ≤ 1s)</text>
  <line x1="420" y1="110" x2="240" y2="110" stroke="#4338ca" stroke-width="2" marker-end="url(#pix-arrow)"/>
  <text x="330" y="103" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">conta + titular</text>

  <!-- Step 3 -->
  <rect x="190" y="125" width="100" height="34" rx="6" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="240" y="147" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">3. valida local</text>

  <!-- Step 4 -->
  <rect x="190" y="170" width="100" height="34" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="240" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">4. reserva no ledger</text>

  <!-- Step 5 -->
  <line x1="240" y1="220" x2="600" y2="220" stroke="#4338ca" stroke-width="2" marker-end="url(#pix-arrow)"/>
  <text x="420" y="213" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">5. pacs.008 (E2E ID)</text>

  <!-- Step 6 -->
  <rect x="550" y="235" width="100" height="34" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="600" y="257" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">6. liquida Conta PI</text>

  <!-- Step 7 -->
  <line x1="600" y1="285" x2="240" y2="285" stroke="#166534" stroke-width="2" marker-end="url(#pix-arrow)"/>
  <text x="420" y="278" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">7. pacs.002 (confirmação)</text>
  <line x1="600" y1="310" x2="800" y2="310" stroke="#166534" stroke-width="2" marker-end="url(#pix-arrow)"/>
  <text x="700" y="303" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">credita Bruno</text>

  <rect x="20" y="330" width="860" height="34" rx="6" fill="#fef9e7" stroke="#d4a017"/>
  <text x="450" y="352" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7a5c00">Passos 1–6 cabem dentro do teto de 40s (SPI real: p99 4,6s) · 3 sistemas externos no caminho crítico: DICT, SPI, banco do recebedor</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Anatomia de um Pix, ponta a ponta — cada seta é uma fatia do orçamento de latência.</p>
</div>

### 5.6 O orçamento decomposto, com os números oficiais

Deixa eu desenhar esse orçamento com os números que o próprio Banco Central publica, para vocês visualizarem onde o tempo vai:

```
Teto normativo ≈ 40.000 ms   (canal primário do SPI, t0'→t4 · Res. BCB 195/2022)
  ├─ consulta ao DICT      SLA p99 ≤ 1.000 ms      (externo, rate-limited, cacheável)
  ├─ validações + antifraude   (o tempo de vocês — a maior fatia controlável)
  ├─ reserva no ledger     (o custo da consistência forte — o nosso ADR-001)
  ├─ liquidação no SPI     p50 2.800 ms · p99 4.600 ms   (externo)
  └─ folga                 (o teto de 40 s é generoso; a experiência-alvo é de poucos segundos)
```

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 160" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="20" font-family="sans-serif" font-size="12" fill="#666">Teto normativo: 40.000 ms (barra inteira) — experiência-alvo real fica nos primeiros milímetros dela</text>
  <rect x="20" y="30" width="860" height="40" rx="6" fill="#f3f4f6" stroke="#999"/>
  <!-- segments, widths scaled roughly to relative weight for legibility, not literal ms-to-px -->
  <rect x="20" y="30" width="60" height="40" fill="#93c5fd" stroke="#1d4ed8"/>
  <rect x="80" y="30" width="140" height="40" fill="#fde68a" stroke="#b45309"/>
  <rect x="220" y="30" width="120" height="40" fill="#c7d2fe" stroke="#4338ca"/>
  <rect x="340" y="30" width="120" height="40" fill="#bbf7d0" stroke="#166534"/>
  <rect x="460" y="30" width="420" height="40" fill="#ffffff" stroke="#999" stroke-dasharray="4 3"/>
  <text x="450" y="90" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">
    <tspan x="450" dy="0"></tspan>
  </text>
  <g font-family="sans-serif" font-size="11" fill="#333">
    <text x="50" y="86" text-anchor="middle">DICT</text>
    <text x="50" y="100" text-anchor="middle" fill="#666">p99 ≤ 1s</text>
    <text x="150" y="86" text-anchor="middle">validações +</text>
    <text x="150" y="100" text-anchor="middle">antifraude (a maior fatia sua)</text>
    <text x="280" y="86" text-anchor="middle">reserva no</text>
    <text x="280" y="100" text-anchor="middle">ledger (ADR-001)</text>
    <text x="400" y="86" text-anchor="middle">SPI</text>
    <text x="400" y="100" text-anchor="middle" fill="#666">p50 2,8s · p99 4,6s</text>
    <text x="670" y="86" text-anchor="middle" fill="#666">folga até o teto de 40s</text>
  </g>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Larguras aproximadas, para dar noção de proporção — não é escala literal de milissegundos.</p>
</div>

Deixa eu bater na mesma tecla: o "10 segundos" que todo mundo repete **não é o número normativo**. O teto real, para o pior caso, é de **40 segundos**; a experiência-alvo, no dia a dia, é de poucos segundos — SPI com p99 de 4,6 segundos, DICT com p99 de 1 segundo. Só que sob pico — pensem numa véspera de feriado, ou 20h de um dia de pagamento de salário —, as filas incham, e o que era 300 milissegundos vira alguns segundos. E furar o SLA do DICT, ou a disponibilidade de vocês, tem consequência regulatória, não é só um incômodo técnico. É exatamente por isso que a Aula 2 começa quebrando esse orçamento.

E aqui vai a tabela com todos os números oficiais que eu usei, tirados diretamente do *Manual de Tempos do Pix*, versão 7.0:

| Indicador | Valor oficial |
|---|---|
| Tempo máximo do Pix — canal primário do SPI | **40 s** (de t0' a t4); se ultrapassar, é rejeitado |
| Canal secundário (agendado / cobrança com vencimento) | 45 minutos |
| Tempo gasto dentro do SPI (canal primário) | p50 **2,8 s** · p99 **4,6 s** |
| Consulta ao DICT | p99 **≤ 1 s** |
| Atualização no DICT | p99 **≤ 5 s** |
| Disponibilidade do SPI (meta) | **99,9%** |
| Disponibilidade dos participantes | meta 100% · referência de 80% a 90% por categoria |
| Pix Automático — autorização entra no **IGA** (o Índice Geral de ANS, o indicador agregado que resume o cumprimento dos SLAs) | desde **1º de julho de 2025** |

### 5.7 O STR e o alto valor

Nem tudo é Pix. A **TED** e as liquidações de grande valor rodam num outro trilho, o **STR**, o Sistema de Transferência de Reservas — também em tempo real, também em moeda de banco central. A lição de design aqui é simples: existem trilhos diferentes, com propriedades diferentes. O Pix foi desenhado para varejo instantâneo, 24 horas por dia; o STR, para alto valor. Escolher o trilho certo é, de novo, escolher um trade-off — e conhecer o cardápio inteiro faz parte do ofício de vocês.

### 5.8 O Pix não é estático

Eu quero deixar bem claro para vocês que essa infraestrutura **continua mudando**, porque a evolução do trilho é, ela mesma, um dos temas centrais desse curso.

O **Pix Automático** já está em produção — os indicadores do ciclo de autorização entraram no cálculo do IGA em 1º de julho de 2025, conforme o próprio Manual de Tempos. Ele permite pagamentos recorrentes a partir de uma autorização única, um mandato. Do ponto de vista de arquitetura, isso introduz um registro de mandatos e um fluxo de iniciação recorrente inteiramente novo — um domínio novo, com invariantes novas: o mandato pode ser revogado, a cobrança tem limites. É um ótimo exemplo para discutirmos bounded contexts, lá na Aula 3.

Tem também o **Pix por Aproximação**, via NFC: pagar encostando o celular, competindo diretamente com o cartão por aproximação. Ele muda a experiência na ponta, mas o núcleo de liquidação continua o mesmo.

O **MED**, o Mecanismo Especial de Devolução, é o trilho regulatório de devolução por fraude ou falha — o mais próximo de um "estorno" que o Pix tem. E ele evoluiu, recentemente, para incorporar um mecanismo bem mais interessante do ponto de vista de arquitetura, que eu quero detalhar numa seção própria daqui a pouco: a **Recuperação de Valores**, que transforma "devolver dinheiro" num problema de rastreamento de grafo.

E, no horizonte mais distante, existe o **Drex**, o Real Digital, uma moeda digital de banco central ainda em pilotos, construída sobre tecnologia de registro distribuído. A promessa ali é liquidação e dinheiro programável, via contratos inteligentes — mas isso é futuro, não é presente, e eu quero ser honesto com vocês sobre essa distinção.

O recado de arquitetura que eu quero que fique: a infraestrutura muda debaixo dos pés de vocês. Uma fintech precisa ser desenhada para **evoluir junto com o trilho**, não para resistir a ele. Esse é o fio que a Aula 2 puxa, e que a Aula 8 fecha.

### 5.9 Recuperação de Valores: rastreando fraude como um problema de grafo

Vou contar para vocês sobre o mecanismo mais tecnicamente interessante que o BACEN construiu recentemente, e que praticamente nenhum curso de arquitetura menciona. Na mídia e no mercado, ele é chamado de **MED 2.0** — a evolução do Mecanismo Especial de Devolução instituída pela **Resolução BCB nº 493, de 28/8/2025**, que se tornou obrigatória para todos os participantes do Pix a partir de **2 de fevereiro de 2026**. Tecnicamente, ela é especificada pelo *Guia de Implementação do MED*, versão 4.3, com uma versão 4.4 já publicada e com vigência a partir de setembro e outubro de 2026.

O problema que ele resolve é o seguinte: quando alguém é vítima de fraude e o dinheiro é devolvido pelo mecanismo tradicional do MED, isso só funciona se o dinheiro **ainda estiver** na conta de quem recebeu o Pix fraudulento. Só que fraudadores sofisticados não deixam o dinheiro parado — eles pulverizam o valor, transferindo para uma segunda conta, depois uma terceira, numa cadeia de saltos, exatamente para que, quando a vítima perceber e notificar, o dinheiro já tenha "sumido" da conta original.

A resposta do BACEN a isso, a **Recuperação de Valores**, transforma a devolução num problema de **rastreamento de grafo**: a partir da transação original — a "transação raiz" —, o sistema mapeia o caminho que os recursos percorreram, identificando as transações subsequentes para onde o dinheiro foi desviado. Pensem literalmente num grafo dirigido: a transação raiz é o nó inicial, cada transferência subsequente do mesmo dinheiro é uma aresta para um novo nó, e o rastreamento percorre esse grafo salto a salto — hoje, com o MED 2.0, até **cinco camadas** de transferências subsequentes, em qualquer instituição participante do Pix. E o resultado prático é poderoso: **todas as contas identificadas nesse rastreamento contribuem para a recuperação**, não só a conta do primeiro recebedor — e os usuários recebedores encontrados ao longo desse fluxo de desvio também podem ser marcados como fraudadores no próprio DICT, propagando o sinal de risco pela rede inteira de participantes.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 820 260" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="graf-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <text x="20" y="24" font-family="sans-serif" font-size="12" fill="#666">transação raiz → cada salto é uma nova aresta no grafo de rastreamento</text>

  <circle cx="80" cy="120" r="36" fill="#fef2f2" stroke="#b91c1c" stroke-width="2.5"/>
  <text x="80" y="116" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">Vítima</text>
  <text x="80" y="130" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">(raiz)</text>

  <line x1="116" y1="120" x2="200" y2="120" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#graf-arrow)"/>
  <text x="158" y="110" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">Pix fraude</text>

  <circle cx="240" cy="120" r="36" fill="#fff7ed" stroke="#c2410c" stroke-width="2.5"/>
  <text x="240" y="124" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">Conta A</text>

  <line x1="276" y1="120" x2="360" y2="120" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#graf-arrow)"/>
  <text x="318" y="110" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">salto 2</text>

  <circle cx="400" cy="120" r="36" fill="#fff7ed" stroke="#c2410c" stroke-width="2.5"/>
  <text x="400" y="124" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">Conta B</text>

  <line x1="428" y1="95" x2="500" y2="55" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#graf-arrow)"/>
  <circle cx="540" cy="45" r="34" fill="#fff7ed" stroke="#c2410c" stroke-width="2.5"/>
  <text x="540" y="49" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">Conta C</text>

  <line x1="428" y1="145" x2="500" y2="185" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#graf-arrow)"/>
  <circle cx="540" cy="195" r="34" fill="#fff7ed" stroke="#c2410c" stroke-width="2.5"/>
  <text x="540" y="199" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7c2d12">Conta D</text>

  <rect x="610" y="90" width="190" height="60" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="705" y="112" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">Todas contribuem</text>
  <text x="705" y="130" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">p/ recuperação, não só a 1ª</text>

  <line x1="705" y1="90" x2="574" y2="55" stroke="#166534" stroke-width="1.5" stroke-dasharray="3 3"/>
  <line x1="705" y1="150" x2="574" y2="190" stroke="#166534" stroke-width="1.5" stroke-dasharray="3 3"/>

  <text x="410" y="235" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">MED 2.0 (Res. BCB 493/2025) — até 5 camadas · SLA p99 6h (fraude) · bloqueio cautelar até 72h</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Recuperação de Valores como travessia de grafo dirigido: cada conta no caminho vira nó recuperável.</p>
</div>

Duas regras de negócio que valem a pena vocês guardarem, porque mostram como esse grafo é modelado com cuidado: cada transação só pode ser a **raiz** de uma única Recuperação de Valores por vez — mesmo que essa recuperação seja cancelada, não se pode abrir outra tendo a mesma transação como raiz —, mas essa mesma transação **pode aparecer no grafo de rastreamento de outras Recuperações de Valores**, como um nó não-raiz. Isso evita duplicidade de "casos" abertos sobre a mesma origem, sem impedir que uma transação legitimamente pertença a mais de uma cadeia de investigação.

Do ponto de vista de System Design, pensem no tamanho do desafio: esse rastreamento **não acontece dentro de uma única empresa**. O dinheiro salta entre contas que podem estar em instituições completamente diferentes — TechPix, Banco Beta, uma terceira fintech. Isso exige um mecanismo de travessia de grafo **federado**, coordenado pelo DICT como autoridade central de marcação, onde cada participante precisa: aceitar bloqueios de valores vindos de investigações iniciadas por outra instituição, propagar a marcação de fraude para o restante da rede, e fazer tudo isso dentro de janelas de tempo regulatórias — não é um "quando der".

E o BACEN definiu essas janelas com precisão, no *Manual de Tempos do Pix*: a conclusão de uma solicitação de devolução por fundada suspeita de fraude tem SLA de **p99 de 6 horas**, do momento em que a solicitação é aberta no DICT até sua conclusão — um salto e tanto em relação ao mecanismo anterior ao MED 2.0, que garantia só 24 horas em 95% dos casos; para devolução por falha operacional do PSP pagador, o SLA é mais folgado, **p95 de 48 horas**. Além disso, existe o **bloqueio cautelar** — um congelamento preventivo de até **72 horas**, que o PSP do recebedor pode aplicar sobre os recursos quando há suspeita de fraude, para dar tempo de uma avaliação mais detalhada antes de decidir se devolve. E, com o MED 2.0, o rastreamento por grafo entre as cinco camadas de contas continua ativo por até **11 dias após a contestação**, para dar tempo de bloquear o dinheiro mesmo que ele já tenha saltado várias vezes antes da vítima notificar. E, tecnicamente, toda devolução no âmbito do MED viaja como uma mensagem `pacs.004` com o campo `codigoDevolucao` preenchido com o código **`MD06`** — o mesmo tipo de mensagem que a gente já viu no fluxo normal do Pix, só que carregando essa marca específica.

Vale registrar também que existe uma via mais simples, para quando não há fraude nenhuma envolvida: o próprio usuário recebedor pode devolver, por iniciativa própria, qualquer Pix que tenha creditado sua conta, dentro de **90 dias** da transação original — valor total ou parcial, com múltiplas devoluções parciais permitidas até completar o valor. Essa via não precisa de investigação nenhuma; é uma decisão discricionária do recebedor.

Para o contexto de **Devoluções**, que a gente vai desenhar como bounded context próprio na Aula 3, isso muda a conversa: não é mais só "receber uma notificação e devolver dinheiro" — é operar, em tempo quase real, um algoritmo de busca em grafo sobre dados financeiros sensíveis, coordenado com outras instituições, dentro de SLAs regulatórios apertados. Se vocês já trabalharam com grafos de fraude, detecção de anel de lavagem de dinheiro, ou sistemas de recomendação por proximidade em grafo, o paralelo técnico é direto — só que aqui o grafo não é sobre relevância de conteúdo, é sobre para onde o dinheiro roubado de alguém foi parar.

### 5.10 Resumindo: o que o Banco Central impõe à arquitetura de vocês

Antes de seguir para a parte de inteligência artificial, deixa eu consolidar tudo que vimos numa única tabela:

| O que o Banco Central impõe | A restrição concreta | A decisão de arquitetura que ela força |
|---|---|---|
| SPI liquida em moeda de banco central, de forma final | Liquidação irrevogável; vocês precisam espelhar a Conta PI | Ledger forte + reconciliação contínua |
| DICT síncrono no caminho crítico | Latência somada + acoplamento a um sistema externo | Timeout, circuit breaker, cache disciplinado |
| DICT com anti-scraping por token bucket (404 custa 20× mais) | Risco de HTTP 429 ao estourar o balde | Cache, consolidação de consultas, evitar 404, tratar a chave como recurso caro |
| SLA de disponibilidade exigido pelo regulador | Patamares altos, monitorados | Redundância, degradação graciosa, plano de contingência |
| Teto normativo de 40 segundos (SPI real com p99 de 4,6 s) | Limite regulatório entre t0' e t4 | Distribuir e defender o orçamento; jogar o que puder para a borda, de forma assíncrona |
| MED 2.0 (Res. BCB 493/2025, obrigatório desde 2/2/2026): Recuperação de Valores por fraude (p99 6 h), rastreamento em até 5 camadas, bloqueio cautelar (até 72 h) | Rastreamento de grafo federado, entre instituições, sob SLA apertado | Bounded context de Devoluções com integração cross-institucional e busca em grafo |
| Evolução constante — Pix Automático, Drex | O trilho não para de mudar | Arquitetura evolutiva (Aulas 2, 6 e 8) |

---

## 6. A inteligência artificial como novo eixo da arquitetura

Chegamos na parte que eu considero o diferencial desse curso, e que é o gancho direto para a Aula 8. A minha tese é esta: **a inteligência artificial não é uma funcionalidade que se adiciona a um sistema — ela muda o que significa, hoje, arquitetar.** Eu vou apresentar quatro disciplinas para vocês, como um sistema coerente, todas ancoradas no que a gente já construiu até aqui.

### 6.1 A virada: de arquitetura-documento para arquitetura-loop

Historicamente, arquitetar seguia essa sequência: pensar, decidir, documentar — e o documento, com o tempo, apodrecia numa gaveta. Com agentes de IA no jogo, esse ciclo vira **executável e contínuo**: a especificação permanece viva, o agente implementa e refatora o sistema em cima dela, e a produção realimenta as próprias decisões arquiteturais. O arquiteto deixa de ser "quem desenha uma vez" e passa a ser **quem projeta o loop inteiro** — as especificações, os guardrails, os sinais de retorno. As quatro disciplinas que eu vou explicar agora são exatamente as peças desse loop.

### 6.2 Spec-Driven Development — a especificação como fonte da verdade

A ideia central do **SDD**, Spec-Driven Development, é: a especificação, e as decisões que ela registra, são o artefato que manda; o código é derivado dela. Em vez do fluxo antigo — escrevo a spec, depois codo, e a spec apodrece — o fluxo vira: especificação, plano, tarefas, implementação assistida por um agente, com a especificação permanecendo viva o tempo todo.

E por que isso é System Design, e não só uma ferramenta bonitinha? Porque uma boa especificação **codifica as invariantes do domínio** — "Σ débitos igual Σ créditos", "saldo nunca fica negativo", "o E2E ID é único", "a resolução de chave respeita o rate limit do DICT". Essas invariantes, uma vez escritas na especificação, viram **testes automáticos** — as mesmas fitness functions que eu expliquei lá atrás. Ou seja: no mundo do SDD, **escrever a arquitetura com clareza É programar o sistema — e é, ao mesmo tempo, gerar o próprio aparato de validação dele.** A habilidade central do arquiteto passa a ser a precisão da especificação. Já existem ferramentas que materializam isso: o **GitHub Spec Kit**, um kit de código aberto para SDD que estrutura exatamente esse fluxo como comandos dentro do agente de código — uma constituição de princípios inegociáveis, e depois especificar, clarificar, planejar, quebrar em tarefas e implementar, cada passo gerando um artefato versionado no repositório (a Aula 3 roda esse fluxo na prática, sobre o nosso TechPix); o Kiro, uma IDE de IA da AWS orientada a spec; e o próprio Claude. O nosso ADR-001, que eu vou escrever com vocês daqui a pouco, é o primeiro artefato de SDD desse curso.

### 6.3 Context Engineering — projetando o que o agente sabe

Se a especificação diz *o quê*, o **contexto** é que determina se o agente consegue raciocinar corretamente sobre isso. Context Engineering é a disciplina — sucessora do que se chamava de "prompt engineering" — de encher a janela de contexto do agente com a informação certa, e só ela. Essa janela é um **recurso escasso**: enchê-la de lixo degrada o raciocínio do agente, o que se chama de "context rot"; deixá-la faltando o essencial produz alucinação.

Pensem comigo numa fintech: o que um agente precisa ter em contexto para propor uma mudança com segurança? A especificação do bounded context em questão, os ADRs relevantes — por que o ledger é forte, por exemplo —, o glossário do domínio, para não confundir "transferência" com "pagamento", os runbooks de incidente, e os dados de produção pertinentes. Projetar *como* essa informação chega até o agente — por recuperação de documentos, o que se chama de RAG, por memória persistente, por sub-agentes que isolam sub-tarefas, por compactação de contexto longo — é uma decisão de arquitetura tão real quanto escolher um banco de dados. Context Engineering é, na prática, arquitetura de informação para agentes.

### 6.4 Harness Engineering — o aparato de validação como arquitetura

A palavra "harness" vem de arreio, cinto de segurança. É o aparato que permite mudar o sistema com segurança — e isso vale tanto para mudanças feitas por humanos quanto por IA. Ele é composto pelas invariantes-como-teste que acabamos de ver, pelos **evals** — avaliações automáticas da qualidade da saída de um agente —, pelos **guardrails** — limites que uma mudança nunca pode violar, como "nenhuma alteração pode permitir saldo negativo" —, e pela entrega progressiva: feature flags, canary, rollback automático.

E aqui vai a minha tese de System Design sobre isso: **o Harness precisa ser projetado dentro do sistema, não pregado por fora depois.** Um sistema pronto para esse tipo de validação tem flags nos pontos certos, métricas de negócio instrumentadas, e a capacidade de reverter uma mudança em segundos. Numa fintech, é o Harness que torna aceitável deixar um agente **propor** mudanças em produção — porque nenhuma proposta escapa dos guardrails. Isso é a materialização em engenharia daquele princípio que eu falei lá no começo: correção acima de disponibilidade. Vocês vão colher isso por completo na Aula 8; a semente já está plantada na linha "Revisão" do ADR que a gente vai escrever daqui a pouco.

### 6.5 Looping Engineering — os dois loops

Aqui existem dois loops, um dentro do outro.

O primeiro é o **loop agêntico**, mais curto: o agente opera num ciclo de planejar, agir, observar, refletir — uma variação do que se chama **OODA**, observar-orientar-decidir-agir, um ciclo de decisão criado pelo estrategista militar John Boyd para ambientes que mudam rápido. Projetar bons loops agênticos é decidir quais ferramentas o agente tem à disposição, quando ele deve parar, e como ele se corrige sozinho.

O segundo é o **loop de feedback**, mais longo: a produção gera sinais, esses sinais alimentam uma avaliação, a avaliação propõe uma mudança, essa mudança é validada pelo Harness, e o resultado volta para a produção. Esse loop é inspirado no **RLHF**, Reinforcement Learning from Human Feedback: o sistema melhora a partir de feedback real, sempre com um humano no circuito nas decisões que realmente importam.

E aqui está a conexão direta com o que a gente viu hoje: "decidir na fé, depois decidir na evidência" é, exatamente, esse loop longo. O ADR-001 que a gente vai escrever é uma hipótese; a produção é o sinal que confirma ou refuta essa hipótese; e é a Aula 8 que fecha esse ciclo.

### 6.6 MCP — a arquitetura de integração dos agentes, e a governança em fintech

O **MCP**, Model Context Protocol, um protocolo aberto criado pela Anthropic, padroniza como um agente se conecta a ferramentas e fontes de dados — métricas, catálogos, APIs internas. Pensem nele como o "USB-C" da integração de agentes: em vez de vocês construírem N integrações artesanais, existe um protocolo comum.

E em fintech, é justamente no MCP que a **governança** vira uma decisão de arquitetura. A regra de ouro que eu quero que vocês memorizem é: **o agente LÊ a produção, PROPÕE mudanças, mas NUNCA move dinheiro.** A fronteira de permissão é desenhada nos próprios servidores MCP: um agente pode consultar o p99 do ledger e propor um novo ADR, mas ele não tem, literalmente não existe no sistema dele, a ferramenta para debitar uma conta ou alterar uma liquidação. Essa separação — a capacidade de observar e propor, sem a capacidade de executar o que é irreversível — é o que reconcilia "usar IA para evoluir o sistema" com "correção acima de disponibilidade", e também com as exigências do regulador: auditabilidade das decisões, e a LGPD. Eu diria até: **projetar a fronteira de permissão de um agente é a decisão de arquitetura mais importante ao trazer IA para dentro de uma fintech.**

### 6.7 O papel do arquiteto, revisitado

Juntando essas seis ideias: com IA no jogo, o arquiteto passa a escrever especificações precisas — isso é SDD —, a projetar o contexto que os agentes recebem — Context Engineering —, a construir o aparato de validação — o Harness —, a desenhar os loops de melhoria — Looping — e a definir as fronteiras de permissão — via MCP. O arquiteto não desaparece; ele sobe de altitude. Em vez de "como eu escrevo essa função", a pergunta vira "como esse sistema decide, valida e evolui — com humanos e agentes dentro do mesmo loop, sob as leis do dinheiro e do Banco Central".

---

## 7. Registrando a decisão: o ADR-001

Tudo que a gente viu até agora converge para um único artefato. Um **ADR**, Architecture Decision Record — um formato criado por Michael Nygard, um engenheiro de software que popularizou esse conceito em 2011 — é um documento curto, datado, e **imutável**, que registra uma única decisão: o contexto, a decisão em si, as consequências — de forma honesta, incluindo o custo —, as alternativas que foram descartadas, e um status, que vai de proposto, para aceito, até eventualmente substituído. Vocês nunca editam um ADR antigo; escrevem um novo, que o substitui. Assim, a história do pensamento arquitetural fica preservada — e um agente, lendo essa sequência de ADRs, entende *como o sistema pensou*, não só como ele está hoje.

Vamos escrever juntos o primeiro ADR do TechPix:

```
ADR-001 · Consistência forte no ledger do core          Status: Aceito (2025-07-30)

Contexto      O Pix é irreversível e liquida em moeda de banco central (SPI).
              O ledger não pode criar/destruir dinheiro nem permitir saldo
              negativo; cada movimento é auditável (BACEN/LGPD).
              Operamos sob teto normativo de 40 s ponta a ponta (SPI real: p99 4,6 s).
Decisão       Escrita no ledger será ACID e fortemente consistente
              (linearizável), síncrona no caminho crítico, idempotente
              pelo EndToEndId.
Consequências (+) Correção garantida; trilha de auditoria completa.
              (+) As invariantes viram testes — base do Harness.
              (−) Custo de latência na escrita — consome parte do teto de 40 s.
              (−) Escrita não escala na horizontal como a leitura.
Alternativas  Ledger eventual (REJEITADO: viola conservação/auditoria).
              Saldo em coluna única (REJEITADO: sem auditoria; não reconstruível).
Revisão       A consequência de latência será MEDIDA em produção. Se o p99
              ameaçar o SLA, reavaliar em novo ADR — via agente + MCP.
```

Reparem na última linha, "Revisão". Ela é uma promessa que amarra os dois grandes temas dessa aula: a decisão de hoje, tomada na fé, vai ser validada pela produção, com evidência. Pelo caminho, a Aula 2 ainda vai complementar essa decisão com um ADR próprio — sem contradizê-la —, e é só na Aula 8, depois de meses de dados reais, que um agente, conectado via MCP, participa do loop propondo, sempre sob guardrails, um novo ADR. É assim que a Aula 1 e a Aula 8 se costuram.

---

## 8. Para fechar: da fé à evidência

Antes de encerrar, deixa eu recapitular com vocês as três ideias-âncora dessa aula.

Primeiro: **o ledger é a verdade.** O dinheiro é conservado, o saldo é só uma projeção, e o passado é imutável.

Segundo: **idempotência é correção sob incerteza.** A rede é ambígua por natureza, e a chave de idempotência transforma "tentou N vezes" em "aconteceu uma vez".

Terceiro: **trade-off explícito é o ofício do arquiteto.** CAP e PACELC, orçamento de latência, forte no núcleo e eventual na borda — e tudo isso registrado formalmente num ADR.

E antes do gancho final, deixa eu inaugurar um ritual que vai se repetir no fim de cada aula desse curso: uma foto do TechPix como ele está **hoje**. A gente vai construir essa fintech peça por peça, aula a aula — e essa régua é como vocês vão ver o sistema crescer. Hoje ela está inteira verde, porque tudo nasceu agora:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 210" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="450" y="26" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333">O TechPix ao fim da Aula 1</text>

  <rect x="20" y="50" width="160" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="100" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Monólito TechPix</text>
  <text x="100" y="96" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">uma aplicação,</text>
  <text x="100" y="110" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">um deploy</text>

  <rect x="196" y="50" width="170" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="281" y="74" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Ledger · PostgreSQL</text>
  <text x="281" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">partida dobrada, append-only,</text>
  <text x="281" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">serializable (Σ = Σ)</text>

  <rect x="382" y="50" width="160" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="462" y="74" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Idempotência</text>
  <text x="462" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">chave = E2E ID,</text>
  <text x="462" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">efeito exactly-once</text>

  <rect x="558" y="50" width="170" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="643" y="74" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">BACEN · DICT + SPI</text>
  <text x="643" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">síncronos no caminho crítico,</text>
  <text x="643" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">teto 40s · DICT p99 1s</text>

  <rect x="744" y="50" width="136" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="812" y="74" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">ADR-001</text>
  <text x="812" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">consistência forte,</text>
  <text x="812" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">decidida na fé</text>

  <rect x="20" y="150" width="860" height="34" rx="8" fill="#fff" stroke="#ccc" stroke-width="1"/>
  <text x="450" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">cinza = já existia · verde = construído nesta aula — hoje é tudo verde: o alicerce da fintech nasceu aqui</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A régua de evolução do TechPix: a cada aula, uma foto do que existe — e do que acabou de nascer.</p>
</div>

E aqui está a moldura que abriu essa aula inteira: **hoje, a gente decidiu na fé** — sem dados de produção, apoiados em princípios, no que o Banco Central exige, e na experiência. E isso foi o certo a se fazer. Mas guardem o ADR-001, porque um dia a produção — e um agente, operando sob guardrails, via MCP — vão ter opinião sobre ele. A Aula 8 troca fé por evidência, e fecha esse loop.

Deixo essa pergunta para vocês pensarem até lá: onde, no sistema de vocês, uma decisão está sendo tomada na fé, sem nenhuma evidência? Anotem. É exatamente aí que a arquitetura evolutiva — e a inteligência artificial — vão agir.

---

Isso fecha a aula de hoje. Deixo abaixo alguns glossários de apoio — consultem sempre que precisarem relembrar uma sigla ou um termo.

## Apêndice A — Glossário BACEN / Pix

| Sigla | O que é |
|---|---|
| **SPB** | Sistema de Pagamentos Brasileiro — o conjunto de trilhos, sob o BACEN. |
| **SPI** | Sistema de Pagamentos Instantâneos — liquida o Pix em tempo real, moeda de BC, 24/7. |
| **Conta PI** | Conta de Pagamentos Instantâneos no BC — onde o participante direto mantém saldo para liquidar Pix. |
| **DICT** | Diretório de chaves (chave → conta). Síncrono, com anti-scraping e SLA regulatório. |
| **STR** | Sistema de Transferência de Reservas — alto valor / TED. |
| **RSFN** | Rede do Sistema Financeiro Nacional — rede segura entre instituições e BC. |
| **E2E ID** | EndToEndId — identificador único de 32 caracteres, ponta a ponta. |
| **ISPB** | Código de 8 dígitos que identifica cada participante no SPB junto ao BACEN. |
| **Participante direto/indireto** | Liquida com conta própria no BC / via um liquidante. |
| **PSP** | Prestador de Serviço de Pagamento — quem oferece o Pix ao usuário final. |
| **PSTI** | Provedor de Serviços de Tecnologia da Informação — opera a infraestrutura de rede (RSFN) para outros participantes. |
| **MED** | Mecanismo Especial de Devolução — trilho regulatório de devolução por fraude/falha. |
| **MED 2.0** | Nome de mercado da evolução do MED trazida pela Resolução BCB nº 493/2025, obrigatória desde 2/2/2026: rastreamento em até 5 camadas de contas, bloqueio cautelar automático de 72h e SLA de conclusão em p99 de 6h para fraude. |
| **Recuperação de Valores** | Extensão do MED (parte do MED 2.0) que rastreia, por grafo, para onde o dinheiro fraudado foi desviado, envolvendo todas as contas do caminho. |
| **Grafo de rastreamento** | Mapeamento do caminho percorrido pelos recursos a partir da transação raiz de uma Recuperação de Valores. |
| **Bloqueio cautelar** | Congelamento preventivo de até 72h de recursos sob suspeita de fraude, para investigação mais detalhada. |
| **ANS** | Acordo de Nível de Serviço — o termo oficial do BACEN para o que este material chama de "SLA". |
| **IGA** | Índice Geral de ANS — indicador agregado que resume o cumprimento dos SLAs de um participante. |
| **ISO 20022 / pacs** | Padrão de mensageria: `pacs.008` (pagamento), `pacs.002` (status), `pacs.004` (devolução). |
| **EVP** | Chave aleatória do Pix — sequência de caracteres sem significado, gerada pelo DICT (o BACEN não divulga publicamente a expansão completa da sigla). |
| **LGPD** | Lei Geral de Proteção de Dados — lei brasileira de privacidade e dados pessoais. |
| **PLD-FT** | Prevenção à Lavagem de Dinheiro e ao Financiamento do Terrorismo — disciplina de compliance financeiro. |
| **Pix Automático** | Pagamentos recorrentes por mandato, em produção em 2025. |
| **Drex** | Real Digital (CBDC) do BACEN, em pilotos, sobre DLT. |

## Apêndice B — Glossário do eixo IA

| Conceito | O que é | Onde no curso |
|---|---|---|
| **SDD (Spec-Driven Development)** | Spec/decisão como fonte da verdade executável; invariantes viram testes. | Aula 1; protagonista na Aula 3. |
| **Context Engineering** | Projetar o que entra na janela de contexto do agente (spec, ADRs, glossário, dados) — recurso escasso. | Semeado na Aula 1; Aulas 3 e 8. |
| **Harness Engineering** | Aparato de validação (invariantes-teste, evals, guardrails, flags, canary) desenhado dentro do sistema. | Semeado (invariantes do ledger); Aula 8. |
| **Looping Engineering** | Loop agêntico (planejar→agir→observar→refletir) + loop de feedback (inspirado em RLHF). | "Fé → evidência"; Aula 8. |
| **MCP (Model Context Protocol)** | Protocolo aberto (Anthropic) que conecta agentes a ferramentas/dados, com fronteira de permissão. | Governança do agente; Aula 8. |
| **RLHF** | Reinforcement Learning from Human Feedback — sistema melhora com feedback real, humano no circuito. | Metáfora do loop longo; Aula 8. |

## Apêndice C — Glossário de termos técnicos gerais (não exclusivos de Pix/BACEN)

| Termo | O que é |
|---|---|
| **CAP (teorema)** | Consistência, Availability (disponibilidade) e tolerância a Partição — o trade-off central de sistemas distribuídos (Eric Brewer). |
| **PACELC** | Extensão do CAP (Daniel Abadi): mesmo sem partição, você escolhe entre Latency (latência) e Consistency. |
| **CQRS** | Command Query Responsibility Segregation — separar o modelo de escrita do modelo de leitura. |
| **Event sourcing** | Guardar o histórico de eventos como fonte da verdade, em vez de só o estado atual. |
| **Lost update** | Duas escritas concorrentes se sobrepõem; uma apaga o efeito da outra sem ninguém perceber. |
| **Append-only** | Um log em que só se acrescenta informação; nunca se apaga nem se sobrescreve um registro. |
| **Fitness function** | Verificação automática (um teste) que confirma se o sistema ainda respeita uma propriedade desejada — termo de arquitetura evolutiva. |
| **TrueTime** | Sistema de relógios do Google (GPS + atômicos) que limita a incerteza de tempo entre datacenters; usado pelo Spanner. |
| **OODA** | Observe-Orient-Decide-Act ("observar-orientar-decidir-agir") — ciclo de decisão de John Boyd; inspira o loop agêntico. |
| **HTTP 200 / 404 / 429** | Códigos de resposta web: sucesso / não encontrado / excesso de requisições (rate limit). |
| **Isolamento (read committed / snapshot / serializable)** | Níveis crescentes de proteção contra anomalias de concorrência num banco de dados; serializable é o mais forte. |
| **Write skew** | Anomalia em snapshot isolation onde duas transações, cada uma vendo um retrato consistente, juntas violam uma invariante que nenhuma violaria sozinha. |
| **Locking pessimista** | Trava a linha/recurso antes de alterá-lo; simples, mas gera fila sob alta contenção (a origem técnica do "ponto quente"). |
| **Controle de concorrência otimista** | Usa uma coluna de versão; grava só se a versão não mudou desde a leitura; retenta se perdeu a corrida. |
| **Two-phase commit** | Protocolo de atomicidade forte entre partições/serviços; correto, mas lento e frágil a travamentos. |
| **Saga** | Alternativa ao two-phase commit: cada partição commita localmente; uma ação compensatória desfaz o que for preciso se uma etapa posterior falhar. |
| **Lei de Little (L = λ × W)** | Concorrência média = taxa de chegada × tempo de permanência no sistema. Ferramenta central para dimensionar pools de conexão. |
| **IOPS** | Operações de entrada/saída por segundo que um disco sustenta; raramente é o gargalo real num sistema bem projetado. |
| **SSI (Serializable Snapshot Isolation)** | Mecanismo do PostgreSQL para serializable: roda transações em paralelo sobre snapshots e aborta quando detecta uma combinação perigosa. |
| **Next-key locking** | Mecanismo do MySQL/InnoDB para evitar leituras fantasmas: trava linhas e as lacunas entre elas. |
| **Raft** | Protocolo de consenso distribuído usado por bancos NewSQL (CockroachDB, YugabyteDB, TiDB) para replicar partições entre nós. |

## Apêndice D — Para aprofundar

- CAP (Brewer, "CAP Twelve Years Later") e PACELC (Abadi).
- Martin Kleppmann, *Designing Data-Intensive Applications* — consistência, replicação, transações, CQRS/event sourcing.
- **Banco Central (fontes verificadas nesta versão):** *Manual de Tempos do Pix* v7.0 (SLAs de SPI, DICT e Recuperação de Valores por fraude/falha operacional); *Regulamento do Pix* (Resolução BCB nº 195, de 3/3/2022); Instrução Normativa BCB nº 243, de 16/3/2022; *Manual de Fluxos do Processo de Efetivação do Pix*; *Manual Operacional do DICT* e documentação da API do DICT (rate limiting / anti-scraping por token bucket); *Guia de Implementação dos Procedimentos de Devolução no Pix, com ênfase no MED*, v4.3 (grafo de rastreamento, bloqueio cautelar, código MD06 — v4.4 já publicada, vigência a partir de set/out de 2026); Resolução BCB nº 493, de 28/8/2025 (MED 2.0 — rastreamento em 5 camadas, bloqueio cautelar de 72h, obrigatório desde 2/2/2026); catálogo de mensagens ISO 20022 (pacs.008 / pacs.002 / pacs.004); Estatísticas do Pix do Portal de Dados Abertos do BACEN (volume e TPS médio, jan-mai/2026).
- **Nota de manutenção:** os números de volume/TPS e as versões de manuais citados aqui foram verificados nesta atualização; como o Pix e seus manuais operacionais mudam com frequência, revalide antes de reusar esses números em uma turma futura.
- Michael Nygard, "Documenting Architecture Decisions" (origem do ADR).
- Chris Richardson, catálogo de padrões de microsserviços — microservices.io/patterns (Event Sourcing, Transactional Outbox, Saga, CQRS, Circuit Breaker — padrões que o TechPix aplica ao longo do curso).
- Anthropic: documentação do Model Context Protocol; materiais sobre engenharia de contexto e agentes. GitHub Spec Kit (SDD) — repositório oficial: github.com/github/spec-kit (fluxo `/speckit.constitution → specify → clarify → plan → tasks → analyze → implement`, aplicado na Aula 3).

---

[Índice](index.md) · [Aula 2 →](aula2-conteudo-completo.md)
