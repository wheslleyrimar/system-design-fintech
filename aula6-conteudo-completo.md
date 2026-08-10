---
layout: default
title: "Aula 6 — Evolução para Microsserviços com Validação"
---

# Aula 6 — Evolução para Microsserviços com Validação
*Curso de Arquitetura de Sistemas Financeiros com IA*

> **Navegação:** [Índice](index.md) · [Aula 1](aula1-conteudo-completo.md) · [Aula 2](aula2-conteudo-completo.md) · [Aula 3](aula3-conteudo-completo.md) · [Aula 4](aula4-conteudo-completo.md) · [Aula 5](aula5-conteudo-completo.md) · **Aula 6 (você está aqui)** · [Aula 7](aula7-conteudo-completo.md) · [Aula 8](aula8-conteudo-completo.md)

Deixa eu contar sobre o dia 14 de novembro de 2025, uma sexta-feira, 9 horas da manhã. Foi o dia em que o TechPix desligou a rota antiga do Antifraude — o dia da primeira extração de verdade, quando um pedaço do monólito virou um serviço separado, com processo próprio, banco próprio, deploy próprio.

E eu vou contar do jeito que aconteceu, não do jeito que fica bonito em palestra: **a primeira tentativa falhou.** Nove e dezessete da manhã, o canary estava com 5% do tráfego na rota nova, e o p99 da chamada de análise de risco saltou de 80 milissegundos para 2,4 segundos. Às 9h19, o sistema fez rollback sozinho — noventa segundos entre a violação da métrica de guarda e o último pacote voltando pela rota antiga. Nenhum Pix falhou. Nenhum cliente percebeu. Ninguém precisou acordar de madrugada, porque nem era madrugada, e mesmo se fosse, ninguém teria acordado: a máquina desfez o que a máquina tinha feito.

Uma semana depois, dia 21, a gente tentou de novo. Subiu limpo. O Antifraude roda como serviço separado desde então.

Eu já disse na Aula 4 quem eu sou: o professor que chamam quando o sistema já está no ar. Passei anos de plantão, e plantão ensina uma coisa que slide nenhum ensina — a diferença entre a mudança que você *torce* para dar certo e a mudança que você *sabe* que, se der errado, desfaz sozinha. Essa aula inteira é sobre transformar a primeira na segunda. E a frase que eu quero que vocês carreguem até o fim é essa:

**Extrair sem rede de validação é coragem. Com rede, é rotina.**

O rollback das 9h19 não foi um fracasso. Foi a rede funcionando. Guardem isso, porque a gente volta nele com números.

---

## 1. Por que agora — e não na Aula 2

### 1.1 A assimetria que o outro professor deixou plantada

Lá na Aula 2, no meio do incidente do dia 5, o professor que esteve aqui antes de mim segurou a turma quando todo mundo queria gritar "vamos virar microsserviços". Ele citou o "monolith first" do Fowler e deixou uma assimetria registrada: **extrair cedo demais é caro; extrair tarde demais só custa um refactor. A assimetria favorece esperar.**

Pois bem. A gente esperou. E eu quero mostrar por que *agora* a espera acabou — não por ansiedade, mas por critério. Na Aula 3, quando desenharam os bounded contexts, ficou uma lista de quatro critérios operacionais para extrair um contexto para serviço. Deixa eu passar por eles, um a um, com o Antifraude e Limites na mão:

| Critério (Aula 3, Seção 6) | O Antifraude em novembro de 2025 |
|---|---|
| **Fronteira estável há meses** | A fronteira não muda desde o event storming de agosto. O contrato — chamada síncrona recebendo transação, devolvendo decisão — sobreviveu à Aula 4 (que o formalizou) e à Aula 5 (que trocou o miolo por um modelo de ML) **sem mudar a assinatura**. Fronteira que sobrevive a uma troca de implementação inteira é fronteira testada. |
| **Necessidade de escala diferente** | Desde a Aula 5, o Antifraude roda inferência de modelo em GPU. O resto do monólito escala por CPU e I/O. Colocar GPU no nó do monólito inteiro é pagar o hardware mais caro do datacenter para servir código que não usa ele. |
| **Time dono, com autonomia** | O time do Diego opera o Antifraude de ponta a ponta: regras, modelo, feature store, plantão. Eles já eram donos de fato; faltava a topologia reconhecer. |
| **Contrato de integração pronto** | O Contrato de Integração da Aula 4 define a aresta Pagamentos↔Antifraude por escrito: síncrona, orçamento de ~100 ms p99, timeout, retry, fallback fail-closed para valor alto e fail-open com limite baixo para valor pequeno. A rede pode entrar no meio dessa aresta porque a aresta já se comporta como se a rede existisse. |

Reparem no padrão: **nenhum critério é "estamos com vontade".** Todos são observáveis. É a diferença entre extrair por moda e extrair por evidência — e é o mesmo espírito do "decidir na fé, depois na evidência" que atravessa esse curso desde a Aula 1. A fronteira do Antifraude passou meses sendo ensaiada *dentro* do monólito, exatamente como o monólito modular da Aula 2 prometia: as fronteiras internas são o ensaio geral das fronteiras de serviço.

### 1.2 A ordem de extração — e o que NÃO sai

A pergunta seguinte é: extrai o quê, em que ordem? A resposta do TechPix:

**Primeiro, Antifraude e Limites.** Pelos quatro critérios acima, e por mais um, tático: a aresta dele já tem fallback definido. Se a extração der errado, o Contrato de Integração diz o que acontece — degrada com regra de negócio, não com estouro de pool. Extrair primeiro o serviço cuja falha já tem resposta escrita é extrair com a rede embaixo.

**Segundo, Pagamentos.** É o orquestrador do fluxo e o dono das camadas anticorrupção para DICT e SPI. Faz sentido ele ser um serviço: é ali que mora a conversa com o mundo externo, os timeouts herdados do teto de 40 segundos, o circuito com o BACEN. Mas ele vai *depois*, porque orquestrador é mais entrelaçado — e porque, extraindo o Antifraude primeiro, a gente aprende no contexto onde errar custa menos.

**E o Ledger fica.** Eu quero ser cirúrgico aqui, porque essa é a decisão mais importante da aula e é uma decisão de *não fazer*: **a escrita do ledger continua no monólito, com a conta única de liquidação `pix_a_liquidar` — e a pendência do ADR-002, aquela linha de revisão que diz "se a contenção persistir, reparticionar a própria escrita do ledger", continua aberta. Eu não vou ser eu a fechá-la.**

Por quê? Três razões. Primeira: o ledger é o agregado com a invariante mais cara do sistema — Σ débitos = Σ créditos, transacional, serializable. Colocar rede no meio de uma invariante transacional é trocar uma transação ACID por um saga com compensação, e ninguém aqui demonstrou que precisa pagar esse preço *hoje*. Segunda: o p99 de escrita do ledger está dentro do SLA. Incomoda? Incomoda. Mas "incomoda" não é evidência, e esse curso inteiro é sobre não decidir no incômodo. Terceira: extração de serviço se faz uma por vez, com aprendizado entre elas — e o ledger, se um dia sair ou reparticionar, tem que ser o último, feito pela equipe mais calejada, com a melhor rede de validação que existir. O próximo ADR numerado, o 003, só nasce quando alguém decidir mexer na escrita do ledger — e hoje não é esse dia.

Guardem a regra geral: **extraia primeiro o que tem fronteira madura e fallback escrito; extraia por último — ou nunca — o que carrega a invariante transacional do dinheiro.**

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a6ext-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <!-- ANTES -->
  <text x="150" y="24" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">ANTES (até nov/2025)</text>
  <rect x="30" y="35" width="250" height="330" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="155" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Monólito modular</text>
  <rect x="45" y="70" width="220" height="34" rx="6" fill="#eef2ff" stroke="#4338ca"/>
  <text x="155" y="91" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Pagamentos (ACLs DICT/SPI)</text>
  <rect x="45" y="112" width="220" height="34" rx="6" fill="#eef2ff" stroke="#4338ca"/>
  <text x="155" y="133" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">Antifraude e Limites (GPU!)</text>
  <rect x="45" y="154" width="220" height="46" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="155" y="173" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">Contas e Ledger</text>
  <text x="155" y="190" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">pix_a_liquidar · Σ = Σ</text>
  <rect x="45" y="208" width="220" height="30" rx="6" fill="#f9f9f7" stroke="#999"/>
  <text x="155" y="227" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">Identidade e Onboarding</text>
  <rect x="45" y="246" width="220" height="30" rx="6" fill="#f9f9f7" stroke="#999"/>
  <text x="155" y="265" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">Devoluções e Disputas</text>
  <rect x="45" y="284" width="220" height="30" rx="6" fill="#f9f9f7" stroke="#999"/>
  <text x="155" y="303" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">Cartões</text>
  <text x="155" y="345" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">1 deploy · 1 banco</text>

  <!-- seta -->
  <line x1="295" y1="200" x2="360" y2="200" stroke="#4338ca" stroke-width="2.5" marker-end="url(#a6ext-arrow)"/>
  <text x="327" y="188" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">extração</text>

  <!-- DEPOIS -->
  <text x="640" y="24" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">DEPOIS (dez/2025)</text>
  <!-- Antifraude service -->
  <rect x="380" y="35" width="240" height="80" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="500" y="57" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Serviço: Antifraude e Limites</text>
  <text x="500" y="76" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">GPU · modelo de ML · feature store</text>
  <text x="500" y="93" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">banco próprio · deploy próprio</text>
  <!-- Pagamentos service -->
  <rect x="640" y="35" width="240" height="80" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="760" y="57" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Serviço: Pagamentos</text>
  <text x="760" y="76" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">ACLs DICT/SPI · orquestração</text>
  <text x="760" y="93" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">timeouts do teto de 40s</text>
  <!-- Monólito remanescente -->
  <rect x="380" y="140" width="500" height="200" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="630" y="162" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Monólito remanescente — "lar legítimo de quem não tem razão para sair"</text>
  <rect x="400" y="176" width="220" height="56" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="510" y="197" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">Contas e Ledger — NÃO SAI</text>
  <text x="510" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">pix_a_liquidar · pendência ADR-002 aberta</text>
  <rect x="640" y="176" width="220" height="26" rx="6" fill="#f9f9f7" stroke="#999"/>
  <text x="750" y="193" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">Identidade e Onboarding</text>
  <rect x="640" y="208" width="220" height="26" rx="6" fill="#f9f9f7" stroke="#999"/>
  <text x="750" y="225" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">Devoluções e Disputas</text>
  <rect x="640" y="240" width="220" height="26" rx="6" fill="#f9f9f7" stroke="#999"/>
  <text x="750" y="257" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">Cartões</text>
  <text x="630" y="300" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">invariante Σ débitos = Σ créditos protegida por transação ACID local</text>
  <text x="630" y="318" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">"o próximo ADR numerado, o 003, só nasce quando alguém mexer aqui"</text>
  <!-- setas de chamada -->
  <line x1="640" y1="75" x2="625" y2="75" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="450" y="385" font-family="sans-serif" font-size="10" fill="#7a5c00"></text>
  <rect x="30" y="372" width="850" height="24" rx="6" fill="#fef9e7" stroke="#d4a017"/>
  <text x="455" y="388" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00">Ordem: 1º Antifraude (4 critérios verdes + fallback escrito) · 2º Pagamentos (runbook maduro) · Ledger fica — extração por evidência, não por moda</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A quebra do monólito guiada pelos bounded contexts da Aula 3: dois serviços saem, o Ledger fica — decisão de <em>não fazer</em>.</p>
</div>

---

## 2. A parte que ninguém conta: os dados

Todo mundo que palestra sobre microsserviços mostra caixinhas e setas. Quase ninguém mostra a parte que dói, então deixa eu fazer isso agora: **extrair o código é a parte fácil. A parte difícil é extrair os dados.**

### 2.1 Database-per-service: a regra de ouro ganha rede

Na Aula 2, o monólito modular tinha uma regra de ouro: **nenhum módulo lê a tabela de outro.** Módulo conversa por interface, nunca por SELECT no schema alheio. Essa regra agora sobe de nível: **nenhum serviço lê o banco de outro serviço. Nunca. Nem "só essa query". Nem "só até a migração terminar".**

A razão é a mesma da Aula 2, amplificada pela rede: banco compartilhado é acoplamento invisível. Se o serviço de Antifraude lê a tabela do monólito, qualquer mudança de schema no monólito quebra o Antifraude — e quebra em produção, em tempo de execução, sem nenhum compilador ou contrato avisando. É o bug do Diego e da Marina da Aula 3, só que agora com dois deploys independentes e ninguém olhando. O schema registry da Aula 4 protege os contratos de *evento*; não existe schema registry para "eu leio sua tabela escondido". Então a proibição é absoluta, e a gente transformou ela em fitness function: um teste no CI varre as connection strings e as permissões de banco, e **o usuário de banco do serviço de Antifraude simplesmente não tem GRANT em nenhum schema do monólito.** Fronteira de permissão por ausência — a Aula 5 ensinou isso para agentes de IA; vale igual para serviços.

O Antifraude, então, nasce com banco próprio: as tabelas de regras, de decisões, de casos — e a feature store, que já era dele desde a Aula 5. E aí vem a pergunta que separa o slide da produção: *como é que os dados saem de um banco e chegam no outro, sem parar o sistema e sem perder um registro?*

### 2.2 Expand/contract, dual-run, backfill — e a velha reconciliação

A resposta é a coreografia que a Aula 4 apresentou para contratos, aplicada agora a dados. Quatro movimentos:

**Expandir.** O serviço novo sobe com o banco novo, vazio, *ao lado* do monólito — sem receber tráfego de verdade. O código do monólito entra em modo de escrita dupla controlada: cada decisão de antifraude que ele toma é também publicada como evento (pelo Outbox da Aula 2 — reparem como tudo se encaixa: o Outbox que nasceu para o extrato agora alimenta a migração), e o serviço novo consome esses eventos e escreve no banco dele. A partir daqui, o banco novo acumula o presente.

**Backfill.** O presente não basta; falta o passado. Um processo de backfill copia o histórico — no caso do Antifraude, as decisões e os agregados de comportamento dos últimos meses — do banco velho para o novo, em lotes, fora do horário de pico, com throttling para não competir com produção. Backfill é chato, lento e absolutamente sem glamour. Também é onde mora metade dos incidentes de migração, então: lotes pequenos, retomável do ponto onde parou (idempotente — a Aula 1 não sai de moda), e medido.

**Dual-run.** Com o banco novo completo, começa a fase que eu considero a mais importante: os dois caminhos rodam *em paralelo*, o velho decidindo de verdade e o novo decidindo "de mentira" — exatamente o shadow mode da Aula 5, que o time do Diego já conhecia do modelo de ML. A cada transação, a decisão do serviço novo é comparada com a do caminho velho. Divergiu? Loga, conta, investiga. A taxa de divergência é a métrica que diz quando a migração está pronta: a gente definiu o critério *antes* — divergência abaixo de 0,01% por sete dias corridos — e só avançou quando ele foi cumprido.

**Contract.** Só então o tráfego migra (via canary, Seção 4), a escrita dupla é desligada, e — semanas depois, com tudo estável — as tabelas velhas do monólito são arquivadas e removidas. Contração é a última etapa, nunca a primeira. Pressa de apagar tabela velha já causou mais perda de dado que disco quebrado.

E atravessando os quatro movimentos, uma disciplina que o TechPix já tinha no sangue: **reconciliação.** Na Aula 1, o professor mostrou que o ledger interno precisa bater com a Conta PI no Banco Central — bater o livro de vocês contra o livro do outro, continuamente, porque divergência silenciosa vira incidente regulatório. A migração de dados é a mesma disciplina, apontada para dentro: um job compara, todo dia, contagens e somas entre o banco velho e o novo, e qualquer diferença acorda alguém. **Migração sem reconciliação não é migração; é esperança com cronograma.**

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 360" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a6dat-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a6dat-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- 4 fases -->
  <text x="20" y="24" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">A coreografia expand/contract aplicada a dados</text>
  <rect x="20" y="38" width="195" height="86" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="117" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">1 · Expandir</text>
  <text x="117" y="80" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">banco novo vazio, ao lado</text>
  <text x="117" y="96" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">escrita dupla via eventos</text>
  <text x="117" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">do Outbox (Aula 2)</text>
  <line x1="215" y1="81" x2="240" y2="81" stroke="#4338ca" stroke-width="2" marker-end="url(#a6dat-arrow)"/>
  <rect x="245" y="38" width="195" height="86" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="342" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">2 · Backfill</text>
  <text x="342" y="80" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">histórico em lotes, fora de pico</text>
  <text x="342" y="96" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">com throttling, idempotente</text>
  <text x="342" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">e retomável (Aula 1)</text>
  <line x1="440" y1="81" x2="465" y2="81" stroke="#4338ca" stroke-width="2" marker-end="url(#a6dat-arrow)"/>
  <rect x="470" y="38" width="195" height="86" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="567" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">3 · Dual-run</text>
  <text x="567" y="80" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">velho decide de verdade</text>
  <text x="567" y="96" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">novo decide "de mentira"</text>
  <text x="567" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">saída: divergência &lt;0,01% / 7 dias</text>
  <line x1="665" y1="81" x2="690" y2="81" stroke="#4338ca" stroke-width="2" marker-end="url(#a6dat-arrow)"/>
  <rect x="695" y="38" width="185" height="86" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="787" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">4 · Contract</text>
  <text x="787" y="80" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">tráfego migra via canary</text>
  <text x="787" y="96" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">desliga escrita dupla</text>
  <text x="787" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">arquivar → 30 dias → remover</text>

  <!-- bancos -->
  <rect x="120" y="170" width="230" height="70" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="235" y="195" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Banco do monólito</text>
  <text x="235" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">schema do Antifraude (velho)</text>
  <rect x="550" y="170" width="230" height="70" rx="8" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="665" y="195" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Banco do serviço novo</text>
  <text x="665" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">regras · decisões · feature store</text>
  <line x1="350" y1="195" x2="545" y2="195" stroke="#4338ca" stroke-width="2" marker-end="url(#a6dat-arrow)"/>
  <text x="447" y="185" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">eventos + backfill</text>
  <!-- reconciliação -->
  <path d="M 350 225 C 420 260, 480 260, 545 225" stroke="#166534" stroke-width="2" fill="none" stroke-dasharray="5 4" marker-end="url(#a6dat-arrow)"/>
  <text x="447" y="262" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">reconciliação diária: contagens e somas velho × novo → alerta</text>

  <!-- proibição -->
  <line x1="665" y1="240" x2="300" y2="290" stroke="#b91c1c" stroke-width="2.5" marker-end="url(#a6dat-red)"/>
  <line x1="455" y1="248" x2="505" y2="284" stroke="#b91c1c" stroke-width="3"/>
  <line x1="505" y1="248" x2="455" y2="284" stroke="#b91c1c" stroke-width="3"/>
  <rect x="180" y="290" width="600" height="26" rx="6" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="480" y="308" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#b91c1c">PROIBIDO: serviço lendo banco alheio — sem GRANT, verificado por fitness function no CI</text>
  <text x="450" y="345" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">O erro do fuso horário (divergência 0,4%) apareceu no dual-run como número num dashboard — custo: zero reais.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Extrair código é fácil; a extração de verdade é a dos dados — quatro movimentos, com reconciliação atravessando todos.</p>
</div>

### 2.3 O que descobrimos no meio do caminho

Uma nota honesta, porque aconteceu: no terceiro dia de dual-run, a taxa de divergência estava em 0,4% — quarenta vezes o critério. Pânico? Não: *informação*. Investigando as divergências (elas estavam logadas, uma a uma, com o EndToEndId de cada transação), o time achou a causa: o backfill tinha copiado os agregados de comportamento com um corte de fuso horário errado — meia-noite UTC em vez de meia-noite de Brasília. Três horas de janela deslocada, contadores de "Pix recebidos no dia" diferentes, decisões diferentes nas transações perto do limite. Corrigiu o corte, rodou o backfill de novo (idempotente, lembra?), divergência caiu para 0,003%.

A lição que eu quero que fique: **o dual-run existe para falhar cedo e barato.** Se a gente tivesse migrado direto, esse erro de fuso teria decidido errado em produção, com dinheiro real, e aparecido semanas depois como "o antifraude anda estranho". No dual-run, ele apareceu como um número num dashboard, três dias depois de existir, custando zero reais.

---

## 3. GitOps e ArgoCD: o deploy vira ledger

Agora o sistema tem dois deploys — monólito e Antifraude — e daqui a pouco terá três. Multiplicar deploys com o processo artesanal de antes ("roda o script, torce, confere no olho") é multiplicar risco. Então essa seção é sobre a mudança de filosofia que sustenta o resto da aula: **GitOps**.

### 3.1 O estado desejado mora no Git

A ideia central cabe numa frase: **a descrição completa do que deveria estar rodando em produção — quais serviços, quais versões, quantas réplicas, com que configuração — mora num repositório Git, em arquivos declarativos. Produção é o que o Git diz que ela é.**

Reparem no que isso inverte. No modelo antigo, deploy é um *verbo*: alguém executa uma ação contra o cluster, e o estado de produção é o acúmulo histórico de ações que pessoas executaram — algumas documentadas, outras na memória de quem saiu da empresa. No GitOps, deploy é um *substantivo*: um commit que muda a declaração do estado desejado. A ação de aplicar isso ao cluster deixa de ser humana.

### 3.2 O loop de reconciliação — vocês já conhecem esse desenho

Quem aplica é o **ArgoCD**: um operador que roda dentro do cluster comparando, continuamente, o estado *desejado* (o que está no Git) com o estado *observado* (o que está de fato rodando). Divergiu? Ele converge: aplica o que falta, remove o que sobra, e marca a aplicação como sincronizada. Esse ciclo — comparar, convergir, comparar de novo — roda para sempre.

E aqui eu quero que vocês parem e reparem numa coisa, porque é o tipo de rima estrutural que esse curso adora: **é o ledger de novo.** O Git é o log imutável de intenções — o write model, cada commit um fato datado, assinado, que nunca se sobrescreve, só se acrescenta. O cluster é a projeção — o read model, o estado materializado que sempre pode ser reconstruído a partir do log. E o ArgoCD é a reconciliação contínua entre os dois, o job que bate o livro contra a realidade. A Aula 1 ensinou esse desenho para dinheiro; a Aula 2 reusou ele no Outbox; agora ele opera a infraestrutura. **Quando a mesma estrutura resolve três problemas diferentes, ela deixou de ser padrão e virou princípio.**

Desse desenho caem três consequências práticas:

**Drift detection.** Se alguém entra no cluster na mão — "só um kubectl rapidinho para aumentar as réplicas" — o ArgoCD detecta o desvio entre observado e desejado e acusa (ou reverte sozinho, dependendo da configuração). O ajuste heroico de madrugada, que no modelo antigo virava estado permanente e não documentado, agora ou vira commit ou desaparece. Plantão agradece: segunda-feira de manhã, o sistema é o que o Git diz, não o que a madrugada deixou.

**Rollback = git revert.** Desfazer um deploy é reverter um commit. Não existe "script de rollback" separado, que ninguém testa até o dia em que precisa: o mecanismo de ida e o de volta são o mesmo mecanismo, exercitado em todo deploy. O rollback de 90 segundos da abertura foi exatamente isso — um revert automático aplicado pelo mesmo loop que tinha aplicado a ida.

**Trilha de auditoria de graça.** Todo estado que produção já teve corresponde a um commit: quem mudou, quando, o que, aprovado por quem no pull request. Numa fintech, isso não é luxo de engenheiro — o BACEN e o auditor perguntam "o que estava rodando no dia X e quem autorizou", e a resposta vira `git log` em vez de arqueologia de planilha. **Auditabilidade era exigência do domínio desde a tabela de propriedades do dinheiro da Aula 1; o GitOps entrega ela na camada de operação sem esforço adicional.**

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a6git-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a6git-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <!-- pipeline -->
  <rect x="20" y="30" width="120" height="50" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="80" y="52" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">commit</text>
  <text x="80" y="68" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">repo de código</text>
  <line x1="140" y1="55" x2="170" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a6git-arrow)"/>
  <rect x="175" y="18" width="180" height="76" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="265" y="38" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">CI — os tribunais</text>
  <text x="265" y="55" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">invariante Σ = Σ como teste</text>
  <text x="265" y="70" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">ArchUnit · GRANTs de banco</text>
  <text x="265" y="85" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">Pact · schema registry</text>
  <line x1="355" y1="55" x2="385" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a6git-arrow)"/>
  <rect x="390" y="30" width="110" height="50" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="445" y="52" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">imagem</text>
  <text x="445" y="68" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">artefato versionado</text>
  <line x1="500" y1="55" x2="530" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a6git-arrow)"/>
  <rect x="535" y="18" width="170" height="76" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="620" y="40" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">repo de deploy</text>
  <text x="620" y="58" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">estado desejado, declarativo</text>
  <text x="620" y="74" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">"produção é uma branch"</text>
  <line x1="705" y1="55" x2="735" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a6git-arrow)"/>
  <rect x="740" y="30" width="140" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="810" y="52" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">ArgoCD</text>
  <text x="810" y="68" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">sincroniza</text>

  <!-- loop de reconciliação -->
  <text x="450" y="140" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">O loop de reconciliação — "é o ledger de novo"</text>
  <rect x="120" y="160" width="260" height="80" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="250" y="185" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Git = write model</text>
  <text x="250" y="205" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">log imutável de intenções</text>
  <text x="250" y="222" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">cada commit: fato datado e assinado</text>
  <rect x="520" y="160" width="260" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="650" y="185" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Cluster = projeção</text>
  <text x="650" y="205" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">estado materializado, sempre</text>
  <text x="650" y="222" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">reconstruível a partir do log</text>
  <path d="M 380 180 C 430 160, 470 160, 520 180" stroke="#4338ca" stroke-width="2" fill="none" marker-end="url(#a6git-arrow)"/>
  <text x="450" y="162" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">converge (aplica o que falta)</text>
  <path d="M 520 225 C 470 248, 430 248, 380 225" stroke="#166534" stroke-width="2" fill="none" stroke-dasharray="5 4" marker-end="url(#a6git-green)"/>
  <text x="450" y="258" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">compara (drift detection · selfHeal desfaz o "kubectl rapidinho")</text>

  <rect x="120" y="280" width="660" height="30" rx="6" fill="#fff" stroke="#999" stroke-dasharray="4 3"/>
  <text x="450" y="300" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">rollback = <tspan font-family="monospace">git revert</tspan> — ida e volta são o mesmo mecanismo · trilha de auditoria = <tspan font-family="monospace">git log</tspan> (BACEN agradece)</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Do commit ao cluster: uma sequência de tribunais, e no fim o mesmo desenho da Aula 1 — log imutável, projeção, reconciliação contínua.</p>
</div>

### 3.3 Como isso fica no concreto

Para não ficar abstrato, o manifesto (resumido) que declara o serviço de Antifraude no ArgoCD:

```yaml
# repositório: techpix-deploy · caminho: apps/antifraude/app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: antifraude
spec:
  source:
    repoURL: https://git.techpix.internal/techpix-deploy
    path: apps/antifraude          # manifests: Deployment, Service, Rollout...
    targetRevision: main           # produção segue o main deste repo
  destination:
    namespace: antifraude
  syncPolicy:
    automated:
      prune: true                  # remove o que sumiu do Git
      selfHeal: true               # desfaz mudança manual no cluster (anti-drift)
```

Duas linhas merecem o dedo: `selfHeal: true` é o drift detection com dente — mudança manual no cluster é desfeita pelo loop; e `targetRevision: main` significa que **a definição de "produção" é uma branch** — com toda a proteção de branch, revisão obrigatória e CI que o repositório de código já tem. O repositório de deploy é separado do repositório de código de propósito: mudar *o que o serviço faz* e mudar *o que está rodando* são decisões diferentes, com revisores diferentes, e o Git registra as duas separadamente.

---

## 4. Entrega progressiva: deploy não é release

Com GitOps, o *como* aplicar mudanças está resolvido. Falta o mais importante: como aplicar mudanças **sem apostar o sistema inteiro em cada uma**. E a chave dessa porta é uma distinção de vocabulário que parece pedante e é estrutural:

**Deploy é colocar código novo em produção. Release é colocar tráfego em cima dele.** São eventos diferentes, e a engenharia moderna de entrega existe no espaço entre os dois.

No modelo antigo, deploy e release eram o mesmo instante: o código novo sobe já recebendo 100% do tráfego, e a validação de produção é feita *por* produção, com todos os clientes de cobaia simultânea. Separar os dois instantes cria uma zona de teste com rede: o código está lá, real, no ambiente real — mas decidindo sobre uma fração controlada do mundo.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 250" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a6dr-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a6dr-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- Deploy -->
  <rect x="20" y="30" width="330" height="130" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="185" y="55" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#333">DEPLOY</text>
  <text x="185" y="78" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">código novo em produção</text>
  <rect x="60" y="92" width="250" height="28" rx="6" fill="#f9f9f7" stroke="#999"/>
  <text x="185" y="111" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">flag OFF · 0% do tráfego · smoke test roda</text>
  <text x="185" y="145" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">deploy virou não-evento</text>
  <!-- seta -->
  <line x1="350" y1="95" x2="440" y2="95" stroke="#4338ca" stroke-width="2.5" marker-end="url(#a6dr-arrow)"/>
  <text x="395" y="83" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#4338ca">a release é um dial</text>
  <!-- Release -->
  <rect x="445" y="30" width="415" height="130" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="652" y="55" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#3730a3">RELEASE</text>
  <text x="652" y="76" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">tráfego em cima do código, em fatias</text>
  <!-- fatias -->
  <rect x="480" y="92" width="30" height="34" rx="4" fill="#c7d2fe" stroke="#4338ca"/>
  <text x="495" y="114" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">1%</text>
  <rect x="525" y="92" width="55" height="34" rx="4" fill="#c7d2fe" stroke="#4338ca"/>
  <text x="552" y="114" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">5%</text>
  <rect x="595" y="92" width="95" height="34" rx="4" fill="#a5b4fc" stroke="#4338ca"/>
  <text x="642" y="114" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#26215c">25%</text>
  <rect x="705" y="92" width="130" height="34" rx="4" fill="#818cf8" stroke="#4338ca"/>
  <text x="770" y="114" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#fff">100%</text>
  <text x="652" y="148" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">mínimo 1h por fatia · guardas pré-declaradas: erro &gt; 0,1% · p99 &gt; ~100 ms</text>
  <!-- kill switch -->
  <path d="M 652 160 C 652 195, 400 195, 200 165" stroke="#b91c1c" stroke-width="2.5" stroke-dasharray="6 4" fill="none" marker-end="url(#a6dr-red)"/>
  <rect x="330" y="196" width="290" height="26" rx="6" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="475" y="214" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#b91c1c">kill switch: desliga o caminho na hora, sem deploy</text>
  <text x="440" y="242" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">testado em game day — ninguém quer usar; todo mundo dorme melhor sabendo que existe</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Deploy é colocar código em produção; release é colocar tráfego em cima — a engenharia de entrega vive no espaço entre os dois.</p>
</div>

### 4.1 Feature flags: o interruptor entre deploy e release

O mecanismo mais simples dessa separação o TechPix adotou via **Unleash** (a Aula 2 já tinha apontado a ferramenta, prometendo que ela importaria "na Aula 8, porque é o mecanismo do canary" — pois é, o caminho até lá passa por aqui): a **feature flag**, um interruptor avaliado em tempo de execução que decide qual caminho de código uma requisição percorre, sem novo deploy.

Feature flag tem quatro usos clássicos, e eu vou ser honesto com vocês como esse curso sempre é: **os quatro usos, com o rigor de cada um, são assunto do professor da Aula 8.** Hoje a gente instala os dois operacionais, que a extração exige:

- **Flag de lançamento:** a rota nova (chamar o serviço de Antifraude em vez do módulo interno) nasce *atrás de uma flag desligada*. O deploy acontece com a flag em off — código em produção, zero tráfego. A release é a flag abrindo, gradualmente, para frações do tráfego. Deploy virou não-evento; a release virou um dial.
- **Kill switch:** a flag inversa — um interruptor que desliga um caminho *na hora*, sem deploy, sem pipeline, sem git revert. Se o serviço de Antifraude entrar em colapso às 3h da manhã, o on-call vira uma chave e o fluxo volta para a rota antiga (enquanto ela existir) ou para o fallback do Contrato de Integração da Aula 4 (fail-closed para valor alto, fail-open com limite baixo para valor pequeno). O kill switch é o freio de emergência: ninguém quer usar, todo mundo dorme melhor sabendo que existe e que foi testado — sim, **testa-se o kill switch em game day**, como a Aula 2 ensinou a testar tudo que só importa no dia ruim.

### 4.2 Canary: a release em fatias, com juiz automático

Com a flag instalada, a release vira uma progressão: **1% → 5% → 25% → 100%** do tráfego na rota nova, cada fatia observada antes de avançar. É o canary — o nome vem do canário na mina de carvão, e o professor da Aula 8 vai contar essa história e fazer a matemática fina dela; o que a gente instala hoje é a mecânica:

- **Métricas de guarda simples e pré-declaradas:** taxa de erro da rota nova acima do baseline de 0,1%, ou p99 da aresta acima do orçamento do Contrato de Integração (~100 ms para Pagamentos↔Antifraude). Os limites são escritos *antes* da release, no plano de canary — decidir o limite depois de ver o número é decidir com o dedo na balança.
- **Juiz automático:** quem compara métrica com limite não é um humano olhando dashboard — é o próprio controlador de rollout (no TechPix, o Argo Rollouts, irmão do ArgoCD, consultando o Prometheus). Violou a guarda? **Rollback automático, primeiro; notificação ao humano, depois.** Nessa ordem. O humano acorda com o sistema já são, lendo o relatório do que a máquina desfez.
- **Honestidade sobre o que falta:** quanto tempo em cada fatia? Cinco erros em 2.700 transações são "muitos"? 1% por cinco minutos prova alguma coisa? **Tem matemática séria nessas perguntas — amostra, significância, o perigo de espiar o resultado antes da hora — e é o professor da Aula 8 que vai fazer essa conta com vocês.** Hoje, o TechPix usa regras conservadoras e fixas: cada fatia segura no mínimo uma hora, e qualquer violação de guarda reverte. Grosseiro? É. Mas grosseiro *na direção segura* — e mecânica instalada é pré-requisito do rigor que vem depois.

E uma pergunta de plantão que sempre aparece aqui, e que merece resposta de engenheiro: **quem, fisicamente, manda 5% do tráfego para um lado e 95% para o outro?** A resposta é uma questão de *camada* — camada 4 contra camada 7 do modelo OSI, aquela mesma distinção que apareceu na Aula 4. Um balanceador de camada 4 (o kube-proxy do Kubernetes, um NLB) enxerga TCP: IP, porta, conexão. Ele é rápido e barato, mas é **cego a HTTP** — não vê rota, não vê header, não sabe o que é "1% das requisições". O split do canary só existe na camada 7, onde vivem o NGINX, o ALB e — no coração da malha do TechPix — o **Envoy**, um sidecar ao lado de cada serviço, com o **Istio** como plano de controle. E reparem no reencontro: a fachada do Strangler Fig da Aula 2 **era** um balanceador L7. O Envoy é a mesma ideia, industrializada.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 440" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a6t-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a6t-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
    <marker id="a6t-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#a8a29e"/>
    </marker>
  </defs>
  <text x="450" y="24" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">Quem divide o tráfego? Camada 4 × Camada 7 (modelo OSI)</text>

  <!-- L4 panel -->
  <rect x="30" y="40" width="410" height="140" rx="10" fill="#f5f5f4" stroke="#a8a29e" stroke-width="2"/>
  <text x="235" y="64" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#57534e">L4 — transporte (TCP/IP)</text>
  <text x="235" y="84" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">exemplos: kube-proxy · NLB</text>
  <text x="235" y="106" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">vê: IP, porta, conexão — e só</text>
  <text x="235" y="130" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">+ rápido, barato, milhões de conexões</text>
  <text x="235" y="150" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">− cego a HTTP: não vê rota, header nem "%"</text>
  <text x="235" y="170" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#b91c1c">não consegue fazer canary por porcentagem</text>

  <!-- L7 panel -->
  <rect x="460" y="40" width="410" height="140" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="665" y="64" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#26215C">L7 — aplicação (HTTP/2, gRPC)</text>
  <text x="665" y="84" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">exemplos: NGINX (borda) · ALB · Envoy (malha)</text>
  <text x="665" y="106" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5a55a0">vê: rota, header, método — e peso por requisição</text>
  <text x="665" y="130" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">+ roteia por conteúdo: 95%/5%, por rota, por header</text>
  <text x="665" y="150" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">− um salto a mais: custo de CPU e ~ms de latência</text>
  <text x="665" y="170" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">é aqui que o canary acontece</text>

  <!-- Mesh: canary split -->
  <text x="450" y="212" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">A malha do TechPix durante o canary de 14/11</text>
  <rect x="40" y="230" width="150" height="56" rx="9" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="115" y="253" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#26215C">Pagamentos</text>
  <text x="115" y="271" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">chama análise de risco</text>
  <line x1="190" y1="258" x2="255" y2="258" stroke="#4338ca" stroke-width="2" marker-end="url(#a6t-arrow)"/>
  <rect x="257" y="230" width="160" height="56" rx="9" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
  <text x="337" y="253" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#26215C">Envoy (sidecar L7)</text>
  <text x="337" y="271" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">pesos: 95 / 5</text>
  <line x1="417" y1="245" x2="530" y2="245" stroke="#a8a29e" stroke-width="2" marker-end="url(#a6t-gray)"/>
  <text x="473" y="237" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#78716c">95%</text>
  <rect x="532" y="222" width="200" height="46" rx="9" fill="#f5f5f4" stroke="#a8a29e" stroke-width="2"/>
  <text x="632" y="242" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#57534e">rota antiga — módulo no monólito</text>
  <text x="632" y="259" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#78716c">ainda decide para 95%</text>
  <line x1="417" y1="272" x2="530" y2="290" stroke="#166534" stroke-width="2" marker-end="url(#a6t-green)"/>
  <text x="473" y="294" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">5%</text>
  <rect x="532" y="278" width="200" height="46" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="632" y="298" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">serviço novo de Antifraude</text>
  <text x="632" y="315" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">K8s · GPU · banco próprio</text>

  <!-- Argo Rollouts control -->
  <rect x="120" y="330" width="220" height="50" rx="9" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="230" y="351" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#7a5c00">Argo Rollouts (juiz)</text>
  <text x="230" y="369" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">consulta Prometheus · ajusta os pesos</text>
  <line x1="300" y1="330" x2="330" y2="292" stroke="#d4a017" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#a6t-arrow)"/>
  <text x="352" y="322" font-family="sans-serif" font-size="10" fill="#7a5c00">1% → 5% → 25% → 100% (ou rollback)</text>

  <rect x="40" y="396" width="820" height="30" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="450" y="416" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">A fachada do Strangler Fig da Aula 2 ERA um balanceador L7 — o Envoy é a mesma ideia, agora ao lado de cada serviço, com o Istio como plano de controle.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O canary de 1% é, fisicamente, um peso num balanceador de camada 7 — a camada 4 não enxerga porcentagem de requisição.</p>
</div>

### 4.3 Anatomia dos 90 segundos — a Lei de Little cobra de novo

Agora eu pago a dívida da abertura: *por que* a primeira tentativa falhou às 9h17 de 14 de novembro?

O time dimensionou o pool de conexões do serviço novo com a ferramenta certa — a Lei de Little, L = λ × W, que vocês carregam desde a Aula 1. Com o canary a 5% do tráfego — que naquela sexta, véspera de dia 15, já rodava perto do pico de 900 TPS desde cedo —, chegava ao serviço algo como λ = 45 transações por segundo. A latência interna da análise, medida no módulo dentro do monólito, era W ≈ 40 ms. L = 45 × 0,04 = **1,8 conexões simultâneas** em média. O pool foi configurado com 10 — folga de mais de cinco vezes. Parecia sobrado.

O erro não foi a lei; foi o **W de outro sistema**. Dentro do monólito, a consulta de features rodava com cache em processo, quente há meses. O serviço extraído estreou com um salto de rede a mais até a feature store — e, pior, com o **cache local nascendo vazio**. Cache frio significa miss atrás de miss; cada miss vira ida ao banco da feature store; com fila, o W real da análise no serviço novo abriu para algo em torno de 250 ms nos primeiros minutos. Refaçam a conta comigo: L = 45 × 0,25 = **11,25**. Pool de 10. Esgotou — e vocês conhecem essa história desde o dia 5 da Aula 2: requisição espera pool, espera aumenta W, W maior aumenta L, L maior espera mais pool. O cotovelo da curva de filas, em miniatura, dentro de um canary de 5%.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 860 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="430" y="24" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">A Lei de Little cobra de novo: L = λ × W — a lei estava certa; o W era de outro sistema</text>
  <!-- Planejado -->
  <rect x="30" y="45" width="380" height="220" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="220" y="70" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">PLANEJADO (W herdado do monólito)</text>
  <text x="220" y="95" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">λ = 45 TPS · W = 40 ms (cache quente, em processo)</text>
  <text x="220" y="118" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">L = 45 × 0,04 = 1,8 conexões</text>
  <!-- barra pool -->
  <rect x="70" y="140" width="300" height="30" rx="4" fill="#fff" stroke="#166534"/>
  <rect x="70" y="140" width="54" height="30" rx="4" fill="#86efac"/>
  <text x="97" y="160" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#14532d">1,8</text>
  <text x="220" y="188" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">pool = 10 → folga de mais de 5× · "parecia sobrado"</text>
  <text x="220" y="230" text-anchor="middle" font-family="sans-serif" font-size="24" fill="#166534">✓</text>
  <!-- Real -->
  <rect x="450" y="45" width="380" height="220" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="640" y="70" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">REAL (estreia: cache local vazio)</text>
  <text x="640" y="95" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">λ = 45 TPS · W ≈ 250 ms (miss atrás de miss + fila)</text>
  <text x="640" y="118" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#b91c1c">L = 45 × 0,25 = 11,25 conexões</text>
  <!-- barra pool estourada -->
  <rect x="490" y="140" width="300" height="30" rx="4" fill="#fff" stroke="#b91c1c"/>
  <rect x="490" y="140" width="300" height="30" rx="4" fill="#fca5a5"/>
  <line x1="790" y1="132" x2="790" y2="178" stroke="#b91c1c" stroke-width="2.5"/>
  <rect x="790" y="140" width="38" height="30" fill="#dc2626"/>
  <text x="640" y="160" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f1d1d">pool 10 lotado</text>
  <text x="809" y="160" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#fff">+1,25</text>
  <text x="640" y="188" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">esgota → espera pool → W sobe → L sobe → espera mais</text>
  <text x="640" y="206" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">p99: 80 ms → 2,4 s (o dia 5 da Aula 2, em miniatura)</text>
  <text x="640" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#b91c1c">guarda viola → rollback automático em 90 s</text>
  <text x="430" y="288" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">Correção (21/11): pool dimensionado com o W medido no dual-run + regra dos 70% · warm-up de cache no readiness · começar em 1%</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O erro de dimensionamento das 9h17: a mesma conta, com o W errado e com o W real — e por que a rede transformou o erro num parágrafo de runbook.</p>
</div>

O p99 saltou de 80 ms para 2,4 s, a métrica de guarda (p99 acima do orçamento da aresta) violou por três janelas seguidas, e o Argo Rollouts reverteu: 90 segundos entre a primeira violação e 100% do tráfego de volta na rota antiga. **Custo do erro: zero clientes afetados além do p99 momentâneo numa fração de 5%, e uma manhã de análise.** No mundo sem canary, esse mesmo erro a 100% do tráfego, no pico do almoço, seria o dia 5 de novo.

A segunda tentativa, dia 21, mudou três coisas — todas anotadas no runbook da Seção 6: o pool foi redimensionado com o W *medido no serviço real* durante o dual-run (não o W herdado do monólito), com a regra dos 70% de utilização máxima por cima; o serviço passou a **aquecer o cache antes de entrar no balanceador** (readiness que só libera tráfego depois de popular as features das contas mais ativas); e a progressão começou em 1%, não 5%. Subiu limpo, fatia por fatia, e às 16h o Antifraude estava a 100% na rota nova.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 320" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a6can-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- Tentativa 1 -->
  <text x="20" y="26" font-family="sans-serif" font-size="13" font-weight="bold" fill="#b91c1c">14/11 — primeira tentativa: a rede funciona</text>
  <line x1="40" y1="70" x2="860" y2="70" stroke="#ccc" stroke-width="2"/>
  <circle cx="120" cy="70" r="7" fill="#4338ca"/>
  <text x="120" y="50" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">9h17</text>
  <text x="120" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">canary a 5%</text>
  <circle cx="330" cy="70" r="7" fill="#d4a017"/>
  <text x="330" y="50" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">+ segundos</text>
  <text x="330" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">p99: 80 ms → 2,4 s</text>
  <circle cx="550" cy="70" r="7" fill="#b91c1c"/>
  <text x="550" y="50" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">3 janelas</text>
  <text x="550" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">guarda violada (p99 &gt; orçamento)</text>
  <circle cx="780" cy="70" r="9" fill="#166534"/>
  <text x="780" y="50" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#333">9h19</text>
  <text x="780" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">rollback automático — 90 s</text>
  <path d="M 550 62 C 620 30, 700 30, 772 60" stroke="#b91c1c" stroke-width="2" stroke-dasharray="5 4" fill="none" marker-end="url(#a6can-red)"/>
  <text x="660" y="32" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">Argo Rollouts reverte; humano é notificado DEPOIS</text>
  <text x="450" y="122" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">zero clientes afetados além do p99 momentâneo em 5% · custo: uma manhã de análise</text>

  <!-- Tentativa 2 -->
  <text x="20" y="160" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">21/11 — segunda tentativa: sobe limpo (com o runbook corrigido)</text>
  <line x1="40" y1="230" x2="860" y2="230" stroke="#ccc" stroke-width="2"/>
  <!-- degraus -->
  <rect x="80" y="212" width="90" height="18" fill="#bbf7d0" stroke="#166534"/>
  <text x="125" y="203" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">1%</text>
  <rect x="210" y="200" width="110" height="30" fill="#86efac" stroke="#166534"/>
  <text x="265" y="192" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">5%</text>
  <rect x="360" y="185" width="140" height="45" fill="#4ade80" stroke="#166534"/>
  <text x="430" y="177" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">25%</text>
  <rect x="540" y="168" width="200" height="62" fill="#22c55e" stroke="#166534"/>
  <text x="640" y="160" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">100% — 16h</text>
  <text x="450" y="250" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">mínimo 1h por fatia, guarda observada em cada degrau — nenhuma violação</text>
  <rect x="40" y="266" width="820" height="38" rx="6" fill="#fef9e7" stroke="#d4a017"/>
  <text x="450" y="282" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">Mudanças entre as tentativas (anotadas no runbook): pool com W medido no serviço real + regra dos 70% ·</text>
  <text x="450" y="297" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">warm-up de cache no readiness (só recebe tráfego quente) · progressão começando em 1%</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">As duas tentativas de novembro: o rollback de 90 segundos não foi fracasso — foi a rede de validação fazendo o trabalho dela.</p>
</div>

Reparem na moral, porque ela é o coração da aula: **o erro da primeira tentativa não foi evitável por mais planejamento — era um desconhecido honesto (quem saberia o W real antes de rodar?). O que era evitável era o erro virar incidente. A rede de validação transformou um erro de dimensionamento em um parágrafo de runbook.**

---

## 5. Fitness functions viram tecido contínuo

A Aula 2 apresentou fitness functions como testes de característica arquitetural — o ArchUnit travando um import proibido no CI, o monitor de p99 em produção. Naquela altura, elas eram verificações pontuais: rodavam quando alguém rodava. A extração muda a natureza delas: com dois (logo três) serviços evoluindo em paralelo, **a validação deixa de ser um evento e vira um tecido — algo que está sempre rodando, em todas as camadas, sem depender de alguém lembrar.**

Olhem o caminho completo de uma mudança no TechPix de hoje, e onde cada verificação mora:

| Etapa | Verificação que roda | De qual aula ela veio |
|---|---|---|
| Pull request | Testes de unidade e de invariante: Σ débitos = Σ créditos como teste, saldo nunca negativo, unicidade de EndToEndId | Aula 1 (invariantes), Aula 2 (fitness function) |
| Pull request | ArchUnit / lint de dependência: módulo não importa módulo, serviço não referencia schema alheio; varredura de GRANTs de banco | Aula 2, endurecida na Seção 2.1 de hoje |
| Pull request | Contract testing (Pact): o consumidor da aresta valida que o provedor não quebrou o contrato | Aula 4 |
| Publicação de evento | Schema registry rejeita evento incompatível com a versão registrada | Aula 3 (conceito), Aula 4 (aplicado) |
| Merge no repo de deploy | ArgoCD sincroniza; drift detection contínuo daí em diante | Hoje, Seção 3 |
| Pós-deploy, pré-release | Smoke test: bateria mínima contra o código novo ainda sem tráfego real (deploy ≠ release rendendo de novo) | Hoje |
| Release em fatias | Métricas de guarda do canary julgadas pelo Argo Rollouts | Hoje, Seção 4 |
| Produção, para sempre | Monitor de p99 por aresta, taxa de divergência de reconciliação de dados, consumer lag, invariante Σ verificada sobre o ledger em job contínuo | Aulas 2, 4 e a próxima |

A frase que resume, e que eu quero que vocês levem para a empresa de vocês: **pipeline não é esteira de empacotamento; é uma sequência de tribunais.** Cada etapa é um juiz com poder de veto, cada veto é barato porque acontece cedo, e a mudança que chega a 100% do tráfego passou por todos. O professor das primeiras aulas plantou a semente com um nome — Harness, o arreio — e disse que vocês colheriam na Aula 8. O que a gente construiu hoje é a parte mecânica dessa colheita: os tribunais existem e funcionam. O que ainda falta — julgar mudanças propostas por não-humanos, e julgar com rigor estatístico — é exatamente o que falta de aula.

---

## 6. O artefato: o Runbook de Extração

Toda aula desse curso fecha com um artefato — ADRs nas Aulas 1 e 2, a spec de contexto na Aula 3, o Contrato de Integração na Aula 4, o Model Card na Aula 5. O de hoje nasceu da diferença entre as duas tentativas de novembro: tudo que a primeira ensinou, a segunda executou por escrito. É o **Runbook de Extração** — o checklist reutilizável que transforma "extrair um serviço" de aventura em procedimento:

```
RUNBOOK DE EXTRAÇÃO DE SERVIÇO · TechPix · v1.1 (revisado após 21/11/2025)

PRÉ-CONDIÇÕES (nenhum passo adiante sem TODAS)
  [ ] Fronteira estável: zero mudanças de contrato da aresta nos últimos 3 meses
  [ ] Contrato de Integração da aresta escrito e em vigor (Aula 4)
  [ ] Time dono nomeado, com plantão definido
  [ ] Fallback da aresta definido POR ESCRITO e testado em game day
  [ ] Justificativa de escala/autonomia registrada (por que extrair este, agora)

PLANO DE DADOS
  [ ] Banco próprio provisionado; usuário SEM grants em schemas alheios (verificado por CI)
  [ ] Escrita dupla via eventos do Outbox ativada
  [ ] Backfill: lotes, throttling, idempotente e retomável; janela fora de pico
  [ ] Dual-run com critério de saída PRÉ-DECLARADO (TechPix: divergência < 0,01% por 7 dias)
  [ ] Reconciliação diária velho×novo, com alerta de divergência

PLANO DE RELEASE
  [ ] Flag de lançamento (off) + kill switch testados
  [ ] Pool e recursos dimensionados com W MEDIDO NO SERVIÇO REAL (dual-run), regra dos 70%
  [ ] Warm-up de caches no readiness — serviço só recebe tráfego quente
  [ ] Canary 1% → 5% → 25% → 100%, mínimo 1h por fatia
  [ ] Guardas pré-declaradas: erro > baseline 0,1%; p99 > orçamento da aresta
  [ ] Rollback automático configurado e ENSAIADO antes da release

SAÍDA (contract)
  [ ] 100% por 14 dias sem violação de guarda
  [ ] Escrita dupla desligada; rota antiga removida
  [ ] Tabelas velhas: arquivar → esperar 30 dias → remover
  [ ] Retrospectiva escrita; runbook atualizado com o que se aprendeu
```

Reparem no espírito: quase todas as linhas desse runbook são cicatrizes. "W medido no serviço real" é a cicatriz das 9h17. "Fuso horário" não aparece literalmente, mas "reconciliação diária com alerta" é a cicatriz do 0,4%. Runbook bom não é escrito; é *acumulado*.

E a prova de que ele funciona veio rápido: semanas depois, o time da Marina extraiu o **Pagamentos** — o orquestrador, com as ACLs de DICT e SPI, os timeouts herdados do teto de 40 segundos, o circuit breaker que a Aula 2 pediu e a Aula 4 formalizou. Uma extração objetivamente mais delicada que a do Antifraude. Sabem o que eu tenho para contar sobre ela? **Quase nada.** Seguiu o runbook, item por item. O dual-run pegou uma divergência pequena de arredondamento na conversão de valores da ACL (centavos, literalmente), corrigida antes de qualquer cliente existir na história. O canary subiu em um dia, sem uma violação de guarda. A extração mais arriscada do sistema rendeu três parágrafos de retrospectiva, e é assim que se mede maturidade: **drama tendendo a zero enquanto o risco intrínseco continua alto.**

O TechPix de hoje, então: **Antifraude e Limites** como serviço (com GPU e modelo), **Pagamentos** como serviço (com as portas para o mundo), e o monólito remanescente segurando **Contas e Ledger** — a conta `pix_a_liquidar` no lugar onde sempre esteve —, além de Identidade, Devoluções e Cartões, cada um aguardando seus critérios maturarem. Ou não: **monólito remanescente não é fila de espera; é lar legítimo de quem não tem razão para sair.**

E antes de fechar, deixa eu fazer uma coisa que eu gosto de fazer no fim de toda migração: olhar para trás com o catálogo na mão. Todos esses padrões que a gente vem aplicando têm nome de prateleira — estão catalogados no **microservices.io**, do Chris Richardson, que é a referência que eu quero que vocês levem para a segunda-feira. E reparem no que o mapa revela: o TechPix não "adotou microsserviços" hoje. Ele vem acumulando os padrões do catálogo desde a Aula 1, **um por dor, nunca por moda** — hoje só entraram os dois últimos.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="440" y="24" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333">Os padrões de microservices.io aplicados ao TechPix — aula a aula</text>

  <g font-family="sans-serif">
    <rect x="20" y="48" width="204" height="72" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="122" y="70" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">Event Sourcing</text>
    <rect x="86" y="80" width="72" height="18" rx="9" fill="#f5f5f4" stroke="#a8a29e"/>
    <text x="122" y="93" text-anchor="middle" font-size="10" font-weight="bold" fill="#57534e">Aula 1</text>
    <text x="122" y="113" text-anchor="middle" font-size="9.5" fill="#666">o log é a verdade; saldo é projeção</text>

    <rect x="232" y="48" width="204" height="72" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="334" y="70" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">Strangler Fig</text>
    <rect x="298" y="80" width="72" height="18" rx="9" fill="#f5f5f4" stroke="#a8a29e"/>
    <text x="334" y="93" text-anchor="middle" font-size="10" font-weight="bold" fill="#57534e">Aula 2</text>
    <text x="334" y="113" text-anchor="middle" font-size="9.5" fill="#666">fachada L7 migrando tráfego aos poucos</text>

    <rect x="444" y="48" width="204" height="72" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="546" y="70" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">Transactional Outbox</text>
    <rect x="510" y="80" width="72" height="18" rx="9" fill="#f5f5f4" stroke="#a8a29e"/>
    <text x="546" y="93" text-anchor="middle" font-size="10" font-weight="bold" fill="#57534e">Aula 2</text>
    <text x="546" y="113" text-anchor="middle" font-size="9.5" fill="#666">evento gravado na mesma transação ACID</text>

    <rect x="656" y="48" width="204" height="72" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="758" y="70" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">CQRS</text>
    <rect x="722" y="80" width="72" height="18" rx="9" fill="#f5f5f4" stroke="#a8a29e"/>
    <text x="758" y="93" text-anchor="middle" font-size="10" font-weight="bold" fill="#57534e">Aula 2</text>
    <text x="758" y="113" text-anchor="middle" font-size="9.5" fill="#666">escrita forte; leitura via Redis/réplica</text>

    <rect x="20" y="132" width="204" height="72" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="122" y="154" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">Circuit Breaker</text>
    <rect x="80" y="164" width="84" height="18" rx="9" fill="#f5f5f4" stroke="#a8a29e"/>
    <text x="122" y="177" text-anchor="middle" font-size="10" font-weight="bold" fill="#57534e">Aulas 2 · 4</text>
    <text x="122" y="197" text-anchor="middle" font-size="9.5" fill="#666">DICT sob timeout; política por aresta</text>

    <rect x="232" y="132" width="204" height="72" rx="8" fill="#fff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="334" y="154" text-anchor="middle" font-size="12" font-weight="bold" fill="#26215C">Saga</text>
    <rect x="298" y="164" width="72" height="18" rx="9" fill="#f5f5f4" stroke="#a8a29e"/>
    <text x="334" y="177" text-anchor="middle" font-size="10" font-weight="bold" fill="#57534e">Aula 4</text>
    <text x="334" y="197" text-anchor="middle" font-size="9.5" fill="#666">devolução com compensação, sem 2PC</text>

    <rect x="444" y="132" width="204" height="72" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="546" y="154" text-anchor="middle" font-size="12" font-weight="bold" fill="#166534">Database per Service</text>
    <rect x="504" y="164" width="84" height="18" rx="9" fill="#dcfce7" stroke="#166534"/>
    <text x="546" y="177" text-anchor="middle" font-size="10" font-weight="bold" fill="#166534">Aula 6 · hoje</text>
    <text x="546" y="197" text-anchor="middle" font-size="9.5" fill="#15803d">banco próprio; GRANT alheio proibido no CI</text>

    <rect x="656" y="132" width="204" height="72" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="758" y="154" text-anchor="middle" font-size="12" font-weight="bold" fill="#166534">Canary + Service Mesh</text>
    <rect x="716" y="164" width="84" height="18" rx="9" fill="#dcfce7" stroke="#166534"/>
    <text x="758" y="177" text-anchor="middle" font-size="10" font-weight="bold" fill="#166534">Aula 6 · hoje</text>
    <text x="758" y="197" text-anchor="middle" font-size="9.5" fill="#15803d">fatias via Envoy/Istio, juiz automático</text>
  </g>

  <rect x="20" y="226" width="840" height="52" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="440" y="248" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#7a5c00">Cada padrão entrou quando uma dor concreta o exigiu — nunca antes: Event Sourcing pela conservação do dinheiro, Outbox pela escrita dupla,</text>
  <text x="440" y="266" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#7a5c00">Saga pela devolução entre instituições, Database per Service porque agora a rede separa os donos dos dados.</text>

  <text x="440" y="308" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">catálogo completo: microservices.io/patterns (Chris Richardson) — padrão sem dor que o justifique é moda, não arquitetura</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O mapa integrador: oito padrões do catálogo microservices.io, cada um marcado com a aula — e a dor — em que entrou no TechPix.</p>
</div>

---

## 7. Para fechar: três ideias-âncora

Primeiro: **extração é evidência, não estilo.** O Antifraude saiu porque quatro critérios observáveis mandaram — fronteira estável, escala diferente, time dono, contrato pronto. O Ledger ficou porque nenhuma evidência mandou ele sair. A pendência do ADR-002 segue aberta, e abrir mão de fechá-la sem dados foi a decisão mais arquitetural da aula.

Segundo: **os dados são a extração de verdade.** Código se move num deploy; dados se movem com expand/contract, escrita dupla, backfill idempotente, dual-run com critério pré-declarado e reconciliação contínua — a disciplina que o TechPix aprendeu com o BACEN na Aula 1, apontada para dentro.

Terceiro: **deploy não é release, e a rede de validação é o que separa erro de incidente.** GitOps fez o deploy virar um log imutável reconciliado — o ledger operando infraestrutura. Flags e canary fizeram a release virar um dial com juiz automático. E o rollback das 9h19 provou o ponto da aula inteira: num sistema com rede, a primeira tentativa *pode* falhar — por isso mesmo ela pôde ser tentada numa sexta-feira de manhã.

O gancho para a próxima aula, e eu quero que vocês percebam que ele esteve na aula inteira sem eu nomear: o canary decidiu com base em métricas. O dual-run decidiu com base em métricas. A reconciliação alerta com base em métricas. Tudo hoje foi julgado por números que alguém, em algum lugar, teve que coletar direito — com a fração de segundo certa, o percentil certo, o rótulo certo. **Quem gera esses números? Onde eles moram? E como se acha, no meio de 900 transações por segundo, um único Pix anormalmente lento?** Na próxima aula, a gente abre a caixa que faz todo o resto ser possível: observabilidade. Tragam o pager.

E o retrato de fim de aula, na régua de sempre — olhem o quanto a fintech cresceu hoje, e olhem também para a caixa âmbar, porque o que a gente **decidiu não mexer** é tão arquitetural quanto o que subiu:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 342" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="440" y="22" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333">O TechPix ao fim da Aula 6</text>

  <text x="20" y="44" font-family="sans-serif" font-size="10" font-weight="bold" fill="#a8a29e">JÁ EXISTIA — AULAS 1 A 5</text>
  <g font-family="sans-serif">
    <rect x="20" y="52" width="278" height="46" rx="8" fill="#f5f5f4" stroke="#d4a017" stroke-width="2"/>
    <text x="159" y="70" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Monólito: Contas e Ledger</text>
    <text x="159" y="87" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#7a5c00">Postgres · pix_a_liquidar · FICA — pendência ADR-002 aberta</text>
    <rect x="307" y="52" width="278" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="446" y="70" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Outbox → Kafka + read models</text>
    <text x="446" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">Redis (saldo) · réplica (extrato) · [A2]</text>
    <rect x="594" y="52" width="266" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="727" y="70" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Bounded contexts + specs</text>
    <text x="727" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">context map · constituição Spec Kit · [A3]</text>

    <rect x="20" y="104" width="278" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="159" y="122" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Contratos por aresta</text>
    <text x="159" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">gRPC/.proto · schema registry · DLQ · [A4]</text>
    <rect x="307" y="104" width="278" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="446" y="122" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Modelo ML + feature store</text>
    <text x="446" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">GPU · Redis online · shadow mode · [A5]</text>
    <rect x="594" y="104" width="266" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="727" y="122" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Defesas de resiliência</text>
    <text x="727" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">circuit breaker · bulkhead · retry budget · [A2·A4]</text>
  </g>

  <text x="20" y="176" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">CONSTRUÍDO NESTA AULA</text>
  <g font-family="sans-serif">
    <rect x="20" y="184" width="278" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="159" y="204" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Antifraude como serviço</text>
    <text x="159" y="221" text-anchor="middle" font-size="9.5" fill="#15803d">Kubernetes · GPU · banco próprio</text>
    <rect x="307" y="184" width="278" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="446" y="204" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Pagamentos como serviço</text>
    <text x="446" y="221" text-anchor="middle" font-size="9.5" fill="#15803d">ACLs DICT/SPI · database-per-service</text>
    <rect x="594" y="184" width="266" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="727" y="204" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">ArgoCD · GitOps</text>
    <text x="727" y="221" text-anchor="middle" font-size="9.5" fill="#15803d">Git = estado desejado · rollback = revert</text>

    <rect x="20" y="240" width="278" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="159" y="260" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Canary via Envoy/Istio + Unleash</text>
    <text x="159" y="277" text-anchor="middle" font-size="9.5" fill="#15803d">1%→5%→25%→100% · rollback automático</text>
    <rect x="307" y="240" width="278" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="446" y="260" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Fitness functions contínuas</text>
    <text x="446" y="277" text-anchor="middle" font-size="9.5" fill="#15803d">Σ · ArchUnit · Pact · GRANTs — no CI, sempre</text>
    <rect x="594" y="240" width="266" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="727" y="260" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Runbook de Extração</text>
    <text x="727" y="277" text-anchor="middle" font-size="9.5" fill="#15803d">extração como procedimento, não aventura</text>
  </g>

  <text x="440" y="322" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">cinza = já existia · verde = construído nesta aula · âmbar = decisão explícita de NÃO mexer</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A régua de evolução do TechPix: a Aula 6 tirou dois contextos do monólito com rede de validação — e deixou o Ledger onde a evidência mandou deixar.</p>
</div>

---

## Apêndice — Termos novos desta aula

| Termo | O que é |
|---|---|
| **GitOps** | Operar infraestrutura com o estado desejado declarado em Git; produção converge para o que o repositório diz. |
| **ArgoCD** | Operador de GitOps: reconcilia continuamente o estado observado do cluster contra o declarado no Git. |
| **Reconciliação contínua** | O loop comparar-convergir-comparar; a mesma estrutura ledger/projeção da Aula 1 aplicada a deploy. |
| **Drift** | Divergência entre o que está rodando e o que o Git declara — detectada e, com selfHeal, desfeita. |
| **Deploy vs release** | Deploy: código novo em produção. Release: tráfego em cima dele. Separá-los cria a zona de validação. |
| **Feature flag de lançamento** | Interruptor que libera gradualmente uma rota nova sem novo deploy (Unleash no TechPix). |
| **Kill switch** | Flag inversa: desliga um caminho instantaneamente; o freio de emergência do on-call, testado em game day. |
| **Canary (mecânico)** | Release em fatias 1%→5%→25%→100% com métricas de guarda pré-declaradas e juiz automático (Argo Rollouts). A matemática fina fica com a Aula 8. |
| **Rollback automático** | Violou guarda → reverte primeiro, notifica depois. Os 90 segundos da abertura. |
| **Database-per-service** | Cada serviço com banco próprio; ler banco alheio é proibido e verificado por fitness function (ausência de GRANT). |
| **Escrita dupla (controlada)** | Fase da migração em que o caminho velho decide e os eventos alimentam o banco novo em paralelo. |
| **Backfill** | Cópia do histórico para o banco novo: em lotes, com throttling, idempotente e retomável. |
| **Dual-run** | Velho decide de verdade, novo decide "de mentira"; divergência medida contra critério pré-declarado. O shadow mode da Aula 5 aplicado a migração. |
| **Expand/contract (dados)** | Coreografia da Aula 4 aplicada a schemas e bancos: expandir, migrar, só contrair no fim. |
| **Smoke test** | Bateria mínima pós-deploy, pré-release: valida o código novo antes de existir tráfego real nele. |
| **Entrega progressiva** | O guarda-chuva: flags + canary + rollback automático — release como processo graduável, não como salto. |
| **Runbook de Extração** | O artefato da aula: checklist reutilizável que transforma extração de aventura em procedimento. Acumulado, não escrito. |
| **Balanceador L4 vs L7** | L4 (kube-proxy, NLB) enxerga conexões TCP — rápido e cego a HTTP; L7 (NGINX, Envoy, ALB) enxerga rota, header e método — é quem consegue fazer o traffic-split percentual do canary. |
| **Service mesh (Envoy/Istio)** | Malha de sidecars L7 entre serviços: o Envoy acompanha cada pod e o Istio orquestra — timeout, retry, mTLS e o split do canary saem do código e viram configuração da malha. |
| **microservices.io** | Catálogo de padrões de microsserviços de Chris Richardson — a prateleira de onde o TechPix vem tirando um padrão por dor desde a Aula 1: Event Sourcing, Strangler Fig, Transactional Outbox, CQRS, Circuit Breaker, Saga, Database per Service. |

---

[← Aula 5](aula5-conteudo-completo.md) · [Índice](index.md) · [Aula 7 →](aula7-conteudo-completo.md)
