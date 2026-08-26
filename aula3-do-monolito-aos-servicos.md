---
layout: default
title: "Aula 3 — Do monólito aos serviços: modelagem de domínio com 20 pessoas e pouco dinheiro"
---

# Aula 3 — Do monólito aos serviços: modelagem de domínio com 20 pessoas, pouco dinheiro e o BACEN olhando

*Curso de Arquitetura de Sistemas Financeiros com IA · versão evolutiva da Aula 3*

> **Navegação:** [Índice](index.md) · [Aula 1](aula1-conteudo-completo.md) · [Aula 2](aula2-conteudo-completo.md) · [Aula 3 — conteúdo completo](aula3-conteudo-completo.md) · **Aula 3 — do monólito aos serviços (você está aqui)** · [Aula 4](aula4-conteudo-completo.md)

> **Sobre os números desta aula.** Os valores de custo que aparecem aqui — R$ 50 mil, R$ 3.400 por mês, R$ 2.500 por mês — são um cenário hipotético, montado para a discussão. Não são cotação de fornecedor nem tabela de preço da AWS. O que eu quero que vocês levem não é o número; é a estrutura do raciocínio: o que entra na conta, o que fica escondido, e em que momento uma decisão vira outra.

Eu quero começar esta aula de um jeito diferente do que está no [conteúdo completo](aula3-conteudo-completo.md). Lá, eu começo pelo substantivo errado — a palavra "conta" significando duas coisas para dois times — e vou construindo a técnica até chegar, na seção 8, na pergunta que toda turma faz: "bounded context é microsserviço?". Hoje eu quero inverter o caminho. Quero começar pela pergunta, porque ela chegou para a TechPix de um jeito muito concreto, numa reunião de planejamento, e a resposta passa por tudo o que a aula ensina — mas passa numa ordem que faz mais sentido para quem está sentado na cadeira de quem decide.

A situação é esta. A TechPix tem hoje **vinte desenvolvedores**. O sistema é **um binário Go** — `cmd/techpix` —, **um Postgres**, **um deploy**. Quinze módulos dentro de `internal/modules/`. Tudo sobe com `docker compose up`. Isso foi uma escolha, e uma boa escolha, registrada no ADR-002: começar por um monólito, porque não tínhamos nem o problema de escala nem o problema de autonomia de times que justifica separar processos. Só que vinte pessoas num único deploy é o tamanho exato em que alguém, na reunião, diz a frase: *"a gente devia começar a quebrar isso em microsserviços"*.

E na mesma reunião, porque a vida é assim, o financeiro pergunta se vamos comprar servidor ou alugar nuvem, e o compliance lembra que somos uma instituição que opera Pix, e que o Banco Central tem opinião sobre continuidade, backup, segurança cibernética e onde os dados moram.

Três pressões de uma vez: a de **organização** (vinte pessoas geram fila de deploy), a de **dinheiro** (somos pequenos; a fatura dos próximos dezoito meses importa), e a **regulatória** (o BACEN não pergunta se somos monólito ou microsserviço — pergunta se temos um plano para quando cair). Esta aula é o que acontece quando a gente leva as três a sério ao mesmo tempo.

A tese que eu vou defender, e que vocês vão poder verificar no repositório `fintechdev-aula-3` no fim, é simples de enunciar e difícil de praticar: **a decisão "microsserviços sim ou não" é a última da lista, não a primeira.** Antes dela vêm três outras — *onde* rodar, *com o quê* rodar, e *quais são as fronteiras de verdade* do nosso domínio. E a terceira dessas, que é o tema desta aula, é a única que não muda seja qual for a resposta das outras. Quem pula as três e vai direto para a última costuma acertar a topologia e errar o sistema.

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

Vamos reler a linha do on-premises com os olhos de quem vai operar isso às três da manhã.

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

O Regulamento do Pix acrescenta requisitos de disponibilidade e tempo de resposta, e um detalhe que sempre surpreende a turma: conectar ao SPI não é abrir uma porta HTTPS. É rede privada, a RSFN. Uma fintech pequena normalmente não faz isso sozinha — ou contrata um **PSTI**, um provedor de tecnologia homologado, ou entra no Pix como **participante indireto**, liquidando por meio de um participante direto. Essa decisão de negócio muda o módulo `bacen` mais do que qualquer decisão sobre microsserviços. O simulador `bacen-sim` do repositório finge exatamente essa fronteira externa.

Agora coloquem os dois cenários lado a lado contra essa lista. On-premises com dois servidores: vocês escrevem, implementam e operam todos os controles; a continuidade exige o segundo par de máquinas num segundo local; a política de segurança é inteiramente responsabilidade de vocês. Na nuvem com serviços gerenciados: vocês escrevem a política, mas boa parte dos controles técnicos vem pronta e auditada — o modelo de responsabilidade compartilhada —; Multi-AZ no banco e réplicas da aplicação são configuração, não compra; a burocracia da contratação existe, mas é papel, não hardware.

A frase que eu quero que fique: **o regulador não está do lado da nuvem; ele está do lado de quem prova continuidade.** Com vinte pessoas, provar continuidade num datacenter próprio custa gente e hardware que a gente não tem. Na nuvem custa configuração e contrato. É por isso — e não por moda — que a maioria das fintechs pequenas começa em nuvem e vai para on-premises ou híbrido só quando a escala inverte a conta.

### 1.3 A decisão

A decisão da TechPix, registrada para a turma: **AWS, sob demanda nos três primeiros meses; compromisso de uso só sobre o que não muda.** Sob demanda primeiro porque ainda não sabemos o tamanho certo — a Lei de Little da Aula 1, pool igual a TPS vezes latência, dá o ponto de partida, mas só o tráfego real dá o tamanho. Compromisso sobre o Postgres depois de estabilizar, porque ele é a parte que a seção 6 vai mostrar que não muda mesmo se a aplicação virar serviços. E reavaliar on-premises ou híbrido no dia em que a fatura mensal ultrapassar o salário de uma pessoa de infraestrutura dedicada. Antes disso, a nuvem *é* a pessoa de infraestrutura.

---

## 2. Com o quê rodar: a stack, decisão por decisão

A segunda pergunta é a que vocês vão receber no primeiro emprego, na forma de uma lista: vamos usar Linux? Docker? Kubernetes? Kafka? E a resposta didática nunca é "sim" ou "não". É "sim ou não, *porque*, e *até quando*". A regra que organiza esta seção inteira é: **toda escolha tem um gatilho de revisão escrito.** Sem gatilho, a escolha vira dogma — e dogma é como se chega tanto no "Kubernetes desde o dia um" quanto no "nunca vamos precisar de Kubernetes".

Vou percorrer a stack da TechPix camada por camada. Muito disso já está no repositório; o que eu estou fazendo é explicitar o raciocínio que está implícito no `Dockerfile`, no `docker-compose.yml` e no `main.go`.

**Linguagem: Go.** Binário estático, sem runtime para instalar, consumo de memória baixo — a instância pequena da nuvem serve —, concorrência nativa para o pipeline outbox/relay da Aula 2. Mas o motivo que mais importa para esta aula é uma regra do compilador: o diretório `internal/`. Um pacote dentro de `internal/` só pode ser importado por quem está acima dele na árvore. Isso vai virar, na seção 5, a nossa fronteira de módulo verificada pelo compilador. O gatilho para trocar de linguagem: nunca por moda; talvez para um contexto específico, e a seção 6 vai mostrar qual.

**Sistema operacional: Linux.** Alpine dentro do container; a distribuição do host é problema do provedor. O `Dockerfile` do repositório diz tudo: `golang:1.25-alpine` compila, `alpine:3.20` roda, o processo sobe como usuário sem privilégio — `app`, uid 10001 —, e a imagem final tem só `ca-certificates`, `tzdata` e `curl` para o health check. Uns quinze megabytes, superfície de ataque mínima, que é exatamente o que a política de segurança cibernética pede. O gatilho: se aparecer dependência em C, trocar Alpine por Debian slim. Nunca voltar a rodar fora de container.

**Empacotamento: Docker, sim.** A mesma imagem no laptop dos vinte desenvolvedores, no CI e em produção. Elimina o "na minha máquina funciona". E é a decisão que **mantém as opções abertas**: qualquer orquestrador futuro consome essa mesma imagem. Não há gatilho — container é o piso, não uma fase.

**Orquestração: Kubernetes, ainda não.** Esta é a resposta que mais surpreende, então deixa eu ser preciso. Kubernetes resolve o problema de *muitos* serviços heterogêneos que precisam de placement, service discovery e rollout independentes. A TechPix tem **um** serviço. O que ganharíamos hoje seria uma curva de aprendizado para vinte pessoas que precisam entregar Pix, e algo como R$ 400 por mês de plano de controle. O que temos hoje: um container em ECS/Fargate, ou uma VM Linux com `systemd` e o próprio compose. O gatilho é objetivo: **o terceiro serviço extraído**, ou o primeiro contexto que precise de autoscaling independente. E quando o gatilho disparar, a migração é um sprint, porque a imagem já existe. Reparem: Docker sem Kubernetes não é contradição. Docker faz o *artefato* ser o mesmo em todo lugar; Kubernetes *coordena muitos artefatos*. A gente tem um.

**Banco: PostgreSQL 17, gerenciado, Multi-AZ, um cluster, um schema por contexto.** O ADR-001 exige que reservar fundos e registrar a idempotência aconteçam na mesma transação — o ledger é ACID, serializable, append-only. Um banco só é o que torna isso trivial; entre processos, seria 2PC ou saga. E os schemas separados — `identidade`, `limites`, `devolucoes`, cada um sem chave estrangeira para fora — já desenham o corte futuro, sem executá-lo. O gatilho: um contexto extraído leva o schema dele para um banco próprio, o que é assunto da Aula 6. O ledger fica.

**Migrations: SQL embutido no binário**, aplicado no boot (`migrations/embed.go`). A versão do schema anda com a versão do código, sem ferramenta externa. O gatilho: no dia em que houver dois deploys independentes escrevendo no mesmo banco, migration vira um pipeline separado.

**Mensageria: nenhum broker.** Outbox no Postgres e um relay dentro do processo. A Aula 2 mostrou que a outbox transacional garante que o evento existe se a transação existiu; um consumidor no mesmo processo não precisa de Kafka. Kafka gerenciado custa na casa de R$ 1.500 por mês e é uma disciplina operacional inteira. O gatilho: o **primeiro consumidor fora do processo**. Nesse dia a tabela de outbox vira a fonte de um tópico, sem mudar o produtor — é a beleza do padrão.

**Cache: em memória, no processo.** O cache do DICT com TTL já existe. Cache distribuído resolve um problema que ainda não temos, porque temos uma réplica. O gatilho: a segunda réplica da aplicação.

**Borda: load balancer gerenciado com TLS e WAF.** Terminação TLS, health check no `/healthz` que já existe, proteção básica. É o item mais barato da lista e o primeiro que uma auditoria pergunta. Gateway ou BFF só quando houver mais de um serviço atrás — a camada 2 da [topologia progressiva](topologia-progressiva.md).

**Segredos e chaves: gerenciador de segredos e KMS; o certificado ICP-Brasil que assina mensagens para o SPI mora num HSM gerenciado.** Chave privada de assinatura **nunca** vive em variável de ambiente. Isso não é preferência; é exigência de segurança cibernética. Sem gatilho.

**Observabilidade: `slog` em JSON para o serviço de logs; métricas no formato Prometheus; tracing só dentro do processo.** O `main.go` já loga JSON estruturado, e o p99 do caminho de pagamento já é uma fitness function (`P99_ALVO_MS`). O gatilho para tracing distribuído é o dia em que a chamada em memória virar rede — Aula 7.

**Infraestrutura como código: Terraform desde o primeiro dia.** O regulador pergunta "como você reconstrói isso?". A resposta tem que ser um repositório, não uma pessoa.

**CI/CD: a cada pull request, `go test ./...` e `make test-arch`; build da imagem; deploy com aprovação.** Os testes de arquitetura da seção 5 só valem se rodarem no PR. Uma fronteira que ninguém verifica evapora em seis semanas.

**Ensaio de carga: k6**, com o `scripts/k6_degrau.js` que reproduz o degrau da Aula 2. Medir antes de dimensionar.

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

Quinze diretórios. Cada um é um pacote Go com um `api.go` — o contrato público — e um `internal/` — o que ninguém de fora enxerga. E a regra não é convenção: importar `ledger/internal/store` a partir de `pix` **não compila**. Ninguém escreve na tabela de lançamentos pelas costas do ledger, não por disciplina, mas por compilador. Isso é o ADR-002, "monólito modular, com fronteiras verificadas pelo compilador", e eu quero que vocês notem a data dele: foi escrito na Aula 1, quando decidimos começar pequeno, e já dizia em que condições seria revisto.

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

Cinco contextos e uma plataforma. As cores são o tipo de subdomínio da §1.5 do conteúdo completo: roxo é core, o que se constrói em casa com o melhor time; azul é genérico, o que se compra; verde é de suporte, o que se constrói simples; cinza é plataforma, o que não é domínio e não pode carregar regra de negócio. (Uma observação honesta: o conteúdo completo classifica Pagamentos como *supporting*, com o argumento de que o `pacs.008` é igual para todos; o `contextos.go` do repositório o marca como *core*, com o argumento de que a orquestração DICT/SPI é o produto. As duas leituras são defensáveis, e é exatamente o tipo de discussão que vale a sala.)

E agora a observação que liga isso à pergunta da reunião. **Vinte pessoas, cinco contextos.** Isso já é um organograma: um squad para cada contexto core — três —, e um squad de plataforma que também cuida de Identidade e Devoluções. Quatro squads de cinco. A Lei de Conway, que eu discuto na §7 do conteúdo completo, diz que a arquitetura vai convergir para o organograma de qualquer jeito. Então é melhor desenhar o organograma *a partir* dos contextos do que o contrário — o *Inverse Conway Maneuver* —, e isso está literalmente escrito no campo `Equipe` de cada contexto em `internal/platform/contextos/contextos.go`.

Reparem que a pergunta "vamos quebrar em serviços?" ainda não foi respondida. Mas ela já ficou mais precisa: virou "quais destes cinco contextos, se algum, precisam de um processo próprio?". E para responder isso, precisamos ter certeza de que os cinco são os cinco certos.

---

## 4. Modelar antes de cortar: o event storming que desenha as fronteiras

Aqui entra o tema da aula, e eu vou ser econômico porque o [conteúdo completo](aula3-conteudo-completo.md) trata cada uma dessas ideias em profundidade. O que eu quero acrescentar é a pergunta que a reunião colocou na frente de tudo: **se a gente for cortar, onde a gente corta?**

A frase "vamos quebrar em microsserviços" tem um pressuposto escondido: que a gente sabe onde estão as linhas. Na Aula 2 eu confessei que os módulos da TechPix foram desenhados no olho. Funcionou — as fronteiras de módulo quebravam o build — mas ninguém sabia dizer *por que aquela linha e não outra*. E o incidente que abre o repositório mostra o custo de não saber.

### 4.1 O bug que mora entre dois times

```bash
make demo-duas-carteiras
```

A Ana tem duas carteiras. O limite diário é R$ 1.000. O time de risco avaliava o limite "por conta"; para o ledger, "conta" é o pote contábil — a carteira. A Ana paga R$ 800 de cada uma. Os dois passam. Nenhuma linha de código está errada; o bug está **na palavra**, entre os times. É a falha de linguagem ubíqua da §1.1, e é a razão de a linguagem ser **por contexto**: "conta" é pote no Ledger e é palavra proibida em Limites, onde se diz `cliente` ou `carteira`; "cliente" é pessoa na Identidade e é proibida no Ledger. O `contextos.go` carrega essas proibições, e `tests/linguagem_test.go` quebra o build se alguém usar a palavra errada no lugar errado.

Agora eu quero que vocês imaginem esse mesmo bug com Limites e Ledger em **serviços separados**, times separados, repositórios separados. A palavra ambígua vira um campo num contrato JSON, e o erro não aparece num teste — aparece na conciliação do fim do mês, ou numa fiscalização. **Microsserviço não corrige fronteira errada; ele a torna permanente.** Esse é o primeiro argumento contra cortar antes de modelar.

### 4.2 O rio de eventos, e onde o dono muda

```bash
make demo-rio
```

A técnica para descobrir as fronteiras em vez de decretá-las é o **event storming** da §2: os fatos do domínio, no passado, em ordem, com quem publica cada um. Sobre o fluxo do Pix, o que sai é um rio: `PixIniciado → ChaveResolvida → LimitesValidados → FundosReservados → OrdemEnviadaAoSPI → PixLiquidado`, com `PixDevolvido` como ramo.

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

A fronteira não é uma linha que alguém traça. É **o lugar onde o dono do fato muda**. Agrupem os eventos por quem os publica e os cinco contextos da seção 3 aparecem sozinhos — e é por isso que o `contextos.go` lista, para cada contexto, os eventos que ele publica: o mapa é a saída do event storming, gravada como código.

### 4.3 Os quatro testes de fronteira, lidos com a pergunta da reunião

Uma fronteira candidata é boa quando passa nos quatro testes da §2.5. Eu quero reler cada um deles com a pergunta "e se fosse um serviço?", porque é assim que eles viram argumento na reunião.

O primeiro teste é **linguagem própria**: a mesma palavra muda de sentido ao cruzar a linha? Se a fronteira falha nesse teste e vocês extraíram um serviço, o contrato carrega uma ambiguidade que ninguém mais pode corrigir sem quebrar o vizinho. O segundo é **co-mutação baixa**, medida com `make comutacao` — pares de módulos que mudam no mesmo commit. Se falha e vocês extraíram, toda funcionalidade vira dois pull requests em dois repositórios e um deploy coordenado, que é o pior dos dois mundos. O terceiro é **a invariante fecha dentro**: a regra de negócio precisa de dado do outro lado para ser verificada? Se falha e vocês extraíram, a transação vira saga e a invariante passa a ser "quase sempre verdadeira", o que num sistema financeiro é a mesma coisa que falsa. O quarto é **contrato pequeno e estável**: quantas chamadas e eventos atravessam a linha, e com que frequência mudam? Se falha e vocês extraíram, é latência de rede a cada chamada de um contrato que muda toda semana.

Reparem no padrão: cada teste que uma fronteira *reprova* como módulo, ela reprova **muito mais caro** como serviço. É o segundo argumento para modelar antes de cortar.

### 4.4 O mapa de contexto não muda quando o módulo vira serviço

```bash
curl -s localhost:8080/v1/contextos | python3 -m json.tool | less
```

A §3 do conteúdo completo dá o vocabulário das relações: upstream decide, downstream respeita; customer/supplier, open host service, camada anticorrupção, published language, conformist. Na TechPix, o Ledger é upstream de quase todos. A Identidade é um *open host service* com um contrato minúsculo — "quem é o titular desta carteira?". O BACEN é *published language* (ISO 20022) atrás de uma **ACL**, o módulo `bacen`, e é o único vizinho que já é, hoje, outro sistema. E Pagamentos com Limites é a única conversa síncrona de alta banda, declarada no mapa como *colaboração* — com o aviso de que, se virar permanente, a fronteira está errada.

Agora a observação que resolve metade da reunião. Olhem para esse mapa e reparem que **ele não muda** se Limites virar um serviço amanhã. Os padrões, a direção das setas, os eventos publicados — tudo igual. O que muda é uma coluna: o campo `Meio` da relação em `contextos.go` sai de "síncrono, em memória" para "síncrono, pela rede". Isso é a frase central da §8, agora com o mapa na mão para prová-la: **bounded context é decisão de modelagem; serviço é decisão de topologia.** São decisões diferentes, tomadas por critérios diferentes, e confundi-las é a origem de boa parte dos projetos de microsserviços que dão errado.

### 4.5 Agregados: a fronteira que já desenha o corte

Dentro de um contexto, o agregado é a unidade de consistência — a §4 do conteúdo completo cobre as quatro regras de Vernon e a matemática da contenção, e eu recomendo a calculadora do painel para sentir o que 1 segundo de DICT dentro de um lock faz com a vazão. Para a discussão de hoje, a regra que importa é a terceira: **referenciar outros agregados por identidade, nunca por objeto.** Devoluções conhece um pagamento pelo E2E ID, não por uma chave estrangeira; Limites conhece um cliente por um id em texto, não por um join. É exatamente por isso que os schemas `devolucoes` e `limites` não têm FK para `pix_payments` nem para `accounts` — e é por isso que, se um dia esses contextos saírem para outro banco, o corte já está desenhado. O agregado bem feito é o pré-requisito silencioso de qualquer extração futura. Quem modela agregados grandes, com objetos atravessando contextos, descobre no dia da extração que não existe onde cortar.

---

## 5. Monólito modular *bem definido*: a garantia de serviço sem a conta de serviço

Chegamos à alternativa concreta aos microsserviços — e eu insisto no adjetivo: não é "monólito", é "monólito modular bem definido". A diferença entre os dois não é a intenção do arquiteto. É a existência de verificação.

Um bounded context que existe só no diagrama tem prazo de validade de mais ou menos seis semanas. Basta uma sexta-feira apertada, um `import` conveniente, e a fronteira que custou um dia de event storming vira ficção — e ninguém percebe, porque nada quebra na hora. O que separa um monólito modular de uma bola de lama é que, no primeiro, o `import` conveniente **não compila**. O repositório tem três camadas dessa defesa, e eu quero que vocês vejam as três rodando:

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

Agora comparem com o que microsserviços dariam "de graça": a fronteira de rede. Ela também impede o `import` conveniente — mas ao custo de latência, falha parcial, saga e tracing distribuído. **As três camadas acima compram a mesma garantia de fronteira por um preço que vinte pessoas podem pagar.** É isso que "monólito modular bem definido" significa nesta aula: a garantia de microsserviço sem a conta de microsserviço. E é o terceiro argumento — o decisivo — para não cortar antes de precisar.

Para quem não está em Go, a §9 do conteúdo completo tem a lista: ArchUnit em Java e Kotlin, Spring Modulith — que é literalmente um monólito modular com estas regras embutidas —, NetArchTest em .NET, import-linter em Python, dependency-cruiser em TypeScript, go-arch-lint em Go. O ponto não é a ferramenta. É rodar no pull request.

---

## 6. Decompor ou não: os quatro gatilhos, contexto a contexto

Agora sim a pergunta da reunião, respondida com o vocabulário que a aula construiu e não com opinião.

A §8 do conteúdo completo dá o critério: extrair um contexto para serviço próprio se justifica quando **pelo menos um** de quatro gatilhos dispara. O contexto precisa **escalar de forma diferente** do resto. O contexto tem **ciclo de deploy diferente** — muda dez vezes por dia enquanto o resto muda uma vez por semana. O contexto pertence a um **time diferente**, e o acoplamento de deploy virou fila entre times — este é, na prática, o motivo mais comum e mais legítimo. Ou o contexto tem **requisito de disponibilidade ou de isolamento de falha** distinto, que é o bulkhead da Aula 2 aplicado no nível de serviço.

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

Há uma assimetria que decide os casos de dúvida, e eu quero que ela fique na parede de vocês.

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

A **Fase 2** dispara pelo gatilho do Antifraude — um modelo de risco em produção, que pede outra linguagem, outro perfil de máquina, outro ciclo de deploy. É o primeiro serviço. E é aqui que a conta muda de patamar, porque o primeiro serviço traz consigo tudo o que um serviço exige: a outbox vira um tópico num broker, o schema `limites` vai para um banco próprio, aparecem OpenTelemetry e um gateway na borda. Mais R$ 3.000 a R$ 4.000 por mês. ECS ainda basta para dois serviços.

A **Fase 3** dispara por fila entre squads — medida em dias de espera de deploy, não em reclamação de retrospectiva. Com três ou mais serviços, Kubernetes se paga: placement, rollout independente, autoscaling por serviço. Mais R$ 2.000 por mês e, honestamente, mais uma pessoa, porque um cluster precisa de dono.

Olhem o que o desenho diz sobre custo: sair da Fase 0 para a Fase 3 multiplica a fatura mensal por três ou quatro e adiciona uma pessoa. Cada seta precisa de um gatilho medido — fila em dias, p99 em milissegundos, co-mutação em percentual. E reparem no que **não** muda em nenhuma das fases: o Ledger e o Postgres dele. É por isso que o compromisso de uso da seção 1 deveria cobrir o banco, e só o banco. Comprometam-se com o que não muda.

---

## 8. Fecho: a ordem certa das perguntas

Deixa eu amarrar o que a reunião de planejamento levou para casa.

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

## Apêndice — Onde cada seção se apoia no conteúdo completo

| Seção desta versão | Seções do [conteúdo completo](aula3-conteudo-completo.md) | Material do repositório |
|---|---|---|
| 1 · Onde rodar | nova; apoia-se na Aula 1 §3.5 (Lei de Little) e Aula 2 §5 (outbox) | `docker-compose.yml`, `Dockerfile` |
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
| **Monólito modular bem definido** | Um processo com fronteiras internas verificadas em três camadas — compilação, banco, publicação — no pull request. A garantia de serviço sem a conta de serviço. |
| **Assimetria da extração** | Virar serviço é um sprint; voltar a ser módulo é um projeto. Por isso o default é módulo. |
