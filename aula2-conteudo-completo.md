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

E existe uma segunda armadilha, mais sutil que o `JOIN` — e mais perigosa, porque ela nem parece errada: **dois módulos escrevendo na mesma transação ACID.** No monólito, com todos os schemas no mesmo banco, isso é tecnicamente grátis: Pagamentos grava a ordem, Contas atualiza o extrato, tudo num `COMMIT` só, atômico, lindo. E é exatamente por ser grátis que todo mundo faz. Só que essa transação compartilhada é um acoplamento invisível: no dia em que um dos dois módulos virar serviço, a chamada vira rede — e **atomicidade não atravessa a rede.** O que era um `COMMIT` vira uma saga com compensação, e vocês descobrem, no meio da extração, que os dois módulos nunca foram separáveis de verdade. Por isso a regra de ouro tem uma irmã: **cada transação pertence a um módulo só.** O que precisa acontecer atomicamente, junto, mora dentro do mesmo módulo; entre módulos, a comunicação aceita atraso. A Aula 3 vai dar um nome preciso para "o que precisa acontecer junto" — guardem a inquietação até lá.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 860 320" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <!-- Monólito modular -->
  <text x="255" y="30" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Monólito modular do TechPix — um único deploy</text>
  <rect x="20" y="42" width="470" height="215" rx="12" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <g font-family="sans-serif" font-size="12" fill="#333">
    <rect x="38" y="60" width="138" height="48" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="107" y="88" text-anchor="middle">Identidade e KYC</text>
    <rect x="188" y="60" width="138" height="48" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="257" y="88" text-anchor="middle">Contas</text>
    <rect x="338" y="60" width="138" height="48" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="407" y="82" text-anchor="middle" font-weight="bold" fill="#166534">Ledger</text>
    <text x="407" y="98" text-anchor="middle" font-size="10" fill="#166534">Σ débitos = Σ créditos</text>
    <rect x="38" y="126" width="138" height="48" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="107" y="154" text-anchor="middle">Pagamentos</text>
    <rect x="188" y="126" width="138" height="48" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="257" y="154" text-anchor="middle">Cartões</text>
    <rect x="338" y="126" width="138" height="48" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="407" y="154" text-anchor="middle">Antifraude</text>
  </g>
  <rect x="38" y="192" width="438" height="48" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="257" y="212" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Regra de ouro: nenhum módulo lê a tabela de outro</text>
  <text x="257" y="229" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">toda comunicação passa por interface explícita</text>
  <text x="255" y="290" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">✓ fronteiras internas = ensaio para futuros serviços</text>

  <!-- Big Ball of Mud -->
  <text x="700" y="30" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#b91c1c">Big Ball of Mud</text>
  <rect x="560" y="42" width="280" height="215" rx="12" fill="#fef2f2" stroke="#b91c1c" stroke-width="2" stroke-dasharray="6 4"/>
  <g font-family="sans-serif" font-size="11" fill="#7f1d1d">
    <rect x="580" y="62" width="90" height="36" rx="6" fill="#fff" stroke="#c2410c"/>
    <text x="625" y="84" text-anchor="middle">Cartões</text>
    <rect x="722" y="62" width="90" height="36" rx="6" fill="#fff" stroke="#c2410c"/>
    <text x="767" y="84" text-anchor="middle">Ledger</text>
    <rect x="580" y="196" width="90" height="36" rx="6" fill="#fff" stroke="#c2410c"/>
    <text x="625" y="218" text-anchor="middle">Pagamentos</text>
    <rect x="722" y="196" width="90" height="36" rx="6" fill="#fff" stroke="#c2410c"/>
    <text x="767" y="218" text-anchor="middle">Antifraude</text>
    <rect x="652" y="128" width="90" height="36" rx="6" fill="#fff" stroke="#c2410c"/>
    <text x="697" y="150" text-anchor="middle">Contas</text>
  </g>
  <g stroke="#b91c1c" stroke-width="1.5" opacity="0.7">
    <line x1="625" y1="98" x2="767" y2="196"/>
    <line x1="767" y1="98" x2="625" y2="196"/>
    <line x1="625" y1="98" x2="697" y2="128"/>
    <line x1="767" y1="98" x2="697" y2="128"/>
    <line x1="625" y1="196" x2="697" y2="164"/>
    <line x1="767" y1="196" x2="697" y2="164"/>
    <line x1="625" y1="98" x2="625" y2="196"/>
    <line x1="767" y1="98" x2="767" y2="196"/>
  </g>
  <text x="700" y="290" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">✗ JOIN direto na tabela alheia — extração impossível</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Monólito não é o vilão: com fronteiras internas reais, ele é o ensaio das fronteiras de serviço. O vilão é a bola de lama.</p>
</div>

Só que caixas paradas não mostram um sistema — mostram um organograma. Para vocês **verem** o monólito funcionando, deixa eu fazer o que todo bom desenho de payment system faz: pegar **uma** transação e acompanhar ela atravessando o sistema, passo numerado por passo numerado, com a fronteira entre "o que é nosso" e "o que é do Banco Central" desenhada explicitamente. Este é o retrato do TechPix na manhã do dia 5 — antes de qualquer coisa quebrar:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 940 560" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2w-int" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a2w-ext" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#d4a017"/>
    </marker>
  </defs>
  <text x="470" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Um Pix atravessa o monólito — o TechPix na manhã do dia 5</text>

  <!-- fronteira dentro/fora -->
  <line x1="700" y1="34" x2="700" y2="505" stroke="#666" stroke-width="1.5" stroke-dasharray="8 5"/>
  <text x="692" y="48" text-anchor="end" font-family="sans-serif" font-size="11" fill="#666">dentro (TechPix)</text>
  <text x="710" y="48" font-family="sans-serif" font-size="11" fill="#666">fora (BACEN)</text>

  <!-- cliente e gateway -->
  <rect x="10" y="190" width="85" height="52" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="52" y="212" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">App da Ana</text>
  <text x="52" y="229" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">toca "enviar"</text>
  <rect x="125" y="178" width="120" height="76" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="185" y="200" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Gateway / BFF</text>
  <text x="185" y="218" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">TLS · rate limit</text>
  <text x="185" y="234" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">idempotência (E2E ID)</text>

  <!-- monólito -->
  <rect x="265" y="40" width="360" height="470" rx="12" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="445" y="62" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">Monólito TechPix — um processo, um deploy, um banco</text>

  <!-- fileira de cima -->
  <rect x="280" y="80" width="105" height="52" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="332" y="102" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Identidade/KYC</text>
  <text x="332" y="118" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#5a55a0">cliente ativo? PLD?</text>
  <rect x="395" y="80" width="105" height="52" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="447" y="102" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Antifraude</text>
  <text x="447" y="118" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#5a55a0">score em ~100 ms</text>
  <rect x="510" y="80" width="100" height="52" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="560" y="102" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Ledger</text>
  <text x="560" y="118" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">Σ déb = Σ créd</text>

  <!-- orquestrador -->
  <rect x="330" y="185" width="230" height="58" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
  <text x="445" y="208" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Pagamentos — orquestrador</text>
  <text x="445" y="227" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">coordena o fluxo inteiro</text>

  <!-- fileira de baixo -->
  <rect x="280" y="290" width="145" height="52" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="352" y="311" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Contas</text>
  <text x="352" y="328" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#5a55a0">extrato · saldo exibido</text>
  <rect x="455" y="290" width="140" height="52" rx="8" fill="#f5f5f4" stroke="#999" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text x="525" y="311" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">Cartões</text>
  <text x="525" y="328" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#78716c">roadmap — fora do fluxo</text>

  <text x="445" y="368" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">passo 8: extrato e notificação no mesmo processo,</text>
  <text x="445" y="384" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">nos mesmos pools da escrita — guardem esse detalhe</text>

  <!-- banco -->
  <rect x="280" y="402" width="330" height="94" rx="10" fill="#f9f9f7" stroke="#78716c" stroke-width="1.5"/>
  <text x="445" y="422" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#44403c">PostgreSQL — um banco físico</text>
  <text x="445" y="437" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#78716c">um schema por módulo: fronteira lógica, recursos compartilhados</text>
  <g stroke-width="1">
    <path d="M 298 448 v22 a22 5 0 0 0 44 0 v-22" fill="#eef2ff" stroke="#4338ca"/>
    <ellipse cx="320" cy="448" rx="22" ry="5" fill="#eef2ff" stroke="#4338ca"/>
    <path d="M 358 448 v22 a22 5 0 0 0 44 0 v-22" fill="#eef2ff" stroke="#4338ca"/>
    <ellipse cx="380" cy="448" rx="22" ry="5" fill="#eef2ff" stroke="#4338ca"/>
    <path d="M 418 448 v22 a22 5 0 0 0 44 0 v-22" fill="#f0fdf4" stroke="#166534"/>
    <ellipse cx="440" cy="448" rx="22" ry="5" fill="#f0fdf4" stroke="#166534"/>
    <path d="M 478 448 v22 a22 5 0 0 0 44 0 v-22" fill="#eef2ff" stroke="#4338ca"/>
    <ellipse cx="500" cy="448" rx="22" ry="5" fill="#eef2ff" stroke="#4338ca"/>
    <path d="M 538 448 v22 a22 5 0 0 0 44 0 v-22" fill="#eef2ff" stroke="#4338ca"/>
    <ellipse cx="560" cy="448" rx="22" ry="5" fill="#eef2ff" stroke="#4338ca"/>
  </g>
  <g font-family="sans-serif" font-size="8" fill="#666" text-anchor="middle">
    <text x="320" y="487">identidade</text>
    <text x="380" y="487">contas</text>
    <text x="440" y="487" fill="#166534">ledger</text>
    <text x="500" y="487">pagamentos</text>
    <text x="560" y="487">antifraude</text>
  </g>

  <!-- BACEN -->
  <rect x="730" y="120" width="170" height="64" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="815" y="145" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">DICT</text>
  <text x="815" y="164" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">resolve chave Pix · p99 1 s</text>
  <rect x="730" y="300" width="170" height="76" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="815" y="323" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">SPI</text>
  <text x="815" y="342" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">pacs.008 → pacs.002</text>
  <text x="815" y="358" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">liquidação final · p99 4,6 s</text>

  <!-- fluxo interno -->
  <g stroke="#4338ca" stroke-width="2">
    <line x1="95" y1="216" x2="123" y2="216" marker-end="url(#a2w-int)"/>
    <line x1="245" y1="216" x2="328" y2="214" marker-end="url(#a2w-int)"/>
    <line x1="375" y1="183" x2="343" y2="136" marker-end="url(#a2w-int)"/>
    <line x1="445" y1="183" x2="447" y2="136" marker-end="url(#a2w-int)"/>
    <line x1="520" y1="183" x2="553" y2="136" marker-end="url(#a2w-int)"/>
    <line x1="390" y1="245" x2="362" y2="286" marker-end="url(#a2w-int)"/>
  </g>
  <!-- fluxo externo -->
  <g stroke="#d4a017" stroke-width="2.5">
    <line x1="560" y1="198" x2="727" y2="150" marker-end="url(#a2w-ext)"/>
    <line x1="560" y1="230" x2="727" y2="320" marker-end="url(#a2w-ext)"/>
  </g>
  <!-- numeração -->
  <g font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
    <circle cx="109" cy="216" r="10" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/><text x="109" y="220" fill="#333">1</text>
    <circle cx="287" cy="215" r="10" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/><text x="287" y="219" fill="#333">2</text>
    <circle cx="359" cy="160" r="10" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/><text x="359" y="164" fill="#333">3</text>
    <circle cx="447" cy="160" r="10" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/><text x="447" y="164" fill="#333">4</text>
    <circle cx="644" cy="174" r="10" fill="#fff" stroke="#b45309" stroke-width="1.5"/><text x="644" y="178" fill="#7a5c00">5</text>
    <circle cx="537" cy="160" r="10" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/><text x="537" y="164" fill="#333">6</text>
    <circle cx="644" cy="275" r="10" fill="#fff" stroke="#b45309" stroke-width="1.5"/><text x="644" y="279" fill="#7a5c00">7</text>
    <circle cx="376" cy="266" r="10" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/><text x="376" y="270" fill="#333">8</text>
  </g>

  <text x="470" y="540" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">O que este desenho ainda não tem: fila, cache, réplica de leitura, pool isolado — tudo síncrono, no mesmo processo, no mesmo banco.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A travessia de um Pix pelos seis módulos — os números são a ordem do fluxo. Fronteiras lógicas de verdade; recursos físicos compartilhados. Essa tensão é a aula inteira.</p>
</div>

Sigam os números comigo, porque cada passo é uma decisão de design que a gente já tomou (ou vai tomar):

1. O app da Ana chama o **Gateway/BFF**: terminação TLS, rate limit e a idempotência por E2E ID da Aula 1 — tudo **antes** de qualquer lógica de negócio.
2. O Gateway entrega ao módulo de **Pagamentos**, a única porta de entrada do domínio. Ninguém de fora fala com Ledger ou Contas diretamente.
3. Pagamentos pergunta a **Identidade/KYC**: esse cliente está ativo? Está dentro dos limites regulatórios de PLD? Chamada síncrona, interna, via interface — nunca via tabela.
4. Pagamentos pergunta ao **Antifraude**: qual o score dessa transação? Orçamento de ~100 ms, síncrono, porque a resposta bloqueia o fluxo.
5. Pagamentos cruza a fronteira e consulta o **DICT**, lá fora: quem é o dono dessa chave Pix? Síncrono, p99 de 1 segundo — e reparem: é a primeira vez que o TechPix fica **esperando alguém que não controla**.
6. Com tudo aprovado, Pagamentos manda o **Ledger** reservar: débito na carteira da Ana, crédito em `pix_a_liquidar`, na mesma transação ACID.
7. Pagamentos envia a `pacs.008` ao **SPI**, com o mesmo E2E ID; a `pacs.002` volta confirmando a liquidação final, e o Ledger registra.
8. Por fim, Pagamentos pede a **Contas** para atualizar o extrato e disparar a notificação — hoje, no mesmo processo, competindo pelos mesmos pools da escrita. Esse "por fim" inocente é uma das sementes do incidente de hoje.

E agora que vocês viram o fluxo, deixa eu preencher a planta do prédio — porque "seis módulos" só vira arquitetura quando cada um tem responsabilidade, dados e interface declarados:

| Módulo | Responsabilidade | Dados que possui (schema) | Quem o chama | Comunicação |
|---|---|---|---|---|
| **Identidade e KYC/PLD** | quem é o cliente, se pode operar, limites regulatórios | clientes, documentos, limites | Gateway (sessão), Pagamentos (passo 3) | síncrona, interna |
| **Contas** | ciclo de vida da conta; extrato e saldo exibido | contas, extrato materializado | app (consultas), Pagamentos (passo 8) | síncrona, interna |
| **Ledger** | fatos financeiros; invariante Σ débitos = Σ créditos | lançamentos, contas contábeis | Pagamentos — única porta de escrita | síncrona, ACID |
| **Pagamentos** | orquestra o fluxo: identidade → antifraude → DICT → ledger → SPI | ordens de pagamento, estado da orquestração | Gateway (passo 2) | síncrona; é quem fala com o mundo externo |
| **Antifraude** | decisão por transação: aprova, nega, segura para análise | regras, histórico de decisões | Pagamentos (passo 4) | síncrona, ~100 ms de orçamento |
| **Cartões** | *(roadmap)* emissão e adquirência, via PSP externo | — nada ainda | ninguém | — |

Uma palavra honesta sobre essa última linha, porque ela vai aparecer em todo desenho do curso: **Cartões existe como fronteira reservada, não como funcionalidade.** O mundo de cartões — PSPs como Stripe e Adyen, as bandeiras, o settlement em D+n — é um trilho inteiro próprio, com diagramas clássicos próprios, e está fora do escopo deste curso, que segue o trilho do Pix. Mas a fronteira fica desenhada desde o dia 1 de propósito: quando (se) o TechPix entrar nesse mundo, o lugar dele no monólito já tem nome e regra de ouro esperando.

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

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 860 340" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <!-- zonas -->
  <rect x="70" y="30" width="511" height="250" fill="#f0fdf4"/>
  <rect x="581" y="30" width="73" height="250" fill="#fef9e7"/>
  <rect x="654" y="30" width="146" height="250" fill="#fef2f2"/>
  <!-- eixos -->
  <line x1="70" y1="280" x2="800" y2="280" stroke="#666" stroke-width="1.5"/>
  <line x1="70" y1="280" x2="70" y2="30" stroke="#666" stroke-width="1.5"/>
  <text x="435" y="315" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">utilização ρ</text>
  <text x="30" y="150" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333" transform="rotate(-90 30 150)">fator de espera ρ/(1−ρ)</text>
  <!-- marcas do eixo x -->
  <g font-family="sans-serif" font-size="11" fill="#666" text-anchor="middle">
    <text x="70" y="296">0%</text>
    <text x="435" y="296">50%</text>
    <text x="581" y="296">70%</text>
    <text x="654" y="296">80%</text>
    <text x="727" y="296">90%</text>
    <text x="764" y="296">95%</text>
  </g>
  <!-- curva -->
  <polyline points="70,280 143,278.7 216,277 289,274.9 362,272 435,268 508,262 581,252 617,244 654,232 690,212 712,192 727,172 742,142 756,92 764,52" fill="none" stroke="#4338ca" stroke-width="3" stroke-linecap="round"/>
  <!-- linha dos 70% -->
  <line x1="581" y1="280" x2="581" y2="40" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="6 4"/>
  <text x="581" y="52" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7a5c00">regra dos 70%</text>
  <!-- pontos -->
  <g font-family="sans-serif" font-size="11" fill="#333">
    <circle cx="435" cy="268" r="4" fill="#4338ca"/><text x="435" y="256">1,0</text>
    <circle cx="581" cy="252" r="4" fill="#4338ca"/><text x="565" y="240">2,3</text>
    <circle cx="654" cy="232" r="4" fill="#4338ca"/><text x="640" y="222">4,0</text>
    <circle cx="727" cy="172" r="4" fill="#4338ca"/><text x="710" y="166">9,0</text>
    <circle cx="764" cy="52" r="4" fill="#b91c1c"/><text x="745" y="48" fill="#b91c1c" font-weight="bold">19,0</text>
  </g>
  <text x="700" y="130" font-family="sans-serif" font-size="12" font-style="italic" fill="#b91c1c">o cotovelo</text>
  <!-- anotação do dia 5 -->
  <rect x="90" y="45" width="330" height="44" rx="8" fill="#fff" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="255" y="63" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">Dia 5: tráfego 3× → ρ de 30% para 90%</text>
  <text x="255" y="80" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">a espera piora 9×, não 3×</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A curva de filas M/M/1: quase plana até 70%, vertical depois de 80%. A intuição linear falha exatamente onde dói.</p>
</div>

### 3.2 O efeito composto com a Lei de Little

Agora juntem isso com a Lei de Little da Aula 1, porque o combo é o que explica o colapso completo. Lembram: `L = λ × W`. A concorrência necessária é a taxa de chegada vezes o tempo no sistema.

Sigam o encadeamento comigo, porque ele é vicioso:

1. O tráfego triplica, então a utilização do lock do ledger sai de ~30% e vai para ~90%.
2. Pela curva de filas, o tempo de espera não triplica — ele salta de um fator 0,4 para um fator 9. O `W` da Lei de Little explode.
3. Pela Lei de Little, se o `W` explode e o `λ` também subiu, o `L` — a concorrência necessária — explode ao quadrado, digamos assim. Foi o cálculo que a gente fez na Aula 1: de 45 conexões para 450.
4. O pool tem 100. Ele esgota.
5. E agora vem a parte que fecha o círculo perverso: **quando o pool esgota, as requisições começam a dar timeout. Timeout faz o cliente tentar de novo. Retry aumenta o λ.** Volta para o passo 1, pior.

Esse último passo tem nome — **retry storm**, ou tempestade de retentativas — e é o mecanismo pelo qual um sistema que estava só lento vira um sistema completamente fora do ar. O tráfego que ele está recebendo agora não é mais a demanda real dos usuários; é a demanda real **mais** todas as retentativas que ele próprio causou. O sistema está se atacando.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 860 360" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2r-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- ciclo em losango -->
  <rect x="310" y="20" width="240" height="52" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="430" y="42" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">1. λ sobe: demanda real</text>
  <text x="430" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">(+ retries, nas voltas seguintes)</text>

  <rect x="600" y="120" width="240" height="52" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="720" y="142" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7a5c00">2. ρ passa do cotovelo (~90%)</text>
  <text x="720" y="160" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7a5c00">W explode: fator 0,4 → 9</text>

  <rect x="310" y="230" width="240" height="52" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="430" y="252" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7f1d1d">3. L = λ×W: 45 → 450 conexões</text>
  <text x="430" y="270" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7f1d1d">pool de 100 esgota</text>

  <rect x="20" y="120" width="240" height="52" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="140" y="142" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7f1d1d">4. timeout → cliente tenta</text>
  <text x="140" y="160" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7f1d1d">de novo (retry) → λ sobe</text>

  <!-- setas do ciclo (horário) -->
  <path d="M 552 62 Q 690 75 718 118" fill="none" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#a2r-arrow)"/>
  <path d="M 715 174 Q 660 245 553 256" fill="none" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#a2r-arrow)"/>
  <path d="M 308 256 Q 175 245 142 174" fill="none" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#a2r-arrow)"/>
  <path d="M 145 118 Q 190 70 308 48" fill="none" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#a2r-arrow)"/>

  <text x="430" y="150" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#b91c1c">RETRY STORM</text>
  <text x="430" y="170" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">o sistema se ataca</text>

  <!-- defesas -->
  <rect x="60" y="310" width="220" height="34" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="170" y="332" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">backoff exponencial + jitter</text>
  <rect x="320" y="310" width="220" height="34" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="430" y="332" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">retry budget (~10% do tráfego)</text>
  <rect x="580" y="310" width="220" height="34" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="690" y="332" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">load shedding (recusar p/ proteger)</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O círculo vicioso do retry storm — e as três defesas que quebram o ciclo (Seção 3.3).</p>
</div>

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

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 360" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2f-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
    <marker id="a2f-arrow2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <!-- Fratura 1: ponto quente -->
  <text x="215" y="26" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">Fratura 1 — ponto quente do ledger</text>
  <g font-family="sans-serif" font-size="11" fill="#333">
    <text x="45" y="66">Pix 1</text>
    <text x="45" y="96">Pix 2</text>
    <text x="45" y="126">Pix 3</text>
    <text x="45" y="156">Pix 4</text>
  </g>
  <line x1="75" y1="62" x2="180" y2="100" stroke="#b91c1c" stroke-width="2" marker-end="url(#a2f-arrow)"/>
  <line x1="75" y1="92" x2="180" y2="106" stroke="#b91c1c" stroke-width="2" marker-end="url(#a2f-arrow)"/>
  <line x1="75" y1="122" x2="180" y2="112" stroke="#b91c1c" stroke-width="2" marker-end="url(#a2f-arrow)"/>
  <line x1="75" y1="152" x2="180" y2="118" stroke="#b91c1c" stroke-width="2" marker-end="url(#a2f-arrow)"/>
  <!-- fila -->
  <g fill="#d4a017">
    <circle cx="200" cy="108" r="5"/>
    <circle cx="216" cy="108" r="5"/>
    <circle cx="232" cy="108" r="5"/>
  </g>
  <text x="216" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">fila do lock</text>
  <rect x="250" y="82" width="160" height="52" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2.5"/>
  <text x="330" y="104" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">pix_a_liquidar</text>
  <text x="330" y="122" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">lock único — uma por vez</text>
  <rect x="250" y="160" width="160" height="40" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="330" y="178" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">outras contas</text>
  <text x="330" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">tranquilas, sem fila</text>
  <text x="215" y="235" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">a decisão (forte) está certa;</text>
  <text x="215" y="250" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">a implementação concentrou contenção</text>

  <!-- divisor -->
  <line x1="445" y1="20" x2="445" y2="340" stroke="#ddd" stroke-width="1.5"/>

  <!-- Fratura 2: DICT síncrono -->
  <text x="665" y="26" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">Fratura 2 — DICT síncrono esgota o pool</text>
  <rect x="480" y="45" width="230" height="110" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="595" y="64" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">pool de threads (100)</text>
  <g>
    <rect x="495" y="75" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="530" y="75" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="565" y="75" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="600" y="75" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="635" y="75" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="670" y="75" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="495" y="100" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="530" y="100" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="565" y="100" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="600" y="100" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="635" y="100" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
    <rect x="670" y="100" width="30" height="20" rx="3" fill="#fecaca" stroke="#b91c1c"/>
  </g>
  <text x="595" y="140" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">todas presas esperando o DICT</text>
  <rect x="740" y="70" width="120" height="60" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="800" y="96" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">DICT</text>
  <text x="800" y="114" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">externo · lento hoje</text>
  <line x1="710" y1="100" x2="738" y2="100" stroke="#888" stroke-width="2" marker-end="url(#a2f-arrow2)"/>
  <rect x="480" y="175" width="230" height="40" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="595" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">consulta de saldo, extrato, tudo:</text>
  <text x="595" y="207" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">bloqueado sem ter culpa (falha em cascata)</text>
  <!-- defesas -->
  <rect x="480" y="235" width="118" height="32" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="539" y="255" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">bulkhead</text>
  <rect x="608" y="235" width="130" height="32" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="673" y="255" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">circuit breaker</text>
  <rect x="748" y="235" width="112" height="32" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="804" y="255" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">timeout ~1s</text>
  <text x="665" y="295" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">pools isolados por dependência; falhar rápido;</text>
  <text x="665" y="310" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">não esperar 10s por quem responde em 1s</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Os dois pontos de fratura do dia 5 — contenção interna no ledger e dependência externa sequestrando o pool.</p>
</div>

---

## 5. Desacoplamento incremental: cortando sem parar de operar

Agora que a gente sabe onde dói, vamos falar de como tratar — sem, no processo, criar um novo incidente pior que o primeiro. E antes da técnica, deixa eu encenar a reunião que aconteceu no TechPix na manhã seguinte ao dia 5, porque essa reunião acontece em **toda** empresa depois de um susto desses, e vocês vão estar nela um dia.

O primeiro a falar é um dev da equipe, ainda com a adrenalina do plantão: *"A causa é óbvia: a gente é um monólito. A Netflix quebrou tudo em microsserviços e escala infinito. Vamos reescrever."* E eu quero que vocês notem que esse argumento é sedutor e **não sobrevive ao diagnóstico que a gente acabou de fazer**. Voltem nas duas fraturas da Seção 4. O ponto quente era o lock da conta `pix_a_liquidar` — se vocês colocarem o Ledger num serviço separado, aquele lock **continua existindo**, só que agora cada transação paga uma viagem de rede para chegar até ele. Vocês não removeram a contenção; mudaram o endereço dela e adicionaram latência e falha parcial no caminho. E o esgotamento de pool era uma dependência externa lenta sequestrando recurso compartilhado — que se resolve com bulkhead e circuit breaker, dentro ou fora de um monólito, indiferente. **Nenhuma das duas fraturas tem "deploy único" como causa raiz.** Microsserviços trocam o problema da contenção pelo problema da distribuição; quem extrai sem critério paga os dois ao mesmo tempo.

Aí alguém mais calmo, do outro lado da mesa, faz a pergunta certa: *"Ok, reescrever tudo não. Mas alguma coisa a gente extrai, não? O quê? E como a gente saberia?"* — e essa pergunta eu quero deixar **aberta**, deliberadamente, porque ela é a pergunta mais importante das próximas aulas. Para respondê-la, vocês precisam de duas coisas que ainda não temos: fronteiras descobertas com técnica em vez de palpite (é a Aula 3), e critérios de evidência — não de vontade — para decidir que uma fronteira está madura para virar serviço (isso vem mais adiante no curso, com nome e checklist). O que dá para fazer **hoje**, com o incidente ainda quente, é o caminho do meio: o **desacoplamento incremental** — aliviar os pontos de fratura específicos, sem big bang, sem reescrita, sem apostar a empresa numa migração.

### 5.1 Strangler Fig

A primeira estratégia tem um nome bonito e uma imagem melhor ainda: **Strangler Fig**, a figueira estranguladora — uma planta que cresce em volta de uma árvore hospedeira, aos poucos, até que a árvore original desaparece e só resta a nova estrutura. Martin Fowler emprestou essa imagem para descrever como migrar um sistema sem um corte único e arriscado: vocês colocam uma fachada, um roteador, na frente do monólito, e começam a desviar uma fatia do tráfego — digamos, uma rota específica, ou um conjunto específico de clientes — para uma nova implementação, enquanto o resto continua batendo no monólito antigo. Aos poucos, mais tráfego migra, até que o monólito, naquele pedaço específico, para de receber chamada nenhuma — e pode ser desligado sem drama.

No TechPix, a estratégia seria: colocar uma fachada na frente do módulo de Pagamentos, e migrar gradualmente a lógica de resolução de chave — que hoje mora dentro do monólito e sofre com o esgotamento de pool que eu descrevi — para um componente isolado, com seu próprio pool de conexões, suas próprias réplicas, dedicado só a essa responsabilidade. Se esse componente ficar sobrecarregado, ele fica sobrecarregado sozinho — não arrasta o resto do sistema junto.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 860 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2s-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a2s-arrow-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
    <marker id="a2s-arrow-c" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#999"/>
    </marker>
  </defs>
  <rect x="30" y="100" width="130" height="50" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="95" y="130" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">Clientes</text>
  <line x1="160" y1="125" x2="280" y2="125" stroke="#4338ca" stroke-width="2.5" marker-end="url(#a2s-arrow)"/>
  <text x="220" y="113" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">100%</text>
  <rect x="282" y="95" width="170" height="60" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
  <text x="367" y="120" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Fachada / roteador</text>
  <text x="367" y="140" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">decide rota por chamada</text>
  <!-- rota antiga -->
  <line x1="452" y1="110" x2="590" y2="60" stroke="#999" stroke-width="2.5" stroke-dasharray="6 4" marker-end="url(#a2s-arrow-c)"/>
  <text x="520" y="70" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#999">80% → 50% → 0%</text>
  <rect x="592" y="30" width="240" height="60" rx="10" fill="#f5f5f4" stroke="#999" stroke-width="2"/>
  <text x="712" y="55" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">Monólito — resolução de chave</text>
  <text x="712" y="74" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#999">(rota antiga, morrendo aos poucos)</text>
  <!-- rota nova -->
  <line x1="452" y1="140" x2="590" y2="195" stroke="#166534" stroke-width="3" marker-end="url(#a2s-arrow-g)"/>
  <text x="516" y="185" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">20% → 50% → 100%</text>
  <rect x="592" y="170" width="240" height="70" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="712" y="192" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Componente novo</text>
  <text x="712" y="210" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">resolução de chave isolada</text>
  <text x="712" y="227" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">pool próprio · réplicas próprias</text>
  <text x="430" y="278" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">no fim, a rota antiga não recebe chamada nenhuma — e é desligada sem drama</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Strangler Fig: a fachada desvia o tráfego aos poucos, até a árvore original desaparecer.</p>
</div>

### 5.2 Branch by Abstraction

Às vezes, um corte limpo por fachada não é possível — a lógica está espalhada demais, ou o corte teria que ser feito de uma vez. Para esses casos existe uma segunda tática: **Branch by Abstraction**. A ideia é introduzir, primeiro, uma camada de abstração **dentro do próprio monólito**, por trás da qual a implementação antiga continua existindo. Só depois, com a abstração já no lugar e todo o resto do sistema já falando com ela — e não diretamente com a implementação concreta —, vocês trocam o que está atrás da abstração, seja por uma nova implementação interna, seja por uma chamada para um serviço externo. O ponto central é: **a abstração desacopla o "quem chama" do "quem implementa"**, e essa troca de implementação vira um detalhe interno, sem precisar de uma reescrita coordenada em todos os pontos de chamada de uma vez.

### 5.3 O problema da escrita dupla, e o Outbox Pattern

Agora, o ponto mais sutil e, para mim, o mais bonito dessa aula: o que acontece quando o TechPix precisa, na mesma operação, gravar um lançamento no ledger **e** avisar o resto do sistema que aquilo aconteceu — para atualizar o extrato, disparar uma notificação, alimentar o feed? Se vocês gravam no banco e, logo em seguida, publicam um evento numa fila de mensagens como duas operações separadas, existe uma janela de falha real: e se o sistema gravar no banco e cair exatamente antes de publicar o evento? O lançamento existe, mas ninguém nunca soube. Isso se chama **problema da escrita dupla**, o *dual write problem*, e é um dos jeitos mais silenciosos de um sistema ficar inconsistente sem ninguém perceber por semanas.

A solução elegante chama-se **Outbox Pattern**. Em vez de escrever no banco e publicar na fila como duas operações, vocês escrevem **duas coisas na mesma transação, no mesmo banco**: o lançamento do ledger, e um registro numa tabela de "outbox" — uma caixa de saída — descrevendo o evento que precisa ser publicado. Como as duas escritas acontecem dentro da mesma transação ACID, ou as duas acontecem, ou nenhuma acontece — nunca existe o estado intermediário perigoso. Depois, um processo separado — um relay — lê a tabela de outbox e publica os eventos, de forma assíncrona, para quem precisar consumir: o serviço de extrato, o de notificações, o de feed.

E aqui eu quero que vocês enxerguem uma coisa linda: a tabela de outbox é, estruturalmente, **a mesma ideia do ledger** que a gente construiu na Aula 1 — um log append-only, que registra fatos, um por um, sem nunca sobrescrever. Vocês não estão aprendendo um padrão novo do zero; estão reaplicando o mesmo princípio — log imutável como fonte da verdade — numa nova camada do sistema.

### 5.4 CQRS, agora de verdade

Isso fecha o círculo que eu abri na Aula 1, quando falei que write model e read model são coisas diferentes. Agora, com o Outbox publicando eventos de forma confiável, dá para materializar isso de verdade: o **caminho de escrita** continua sendo o ledger, forte, síncrono, protegido pelo ADR-001. O **caminho de leitura** — extrato, saldo exibido, feed — passa a ser alimentado, de forma assíncrona, pelos eventos que saem do Outbox, numa base de dados otimizada só para consulta, que pode escalar de forma completamente independente da escrita. Essa separação, que vocês já intuíam desde a Aula 1, agora tem um mecanismo concreto de sustentação: o Outbox é a ponte confiável entre os dois mundos.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2o-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a2o-arrow-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <text x="70" y="120" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">escrita</text>
  <text x="70" y="136" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">do Pix</text>
  <line x1="105" y1="128" x2="160" y2="128" stroke="#4338ca" stroke-width="2.5" marker-end="url(#a2o-arrow)"/>
  <!-- transação ACID -->
  <rect x="165" y="40" width="240" height="180" rx="12" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5" stroke-dasharray="8 5"/>
  <text x="285" y="65" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">MESMA transação ACID</text>
  <rect x="185" y="80" width="200" height="52" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="285" y="102" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">ledger: lançamentos</text>
  <text x="285" y="120" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">débito / crédito (Σ = Σ)</text>
  <rect x="185" y="146" width="200" height="52" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="285" y="168" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">outbox: evento</text>
  <text x="285" y="186" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">"PixLiquidado" (append-only)</text>
  <text x="285" y="242" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">ou as duas escritas acontecem, ou nenhuma</text>
  <text x="285" y="258" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">(sem dual write problem)</text>
  <!-- relay -->
  <line x1="405" y1="172" x2="470" y2="172" stroke="#166534" stroke-width="2.5" marker-end="url(#a2o-arrow-g)"/>
  <rect x="472" y="146" width="110" height="52" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="527" y="168" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Relay</text>
  <text x="527" y="186" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">poller ou CDC</text>
  <line x1="582" y1="172" x2="648" y2="172" stroke="#166534" stroke-width="2.5" marker-end="url(#a2o-arrow-g)"/>
  <text x="615" y="160" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">assíncrono</text>
  <!-- read models -->
  <rect x="650" y="48" width="230" height="40" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="765" y="73" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">Extrato (read model)</text>
  <rect x="650" y="100" width="230" height="40" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="765" y="125" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">Saldo exibido (read model)</text>
  <rect x="650" y="152" width="230" height="40" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="765" y="177" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">Feed / notificações</text>
  <rect x="650" y="204" width="230" height="56" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="765" y="226" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Reconciliação (Seção 5.5)</text>
  <text x="765" y="244" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4d7c5f">ledger × Conta PI, por E2E ID</text>
  <line x1="648" y1="172" x2="650" y2="68" stroke="#166534" stroke-width="1.5" stroke-dasharray="4 3"/>
  <line x1="648" y1="172" x2="650" y2="232" stroke="#166534" stroke-width="1.5" stroke-dasharray="4 3"/>
  <!-- rodapé -->
  <rect x="165" y="290" width="715" height="30" rx="6" fill="#fef9e7" stroke="#d4a017"/>
  <text x="522" y="310" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7a5c00">escrita: forte e síncrona (ADR-001) · leitura: eventual, 100–300 ms atrás, escalando sozinha (ADR-002)</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Outbox + CQRS: o log imutável da Aula 1, reaplicado como ponte confiável entre escrita e leitura — com quatro consumidores, não três.</p>
</div>

### 5.5 O quarto consumidor: a reconciliação

Reparem que eu desenhei **quatro** consumidores saindo do relay, e o quarto não é um read model como os outros — ele é uma promessa da Aula 1 sendo paga. Lembram do que eu disse lá, quase de passagem, na seção do SPI? *"O ledger interno de vocês precisa espelhar e reconciliar com o que acontece na Conta PI — e reconciliação é uma disciplina de engenharia por si só."* Pois bem: até hoje, isso era uma frase. Agora vira um componente.

O mecanismo: o serviço de **Reconciliação** consome duas fontes independentes. De um lado, os eventos `PixLiquidado` que saem do Outbox — o que o **nosso** livro diz que aconteceu. Do outro, o extrato da Conta PI que o próprio SPI fornece — o que o livro do **Banco Central** diz que aconteceu. E ele bate as duas listas, movimento a movimento, usando a chave que costura o curso inteiro: o **E2E ID**. É por isso que aquele identificador viaja em tudo — no registro de idempotência, na `pacs.008`, no evento do Outbox: ele é o que permite dizer "este lançamento aqui é aquele movimento lá".

Cada comparação tem três resultados possíveis, e a gravidade cresce na ordem:

- **Bateu.** O caso normal, 99,9-e-alguma-coisa por cento das vezes. Ninguém escreve post-mortem sobre ele.
- **Está no nosso ledger, não está no extrato do BACEN.** Dentro da janela de propagação, é trânsito normal — o evento pode estar a caminho. Persistiu além da janela? Alguma coisa que a gente **acha** que liquidou, não liquidou. Investigação.
- **Está no extrato do BACEN, não está no nosso ledger.** Este é o grave. Dinheiro se moveu em moeda de banco central e o nosso livro não sabe. Não existe "janela de tolerância" confortável aqui — é alarme, e é gente olhando **agora**.

E duas regras de conduta, que valem mais que a implementação. Primeira: **divergência abre investigação, nunca correção automática.** Um robô que "conserta" o ledger para bater com o extrato é um robô que transforma um bug detectável num rombo silencioso. Segunda: quando a investigação concluir, a correção entra como **lançamento novo, vinculado ao original** — nunca como edição do passado. É a regra de imutabilidade da Aula 1, de novo, agora protegendo vocês do próprio processo de correção.

Se vocês já viram o diagrama clássico de payment system — aquele com PSP, settlement file e uma caixa de *Reconciliation* recebendo o arquivo de fora — reconheçam a estrutura: é exatamente esta. Muda o nome do trilho (lá, adquirência e bandeiras; aqui, SPI e Conta PI), não muda o papel: **a reconciliação é o sistema que salva vocês quando todos os outros falharem em silêncio.** Como esse componente se opera no dia a dia — o que monitorar, quando alarmar, o que é taxa de divergência aceitável — é assunto da Aula 7.

E antes de eu fazer a conta do particionamento, deixa eu nomear uma distinção que está implícita em tudo isso — porque ela explica **por que** o caminho de leitura sai barato e o de escrita sai caro. Existem dois eixos para escalar qualquer sistema: **vertical** (scale-up: máquina maior) e **horizontal** (scale-out: mais máquinas). E a consequência que o ADR-001 já registrava — "a escrita não escala na horizontal como a leitura" — é exatamente isso em uma linha: para a leitura, o eixo horizontal é quase de graça (réplicas); para a escrita fortemente consistente, o eixo horizontal cobra o preço da coordenação, e é essa conta que a Seção 6 vai fazer.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 350" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2t-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <!-- Vertical -->
  <text x="220" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Escala VERTICAL (scale-up)</text>
  <rect x="150" y="120" width="70" height="60" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="185" y="155" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">Postgres</text>
  <line x1="228" y1="150" x2="268" y2="150" stroke="#4338ca" stroke-width="2" marker-end="url(#a2t-arrow)"/>
  <rect x="275" y="90" width="110" height="120" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
  <text x="330" y="130" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Postgres</text>
  <text x="330" y="150" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">+ CPU · + RAM</text>
  <text x="330" y="166" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">+ NVMe</text>
  <g font-family="sans-serif" font-size="11">
    <text x="70" y="245" fill="#166534">✓ simples: nenhuma mudança de código</text>
    <text x="70" y="265" fill="#166534">✓ preserva a transação ACID local</text>
    <text x="70" y="290" fill="#b91c1c">✗ teto físico — a maior máquina acaba</text>
    <text x="70" y="310" fill="#b91c1c">✗ custo cresce não-linear</text>
    <text x="70" y="330" fill="#b91c1c">✗ continua um único ponto de falha</text>
  </g>
  <line x1="440" y1="40" x2="440" y2="335" stroke="#ccc" stroke-width="1.5" stroke-dasharray="6 4"/>
  <!-- Horizontal -->
  <text x="660" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1a1a1a">Escala HORIZONTAL (scale-out)</text>
  <text x="560" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Leitura: réplicas</text>
  <rect x="480" y="72" width="70" height="44" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="515" y="98" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">réplica 1</text>
  <rect x="558" y="72" width="70" height="44" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="593" y="98" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">réplica 2</text>
  <rect x="636" y="72" width="70" height="44" rx="7" fill="#f0fdf4" stroke="#166534" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="671" y="98" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">réplica N…</text>
  <text x="597" y="136" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">quase de graça: adicionar nó = mais capacidade de leitura</text>
  <text x="590" y="172" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Escrita: particionar</text>
  <rect x="480" y="184" width="70" height="44" rx="7" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="515" y="210" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#7a5c00">partição 1</text>
  <rect x="558" y="184" width="70" height="44" rx="7" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="593" y="210" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#7a5c00">partição 2</text>
  <rect x="636" y="184" width="70" height="44" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="671" y="204" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#7f1d1d">partição 3</text>
  <text x="671" y="218" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#b91c1c">(a quente)</text>
  <g font-family="sans-serif" font-size="11">
    <text x="470" y="260" fill="#166534">✓ sem teto: cresce nó a nó</text>
    <text x="470" y="280" fill="#b91c1c">✗ invariante Σ=Σ atravessa partições → coordenação</text>
    <text x="470" y="300" fill="#b91c1c">✗ transação cross-partição: 2PC ou saga (Aula 1, §2.6)</text>
    <text x="470" y="320" fill="#b91c1c">✗ chave quente limita o ganho (Lei de Amdahl, Seção 6)</text>
  </g>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Os dois eixos de escala: a leitura escala na horizontal quase de graça (réplicas); a escrita fortemente consistente paga coordenação — a consequência registrada no ADR-001.</p>
</div>

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

E agora que os nomes estão na mesa, deixa eu juntar as peças num desenho só — o CQRS da Seção 5.4, mas com a stack de verdade, caixa por caixa, do jeito que ele roda em produção. Reparem que cada caixa desse desenho é um dos padrões do catálogo do microservices.io, do Chris Richardson — Transactional Outbox e CQRS têm página própria lá, e vale a visita:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 920 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2u-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a2u-arrow-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <!-- Write model -->
  <rect x="20" y="40" width="240" height="180" rx="12" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
  <text x="140" y="66" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">PostgreSQL — write model</text>
  <text x="140" y="84" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">serializable (SSI) · ADR-001</text>
  <rect x="40" y="98" width="200" height="42" rx="7" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="140" y="116" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">ledger (Σ = Σ)</text>
  <text x="140" y="132" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">particionado por tempo + hash</text>
  <rect x="40" y="150" width="200" height="42" rx="7" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="140" y="168" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">tabela outbox</text>
  <text x="140" y="184" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">mesma transação ACID</text>
  <text x="140" y="212" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">Transactional Outbox (microservices.io)</text>

  <!-- Relay -->
  <line x1="260" y1="130" x2="320" y2="130" stroke="#166534" stroke-width="2.5" marker-end="url(#a2u-arrow-g)"/>
  <rect x="322" y="95" width="140" height="70" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="392" y="118" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Relay</text>
  <text x="392" y="136" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">dia 1: poller</text>
  <text x="392" y="152" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">maduro: Debezium (CDC/WAL)</text>

  <!-- Kafka -->
  <line x1="462" y1="130" x2="522" y2="130" stroke="#166534" stroke-width="2.5" marker-end="url(#a2u-arrow-g)"/>
  <rect x="524" y="85" width="150" height="90" rx="9" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="599" y="110" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">Kafka</text>
  <text x="599" y="128" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">tópico "PixLiquidado"</text>
  <text x="599" y="144" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">+ retenção, reprocesso</text>
  <text x="599" y="160" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">− mais uma peça p/ operar</text>

  <!-- Read models -->
  <line x1="674" y1="112" x2="730" y2="80" stroke="#166534" stroke-width="2" marker-end="url(#a2u-arrow-g)"/>
  <line x1="674" y1="148" x2="730" y2="185" stroke="#166534" stroke-width="2" marker-end="url(#a2u-arrow-g)"/>
  <rect x="732" y="45" width="170" height="70" rx="9" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="817" y="68" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">Redis</text>
  <text x="817" y="86" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#991b1b">saldo exibido (chave-valor)</text>
  <text x="817" y="102" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">+ leitura em µs · reconstruível</text>
  <rect x="732" y="150" width="170" height="70" rx="9" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="817" y="173" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Réplica Postgres</text>
  <text x="817" y="191" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">extrato (SQL, paginação)</text>
  <text x="817" y="207" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">+ consulta rica · − lag de réplica</text>

  <!-- Latency + reads -->
  <text x="597" y="205" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">atraso eventual ponta a ponta: 100–300 ms</text>
  <line x1="817" y1="245" x2="817" y2="228" stroke="#888" stroke-width="2" marker-end="url(#a2u-arrow)"/>
  <text x="817" y="262" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">app da Ana lê saldo e extrato AQUI — nunca do ledger</text>

  <!-- Footer -->
  <rect x="20" y="290" width="882" height="88" rx="8" fill="#fff" stroke="#ccc"/>
  <g font-family="sans-serif" font-size="11">
    <text x="35" y="313" fill="#166534">+ escrita e leitura escalam separadas (a leitura, com réplica e Redis, cresce sem tocar no lock do ledger)</text>
    <text x="35" y="333" fill="#166534">+ nenhum evento se perde: fato e evento nascem na mesma transação (sem dual write)</text>
    <text x="35" y="353" fill="#b91c1c">− três peças novas para operar e monitorar (relay, Kafka, read stores) · − o extrato atrasa 100–300 ms, e isso precisa estar combinado com o produto</text>
    <text x="35" y="371" fill="#666">Padrões: Transactional Outbox + CQRS — catálogo microservices.io (Chris Richardson)</text>
  </g>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O CQRS da Seção 5.4 com a stack nomeada: Postgres → outbox → relay (poller→Debezium) → Kafka → Redis + réplica. O desenho conceitual e este são o mesmo sistema — um para entender, outro para operar.</p>
</div>

E o Redis ali no canto merece uma pausa, porque "botar um cache" é a frase mais enganosamente simples da engenharia. Existem três estratégias clássicas de manter um cache — e duas formas de ele parar de mentir. O TechPix usa duas combinações diferentes, para dois problemas diferentes:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 920 430" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2u-c-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <!-- Panel 1: cache-aside -->
  <rect x="15" y="20" width="285" height="215" rx="10" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="157" y="45" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Cache-aside (lazy)</text>
  <rect x="35" y="60" width="80" height="36" rx="7" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="75" y="82" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">app</text>
  <rect x="185" y="60" width="90" height="36" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="230" y="82" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">Redis</text>
  <line x1="115" y1="70" x2="183" y2="70" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a2u-c-arrow)"/>
  <text x="149" y="62" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">1. consulta</text>
  <rect x="185" y="130" width="90" height="36" rx="7" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
  <text x="230" y="152" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#78716c">banco</text>
  <line x1="115" y1="88" x2="183" y2="145" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a2u-c-arrow)"/>
  <text x="120" y="130" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">2. miss? busca</text>
  <line x1="230" y1="128" x2="230" y2="100" stroke="#4338ca" stroke-width="1.5" stroke-dasharray="3 3" marker-end="url(#a2u-c-arrow)"/>
  <text x="262" y="118" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">3. grava</text>
  <g font-family="sans-serif" font-size="10">
    <text x="30" y="192" fill="#166534">+ só cacheia o que é lido; app no controle</text>
    <text x="30" y="209" fill="#b91c1c">− 1º acesso lento (miss) · lógica na app</text>
    <text x="30" y="226" fill="#7a5c00">TechPix: cache do DICT (Aula 1)</text>
  </g>
  <!-- Panel 2: read-through -->
  <rect x="315" y="20" width="285" height="215" rx="10" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="457" y="45" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Read-through</text>
  <rect x="335" y="60" width="80" height="36" rx="7" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="375" y="82" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">app</text>
  <rect x="475" y="60" width="100" height="36" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="525" y="82" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">cache</text>
  <rect x="475" y="130" width="100" height="36" rx="7" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
  <text x="525" y="152" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#78716c">banco</text>
  <line x1="415" y1="78" x2="473" y2="78" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a2u-c-arrow)"/>
  <line x1="525" y1="98" x2="525" y2="128" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a2u-c-arrow)"/>
  <text x="558" y="116" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">cache busca</text>
  <g font-family="sans-serif" font-size="10">
    <text x="330" y="192" fill="#166534">+ app não sabe que o cache existe</text>
    <text x="330" y="209" fill="#b91c1c">− exige infra/biblioteca que suporte</text>
    <text x="330" y="226" fill="#666">mesmos misses do cache-aside, sem o controle</text>
  </g>
  <!-- Panel 3: write-through -->
  <rect x="615" y="20" width="290" height="215" rx="10" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="760" y="45" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Write-through</text>
  <rect x="635" y="60" width="80" height="36" rx="7" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="675" y="82" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">app</text>
  <rect x="785" y="60" width="100" height="36" rx="7" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="835" y="82" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">cache</text>
  <rect x="785" y="130" width="100" height="36" rx="7" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
  <text x="835" y="152" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#78716c">banco</text>
  <line x1="715" y1="78" x2="783" y2="78" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a2u-c-arrow)"/>
  <text x="748" y="70" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">escrita</text>
  <line x1="835" y1="98" x2="835" y2="128" stroke="#4338ca" stroke-width="1.5" marker-end="url(#a2u-c-arrow)"/>
  <text x="875" y="116" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">sincroniza</text>
  <g font-family="sans-serif" font-size="10">
    <text x="630" y="192" fill="#166534">+ leitura sempre quente e coerente</text>
    <text x="630" y="209" fill="#b91c1c">− toda escrita paga o custo do cache</text>
    <text x="630" y="226" fill="#b91c1c">− cacheia até o que ninguém vai ler</text>
  </g>
  <!-- Invalidation band -->
  <rect x="15" y="255" width="890" height="120" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="460" y="280" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">E quando o cache mente? — as duas formas de invalidar</text>
  <g font-family="sans-serif" font-size="11">
    <text x="35" y="305" fill="#333"><tspan font-weight="bold">TTL (expiração):</tspan> o dado morre sozinho depois de N segundos. Simples; a mentira dura no máximo o TTL.</text>
    <text x="35" y="323" fill="#7a5c00">→ cache do DICT: TTL respeitando as regras de retenção do BACEN (Aula 1, Seção 5.4) — chave Pix muda raramente, staleness barata.</text>
    <text x="35" y="348" fill="#333"><tspan font-weight="bold">Por evento:</tspan> o consumidor do Kafka atualiza o Redis a cada "PixLiquidado" — o saldo exibido não expira, ele é projeção.</text>
    <text x="35" y="366" fill="#7a5c00">→ saldo exibido: staleness limitada aos 100–300 ms do relay — e reconstruível do ledger, como manda a Aula 1.</text>
  </g>
  <text x="460" y="400" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">O trade-off é sempre o mesmo triângulo: staleness aceitável × custo por leitura × complexidade de invalidação. Escolham por caso, não por moda.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Três estratégias de cache com Redis, duas formas de invalidar — e os dois casos reais do TechPix: DICT (cache-aside + TTL) e saldo exibido (projeção por evento).</p>
</div>

**Feature flags para o Strangler Fig.** O **Unleash** é a opção open source madura; o **LaunchDarkly** é a comercial mais conhecida. E vale dizer para a turma: começar com um sistema próprio de flags é tentador e quase sempre subestimado — o difícil não é o `if`, é a propagação de mudança de configuração em segundos para centenas de instâncias, com auditoria de quem mudou o quê. Isso importa muito na Aula 8, porque é o mecanismo do canary.

**Teste de carga.** O **k6** (script em JavaScript, roda em CI), o **Gatling** e o **JMeter** são as opções conhecidas. Aqui vai a dica que a maioria erra: um teste de carga que sobe o tráfego suavemente até o alvo **não** reproduz o dia 5. Vocês precisam de um teste de **degrau** — salta de 30% para 300% instantaneamente — porque é o degrau que expõe o comportamento do pool, do autoscaling lento e do retry storm. Teste suave mede capacidade; teste de degrau mede sobrevivência.

---

## 8. Registrando a decisão: ADR-002

Chegou a hora de formalizar. Vamos escrever, juntos, o segundo registro de decisão do TechPix — e reparem que ele **não contradiz** o ADR-001. Ele o complementa, resolvendo exatamente o ponto de fratura que a gente diagnosticou hoje, sem tocar na consistência forte do núcleo.

```
ADR-002 · Outbox + CQRS para o caminho de leitura          Status: Aceito (2026-08-06)

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

E antes de encerrar, o retrato de sempre — a gente vai tirar um desses ao fim de cada aula, para vocês verem a fintech crescendo tijolo a tijolo. Só que, desta vez, o retrato não é um inventário de caixas: é **a própria arquitetura** — a travessia da Seção 1, com tudo que a aula construiu por cima, em verde:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 960 660" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a2z-int" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a2z-ext" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#d4a017"/>
    </marker>
    <marker id="a2z-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <text x="480" y="24" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333">O TechPix ao fim da Aula 2</text>

  <!-- fronteira em L -->
  <line x1="760" y1="34" x2="760" y2="272" stroke="#666" stroke-width="1.5" stroke-dasharray="8 5"/>
  <line x1="760" y1="272" x2="950" y2="272" stroke="#666" stroke-width="1.5" stroke-dasharray="8 5"/>
  <text x="752" y="48" text-anchor="end" font-family="sans-serif" font-size="11" fill="#666">dentro (TechPix)</text>
  <text x="768" y="48" font-family="sans-serif" font-size="11" fill="#666">fora (BACEN)</text>
  <text x="945" y="290" text-anchor="end" font-family="sans-serif" font-size="9" fill="#666">↓ dentro de novo</text>

  <!-- cliente e gateway -->
  <rect x="10" y="118" width="88" height="66" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="54" y="140" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">App da Ana</text>
  <text x="54" y="156" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#166534">+ backoff exp.</text>
  <text x="54" y="169" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#166534">+ jitter no retry</text>
  <rect x="118" y="110" width="126" height="82" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="181" y="130" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#3730a3">Gateway / BFF</text>
  <text x="181" y="146" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#5a55a0">TLS · rate limit · E2E</text>
  <text x="181" y="162" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">+ load shedding</text>
  <text x="181" y="177" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">+ retry budget</text>

  <!-- monólito -->
  <rect x="264" y="40" width="356" height="380" rx="12" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="442" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Monólito TechPix — ainda um deploy</text>

  <rect x="278" y="76" width="100" height="52" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="328" y="98" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">Identidade/KYC</text>
  <text x="328" y="114" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#5a55a0">KYC · PLD</text>
  <rect x="388" y="76" width="100" height="52" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="438" y="98" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">Antifraude</text>
  <text x="438" y="114" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#5a55a0">~100 ms</text>
  <rect x="498" y="76" width="112" height="52" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="554" y="94" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">Ledger</text>
  <text x="554" y="108" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#166534">Σ=Σ · + outbox na</text>
  <text x="554" y="121" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#166534">mesma transação</text>

  <rect x="320" y="160" width="230" height="64" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
  <text x="435" y="182" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#3730a3">Pagamentos — orquestrador</text>
  <text x="435" y="200" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">+ pools por dependência (bulkhead)</text>
  <text x="435" y="214" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">+ timeouts por aresta</text>

  <rect x="278" y="250" width="145" height="48" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="350" y="270" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Contas</text>
  <text x="350" y="287" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#166534">consulta os read models →</text>
  <rect x="455" y="250" width="140" height="48" rx="8" fill="#f5f5f4" stroke="#999" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text x="525" y="270" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">Cartões</text>
  <text x="525" y="287" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#78716c">roadmap</text>

  <!-- banco particionado -->
  <rect x="278" y="316" width="332" height="96" rx="10" fill="#f9f9f7" stroke="#78716c" stroke-width="1.5"/>
  <text x="444" y="334" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#44403c">PostgreSQL — particionado: tempo + hash(conta_id)</text>
  <text x="444" y="349" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#166534">conta quente do marketplace em N baldes (Seção 6)</text>
  <g stroke-width="1">
    <path d="M 288 360 v20 a20 4.5 0 0 0 40 0 v-20" fill="#eef2ff" stroke="#4338ca"/>
    <ellipse cx="308" cy="360" rx="20" ry="4.5" fill="#eef2ff" stroke="#4338ca"/>
    <path d="M 342 360 v20 a20 4.5 0 0 0 40 0 v-20" fill="#eef2ff" stroke="#4338ca"/>
    <ellipse cx="362" cy="360" rx="20" ry="4.5" fill="#eef2ff" stroke="#4338ca"/>
    <path d="M 396 360 v20 a20 4.5 0 0 0 40 0 v-20" fill="#f0fdf4" stroke="#166534"/>
    <ellipse cx="416" cy="360" rx="20" ry="4.5" fill="#f0fdf4" stroke="#166534"/>
    <path d="M 450 360 v20 a20 4.5 0 0 0 40 0 v-20" fill="#f0fdf4" stroke="#166534"/>
    <ellipse cx="470" cy="360" rx="20" ry="4.5" fill="#f0fdf4" stroke="#166534"/>
    <path d="M 504 360 v20 a20 4.5 0 0 0 40 0 v-20" fill="#eef2ff" stroke="#4338ca"/>
    <ellipse cx="524" cy="360" rx="20" ry="4.5" fill="#eef2ff" stroke="#4338ca"/>
    <path d="M 558 360 v20 a20 4.5 0 0 0 40 0 v-20" fill="#eef2ff" stroke="#4338ca"/>
    <ellipse cx="578" cy="360" rx="20" ry="4.5" fill="#eef2ff" stroke="#4338ca"/>
  </g>
  <g font-family="sans-serif" font-size="7.5" fill="#666" text-anchor="middle">
    <text x="308" y="398">identidade</text>
    <text x="362" y="398">contas</text>
    <text x="416" y="398" fill="#166534">ledger ×8</text>
    <text x="470" y="398" fill="#166534">outbox</text>
    <text x="524" y="398">pagamentos</text>
    <text x="578" y="398">antifraude</text>
  </g>

  <!-- bulkhead na aresta do DICT -->
  <rect x="630" y="64" width="120" height="54" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="690" y="84" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#166534">bulkhead · circuit</text>
  <text x="690" y="99" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#166534">breaker · timeout 1 s</text>

  <!-- BACEN -->
  <rect x="790" y="60" width="150" height="56" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="865" y="84" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">DICT</text>
  <text x="865" y="102" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#7a5c00">p99 1 s</text>
  <rect x="790" y="170" width="150" height="72" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="865" y="193" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">SPI</text>
  <text x="865" y="211" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#7a5c00">pacs.008 → pacs.002</text>
  <text x="865" y="227" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#7a5c00">liquidação final</text>

  <!-- pipeline assíncrono -->
  <rect x="402" y="452" width="140" height="56" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="472" y="474" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">Relay</text>
  <text x="472" y="492" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">poller → Debezium (CDC)</text>
  <rect x="578" y="452" width="132" height="56" rx="9" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="644" y="474" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7a5c00">Kafka</text>
  <text x="644" y="492" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#7a5c00">tópico PixLiquidado</text>

  <!-- read models -->
  <rect x="760" y="380" width="190" height="44" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="855" y="398" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#166534">Redis — saldo exibido</text>
  <text x="855" y="414" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#4d7c5f">leitura em µs</text>
  <rect x="760" y="432" width="190" height="44" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="855" y="450" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#166534">Réplica PG — extrato</text>
  <text x="855" y="466" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#4d7c5f">SQL · paginação</text>
  <rect x="760" y="484" width="190" height="44" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="855" y="502" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#166534">Feed / notificações</text>
  <text x="855" y="518" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#4d7c5f">push · e-mail</text>
  <rect x="760" y="536" width="190" height="64" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="855" y="556" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#166534">Reconciliação</text>
  <text x="855" y="572" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#166534">ledger × Conta PI, por E2E ID</text>
  <text x="855" y="586" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#4d7c5f">divergência vira investigação</text>

  <!-- fluxos -->
  <g stroke="#4338ca" stroke-width="2">
    <line x1="98" y1="150" x2="116" y2="150" marker-end="url(#a2z-int)"/>
    <line x1="244" y1="152" x2="316" y2="185" marker-end="url(#a2z-int)"/>
    <line x1="550" y1="178" x2="628" y2="95" marker-end="url(#a2z-int)"/>
  </g>
  <g stroke="#d4a017" stroke-width="2.5">
    <line x1="750" y1="88" x2="788" y2="88" marker-end="url(#a2z-ext)"/>
    <line x1="550" y1="205" x2="788" y2="205" marker-end="url(#a2z-ext)"/>
  </g>
  <g stroke="#166534" stroke-width="2">
    <line x1="470" y1="412" x2="471" y2="448" marker-end="url(#a2z-g)"/>
    <line x1="542" y1="480" x2="574" y2="480" marker-end="url(#a2z-g)"/>
  </g>
  <g stroke="#166534" stroke-width="1.5">
    <line x1="710" y1="472" x2="756" y2="404" marker-end="url(#a2z-g)"/>
    <line x1="710" y1="478" x2="756" y2="454" marker-end="url(#a2z-g)"/>
    <line x1="710" y1="486" x2="756" y2="506" marker-end="url(#a2z-g)"/>
    <line x1="710" y1="492" x2="756" y2="562" marker-end="url(#a2z-g)"/>
  </g>
  <line x1="862" y1="244" x2="858" y2="533" stroke="#d4a017" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#a2z-ext)"/>
  <text x="876" y="330" font-family="sans-serif" font-size="9" fill="#7a5c00">extrato da</text>
  <text x="876" y="344" font-family="sans-serif" font-size="9" fill="#7a5c00">Conta PI</text>
  <text x="876" y="358" font-family="sans-serif" font-size="9" fill="#7a5c00">(settlement)</text>

  <!-- CI -->
  <rect x="30" y="452" width="210" height="76" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="135" y="474" text-anchor="middle" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#166534">CI — fitness functions</text>
  <text x="135" y="492" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#166534">ArchUnit: fronteira de módulo quebra o build</text>
  <text x="135" y="508" text-anchor="middle" font-family="sans-serif" font-size="8.5" fill="#166534">k6: teste de degrau a cada release</text>

  <!-- pendência -->
  <rect x="30" y="560" width="580" height="44" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="6 4"/>
  <text x="320" y="578" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">pendência aberta (ADR-002, linha "Revisão"): se a contenção persistir,</text>
  <text x="320" y="594" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">reparticionar a própria escrita do ledger — ainda sem dono</text>

  <text x="480" y="640" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">branco/cinza = já existia (Aula 1) · verde = construído nesta aula · tracejado = roadmap</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O retrato ao fim da Aula 2: a travessia da Seção 1, agora com defesas na borda, bulkhead na aresta do DICT, banco particionado, e o pipeline Outbox → Kafka alimentando os quatro read models. Reparem no canto direito — eventos internos de um lado, extrato da Conta PI do outro, reconciliação no meio: é o mesmo desenho de settlement e reconciliation que aparece em qualquer referência clássica de payment system.</p>
</div>

---

## Apêndice — Termos novos desta aula

| Termo | O que é |
|---|---|
| **Big Ball of Mud** | Sistema sem fronteiras internas reais; qualquer parte pode acoplar em qualquer outra. O oposto de um monólito modular bem-feito. |
| **Monolith first** | Recomendação (Martin Fowler) de começar um sistema novo como monólito modular, extraindo serviços só depois que as fronteiras se provarem estáveis. |
| **Transação cross-módulo** | Dois módulos escrevendo no mesmo `COMMIT` ACID. Grátis no monólito, fatal na extração: atomicidade não atravessa a rede, e o `COMMIT` vira saga. Cada transação pertence a um módulo só. |
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
| **Reconciliação** | Bater, movimento a movimento (por E2E ID), o ledger interno contra o extrato da Conta PI no BACEN. Divergência abre investigação — nunca correção automática; a correção entra como lançamento novo. |
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
| **Scale-up (escala vertical)** | Máquina maior (mais CPU/RAM/NVMe). Simples e preserva a transação local, mas tem teto físico, custo não-linear e continua um único ponto de falha. |
| **Scale-out (escala horizontal)** | Mais máquinas. Para leitura, réplicas — quase de graça; para escrita fortemente consistente, exige particionar e pagar coordenação. |
| **Cache-aside** | A aplicação consulta o cache; no miss, busca no banco e grava no cache. Só cacheia o que é lido; o primeiro acesso paga o miss. Caso TechPix: cache do DICT. |
| **Read-through / write-through** | Variações em que o próprio cache busca no banco (read-through) ou toda escrita passa pelo cache e pelo banco juntos (write-through). |
| **Invalidação: TTL × por evento** | TTL: o dado expira sozinho (mentira limitada ao TTL). Por evento: um consumidor atualiza o cache a cada evento — o saldo exibido no Redis é projeção, não expira. |
| **microservices.io** | Catálogo de padrões de microsserviços de Chris Richardson — referência para Transactional Outbox, CQRS, Saga, Strangler Fig, Circuit Breaker e afins. |

---

[← Aula 1](aula1-conteudo-completo.md) · [Índice](index.md) · [Aula 3 →](aula3-conteudo-completo.md)
