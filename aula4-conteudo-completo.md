---
layout: default
title: "Aula 4 — Comunicação, Integração e Resiliência"
---

# Aula 4 — Comunicação, Integração e Resiliência
*Curso de Arquitetura de Sistemas Financeiros com IA*

> **Navegação:** [Índice](index.md) · [Aula 1](aula1-conteudo-completo.md) · [Aula 2](aula2-conteudo-completo.md) · [Aula 3](aula3-conteudo-completo.md) · **Aula 4 (você está aqui)** · [Aula 5](aula5-conteudo-completo.md) · [Aula 6](aula6-conteudo-completo.md) · [Aula 7](aula7-conteudo-completo.md) · [Aula 8](aula8-conteudo-completo.md)

Boa noite. Meu nome não importa tanto quanto o meu crachá anterior: eu passei os últimos dez anos de plantão. Eu sou o engenheiro que chamam quando o sistema já está no ar, já tem cliente dentro, e alguma coisa acabou de fazer um barulho estranho. O professor que esteve aqui antes de mim desenhou com vocês o ledger, os trade-offs, as fronteiras — e desenhou bem, eu li tudo, inclusive os ADRs. O meu trabalho, nas próximas quatro aulas, é outro: é fazer esse desenho **sobreviver ao contato com a produção**. E eu quero começar do jeito que eu conheço melhor — contando um incidente.

Sexta-feira, 12 de setembro de 2025, 19h47. O time de Antifraude e Limites fez um deploy. Um deploy pequeno, revisado, testado, aprovado — e, vejam só, um deploy **correto** do ponto de vista de quem o fez. Lembram do bug do Diego e da Marina, da aula passada? Aquele em que a palavra "conta" significava identidade para um time e carteira para outro? Pois bem: depois daquela aula, o time do Diego fez a lição de casa. Adotou a linguagem ubíqua, revisou o vocabulário do contexto — e, no meio dessa revisão, renomeou um campo do evento `LimitesValidados`: onde estava escrito `contaId`, passou a estar escrito `carteiraId`. Semanticamente, é a correção *certa*. O campo sempre tinha sido a carteira, nunca a identidade; o nome antigo era exatamente a ambiguidade que quase custou caro.

Só que às 19h52, cinco minutos depois do deploy, o projetor do caminho de leitura — aquele componente do ADR-002 que consome os eventos do Outbox e monta o extrato, o feed e o status de cada Pix na tela do aplicativo — recebeu o primeiro `LimitesValidados` no formato novo, procurou o campo `contaId`, não achou, e lançou uma exceção. E aí vem o detalhe que eu quero que vocês guardem para sempre: ele **não morreu com barulho**. Ele fez o que consumidores ingênuos fazem: falhou, voltou para a mesma mensagem, falhou de novo, voltou de novo. Uma mensagem envenenada na frente da fila, e o consumidor batendo a cabeça nela em loop, sem processar nada do que vinha atrás.

Nenhum pagamento falhou. Eu repito, porque é importante: **nenhum centavo se moveu errado**. O ledger, forte e síncrono como o ADR-001 manda, continuou reservando e liquidando; o SPI continuou confirmando; a invariante Σ débitos = Σ créditos não tremeu. Mas o extrato de milhares de clientes congelou no tempo. Às 20h12, a central de atendimento recebeu a primeira ligação de um cliente que tinha feito um Pix, visto o dinheiro sair da tela de saldo — e não visto o pagamento aparecer no extrato. Ele achou que o dinheiro tinha sumido. Nos quarenta minutos seguintes, mais de trezentas pessoas acharam a mesma coisa. O Rafael, que estava de on-call naquela noite — guardem o nome dele, ele vai voltar nesse curso —, não foi acordado por um alerta: foi acordado pelo telefone do suporte, porque **não existia alerta para "a fila de leitura parou de andar"**. Às 20h27 ele achou a causa; às 20h34 subiu uma correção no consumidor para aceitar os dois nomes de campo; às 20h51, a fila de trezentos e poucos mil eventos represados terminou de drenar e o mundo voltou ao normal.

Quarenta minutos de extrato congelado. Custo direto: zero reais. Custo real: trezentas ligações de gente achando que uma fintech tinha perdido o dinheiro dela — e numa fintech, **a percepção de que o dinheiro sumiu é quase tão cara quanto o dinheiro sumir**.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 340" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a4inc-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
    <marker id="a4inc-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- Deploy -->
  <rect x="20" y="30" width="160" height="60" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="100" y="53" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Antifraude e Limites</text>
  <text x="100" y="72" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">deploy 19h47</text>
  <line x1="180" y1="60" x2="240" y2="60" stroke="#888" stroke-width="2" marker-end="url(#a4inc-arrow)"/>
  <!-- Evento novo -->
  <rect x="240" y="30" width="190" height="60" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="335" y="52" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7a5c00">LimitesValidados</text>
  <text x="335" y="72" text-anchor="middle" font-family="monospace" font-size="11" fill="#7a5c00">{ carteiraId }  ← era contaId</text>
  <line x1="430" y1="60" x2="490" y2="60" stroke="#888" stroke-width="2" marker-end="url(#a4inc-arrow)"/>
  <!-- Fila -->
  <g>
    <rect x="490" y="38" width="30" height="44" rx="4" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
    <text x="505" y="65" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#b91c1c">☠</text>
    <rect x="524" y="38" width="26" height="44" rx="4" fill="#eef2ff" stroke="#c7d2fe"/>
    <rect x="554" y="38" width="26" height="44" rx="4" fill="#eef2ff" stroke="#c7d2fe"/>
    <rect x="584" y="38" width="26" height="44" rx="4" fill="#eef2ff" stroke="#c7d2fe"/>
    <text x="565" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">fila do Outbox · ninguém passa na frente do veneno</text>
  </g>
  <line x1="614" y1="60" x2="670" y2="60" stroke="#b91c1c" stroke-width="2" marker-end="url(#a4inc-red)"/>
  <!-- Projetor -->
  <rect x="670" y="20" width="190" height="80" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="765" y="44" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">Projetor de leitura</text>
  <text x="765" y="63" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">procura contaId → exceção</text>
  <text x="765" y="81" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">↻ retry na mesma mensagem</text>
  <!-- Extrato -->
  <rect x="670" y="130" width="190" height="52" rx="8" fill="#fff" stroke="#b91c1c" stroke-width="2" stroke-dasharray="5 4"/>
  <text x="765" y="152" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">Extrato / feed / status</text>
  <text x="765" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">congelado por 40 min</text>
  <line x1="765" y1="100" x2="765" y2="130" stroke="#b91c1c" stroke-width="2" stroke-dasharray="4 3" marker-end="url(#a4inc-red)"/>
  <!-- Caminho do dinheiro intacto -->
  <rect x="20" y="130" width="560" height="52" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="300" y="152" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Ledger (ADR-001) + SPI: nenhum pagamento falhou · Σ débitos = Σ créditos ✓</text>
  <text x="300" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">o caminho da escrita nem ficou sabendo — só o caminho de leitura (ADR-002) parou</text>
  <!-- Timeline -->
  <line x1="30" y1="240" x2="850" y2="240" stroke="#999" stroke-width="2"/>
  <g font-family="sans-serif" font-size="11" fill="#333">
    <circle cx="60" cy="240" r="5" fill="#d4a017"/><text x="60" y="262" text-anchor="middle">19h47</text><text x="60" y="278" text-anchor="middle" fill="#666">deploy</text>
    <circle cx="200" cy="240" r="5" fill="#b91c1c"/><text x="200" y="262" text-anchor="middle">19h52</text><text x="200" y="278" text-anchor="middle" fill="#666">veneno na fila</text>
    <circle cx="380" cy="240" r="5" fill="#b91c1c"/><text x="380" y="262" text-anchor="middle">20h12</text><text x="380" y="278" text-anchor="middle" fill="#666">1ª ligação (não alerta!)</text>
    <circle cx="560" cy="240" r="5" fill="#4338ca"/><text x="560" y="262" text-anchor="middle">20h27</text><text x="560" y="278" text-anchor="middle" fill="#666">causa achada</text>
    <circle cx="680" cy="240" r="5" fill="#4338ca"/><text x="680" y="262" text-anchor="middle">20h34</text><text x="680" y="278" text-anchor="middle" fill="#666">fix: aceita os 2 campos</text>
    <circle cx="810" cy="240" r="5" fill="#166534"/><text x="810" y="262" text-anchor="middle">20h51</text><text x="810" y="278" text-anchor="middle" fill="#666">fila drenada</text>
  </g>
  <rect x="180" y="300" width="480" height="28" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="420" y="319" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#b91c1c">Ninguém errou — o contrato quebrou entre dois componentes, em silêncio</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O incidente da sexta 12/09: um campo renomeado quebra o consumidor sem derrubar nenhum pagamento — o dinheiro andou, a percepção dele congelou.</p>
</div>

Agora reparem no formato desse incidente, porque ele é o tema da aula inteira. Ninguém errou. O time do Antifraude fez uma correção semanticamente certa. O projetor de leitura fazia exatamente o que sempre fez. O bug do Diego e da Marina morava *entre* dois times, em tempo de projeto; esse aqui morava *entre* dois componentes, em tempo de execução. É o mesmo fantasma, um andar abaixo. E a lição-mãe que eu quero pregar na parede desde já: **contrato é arquitetura**. A fronteira entre dois pedaços do sistema — o formato da mensagem, o nome do campo, a semântica do erro, o tempo máximo de espera — é tão decisão de arquitetura quanto o banco de dados que vocês escolhem. A diferença é que o banco de dados, quando quebra, quebra com estardalhaço; o contrato quebra em silêncio, numa sexta à noite, sem que nenhum teste unitário de nenhum dos dois lados fique vermelho.

Hoje a gente vai transformar o mapa de contexto que vocês desenharam na Aula 3 — aquele diagrama bonito de caixas e setas — em **malha de comunicação de verdade**: cada seta vai ganhar um estilo, um contrato, um orçamento de tempo, uma política de falha e um dono. No fim, a gente escreve juntos o artefato que teria evitado essa sexta-feira.

---

## 1. O mapa vira malha: cada aresta é uma decisão

O professor anterior encerrou a Aula 3 com o context map do TechPix: Identidade e Onboarding, Contas e Ledger, Pagamentos, Antifraude e Limites, Devoluções e Disputas, Cartões. E ele disse uma coisa que eu quero retomar com todo o peso: bounded context é decisão de modelagem; microsserviço é decisão de topologia. Hoje o TechPix ainda é um monólito modular — os contextos moram no mesmo processo. Mas a comunicação entre eles **já é real**: o módulo de Pagamentos já chama o de Antifraude, o Ledger já publica eventos pelo Outbox, o ACL já traduz `pacs.008` para o dialeto interno. A pergunta desta seção é: **para cada aresta desse mapa, qual é o estilo certo de conversa?**

E a resposta nunca é "síncrono" ou "assíncrono" no atacado. É aresta por aresta, com critério. O critério que eu uso há dez anos cabe numa pergunta: **quem chama consegue continuar seu trabalho sem a resposta?** Se a resposta é necessária para decidir o próximo passo — validar antes de reservar, resolver a chave antes de enviar —, a conversa é síncrona, e vocês pagam o preço em acoplamento de disponibilidade. Se a resposta pode chegar depois — atualizar extrato, recalcular limite, notificar —, a conversa é assíncrona, e vocês pagam o preço em atraso e em complexidade de entendimento.

Vejam o mapa do TechPix com esse critério aplicado:

| Aresta | Estilo | Por quê | Orçamento / SLA |
|---|---|---|---|
| Pagamentos → Antifraude e Limites | **Síncrono** (chamada direta; gRPC quando virar serviço) | A decisão "pode ou não pode" está no caminho crítico: não dá para enviar ao SPI sem `LimitesValidados` | **~100 ms p99** — a fatia mais disputada do orçamento |
| Pagamentos → DICT (via ACL) | **Síncrono** | Resolução de chave é pré-condição do fluxo; obrigação regulatória | p99 ≤ 1 s (SLA BACEN), com timeout interno mais agressivo |
| Pagamentos → SPI (via ACL) | **Síncrono** (`pacs.008` → `pacs.002`) | Liquidação é o coração do fluxo; irrevogável | p50 2,8 s · p99 4,6 s (números do BACEN) |
| Pagamentos → Contas e Ledger (reserva) | **Síncrono, transacional** | ADR-001: consistência forte na escrita; hoje é a mesma transação do monólito | dezenas de ms |
| Contas e Ledger → caminho de leitura (extrato, feed, saldo exibido) | **Assíncrono** (Outbox → eventos) | ADR-002: leitura desacoplada da escrita | atraso eventual de 100–300 ms |
| Antifraude e Limites → recálculo de limites, features | **Assíncrono** | Tolera janela de imprecisão (Aula 3, Seção 4.3) | segundos |
| Devoluções e Disputas ↔ Pagamentos | **Assíncrono** (eventos + trilho MED) | SLAs em horas, não milissegundos (MED: p99 de 6 h) | horas |
| Identidade e Onboarding → demais contextos | **Assíncrono** para propagação de status; síncrono só em verificação pontual de onboarding | Status cadastral muda raramente; verificação pontual é caminho crítico do cadastro, não do Pix | segundos / ~100 ms |

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 430" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a4map-sync" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a4map-async" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <!-- Externos BACEN -->
  <rect x="250" y="20" width="130" height="52" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="315" y="42" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">DICT</text>
  <text x="315" y="60" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">externo · p99 ≤ 1s</text>
  <rect x="470" y="20" width="130" height="52" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="535" y="42" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">SPI</text>
  <text x="535" y="60" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">externo · p99 4,6s</text>
  <!-- ACL -->
  <rect x="330" y="105" width="190" height="34" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5" stroke-dasharray="3 3"/>
  <text x="425" y="127" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">ACL — traduz pacs.* p/ dialeto interno</text>
  <line x1="315" y1="72" x2="390" y2="105" stroke="#4338ca" stroke-width="2.5" marker-start="url(#a4map-sync)" marker-end="url(#a4map-sync)"/>
  <line x1="535" y1="72" x2="465" y2="105" stroke="#4338ca" stroke-width="2.5" marker-start="url(#a4map-sync)" marker-end="url(#a4map-sync)"/>
  <text x="300" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">timeout 1,2s</text>
  <text x="555" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">timeout 6s</text>
  <!-- Pagamentos (centro) -->
  <rect x="340" y="170" width="170" height="60" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
  <text x="425" y="195" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Pagamentos</text>
  <text x="425" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">orquestra o fluxo do Pix</text>
  <line x1="425" y1="139" x2="425" y2="170" stroke="#4338ca" stroke-width="2.5" marker-start="url(#a4map-sync)" marker-end="url(#a4map-sync)"/>
  <!-- Antifraude (direita) -->
  <rect x="660" y="170" width="200" height="60" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="760" y="195" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Antifraude e Limites</text>
  <text x="760" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">decisão no caminho crítico</text>
  <line x1="510" y1="200" x2="660" y2="200" stroke="#4338ca" stroke-width="2.5" marker-start="url(#a4map-sync)" marker-end="url(#a4map-sync)"/>
  <text x="585" y="190" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#4338ca">sínc · 100ms p99 · zero retry</text>
  <!-- features assínc (loop antifraude) -->
  <rect x="690" y="270" width="140" height="40" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="760" y="288" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">recálculo de limites /</text>
  <text x="760" y="302" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">features</text>
  <line x1="760" y1="230" x2="760" y2="270" stroke="#166534" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#a4map-async)"/>
  <text x="805" y="252" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">assínc · s</text>
  <!-- Ledger (esquerda) -->
  <rect x="30" y="170" width="180" height="60" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2.5"/>
  <text x="120" y="195" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Contas e Ledger</text>
  <text x="120" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">a verdade do dinheiro · forte</text>
  <line x1="210" y1="200" x2="340" y2="200" stroke="#4338ca" stroke-width="2.5" marker-start="url(#a4map-sync)" marker-end="url(#a4map-sync)"/>
  <text x="275" y="190" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#4338ca">sínc transacional · ADR-001</text>
  <!-- Caminho de leitura -->
  <rect x="30" y="290" width="180" height="56" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="120" y="312" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Caminho de leitura</text>
  <text x="120" y="331" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">extrato · feed · saldo exibido</text>
  <line x1="120" y1="230" x2="120" y2="290" stroke="#166534" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#a4map-async)"/>
  <text x="190" y="262" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">Outbox · 100–300ms (ADR-002)</text>
  <!-- Devoluções -->
  <rect x="360" y="290" width="190" height="56" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="455" y="312" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Devoluções e Disputas</text>
  <text x="455" y="331" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">MED · pacs.004</text>
  <line x1="440" y1="230" x2="450" y2="290" stroke="#166534" stroke-width="2" stroke-dasharray="6 4" marker-start="url(#a4map-async)" marker-end="url(#a4map-async)"/>
  <text x="530" y="262" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">assínc · MED p99 6h</text>
  <!-- Identidade -->
  <rect x="30" y="60" width="160" height="52" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="110" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Identidade e Onboarding</text>
  <text x="110" y="100" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">status cadastral</text>
  <line x1="140" y1="112" x2="180" y2="170" stroke="#166534" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#a4map-async)"/>
  <text x="115" y="145" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">propagação assínc</text>
  <!-- Legenda -->
  <rect x="30" y="380" width="820" height="36" rx="6" fill="#fff" stroke="#ddd"/>
  <line x1="55" y1="398" x2="115" y2="398" stroke="#4338ca" stroke-width="2.5" marker-start="url(#a4map-sync)" marker-end="url(#a4map-sync)"/>
  <text x="130" y="402" font-family="sans-serif" font-size="11" fill="#333">síncrono — acopla <tspan font-weight="bold">disponibilidade</tspan></text>
  <line x1="400" y1="398" x2="460" y2="398" stroke="#166534" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#a4map-async)"/>
  <text x="475" y="402" font-family="sans-serif" font-size="11" fill="#333">assíncrono — acopla <tspan font-weight="bold">entendimento</tspan></text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O context map da Aula 3 virou malha: cada aresta com estilo, orçamento e política — nunca "síncrono ou assíncrono" no atacado.</p>
</div>

Duas observações sobre essa tabela, porque ela é menos inocente do que parece.

Primeira: reparem que o caminho crítico do Pix — DICT, Antifraude, Ledger, SPI — é uma **corrente de chamadas síncronas**. Cada elo soma latência e subtrai disponibilidade: se a disponibilidade de cada elo é 99,9%, quatro elos em série entregam no máximo 99,6% — a matemática da multiplicação é impiedosa, e foi exatamente ela que o professor da Aula 2 mostrou quando o DICT síncrono esgotou o pool de conexões. A gente não consegue tirar esses elos do caminho — o fluxo do Pix *é* essa sequência —, mas consegue, e vai fazer isso na Seção 5, colocar em cada elo uma política explícita de falha.

Segunda: reparem que a aresta assíncrona do extrato — a que quebrou na sexta-feira — está marcada com um atraso de 100 a 300 milissegundos. Esse número vem do ADR-002 e ele é uma **promessa ao negócio**: o app pode mostrar "processando" por um instante, mas o extrato converge em menos de meio segundo. No incidente, esse atraso foi de 100 milissegundos para quarenta minutos — e não existia nenhum alerta ligado a essa promessa. Guardem isso: **promessa sem métrica é promessa que já foi quebrada, só que vocês ainda não sabem.** A Aula 7 volta nisso com força.

E um aforismo para fixar a seção, porque eu gosto de aforismo que cabe num post-it: **síncrono acopla disponibilidade; assíncrono acopla entendimento.** Na chamada síncrona, se o outro cai, eu caio junto — meu risco é operacional. Na mensagem assíncrona, se o outro entende diferente de mim, a gente diverge em silêncio — meu risco é semântico. A sexta-feira do extrato foi um risco semântico cobrado em horário comercial estendido.

---

## 2. Síncrono bem-feito: o orçamento desce pela pilha

Vamos primeiro arrumar as arestas síncronas. Quatro disciplinas.

### 2.1 REST na borda, gRPC no miolo

O aplicativo da Ana fala com o TechPix por uma API REST/JSON — e deve continuar assim: REST é a língua franca da borda, legível, depurável, cacheável. Mas **entre contextos internos**, quando a gente extrair serviços (Aula 6), a conversa vai ser gRPC, e eu quero justificar essa escolha com critério, não com moda.

Primeiro, o contrato: gRPC nasce de um arquivo `.proto` — a definição da interface é um artefato versionado, compilado, que gera cliente e servidor. Não existe "eu achava que esse campo era string". O contrato é código, e código entra em CI — vocês já estão vendo onde isso vai dar quando a gente chegar na Seção 4. Segundo, o custo: serialização binária e multiplexação sobre HTTP/2 importam quando o TechPix opera a 900 transações por segundo no pico e cada transação atravessa três ou quatro contextos — a diferença entre 5 ms e 0,5 ms de overhead por chamada, multiplicada pela cadeia, é uma fatia real do orçamento. Terceiro — e para mim o argumento decisivo — o **deadline propagation**, que merece a subseção própria.

Antes disso, um parêntese que plantão me ensinou a nunca pular: quando eu falo "gRPC sobre HTTP/2", "TCP", "TLS na RSFN", eu estou andando por camadas diferentes de uma mesma pilha — o **modelo OSI**. E saber em qual camada cada coisa vive não é teoria de prova de certificação: é o que diz **qual ferramenta enxerga o quê**. Um firewall olha endereço e porta; ele não faz ideia do que é um retry. Um circuit breaker olha respostas de aplicação; ele não sabe o que é um pacote. Quem confunde as camadas compra defesa no andar errado.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 470" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="26" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">O modelo OSI, com o TechPix morando dentro dele</text>
  <!-- Layer bars -->
  <g font-family="sans-serif">
    <rect x="20" y="42" width="440" height="50" rx="7" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
    <text x="35" y="63" font-size="12" font-weight="bold" fill="#26215C">L7 · Aplicação</text>
    <text x="35" y="82" font-size="10.5" fill="#5a55a0">HTTP/2 · gRPC · REST · header Idempotency-Key · deadline · pacs.008</text>

    <rect x="20" y="97" width="440" height="44" rx="7" fill="#fff" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="35" y="115" font-size="12" font-weight="bold" fill="#57534e">L6 · Apresentação</text>
    <text x="35" y="133" font-size="10.5" fill="#78716c">TLS (mTLS na RSFN) · serialização protobuf / JSON</text>

    <rect x="20" y="146" width="440" height="44" rx="7" fill="#fff" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="35" y="164" font-size="12" font-weight="bold" fill="#57534e">L5 · Sessão</text>
    <text x="35" y="182" font-size="10.5" fill="#78716c">streams multiplexados do HTTP/2 · conexões persistentes</text>

    <rect x="20" y="195" width="440" height="50" rx="7" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
    <text x="35" y="216" font-size="12" font-weight="bold" fill="#26215C">L4 · Transporte</text>
    <text x="35" y="235" font-size="10.5" fill="#5a55a0">TCP · portas · handshake · os pools de conexão da Aula 2 vivem aqui</text>

    <rect x="20" y="250" width="440" height="44" rx="7" fill="#fff" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="35" y="268" font-size="12" font-weight="bold" fill="#57534e">L3 · Rede</text>
    <text x="35" y="286" font-size="10.5" fill="#78716c">IP · roteamento entre datacenters e a RSFN</text>

    <rect x="20" y="299" width="440" height="38" rx="7" fill="#fff" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="35" y="316" font-size="12" font-weight="bold" fill="#57534e">L2 · Enlace</text>
    <text x="35" y="331" font-size="10.5" fill="#78716c">Ethernet · switches</text>

    <rect x="20" y="342" width="440" height="38" rx="7" fill="#fff" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="35" y="359" font-size="12" font-weight="bold" fill="#57534e">L1 · Física</text>
    <text x="35" y="374" font-size="10.5" fill="#78716c">fibra óptica — a RSFN que liga o TechPix ao BACEN é, no fim, isto</text>
  </g>
  <!-- Right: where each defense lives -->
  <g font-family="sans-serif">
    <rect x="500" y="42" width="360" height="106" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="680" y="63" text-anchor="middle" font-size="12" font-weight="bold" fill="#166534">Enxergam L7 (conteúdo da conversa)</text>
    <text x="680" y="83" text-anchor="middle" font-size="10.5" fill="#166534">timeout · retry · circuit breaker · deadline propagation</text>
    <text x="680" y="101" text-anchor="middle" font-size="10.5" fill="#166534">LB L7: NGINX · Envoy · ALB — leem rota, header, status</text>
    <text x="680" y="123" text-anchor="middle" font-size="10" fill="#3f6212">+ decide por conteúdo · − mais caro por requisição</text>
    <line x1="500" y1="80" x2="465" y2="67" stroke="#166534" stroke-width="1.5" stroke-dasharray="4 3"/>

    <rect x="500" y="195" width="360" height="92" rx="9" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
    <text x="680" y="216" text-anchor="middle" font-size="12" font-weight="bold" fill="#7a5c00">Enxergam L3/L4 (pacotes e portas)</text>
    <text x="680" y="236" text-anchor="middle" font-size="10.5" fill="#7a5c00">firewall · LB L4: kube-proxy, NLB — não leem HTTP</text>
    <text x="680" y="254" text-anchor="middle" font-size="10.5" fill="#7a5c00">+ rápidos e baratos · − cegos ao conteúdo:</text>
    <text x="680" y="271" text-anchor="middle" font-size="10.5" fill="#7a5c00">não distinguem /pix de /extrato, nem 200 de 500</text>
    <line x1="500" y1="225" x2="465" y2="218" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="4 3"/>
  </g>
  <rect x="20" y="398" width="840" height="34" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="440" y="420" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#3730a3">Guardem o L4 × L7: é o LB L7 — que lê rota e header — que vai fatiar o tráfego do canary na Aula 6. O L4 não saberia nem por onde começar.</text>
  <text x="440" y="456" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">Defesa comprada no andar errado é defesa que não dispara: firewall não vê retry storm; circuit breaker não vê pacote perdido.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O modelo OSI aplicado ao TechPix: cada defesa da Aula 2 e desta aula vive numa camada — e só enxerga o que a camada dela mostra.</p>
</div>

### 2.2 Deadline propagation: o orçamento viaja com a requisição

O professor da Aula 1 ensinou o orçamento de latência: teto normativo de 40 segundos, experiência-alvo de poucos segundos, cada componente gastando uma fatia. O erro clássico de implementação é traduzir esse orçamento em **timeouts locais e independentes**: Pagamentos espera o Antifraude por 2 segundos, o Antifraude espera a feature store por 2 segundos, a feature store espera o cache por 2 segundos... e ninguém percebe que, somados, os timeouts locais estouram o orçamento global — ou, pior, que um componente lá no fundo continua trabalhando duro numa requisição que o cliente lá em cima **já abandonou**. Trabalho zumbi: queima CPU, segura conexão do pool, e o resultado vai para o lixo.

A disciplina certa se chama propagação de deadline: quem inicia a requisição carimba nela o **instante absoluto** em que a resposta deixa de ter valor — "essa requisição expira às 20h31m04.250s" — e cada salto repassa o carimbo, descontando o tempo já gasto. O gRPC faz isso nativamente; em REST dá para fazer com um header, com mais disciplina manual. O efeito prático: quando o orçamento acaba, **a cadeia inteira desiste junta**, do primeiro ao último elo, e nenhum recurso fica preso trabalhando para ninguém. Na Aula 2, quando o pool de 100 conexões esgotou, uma parte relevante daquelas conexões estava exatamente nisso: trabalhando em requisições que o cliente já tinha abandonado e retentado. Deadline propagado é a vacina contra trabalho zumbi.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a4dl-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
    <marker id="a4dl-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <!-- ERRADO: timeouts locais -->
  <text x="20" y="28" font-family="sans-serif" font-size="13" font-weight="bold" fill="#b91c1c">✗ Timeouts locais e independentes</text>
  <rect x="20" y="42" width="180" height="48" rx="8" fill="#fff" stroke="#b91c1c" stroke-width="2"/>
  <text x="110" y="62" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Pagamentos</text>
  <text x="110" y="80" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">espera 2s</text>
  <line x1="200" y1="66" x2="250" y2="66" stroke="#b91c1c" stroke-width="2" marker-end="url(#a4dl-red)"/>
  <rect x="250" y="42" width="180" height="48" rx="8" fill="#fff" stroke="#b91c1c" stroke-width="2"/>
  <text x="340" y="62" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Antifraude</text>
  <text x="340" y="80" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">espera 2s</text>
  <line x1="430" y1="66" x2="480" y2="66" stroke="#b91c1c" stroke-width="2" marker-end="url(#a4dl-red)"/>
  <rect x="480" y="42" width="180" height="48" rx="8" fill="#fff" stroke="#b91c1c" stroke-width="2"/>
  <text x="570" y="62" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Feature store</text>
  <text x="570" y="80" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">espera 2s</text>
  <rect x="690" y="42" width="170" height="48" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="775" y="62" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">somados: 6s — estoura</text>
  <text x="775" y="80" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">+ trabalho zumbi 🧟</text>
  <text x="340" y="115" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">o cliente já desistiu lá em cima — e o fundo da cadeia continua trabalhando para o lixo</text>
  <!-- CERTO: deadline propagado -->
  <text x="20" y="158" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">✓ Deadline propagado — o carimbo viaja com a requisição</text>
  <rect x="20" y="172" width="200" height="62" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="120" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">Gateway carimba</text>
  <text x="120" y="209" text-anchor="middle" font-family="monospace" font-size="10" fill="#166534">expira: 20h31m04,250s</text>
  <text x="120" y="226" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">orçamento: 3.000 ms</text>
  <line x1="220" y1="203" x2="270" y2="203" stroke="#166534" stroke-width="2" marker-end="url(#a4dl-green)"/>
  <rect x="270" y="172" width="180" height="62" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="360" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Pagamentos</text>
  <text x="360" y="209" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">herda o carimbo</text>
  <text x="360" y="226" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">restam 2.850 ms</text>
  <line x1="450" y1="203" x2="500" y2="203" stroke="#166534" stroke-width="2" marker-end="url(#a4dl-green)"/>
  <rect x="500" y="172" width="180" height="62" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="590" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Antifraude</text>
  <text x="590" y="209" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">mesmo carimbo</text>
  <text x="590" y="226" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">restam 2.700 ms</text>
  <line x1="680" y1="203" x2="730" y2="203" stroke="#166534" stroke-width="2" marker-end="url(#a4dl-green)"/>
  <rect x="730" y="172" width="130" height="62" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="795" y="197" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Feature store</text>
  <text x="795" y="217" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">restam 2.560 ms</text>
  <rect x="20" y="262" width="840" height="30" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="440" y="282" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#3730a3">Quando o orçamento acaba, a cadeia inteira desiste junta — nenhuma conexão do pool fica presa trabalhando para ninguém</text>
  <text x="440" y="316" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">gRPC propaga o deadline nativamente; em REST, um header + disciplina · o teto de 40s da Aula 1 é o carimbo original</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Deadline propagation: timeout local é opinião de um elo; deadline propagado é o orçamento inteiro descendo pela pilha.</p>
</div>

### 2.3 Timeout é derivado, não chutado

Com deadline na mão, o timeout de cada aresta vira uma conta, não um chute. A chamada ao DICT tem SLA regulatório de p99 ≤ 1 segundo — então o timeout interno do TechPix para essa chamada é da ordem de 1 segundo e pouco, não os "30 segundos default do framework" que eu já encontrei em produção mais vezes do que gostaria. A chamada ao Antifraude tem orçamento de ~100 ms — porque ela acontece **antes** da reserva no ledger e do envio ao SPI, e a experiência-alvo do Pix inteiro é de poucos segundos; se a validação de risco comer meio segundo, ela sozinha dobra a latência percebida. Escrevam isso como regra: **timeout default de framework é uma decisão de arquitetura tomada por quem nunca viu o seu sistema.** Toda aresta síncrona do mapa recebe timeout derivado do orçamento, documentado, revisado.

E esse número de 100 ms para o Antifraude — segurem ele com carinho. Na próxima aula, a gente vai tentar enfiar um modelo de machine learning **dentro** desses 100 milissegundos, e vocês vão ver que esse orçamento apertado dita metade da arquitetura de inferência.

### 2.4 Idempotência agora é interface: a chave vira header

A Aula 1 estabeleceu o princípio — a chave de idempotência nasce no cliente, identifica a intenção, e transforma "tentou N vezes" em "aconteceu uma vez". Falta dar a ele forma de **contrato de API**. O padrão da indústria é o header `Idempotency-Key`: o cliente gera uma chave única por intenção (no Pix, o EndToEndId já cumpre esse papel de ponta a ponta), envia em toda tentativa, e o servidor responde a duplicatas com o resultado original — mesmo status, mesmo corpo. E o contrato precisa dizer isso *explicitamente*: quais operações exigem a chave (toda escrita), quanto tempo o servidor guarda o resultado (mais que a janela de retry mais pessimista), e o que acontece se a mesma chave chegar com um corpo **diferente** (erro 422, sempre — chave igual com conteúdo diferente é bug do cliente ou fraude, nunca um retry legítimo).

Por que isso é assunto de contrato e não de implementação? Porque retry seguro é uma **negociação entre os dois lados**: o cliente só pode retentar porque o servidor prometeu deduplicar. Se essa promessa não está escrita na interface, cada consumidor novo da API vai descobri-la — ou não — por tentativa e erro em produção.

---

## 3. Assíncrono bem-feito: a fila não perdoa improviso

Agora as arestas assíncronas — e aqui eu falo com a autoridade de quem já drenou muita fila entupida de madrugada. O Outbox da Aula 2 garantiu que **nenhum evento se perde** entre a transação do ledger e a publicação. Ótimo. Mas entre a publicação e o consumo mora um mundo de modos de falha que o incidente da sexta-feira exibiu quase todos. Vamos por partes.

### 3.1 O consumidor idempotente: exactly-once é responsabilidade de quem lê

A Aula 1 cravou: entrega exactly-once é impossível; o que existe é **efeito** exactly-once, construído sobre entrega at-least-once. Na época, o palco era a API de pagamento. Agora reparem que a mesma lei vale do lado do consumidor de eventos: o broker vai, sim, entregar `PixLiquidado` duas vezes — no rebalanceamento de partições, na retomada pós-crash, no retry do relay do Outbox. Se o projetor de extrato somar o mesmo evento duas vezes, a Ana vê dois pagamentos na tela onde houve um. O antídoto tem os mesmos dois sabores de sempre: **deduplicação explícita** — o consumidor registra os IDs de evento já processados (o EndToEndId mais o tipo do evento servem lindamente) e ignora repetidos — ou **escrita naturalmente idempotente** — a projeção é um *upsert* por chave ("o status do Pix E2E-tal é liquidado"), que aplicado duas vezes produz o mesmo estado. Regra da casa: todo consumidor novo no TechPix responde por escrito à pergunta "o que acontece se você receber essa mensagem duas vezes?" antes de ir para produção.

### 3.2 Ordem: por chave, nunca global

Segunda pergunta obrigatória: "e se as mensagens chegarem fora de ordem?". A resposta arquitetural do TechPix: o tópico de eventos é particionado por `conta_id` — a mesma chave de particionamento que vocês conhecem desde a Aula 1 —, o que garante ordem **dentro de cada conta** e nenhuma garantia entre contas. E isso basta: para montar o extrato da Ana, importa que `FundosReservados` da Ana venha antes de `PixLiquidado` da Ana; não importa nada a ordem entre o Pix da Ana e o do Bruno. Ordem global exigiria serializar o mundo inteiro num ponto só — vocês já sabem, da Aula 2, o nome disso: ponto quente. **Quem pede ordem global está pedindo um gargalo com outras palavras.**

### 3.3 Consumer lag: a métrica que faltou na sexta-feira

Todo consumidor assíncrono tem uma métrica vital chamada *consumer lag*: quantas mensagens já publicadas ele ainda não processou. Em regime saudável, o lag do projetor de extrato oscila perto de zero — é isso que sustenta a promessa dos 100–300 ms. Na sexta-feira, às 19h52, o lag começou a subir a 140 mensagens por segundo — era o tráfego de sexta à noite se acumulando atrás da mensagem envenenada — e **ninguém olhou**, porque não havia alerta. Trezentos mil eventos depois, foi o telefone do suporte que fez o papel do alerta, com vinte minutos de atraso e trezentos clientes de custo. A lição em uma linha: **para toda aresta assíncrona, o lag é métrica de primeira classe, com alerta amarrado à promessa de atraso do contrato.** Se o contrato promete 300 ms, o alerta dispara em segundos de lag — não em minutos, e jamais em ligações.

### 3.4 Mensagem envenenada e DLQ: falhar para o lado, não para trás

Agora o mecanismo exato da paralisia. O projetor recebeu uma mensagem que ele não conseguia processar — a *poison message*, a mensagem envenenada — e fez a única coisa que sabia: tentar de novo. Só que retry resolve falha **transitória** (rede piscou, banco reiniciou); a mensagem envenenada é falha **permanente** — pode tentar um milhão de vezes, o campo `contaId` não vai renascer no payload. Retry infinito numa falha permanente transforma um evento ruim em paralisação total, porque a fila é ordenada: ninguém passa na frente do veneno.

O padrão civilizado: retentar poucas vezes com backoff — os mesmos 100, 200, 400, 800 ms da Aula 2 —, e na falha persistente **tirar a mensagem do caminho**: movê-la para uma *dead letter queue*, a DLQ, uma fila estacionamento onde mensagens problemáticas aguardam inspeção humana, com alerta imediato. O fluxo principal continua andando; um evento estranho vira um chamado de investigação, não um incidente de quarenta minutos.

Mas eu preciso ser honesto sobre o custo, porque DLQ tem uma rasteira que quase ninguém conta: **ela quebra a ordem**. Se eu estaciono o `FundosReservados` da Ana e sigo processando, o `PixLiquidado` dela vai ser aplicado antes do antecessor — e a projeção da conta da Ana fica inconsistente. Para fluxo ordenado por chave, o padrão refinado é estacionar a mensagem **e pausar aquela chave**: os eventos da Ana aguardam a resolução do veneno dela; o resto do mundo segue. Mais complexo? É. Mas é a complexidade proporcional a um sistema que mostra dinheiro na tela. No mínimo, saibam qual dos dois modos o seu consumidor implementa — descobrir isso durante o incidente é tarde.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a4dlq-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
    <marker id="a4dlq-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
    <marker id="a4dlq-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <!-- Fila de entrada -->
  <text x="20" y="28" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Tópico (particionado por conta_id — ordem por chave, nunca global)</text>
  <g font-family="monospace" font-size="10">
    <rect x="20" y="42" width="90" height="40" rx="5" fill="#eef2ff" stroke="#c7d2fe"/><text x="65" y="66" text-anchor="middle" fill="#333">E2E-101</text>
    <rect x="118" y="42" width="90" height="40" rx="5" fill="#eef2ff" stroke="#c7d2fe"/><text x="163" y="66" text-anchor="middle" fill="#333">E2E-102</text>
    <rect x="216" y="42" width="90" height="40" rx="5" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/><text x="261" y="60" text-anchor="middle" fill="#7a5c00">E2E-102</text><text x="261" y="74" text-anchor="middle" fill="#7a5c00">(duplicada)</text>
    <rect x="314" y="42" width="90" height="40" rx="5" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/><text x="359" y="60" text-anchor="middle" fill="#7f1d1d">☠ E2E-103</text><text x="359" y="74" text-anchor="middle" fill="#7f1d1d">(veneno)</text>
    <rect x="412" y="42" width="90" height="40" rx="5" fill="#eef2ff" stroke="#c7d2fe"/><text x="457" y="66" text-anchor="middle" fill="#333">E2E-104</text>
  </g>
  <line x1="502" y1="62" x2="560" y2="62" stroke="#888" stroke-width="2" marker-end="url(#a4dlq-arrow)"/>
  <!-- Consumidor -->
  <rect x="560" y="30" width="300" height="70" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="710" y="55" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Consumidor idempotente</text>
  <text x="710" y="75" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">dedup por E2E ID + tipo · ou projeção upsert</text>
  <!-- Saída 1: duplicada ignorada -->
  <line x1="640" y1="100" x2="530" y2="150" stroke="#888" stroke-width="2" stroke-dasharray="4 3" marker-end="url(#a4dlq-arrow)"/>
  <rect x="380" y="150" width="200" height="44" rx="8" fill="#fff" stroke="#999" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="480" y="169" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">E2E-102 já processado</text>
  <text x="480" y="186" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">→ ignora (efeito exactly-once)</text>
  <!-- Saída 2: veneno para DLQ -->
  <line x1="710" y1="100" x2="710" y2="150" stroke="#b91c1c" stroke-width="2" marker-end="url(#a4dlq-red)"/>
  <text x="800" y="128" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">4 tentativas · backoff</text>
  <text x="800" y="142" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">100–800ms · falhou</text>
  <rect x="620" y="150" width="180" height="60" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="710" y="172" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">DLQ + alerta imediato</text>
  <text x="710" y="190" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">veneno sai do caminho;</text>
  <text x="710" y="203" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">a chave (conta) fica pausada</text>
  <!-- Saída 3: projeção -->
  <line x1="820" y1="100" x2="850" y2="150" stroke="#166534" stroke-width="2" marker-end="url(#a4dlq-green)"/>
  <rect x="812" y="150" width="58" height="60" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="841" y="176" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">projeção</text>
  <text x="841" y="192" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">(upsert)</text>
  <!-- Lag -->
  <rect x="20" y="240" width="850" height="70" rx="8" fill="#fff" stroke="#d4a017" stroke-width="2"/>
  <text x="40" y="264" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Consumer lag — a métrica que faltou na sexta-feira</text>
  <rect x="40" y="276" width="500" height="14" rx="4" fill="#f3f4f6" stroke="#ccc"/>
  <rect x="40" y="276" width="120" height="14" rx="4" fill="#d4a017"/>
  <text x="560" y="288" font-family="sans-serif" font-size="11" fill="#333">lag ≈ 0 sustenta a promessa de 100–300ms;</text>
  <text x="560" y="303" font-family="sans-serif" font-size="11" fill="#b91c1c">alerta em segundos de lag — não em ligações</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O consumidor civilizado: duplicata ignorada, veneno estacionado na DLQ com a chave pausada, e o lag vigiado como promessa de contrato.</p>
</div>

### 3.5 Backpressure: quando o produtor é mais rápido que o mundo

Último modo de falha assíncrono, para completar o mapa: o produtor sustentadamente mais rápido que o consumidor. Não foi o caso da sexta-feira — ali o consumidor estava *parado*, não lento — mas é o caso clássico do pico: 900 TPS de eventos entrando, projetor dando conta de 600. A fila cresce, o atraso cresce com ela, e a promessa dos 300 ms morre por estrangulamento em vez de morrer por veneno. As saídas são três, e vocês já conhecem a lógica de todas pela Aula 2: **escalar o consumidor** (mais instâncias, até o limite do paralelismo por partição), **aliviar o trabalho** (processar em lote, simplificar a projeção), ou **derramar com critério** — o load shedding do lado de quem lê: em sobrecarga, o projetor prioriza eventos que afetam saldo exibido e atrasa os de notificação. Recusar trabalho continua sendo uma forma de proteger trabalho; a Aula 2 ensinou isso para requisições, e vale igual para eventos.

### 3.6 Saga: a transação que atravessa fronteiras sem travar ninguém

E antes de fechar o capítulo assíncrono, deixa eu nomear um padrão que está escondido na aresta mais lenta da tabela — Devoluções e Disputas, a que trabalha em horas, no trilho do MED. Lembram do que a Aula 1 cravou: liquidou, acabou. Pix liquidado não se desfaz; se **compensa**, com uma transação nova — a `pacs.004`. Pois o nome de engenharia desse desenho é **saga**, do catálogo de padrões de microsserviços do Chris Richardson (microservices.io) — a alternativa ao **two-phase commit** que o professor da Aula 1 já tinha posto na mesa lá na Seção 2.6, quando falou de transações entre partições. A devolução do MED é uma saga literal: uma sequência de transações locais — cada uma commitada de verdade, na sua instituição —, costurada por eventos, com uma ação compensatória escrita para cada passo que pode falhar. E reparem que o BACEN não teria como fazer diferente: two-phase commit entre instituições independentes significaria uma instituição travada no meio do protocolo esperando a outra responder — e o trilho do país inteiro parado junto. Quem opera fila sabe: **bloqueio distribuído é incidente distribuído.**

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a4u-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a4u-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- Painel 2PC -->
  <rect x="20" y="20" width="400" height="310" rx="12" fill="#fff" stroke="#b91c1c" stroke-width="2"/>
  <text x="220" y="48" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#7f1d1d">Two-phase commit (2PC)</text>
  <rect x="130" y="65" width="180" height="40" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="220" y="90" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">Coordenador</text>
  <line x1="160" y1="105" x2="110" y2="150" stroke="#b91c1c" stroke-width="1.5" marker-end="url(#a4u-red)"/>
  <line x1="280" y1="105" x2="330" y2="150" stroke="#b91c1c" stroke-width="1.5" marker-end="url(#a4u-red)"/>
  <text x="220" y="135" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#991b1b">prepare → vote → commit</text>
  <rect x="40" y="152" width="150" height="44" rx="8" fill="#fff" stroke="#999" stroke-width="1.5"/>
  <text x="115" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">TechPix</text>
  <text x="115" y="188" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">recursos TRAVADOS</text>
  <rect x="250" y="152" width="150" height="44" rx="8" fill="#fff" stroke="#999" stroke-width="1.5"/>
  <text x="325" y="171" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Banco Beta</text>
  <text x="325" y="188" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">…não responde ⏳</text>
  <rect x="40" y="220" width="360" height="52" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="5 4"/>
  <text x="220" y="242" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7f1d1d">Se um participante trava no meio do protocolo,</text>
  <text x="220" y="260" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#991b1b">TODOS ficam bloqueados esperando — o trilho para</text>
  <text x="220" y="300" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">(+) atomicidade forte imediata</text>
  <text x="220" y="318" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">(−) latência · fragilidade · bloqueio distribuído</text>

  <!-- Painel Saga -->
  <rect x="460" y="20" width="400" height="310" rx="12" fill="#fff" stroke="#166534" stroke-width="2"/>
  <text x="660" y="48" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">Saga (microservices.io) — o MED é uma</text>
  <text x="660" y="66" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">saga regulatória</text>
  <g font-family="sans-serif" font-size="10">
    <rect x="480" y="82" width="170" height="38" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
    <text x="565" y="98" text-anchor="middle" fill="#166534">1. abre caso MED</text>
    <text x="565" y="112" text-anchor="middle" fill="#4d7c0f">commit local · TechPix</text>
    <rect x="680" y="82" width="160" height="38" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
    <text x="760" y="98" text-anchor="middle" fill="#166534">2. bloqueio cautelar</text>
    <text x="760" y="112" text-anchor="middle" fill="#4d7c0f">commit local · Banco Beta</text>
    <rect x="480" y="150" width="170" height="38" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
    <text x="565" y="166" text-anchor="middle" fill="#166534">3. pacs.004 (MD06) no SPI</text>
    <text x="565" y="180" text-anchor="middle" fill="#4d7c0f">liquidação da devolução</text>
    <rect x="680" y="150" width="160" height="38" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
    <text x="760" y="166" text-anchor="middle" fill="#166534">4. credita a vítima</text>
    <text x="760" y="180" text-anchor="middle" fill="#4d7c0f">fecha o caso</text>
  </g>
  <line x1="650" y1="101" x2="678" y2="101" stroke="#4338ca" stroke-width="2" marker-end="url(#a4u-arrow)"/>
  <line x1="760" y1="120" x2="567" y2="148" stroke="#4338ca" stroke-width="2" marker-end="url(#a4u-arrow)"/>
  <line x1="650" y1="169" x2="678" y2="169" stroke="#4338ca" stroke-width="2" marker-end="url(#a4u-arrow)"/>
  <rect x="480" y="212" width="360" height="56" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="5 4"/>
  <text x="660" y="234" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7a5c00">Passo 3 falhou? COMPENSA, não trava:</text>
  <text x="660" y="252" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">desbloqueia o cautelar, reabre a análise — trilha auditável</text>
  <text x="660" y="300" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">(+) ninguém trava ninguém · cada passo auditável (BACEN ✓)</text>
  <text x="660" y="318" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">(−) consistência eventual · compensação tem que estar ESCRITA</text>

  <text x="440" y="365" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">A Aula 1 (§2.6) apresentou os dois; o Outbox da Aula 2 é quem carrega os eventos que costuram a saga.</text>
  <text x="440" y="385" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">Pix liquidado é irrevogável — "desfazer" não existe; existe transação nova de compensação. O BACEN escolheu saga.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Saga × two-phase commit na devolução do MED: transações locais costuradas por eventos, com compensação escrita — em vez de bloqueio distribuído entre instituições.</p>
</div>

---

## 4. Mudanças seguras: o contrato evolui sem quebrar ninguém

Chegamos ao coração da aula — a parte que teria evitado a sexta-feira inteira. Porque reparem: nada do que eu descrevi até aqui foi *causado* por má engenharia de fila ou de API. A causa foi uma **mudança de contrato entregue como mudança de código**. O time do Diego tratou "renomear campo do evento" como tratava "renomear variável local": refatoração segura, testes verdes, deploy. Mas evento publicado não é variável local — o professor da Aula 3 avisou, na Seção 4.4, com a frase que eu teria emoldurado: **evento publicado é contrato público**. Vocês não sabem quem consome, não controlam quando o consumidor atualiza, e não têm o direito de mudar o passado. Hoje eu pego aquela seção teórica e transformo em processo operacional.

### 4.1 Expand/contract: toda mudança quebra-contrato vira três mudanças

O padrão fundamental para evoluir qualquer interface viva — evento, API, até schema de banco — chama-se *expand/contract*, ou *parallel change*. A ideia: nunca fazer **uma** mudança incompatível; fazer **três** mudanças compatíveis.

**Expandir:** adicionar o novo sem remover o velho. O evento `LimitesValidados` passa a carregar `carteiraId` **e** `contaId`, com o mesmo valor. Nenhum consumidor quebra — os antigos leem o campo velho, os novos já podem ler o certo.

**Migrar:** cada consumidor, no seu ritmo, passa a ler `carteiraId`. Sem coordenação de big bang, sem "todo mundo faz deploy junto na sexta" — cada time migra quando puder, e o produtor **observa** quem ainda lê o campo velho (métrica de uso por campo, ou na falta dela, uma conversa com os times consumidores).

**Contrair:** quando a telemetria mostra zero leitores do campo antigo — e só então —, o produtor remove `contaId` numa versão nova do evento. A remoção vira um não-evento: ninguém depende, ninguém sente.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 310" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a4ec-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <!-- O jeito errado -->
  <rect x="20" y="20" width="840" height="46" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="5 4"/>
  <text x="440" y="40" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">✗ 1 passo incompatível: contaId → carteiraId direto = 40 min de incidente, 300 ligações, on-call de sexta</text>
  <text x="440" y="58" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">(o que aconteceu em 12/09)</text>
  <!-- Fase 1 -->
  <rect x="20" y="95" width="260" height="130" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="150" y="120" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">1 · EXPANDIR</text>
  <rect x="45" y="132" width="210" height="48" rx="6" fill="#fff" stroke="#166534"/>
  <text x="150" y="152" text-anchor="middle" font-family="monospace" font-size="11" fill="#333">{ contaId: "c-42",</text>
  <text x="150" y="169" text-anchor="middle" font-family="monospace" font-size="11" fill="#166534">  carteiraId: "c-42" }</text>
  <text x="150" y="200" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">novo E velho, mesmo valor</text>
  <text x="150" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">nenhum consumidor quebra</text>
  <line x1="280" y1="160" x2="320" y2="160" stroke="#4338ca" stroke-width="2.5" marker-end="url(#a4ec-arrow)"/>
  <!-- Fase 2 -->
  <rect x="320" y="95" width="260" height="130" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="450" y="120" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">2 · MIGRAR</text>
  <text x="450" y="145" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">cada consumidor passa a ler</text>
  <text x="450" y="162" text-anchor="middle" font-family="monospace" font-size="11" fill="#3730a3">carteiraId</text>
  <text x="450" y="182" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">no seu ritmo — sem big bang</text>
  <text x="450" y="205" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">produtor observa a métrica de</text>
  <text x="450" y="218" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">uso do campo velho caindo</text>
  <line x1="580" y1="160" x2="620" y2="160" stroke="#4338ca" stroke-width="2.5" marker-end="url(#a4ec-arrow)"/>
  <!-- Fase 3 -->
  <rect x="620" y="95" width="240" height="130" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="740" y="120" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">3 · CONTRAIR</text>
  <rect x="645" y="132" width="190" height="48" rx="6" fill="#fff" stroke="#166534"/>
  <text x="740" y="152" text-anchor="middle" font-family="monospace" font-size="11" fill="#999" text-decoration="line-through">contaId</text>
  <text x="740" y="169" text-anchor="middle" font-family="monospace" font-size="11" fill="#166534">{ carteiraId: "c-42" }</text>
  <text x="740" y="200" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">só com ZERO leitores do velho</text>
  <text x="740" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">a remoção vira não-evento</text>
  <!-- Régua -->
  <rect x="20" y="252" width="840" height="40" rx="8" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="440" y="270" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">✓ 3 passos compatíveis: alguns dias de calendário, zero adrenalina</text>
  <text x="440" y="287" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">o schema registry recusa no CI qualquer mudança que pule essas fases — a fitness function do contrato</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Expand/contract: toda mudança quebra-contrato vira três mudanças compatíveis — e a velocidade se mede pela ausência de vítimas.</p>
</div>

O custo é evidente: três passos onde antes havia um, e uma janela em que o payload carrega redundância. E eu defendo esse custo sem pestanejar, com a régua de plantonista: o passo único custou quarenta minutos de incidente, trezentas ligações e um on-call de sexta à noite; os três passos custam alguns dias de calendário e zero adrenalina. **Velocidade de mudança não se mede pela pressa do produtor; mede-se pela ausência de vítimas entre os consumidores.**

### 4.2 Schema registry: a fitness function dos contratos

Mas processo que depende de disciplina humana falha no dia em que alguém está com pressa — e time de fintech está sempre com pressa. Então a gente automatiza a disciplina, e o instrumento se chama *schema registry*: um serviço que guarda o esquema de cada tipo de evento, versão a versão, e que **valida compatibilidade no ato da publicação**. O time do Diego tenta registrar o `LimitesValidados` sem o campo `contaId`; o registry compara com a versão vigente, aplica a regra de compatibilidade configurada — retrocompatível: consumidores antigos precisam conseguir ler eventos novos — e **recusa**. A quebra morre no CI, numa mensagem de erro educada, semanas antes de qualquer sexta-feira.

Reparem no que isso é, na linguagem do curso: uma **fitness function de contrato** — a mesma espécie de verificação automática que a Aula 2 usou para proteger fronteiras de módulo (ArchUnit) e que protege a invariante do ledger. O professor da Aula 3 encerrou a Seção 4.4 prometendo exatamente essa ponte; está paga. E a régua de compatibilidade — retrocompatível, prospectiva ou completa — deixa de ser opinião em code review e vira configuração versionada, auditável, igual para todos os times.

### 4.3 Contratos dirigidos pelo consumidor: o Pact para as arestas síncronas

O registry protege eventos. E as arestas síncronas — a API que Pagamentos expõe, a que Antifraude expõe? O padrão equivalente chama-se *consumer-driven contracts*, contratos dirigidos pelo consumidor, e a ferramenta canônica é o **Pact**. A inversão é elegante: em vez de o provedor declarar "minha API é essa, virem-se", cada **consumidor** declara, em teste executável, o que ele efetivamente usa — "eu chamo `POST /validar-limites` e leio os campos `resultado` e `carteiraId` da resposta". Esses contratos ficam num repositório central, e o CI do **provedor** roda todos eles a cada mudança: se uma alteração minha quebra o uso declarado de qualquer consumidor, meu build falha — com nome e endereço de quem eu ia quebrar.

O efeito de segunda ordem é quase mais valioso que o teste: o provedor ganha, de graça, o **inventário de quem depende de quê**. Metade dos incidentes de integração que eu atendi na vida começaram com a frase "a gente não sabia que alguém usava esse campo". Contrato dirigido pelo consumidor torna essa frase impossível.

### 4.4 E o mundo que vocês não controlam

Uma nota de realismo antes de seguir: tudo isso vale para contratos **internos**. O contrato com o BACEN — `pacs.008`, `pacs.002`, `pacs.004`, a API do DICT — evolui no ritmo do regulador, com manuais versionados e datas de vigência, como vocês viram na Aula 1 com o Pix Automático e o MED. O TechPix não negocia esse contrato; ele **se adapta**. E é por isso que a camada anticorrupção da Aula 3 é tão preciosa: quando o BACEN muda uma mensagem, a mudança bate no ACL e para nele — o dialeto interno, `PixIniciado`, `PixLiquidado`, fica intacto, e o resto do sistema nem fica sabendo. ACL não é burocracia de tradução; é **amortecedor de mudança alheia**.

---

## 5. Resiliência por aresta: de heroísmo a política

A Aula 2 apresentou o arsenal — timeout, retry com backoff e jitter, retry budget, circuit breaker, bulkhead, load shedding — no calor do incidente do dia 5. O que eu quero acrescentar é a mudança de postura que separa um sistema que *tem* esses padrões de um sistema *operável*: sair de "cada desenvolvedor aplica o padrão que lembrar, onde lembrar" para **política declarada por aresta** — escrita, versionada, revisada como código.

A tabela de políticas do caminho crítico do TechPix, hoje:

| Aresta | Timeout | Retry | Circuit breaker | Bulkhead | Fallback |
|---|---|---|---|---|---|
| → DICT | 1,2 s | 1 retentativa, backoff 100 ms, dentro do retry budget global de 10% | abre com 50% de falha em janela de 30 s | pool dedicado (o do incidente da Aula 2!) | cache de chaves recentes, respeitando as regras de retenção do BACEN |
| → Antifraude | 150 ms | **zero retry** (decisão no caminho crítico; retentar é estourar o orçamento) | abre com 30% de falha em 10 s | pool dedicado | **política de negócio** — Seção 5.2 |
| → SPI | 6 s (folga sobre o p99 de 4,6 s) | zero retry síncrono; incerteza vai para reconciliação por E2E ID (Aula 1) | abre em falha sustentada; aciona plano de contingência | pool dedicado | fila de reapresentação + comunicação ao cliente |
| → Ledger (reserva) | 500 ms | zero (transação local) | n/a (mesmo processo, hoje) | n/a | não existe fallback para a verdade — falhou, falhou fechado |
| Outbox → projetores | n/a (assíncrono) | 4 tentativas, backoff 100–800 ms | n/a | consumidores isolados por grupo | DLQ com pausa por chave + alerta de lag |

Três comentários que a tabela sozinha não faz.

**Zero retry no Antifraude não é descaso — é aritmética.** Orçamento de 100 ms, timeout de 150: uma retentativa dobraria o gasto e roubaria a fatia dos elos seguintes. No caminho crítico apertado, retry é um luxo que o orçamento não compra; a robustez tem que vir de outro lugar — do fallback, que é a próxima conversa.

**O circuit breaker do SPI existe para proteger o SPI de vocês — e vocês do acúmulo.** Se o SPI degrada, martelar `pacs.008` numa infraestrutura sofrendo só engorda a fila do outro lado e a de vocês. Abrir o circuito, enfileirar com honestidade, avisar o cliente que o pagamento está em processamento — é feio, mas é o feio controlado, infinitamente melhor que o bonito que desaba.

**E reparem na linha do Ledger: não existe fallback para a verdade.** Se a escrita da reserva falha, o Pix falha, fechado, na hora. Tentar "aceitar e acertar depois" é criar dinheiro por otimismo — a violação exata da conservação que o ledger existe para impedir. Falhar fechado no núcleo é o fallback.

### 5.2 Fail-open ou fail-closed: a decisão que não é de engenharia

Agora a linha mais interessante da tabela: o que fazer quando o **Antifraude não responde** — timeout estourado, circuito aberto — e há um Pix na mão esperando veredito?

Duas respostas possíveis, ambas defensáveis, ambas caras. **Fail-closed:** na dúvida, recusa. Nenhuma fraude passa; em compensação, durante os minutos de uma degradação do Antifraude, o TechPix recusa 100% dos Pix — clientes legítimos barrados, receita perdida, reputação arranhada, e possivelmente uma menção desagradável no índice de disponibilidade que o BACEN monitora. **Fail-open:** na dúvida, deixa passar. Disponibilidade preservada; em compensação, a janela de degradação vira temporada de caça aberta para exatamente o tipo de adversário que monitora fintechs esperando esses momentos.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 860 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a4fb-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
    <marker id="a4fb-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
    <marker id="a4fb-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
    <marker id="a4fb-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#d4a017"/>
    </marker>
  </defs>
  <!-- Pix chega -->
  <rect x="20" y="90" width="140" height="52" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="90" y="112" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Pix na mão</text>
  <text x="90" y="130" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">aguardando veredito</text>
  <line x1="160" y1="116" x2="215" y2="116" stroke="#888" stroke-width="2" marker-end="url(#a4fb-arrow)"/>
  <!-- Antifraude fora -->
  <rect x="215" y="82" width="180" height="68" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2" stroke-dasharray="5 4"/>
  <text x="305" y="106" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">Antifraude não responde</text>
  <text x="305" y="124" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">timeout 150ms estourado</text>
  <text x="305" y="139" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">ou circuito aberto</text>
  <line x1="395" y1="116" x2="450" y2="116" stroke="#888" stroke-width="2" marker-end="url(#a4fb-arrow)"/>
  <!-- Decisão -->
  <polygon points="510,66 590,116 510,166 430,116" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="510" y="112" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">valor?</text>
  <text x="510" y="130" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">(política escrita)</text>
  <!-- Ramo baixo -->
  <line x1="540" y1="80" x2="640" y2="45" stroke="#166534" stroke-width="2.5" marker-end="url(#a4fb-green)"/>
  <text x="575" y="48" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">≤ R$ 200</text>
  <rect x="640" y="20" width="200" height="56" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="740" y="42" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">FAIL-OPEN controlado</text>
  <text x="740" y="60" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">aprova + flag de análise posterior</text>
  <!-- Ramo intermediário -->
  <line x1="590" y1="116" x2="640" y2="116" stroke="#d4a017" stroke-width="2.5" marker-end="url(#a4fb-amber)"/>
  <text x="612" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">faixa média</text>
  <rect x="640" y="92" width="200" height="50" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="740" y="112" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7a5c00">política intermediária</text>
  <text x="740" y="130" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">limite reduzido · confirmação extra</text>
  <!-- Ramo alto -->
  <line x1="540" y1="152" x2="640" y2="185" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#a4fb-red)"/>
  <text x="575" y="185" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">&gt; R$ 200</text>
  <rect x="640" y="160" width="200" height="56" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="740" y="182" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">FAIL-CLOSED</text>
  <text x="740" y="200" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">recusa — prudência acima de otimismo</text>
  <!-- Rodapé -->
  <rect x="20" y="240" width="820" height="46" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="430" y="259" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">O número "R$ 200" é apetite de risco — decisão de produto, risco e compliance, escrita ANTES do incidente</text>
  <text x="430" y="277" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">a pior versão é a decidida implicitamente por um catch genérico, descoberta na frente do regulador</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Fail-open ou fail-closed, segmentado por valor: a engenharia executa; quem decide é o negócio.</p>
</div>

A resposta madura recusa o binário e **segmenta pelo risco**: valor baixo — digamos, até R$ 200 — passa com registro para análise posterior; valor alto falha fechado; faixa intermediária, política intermediária (limite reduzido, confirmação adicional). O ponto pedagógico, e eu quero que isso fique gravado: **essa segmentação não é uma decisão de engenharia — é uma decisão de negócio que a engenharia executa.** O número "R$ 200" é uma aposta sobre apetite de risco: quanto prejuízo de fraude a empresa aceita para não recusar clientes legítimos? Quem responde isso é produto, risco e compliance — juntos, de olhos abertos, **antes** do incidente, com a decisão escrita no contrato da aresta. A pior versão possível dessa decisão é a tomada implicitamente por um `catch` genérico que algum estagiário escreveu, descoberta durante o incidente, na frente do regulador. Eu já vi. Não recomendo.

---

## 6. O artefato: o Contrato de Integração

Tudo que a gente construiu hoje converge para um documento — e seguindo a tradição da casa, a gente escreve juntos. A Aula 3 deixou a **spec de contexto**, que descreve o *interior* de uma fronteira: linguagem, invariantes, eventos. O artefato de hoje é o irmão dela que descreve as *arestas*: o **Contrato de Integração** — uma entrada por aresta do mapa, com tudo que dois lados precisam pactuar para conversar sem se machucar.

A entrada da aresta mais quente do sistema, como exemplo:

```
CONTRATO DE INTEGRAÇÃO · Pagamentos → Antifraude e Limites        v1.2 (2025-09-19)

Estilo          Síncrono, requisição-resposta (gRPC quando extraído; chamada de
                módulo hoje). Decisão no caminho crítico do Pix.
Contrato        ValidarLimites(carteiraId, valor, e2eId) → resultado + fatores.
                Schema no registry; regra de compatibilidade: retrocompatível.
Mudanças        Expand/contract obrigatório para qualquer campo. Anúncio no canal
                #contratos com 2 semanas de antecedência para mudança de semântica.
Orçamento       100 ms p99 · timeout 150 ms · deadline propagado do gateway.
Retry           Nenhum (caminho crítico). Idempotente por e2eId mesmo assim —
                retry de camada superior pode reapresentar.
Circuit breaker 30% de falha em janela de 10 s → aberto; meia-abertura a cada 5 s.
Fallback        POLÍTICA DE NEGÓCIO (aprovada por Risco, 2025-09-15):
                valor ≤ R$ 200 → aprova com flag de análise posterior;
                valor > R$ 200 → falha fechado.
Consumidores    Pagamentos (Pact registrado). Inventário completo no broker de
                contratos.
Donos           Provedor: Antifraude e Limites (Diego). Consumidor: Pagamentos
                (Marina). Revisão conjunta trimestral.
Observação      Lag e taxa de fallback são métricas de primeira classe (Aula 7).
```

Reparem no que esse documento **não** é: não é um ADR. E não por acaso — deixa eu ser explícito, porque sei que a pergunta vem. O ADR registra uma decisão pontual e imutável; o contrato de integração é um **documento vivo**, versionado, que muda toda vez que a aresta muda — mais parecido com a spec da Aula 3 do que com o ADR-001. A numeração dos ADRs do TechPix parou no 002, aquele do Outbox, com a linha de revisão dele ainda em aberto — "se a contenção persistir, reparticionar a própria escrita do ledger". Eu li essa linha quando assumi a turma, e vou dizer o que eu disse para o time: **o próximo ADR numerado, o 003, só nasce quando alguém decidir mexer na escrita do ledger — e hoje não é esse dia.** A conta `pix_a_liquidar` segue lá, única, aguentando o tranco. Anotem que eu falei isso; essa linha em aberto ainda vai dar história nesse curso.

E uma última honestidade sobre documento vivo, porque eu sei o destino de 90% deles: wiki esquecida. O contrato de integração só fica vivo se estiver **amarrado a coisas que executam**: o schema aponta para o registry (que valida no CI), os consumidores apontam para o broker de Pact (que roda no CI), as métricas apontam para dashboards (que alertam). Documento que nada executa é obituário antecipado. Documento que o CI lê é lei.

---

## 7. Para fechar: três âncoras e uma promessa

Recapitulando o que eu quero que atravesse a semana com vocês.

Primeiro: **contrato é arquitetura.** A fronteira entre dois componentes — nome de campo, semântica de erro, orçamento de tempo, promessa de atraso — quebra sem que nenhum dos lados erre. Diego e Marina, um andar abaixo, em tempo de execução. Trate toda interface como contrato público: versionada, validada por máquina, evoluída por expand/contract.

Segundo: **síncrono acopla disponibilidade; assíncrono acopla entendimento.** Escolham por aresta, com critério, e paguem o preço certo de cada lado: deadline propagado e timeout derivado no síncrono; consumidor idempotente, lag monitorado e DLQ no assíncrono.

Terceiro: **resiliência é política declarada, não heroísmo de plantão.** Timeout, retry, breaker, fallback — por aresta, por escrito, com a decisão de negócio (fail-open ou fail-closed, e a quantos reais) tomada por quem tem mandato para ela, antes do incidente.

E a promessa: na tabela de políticas, a aresta Pagamentos → Antifraude ficou com o orçamento mais apertado do sistema — 100 milissegundos para decidir se um Pix é honesto. Hoje, atrás dessa aresta, moram regras: limiares, listas, heurísticas que o Diego mantém. Na próxima aula, a gente vai descobrir por que as regras não bastam — vai ser numa madrugada de outubro, com um golpe que nenhuma regra pegou — e vai colocar um **modelo de machine learning dentro desses 100 milissegundos**: feature store, inferência em tempo real, modelo aberto rodando na casa, e a pergunta que define IA em fintech: quando o modelo diz "talvez", quem decide? Tragam a tabela de políticas. Ela vai ganhar uma linha que pensa.

E uma última coisa, que eu vou repetir no fim de todas as minhas aulas, porque plantão me ensinou a nunca perder de vista o estado da obra: o retrato do TechPix como ele fica hoje. Cinza é o que a gente herdou; verde é o que foi parafusado nesta aula.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 290" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="440" y="26" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333">O TechPix ao fim da Aula 4</text>
  <!-- Já existia (cinza) -->
  <g font-family="sans-serif">
    <rect x="20" y="48" width="200" height="48" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="120" y="68" text-anchor="middle" font-size="11" font-weight="bold" fill="#57534e">Monólito modular + ledger</text>
    <text x="120" y="84" text-anchor="middle" font-size="10" fill="#78716c">PostgreSQL serializable · A1/A2</text>
    <rect x="234" y="48" width="200" height="48" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="334" y="68" text-anchor="middle" font-size="11" font-weight="bold" fill="#57534e">Idempotência E2E ID</text>
    <text x="334" y="84" text-anchor="middle" font-size="10" fill="#78716c">efeito exactly-once · A1</text>
    <rect x="448" y="48" width="200" height="48" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="548" y="68" text-anchor="middle" font-size="11" font-weight="bold" fill="#57534e">Outbox → relay → Kafka</text>
    <text x="548" y="84" text-anchor="middle" font-size="10" fill="#78716c">CQRS: Redis + réplica · A2</text>
    <rect x="662" y="48" width="198" height="48" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="761" y="68" text-anchor="middle" font-size="11" font-weight="bold" fill="#57534e">5 contextos + ACL BACEN</text>
    <text x="761" y="84" text-anchor="middle" font-size="10" fill="#78716c">spec + constituição · A3</text>
    <rect x="20" y="104" width="200" height="48" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="120" y="124" text-anchor="middle" font-size="11" font-weight="bold" fill="#57534e">Defesas da Aula 2</text>
    <text x="120" y="140" text-anchor="middle" font-size="10" fill="#78716c">backoff+jitter · breaker · bulkhead</text>
  </g>
  <!-- Novo desta aula (verde) -->
  <g font-family="sans-serif">
    <rect x="20" y="176" width="200" height="48" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="120" y="196" text-anchor="middle" font-size="11" font-weight="bold" fill="#166534">Contratos por aresta</text>
    <text x="120" y="212" text-anchor="middle" font-size="10" fill="#4d7c0f">gRPC/.proto interno · REST borda</text>
    <rect x="234" y="176" width="200" height="48" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="334" y="196" text-anchor="middle" font-size="11" font-weight="bold" fill="#166534">Deadline propagation</text>
    <text x="334" y="212" text-anchor="middle" font-size="10" fill="#4d7c0f">o orçamento viaja com a requisição</text>
    <rect x="448" y="176" width="200" height="48" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="548" y="196" text-anchor="middle" font-size="11" font-weight="bold" fill="#166534">Consumidor idempotente + DLQ</text>
    <text x="548" y="212" text-anchor="middle" font-size="10" fill="#4d7c0f">lag vigiado · saga nas Devoluções</text>
    <rect x="662" y="176" width="198" height="48" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="761" y="196" text-anchor="middle" font-size="11" font-weight="bold" fill="#166534">Schema registry + Pact</text>
    <text x="761" y="212" text-anchor="middle" font-size="10" fill="#4d7c0f">expand/contract · registry no CI</text>
    <rect x="234" y="232" width="414" height="44" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="441" y="250" text-anchor="middle" font-size="11" font-weight="bold" fill="#166534">Contrato de Integração — políticas timeout/retry/fallback por aresta</text>
    <text x="441" y="266" text-anchor="middle" font-size="10" fill="#4d7c0f">fail-open/fail-closed decidido por valor, por escrito, antes do incidente</text>
  </g>
  <text x="440" y="288" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#999">cinza = já existia · verde = construído nesta aula</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A construção incremental do TechPix: a Aula 4 não adicionou caixas novas — ela transformou cada seta em contrato.</p>
</div>

---

## Apêndice — Termos novos desta aula

| Termo | O que é |
|---|---|
| **Deadline propagation** | Propagar o instante absoluto de expiração da requisição por toda a cadeia de chamadas; quando o orçamento acaba, todos desistem juntos — elimina trabalho zumbi. |
| **Trabalho zumbi** | Processamento que continua consumindo recursos para uma requisição que o cliente já abandonou. |
| **gRPC / protobuf** | Protocolo de RPC com contrato compilado (`.proto`), serialização binária e deadline nativo; padrão para comunicação interna entre serviços. |
| **`Idempotency-Key`** | Header que carrega a chave de idempotência da Aula 1 como contrato explícito de API; mesma chave + corpo diferente = erro, nunca retry. |
| **Consumidor idempotente** | Consumidor que produz o mesmo estado ao receber a mesma mensagem N vezes — por deduplicação explícita ou escrita upsert. |
| **Consumer lag** | Quantidade de mensagens publicadas e ainda não processadas por um consumidor; métrica de primeira classe de toda aresta assíncrona. |
| **Poison message (mensagem envenenada)** | Mensagem que falha de forma permanente; sob retry infinito, paralisa a fila inteira. |
| **DLQ (dead letter queue)** | Fila-estacionamento para mensagens que esgotaram as retentativas; tira o veneno do caminho ao custo de quebrar a ordem — em fluxo ordenado, exige pausa por chave. |
| **Backpressure** | Pressão de acúmulo quando o produtor é sustentadamente mais rápido que o consumidor; respostas: escalar, aliviar, derramar com critério. |
| **Expand/contract (parallel change)** | Evoluir contrato em três passos compatíveis — expandir, migrar, contrair — em vez de um passo incompatível. |
| **Schema registry** | Serviço que versiona esquemas de eventos e valida compatibilidade no ato da publicação; a fitness function dos contratos. |
| **Consumer-driven contracts / Pact** | Cada consumidor declara em teste executável o que usa da API; o CI do provedor roda esses contratos e não deixa quebrar quem depende. |
| **Fail-open / fail-closed** | Na falha do validador: deixar passar (disponibilidade, risco de fraude) ou recusar (segurança, custo de clientes barrados); em fintech, segmentado por valor — decisão de negócio, não de engenharia. |
| **Política por aresta** | Timeout, retry, breaker, bulkhead e fallback declarados por escrito para cada aresta do mapa, versionados como código. |
| **Contrato de Integração** | Artefato vivo, irmão da spec da Aula 3: uma entrada por aresta com estilo, contrato, orçamento, políticas, fallback e donos — amarrado a registry, Pact e dashboards para não virar wiki morta. |
| **Saga** | Transação distribuída como sequência de transações locais costuradas por eventos, com ação compensatória escrita para cada passo — a devolução do MED (`pacs.004`/MD06) é uma saga regulatória. Padrão do catálogo microservices.io (Chris Richardson). |
| **Two-phase commit (2PC)** | Protocolo de atomicidade forte entre participantes (prepare → vote → commit); se um trava no meio, todos ficam bloqueados esperando — inviável entre instituições independentes, por isso o BACEN escolheu saga. |
| **Modelo OSI** | As 7 camadas da comunicação em rede; no TechPix: TLS/RSFN na apresentação, HTTP/2+gRPC em L7, TCP em L4 — timeout e circuit breaker enxergam L7; firewall enxerga L3/L4. Semente do L4×L7 que a Aula 6 usa no canary. |
| **microservices.io** | Catálogo de padrões de microsserviços de Chris Richardson — referência dos padrões usados no curso: Transactional Outbox, Saga, CQRS, Event Sourcing, Circuit Breaker, Database per Service, Strangler Fig. |

---

[← Aula 3](aula3-conteudo-completo.md) · [Índice](index.md) · [Aula 5 →](aula5-conteudo-completo.md)
