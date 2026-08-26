---
layout: default
title: "Aula 3 — Do monólito aos serviços: modelagem de domínio com 20 pessoas e pouco dinheiro"
---

# Aula 3 — Do monólito aos serviços: modelagem de domínio com 20 pessoas, pouco dinheiro e o BACEN olhando

*Curso de Arquitetura de Sistemas Financeiros com IA · versão evolutiva da Aula 3*

> **Nota para mim (não é falada):** os números de custo — R$ 50 mil, R$ 3.400/mês, R$ 2.500/mês — são cenário hipotético montado para a discussão, não cotação. Dizer isso à turma na hora da tabela da seção 1. Os alunos não veem este documento; o que está abaixo é o texto como eu falo. Ao fim, eles recebem o repositório `fintechdev-aula-3`.

Bom, a aula de hoje é sobre modelagem de domínio. Mas eu não vou começar por modelagem de domínio. Vou começar por uma reunião.

Nas duas primeiras aulas a gente construiu a TechPix: um ledger que não perde dinheiro, um fluxo de Pix que fala com o DICT e com o SPI, uma outbox que garante que evento não some, defesas contra pico de tráfego. E tudo isso mora num único lugar — um binário Go, um Postgres, um deploy. Eu disse na Aula 1 que isso era uma escolha, e uma boa escolha. Hoje eu quero contar o que aconteceu quando essa escolha foi questionada.

A TechPix cresceu. São vinte desenvolvedores mexendo nesse código. E vinte pessoas num único deploy é exatamente o tamanho em que alguém, numa reunião de planejamento, levanta a mão e diz: *"a gente devia começar a quebrar isso em microsserviços"*. Na mesma reunião — porque a vida é assim — o financeiro pergunta se vamos comprar servidor ou alugar nuvem, e o compliance lembra que a gente opera Pix, e que o Banco Central tem opinião sobre continuidade, backup, segurança e onde os dados moram.

Eu quero levar essa reunião a sério, com vocês, nas próximas duas horas. Porque a resposta certa para "quebrar ou não quebrar" passa por tudo o que a aula de hoje ensina — bounded contexts, event storming, agregados, mapa de contexto —, só que numa ordem diferente da que os livros usam. Os livros começam pela técnica e chegam na arquitetura. A gente vai começar pela situação: vinte pessoas, pouco dinheiro, o regulador olhando. E vai descobrir que a pergunta "microsserviços sim ou não" é a **última** da lista, não a primeira. Antes dela vêm três outras. E a terceira delas — quais são as fronteiras de verdade do nosso domínio — é a única que não muda seja qual for a resposta das outras. Por isso ela é o tema de hoje.

## 0. A reunião de planejamento

A situação é esta. A TechPix tem hoje **vinte desenvolvedores**. O sistema é **um binário Go** — `cmd/techpix` —, **um Postgres**, **um deploy**. Quinze módulos dentro de `internal/modules/`. Tudo sobe com `docker compose up`. Isso foi uma escolha registrada por escrito, no ADR-002: começar por um monólito, porque não tínhamos nem o problema de escala nem o problema de autonomia de times que justifica separar processos.

Deixa eu desenhar o que existe hoje, porque tudo nesta aula parte deste desenho.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 260" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p0-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">A TechPix hoje: um processo, um banco, um deploy — e vinte pessoas atrás dele</text>
  <!-- devs -->
  <g fill="#534AB7">
    <circle cx="45" cy="90" r="9"/><circle cx="70" cy="90" r="9"/><circle cx="95" cy="90" r="9"/><circle cx="120" cy="90" r="9"/><circle cx="145" cy="90" r="9"/>
    <circle cx="45" cy="115" r="9"/><circle cx="70" cy="115" r="9"/><circle cx="95" cy="115" r="9"/><circle cx="120" cy="115" r="9"/><circle cx="145" cy="115" r="9"/>
    <circle cx="45" cy="140" r="9"/><circle cx="70" cy="140" r="9"/><circle cx="95" cy="140" r="9"/><circle cx="120" cy="140" r="9"/><circle cx="145" cy="140" r="9"/>
    <circle cx="45" cy="165" r="9"/><circle cx="70" cy="165" r="9"/><circle cx="95" cy="165" r="9"/><circle cx="120" cy="165" r="9"/><circle cx="145" cy="165" r="9"/>
  </g>
  <text x="95" y="195" text-anchor="middle" font-size="11" fill="#57534e">20 desenvolvedores</text>
  <line x1="165" y1="128" x2="215" y2="128" stroke="#57534e" stroke-width="2" marker-end="url(#p0-a)"/>
  <text x="190" y="118" text-anchor="middle" font-size="10" fill="#8a897f">1 repo</text>
  <!-- pipeline -->
  <rect x="220" y="100" width="130" height="56" rx="8" fill="#fff" stroke="#57534e" stroke-width="2"/>
  <text x="285" y="124" text-anchor="middle" font-size="12" font-weight="bold" fill="#1f1e1c">1 pipeline</text>
  <text x="285" y="142" text-anchor="middle" font-size="10.5" fill="#57534e">build · test · deploy</text>
  <line x1="352" y1="128" x2="392" y2="128" stroke="#57534e" stroke-width="2" marker-end="url(#p0-a)"/>
  <!-- binary -->
  <rect x="398" y="60" width="250" height="140" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="523" y="84" text-anchor="middle" font-size="13" font-weight="bold" fill="#26215C">cmd/techpix — 1 binário Go</text>
  <g font-size="9.5" fill="#26215C" text-anchor="middle">
    <rect x="410" y="96" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="445" y="111">ledger</text>
    <rect x="488" y="96" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="523" y="111">pix</text>
    <rect x="566" y="96" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="601" y="111">limites</text>
    <rect x="410" y="124" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="445" y="139">bacen</text>
    <rect x="488" y="124" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="523" y="139">identidade</text>
    <rect x="566" y="124" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="601" y="139">devolucoes</text>
    <rect x="410" y="152" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="445" y="167">outbox</text>
    <rect x="488" y="152" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="523" y="167">idempotency</text>
    <rect x="566" y="152" width="70" height="22" rx="4" fill="#fff" stroke="#534AB7"/><text x="601" y="167">+ 6 outros</text>
  </g>
  <text x="523" y="190" text-anchor="middle" font-size="10" fill="#5a55a0">15 módulos · 1 deploy</text>
  <line x1="650" y1="128" x2="690" y2="128" stroke="#57534e" stroke-width="2" marker-end="url(#p0-a)"/>
  <!-- db -->
  <rect x="696" y="88" width="180" height="80" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2.5"/>
  <text x="786" y="114" text-anchor="middle" font-size="13" font-weight="bold" fill="#04342C">1 PostgreSQL</text>
  <text x="786" y="134" text-anchor="middle" font-size="10.5" fill="#04342C">ledger ACID · outbox</text>
  <text x="786" y="152" text-anchor="middle" font-size="10.5" fill="#04342C">4 schemas</text>
  <text x="450" y="240" text-anchor="middle" font-size="11" fill="#8a897f">o que a reunião questionou não foi o desenho — foi se ele aguenta vinte pessoas, pouco dinheiro e o regulador</text>
</svg>
</div>

Só que vinte pessoas num único deploy é o tamanho exato em que alguém, na reunião, diz a frase: *"a gente devia começar a quebrar isso em microsserviços"*. E na mesma reunião, porque a vida é assim, o financeiro pergunta se vamos comprar servidor ou alugar nuvem, e o compliance lembra que somos uma instituição que opera Pix, e que o Banco Central tem opinião sobre continuidade, backup, segurança cibernética e onde os dados moram.

Três pressões de uma vez, e eu quero que vocês vejam as três como forças puxando o mesmo desenho em direções diferentes:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 280" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p0-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Três pressões, um sistema</text>
  <rect x="350" y="105" width="200" height="70" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="450" y="134" text-anchor="middle" font-size="13" font-weight="bold" fill="#26215C">o monólito TechPix</text>
  <text x="450" y="156" text-anchor="middle" font-size="10.5" fill="#26215C">como está hoje</text>
  <!-- organização -->
  <rect x="20" y="60" width="230" height="80" rx="10" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
  <text x="135" y="84" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#1e2a5a">Organização</text>
  <text x="135" y="104" text-anchor="middle" font-size="10.5" fill="#1e2a5a">20 pessoas → fila de deploy</text>
  <text x="135" y="122" text-anchor="middle" font-size="10.5" fill="#1e2a5a">"cada squad com seu serviço"</text>
  <line x1="252" y1="110" x2="345" y2="128" stroke="#1d4ed8" stroke-width="2" marker-end="url(#p0-b)"/>
  <text x="290" y="108" text-anchor="middle" font-size="9.5" fill="#1d4ed8">puxa para separar</text>
  <!-- dinheiro -->
  <rect x="20" y="170" width="230" height="80" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="135" y="194" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#04342C">Dinheiro</text>
  <text x="135" y="214" text-anchor="middle" font-size="10.5" fill="#04342C">R$ 50 mil × R$ 3.400/mês</text>
  <text x="135" y="232" text-anchor="middle" font-size="10.5" fill="#04342C">o caixa dos próximos 18 meses</text>
  <line x1="252" y1="200" x2="345" y2="160" stroke="#166534" stroke-width="2" marker-end="url(#p0-b)"/>
  <text x="290" y="192" text-anchor="middle" font-size="9.5" fill="#166534">puxa para simples</text>
  <!-- regulador -->
  <rect x="650" y="105" width="230" height="90" rx="10" fill="#FDE7EC" stroke="#be123c" stroke-width="2"/>
  <text x="765" y="129" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#5a1e2b">Regulador (BACEN)</text>
  <text x="765" y="149" text-anchor="middle" font-size="10.5" fill="#5a1e2b">continuidade · backup · auditoria</text>
  <text x="765" y="167" text-anchor="middle" font-size="10.5" fill="#5a1e2b">segurança cibernética · nuvem</text>
  <text x="765" y="185" text-anchor="middle" font-size="10.5" fill="#5a1e2b">não pergunta "monólito ou serviço"</text>
  <line x1="648" y1="140" x2="555" y2="140" stroke="#be123c" stroke-width="2" marker-end="url(#p0-b)"/>
  <text x="600" y="132" text-anchor="middle" font-size="9.5" fill="#be123c">puxa para provar</text>
  <text x="450" y="262" text-anchor="middle" font-size="11" fill="#8a897f">a boa arquitetura não escolhe uma força; ela encontra o desenho em que as três se sustentam</text>
</svg>
</div>

A pressão de **organização** empurra para separar: vinte pessoas geram fila de deploy, e a saída aparente é "cada squad com seu serviço". A pressão de **dinheiro** empurra para o simples: somos pequenos, e cada componente novo é uma linha na fatura e uma pessoa a menos escrevendo produto. E a pressão **regulatória** empurra para provar: o BACEN não pergunta se somos monólito ou microsserviço — pergunta se temos um plano para quando cair, e se conseguimos demonstrar isso.

A tese que eu vou defender, e que vocês vão poder verificar no repositório que recebem no fim, é simples de enunciar e difícil de praticar: **a decisão "microsserviços sim ou não" é a última da lista, não a primeira.** Antes dela vêm três outras — *onde* rodar, *com o quê* rodar, e *quais são as fronteiras de verdade* do nosso domínio. Quem pula as três e vai direto para a última costuma acertar a topologia e errar o sistema.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 250" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="m4d-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">As quatro decisões — nesta ordem</text>
  <rect x="20" y="60" width="190" height="120" rx="10" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
  <text x="115" y="88" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#1e2a5a">1 · ONDE rodar</text>
  <text x="115" y="114" text-anchor="middle" font-size="11.5" fill="#1e2a5a">on-prem × AWS</text>
  <text x="115" y="134" text-anchor="middle" font-size="11.5" fill="#1e2a5a">CAPEX × OPEX</text>
  <text x="115" y="154" text-anchor="middle" font-size="11.5" fill="#1e2a5a">o que o BACEN exige</text>
  <line x1="212" y1="120" x2="238" y2="120" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-a)"/>
  <rect x="242" y="60" width="190" height="120" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="337" y="88" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#04342C">2 · COM O QUÊ</text>
  <text x="337" y="114" text-anchor="middle" font-size="11.5" fill="#04342C">Linux, Docker, Go, Postgres</text>
  <text x="337" y="134" text-anchor="middle" font-size="11.5" fill="#04342C">Kubernetes? ainda não</text>
  <text x="337" y="154" text-anchor="middle" font-size="11.5" fill="#04342C">cada escolha com gatilho</text>
  <line x1="434" y1="120" x2="460" y2="120" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-a)"/>
  <rect x="464" y="60" width="190" height="120" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="559" y="88" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#26215C">3 · QUAIS fronteiras</text>
  <text x="559" y="114" text-anchor="middle" font-size="11.5" fill="#26215C">event storming</text>
  <text x="559" y="134" text-anchor="middle" font-size="11.5" fill="#26215C">bounded contexts</text>
  <text x="559" y="154" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#534AB7">o tema desta aula</text>
  <line x1="656" y1="120" x2="682" y2="120" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-a)"/>
  <rect x="686" y="60" width="190" height="120" rx="10" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/>
  <text x="781" y="88" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#412402">4 · DECOMPOR?</text>
  <text x="781" y="114" text-anchor="middle" font-size="11.5" fill="#412402">módulo ou serviço,</text>
  <text x="781" y="134" text-anchor="middle" font-size="11.5" fill="#412402">contexto por contexto,</text>
  <text x="781" y="154" text-anchor="middle" font-size="11.5" fill="#412402">com quatro gatilhos</text>
  <text x="450" y="222" text-anchor="middle" font-size="12" fill="#8a897f">a decisão 4 só faz sentido depois da 3 — e a 3 é a mesma seja qual for a resposta da 1 e da 2</text>
</svg>
</div>

Uma pergunta para a sala antes de seguir: *se a TechPix tivesse decidido, hoje, quebrar em serviços, por onde ela cortaria?* Guardem a resposta. No fim da aula vocês vão comparar com o que a técnica diz.

---

## 1. Onde rodar: a conta que chega na reunião, e as duas que faltam

A primeira pergunta é a que o financeiro fez, e ela chega em forma de planilha. Deixa eu reproduzir a planilha como ela apareceu.

| Cenário | Investimento inicial | Recorrente por mês | O que está incluído |
|---|---|---|---|
| **On-premises** | R$ 50.000 | energia, backup e manutenção | um servidor de aplicação (R$ 25 mil) e um servidor de PostgreSQL (R$ 25 mil) |
| **AWS sob demanda** | R$ 0 | ≈ R$ 3.400 | ≈ R$ 1.300 para a aplicação, ≈ R$ 1.300 para o Postgres gerenciado, e o restante em storage, backup e monitoramento |
| **AWS com compromisso de uso** | R$ 0 | ≈ R$ 2.500 | a mesma topologia, com um Savings Plan ou instâncias reservadas de um ano |

A primeira leitura é a mais natural e a mais enganosa: **R$ 50.000 dividido por R$ 3.400 dá mais ou menos quinze meses**. Depois de quinze meses, o servidor "se pagou", e a nuvem é aluguel para sempre. Com o compromisso de uso, R$ 50.000 dividido por R$ 2.500 dá vinte meses. Parece que, a partir do segundo ano, o datacenter próprio ganha. Eu já vi essa conta decidir a infraestrutura de empresas inteiras, e quero mostrar por que ela está incompleta em duas direções.

### 1.1 A conta da operação: o que R$ 50 mil não compra

Vamos reler a linha do on-premises com os olhos de quem vai operar isso às três da manhã. Primeiro, o desenho do que os R$ 50 mil compram:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p1-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">O que R$ 50 mil compram: dois servidores, dois pontos únicos de falha</text>
  <!-- left: what was bought -->
  <rect x="20" y="50" width="400" height="230" rx="12" fill="none" stroke="#8a897f" stroke-width="1.5" stroke-dasharray="7 5"/>
  <text x="35" y="70" font-size="11" fill="#8a897f">sala de servidores da TechPix · 1 local · 1 link</text>
  <text x="120" y="120" text-anchor="middle" font-size="11" fill="#57534e">clientes</text>
  <line x1="120" y1="126" x2="120" y2="150" stroke="#57534e" stroke-width="2" marker-end="url(#p1-a)"/>
  <rect x="50" y="155" width="140" height="60" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="120" y="180" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">servidor app</text>
  <text x="120" y="200" text-anchor="middle" font-size="10.5" fill="#26215C">R$ 25 mil</text>
  <line x1="192" y1="185" x2="248" y2="185" stroke="#57534e" stroke-width="2" marker-end="url(#p1-a)"/>
  <rect x="252" y="155" width="140" height="60" rx="8" fill="#E1F5EE" stroke="#166534" stroke-width="2.5"/>
  <text x="322" y="180" text-anchor="middle" font-size="12" font-weight="bold" fill="#04342C">servidor Postgres</text>
  <text x="322" y="200" text-anchor="middle" font-size="10.5" fill="#04342C">R$ 25 mil</text>
  <!-- X marks -->
  <g stroke="#be123c" stroke-width="3.5" stroke-linecap="round">
    <line x1="160" y1="140" x2="185" y2="165"/><line x1="185" y1="140" x2="160" y2="165"/>
    <line x1="362" y1="140" x2="387" y2="165"/><line x1="387" y1="140" x2="362" y2="165"/>
  </g>
  <text x="120" y="245" text-anchor="middle" font-size="10" fill="#be123c">fonte queima → TechPix para</text>
  <text x="322" y="245" text-anchor="middle" font-size="10" fill="#be123c">disco morre → TechPix para</text>
  <text x="220" y="268" text-anchor="middle" font-size="10" fill="#be123c">incêndio / queda de energia / link → tudo para junto</text>
  <!-- right: what a fintech needs -->
  <rect x="460" y="50" width="420" height="230" rx="12" fill="none" stroke="#166534" stroke-width="1.5" stroke-dasharray="7 5"/>
  <text x="475" y="70" font-size="11" fill="#166534">o mínimo que uma operação Pix precisa provar</text>
  <text x="560" y="98" text-anchor="middle" font-size="10.5" fill="#57534e">local A</text>
  <rect x="490" y="108" width="140" height="42" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="560" y="134" text-anchor="middle" font-size="11" fill="#26215C">app</text>
  <rect x="490" y="160" width="140" height="42" rx="8" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="560" y="186" text-anchor="middle" font-size="11" fill="#04342C">Postgres primário</text>
  <text x="780" y="98" text-anchor="middle" font-size="10.5" fill="#57534e">local B (outro prédio)</text>
  <rect x="710" y="108" width="140" height="42" rx="8" fill="#fff" stroke="#534AB7" stroke-width="2" stroke-dasharray="5 3"/>
  <text x="780" y="134" text-anchor="middle" font-size="11" fill="#26215C">app (réplica)</text>
  <rect x="710" y="160" width="140" height="42" rx="8" fill="#fff" stroke="#166534" stroke-width="2" stroke-dasharray="5 3"/>
  <text x="780" y="186" text-anchor="middle" font-size="11" fill="#04342C">Postgres réplica</text>
  <line x1="632" y1="181" x2="706" y2="181" stroke="#166534" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="669" y="174" text-anchor="middle" font-size="9" fill="#166534">replicação</text>
  <text x="670" y="228" text-anchor="middle" font-size="11" font-weight="bold" fill="#166534">4 máquinas · 2 locais · 2 links · ≈ R$ 100 mil</text>
  <text x="670" y="250" text-anchor="middle" font-size="10" fill="#57534e">+ alguém para operar, testar o backup e trocar o disco</text>
  <text x="670" y="268" text-anchor="middle" font-size="10" fill="#57534e">+ hardware que se repete em 3–5 anos</text>
</svg>
</div>

Um servidor de aplicação e um servidor de banco são **dois pontos únicos de falha**. Não existe alta disponibilidade nessa configuração. Se o disco do Postgres morre, a TechPix para. Se a fonte do servidor queima, a TechPix para. E para uma instituição que participa do Pix, "parar" não é um inconveniente — é uma indisponibilidade que precisa ser reportada, que conta contra os requisitos de disponibilidade do arranjo, e que aparece na conversa seguinte com o regulador. Ter redundância mínima on-premises significa **dobrar** o hardware: são cem mil, não cinquenta. E dobrar em outro lugar físico, porque duas máquinas no mesmo rack dividem o mesmo incêndio, a mesma queda de energia e o mesmo link.

A linha "energia, backup e manutenção" tem gente dentro dela. Backup que ninguém testa não é backup — é um arquivo. Manutenção inclui patch de sistema operacional, troca de disco, atualização de firmware, renovação de certificado. Quem faz isso? Ou é um dos vinte desenvolvedores, que deixa de desenvolver, ou é uma contratação. Esse custo é o maior da linha e é justamente o que a planilha não mostra. E o hardware envelhece: em três a cinco anos, o investimento inicial se repete.

Agora a linha da nuvem. O que os R$ 3.400 estão comprando de verdade não é um servidor. É um Postgres gerenciado com backup automático e uma réplica em outra zona de disponibilidade; é patch de sistema operacional feito por outra pessoa; é monitoramento pronto; é storage que cresce sem ninguém comprar disco; e é a possibilidade de **errar o tamanho e corrigir amanhã**, que com hardware comprado não existe. Vocês não estão pagando uma máquina. Estão pagando o time de operação que não precisam contratar.

E o compromisso de uso, os R$ 2.500, precisa ser lido como o que ele é: **uma aposta na topologia**. O Savings Plan reduz em torno de um quarto do valor em troca de um ano de previsibilidade. A pergunta certa não é "vale a pena?"; é "temos certeza de que essa topologia sobrevive um ano?". Se a resposta da seção 6 desta aula for "vamos extrair dois serviços em seis meses", o compromisso só deveria cobrir a parte que não muda. Guardem essa observação; ela volta no fim.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Custo acumulado em 36 meses (cenário hipotético)</text>
  <line x1="70" y1="250" x2="860" y2="250" stroke="#8a897f" stroke-width="1.5"/>
  <line x1="70" y1="250" x2="70" y2="50" stroke="#8a897f" stroke-width="1.5"/>
  <text x="865" y="255" font-size="11" fill="#8a897f">meses</text>
  <text x="30" y="42" font-size="11" fill="#8a897f" text-anchor="middle">R$</text>
  <g font-size="11" fill="#8a897f" text-anchor="middle"><text x="70" y="270">0</text><text x="333" y="270">12</text><text x="596" y="270">24</text><text x="858" y="270">36</text></g>
  <g font-size="10.5" fill="#8a897f" text-anchor="end"><text x="64" y="204">50k</text><text x="64" y="154">100k</text><text x="64" y="104">150k</text><text x="64" y="54">200k</text></g>
  <line x1="70" y1="250" x2="858" y2="128" stroke="#1d4ed8" stroke-width="3"/>
  <text x="640" y="118" font-size="12" fill="#1d4ed8">AWS sob demanda · 3,4k/mês</text>
  <line x1="70" y1="250" x2="858" y2="160" stroke="#166534" stroke-width="3"/>
  <text x="690" y="205" font-size="12" fill="#166534">AWS compromisso · 2,5k/mês</text>
  <line x1="70" y1="200" x2="858" y2="171" stroke="#b45309" stroke-width="3" stroke-dasharray="8 5"/>
  <text x="180" y="185" font-size="12" fill="#b45309">on-prem "planilha" · 50k + 0,8k/mês</text>
  <line x1="70" y1="150" x2="858" y2="42" stroke="#be123c" stroke-width="3"/>
  <text x="200" y="118" font-size="12" fill="#be123c">on-prem com redundância + operação · 100k + 3k/mês</text>
  <circle cx="530" cy="180" r="5" fill="#b45309"/>
  <text x="540" y="235" font-size="11" fill="#8a897f">↑ cruzamento "planilha" ≈ mês 20</text>
</svg>
</div>

Reparem no desenho. A linha tracejada é a que a planilha mostra, e ela cruza a linha da nuvem lá pelo mês vinte. A linha vermelha é a que a planilha esconde: assim que a redundância que uma operação financeira exige entra na conta, junto com uma fração de uma pessoa para operar, o cruzamento simplesmente some do horizonte de três anos. Os valores são ilustrativos; a forma das curvas não é.

### 1.2 A conta do regulador

A terceira coluna da conta é a que o compliance trouxe, e ela é a mais interessante porque **o BACEN não escolhe nuvem ou datacenter por vocês**. Ele impõe requisitos, e os requisitos tornam uma das opções muito mais cara de cumprir com vinte pessoas e pouco dinheiro. Eu vou descrever em traços largos — a leitura fina é com o jurídico, e as normas mudam.

A Resolução BCB 85/2021, para instituições de pagamento, e a Resolução CMN 4.893/2021, para instituições financeiras, exigem uma **política de segurança cibernética**, um plano de resposta a incidentes e a comunicação de incidentes relevantes. Elas também regulam a **contratação de serviços de nuvem**: comunicar ao Banco Central, ter contrato que garanta ao regulador acesso aos dados e à documentação, ter plano de saída, e garantir que os dados sejam acessíveis a partir do Brasil — a região de São Paulo resolve a localização, mas o contrato e a comunicação são trabalho real do jurídico. E exigem **continuidade de negócios**: backup, recuperação, redundância proporcional ao risco.

A ideia que organiza tudo isso na nuvem chama-se **responsabilidade compartilhada**, e vale desenhar, porque é o que explica por que a mesma lista de exigências custa tão diferente nos dois cenários:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Quem responde por cada camada — on-premises × nuvem</text>
  <text x="230" y="56" text-anchor="middle" font-size="12" font-weight="bold" fill="#57534e">on-premises</text>
  <text x="670" y="56" text-anchor="middle" font-size="12" font-weight="bold" fill="#57534e">nuvem (serviços gerenciados)</text>
  <!-- layers labels -->
  <g font-size="10.5" fill="#1f1e1c" text-anchor="middle">
    <!-- on-prem column: all yours -->
    <rect x="60" y="70" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="230" y="90">política de segurança, resposta a incidentes, LGPD</text>
    <rect x="60" y="104" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="230" y="124">aplicação, regras de negócio, ledger, trilha de auditoria</text>
    <rect x="60" y="138" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="230" y="158">Postgres: patch, backup, réplica, failover, restore testado</text>
    <rect x="60" y="172" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="230" y="192">sistema operacional, kernel, certificados, hardening</text>
    <rect x="60" y="206" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="230" y="226">rede, firewall, links, DDoS</text>
    <rect x="60" y="240" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="230" y="260">hardware, disco, fonte, refrigeração, energia</text>
    <rect x="60" y="274" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="230" y="294">prédio, acesso físico, segundo local</text>
    <!-- cloud column -->
    <rect x="500" y="70" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="670" y="90">política de segurança, resposta a incidentes, LGPD</text>
    <rect x="500" y="104" width="340" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="670" y="124">aplicação, regras de negócio, ledger, trilha de auditoria</text>
    <rect x="500" y="138" width="340" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="670" y="158">Postgres: configurar Multi-AZ e retenção (o resto é do provedor)</text>
    <rect x="500" y="172" width="340" height="30" rx="5" fill="#E1F5EE" stroke="#166534"/><text x="670" y="192">SO e hardening do serviço gerenciado</text>
    <rect x="500" y="206" width="340" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="670" y="226">rede: vocês desenham a VPC; o provedor opera</text>
    <rect x="500" y="240" width="340" height="30" rx="5" fill="#E1F5EE" stroke="#166534"/><text x="670" y="260">hardware, disco, fonte, refrigeração, energia</text>
    <rect x="500" y="274" width="340" height="30" rx="5" fill="#E1F5EE" stroke="#166534"/><text x="670" y="294">prédio, acesso físico, zonas de disponibilidade</text>
  </g>
  <g font-size="10" text-anchor="start">
    <rect x="60" y="312" width="12" height="12" fill="#FDE7EC" stroke="#be123c"/><text x="78" y="322" fill="#57534e">vocês</text>
    <rect x="130" y="312" width="12" height="12" fill="#FAEEDA" stroke="#b45309"/><text x="148" y="322" fill="#57534e">compartilhado</text>
    <rect x="240" y="312" width="12" height="12" fill="#E1F5EE" stroke="#166534"/><text x="258" y="322" fill="#57534e">provedor (auditado, com relatórios que o regulador aceita)</text>
  </g>
</svg>
</div>

Olhem para as duas colunas. As duas linhas de cima — política, aplicação, ledger, auditoria — são vermelhas nos dois lados: são **de vocês** em qualquer cenário, e nenhum provedor vai escrevê-las. A diferença está nas cinco linhas de baixo. On-premises, todas são de vocês. Na nuvem, boa parte vira responsabilidade do provedor, que entrega relatórios de auditoria que o regulador reconhece. O trabalho não desaparece; ele muda de dono — e para vinte pessoas, mudar de dono é a diferença entre conseguir cumprir e não conseguir.

O Regulamento do Pix acrescenta requisitos de disponibilidade e tempo de resposta, e um detalhe que sempre surpreende a turma: conectar ao SPI não é abrir uma porta HTTPS. É rede privada, a RSFN. Uma fintech pequena normalmente não faz isso sozinha — ou contrata um **PSTI**, um provedor de tecnologia homologado, ou entra no Pix como **participante indireto**, liquidando por meio de um participante direto.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p1-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Três jeitos de chegar ao SPI — e o que cada um exige da TechPix</text>
  <!-- BACEN box right -->
  <rect x="700" y="70" width="180" height="170" rx="10" fill="#FDE7EC" stroke="#be123c" stroke-width="2.5"/>
  <text x="790" y="96" text-anchor="middle" font-size="13" font-weight="bold" fill="#5a1e2b">BACEN</text>
  <text x="790" y="118" text-anchor="middle" font-size="11" fill="#5a1e2b">DICT · SPI</text>
  <text x="790" y="150" text-anchor="middle" font-size="10" fill="#5a1e2b">acessível só pela</text>
  <text x="790" y="166" text-anchor="middle" font-size="11" font-weight="bold" fill="#5a1e2b">RSFN (rede privada)</text>
  <text x="790" y="196" text-anchor="middle" font-size="10" fill="#5a1e2b">mensagens ISO 20022</text>
  <text x="790" y="212" text-anchor="middle" font-size="10" fill="#5a1e2b">assinadas (ICP-Brasil)</text>
  <!-- option A -->
  <rect x="20" y="60" width="180" height="50" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="110" y="80" text-anchor="middle" font-size="11" font-weight="bold" fill="#26215C">A · participante direto</text>
  <text x="110" y="98" text-anchor="middle" font-size="10" fill="#26215C">link RSFN próprio, conta PI</text>
  <line x1="202" y1="85" x2="696" y2="85" stroke="#534AB7" stroke-width="2" marker-end="url(#p1-b)"/>
  <text x="450" y="78" text-anchor="middle" font-size="10" fill="#534AB7">infra e homologação inteiras de vocês — caro, lento, para grandes</text>
  <!-- option B -->
  <rect x="20" y="130" width="180" height="50" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="110" y="150" text-anchor="middle" font-size="11" font-weight="bold" fill="#26215C">B · direto via PSTI</text>
  <text x="110" y="168" text-anchor="middle" font-size="10" fill="#26215C">conta PI própria</text>
  <line x1="202" y1="155" x2="378" y2="155" stroke="#534AB7" stroke-width="2" marker-end="url(#p1-b)"/>
  <rect x="382" y="130" width="140" height="50" rx="8" fill="#fff" stroke="#57534e" stroke-width="2"/>
  <text x="452" y="150" text-anchor="middle" font-size="11" font-weight="bold" fill="#1f1e1c">PSTI</text>
  <text x="452" y="168" text-anchor="middle" font-size="10" fill="#57534e">provedor homologado</text>
  <line x1="524" y1="155" x2="696" y2="155" stroke="#534AB7" stroke-width="2" marker-end="url(#p1-b)"/>
  <text x="610" y="148" text-anchor="middle" font-size="10" fill="#534AB7">RSFN do provedor</text>
  <!-- option C -->
  <rect x="20" y="200" width="180" height="50" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="110" y="220" text-anchor="middle" font-size="11" font-weight="bold" fill="#26215C">C · participante indireto</text>
  <text x="110" y="238" text-anchor="middle" font-size="10" fill="#26215C">sem conta PI própria</text>
  <line x1="202" y1="225" x2="378" y2="225" stroke="#534AB7" stroke-width="2" marker-end="url(#p1-b)"/>
  <rect x="382" y="200" width="140" height="50" rx="8" fill="#fff" stroke="#57534e" stroke-width="2"/>
  <text x="452" y="220" text-anchor="middle" font-size="11" font-weight="bold" fill="#1f1e1c">participante direto</text>
  <text x="452" y="238" text-anchor="middle" font-size="10" fill="#57534e">liquida por vocês</text>
  <line x1="524" y1="225" x2="696" y2="225" stroke="#534AB7" stroke-width="2" marker-end="url(#p1-b)"/>
  <text x="610" y="218" text-anchor="middle" font-size="10" fill="#534AB7">a RSFN dele</text>
  <text x="450" y="280" text-anchor="middle" font-size="11" fill="#8a897f">nas três, o módulo <tspan font-family="monospace">bacen</tspan> da TechPix é a mesma ACL — só muda com quem ele fala do outro lado do fio</text>
</svg>
</div>

Essa decisão de negócio — A, B ou C — muda o módulo `bacen` mais do que qualquer decisão sobre microsserviços, e é por isso que ela entra numa aula de modelagem: a fronteira com o BACEN é a única fronteira que **já é** um sistema externo hoje, e ela já está atrás de uma camada anticorrupção. O simulador `bacen-sim` do repositório finge exatamente essa fronteira.

Agora coloquem os dois cenários lado a lado contra a lista de exigências. On-premises com dois servidores: vocês escrevem, implementam e operam todos os controles; a continuidade exige o segundo par de máquinas num segundo local; a política de segurança é inteiramente de vocês. Na nuvem com serviços gerenciados: vocês escrevem a política, mas boa parte dos controles técnicos vem pronta e auditada; Multi-AZ no banco e réplicas da aplicação são configuração, não compra; a burocracia da contratação existe, mas é papel, não hardware.

A frase que eu quero que fique: **o regulador não está do lado da nuvem; ele está do lado de quem prova continuidade.** Com vinte pessoas, provar continuidade num datacenter próprio custa gente e hardware que a gente não tem. Na nuvem custa configuração e contrato. É por isso — e não por moda — que a maioria das fintechs pequenas começa em nuvem e vai para on-premises ou híbrido só quando a escala inverte a conta.

### 1.3 A decisão

A decisão da TechPix, registrada para a turma: **AWS, sob demanda nos três primeiros meses; compromisso de uso só sobre o que não muda.** Sob demanda primeiro porque ainda não sabemos o tamanho certo — a Lei de Little da Aula 1, pool igual a TPS vezes latência, dá o ponto de partida, mas só o tráfego real dá o tamanho. Compromisso sobre o Postgres depois de estabilizar, porque ele é a parte que a seção 6 vai mostrar que não muda mesmo se a aplicação virar serviços. E reavaliar on-premises ou híbrido no dia em que a fatura mensal ultrapassar o salário de uma pessoa de infraestrutura dedicada. Antes disso, a nuvem *é* a pessoa de infraestrutura.

Pergunta para a sala: *qual é a primeira linha da fatura de vocês que, se dobrar, muda essa decisão?* Se ninguém sabe responder, a decisão não tem gatilho — e é disso que trata a próxima seção.

---
## 2. Com o quê rodar: a stack, decisão por decisão

A segunda pergunta é a que vocês vão receber no primeiro emprego, na forma de uma lista: vamos usar Linux? Docker? Kubernetes? Kafka? E a resposta didática nunca é "sim" ou "não". É "sim ou não, *porque*, e *até quando*". A regra que organiza esta seção inteira é: **toda escolha tem um gatilho de revisão escrito.** Sem gatilho, a escolha vira dogma — e dogma é como se chega tanto no "Kubernetes desde o dia um" quanto no "nunca vamos precisar de Kubernetes".

Antes de percorrer a lista, eu quero dar a vocês o desenho mental que separa as camadas, porque a confusão mais comum da turma é misturar "empacotar" com "orquestrar":

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">As camadas da stack — e o que cada uma responde</text>
  <g font-size="11">
    <rect x="40" y="50" width="820" height="36" rx="6" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
    <text x="60" y="73" font-weight="bold" fill="#26215C">código</text><text x="200" y="73" fill="#26215C">Go 1.25 · 15 módulos · internal/ como fronteira</text><text x="700" y="73" fill="#5a55a0">"o que o sistema faz"</text>
    <rect x="40" y="92" width="820" height="36" rx="6" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
    <text x="60" y="115" font-weight="bold" fill="#04342C">artefato</text><text x="200" y="115" fill="#04342C">imagem Docker (Alpine, binário estático, usuário sem privilégio)</text><text x="700" y="115" fill="#166534">"o que se entrega"</text>
    <rect x="40" y="134" width="820" height="36" rx="6" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/>
    <text x="60" y="157" font-weight="bold" fill="#412402">execução</text><text x="200" y="157" fill="#412402">ECS/Fargate ou 1 VM Linux + systemd — <tspan font-weight="bold">não Kubernetes</tspan></text><text x="700" y="157" fill="#b45309">"onde o artefato roda"</text>
    <rect x="40" y="176" width="820" height="36" rx="6" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
    <text x="60" y="199" font-weight="bold" fill="#1e2a5a">dados</text><text x="200" y="199" fill="#1e2a5a">RDS PostgreSQL 17 Multi-AZ · outbox na mesma base · sem broker</text><text x="700" y="199" fill="#1d4ed8">"o que não pode se perder"</text>
    <rect x="40" y="218" width="820" height="36" rx="6" fill="#fff" stroke="#57534e" stroke-width="2"/>
    <text x="60" y="241" font-weight="bold" fill="#1f1e1c">borda</text><text x="200" y="241" fill="#1f1e1c">ALB + TLS + WAF · Secrets Manager + KMS/HSM</text><text x="700" y="241" fill="#57534e">"quem entra e com o quê"</text>
    <rect x="40" y="260" width="820" height="36" rx="6" fill="#f1efe8" stroke="#8a897f" stroke-width="2"/>
    <text x="60" y="283" font-weight="bold" fill="#444">operação</text><text x="200" y="283" fill="#444">Terraform · GitHub Actions · logs JSON · Prometheus/Grafana · k6</text><text x="700" y="283" fill="#8a897f">"como se prova e se repete"</text>
  </g>
  <text x="450" y="318" text-anchor="middle" font-size="11" fill="#8a897f">a discussão "Docker ou Kubernetes?" é falsa: são camadas diferentes — artefato e execução</text>
</svg>
</div>

Vou percorrer a stack camada por camada. Muito disso já está no repositório; o que eu estou fazendo é explicitar o raciocínio que está implícito no `Dockerfile`, no `docker-compose.yml` e no `main.go`.

### 2.1 Código: Go, e por que o compilador é parte da arquitetura

**Go 1.25.** Binário estático, sem runtime para instalar, consumo de memória baixo — a instância pequena da nuvem serve —, concorrência nativa para o pipeline outbox/relay da Aula 2. Mas o motivo que mais importa para esta aula é uma regra do compilador: o diretório `internal/`. Um pacote dentro de `internal/` só pode ser importado por quem está acima dele na árvore. Isso vai virar, na seção 5, a nossa fronteira de módulo verificada pelo compilador. O gatilho para trocar de linguagem: nunca por moda; talvez para um contexto específico, e a seção 6 vai mostrar qual.

### 2.2 Artefato: Linux dentro de um container

**Linux.** Alpine dentro do container; a distribuição do host é problema do provedor. O `Dockerfile` do repositório diz tudo, e vale desenhar o que ele faz, porque é o desenho que um auditor de segurança quer ver:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 250" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p2-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">O Dockerfile em dois estágios: compilar num lugar, rodar em outro</text>
  <rect x="30" y="60" width="380" height="150" rx="10" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
  <text x="220" y="84" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#1e2a5a">estágio 1 · build — golang:1.25-alpine</text>
  <g font-size="10.5" fill="#1e2a5a" font-family="monospace">
    <text x="50" y="110">COPY go.mod go.sum → go mod download   (cache)</text>
    <text x="50" y="130">COPY . .</text>
    <text x="50" y="150">CGO_ENABLED=0 GOOS=linux go build</text>
    <text x="50" y="170">  -trimpath -ldflags="-s -w" -o /out/app</text>
  </g>
  <text x="220" y="198" text-anchor="middle" font-size="10" fill="#1d4ed8">≈ 400 MB de toolchain — fica aqui, não vai para produção</text>
  <line x1="412" y1="135" x2="478" y2="135" stroke="#57534e" stroke-width="2" marker-end="url(#p2-a)"/>
  <text x="445" y="126" text-anchor="middle" font-size="9.5" fill="#57534e">só o binário</text>
  <rect x="482" y="60" width="390" height="150" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2.5"/>
  <text x="677" y="84" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#04342C">estágio 2 · runtime — alpine:3.20</text>
  <g font-size="10.5" fill="#04342C" font-family="monospace">
    <text x="500" y="110">apk add ca-certificates tzdata curl</text>
    <text x="500" y="130">adduser -D -u 10001 app  →  USER app</text>
    <text x="500" y="150">COPY --from=build /out/app /usr/local/bin/app</text>
    <text x="500" y="170">ENTRYPOINT ["/usr/local/bin/app"]</text>
  </g>
  <text x="677" y="198" text-anchor="middle" font-size="10" fill="#166534">≈ 15 MB · sem shell útil · sem root · superfície mínima</text>
  <text x="450" y="236" text-anchor="middle" font-size="11" fill="#8a897f">o mesmo Dockerfile gera o bacen-sim (ARG CMD) — porque simular o BACEN é simular um sistema de fora</text>
</svg>
</div>

O estágio de build tem a toolchain inteira do Go; o estágio de runtime tem só o binário, os certificados de raiz, os fusos horários e um `curl` para o health check. O processo sobe como o usuário `app`, sem privilégio. Uns quinze megabytes, superfície de ataque mínima, que é exatamente o que a política de segurança cibernética pede. O gatilho: se aparecer dependência em C, trocar Alpine por Debian slim. Nunca voltar a rodar fora de container.

**Docker, sim.** A mesma imagem no laptop dos vinte desenvolvedores, no CI e em produção. Elimina o "na minha máquina funciona". E é a decisão que **mantém as opções abertas**: qualquer orquestrador futuro consome essa mesma imagem. Não há gatilho — container é o piso, não uma fase.

### 2.3 Execução: por que Kubernetes ainda não

Esta é a resposta que mais surpreende, então deixa eu ser preciso, com um desenho do que Kubernetes resolve e do que a TechPix tem:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 320" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">O problema que Kubernetes resolve × o problema que a TechPix tem</text>
  <!-- left: k8s world -->
  <rect x="20" y="50" width="420" height="240" rx="12" fill="none" stroke="#b45309" stroke-width="1.5" stroke-dasharray="7 5"/>
  <text x="230" y="72" text-anchor="middle" font-size="12" font-weight="bold" fill="#412402">muitos serviços heterogêneos</text>
  <g font-size="9.5" text-anchor="middle">
    <rect x="40" y="90" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="75" y="109" fill="#412402">api ×3</text>
    <rect x="120" y="90" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="155" y="109" fill="#412402">risco ×8</text>
    <rect x="200" y="90" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="235" y="109" fill="#412402">worker ×2</text>
    <rect x="280" y="90" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="315" y="109" fill="#412402">gateway</text>
    <rect x="360" y="90" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="395" y="109" fill="#412402">…</text>
    <rect x="40" y="130" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="75" y="149" fill="#412402">ml (GPU)</text>
    <rect x="120" y="130" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="155" y="149" fill="#412402">notif ×2</text>
    <rect x="200" y="130" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="235" y="149" fill="#412402">recon</text>
    <rect x="280" y="130" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="315" y="149" fill="#412402">cron</text>
    <rect x="360" y="130" width="70" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="395" y="149" fill="#412402">…</text>
  </g>
  <g font-size="10.5" fill="#412402">
    <text x="40" y="190">precisa de: placement (qual nó?), service discovery,</text>
    <text x="40" y="208">rollout independente por serviço, autoscaling por serviço,</text>
    <text x="40" y="226">rede entre pods, segredos por serviço, um time cuidando do cluster</text>
  </g>
  <text x="230" y="262" text-anchor="middle" font-size="11" font-weight="bold" fill="#b45309">Kubernetes se paga aqui</text>
  <text x="230" y="280" text-anchor="middle" font-size="10" fill="#8a897f">+ ≈ R$ 400/mês de control plane + a curva de aprendizado</text>
  <!-- right: techpix -->
  <rect x="470" y="50" width="410" height="240" rx="12" fill="none" stroke="#534AB7" stroke-width="1.5" stroke-dasharray="7 5"/>
  <text x="675" y="72" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">um serviço</text>
  <rect x="590" y="95" width="170" height="60" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="675" y="120" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">techpix ×1</text>
  <text x="675" y="140" text-anchor="middle" font-size="10" fill="#26215C">(×2 na Fase 1)</text>
  <g font-size="10.5" fill="#26215C">
    <text x="490" y="190">precisa de: subir o container, reiniciar se cair,</text>
    <text x="490" y="208">health check, rolar a versão nova, ler um segredo</text>
    <text x="490" y="226">→ ECS/Fargate faz isso; uma VM com systemd também</text>
  </g>
  <text x="675" y="262" text-anchor="middle" font-size="11" font-weight="bold" fill="#534AB7">Kubernetes aqui é custo sem benefício</text>
  <text x="675" y="280" text-anchor="middle" font-size="10" fill="#8a897f">gatilho: 3º serviço extraído, ou autoscaling independente</text>
  <text x="450" y="310" text-anchor="middle" font-size="11" fill="#8a897f">a imagem Docker é a mesma nos dois mundos — por isso a migração, quando vier, é um sprint</text>
</svg>
</div>

Kubernetes resolve o problema de *muitos* serviços heterogêneos que precisam de placement, service discovery e rollout independentes. A TechPix tem **um** serviço. O que ganharíamos hoje seria uma curva de aprendizado para vinte pessoas que precisam entregar Pix, e algo como R$ 400 por mês de plano de controle. O que temos hoje: um container em ECS/Fargate, ou uma VM Linux com `systemd` e o próprio compose. O gatilho é objetivo: **o terceiro serviço extraído**, ou o primeiro contexto que precise de autoscaling independente. E quando o gatilho disparar, a migração é um sprint, porque a imagem já existe. Reparem: Docker sem Kubernetes não é contradição. Docker faz o *artefato* ser o mesmo em todo lugar; Kubernetes *coordena muitos artefatos*. A gente tem um.

### 2.4 Dados: um banco, quatro schemas, nenhum broker

**PostgreSQL 17, gerenciado, Multi-AZ, um cluster, um schema por contexto.** O ADR-001 exige que reservar fundos e registrar a idempotência aconteçam na mesma transação — o ledger é ACID, serializable, append-only. Um banco só é o que torna isso trivial; entre processos, seria 2PC ou saga. E os schemas separados — `identidade`, `limites`, `devolucoes`, cada um sem chave estrangeira para fora — já desenham o corte futuro, sem executá-lo. O gatilho: um contexto extraído leva o schema dele para um banco próprio, o que é assunto da Aula 6. O ledger fica.

**Migrations: SQL embutido no binário**, aplicado no boot (`migrations/embed.go`). A versão do schema anda com a versão do código, sem ferramenta externa. O gatilho: no dia em que houver dois deploys independentes escrevendo no mesmo banco, migration vira um pipeline separado.

**Mensageria: nenhum broker.** Esta é a segunda resposta que surpreende, e ela merece um desenho porque é o exemplo mais limpo de "gatilho escrito":

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p2-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Outbox no Postgres hoje — o broker entra só quando houver consumidor fora do processo</text>
  <!-- today -->
  <text x="220" y="58" text-anchor="middle" font-size="12" font-weight="bold" fill="#57534e">hoje (Fase 0)</text>
  <rect x="30" y="70" width="380" height="200" rx="12" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="220" y="92" text-anchor="middle" font-size="11" fill="#26215C">processo techpix</text>
  <rect x="50" y="105" width="100" height="40" rx="6" fill="#fff" stroke="#534AB7"/><text x="100" y="129" text-anchor="middle" font-size="10.5" fill="#26215C">pix (produtor)</text>
  <line x1="152" y1="125" x2="188" y2="125" stroke="#57534e" stroke-width="2" marker-end="url(#p2-b)"/>
  <rect x="192" y="105" width="100" height="40" rx="6" fill="#E1F5EE" stroke="#166534"/><text x="242" y="123" text-anchor="middle" font-size="10" fill="#04342C">tabela outbox</text><text x="242" y="137" text-anchor="middle" font-size="8.5" fill="#166534">mesma transação</text>
  <line x1="294" y1="125" x2="330" y2="125" stroke="#57534e" stroke-width="2" marker-end="url(#p2-b)"/>
  <rect x="334" y="105" width="60" height="40" rx="6" fill="#fff" stroke="#534AB7"/><text x="364" y="129" text-anchor="middle" font-size="10" fill="#26215C">relay</text>
  <path d="M364,147 L364,175 L242,175 L242,200" fill="none" stroke="#57534e" stroke-width="2" marker-end="url(#p2-b)"/>
  <rect x="150" y="204" width="184" height="40" rx="6" fill="#fff" stroke="#534AB7"/><text x="242" y="222" text-anchor="middle" font-size="10" fill="#26215C">limites · statement · feed</text><text x="242" y="236" text-anchor="middle" font-size="8.5" fill="#5a55a0">consumidores no mesmo processo</text>
  <text x="220" y="262" text-anchor="middle" font-size="10" fill="#534AB7">zero infra nova · evento garantido pela transação</text>
  <!-- trigger -->
  <line x1="420" y1="170" x2="470" y2="170" stroke="#b45309" stroke-width="2.5" marker-end="url(#p2-b)"/>
  <text x="445" y="160" text-anchor="middle" font-size="9.5" fill="#b45309">gatilho</text>
  <!-- future -->
  <text x="680" y="58" text-anchor="middle" font-size="12" font-weight="bold" fill="#57534e">quando o 1º consumidor sair do processo (Fase 2)</text>
  <rect x="490" y="70" width="240" height="120" rx="12" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="610" y="92" text-anchor="middle" font-size="11" fill="#26215C">processo techpix</text>
  <rect x="505" y="105" width="90" height="40" rx="6" fill="#fff" stroke="#534AB7"/><text x="550" y="129" text-anchor="middle" font-size="10.5" fill="#26215C">pix</text>
  <line x1="597" y1="125" x2="623" y2="125" stroke="#57534e" stroke-width="2" marker-end="url(#p2-b)"/>
  <rect x="627" y="105" width="90" height="40" rx="6" fill="#E1F5EE" stroke="#166534"/><text x="672" y="129" text-anchor="middle" font-size="10" fill="#04342C">outbox</text>
  <text x="610" y="172" text-anchor="middle" font-size="9.5" fill="#5a55a0">o produtor não muda uma linha</text>
  <line x1="672" y1="147" x2="672" y2="200" stroke="#57534e" stroke-width="2" marker-end="url(#p2-b)"/>
  <rect x="600" y="204" width="145" height="36" rx="6" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/><text x="672" y="226" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#412402">tópico (broker)</text>
  <line x1="747" y1="222" x2="785" y2="222" stroke="#57534e" stroke-width="2" marker-end="url(#p2-b)"/>
  <rect x="789" y="204" width="95" height="36" rx="6" fill="#FAEEDA" stroke="#b45309"/><text x="836" y="226" text-anchor="middle" font-size="10" fill="#412402">antifraude</text>
  <text x="836" y="252" text-anchor="middle" font-size="8.5" fill="#b45309">outro processo</text>
  <text x="690" y="280" text-anchor="middle" font-size="10" fill="#b45309">+ ≈ R$ 1.500/mês e uma disciplina operacional inteira</text>
</svg>
</div>

A Aula 2 mostrou que a outbox transacional garante que o evento existe se a transação existiu; um consumidor no mesmo processo não precisa de Kafka. Kafka gerenciado custa na casa de R$ 1.500 por mês e é uma disciplina operacional inteira — partições, retenção, consumer groups, rebalanceamento. O gatilho: o **primeiro consumidor fora do processo**. Nesse dia a tabela de outbox vira a fonte de um tópico, sem mudar o produtor — é a beleza do padrão, e é por isso que ele foi escolhido na Aula 2 mesmo sem broker.

**Cache: em memória, no processo.** O cache do DICT com TTL já existe. Cache distribuído resolve um problema que ainda não temos, porque temos uma réplica. O gatilho: a segunda réplica da aplicação.

### 2.5 Borda, segredos, operação

**Borda: load balancer gerenciado com TLS e WAF.** Terminação TLS, health check no `/healthz` que já existe, proteção básica. É o item mais barato da lista e o primeiro que uma auditoria pergunta. Gateway ou BFF só quando houver mais de um serviço atrás — e isso é assunto da aula de integração.

**Segredos e chaves: gerenciador de segredos e KMS; o certificado ICP-Brasil que assina mensagens para o SPI mora num HSM gerenciado.** Chave privada de assinatura **nunca** vive em variável de ambiente. Isso não é preferência; é exigência de segurança cibernética. Sem gatilho.

**Observabilidade: `slog` em JSON para o serviço de logs; métricas no formato Prometheus; tracing só dentro do processo.** O `main.go` já loga JSON estruturado, e o p99 do caminho de pagamento já é uma fitness function (`P99_ALVO_MS`). O gatilho para tracing distribuído é o dia em que a chamada em memória virar rede — Aula 7.

**Infraestrutura como código: Terraform desde o primeiro dia.** O regulador pergunta "como você reconstrói isso?". A resposta tem que ser um repositório, não uma pessoa.

**CI/CD: a cada pull request, `go test ./...` e `make test-arch`; build da imagem; deploy com aprovação.** Os testes de arquitetura da seção 5 só valem se rodarem no PR. Uma fronteira que ninguém verifica evapora em seis semanas. O pipeline inteiro cabe num desenho, e eu quero que vocês reparem em *onde* a arquitetura é verificada:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 200" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p2-c" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">O pipeline — a arquitetura é verificada antes de qualquer imagem existir</text>
  <g font-size="10.5" text-anchor="middle">
    <rect x="20" y="70" width="110" height="60" rx="8" fill="#fff" stroke="#57534e" stroke-width="2"/><text x="75" y="96" font-weight="bold" fill="#1f1e1c">pull request</text><text x="75" y="114" fill="#57534e">1 dos 20 devs</text>
    <line x1="132" y1="100" x2="158" y2="100" stroke="#57534e" stroke-width="2" marker-end="url(#p2-c)"/>
    <rect x="162" y="70" width="130" height="60" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/><text x="227" y="90" font-weight="bold" fill="#26215C">make test-arch</text><text x="227" y="106" fill="#26215C">contextos · linguagem</text><text x="227" y="120" fill="#26215C">contratos · schema · specs</text>
    <line x1="294" y1="100" x2="320" y2="100" stroke="#57534e" stroke-width="2" marker-end="url(#p2-c)"/>
    <rect x="324" y="70" width="120" height="60" rx="8" fill="#E1F5EE" stroke="#166534" stroke-width="2"/><text x="384" y="96" font-weight="bold" fill="#04342C">go test ./...</text><text x="384" y="114" fill="#04342C">domínio, no Postgres</text>
    <line x1="446" y1="100" x2="472" y2="100" stroke="#57534e" stroke-width="2" marker-end="url(#p2-c)"/>
    <rect x="476" y="70" width="120" height="60" rx="8" fill="#fff" stroke="#57534e" stroke-width="2"/><text x="536" y="96" font-weight="bold" fill="#1f1e1c">docker build</text><text x="536" y="114" fill="#57534e">imagem + tag do commit</text>
    <line x1="598" y1="100" x2="624" y2="100" stroke="#57534e" stroke-width="2" marker-end="url(#p2-c)"/>
    <rect x="628" y="70" width="120" height="60" rx="8" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/><text x="688" y="96" font-weight="bold" fill="#412402">aprovação</text><text x="688" y="114" fill="#412402">4 olhos (regulador gosta)</text>
    <line x1="750" y1="100" x2="776" y2="100" stroke="#57534e" stroke-width="2" marker-end="url(#p2-c)"/>
    <rect x="780" y="70" width="100" height="60" rx="8" fill="#fff" stroke="#57534e" stroke-width="2"/><text x="830" y="96" font-weight="bold" fill="#1f1e1c">deploy</text><text x="830" y="114" fill="#57534e">ECS · Terraform</text>
  </g>
  <text x="227" y="160" text-anchor="middle" font-size="10" fill="#534AB7">segundos, sem banco — falha aqui custa quase nada</text>
  <text x="620" y="160" text-anchor="middle" font-size="10" fill="#8a897f">falha em produção custa uma comunicação ao BACEN</text>
  <text x="450" y="188" text-anchor="middle" font-size="11" fill="#8a897f">quanto mais à esquerda a verificação, mais barato o erro — é a mesma lógica das três camadas da seção 5</text>
</svg>
</div>

**Ensaio de carga: k6**, com o `scripts/k6_degrau.js` que reproduz o degrau da Aula 2. Medir antes de dimensionar.

### 2.6 A topologia do dia 1, inteira

Juntando tudo:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 360" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="m4d-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Topologia do dia 1 na AWS (região de São Paulo)</text>
  <text x="60" y="132" text-anchor="middle" font-size="12" fill="#57534e">app / web</text>
  <text x="60" y="150" text-anchor="middle" font-size="12" fill="#57534e">dos clientes</text>
  <line x1="100" y1="140" x2="150" y2="140" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-b)"/>
  <rect x="155" y="105" width="120" height="70" rx="10" fill="#fff" stroke="#57534e" stroke-width="2"/>
  <text x="215" y="134" text-anchor="middle" font-size="13" font-weight="bold" fill="#1f1e1c">ALB + WAF</text>
  <text x="215" y="156" text-anchor="middle" font-size="11" fill="#57534e">TLS · /healthz</text>
  <line x1="277" y1="140" x2="322" y2="140" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-b)"/>
  <rect x="330" y="60" width="540" height="270" rx="12" fill="none" stroke="#8a897f" stroke-width="1.5" stroke-dasharray="7 5"/>
  <text x="345" y="80" font-size="11" fill="#8a897f">VPC privada · duas zonas de disponibilidade</text>
  <rect x="345" y="100" width="230" height="90" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="460" y="126" text-anchor="middle" font-size="13" font-weight="bold" fill="#26215C">techpix (1 container)</text>
  <text x="460" y="148" text-anchor="middle" font-size="11" fill="#26215C">ECS/Fargate ou 1 VM Linux</text>
  <text x="460" y="168" text-anchor="middle" font-size="11" fill="#26215C">15 módulos · relay da outbox dentro</text>
  <rect x="345" y="200" width="230" height="46" rx="10" fill="#fff" stroke="#534AB7" stroke-width="1.5" stroke-dasharray="6 4"/>
  <text x="460" y="228" text-anchor="middle" font-size="11" fill="#5a55a0">2ª réplica: liga quando o cache sair do processo</text>
  <rect x="620" y="100" width="230" height="90" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2.5"/>
  <text x="735" y="126" text-anchor="middle" font-size="13" font-weight="bold" fill="#04342C">RDS PostgreSQL 17</text>
  <text x="735" y="148" text-anchor="middle" font-size="11" fill="#04342C">Multi-AZ · backup automático</text>
  <text x="735" y="168" text-anchor="middle" font-size="11" fill="#04342C">public · identidade · limites · devolucoes</text>
  <line x1="577" y1="145" x2="616" y2="145" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-b)"/>
  <rect x="620" y="200" width="230" height="46" rx="10" fill="#fff" stroke="#8a897f" stroke-width="1.5"/>
  <text x="735" y="228" text-anchor="middle" font-size="11" fill="#57534e">Secrets Manager · KMS/HSM · CloudWatch</text>
  <rect x="345" y="262" width="505" height="52" rx="10" fill="#FDE7EC" stroke="#be123c" stroke-width="2"/>
  <text x="597" y="284" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#5a1e2b">BACEN — DICT + SPI via PSTI ou participante direto (RSFN)</text>
  <text x="597" y="304" text-anchor="middle" font-size="10.5" fill="#5a1e2b">o único vizinho que já é "outro sistema" hoje — e por isso já está atrás de uma ACL (módulo bacen)</text>
  <line x1="460" y1="192" x2="460" y2="258" stroke="#be123c" stroke-width="2" marker-end="url(#m4d-b)"/>
</svg>
</div>

Um container, um banco gerenciado, uma borda gerenciada. Nada de Kubernetes, broker ou cache distribuído. Cada caixa tracejada do desenho é um gatilho da lista acima esperando para disparar — e é assim que eu quero que vocês desenhem a infraestrutura de vocês: com as ausências nomeadas, cada uma com a condição que a transforma em presença.

---

## 3. O monólito por dentro: o que os vinte desenvolvedores realmente têm

Antes de discutir se cortamos, vamos olhar o que existe. Não um diagrama: o código.

```bash
ls internal/modules/
# accounts bacen devolucoes feed filas idempotency identidade ledger limites loadgen outbox pix reconcile statement ui
sed -n '100,180p' cmd/techpix/main.go   # a função de composição: quem depende de quem, numa tela
```

Quinze diretórios. Cada um é um pacote Go com um `api.go` — o contrato público — e um `internal/` — o que ninguém de fora enxerga. E a regra não é convenção: importar `ledger/internal/store` a partir de `pix` **não compila**. Vale desenhar exatamente o que o compilador permite e o que ele proíbe, porque é a ideia mais importante desta seção:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 290" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p3-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#166534"/></marker><marker id="p3-x" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#be123c"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">A regra do internal/: a fronteira que o compilador de Go impõe</text>
  <!-- pix module -->
  <rect x="40" y="70" width="260" height="180" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="170" y="94" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#26215C">internal/modules/pix</text>
  <rect x="60" y="110" width="220" height="34" rx="6" fill="#fff" stroke="#534AB7"/><text x="170" y="132" text-anchor="middle" font-size="11" font-family="monospace" fill="#26215C">api.go · module.go</text>
  <rect x="60" y="154" width="220" height="80" rx="6" fill="#f6f5ff" stroke="#534AB7" stroke-dasharray="4 3"/>
  <text x="170" y="174" text-anchor="middle" font-size="10.5" font-family="monospace" fill="#5a55a0">internal/store</text>
  <text x="170" y="192" text-anchor="middle" font-size="10.5" font-family="monospace" fill="#5a55a0">internal/risco</text>
  <text x="170" y="222" text-anchor="middle" font-size="9.5" fill="#5a55a0">só pix enxerga</text>
  <!-- ledger module -->
  <rect x="600" y="70" width="260" height="180" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="730" y="94" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#04342C">internal/modules/ledger</text>
  <rect x="620" y="110" width="220" height="34" rx="6" fill="#fff" stroke="#166534"/><text x="730" y="132" text-anchor="middle" font-size="11" font-family="monospace" fill="#04342C">api.go — RegistrarTx(...)</text>
  <rect x="620" y="154" width="220" height="80" rx="6" fill="#eefaf4" stroke="#166534" stroke-dasharray="4 3"/>
  <text x="730" y="174" text-anchor="middle" font-size="10.5" font-family="monospace" fill="#166534">internal/store</text>
  <text x="730" y="192" text-anchor="middle" font-size="10" fill="#166534">INSERT INTO entries …</text>
  <text x="730" y="222" text-anchor="middle" font-size="9.5" fill="#166534">só ledger enxerga</text>
  <!-- allowed -->
  <line x1="302" y1="127" x2="616" y2="127" stroke="#166534" stroke-width="2.5" marker-end="url(#p3-a)"/>
  <text x="459" y="118" text-anchor="middle" font-size="11" font-weight="bold" fill="#166534">✓ compila — pela interface pública</text>
  <!-- forbidden -->
  <line x1="302" y1="194" x2="616" y2="194" stroke="#be123c" stroke-width="2.5" stroke-dasharray="6 4" marker-end="url(#p3-x)"/>
  <text x="459" y="185" text-anchor="middle" font-size="11" font-weight="bold" fill="#be123c">✗ não compila — "use of internal package not allowed"</text>
  <text x="459" y="212" text-anchor="middle" font-size="10" fill="#be123c">pix jamais escreve em entries pelas costas do ledger</text>
  <text x="450" y="272" text-anchor="middle" font-size="11" fill="#8a897f">isso não é lint, nem convenção de time: é erro de compilação — a fronteira mais barata que existe</text>
</svg>
</div>

Ninguém escreve na tabela de lançamentos pelas costas do ledger, não por disciplina, mas por compilador. Isso é o ADR-002, "monólito modular, com fronteiras verificadas pelo compilador", e eu quero que vocês notem a data dele: foi escrito na Aula 1, quando decidimos começar pequeno, e já dizia em que condições seria revisto.

As dependências entre módulos são declaradas por interface e ligadas num único lugar, a função de composição do `main.go`. Ela cabe numa tela, e o ADR diz explicitamente: se ela ficar difícil de ler, a arquitetura azedou. Vale desenhar o que ela liga, porque é a versão "de código" do context map que vem na seção 4:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 360" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p3-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">O grafo de composição do main.go — quem recebe quem no construtor</text>
  <g font-size="10.5" text-anchor="middle">
    <!-- platform row -->
    <rect x="30" y="60" width="90" height="34" rx="6" fill="#f1efe8" stroke="#8a897f"/><text x="75" y="82" fill="#444">db (pg)</text>
    <rect x="140" y="60" width="90" height="34" rx="6" fill="#f1efe8" stroke="#8a897f"/><text x="185" y="82" fill="#444">outbox</text>
    <rect x="250" y="60" width="100" height="34" rx="6" fill="#f1efe8" stroke="#8a897f"/><text x="300" y="82" fill="#444">idempotency</text>
    <rect x="370" y="60" width="90" height="34" rx="6" fill="#f1efe8" stroke="#8a897f"/><text x="415" y="82" fill="#444">knobs</text>
    <!-- core row -->
    <rect x="30" y="150" width="90" height="34" rx="6" fill="#E1F5EE" stroke="#166534" stroke-width="2"/><text x="75" y="172" fill="#04342C">ledger</text>
    <rect x="140" y="150" width="90" height="34" rx="6" fill="#E3ECFD" stroke="#1d4ed8"/><text x="185" y="172" fill="#1e2a5a">identidade</text>
    <rect x="250" y="150" width="100" height="34" rx="6" fill="#EEEDFE" stroke="#534AB7"/><text x="300" y="172" fill="#26215C">limites</text>
    <rect x="370" y="150" width="90" height="34" rx="6" fill="#FDE7EC" stroke="#be123c"/><text x="415" y="172" fill="#5a1e2b">bacen (ACL)</text>
    <rect x="520" y="150" width="90" height="34" rx="6" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/><text x="565" y="172" fill="#26215C">pix</text>
    <!-- downstream row -->
    <rect x="30" y="250" width="90" height="34" rx="6" fill="#E1F5EE" stroke="#166534"/><text x="75" y="272" fill="#04342C">accounts</text>
    <rect x="140" y="250" width="90" height="34" rx="6" fill="#E1F5EE" stroke="#166534"/><text x="185" y="272" fill="#04342C">statement</text>
    <rect x="370" y="250" width="90" height="34" rx="6" fill="#EEEDFE" stroke="#534AB7"/><text x="415" y="272" fill="#26215C">reconcile</text>
    <rect x="480" y="250" width="80" height="34" rx="6" fill="#EEEDFE" stroke="#534AB7"/><text x="520" y="272" fill="#26215C">feed</text>
    <rect x="600" y="250" width="100" height="34" rx="6" fill="#E1F5EE" stroke="#166534"/><text x="650" y="272" fill="#04342C">devolucoes</text>
  </g>
  <g stroke="#57534e" stroke-width="1.5" fill="none" marker-end="url(#p3-b)">
    <!-- ledger <- db, outbox -->
    <line x1="75" y1="96" x2="75" y2="146"/><line x1="185" y1="96" x2="100" y2="146"/>
    <!-- limites <- identidade, outbox -->
    <line x1="230" y1="167" x2="246" y2="167"/><line x1="200" y1="96" x2="285" y2="146"/>
    <!-- pix <- ledger, idempotency, bacen -->
    <path d="M120,160 C300,120 420,120 518,158"/><line x1="320" y1="96" x2="545" y2="146"/><line x1="462" y1="167" x2="516" y2="167"/>
    <!-- accounts <- ledger, idem -->
    <line x1="75" y1="186" x2="75" y2="246"/>
    <!-- statement <- ledger -->
    <line x1="100" y1="186" x2="165" y2="246"/>
    <!-- reconcile <- pix, bacen -->
    <line x1="545" y1="186" x2="440" y2="246"/><line x1="415" y1="186" x2="415" y2="246"/>
    <!-- feed <- pix -->
    <line x1="560" y1="186" x2="525" y2="246"/>
    <!-- devolucoes <- ledger, pix, outbox -->
    <line x1="585" y1="186" x2="635" y2="246"/><path d="M120,175 C300,230 500,215 600,262"/>
  </g>
  <text x="640" y="72" font-size="10" fill="#8a897f">↑ plataforma: todo mundo usa,</text>
  <text x="640" y="86" font-size="10" fill="#8a897f">ela não usa ninguém</text>
  <text x="640" y="166" font-size="10" fill="#8a897f">← o ledger é o upstream</text>
  <text x="640" y="180" font-size="10" fill="#8a897f">de quase tudo</text>
  <text x="720" y="272" font-size="10" fill="#8a897f">← a borda: só leem ou derivam</text>
  <text x="450" y="330" text-anchor="middle" font-size="11" fill="#8a897f">nenhuma seta sobe: dependência só desce ou anda para o lado — e cada seta nova exige mudar o mapa e escrever um ADR</text>
</svg>
</div>

Reparem no formato do grafo: a plataforma em cima, usada por todos e sem usar ninguém; o ledger como upstream de quase tudo; a borda embaixo, só lendo ou derivando. Nenhuma seta sobe. O ADR-005 é explícito: uma seta nova aqui exige mudar o mapa de contextos **e** escrever um ADR, porque mudar dependência é mudar arquitetura.

Os quinze módulos não são quinze coisas soltas. Eles se agrupam — e o agrupamento é o resultado da seção 4, mas eu vou mostrar o resultado antes, para vocês terem o mapa na cabeça:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 420" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Um binário, quinze módulos, cinco contextos + plataforma</text>
  <rect x="20" y="45" width="860" height="355" rx="14" fill="#fff" stroke="#1f1e1c" stroke-width="2.5"/>
  <text x="40" y="68" font-size="12" font-weight="bold" fill="#1f1e1c">cmd/techpix — processo único</text>
  <rect x="40" y="85" width="260" height="95" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="170" y="108" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#26215C">Contas e Ledger · core</text>
  <text x="170" y="132" text-anchor="middle" font-size="11.5" fill="#26215C">ledger · accounts · statement</text>
  <text x="170" y="156" text-anchor="middle" font-size="10.5" fill="#5a55a0">TransacaoRegistrada · FundosReservados</text>
  <rect x="320" y="85" width="260" height="95" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="450" y="108" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#26215C">Pagamentos (Pix) · core</text>
  <text x="450" y="132" text-anchor="middle" font-size="11.5" fill="#26215C">pix · bacen (ACL) · reconcile · feed</text>
  <text x="450" y="156" text-anchor="middle" font-size="10.5" fill="#5a55a0">PixIniciado … PixLiquidado · PixEstornado</text>
  <rect x="600" y="85" width="260" height="95" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="730" y="108" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#26215C">Antifraude e Limites · core</text>
  <text x="730" y="132" text-anchor="middle" font-size="11.5" fill="#26215C">limites</text>
  <text x="730" y="156" text-anchor="middle" font-size="10.5" fill="#5a55a0">LimitesValidados</text>
  <rect x="40" y="200" width="260" height="80" rx="10" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
  <text x="170" y="223" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#1e2a5a">Identidade e Onboarding · generic</text>
  <text x="170" y="246" text-anchor="middle" font-size="11.5" fill="#1e2a5a">identidade</text>
  <text x="170" y="267" text-anchor="middle" font-size="10.5" fill="#1e2a5a">comprar KYC; só a política é nossa</text>
  <rect x="320" y="200" width="260" height="80" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="450" y="223" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#04342C">Devoluções e Disputas · supporting</text>
  <text x="450" y="246" text-anchor="middle" font-size="11.5" fill="#04342C">devolucoes</text>
  <text x="450" y="267" text-anchor="middle" font-size="10.5" fill="#04342C">PixDevolvido · construído simples</text>
  <rect x="600" y="200" width="260" height="80" rx="10" fill="#f1efe8" stroke="#8a897f" stroke-width="2"/>
  <text x="730" y="223" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#444">Plataforma · não é domínio</text>
  <text x="730" y="246" text-anchor="middle" font-size="11.5" fill="#444">outbox · idempotency · filas</text>
  <text x="730" y="267" text-anchor="middle" font-size="11.5" fill="#444">loadgen · ui</text>
  <rect x="40" y="305" width="820" height="80" rx="10" fill="#fff" stroke="#166534" stroke-width="2.5"/>
  <text x="450" y="330" text-anchor="middle" font-size="13" font-weight="bold" fill="#04342C">PostgreSQL — um cluster, quatro schemas</text>
  <text x="450" y="353" text-anchor="middle" font-size="11" fill="#04342C">public (ledger, pix — herdados, com uma FK de dívida anotada) · identidade · limites · devolucoes</text>
  <text x="450" y="373" text-anchor="middle" font-size="10.5" fill="#8a897f">nenhuma FK atravessa contexto; referência por identidade (código da carteira, E2E ID, id do cliente)</text>
</svg>
</div>

Cinco contextos e uma plataforma. As cores são o tipo de subdomínio, uma ideia do DDD estratégico que eu vou usar o dia inteiro: roxo é core, o que se constrói em casa com o melhor time; azul é genérico, o que se compra; verde é de suporte, o que se constrói simples; cinza é plataforma, o que não é domínio e não pode carregar regra de negócio. (Uma provocação honesta: Pagamentos é core mesmo? O `pacs.008` é igual para todos os participantes — o Banco Central dita formato, prazo e semântica; ninguém ganha mercado por orquestrar o Pix melhor. Dá para defender que é *supporting*. O repositório o marca como *core* porque a orquestração DICT/SPI é o produto. As duas leituras são defensáveis, e é exatamente o tipo de discussão que vale a sala.)

E agora a observação que liga isso à pergunta da reunião. **Vinte pessoas, cinco contextos.** Isso já é um organograma:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p3-c" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Inverse Conway Maneuver: o organograma desenhado a partir dos contextos</text>
  <g font-size="11" text-anchor="middle">
    <!-- squad 1 -->
    <rect x="30" y="60" width="195" height="120" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
    <text x="127" y="82" font-weight="bold" fill="#26215C">Squad Ledger · 5</text>
    <text x="127" y="100" font-size="9.5" fill="#5a55a0">complicated-subsystem</text>
    <g fill="#534AB7"><circle cx="87" cy="122" r="7"/><circle cx="107" cy="122" r="7"/><circle cx="127" cy="122" r="7"/><circle cx="147" cy="122" r="7"/><circle cx="167" cy="122" r="7"/></g>
    <text x="127" y="150" font-size="10" fill="#26215C">Contas e Ledger</text>
    <text x="127" y="166" font-size="9.5" fill="#5a55a0">X-as-a-Service para todos</text>
    <!-- squad 2 -->
    <rect x="245" y="60" width="195" height="120" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
    <text x="342" y="82" font-weight="bold" fill="#26215C">Squad Pix · 5</text>
    <text x="342" y="100" font-size="9.5" fill="#5a55a0">stream-aligned</text>
    <g fill="#534AB7"><circle cx="302" cy="122" r="7"/><circle cx="322" cy="122" r="7"/><circle cx="342" cy="122" r="7"/><circle cx="362" cy="122" r="7"/><circle cx="382" cy="122" r="7"/></g>
    <text x="342" y="150" font-size="10" fill="#26215C">Pagamentos + ACL BACEN</text>
    <text x="342" y="166" font-size="9.5" fill="#5a55a0">colabora com Limites (declarado)</text>
    <!-- squad 3 -->
    <rect x="460" y="60" width="195" height="120" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
    <text x="557" y="82" font-weight="bold" fill="#26215C">Squad Risco · 5</text>
    <text x="557" y="100" font-size="9.5" fill="#5a55a0">stream-aligned</text>
    <g fill="#534AB7"><circle cx="517" cy="122" r="7"/><circle cx="537" cy="122" r="7"/><circle cx="557" cy="122" r="7"/><circle cx="577" cy="122" r="7"/><circle cx="597" cy="122" r="7"/></g>
    <text x="557" y="150" font-size="10" fill="#26215C">Antifraude e Limites</text>
    <text x="557" y="166" font-size="9.5" fill="#5a55a0">1º candidato a serviço (seção 6)</text>
    <!-- squad 4 -->
    <rect x="675" y="60" width="195" height="120" rx="10" fill="#f1efe8" stroke="#8a897f" stroke-width="2"/>
    <text x="772" y="82" font-weight="bold" fill="#444">Squad Plataforma · 5</text>
    <text x="772" y="100" font-size="9.5" fill="#666">platform</text>
    <g fill="#8a897f"><circle cx="732" cy="122" r="7"/><circle cx="752" cy="122" r="7"/><circle cx="772" cy="122" r="7"/><circle cx="792" cy="122" r="7"/><circle cx="812" cy="122" r="7"/></g>
    <text x="772" y="150" font-size="10" fill="#444">outbox · idempotency · infra</text>
    <text x="772" y="166" font-size="9.5" fill="#666">+ Identidade e Devoluções (leves)</text>
  </g>
  <!-- conway arrow -->
  <rect x="200" y="215" width="500" height="50" rx="10" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/>
  <text x="450" y="236" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#412402">Lei de Conway: o sistema vai espelhar a comunicação dos times</text>
  <text x="450" y="254" text-anchor="middle" font-size="10.5" fill="#412402">então desenhe os times a partir das fronteiras que a modelagem descobriu — não o contrário</text>
  <text x="450" y="288" text-anchor="middle" font-size="10.5" fill="#8a897f">o campo <tspan font-family="monospace">Equipe</tspan> de cada contexto em <tspan font-family="monospace">contextos.go</tspan> é exatamente isto, escrito como código</text>
</svg>
</div>

Um squad para cada contexto core — três —, e um squad de plataforma que também cuida de Identidade e Devoluções, que são leves. Quatro squads de cinco. A Lei de Conway — a organização sempre vence o diagrama; o sistema espelha a estrutura de comunicação de quem o constrói — diz que a arquitetura vai convergir para o organograma de qualquer jeito. Então é melhor desenhar o organograma *a partir* dos contextos do que o contrário — o *Inverse Conway Maneuver* —, e isso está literalmente escrito no campo `Equipe` de cada contexto em `internal/platform/contextos/contextos.go`.

Reparem que a pergunta "vamos quebrar em serviços?" ainda não foi respondida. Mas ela já ficou mais precisa: virou "quais destes cinco contextos, se algum, precisam de um processo próprio?". E para responder isso, precisamos ter certeza de que os cinco são os cinco certos.

---
## 4. Modelar antes de cortar: o event storming que desenha as fronteiras

Aqui entra o tema da aula. Domain-Driven Design tem um vocabulário grande — linguagem ubíqua, bounded context, agregado, evento de domínio, mapa de contexto — e eu vou apresentar cada peça no momento em que a reunião precisar dela, não antes. A pergunta que a reunião colocou na frente de tudo é: **se a gente for cortar, onde a gente corta?**

A frase "vamos quebrar em microsserviços" tem um pressuposto escondido: que a gente sabe onde estão as linhas. Na Aula 2 eu confessei que os módulos da TechPix foram desenhados no olho. Funcionou — as fronteiras de módulo quebravam o build — mas ninguém sabia dizer *por que aquela linha e não outra*. E o incidente que abre o repositório mostra o custo de não saber.

### 4.1 O bug que mora entre dois times

```bash
make demo-duas-carteiras
```

A Ana tem duas carteiras. O limite diário é R$ 1.000. O time de risco avaliava o limite "por conta"; para o ledger, "conta" é o pote contábil — a carteira. Vale desenhar o que cada time via, porque o bug fica óbvio no desenho e invisível no código:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p4-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">A palavra "conta": o que cada time via — e por onde a Ana passou duas vezes</text>
  <!-- Ana -->
  <circle cx="80" cy="150" r="22" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
  <text x="80" y="155" text-anchor="middle" font-size="11" font-weight="bold" fill="#1e2a5a">Ana</text>
  <text x="80" y="190" text-anchor="middle" font-size="10" fill="#1e2a5a">1 pessoa (CPF)</text>
  <line x1="104" y1="140" x2="160" y2="105" stroke="#57534e" stroke-width="2" marker-end="url(#p4-a)"/>
  <line x1="104" y1="160" x2="160" y2="195" stroke="#57534e" stroke-width="2" marker-end="url(#p4-a)"/>
  <!-- wallets -->
  <rect x="165" y="80" width="150" height="50" rx="8" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="240" y="100" text-anchor="middle" font-size="11" font-weight="bold" fill="#04342C">carteira:ana</text>
  <text x="240" y="118" text-anchor="middle" font-size="10" fill="#04342C">conta PASSIVO no ledger</text>
  <rect x="165" y="170" width="150" height="50" rx="8" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="240" y="190" text-anchor="middle" font-size="11" font-weight="bold" fill="#04342C">carteira:ana2</text>
  <text x="240" y="208" text-anchor="middle" font-size="10" fill="#04342C">outra conta PASSIVO</text>
  <!-- limite por carteira -->
  <rect x="380" y="60" width="220" height="90" rx="10" fill="#FDE7EC" stroke="#be123c" stroke-width="2"/>
  <text x="490" y="82" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#5a1e2b">LIMITE_POR=carteira (o bug)</text>
  <text x="490" y="102" text-anchor="middle" font-size="10.5" fill="#5a1e2b">ana: R$ 800 de 1.000 ✓</text>
  <text x="490" y="120" text-anchor="middle" font-size="10.5" fill="#5a1e2b">ana2: R$ 800 de 1.000 ✓</text>
  <text x="490" y="140" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#be123c">total da pessoa: R$ 1.600</text>
  <!-- limite por cliente -->
  <rect x="380" y="170" width="220" height="90" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="490" y="192" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#04342C">LIMITE_POR=cliente (a correção)</text>
  <text x="490" y="212" text-anchor="middle" font-size="10.5" fill="#04342C">ana: R$ 800 de 1.000 ✓</text>
  <text x="490" y="230" text-anchor="middle" font-size="10.5" fill="#04342C">ana2: 800 + 800 &gt; 1.000 ✗</text>
  <text x="490" y="250" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#166534">LIMITE_DIARIO_EXCEDIDO · cliente:&lt;id&gt;</text>
  <line x1="317" y1="105" x2="376" y2="105" stroke="#57534e" stroke-width="1.5" marker-end="url(#p4-a)"/>
  <line x1="317" y1="195" x2="376" y2="215" stroke="#57534e" stroke-width="1.5" marker-end="url(#p4-a)"/>
  <!-- the two dictionaries -->
  <rect x="640" y="60" width="240" height="200" rx="10" fill="#fff" stroke="#57534e" stroke-width="1.5"/>
  <text x="760" y="84" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#1f1e1c">"conta" significa…</text>
  <text x="655" y="112" font-size="10.5" fill="#04342C"><tspan font-weight="bold">no Ledger:</tspan> pote contábil com natureza</text>
  <text x="655" y="128" font-size="10.5" fill="#04342C">(ATIVO/PASSIVO) — a carteira</text>
  <text x="655" y="158" font-size="10.5" fill="#1e2a5a"><tspan font-weight="bold">na Identidade:</tspan> a pessoa, o CPF,</text>
  <text x="655" y="174" font-size="10.5" fill="#1e2a5a">o cadastro aprovado</text>
  <text x="655" y="204" font-size="10.5" fill="#be123c"><tspan font-weight="bold">em Limites:</tspan> palavra PROIBIDA —</text>
  <text x="655" y="220" font-size="10.5" fill="#be123c">diga "cliente" ou "carteira"</text>
  <text x="760" y="248" text-anchor="middle" font-size="9.5" fill="#8a897f">tests/linguagem_test.go cobra isto</text>
  <text x="450" y="300" text-anchor="middle" font-size="11" fill="#8a897f">nenhuma linha de código estava errada; cada time estava certo dentro do próprio dicionário — o bug morava entre eles</text>
</svg>
</div>

A Ana paga R$ 800 de cada uma. Os dois passam. Nenhuma linha de código está errada; o bug está **na palavra**, entre os times. O DDD tem um nome para isso: falha de **linguagem ubíqua** — a ideia de que, dentro de uma fronteira, todo mundo usa a mesma palavra com o mesmo significado, do engenheiro ao especialista de negócio. E reparem na nuance que pegou os dois times: a linguagem ubíqua **não é global**. Ela vale dentro de um contexto; fora dele, a mesma palavra pode — e frequentemente deve — significar outra coisa. É a razão de a linguagem ser **por contexto**: "conta" é pote no Ledger e é palavra proibida em Limites, onde se diz `cliente` ou `carteira`; "cliente" é pessoa na Identidade e é proibida no Ledger. O `contextos.go` carrega essas proibições, e `tests/linguagem_test.go` quebra o build se alguém usar a palavra errada no lugar errado.

Agora eu quero que vocês imaginem esse mesmo bug com Limites e Ledger em **serviços separados**, times separados, repositórios separados:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 270" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p4-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">O mesmo bug, em duas topologias — onde ele aparece e quanto custa corrigir</text>
  <!-- monolith -->
  <text x="225" y="58" text-anchor="middle" font-size="12" font-weight="bold" fill="#57534e">monólito modular</text>
  <rect x="40" y="70" width="370" height="130" rx="12" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <rect x="60" y="95" width="140" height="44" rx="6" fill="#fff" stroke="#534AB7"/><text x="130" y="113" text-anchor="middle" font-size="10.5" fill="#26215C">limites</text><text x="130" y="129" text-anchor="middle" font-size="9" fill="#5a55a0">type ContaCliente ← proibido</text>
  <rect x="250" y="95" width="140" height="44" rx="6" fill="#fff" stroke="#166534"/><text x="320" y="113" text-anchor="middle" font-size="10.5" fill="#04342C">ledger</text><text x="320" y="129" text-anchor="middle" font-size="9" fill="#166534">Conta = pote contábil</text>
  <line x1="202" y1="117" x2="246" y2="117" stroke="#57534e" stroke-width="1.5" marker-end="url(#p4-b)"/>
  <rect x="60" y="150" width="330" height="36" rx="6" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="225" y="173" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#04342C">tests/linguagem_test.go → build quebra no PR, em segundos</text>
  <text x="225" y="222" text-anchor="middle" font-size="10.5" fill="#534AB7">custo da correção: renomear um tipo</text>
  <!-- services -->
  <text x="675" y="58" text-anchor="middle" font-size="12" font-weight="bold" fill="#57534e">dois serviços</text>
  <rect x="490" y="70" width="170" height="130" rx="12" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/>
  <text x="575" y="92" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#412402">svc-limites · repo A</text>
  <text x="575" y="112" text-anchor="middle" font-size="9.5" fill="#412402">"conta" = pessoa</text>
  <rect x="710" y="70" width="170" height="130" rx="12" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/>
  <text x="795" y="92" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#412402">svc-ledger · repo B</text>
  <text x="795" y="112" text-anchor="middle" font-size="9.5" fill="#412402">"conta" = carteira</text>
  <line x1="662" y1="150" x2="706" y2="150" stroke="#be123c" stroke-width="2.5" marker-end="url(#p4-b)"/>
  <text x="684" y="141" text-anchor="middle" font-size="9" fill="#be123c">{"conta_id": …}</text>
  <text x="575" y="150" text-anchor="middle" font-size="9.5" fill="#412402">contrato JSON</text>
  <text x="575" y="166" text-anchor="middle" font-size="9.5" fill="#412402">versionado, com</text>
  <text x="575" y="182" text-anchor="middle" font-size="9.5" fill="#412402">a ambiguidade dentro</text>
  <text x="795" y="150" text-anchor="middle" font-size="9.5" fill="#412402">ninguém testa</text>
  <text x="795" y="166" text-anchor="middle" font-size="9.5" fill="#412402">a palavra do outro</text>
  <text x="795" y="182" text-anchor="middle" font-size="9.5" fill="#412402">repositório</text>
  <text x="685" y="222" text-anchor="middle" font-size="10.5" fill="#be123c">aparece na conciliação do fim do mês, ou numa fiscalização</text>
  <text x="685" y="240" text-anchor="middle" font-size="10.5" fill="#be123c">custo da correção: dois PRs, dois deploys coordenados, versão nova do contrato</text>
</svg>
</div>

A palavra ambígua vira um campo num contrato JSON, e o erro não aparece num teste — aparece na conciliação do fim do mês, ou numa fiscalização. **Microsserviço não corrige fronteira errada; ele a torna permanente.** Esse é o primeiro argumento contra cortar antes de modelar.

### 4.2 O rio de eventos, e onde o dono muda

```bash
make demo-rio
```

A técnica para descobrir as fronteiras em vez de decretá-las chama-se **event storming**: a gente coloca numa parede, em post-its, os fatos do domínio, no passado, em ordem, com quem publica cada um. Antes do rio, a gramática — porque é a gramática que faz a fronteira aparecer sozinha:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 230" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p4-c" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">A gramática do event storming — a frase que se repete ao longo do rio</text>
  <g font-size="10.5" text-anchor="middle">
    <rect x="20" y="70" width="130" height="70" rx="4" fill="#fde68a" stroke="#b45309"/><text x="85" y="98" font-weight="bold" fill="#412402">ator</text><text x="85" y="116" fill="#412402">cliente · operador</text><text x="85" y="130" font-size="9" fill="#7a5c00">amarelo</text>
    <line x1="152" y1="105" x2="176" y2="105" stroke="#57534e" stroke-width="1.5" marker-end="url(#p4-c)"/>
    <rect x="180" y="70" width="130" height="70" rx="4" fill="#bfdbfe" stroke="#1d4ed8"/><text x="245" y="98" font-weight="bold" fill="#1e2a5a">comando</text><text x="245" y="116" fill="#1e2a5a">IniciarPix</text><text x="245" y="130" font-size="9" fill="#1d4ed8">azul</text>
    <line x1="312" y1="105" x2="336" y2="105" stroke="#57534e" stroke-width="1.5" marker-end="url(#p4-c)"/>
    <rect x="340" y="70" width="130" height="70" rx="4" fill="#fef3c7" stroke="#b45309"/><text x="405" y="98" font-weight="bold" fill="#412402">agregado</text><text x="405" y="116" fill="#412402">Pagamento</text><text x="405" y="130" font-size="9" fill="#7a5c00">amarelo claro · decide</text>
    <line x1="472" y1="105" x2="496" y2="105" stroke="#57534e" stroke-width="1.5" marker-end="url(#p4-c)"/>
    <rect x="500" y="70" width="130" height="70" rx="4" fill="#fdba74" stroke="#b45309"/><text x="565" y="98" font-weight="bold" fill="#412402">evento</text><text x="565" y="116" fill="#412402">PixIniciado</text><text x="565" y="130" font-size="9" fill="#7a5c00">laranja · verbo no passado</text>
    <line x1="632" y1="105" x2="656" y2="105" stroke="#57534e" stroke-width="1.5" marker-end="url(#p4-c)"/>
    <rect x="660" y="70" width="130" height="70" rx="4" fill="#e9d5ff" stroke="#534AB7"/><text x="725" y="98" font-weight="bold" fill="#26215C">política</text><text x="725" y="116" fill="#26215C">"sempre que … então"</text><text x="725" y="130" font-size="9" fill="#534AB7">roxo · vira consumidor</text>
    <path d="M725,142 L725,170 L245,170 L245,144" fill="none" stroke="#57534e" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#p4-c)"/>
    <text x="485" y="185" fill="#8a897f" font-size="10">…e a frase recomeça com outro comando</text>
    <rect x="800" y="70" width="90" height="70" rx="4" fill="#fecaca" stroke="#be123c"/><text x="845" y="98" font-weight="bold" fill="#5a1e2b">externo</text><text x="845" y="116" fill="#5a1e2b">DICT / SPI</text><text x="845" y="130" font-size="9" fill="#be123c">rosa · atrás de ACL</text>
  </g>
  <text x="450" y="215" text-anchor="middle" font-size="11" fill="#8a897f">o agregado é onde o comando aterrissa e uma invariante decide; o dono do evento é quem o publica — e é aí que a fronteira mora</text>
</svg>
</div>

Sobre o fluxo do Pix, o que sai é um rio: `PixIniciado → ChaveResolvida → LimitesValidados → FundosReservados → OrdemEnviadaAoSPI → PixLiquidado`, com `PixDevolvido` como ramo.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 200" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="m4d-c" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#8a897f"/></marker></defs>
  <text x="450" y="30" text-anchor="middle" font-size="14" font-weight="bold" fill="#1f1e1c">Cada fato tem um dono. Agrupe por dono: os contextos aparecem.</text>
  <g font-size="11" font-weight="bold">
    <rect x="15" y="60" width="125" height="60" rx="6" fill="#FAEEDA" stroke="#534AB7" stroke-width="2"/><text x="77" y="86" text-anchor="middle" fill="#412402">PixIniciado</text><text x="77" y="106" text-anchor="middle" font-size="9.5" font-weight="normal" fill="#534AB7">Pagamentos</text>
    <rect x="160" y="60" width="125" height="60" rx="6" fill="#FAEEDA" stroke="#534AB7" stroke-width="2"/><text x="222" y="86" text-anchor="middle" fill="#412402">ChaveResolvida</text><text x="222" y="106" text-anchor="middle" font-size="9.5" font-weight="normal" fill="#534AB7">Pagamentos (ACL)</text>
    <rect x="305" y="60" width="125" height="60" rx="6" fill="#FAEEDA" stroke="#166534" stroke-width="2"/><text x="367" y="86" text-anchor="middle" fill="#412402">LimitesValidados</text><text x="367" y="106" text-anchor="middle" font-size="9.5" font-weight="normal" fill="#166534">Limites</text>
    <rect x="450" y="60" width="125" height="60" rx="6" fill="#FAEEDA" stroke="#1d4ed8" stroke-width="2"/><text x="512" y="86" text-anchor="middle" fill="#412402">FundosReservados</text><text x="512" y="106" text-anchor="middle" font-size="9.5" font-weight="normal" fill="#1d4ed8">Ledger</text>
    <rect x="595" y="60" width="135" height="60" rx="6" fill="#FAEEDA" stroke="#534AB7" stroke-width="2"/><text x="662" y="86" text-anchor="middle" fill="#412402">OrdemEnviadaAoSPI</text><text x="662" y="106" text-anchor="middle" font-size="9.5" font-weight="normal" fill="#534AB7">Pagamentos</text>
    <rect x="750" y="60" width="125" height="60" rx="6" fill="#FAEEDA" stroke="#534AB7" stroke-width="2"/><text x="812" y="86" text-anchor="middle" fill="#412402">PixLiquidado</text><text x="812" y="106" text-anchor="middle" font-size="9.5" font-weight="normal" fill="#534AB7">Pagamentos</text>
  </g>
  <g stroke="#8a897f" stroke-width="1.5" marker-end="url(#m4d-c)"><line x1="142" y1="90" x2="156" y2="90"/><line x1="287" y1="90" x2="301" y2="90"/><line x1="432" y1="90" x2="446" y2="90"/><line x1="577" y1="90" x2="591" y2="90"/><line x1="732" y1="90" x2="746" y2="90"/></g>
  <path d="M812,122 Q812,160 700,160" fill="none" stroke="#8a897f" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#m4d-c)"/>
  <rect x="560" y="140" width="135" height="40" rx="6" fill="#FAEEDA" stroke="#166534" stroke-width="2" stroke-dasharray="6 3"/><text x="627" y="158" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#412402">PixDevolvido</text><text x="627" y="173" text-anchor="middle" font-size="9" fill="#166534">Devoluções (ramo)</text>
</svg>
</div>

A fronteira não é uma linha que alguém traça. É **o lugar onde o dono do fato muda**. Agrupem os eventos por quem os publica e os cinco contextos da seção 3 aparecem sozinhos:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 250" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">O mesmo rio, agrupado por dono — os contextos emergem</text>
  <g font-size="10" text-anchor="middle">
    <rect x="20" y="50" width="300" height="180" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
    <text x="170" y="72" font-size="12" font-weight="bold" fill="#26215C">Pagamentos</text>
    <rect x="35" y="85" width="130" height="30" rx="4" fill="#FAEEDA" stroke="#b45309"/><text x="100" y="104" fill="#412402">PixIniciado</text>
    <rect x="175" y="85" width="130" height="30" rx="4" fill="#FAEEDA" stroke="#b45309"/><text x="240" y="104" fill="#412402">ChaveResolvida</text>
    <rect x="35" y="125" width="130" height="30" rx="4" fill="#FAEEDA" stroke="#b45309"/><text x="100" y="144" fill="#412402">OrdemEnviadaAoSPI</text>
    <rect x="175" y="125" width="130" height="30" rx="4" fill="#FAEEDA" stroke="#b45309"/><text x="240" y="144" fill="#412402">PixLiquidado</text>
    <rect x="35" y="165" width="130" height="30" rx="4" fill="#FAEEDA" stroke="#b45309"/><text x="100" y="184" fill="#412402">PixEstornado</text>
    <text x="170" y="218" font-size="9.5" fill="#5a55a0">pix · bacen · reconcile · feed</text>
    <rect x="340" y="50" width="170" height="85" rx="10" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
    <text x="425" y="72" font-size="12" font-weight="bold" fill="#1e2a5a">Contas e Ledger</text>
    <rect x="355" y="85" width="140" height="30" rx="4" fill="#FAEEDA" stroke="#b45309"/><text x="425" y="104" fill="#412402">FundosReservados</text>
    <text x="425" y="128" font-size="9" fill="#1e2a5a">+ TransacaoRegistrada</text>
    <rect x="340" y="145" width="170" height="85" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
    <text x="425" y="167" font-size="12" font-weight="bold" fill="#04342C">Antifraude e Limites</text>
    <rect x="355" y="180" width="140" height="30" rx="4" fill="#FAEEDA" stroke="#b45309"/><text x="425" y="199" fill="#412402">LimitesValidados</text>
    <rect x="530" y="50" width="170" height="85" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
    <text x="615" y="72" font-size="12" font-weight="bold" fill="#04342C">Devoluções</text>
    <rect x="545" y="85" width="140" height="30" rx="4" fill="#FAEEDA" stroke="#b45309"/><text x="615" y="104" fill="#412402">PixDevolvido</text>
    <rect x="530" y="145" width="170" height="85" rx="10" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
    <text x="615" y="167" font-size="12" font-weight="bold" fill="#1e2a5a">Identidade</text>
    <text x="615" y="192" font-size="9.5" fill="#1e2a5a">publica nada — responde</text>
    <text x="615" y="206" font-size="9.5" fill="#1e2a5a">"quem é o titular?" (OHS)</text>
    <rect x="720" y="50" width="160" height="180" rx="10" fill="#FDE7EC" stroke="#be123c" stroke-width="2"/>
    <text x="800" y="72" font-size="12" font-weight="bold" fill="#5a1e2b">BACEN (externo)</text>
    <text x="800" y="100" font-size="9.5" fill="#5a1e2b">pacs.008 · pacs.002</text>
    <text x="800" y="116" font-size="9.5" fill="#5a1e2b">DICT lookup</text>
    <text x="800" y="150" font-size="9.5" fill="#be123c">entra e sai só pela ACL;</text>
    <text x="800" y="166" font-size="9.5" fill="#be123c">ChaveResolvida não carrega</text>
    <text x="800" y="182" font-size="9.5" fill="#be123c">CPF nem formato ISO</text>
  </g>
</svg>
</div>

É por isso que o `contextos.go` lista, para cada contexto, os eventos que ele publica: o mapa é a saída do event storming, gravada como código. E é por isso que a resposta à pergunta "onde cortar?" **não pode vir da reunião** — ela vem de um dia de parede com post-its, e o resultado é verificável.

### 4.3 Os quatro testes de fronteira, lidos com a pergunta da reunião

Uma fronteira candidata é boa quando passa em quatro testes — e os quatro dão para medir, não são opinião. Eu quero reler cada um deles com a pergunta "e se fosse um serviço?", porque é assim que eles viram argumento na reunião.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Os quatro testes de fronteira — e o preço de reprovar em cada topologia</text>
  <g font-size="10.5">
    <rect x="20" y="50" width="200" height="30" rx="5" fill="#f7f5ee" stroke="#8a897f"/><text x="120" y="70" text-anchor="middle" font-weight="bold" fill="#1f1e1c">teste</text>
    <rect x="230" y="50" width="200" height="30" rx="5" fill="#f7f5ee" stroke="#8a897f"/><text x="330" y="70" text-anchor="middle" font-weight="bold" fill="#1f1e1c">como medir</text>
    <rect x="440" y="50" width="215" height="30" rx="5" fill="#EEEDFE" stroke="#534AB7"/><text x="547" y="70" text-anchor="middle" font-weight="bold" fill="#26215C">reprova como módulo</text>
    <rect x="665" y="50" width="215" height="30" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="772" y="70" text-anchor="middle" font-weight="bold" fill="#5a1e2b">reprova como serviço</text>
    <!-- row 1 -->
    <rect x="20" y="90" width="200" height="50" rx="5" fill="#fff" stroke="#ddd"/><text x="30" y="110" font-weight="bold" fill="#1f1e1c">1 · linguagem própria</text><text x="30" y="128" fill="#57534e">a palavra muda de sentido ao cruzar?</text>
    <rect x="230" y="90" width="200" height="50" rx="5" fill="#fff" stroke="#ddd"/><text x="240" y="110" fill="#57534e">glossário por contexto;</text><text x="240" y="128" fill="#57534e">termos proibidos no teste</text>
    <rect x="440" y="90" width="215" height="50" rx="5" fill="#fff" stroke="#534AB7"/><text x="450" y="110" fill="#26215C">um rename e um teste</text><text x="450" y="128" fill="#26215C">de linguagem</text>
    <rect x="665" y="90" width="215" height="50" rx="5" fill="#fff" stroke="#be123c"/><text x="675" y="110" fill="#5a1e2b">ambiguidade congelada</text><text x="675" y="128" fill="#5a1e2b">num contrato versionado</text>
    <!-- row 2 -->
    <rect x="20" y="150" width="200" height="50" rx="5" fill="#fff" stroke="#ddd"/><text x="30" y="170" font-weight="bold" fill="#1f1e1c">2 · co-mutação baixa</text><text x="30" y="188" fill="#57534e">mudam juntos no mesmo commit?</text>
    <rect x="230" y="150" width="200" height="50" rx="5" fill="#fff" stroke="#ddd"/><text x="240" y="170" fill="#57534e" font-family="monospace">make comutacao</text><text x="240" y="188" fill="#57534e">(git log, últimos 6 meses)</text>
    <rect x="440" y="150" width="215" height="50" rx="5" fill="#fff" stroke="#534AB7"/><text x="450" y="170" fill="#26215C">um PR toca dois diretórios;</text><text x="450" y="188" fill="#26215C">sinal de fronteira errada</text>
    <rect x="665" y="150" width="215" height="50" rx="5" fill="#fff" stroke="#be123c"/><text x="675" y="170" fill="#5a1e2b">dois PRs, dois repos,</text><text x="675" y="188" fill="#5a1e2b">deploy coordenado — o pior dos mundos</text>
    <!-- row 3 -->
    <rect x="20" y="210" width="200" height="50" rx="5" fill="#fff" stroke="#ddd"/><text x="30" y="230" font-weight="bold" fill="#1f1e1c">3 · invariante fecha dentro</text><text x="30" y="248" fill="#57534e">a regra precisa de dado do outro lado?</text>
    <rect x="230" y="210" width="200" height="50" rx="5" fill="#fff" stroke="#ddd"/><text x="240" y="230" fill="#57534e">listar invariantes; ver de</text><text x="240" y="248" fill="#57534e">quais tabelas cada uma lê</text>
    <rect x="440" y="210" width="215" height="50" rx="5" fill="#fff" stroke="#534AB7"/><text x="450" y="230" fill="#26215C">uma transação que atravessa</text><text x="450" y="248" fill="#26215C">dois schemas — feio, mas ACID</text>
    <rect x="665" y="210" width="215" height="50" rx="5" fill="#fff" stroke="#be123c"/><text x="675" y="230" fill="#5a1e2b">vira saga; a invariante passa</text><text x="675" y="248" fill="#5a1e2b">a ser "quase sempre verdadeira"</text>
    <!-- row 4 -->
    <rect x="20" y="270" width="200" height="50" rx="5" fill="#fff" stroke="#ddd"/><text x="30" y="290" font-weight="bold" fill="#1f1e1c">4 · contrato pequeno e estável</text><text x="30" y="308" fill="#57534e">quantas chamadas cruzam? mudam muito?</text>
    <rect x="230" y="270" width="200" height="50" rx="5" fill="#fff" stroke="#ddd"/><text x="240" y="290" fill="#57534e">contar métodos em api.go e</text><text x="240" y="308" fill="#57534e">eventos no catálogo; ver o churn</text>
    <rect x="440" y="270" width="215" height="50" rx="5" fill="#fff" stroke="#534AB7"/><text x="450" y="290" fill="#26215C">interface gorda; refatorar</text><text x="450" y="308" fill="#26215C">é um PR</text>
    <rect x="665" y="270" width="215" height="50" rx="5" fill="#fff" stroke="#be123c"/><text x="675" y="290" fill="#5a1e2b">latência de rede em cada chamada</text><text x="675" y="308" fill="#5a1e2b">de um contrato que muda toda semana</text>
  </g>
</svg>
</div>

O primeiro teste é **linguagem própria**: a mesma palavra muda de sentido ao cruzar a linha? Se a fronteira falha nesse teste e vocês extraíram um serviço, o contrato carrega uma ambiguidade que ninguém mais pode corrigir sem quebrar o vizinho. O segundo é **co-mutação baixa**, medida com `make comutacao` — pares de módulos que mudam no mesmo commit. Se falha e vocês extraíram, toda funcionalidade vira dois pull requests em dois repositórios e um deploy coordenado, que é o pior dos dois mundos. O terceiro é **a invariante fecha dentro**: a regra de negócio precisa de dado do outro lado para ser verificada? Se falha e vocês extraíram, a transação vira saga e a invariante passa a ser "quase sempre verdadeira", o que num sistema financeiro é a mesma coisa que falsa. O quarto é **contrato pequeno e estável**: quantas chamadas e eventos atravessam a linha, e com que frequência mudam? Se falha e vocês extraíram, é latência de rede a cada chamada de um contrato que muda toda semana.

Reparem no padrão da última coluna: cada teste que uma fronteira *reprova* como módulo, ela reprova **muito mais caro** como serviço. É o segundo argumento para modelar antes de cortar.

### 4.4 O mapa de contexto não muda quando o módulo vira serviço

```bash
curl -s localhost:8080/v1/contextos | python3 -m json.tool | less
```

Contextos conversam, e o DDD tem um vocabulário para descrever *como*: **upstream** é quem decide, **downstream** é quem respeita. Um par pode ser *customer/supplier* (o de baixo tem voz no backlog do de cima), *open host service* (o de cima publica um contrato estável para qualquer um consumir), *conformist* (o de baixo aceita o modelo do de cima sem traduzir), ou ter uma *camada anticorrupção* — uma ACL — que traduz o modelo alheio na porta de entrada. Este é o mapa da TechPix, desenhado a partir do `contextos.go`:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p4-d" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker><marker id="p4-e" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#be123c"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Context map da TechPix — setas de upstream (decide) para downstream (respeita)</text>
  <g font-size="10.5" text-anchor="middle">
    <rect x="60" y="60" width="200" height="70" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
    <text x="160" y="84" font-size="12" font-weight="bold" fill="#26215C">Contas e Ledger</text>
    <text x="160" y="102" fill="#26215C">core · complicated-subsystem</text>
    <text x="160" y="118" font-size="9.5" fill="#5a55a0">RegistrarTx · TransacaoRegistrada</text>
    <rect x="350" y="200" width="200" height="70" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
    <text x="450" y="224" font-size="12" font-weight="bold" fill="#26215C">Pagamentos (Pix)</text>
    <text x="450" y="242" fill="#26215C">core · stream-aligned</text>
    <text x="450" y="258" font-size="9.5" fill="#5a55a0">pix · bacen (ACL) · reconcile · feed</text>
    <rect x="640" y="60" width="200" height="70" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
    <text x="740" y="84" font-size="12" font-weight="bold" fill="#26215C">Antifraude e Limites</text>
    <text x="740" y="102" fill="#26215C">core · stream-aligned</text>
    <text x="740" y="118" font-size="9.5" fill="#5a55a0">ValidarDebito · LimitesValidados</text>
    <rect x="640" y="300" width="200" height="70" rx="10" fill="#E3ECFD" stroke="#1d4ed8" stroke-width="2"/>
    <text x="740" y="324" font-size="12" font-weight="bold" fill="#1e2a5a">Identidade e Onboarding</text>
    <text x="740" y="342" fill="#1e2a5a">generic · platform</text>
    <text x="740" y="358" font-size="9.5" fill="#1d4ed8">PorCarteira → cliente</text>
    <rect x="60" y="300" width="200" height="70" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
    <text x="160" y="324" font-size="12" font-weight="bold" fill="#04342C">Devoluções e Disputas</text>
    <text x="160" y="342" fill="#04342C">supporting · stream-aligned</text>
    <text x="160" y="358" font-size="9.5" fill="#166534">PixDevolvido</text>
    <rect x="350" y="330" width="200" height="50" rx="10" fill="#FDE7EC" stroke="#be123c" stroke-width="2"/>
    <text x="450" y="351" font-size="12" font-weight="bold" fill="#5a1e2b">BACEN (DICT + SPI)</text>
    <text x="450" y="368" font-size="9.5" fill="#5a1e2b">externo · OHS + published language</text>
  </g>
  <g stroke="#57534e" stroke-width="2" fill="none" marker-end="url(#p4-d)">
    <line x1="220" y1="132" x2="400" y2="198"/>
    <line x1="160" y1="132" x2="160" y2="296"/>
    <line x1="680" y1="132" x2="500" y2="198"/>
    <line x1="740" y1="298" x2="740" y2="134"/>
    <line x1="350" y1="250" x2="264" y2="310"/>
    <path d="M552,215 C620,180 660,160 700,134"/>
  </g>
  <line x1="450" y1="328" x2="450" y2="274" stroke="#be123c" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#p4-e)"/>
  <g font-size="9.5" fill="#57534e">
    <text x="330" y="150" text-anchor="end">customer/supplier · síncrono + evento</text>
    <text x="172" y="220">customer/supplier · síncrono</text>
    <text x="575" y="168">customer/supplier · síncrono</text>
    <text x="575" y="180">(colaboração declarada)</text>
    <text x="752" y="220">open host service · síncrono</text>
    <text x="290" y="282" text-anchor="end">customer/supplier</text>
    <text x="290" y="294" text-anchor="end">E2E ID + PixLiquidado</text>
    <text x="612" y="200">customer/supplier · por evento (fat)</text>
    <text x="462" y="300" fill="#be123c">ACL na porta · conformist no fio</text>
  </g>
  <text x="450" y="395" text-anchor="middle" font-size="10.5" fill="#8a897f">nenhum partnership de propósito: dois contextos que só evoluem juntos são, provavelmente, um só</text>
</svg>
</div>

O Ledger é upstream de quase todos. A Identidade é um *open host service* com um contrato minúsculo — "quem é o titular desta carteira?". O BACEN é *published language* (ISO 20022) atrás de uma **ACL**, o módulo `bacen`, e é o único vizinho que já é, hoje, outro sistema. E Pagamentos com Limites é a única conversa síncrona de alta banda, declarada no mapa como *colaboração* — com o aviso de que, se virar permanente, a fronteira está errada.

Agora a observação que resolve metade da reunião. Olhem para esse mapa e reparem que **ele não muda** se Limites virar um serviço amanhã:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 280" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p4-f" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Mesma relação, dois meios — só a coluna "Meio" muda</text>
  <!-- module -->
  <text x="225" y="60" text-anchor="middle" font-size="12" font-weight="bold" fill="#57534e">como módulo (hoje)</text>
  <rect x="40" y="75" width="370" height="120" rx="12" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="225" y="95" text-anchor="middle" font-size="10" fill="#5a55a0">um processo</text>
  <rect x="60" y="110" width="140" height="50" rx="8" fill="#fff" stroke="#534AB7" stroke-width="2"/><text x="130" y="140" text-anchor="middle" font-size="11" fill="#26215C">pix</text>
  <rect x="250" y="110" width="140" height="50" rx="8" fill="#fff" stroke="#534AB7" stroke-width="2"/><text x="320" y="140" text-anchor="middle" font-size="11" fill="#26215C">limites</text>
  <line x1="202" y1="135" x2="246" y2="135" stroke="#57534e" stroke-width="2" marker-end="url(#p4-f)"/>
  <text x="225" y="126" text-anchor="middle" font-size="9" fill="#57534e">ValidarDebito()</text>
  <text x="225" y="180" text-anchor="middle" font-size="10" fill="#26215C">chamada em memória · ~microssegundos · nunca falha parcialmente</text>
  <!-- service -->
  <text x="675" y="60" text-anchor="middle" font-size="12" font-weight="bold" fill="#57534e">como serviço (se o gatilho disparar)</text>
  <rect x="490" y="75" width="170" height="120" rx="12" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="575" y="95" text-anchor="middle" font-size="10" fill="#5a55a0">processo techpix</text>
  <rect x="505" y="110" width="140" height="50" rx="8" fill="#fff" stroke="#534AB7" stroke-width="2"/><text x="575" y="140" text-anchor="middle" font-size="11" fill="#26215C">pix</text>
  <rect x="710" y="75" width="170" height="120" rx="12" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/>
  <text x="795" y="95" text-anchor="middle" font-size="10" fill="#7a5c00">processo antifraude</text>
  <rect x="725" y="110" width="140" height="50" rx="8" fill="#fff" stroke="#b45309" stroke-width="2"/><text x="795" y="140" text-anchor="middle" font-size="11" fill="#412402">limites</text>
  <line x1="647" y1="135" x2="721" y2="135" stroke="#57534e" stroke-width="2" marker-end="url(#p4-f)"/>
  <text x="684" y="126" text-anchor="middle" font-size="9" fill="#57534e">HTTP/gRPC</text>
  <text x="685" y="180" text-anchor="middle" font-size="10" fill="#412402">rede · ~milissegundos · timeout, retry, falha parcial</text>
  <!-- the table row -->
  <rect x="120" y="215" width="660" height="50" rx="8" fill="#fff" stroke="#57534e" stroke-width="1.5"/>
  <g font-size="10.5" font-family="monospace">
    <text x="135" y="235" fill="#1f1e1c">Relacao{Upstream: "antifraude_limites", Downstream: "pagamentos", Padrao: "customer_supplier",</text>
    <text x="135" y="253" fill="#1f1e1c">        Meio: <tspan fill="#534AB7" font-weight="bold">"sincrono"</tspan> }   ← o padrão, a direção e o evento não mudam; só o meio</text>
  </g>
</svg>
</div>

Os padrões, a direção das setas, os eventos publicados — tudo igual. O que muda é uma coluna: o campo `Meio` da relação em `contextos.go` sai de "síncrono, em memória" para "síncrono, pela rede". Isso é a frase central da aula, agora com o mapa na mão para prová-la: **bounded context é decisão de modelagem; serviço é decisão de topologia.** São decisões diferentes, tomadas por critérios diferentes, e confundi-las é a origem de boa parte dos projetos de microsserviços que dão errado.

### 4.5 Agregados: a fronteira que já desenha o corte

Dentro de um contexto, o **agregado** é a unidade de consistência: o conjunto de coisas que precisa ser atualizado junto, na mesma transação, para uma invariante nunca ser violada. Vocês já conhecem um: o Ledger, com Σdébitos = Σcréditos e saldo ≥ 0. Vaughn Vernon dá quatro regras para desenhá-los — proteger a invariante dentro; manter o agregado pequeno; referenciar outros agregados por identidade; consistência entre agregados só por evento — e a segunda tem uma matemática que eu recomendo sentir na calculadora do painel: vazão é 1 dividido pelo tempo de lock, então 4 ms de lock são 250 transações por segundo, e 1 segundo de DICT dentro do lock é 1 por segundo. Para a discussão de hoje, a regra que importa é a terceira: **referenciar outros agregados por identidade, nunca por objeto.**

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p4-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Referência por objeto × por identidade — e o que isso faz com o corte futuro</text>
  <!-- bad -->
  <text x="225" y="58" text-anchor="middle" font-size="12" font-weight="bold" fill="#be123c">✗ por objeto (FK atravessando contexto)</text>
  <rect x="40" y="70" width="370" height="150" rx="12" fill="#FDE7EC" stroke="#be123c" stroke-width="1.5"/>
  <rect x="60" y="95" width="150" height="60" rx="6" fill="#fff" stroke="#57534e"/>
  <text x="135" y="113" text-anchor="middle" font-size="10" font-family="monospace" fill="#1f1e1c">devolucoes.devolucoes</text>
  <text x="135" y="130" text-anchor="middle" font-size="9.5" font-family="monospace" fill="#be123c">pagamento_id FK →</text>
  <text x="135" y="145" text-anchor="middle" font-size="9.5" font-family="monospace" fill="#be123c">carteira_id   FK →</text>
  <rect x="250" y="80" width="140" height="40" rx="6" fill="#fff" stroke="#57534e"/><text x="320" y="104" text-anchor="middle" font-size="10" font-family="monospace" fill="#1f1e1c">public.pix_payments</text>
  <rect x="250" y="135" width="140" height="40" rx="6" fill="#fff" stroke="#57534e"/><text x="320" y="159" text-anchor="middle" font-size="10" font-family="monospace" fill="#1f1e1c">public.accounts</text>
  <line x1="212" y1="126" x2="246" y2="102" stroke="#be123c" stroke-width="2" marker-end="url(#p4-g)"/>
  <line x1="212" y1="142" x2="246" y2="152" stroke="#be123c" stroke-width="2" marker-end="url(#p4-g)"/>
  <text x="225" y="195" text-anchor="middle" font-size="10" fill="#5a1e2b">o agregado cresce sem ninguém decidir; join fácil hoje,</text>
  <text x="225" y="210" text-anchor="middle" font-size="10" fill="#5a1e2b">banco impossível de separar amanhã</text>
  <!-- good -->
  <text x="675" y="58" text-anchor="middle" font-size="12" font-weight="bold" fill="#166534">✓ por identidade (texto, sem FK)</text>
  <rect x="490" y="70" width="370" height="150" rx="12" fill="#E1F5EE" stroke="#166534" stroke-width="1.5"/>
  <rect x="510" y="95" width="150" height="60" rx="6" fill="#fff" stroke="#57534e"/>
  <text x="585" y="113" text-anchor="middle" font-size="10" font-family="monospace" fill="#1f1e1c">devolucoes.devolucoes</text>
  <text x="585" y="130" text-anchor="middle" font-size="9.5" font-family="monospace" fill="#166534">e2e_id_original text</text>
  <text x="585" y="145" text-anchor="middle" font-size="9.5" font-family="monospace" fill="#166534">carteira        text</text>
  <rect x="700" y="80" width="140" height="40" rx="6" fill="#fff" stroke="#57534e" stroke-dasharray="5 3"/><text x="770" y="104" text-anchor="middle" font-size="10" font-family="monospace" fill="#1f1e1c">public.pix_payments</text>
  <rect x="700" y="135" width="140" height="40" rx="6" fill="#fff" stroke="#57534e" stroke-dasharray="5 3"/><text x="770" y="159" text-anchor="middle" font-size="10" font-family="monospace" fill="#1f1e1c">public.accounts</text>
  <text x="680" y="126" text-anchor="middle" font-size="9" fill="#166534">só o E2E ID</text>
  <text x="680" y="150" text-anchor="middle" font-size="9" fill="#166534">só o código</text>
  <text x="675" y="195" text-anchor="middle" font-size="10" fill="#04342C">o schema devolucoes pode ir para outro banco amanhã</text>
  <text x="675" y="210" text-anchor="middle" font-size="10" fill="#04342C">sem tocar em pix nem em accounts — o corte já existe</text>
  <text x="450" y="250" text-anchor="middle" font-size="10.5" fill="#8a897f">a única FK cruzada da TechPix (pix_payments → accounts) é herdada, anotada como dívida em tests/fronteira_schema_test.go,</text>
  <text x="450" y="266" text-anchor="middle" font-size="10.5" fill="#8a897f">e o teste impede que nasça outra</text>
</svg>
</div>

Devoluções conhece um pagamento pelo E2E ID, não por uma chave estrangeira; Limites conhece um cliente por um id em texto, não por um join. É exatamente por isso que os schemas `devolucoes` e `limites` não têm FK para `pix_payments` nem para `accounts` — e é por isso que, se um dia esses contextos saírem para outro banco, o corte já está desenhado. O agregado bem feito é o pré-requisito silencioso de qualquer extração futura. Quem modela agregados grandes, com objetos atravessando contextos, descobre no dia da extração que não existe onde cortar.

Pergunta para a sala: *no banco de vocês, quantas chaves estrangeiras atravessam o que vocês chamam de "módulo"?* Se a resposta for "não sei", vocês não têm módulos — têm diretórios.

---
## 5. Monólito modular *bem definido*: a garantia de serviço sem a conta de serviço

Chegamos à alternativa concreta aos microsserviços — e eu insisto no adjetivo: não é "monólito", é "monólito modular bem definido". A diferença entre os dois não é a intenção do arquiteto. É a existência de verificação.

Um bounded context que existe só no diagrama tem prazo de validade de mais ou menos seis semanas. Basta uma sexta-feira apertada, um `import` conveniente, e a fronteira que custou um dia de event storming vira ficção — e ninguém percebe, porque nada quebra na hora. Deixa eu desenhar como isso acontece, porque todo mundo nesta sala já viu:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 260" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p5-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Como uma fronteira sem verificação evapora em seis semanas</text>
  <line x1="60" y1="150" x2="850" y2="150" stroke="#8a897f" stroke-width="2" marker-end="url(#p5-a)"/>
  <g font-size="10.5" text-anchor="middle">
    <circle cx="100" cy="150" r="7" fill="#166534"/>
    <text x="100" y="120" font-weight="bold" fill="#166534">semana 0</text>
    <text x="100" y="180" fill="#04342C">event storming;</text><text x="100" y="195" fill="#04342C">fronteiras no diagrama</text>
    <circle cx="300" cy="150" r="7" fill="#b45309"/>
    <text x="300" y="120" font-weight="bold" fill="#b45309">semana 2</text>
    <text x="300" y="180" fill="#412402">"só dessa vez":</text><text x="300" y="195" fill="#412402">import de pix em limites</text>
    <text x="300" y="210" font-size="9.5" fill="#8a897f">nada quebra</text>
    <circle cx="500" cy="150" r="7" fill="#b45309"/>
    <text x="500" y="120" font-weight="bold" fill="#b45309">semana 4</text>
    <text x="500" y="180" fill="#412402">um JOIN entre schemas</text><text x="500" y="195" fill="#412402">"é mais rápido assim"</text>
    <text x="500" y="210" font-size="9.5" fill="#8a897f">nada quebra</text>
    <circle cx="700" cy="150" r="7" fill="#be123c"/>
    <text x="700" y="120" font-weight="bold" fill="#be123c">semana 6</text>
    <text x="700" y="180" fill="#5a1e2b">o diagrama e o código</text><text x="700" y="195" fill="#5a1e2b">já não se parecem</text>
    <text x="700" y="210" font-size="9.5" fill="#8a897f">ninguém percebeu</text>
    <text x="830" y="120" font-weight="bold" fill="#5a1e2b">mês 6</text>
    <text x="830" y="180" fill="#5a1e2b">"vamos extrair"</text><text x="830" y="195" fill="#5a1e2b">— e não há onde</text>
  </g>
  <text x="450" y="245" text-anchor="middle" font-size="11" fill="#8a897f">o acoplamento é uma dívida que só cobra juros no futuro — por isso a verificação tem de ser automática e imediata</text>
</svg>
</div>

O que separa um monólito modular de uma bola de lama é que, no primeiro, o `import` da semana 2 **não compila**, e o JOIN da semana 4 **não passa na migration**. O repositório tem três camadas dessa defesa, e eu quero que vocês vejam as três rodando:

```bash
make test-arch          # segundos, sem banco: contextos, linguagem, contratos, schema, specs
make demo-linguagem     # planta um `type Transferencia` em Pagamentos → o build quebra → limpa
```

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 250" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Três camadas de defesa da fronteira — e quando cada uma acusa</text>
  <rect x="20" y="55" width="270" height="160" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="155" y="80" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#26215C">1 · Compilação</text>
  <text x="155" y="104" text-anchor="middle" font-size="11" fill="#26215C">internal/ do Go: importar o</text>
  <text x="155" y="122" text-anchor="middle" font-size="11" fill="#26215C">interior alheio não compila</text>
  <text x="155" y="146" text-anchor="middle" font-size="11" fill="#26215C">tests/contextos_test.go: dependência</text>
  <text x="155" y="164" text-anchor="middle" font-size="11" fill="#26215C">fora do mapa ou na direção errada</text>
  <text x="155" y="198" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#534AB7">acusa em segundos</text>
  <rect x="315" y="55" width="270" height="160" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="450" y="80" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#04342C">2 · Banco</text>
  <text x="450" y="104" text-anchor="middle" font-size="11" fill="#04342C">um schema por contexto</text>
  <text x="450" y="122" text-anchor="middle" font-size="11" fill="#04342C">tests/fronteira_schema_test.go:</text>
  <text x="450" y="146" text-anchor="middle" font-size="11" fill="#04342C">nenhuma FK nova atravessa contexto</text>
  <text x="450" y="164" text-anchor="middle" font-size="11" fill="#04342C">(a herdada está anotada como dívida)</text>
  <text x="450" y="198" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">acusa na migration</text>
  <rect x="610" y="55" width="270" height="160" rx="10" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/>
  <text x="745" y="80" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#412402">3 · Publicação</text>
  <text x="745" y="104" text-anchor="middle" font-size="11" fill="#412402">todo evento tem contrato JSON</text>
  <text x="745" y="122" text-anchor="middle" font-size="11" fill="#412402">versionado em platform/contratos</text>
  <text x="745" y="146" text-anchor="middle" font-size="11" fill="#412402">tests/contratos_test.go: mudança</text>
  <text x="745" y="164" text-anchor="middle" font-size="11" fill="#412402">incompatível é recusada</text>
  <text x="745" y="198" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#b45309">acusa antes do deploy</text>
  <text x="450" y="238" text-anchor="middle" font-size="11" fill="#8a897f">+ tests/linguagem_test.go: termo proibido em identificador quebra o build (a palavra "conta" em Limites)</text>
</svg>
</div>

A primeira camada é a **compilação**: o `internal/` do Go, mais o `tests/contextos_test.go`, que lê o mapa e recusa qualquer dependência entre módulos que não esteja declarada como relação entre contextos — ou que esteja na direção errada. Acusa em segundos, no PR. A segunda é o **banco**: um schema por contexto, e o `tests/fronteira_schema_test.go`, que impede que nasça uma chave estrangeira nova atravessando contextos — a única que existe, herdada, está anotada como dívida conhecida. Acusa na migration. A terceira é a **publicação**: todo evento tem um contrato JSON versionado em `platform/contratos/catalogo`, e o `tests/contratos_test.go` recusa mudanças incompatíveis. Acusa antes do deploy. Por cima das três, o `tests/linguagem_test.go` faz a palavra do bug — "conta", em Limites — quebrar o build.

Agora comparem com o que microsserviços dariam "de graça": a fronteira de rede. Ela também impede o `import` conveniente — mas a que preço?

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">A mesma garantia de fronteira — comprada de dois jeitos</text>
  <g font-size="10.5">
    <rect x="20" y="50" width="280" height="30" rx="5" fill="#f7f5ee" stroke="#8a897f"/><text x="160" y="70" text-anchor="middle" font-weight="bold" fill="#1f1e1c">o que se quer garantir</text>
    <rect x="310" y="50" width="280" height="30" rx="5" fill="#EEEDFE" stroke="#534AB7"/><text x="450" y="70" text-anchor="middle" font-weight="bold" fill="#26215C">monólito modular verificado</text>
    <rect x="600" y="50" width="280" height="30" rx="5" fill="#FAEEDA" stroke="#b45309"/><text x="740" y="70" text-anchor="middle" font-weight="bold" fill="#412402">microsserviços</text>
    <!-- rows -->
    <rect x="20" y="88" width="280" height="36" rx="5" fill="#fff" stroke="#ddd"/><text x="30" y="110" fill="#1f1e1c">ninguém importa o interior alheio</text>
    <rect x="310" y="88" width="280" height="36" rx="5" fill="#fff" stroke="#534AB7"/><text x="320" y="110" fill="#26215C">internal/ + contextos_test — grátis</text>
    <rect x="600" y="88" width="280" height="36" rx="5" fill="#fff" stroke="#b45309"/><text x="610" y="110" fill="#412402">repositórios separados — grátis</text>
    <rect x="20" y="132" width="280" height="36" rx="5" fill="#fff" stroke="#ddd"/><text x="30" y="154" fill="#1f1e1c">ninguém escreve na tabela alheia</text>
    <rect x="310" y="132" width="280" height="36" rx="5" fill="#fff" stroke="#534AB7"/><text x="320" y="154" fill="#26215C">schema por contexto + fronteira_schema_test</text>
    <rect x="600" y="132" width="280" height="36" rx="5" fill="#fff" stroke="#b45309"/><text x="610" y="154" fill="#412402">banco por serviço + dual-run + backfill (Aula 6)</text>
    <rect x="20" y="176" width="280" height="36" rx="5" fill="#fff" stroke="#ddd"/><text x="30" y="198" fill="#1f1e1c">contrato explícito e versionado</text>
    <rect x="310" y="176" width="280" height="36" rx="5" fill="#fff" stroke="#534AB7"/><text x="320" y="198" fill="#26215C">catálogo JSON + contratos_test</text>
    <rect x="600" y="176" width="280" height="36" rx="5" fill="#fff" stroke="#b45309"/><text x="610" y="198" fill="#412402">API versionada + gateway + tracing (Aula 7)</text>
    <rect x="20" y="220" width="280" height="36" rx="5" fill="#fff" stroke="#ddd"/><text x="30" y="242" fill="#1f1e1c">o que se ganha "de brinde"</text>
    <rect x="310" y="220" width="280" height="36" rx="5" fill="#E1F5EE" stroke="#166534"/><text x="320" y="242" fill="#04342C">uma transação, um deploy, um plantão</text>
    <rect x="600" y="220" width="280" height="36" rx="5" fill="#FDE7EC" stroke="#be123c"/><text x="610" y="242" fill="#5a1e2b">latência, falha parcial, saga, 4 plantões</text>
  </g>
  <text x="450" y="285" text-anchor="middle" font-size="11" fill="#8a897f">a coluna do meio compra a mesma garantia por um preço que vinte pessoas pagam — e mantém a coluna da direita como opção</text>
</svg>
</div>

**As três camadas compram a mesma garantia de fronteira por um preço que vinte pessoas podem pagar.** É isso que "monólito modular bem definido" significa nesta aula: a garantia de microsserviço sem a conta de microsserviço. E é o terceiro argumento — o decisivo — para não cortar antes de precisar.

Para quem não está em Go, as ferramentas equivalentes existem em toda linguagem: ArchUnit em Java e Kotlin, Spring Modulith — que é literalmente um monólito modular com estas regras embutidas —, NetArchTest em .NET, import-linter em Python, dependency-cruiser em TypeScript, go-arch-lint em Go. O ponto não é a ferramenta. É rodar no pull request.

---

## 6. Decompor ou não: os quatro gatilhos, contexto a contexto

Agora sim a pergunta da reunião, respondida com o vocabulário que a aula construiu e não com opinião.

O critério: extrair um contexto para serviço próprio se justifica quando **pelo menos um** de quatro gatilhos dispara. O contexto precisa **escalar de forma diferente** do resto. O contexto tem **ciclo de deploy diferente** — muda dez vezes por dia enquanto o resto muda uma vez por semana. O contexto pertence a um **time diferente**, e o acoplamento de deploy virou fila entre times — este é, na prática, o motivo mais comum e mais legítimo. Ou o contexto tem **requisito de disponibilidade ou de isolamento de falha** distinto, que é o bulkhead da Aula 2 aplicado no nível de serviço.

Isso vira um fluxo de decisão, e eu quero que vocês o apliquem literalmente, contexto por contexto:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p6-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">O fluxo de decisão — para cada bounded context</text>
  <rect x="350" y="45" width="200" height="40" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="2"/>
  <text x="450" y="70" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#26215C">um bounded context</text>
  <line x1="450" y1="87" x2="450" y2="108" stroke="#57534e" stroke-width="2" marker-end="url(#p6-a)"/>
  <g font-size="10.5" text-anchor="middle">
    <rect x="40" y="112" width="190" height="60" rx="8" fill="#fff" stroke="#534AB7" stroke-width="2"/>
    <text x="135" y="134" font-weight="bold" fill="#26215C">1 · escala diferente?</text>
    <text x="135" y="152" fill="#5a55a0">CPU/GPU/memória ≠ resto</text>
    <rect x="250" y="112" width="190" height="60" rx="8" fill="#fff" stroke="#534AB7" stroke-width="2"/>
    <text x="345" y="134" font-weight="bold" fill="#26215C">2 · deploy diferente?</text>
    <text x="345" y="152" fill="#5a55a0">10×/dia vs 1×/semana</text>
    <rect x="460" y="112" width="190" height="60" rx="8" fill="#fff" stroke="#166534" stroke-width="2.5"/>
    <text x="555" y="134" font-weight="bold" fill="#166534">3 · time diferente + fila?</text>
    <text x="555" y="152" fill="#3f7a52">medida em dias de espera</text>
    <rect x="670" y="112" width="190" height="60" rx="8" fill="#fff" stroke="#534AB7" stroke-width="2"/>
    <text x="765" y="134" font-weight="bold" fill="#26215C">4 · falha/SLA diferente?</text>
    <text x="765" y="152" fill="#5a55a0">bulkhead no nível de serviço</text>
  </g>
  <g stroke="#57534e" stroke-width="1.5" fill="none" marker-end="url(#p6-a)">
    <path d="M450,108 L135,108 L135,110"/><path d="M450,108 L345,108 L345,110"/><path d="M450,108 L555,108 L555,110"/><path d="M450,108 L765,108 L765,110"/>
  </g>
  <!-- outcomes -->
  <line x1="450" y1="175" x2="450" y2="205" stroke="#57534e" stroke-width="2" marker-end="url(#p6-a)"/>
  <text x="450" y="195" text-anchor="middle" font-size="10" fill="#57534e">algum "sim" com evidência medida?</text>
  <rect x="80" y="215" width="300" height="80" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="230" y="240" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#26215C">NÃO → permanece módulo</text>
  <text x="230" y="260" text-anchor="middle" font-size="10.5" fill="#26215C">com as três camadas de verificação</text>
  <text x="230" y="278" text-anchor="middle" font-size="10.5" fill="#26215C">e o gatilho escrito no ADR</text>
  <rect x="520" y="215" width="300" height="80" rx="10" fill="#FAEEDA" stroke="#b45309" stroke-width="2.5"/>
  <text x="670" y="240" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#412402">SIM → avaliar extração</text>
  <text x="670" y="260" text-anchor="middle" font-size="10.5" fill="#412402">com a conta dos custos na mão:</text>
  <text x="670" y="278" text-anchor="middle" font-size="10.5" fill="#412402">rede · saga · banco próprio · tracing · plantão</text>
  <line x1="430" y1="210" x2="260" y2="214" stroke="#534AB7" stroke-width="2" marker-end="url(#p6-a)"/>
  <line x1="470" y1="210" x2="640" y2="214" stroke="#b45309" stroke-width="2" marker-end="url(#p6-a)"/>
  <text x="450" y="330" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#1f1e1c">se nenhum gatilho dispara, extrair compra só os custos do sistema distribuído — sem nenhum benefício</text>
  <text x="450" y="352" text-anchor="middle" font-size="10.5" fill="#8a897f">"vocês pagaram o preço e não levaram o produto"</text>
  <text x="450" y="380" text-anchor="middle" font-size="10.5" fill="#8a897f">o gatilho 3 é o mais comum e o mais legítimo — mas "fila" tem de ser medida, não sentida em retrospectiva</text>
</svg>
</div>

Vamos aplicar os quatro aos cinco contextos da TechPix, com a equipe de vinte e o orçamento da seção 1.

| Contexto | Escala ≠ | Deploy ≠ | Time ≠ com fila | Falha / SLA ≠ | Veredito hoje | O que faria disparar |
|---|---|---|---|---|---|---|
| **Contas e Ledger** | não | não — muda pouco | não | é o núcleo; se cair, tudo cai de qualquer jeito | **módulo — provavelmente para sempre** | Nada. É a verdade financeira; a transação atômica do ADR-001 mora aqui |
| **Pagamentos (Pix)** | não — o gargalo é o BACEN, não a CPU | muda mais que os outros | squad próprio, mas sem fila hoje | não | **módulo** | Fila de deploy *medida* entre squads; ou volume de Pix que exija réplicas que o resto não precisa |
| **Antifraude e Limites** | **talvez** — se entrar modelo de risco (CPU/GPU, Python) | a política de risco muda muito | squad próprio | quer falhar fechado sem derrubar o resto | **primeiro candidato** | Um modelo de ML em produção: outra linguagem, outro perfil de máquina, outro ciclo. Três gatilhos de uma vez |
| **Identidade e Onboarding** | não | não | não | **sim, se virar fornecedor externo** | **módulo → talvez "serviço de terceiro"** | Contratar KYC de mercado. O módulo vira uma ACL para o fornecedor — não um serviço nosso |
| **Devoluções e Disputas** | não | não | não | não | **módulo** | Nenhum previsível. Subdomínio de suporte: construído simples, fica simples |
| **Plataforma** | — | — | — | — | **biblioteca, nunca serviço** | Vira pacote compartilhado no dia em que houver dois binários |

O resultado, dito sem rodeios: **zero serviços hoje. Um candidato com gatilho claro. Kubernetes continua desnecessário.** E reparem que o candidato — Antifraude — é exatamente o que o ADR-002 e o `CONTEXT-MAP.md` já previam, escrito antes de a pergunta aparecer na reunião. É para isso que serve registrar a decisão com os critérios de revisão: quando a pressão chega, a resposta não é improvisada.

Vale desenhar como seria a extração do Antifraude, no dia em que o gatilho disparar — porque é o desenho que mostra o que a seção 4 preparou e o que a seção 7 vai cobrar:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 380" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p6-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Se o gatilho disparar: a extração do Antifraude — o que muda e o que não muda</text>
  <!-- techpix -->
  <rect x="30" y="60" width="380" height="200" rx="12" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="220" y="82" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">techpix (continua um binário)</text>
  <g font-size="10" text-anchor="middle">
    <rect x="45" y="95" width="100" height="30" rx="5" fill="#fff" stroke="#534AB7"/><text x="95" y="114" fill="#26215C">ledger</text>
    <rect x="155" y="95" width="100" height="30" rx="5" fill="#fff" stroke="#534AB7"/><text x="205" y="114" fill="#26215C">pix</text>
    <rect x="265" y="95" width="130" height="30" rx="5" fill="#fff" stroke="#534AB7"/><text x="330" y="114" fill="#26215C">bacen · reconcile · feed</text>
    <rect x="45" y="135" width="100" height="30" rx="5" fill="#fff" stroke="#534AB7"/><text x="95" y="154" fill="#26215C">identidade</text>
    <rect x="155" y="135" width="100" height="30" rx="5" fill="#fff" stroke="#534AB7"/><text x="205" y="154" fill="#26215C">devolucoes</text>
    <rect x="265" y="135" width="130" height="30" rx="5" fill="#FDE7EC" stroke="#be123c" stroke-dasharray="4 3"/><text x="330" y="154" fill="#be123c">limites → cliente HTTP</text>
    <rect x="45" y="175" width="350" height="30" rx="5" fill="#f1efe8" stroke="#8a897f"/><text x="220" y="194" fill="#444">plataforma: outbox · idempotency (vira pacote compartilhado)</text>
  </g>
  <text x="220" y="232" text-anchor="middle" font-size="10" fill="#5a55a0">limites vira um adaptador:</text>
  <text x="220" y="246" text-anchor="middle" font-size="10" fill="#5a55a0">mesma interface, chamada pela rede</text>
  <!-- antifraude svc -->
  <rect x="560" y="60" width="310" height="200" rx="12" fill="#FAEEDA" stroke="#b45309" stroke-width="2.5"/>
  <text x="715" y="82" text-anchor="middle" font-size="12" font-weight="bold" fill="#412402">svc-antifraude (novo processo)</text>
  <g font-size="10" text-anchor="middle">
    <rect x="580" y="95" width="130" height="30" rx="5" fill="#fff" stroke="#b45309"/><text x="645" y="114" fill="#412402">limites (o mesmo código)</text>
    <rect x="720" y="95" width="130" height="30" rx="5" fill="#fff" stroke="#b45309"/><text x="785" y="114" fill="#412402">modelo de risco (Python)</text>
    <rect x="580" y="135" width="270" height="30" rx="5" fill="#fff" stroke="#b45309"/><text x="715" y="154" fill="#412402">API: ValidarDebito · consumidor de FundosReservados</text>
    <rect x="580" y="175" width="270" height="30" rx="5" fill="#fff" stroke="#b45309"/><text x="715" y="194" fill="#412402">máquina com GPU · autoscaling próprio · plantão próprio</text>
  </g>
  <text x="715" y="232" text-anchor="middle" font-size="10" fill="#7a5c00">a linguagem de Limites vem junto:</text>
  <text x="715" y="246" text-anchor="middle" font-size="10" fill="#7a5c00">"conta" continua proibida</text>
  <!-- sync call -->
  <line x1="412" y1="150" x2="556" y2="150" stroke="#57534e" stroke-width="2.5" marker-end="url(#p6-b)"/>
  <text x="484" y="140" text-anchor="middle" font-size="9.5" fill="#57534e">HTTP · timeout · circuit breaker</text>
  <!-- dbs -->
  <rect x="30" y="290" width="380" height="60" rx="10" fill="#E1F5EE" stroke="#166534" stroke-width="2"/>
  <text x="220" y="313" text-anchor="middle" font-size="11" font-weight="bold" fill="#04342C">Postgres techpix — public · identidade · devolucoes</text>
  <text x="220" y="333" text-anchor="middle" font-size="10" fill="#04342C">o ledger não muda uma linha</text>
  <rect x="560" y="290" width="310" height="60" rx="10" fill="#FAEEDA" stroke="#b45309" stroke-width="2"/>
  <text x="715" y="313" text-anchor="middle" font-size="11" font-weight="bold" fill="#412402">Postgres antifraude — schema limites (migrado)</text>
  <text x="715" y="333" text-anchor="middle" font-size="10" fill="#412402">possível porque não havia FK cruzada</text>
  <!-- topic -->
  <rect x="420" y="268" width="60" height="1" fill="none"/>
  <text x="450" y="278" text-anchor="middle" font-size="9.5" fill="#57534e">tópico (outbox → broker):</text>
  <text x="450" y="291" text-anchor="middle" font-size="9.5" fill="#57534e">FundosReservados · PixEstornado</text>
  <text x="450" y="370" text-anchor="middle" font-size="10.5" fill="#8a897f">tudo o que tornou isto um sprint foi decidido na seção 4: fronteira por evento, schema próprio, referência por identidade, contrato versionado</text>
</svg>
</div>

Olhem o que muda: um processo novo, um banco novo, um tópico, um adaptador HTTP no lugar da chamada em memória. E olhem o que **não** muda: o ledger, o mapa de contextos, os eventos, a linguagem. A extração é um sprint porque a modelagem foi feita antes. Sem a seção 4, esse mesmo desenho seria um projeto de seis meses — e é essa a assimetria que decide os casos de dúvida:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 290" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="m4d-d" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">A assimetria que decide em caso de dúvida</text>
  <rect x="60" y="70" width="300" height="120" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="210" y="98" text-anchor="middle" font-size="14" font-weight="bold" fill="#26215C">módulo</text>
  <text x="210" y="124" text-anchor="middle" font-size="11" fill="#26215C">chamada em memória · uma transação</text>
  <text x="210" y="144" text-anchor="middle" font-size="11" fill="#26215C">um deploy · um plantão</text>
  <text x="210" y="164" text-anchor="middle" font-size="11" fill="#26215C">fronteira verificada no build</text>
  <rect x="540" y="70" width="300" height="120" rx="10" fill="#FAEEDA" stroke="#b45309" stroke-width="2.5"/>
  <text x="690" y="98" text-anchor="middle" font-size="14" font-weight="bold" fill="#412402">serviço</text>
  <text x="690" y="124" text-anchor="middle" font-size="11" fill="#412402">rede · saga · contrato versionado</text>
  <text x="690" y="144" text-anchor="middle" font-size="11" fill="#412402">deploy próprio · plantão próprio</text>
  <text x="690" y="164" text-anchor="middle" font-size="11" fill="#412402">tracing distribuído para enxergar</text>
  <path d="M365,110 L535,110" stroke="#166534" stroke-width="3" marker-end="url(#m4d-d)"/>
  <text x="450" y="100" text-anchor="middle" font-size="12" font-weight="bold" fill="#166534">extrair: um sprint</text>
  <path d="M535,160 L365,160" stroke="#be123c" stroke-width="3" marker-end="url(#m4d-d)"/>
  <text x="450" y="183" text-anchor="middle" font-size="12" font-weight="bold" fill="#be123c">voltar: um projeto</text>
  <text x="450" y="235" text-anchor="middle" font-size="12" fill="#57534e">As duas direções não custam o mesmo — logo não merecem o mesmo grau de certeza.</text>
  <text x="450" y="258" text-anchor="middle" font-size="12" fill="#57534e">Na dúvida, a decisão reversível é ficar módulo: ela mantém a opção aberta, e a opção tem valor.</text>
</svg>
</div>

**Transformar um módulo em serviço é um sprint; transformar um serviço de volta em módulo é um projeto.** As duas direções não custam o mesmo, e por isso não merecem o mesmo grau de certeza. Na dúvida, a decisão reversível é ficar no monólito modular — não por conservadorismo, mas por valor de opção.

E o comentário que fecha a reunião: vinte pessoas é o tamanho exato em que essa pergunta aparece, e o tamanho exato em que a resposta errada mais dói. Com duzentas pessoas, a fila de deploy é real e a extração se paga. Com vinte, quatro squads num monólito modular com `make test-arch` no pull request entregam mais do que quatro squads com quatro serviços, quatro pipelines, quatro plantões e um Kubernetes que ninguém domina. O custo de um sistema distribuído não é só dinheiro de nuvem. É atenção — e atenção é o recurso mais escasso de um time de vinte.

---

## 7. O plano de evolução, e o que cada passo custa

Eu não quero fechar com uma opinião; quero fechar com um caminho. Cada fase tem o gatilho que a dispara e o custo que ela adiciona — e, como todos os números desta aula, os valores são ilustrativos.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="m4d-e" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Fases — cada seta é um gatilho, não uma data</text>
  <rect x="20" y="60" width="200" height="200" rx="10" fill="#EEEDFE" stroke="#534AB7" stroke-width="2.5"/>
  <text x="120" y="86" text-anchor="middle" font-size="13" font-weight="bold" fill="#26215C">Fase 0 · HOJE</text>
  <text x="120" y="110" text-anchor="middle" font-size="10.5" fill="#26215C">monólito modular</text>
  <text x="120" y="128" text-anchor="middle" font-size="10.5" fill="#26215C">1 container · RDS Multi-AZ</text>
  <text x="120" y="146" text-anchor="middle" font-size="10.5" fill="#26215C">outbox no Postgres</text>
  <text x="120" y="164" text-anchor="middle" font-size="10.5" fill="#26215C">test-arch no PR</text>
  <text x="120" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#534AB7">≈ R$ 3.400 → 2.500/mês</text>
  <text x="120" y="222" text-anchor="middle" font-size="10" fill="#5a55a0">4 squads · 1 deploy</text>
  <line x1="222" y1="160" x2="240" y2="160" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-e)"/>
  <rect x="244" y="60" width="200" height="200" rx="10" fill="#fff" stroke="#534AB7" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="344" y="86" text-anchor="middle" font-size="13" font-weight="bold" fill="#26215C">Fase 1</text>
  <text x="344" y="110" text-anchor="middle" font-size="10.5" fill="#26215C">2ª réplica da aplicação</text>
  <text x="344" y="128" text-anchor="middle" font-size="10.5" fill="#26215C">cache sai do processo (Redis)</text>
  <text x="344" y="146" text-anchor="middle" font-size="10.5" fill="#26215C">relay da outbox vira worker</text>
  <text x="344" y="164" text-anchor="middle" font-size="10.5" fill="#26215C">separado (mesmo binário)</text>
  <text x="344" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#534AB7">+ ≈ R$ 1.500/mês</text>
  <text x="344" y="222" text-anchor="middle" font-size="10" fill="#5a55a0">gatilho: p99 ou disponibilidade</text>
  <text x="344" y="240" text-anchor="middle" font-size="10" fill="#5a55a0">ainda sem Kubernetes</text>
  <line x1="446" y1="160" x2="464" y2="160" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-e)"/>
  <rect x="468" y="60" width="200" height="200" rx="10" fill="#fff" stroke="#b45309" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="568" y="86" text-anchor="middle" font-size="13" font-weight="bold" fill="#412402">Fase 2</text>
  <text x="568" y="110" text-anchor="middle" font-size="10.5" fill="#412402">1º serviço: Antifraude</text>
  <text x="568" y="128" text-anchor="middle" font-size="10.5" fill="#412402">outbox → tópico (broker)</text>
  <text x="568" y="146" text-anchor="middle" font-size="10.5" fill="#412402">schema limites → banco próprio</text>
  <text x="568" y="164" text-anchor="middle" font-size="10.5" fill="#412402">OpenTelemetry · gateway</text>
  <text x="568" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#b45309">+ ≈ R$ 3.000–4.000/mês</text>
  <text x="568" y="222" text-anchor="middle" font-size="10" fill="#7a5c00">gatilho: modelo de ML / GPU</text>
  <text x="568" y="240" text-anchor="middle" font-size="10" fill="#7a5c00">ECS ainda basta</text>
  <line x1="670" y1="160" x2="688" y2="160" stroke="#57534e" stroke-width="2" marker-end="url(#m4d-e)"/>
  <rect x="692" y="60" width="190" height="200" rx="10" fill="#fff" stroke="#be123c" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="787" y="86" text-anchor="middle" font-size="13" font-weight="bold" fill="#5a1e2b">Fase 3</text>
  <text x="787" y="110" text-anchor="middle" font-size="10.5" fill="#5a1e2b">3+ serviços</text>
  <text x="787" y="128" text-anchor="middle" font-size="10.5" fill="#5a1e2b">Kubernetes (EKS) agora</text>
  <text x="787" y="146" text-anchor="middle" font-size="10.5" fill="#5a1e2b">se paga: placement,</text>
  <text x="787" y="164" text-anchor="middle" font-size="10.5" fill="#5a1e2b">rollout, autoscaling</text>
  <text x="787" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#be123c">+ ≈ R$ 2.000/mês + 1 pessoa</text>
  <text x="787" y="222" text-anchor="middle" font-size="10" fill="#7a3040">gatilho: fila entre squads</text>
  <text x="787" y="240" text-anchor="middle" font-size="10" fill="#7a3040">medida, não sentida</text>
  <text x="450" y="300" text-anchor="middle" font-size="11.5" fill="#57534e">O Ledger e o Postgres dele atravessam as quatro fases sem mudar — por isso são a parte certa para o compromisso de uso.</text>
</svg>
</div>

A **Fase 0** é hoje: monólito modular, um container, Postgres gerenciado com réplica, outbox no banco, testes de arquitetura no pull request. Em torno de R$ 3.400 por mês, caindo para R$ 2.500 quando o compromisso entrar. Quatro squads, um deploy.

A **Fase 1** dispara por p99 ou por disponibilidade, nunca por sensação: a segunda réplica da aplicação, o cache saindo do processo para um Redis gerenciado, e o relay da outbox virando um worker separado — ainda do mesmo binário, só com outro ponto de entrada. Mais ou menos R$ 1.500 por mês a mais. Ainda sem Kubernetes: duas réplicas de um container é o que ECS faz sem esforço.

A **Fase 2** dispara pelo gatilho do Antifraude — um modelo de risco em produção, que pede outra linguagem, outro perfil de máquina, outro ciclo de deploy. É o primeiro serviço, e é o desenho da seção 6. E é aqui que a conta muda de patamar, porque o primeiro serviço traz consigo tudo o que um serviço exige: a outbox vira um tópico num broker, o schema `limites` vai para um banco próprio, aparecem OpenTelemetry e um gateway na borda. Mais R$ 3.000 a R$ 4.000 por mês. ECS ainda basta para dois serviços.

A **Fase 3** dispara por fila entre squads — medida em dias de espera de deploy, não em reclamação de retrospectiva. Com três ou mais serviços, Kubernetes se paga: placement, rollout independente, autoscaling por serviço. Mais R$ 2.000 por mês e, honestamente, mais uma pessoa, porque um cluster precisa de dono.

Deixa eu empilhar esses custos, porque o desenho diz mais do que os números:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 320" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">Custo mensal por fase — o que cada camada adiciona (valores ilustrativos)</text>
  <line x1="120" y1="270" x2="860" y2="270" stroke="#8a897f" stroke-width="1.5"/>
  <line x1="120" y1="270" x2="120" y2="50" stroke="#8a897f" stroke-width="1.5"/>
  <g font-size="10" fill="#8a897f" text-anchor="end"><text x="112" y="274">0</text><text x="112" y="219">2,5k</text><text x="112" y="164">5k</text><text x="112" y="109">7,5k</text><text x="112" y="54">10k</text></g>
  <!-- scale: 1k = 22px; base y=270 -->
  <!-- Fase 0: db 1.3 + app 1.3 + obs 0.8 = 3.4 -->
  <g>
    <rect x="170" y="241.4" width="110" height="28.6" fill="#166534"/>
    <rect x="170" y="212.8" width="110" height="28.6" fill="#534AB7"/>
    <rect x="170" y="195.2" width="110" height="17.6" fill="#8a897f"/>
    <text x="225" y="186" text-anchor="middle" font-size="11" font-weight="bold" fill="#1f1e1c">≈ 3,4k</text>
    <text x="225" y="290" text-anchor="middle" font-size="11" fill="#57534e">Fase 0</text>
    <text x="225" y="305" text-anchor="middle" font-size="9.5" fill="#8a897f">monólito</text>
  </g>
  <!-- Fase 1: +1.5 (2nd app 1.3 + redis ~0.2) = 4.9 -->
  <g>
    <rect x="340" y="241.4" width="110" height="28.6" fill="#166534"/>
    <rect x="340" y="212.8" width="110" height="28.6" fill="#534AB7"/>
    <rect x="340" y="195.2" width="110" height="17.6" fill="#8a897f"/>
    <rect x="340" y="166.6" width="110" height="28.6" fill="#7c74d6"/>
    <rect x="340" y="162.2" width="110" height="4.4" fill="#1d4ed8"/>
    <text x="395" y="153" text-anchor="middle" font-size="11" font-weight="bold" fill="#1f1e1c">≈ 4,9k</text>
    <text x="395" y="290" text-anchor="middle" font-size="11" fill="#57534e">Fase 1</text>
    <text x="395" y="305" text-anchor="middle" font-size="9.5" fill="#8a897f">2 réplicas + Redis</text>
  </g>
  <!-- Fase 2: +3.5 (broker 1.5 + db2 1.0 + svc gpu ~1.0) = 8.4 -->
  <g>
    <rect x="510" y="241.4" width="110" height="28.6" fill="#166534"/>
    <rect x="510" y="212.8" width="110" height="28.6" fill="#534AB7"/>
    <rect x="510" y="195.2" width="110" height="17.6" fill="#8a897f"/>
    <rect x="510" y="166.6" width="110" height="28.6" fill="#7c74d6"/>
    <rect x="510" y="162.2" width="110" height="4.4" fill="#1d4ed8"/>
    <rect x="510" y="129.2" width="110" height="33" fill="#b45309"/>
    <rect x="510" y="107.2" width="110" height="22" fill="#d97706"/>
    <rect x="510" y="85.2" width="110" height="22" fill="#f59e0b"/>
    <text x="565" y="76" text-anchor="middle" font-size="11" font-weight="bold" fill="#1f1e1c">≈ 8,4k</text>
    <text x="565" y="290" text-anchor="middle" font-size="11" fill="#57534e">Fase 2</text>
    <text x="565" y="305" text-anchor="middle" font-size="9.5" fill="#8a897f">1º serviço + broker</text>
  </g>
  <!-- Fase 3: +2 (EKS) = 10.4 + 1 pessoa -->
  <g>
    <rect x="680" y="241.4" width="110" height="28.6" fill="#166534"/>
    <rect x="680" y="212.8" width="110" height="28.6" fill="#534AB7"/>
    <rect x="680" y="195.2" width="110" height="17.6" fill="#8a897f"/>
    <rect x="680" y="166.6" width="110" height="28.6" fill="#7c74d6"/>
    <rect x="680" y="162.2" width="110" height="4.4" fill="#1d4ed8"/>
    <rect x="680" y="129.2" width="110" height="33" fill="#b45309"/>
    <rect x="680" y="107.2" width="110" height="22" fill="#d97706"/>
    <rect x="680" y="85.2" width="110" height="22" fill="#f59e0b"/>
    <rect x="680" y="41.2" width="110" height="44" fill="#be123c"/>
    <text x="735" y="60" text-anchor="middle" font-size="11" font-weight="bold" fill="#fff">≈ 10,4k</text>
    <text x="735" y="76" text-anchor="middle" font-size="9.5" fill="#fff">+ 1 pessoa</text>
    <text x="735" y="290" text-anchor="middle" font-size="11" fill="#57534e">Fase 3</text>
    <text x="735" y="305" text-anchor="middle" font-size="9.5" fill="#8a897f">3+ serviços + EKS</text>
  </g>
  <!-- legend -->
  <g font-size="9.5" fill="#57534e">
    <rect x="800" y="120" width="10" height="10" fill="#166534"/><text x="815" y="129">Postgres (fixo)</text>
    <rect x="800" y="136" width="10" height="10" fill="#534AB7"/><text x="815" y="145">app</text>
    <rect x="800" y="152" width="10" height="10" fill="#8a897f"/><text x="815" y="161">obs/backup</text>
    <rect x="800" y="168" width="10" height="10" fill="#7c74d6"/><text x="815" y="177">2ª réplica</text>
    <rect x="800" y="184" width="10" height="10" fill="#b45309"/><text x="815" y="193">broker</text>
    <rect x="800" y="200" width="10" height="10" fill="#d97706"/><text x="815" y="209">2º banco</text>
    <rect x="800" y="216" width="10" height="10" fill="#f59e0b"/><text x="815" y="225">svc GPU</text>
    <rect x="800" y="232" width="10" height="10" fill="#be123c"/><text x="815" y="241">EKS</text>
  </g>
</svg>
</div>

Olhem o que o desenho diz: sair da Fase 0 para a Fase 3 multiplica a fatura mensal por três e adiciona uma pessoa. Cada seta precisa de um gatilho medido — fila em dias, p99 em milissegundos, co-mutação em percentual. E reparem na barra verde embaixo de todas as colunas, sempre do mesmo tamanho: o Postgres do ledger. É por isso que o compromisso de uso da seção 1 deveria cobrir o banco, e só o banco. **Comprometam-se com o que não muda.**

---

## 8. Fecho: a ordem certa das perguntas

Deixa eu amarrar o que a reunião de planejamento levou para casa — e voltar à pergunta que eu fiz no início: *por onde vocês cortariam?*

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 260" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p8-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#57534e"/></marker></defs>
  <text x="450" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f1e1c">A resposta da reunião — e a resposta da técnica</text>
  <rect x="30" y="60" width="400" height="160" rx="12" fill="#FDE7EC" stroke="#be123c" stroke-width="2"/>
  <text x="230" y="86" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#5a1e2b">"vamos quebrar em microsserviços"</text>
  <g font-size="10.5" fill="#5a1e2b">
    <text x="50" y="112">• corta por squad (Conway de trás para frente)</text>
    <text x="50" y="132">• Kubernetes no dia 1, broker no dia 2</text>
    <text x="50" y="152">• a palavra "conta" vira campo de contrato</text>
    <text x="50" y="172">• fatura ×3, plantão ×4, atenção ÷4</text>
    <text x="50" y="200" font-weight="bold">• e a fronteira errada fica permanente</text>
  </g>
  <line x1="435" y1="140" x2="465" y2="140" stroke="#57534e" stroke-width="2" marker-end="url(#p8-a)"/>
  <rect x="470" y="60" width="400" height="160" rx="12" fill="#E1F5EE" stroke="#166534" stroke-width="2.5"/>
  <text x="670" y="86" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#04342C">"vamos modelar, verificar e esperar o gatilho"</text>
  <g font-size="10.5" fill="#04342C">
    <text x="490" y="112">• event storming → 5 contextos descobertos</text>
    <text x="490" y="132">• 3 camadas de verificação no PR</text>
    <text x="490" y="152">• 4 gatilhos aplicados: zero serviços hoje</text>
    <text x="490" y="172">• Antifraude com gatilho escrito e extração desenhada</text>
    <text x="490" y="200" font-weight="bold">• a opção fica aberta, e a opção tem valor</text>
  </g>
  <text x="450" y="245" text-anchor="middle" font-size="11" fill="#8a897f">a diferença não é coragem nem conservadorismo — é a ordem das perguntas</text>
</svg>
</div>

Primeiro: **onde rodar é uma conta de três colunas** — a da planilha, a da operação e a do regulador. Com vinte pessoas, a nuvem é o time de infraestrutura que vocês não têm; e o BACEN pede continuidade, não datacenter.

Segundo: **com o quê rodar tem gatilho escrito para cada escolha.** Linux e Docker sempre; Kubernetes, broker e cache distribuído só quando a condição nomeada disparar. Escolha sem gatilho é dogma, nas duas direções.

Terceiro: **as fronteiras se descobrem, não se decretam.** O event storming sobre o rio de eventos do Pix é o que diz onde o dono do fato muda. A palavra ambígua entre dois times é o bug mais caro que existe — e serviços não o corrigem; o eternizam.

Quarto: **bounded context é modelagem; serviço é topologia.** O mapa de contexto não muda quando um módulo vira serviço; só a coluna `Meio` muda. São duas decisões, com dois critérios.

Quinto: **monólito modular bem definido é uma arquitetura, não uma esperança** — e o que o define são as três camadas de verificação, compilação, banco e publicação, rodando no pull request. Sem elas, é bola de lama com boas intenções.

Sexto: **quatro gatilhos, contexto a contexto.** Na TechPix de hoje: zero serviços, um candidato. Extrair é um sprint; voltar é um projeto. Na dúvida, a decisão reversível.

Sétimo: **o plano tem fases com gatilho e preço, e o Ledger não muda em nenhuma delas.** Comprometam-se com o que não muda.

E a pergunta para vocês levarem: no sistema de vocês, qual módulo *já* tem um dos quatro gatilhos disparado — e qual está sendo extraído só porque alguém disse a frase?

---

## Apêndice — Comandos do repositório usados nesta aula

```bash
# fintechdev-aula-3 — pré-requisitos: Docker e make
make reset && make up            # banco zerado, bug das duas carteiras ligado
make painel                      # http://localhost:8080 — aba Contextos: o mapa
make demo-duas-carteiras         # §4.1 — a palavra "conta" entre dois times
make demo-rio                    # §4.2 — o rio de eventos pintado por contexto
make comutacao                   # §4.3 — co-mutação entre módulos pelo git log
curl -s localhost:8080/v1/contextos | python3 -m json.tool    # §4.4 — o mapa é código
curl 'localhost:8080/v1/filas/aggregate?lock_ms=4&espera_rede_ms=1000'   # §4.5 — contenção
make test-arch                   # §5 — as três camadas, em segundos
make demo-linguagem              # §5 — termo proibido quebra o build
make demo-fat-thin && make demo-versao   # se sobrar tempo: autonomia do consumidor e versionamento
cat docs/ADR-002-monolito-modular.md docs/ADR-005-bounded-contexts.md   # as decisões, por escrito
```

## Apêndice (só para mim) — Onde aprofundar, se sobrar tempo ou surgir pergunta

| Seção desta aula | Seções do conteúdo completo (aula3-conteudo-completo.md) | Material do repositório |
|---|---|---|
| 0 · A reunião | novo | `cmd/techpix/main.go`, ADR-002 |
| 1 · Onde rodar | nova; apoia-se na Aula 1 §3.5 (Lei de Little) e Aula 2 §5 (outbox) | `docker-compose.yml`, `Dockerfile`, `bacen-sim` |
| 2 · Stack | §9 (ferramentas reais) | `Dockerfile`, `cmd/techpix/main.go`, `migrations/embed.go`, `scripts/k6_degrau.js` |
| 3 · Módulos | §1.5 (core/supporting/generic), §7 (Conway) | `internal/modules/`, `internal/platform/modular/`, ADR-002 |
| 4 · Modelar antes de cortar | §1–§3 (DDD, event storming, context map), §4.1–§4.2 (agregados) | `contextos.go`, `docs/EVENT-STORMING.md`, `docs/CONTEXT-MAP.md`, ADR-005, ADR-007 |
| 5 · Monólito modular | §4.5, §6 (fronteira que ninguém verifica não existe) | `tests/*_test.go`, `migrations/006_contextos_aula3.sql`, `specs/` |
| 6 · Decompor? | §8 (bounded context = microsserviço?) | ADR-002 "Revisão", `CONTEXT-MAP.md` §8 |
| 7 · Plano | §10 (fecho) e a [topologia progressiva](topologia-progressiva.md) | — |

## Apêndice — Termos novos desta versão

| Termo | Significado nesta aula |
|---|---|
| **CAPEX / OPEX** | Investimento inicial em ativo (comprar servidor) versus despesa recorrente (alugar capacidade). A planilha compara os dois; a operação e o regulador decidem. |
| **Ponto único de falha** | Componente cuja falha derruba o sistema inteiro. Um servidor de aplicação e um de banco são dois. |
| **Multi-AZ** | Réplica do banco em outra zona de disponibilidade, com failover automático. É a redundância mínima que uma operação financeira exige, como configuração e não como compra. |
| **Savings Plan / compromisso de uso** | Desconto em troca de um compromisso de gasto por um ou três anos. Uma aposta na topologia: só faz sentido sobre o que não muda. |
| **Responsabilidade compartilhada** | O provedor responde pela segurança *da* nuvem; vocês, pela segurança *na* nuvem. Boa parte dos controles técnicos exigidos vem pronta; a política e a operação continuam de vocês. |
| **RSFN / PSTI** | A rede privada do Sistema Financeiro Nacional, pela qual se fala com o SPI; e o provedor homologado que conecta uma instituição pequena a ela. |
| **Participante indireto** | Instituição que acessa o Pix por meio de um participante direto, que liquida por ela. Alternativa de negócio à conexão própria. |
| **Gatilho de revisão** | A condição, escrita junto com a decisão, que obriga a reavaliá-la. Sem gatilho, a decisão vira dogma. |
| **Artefato × execução** | A imagem Docker é o artefato; ECS, uma VM ou Kubernetes são onde ele executa. "Docker ou Kubernetes?" compara camadas diferentes. |
| **Monólito modular bem definido** | Um processo com fronteiras internas verificadas em três camadas — compilação, banco, publicação — no pull request. A garantia de serviço sem a conta de serviço. |
| **Assimetria da extração** | Virar serviço é um sprint; voltar a ser módulo é um projeto. Por isso o default é módulo. |
