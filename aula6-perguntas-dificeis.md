---
layout: default
title: "Aula 6 — Guia de perguntas difíceis"
---

# Aula 6 — Guia de perguntas difíceis
*Munição de embasamento para quando a plateia técnica empurrar.*

---

## Sobre a decisão de extrair

**"Por que não reescrever tudo de uma vez? O monólito já mostrou os limites dele no dia 5."**

Porque o big bang rewrite aposta o sistema inteiro numa única validação — a final, em produção, com todos os clientes ao mesmo tempo. O histórico da indústria com essa aposta é péssimo, e numa fintech o downside não é "site fora do ar", é dinheiro parado e incidente regulatório. A extração incremental faz o caminho contrário: cada passo é pequeno, tem critério de saída pré-declarado, roda em dual-run antes de valer e reverte em segundos se a guarda violar. Reparem que o dia 5, aliás, não condenou o monólito — condenou o ponto quente do ledger e o DICT síncrono, e ambos foram tratados *dentro* do monólito com o ADR-002. A reescrita total troca um risco conhecido e fatiável por um risco desconhecido e indivisível. A assimetria de Fowler continua valendo: extrair tarde custa um refactor; reescrever tudo e errar custa a empresa.

**"Por que o Ledger não sai? Não é covardia deixar o núcleo no legado?"**

É o contrário de covardia — é a decisão com mais evidência da aula. O ledger carrega a invariante transacional Σ débitos = Σ créditos em nível serializable; colocar rede no meio disso significa trocar uma transação ACID local por saga com compensação ou two-phase commit, pagando latência e fragilidade para resolver um problema que *ninguém demonstrou existir*: o p99 de escrita está dentro do SLA. "Está no monólito" não é sinônimo de "está errado" — monólito remanescente é lar legítimo de quem não tem razão para sair. E tem o ponto de sequência: se um dia a escrita do ledger precisar mudar — e a linha de revisão do ADR-002 continua aberta exatamente para isso —, essa tem que ser a última extração, feita pela equipe mais calejada, com a melhor rede de validação. Decidir isso hoje, sem os dados, seria repetir o pecado que o curso passou seis aulas condenando.

**"Antifraude primeiro parece conveniente demais. Não era mais valioso extrair Pagamentos, que é quem fala com o mundo?"**

Mais valioso, talvez; mais sensato, não. A ordem de extração não otimiza valor do serviço — otimiza custo do erro durante o aprendizado. O Antifraude tinha a aresta com fallback escrito e testado: se a extração desse errado, o Contrato de Integração já dizia o que fazer (fail-closed para valor alto, fail-open com limite baixo para valor pequeno). Errar ali custava degradação controlada. O Pagamentos concentra as ACLs de DICT e SPI e os timeouts herdados do teto de 40 segundos — errar ali custa Pix não liquidado. A gente extraiu primeiro onde errar era barato, converteu o aprendizado em runbook, e a extração do Pagamentos rendeu três parágrafos de retrospectiva. Isso não é sorte; é sequenciamento.

**"Vocês criaram um distributed monolith: Pagamentos chama Antifraude de forma síncrona no caminho crítico. Cadê a independência?"**

A crítica seria correta se a chamada síncrona fosse acoplamento não gerenciado — e é exatamente por isso que a Aula 4 veio antes desta. A aresta Pagamentos↔Antifraude é síncrona por decisão de domínio (a análise de risco precisa acontecer antes de reservar fundos), não por preguiça, e é governada por contrato: orçamento de ~100 ms p99, timeout, retry budget, circuit breaker e fallback de negócio. Distributed monolith é quando a falha de um serviço arrasta o outro sem plano; aqui, a falha do Antifraude degrada o fluxo segundo uma política escrita — o sistema continua decidindo, só que mais conservador. Independência total entre serviços que participam do mesmo fluxo de dinheiro é fantasia; o que existe é dependência explícita, orçada e com plano B. Essa é a diferença entre acoplamento e contrato.

## Sobre dados e migração

**"Escrita dupla não é exatamente o dual write problem que a Aula 2 mandou evitar?"**

Boa pegada — e a resposta está em *quem* escreve a segunda via. O dual write problem da Aula 2 é a aplicação escrevendo em dois lugares na mesma operação sem atomicidade: se a segunda escrita falha, os dois mundos divergem silenciosamente. A escrita dupla da migração não faz isso: o monólito escreve *uma vez*, na transação local, e o evento sai pelo Outbox — a mesma transação ACID garante que o fato e o evento existem juntos. O banco novo é populado por um consumidor desse stream, idempotente, com dedup por EndToEndId. Se o consumidor cair, o evento espera; se processar duas vezes, o efeito é um. Ou seja: não são duas escritas concorrentes, é uma escrita com uma projeção assíncrona — o desenho do ADR-002, reutilizado. E ainda assim a gente não confia cegamente: a reconciliação diária existe porque "deveria estar certo" não é um controle.

**"Divergência de 0,01% por sete dias como critério de saída — de onde saiu esse número? Não é tão chutado quanto o fator de pico da Aula 1?"**

É calibrado, não deduzido — e a diferença importa. O 0,01% veio de baixo para cima: o time mediu a divergência *irredutível* do dual-run, aquela causada por corridas benignas de timing (evento chegando milissegundos antes ou depois do corte de janela), e ela ficava em torno de 0,003%. O critério foi posto três vezes acima desse chão: folga para ruído, sensibilidade para erro real — e o caso do fuso horário provou a sensibilidade, estourando o critério em quarenta vezes. Os sete dias cobrem um ciclo completo de padrões semanais, incluindo o fim de semana e um dia útil de pico. Vocês têm razão que há juízo de engenharia embutido; a diferença para o chute é que o número tem uma referência medida embaixo e um evento que o testou. Critério pré-declarado imperfeito ainda ganha, por muito, de critério nenhum.

**"Backfill idempotente e retomável é fácil de falar. Na prática, reprocessar lotes não corrompe agregados?"**

Corrompe, se o backfill fizer *incremento* — e é por isso que ele não pode fazer. A regra prática: backfill escreve por upsert com chave natural determinística (conta, janela, tipo de agregado), nunca por "soma mais um". Reprocessar o lote produz exatamente o mesmo registro, byte a byte — efeito exactly-once por construção, a lição da Aula 1 aplicada a ETL. O caso do fuso horário da TechPix é o exemplo perfeito: quando o corte de meia-noite foi corrigido, o time simplesmente rodou o backfill inteiro de novo por cima, e os upserts substituíram os agregados errados pelos certos. Se o backfill fosse incremental, a correção exigiria limpar tudo e torcer. Backfill que não pode ser rodado duas vezes é backfill que vai dar errado na única vez que importa.

## Sobre GitOps e ArgoCD

**"GitOps não é burocracia? Antes eu rodava um script e o deploy saía; agora preciso de PR, revisão e um operador no meio."**

Concedo o ponto de latência: um hotfix que era um comando virou um commit revisado. Mas comparem o que se compra. O script manual produz um sistema cujo estado é o acúmulo de ações que pessoas lembram de ter feito — e às 3h da manhã, com o pager tocando, "o que está rodando agora?" não tem resposta confiável. No GitOps a resposta é `git log`, sempre. O rollback deixa de ser um script separado que ninguém testa e vira o mesmo mecanismo do deploy, exercitado todo dia. E numa fintech tem o argumento que encerra a discussão: o BACEN e o auditor perguntam "o que rodava no dia X e quem aprovou" — com GitOps isso é uma consulta; sem, é arqueologia. A burocracia que vocês sentem é o custo visível; o que ela substitui é um custo invisível que só aparece no pior dia possível. E para o incêndio real existe o kill switch, que não passa por PR nenhum.

**"selfHeal desfazendo mudança manual no cluster é perigoso: e se o on-call PRECISAR de um ajuste imediato e o ArgoCD ficar revertendo?"**

Cenário real, e a TechPix trata com hierarquia de mecanismos, não com fé. Primeiro: as intervenções de emergência legítimas — desligar uma rota, reduzir tráfego — têm mecanismo próprio que não passa pelo cluster: feature flag e kill switch, avaliados em runtime, fora do alcance do selfHeal. Segundo: para o caso raro de precisar mesmo mexer em recurso do cluster, o procedimento é pausar o sync da aplicação no ArgoCD (uma ação, auditada) antes do ajuste — o operador para de convergir até alguém religar. O que o selfHeal impede não é a emergência; é a emergência *virar estado permanente não documentado*. O ajuste heroico de madrugada, no mundo antigo, ficava lá para sempre e ninguém sabia; agora ele ou vira commit na segunda-feira ou desaparece — e as duas saídas são corretas. O perigo que vocês descrevem existe, mas a resposta é desenhar a válvula de escape, não abrir mão da reconciliação.

**"Repositório de deploy separado do repositório de código dobra o trabalho. Por quê?"**

Porque muda quem decide o quê — e isso vale o segundo repositório. Mudar *o que o serviço faz* é decisão do time de produto/engenharia; mudar *o que está rodando em produção* — versão, réplicas, recursos, flags de infra — é decisão de operação, com revisores diferentes e, numa fintech, com trilha de auditoria própria. Juntar os dois no mesmo repo mistura os dois fluxos: todo merge de feature vira potencialmente um evento de produção, e o auditor que pergunta "quem aprovou essa mudança de produção" recebe um PR de refactor com 40 arquivos. Separando, o `git log` do repo de deploy é, literalmente, o diário de bordo de produção — só mudanças de estado operacional, uma por commit. O custo real é manter a referência de versão entre os dois (o CI faz: build publica imagem, abre PR no repo de deploy). É trabalho a mais na tubulação, uma vez, em troca de clareza permanente na pergunta mais cara da operação.

## Sobre canary, flags e a rede de validação

**"Canary a 1% de 900 TPS são 9 transações por segundo. Isso dá amostra estatística para decidir alguma coisa?"**

Resposta honesta: para detectar regressão *grossa*, dá; para afirmar "a rota nova é tão boa quanto a velha" com rigor, não dá — e a TechPix sabe disso. A 9 TPS, uma hora de fatia são ~32 mil transações: um p99 que saltou de 80 ms para 2,4 s aparece em minutos com significância sobrando (foi exatamente o caso das 9h17), e uma taxa de erro que dobrou também. O que NÃO aparece é o defeito raro — o evento de 1 em 100 mil precisa de horas só para ocorrer algumas vezes. Por isso as regras de hoje são conservadoras e fixas: mínimo de uma hora por fatia, qualquer violação reverte, e ninguém trata canary limpo como prova de equivalência — ele é um detector de desastre, não um atestado de qualidade. Quantas transações provam o quê, o perigo de espiar o resultado antes da hora, quando um guardrail dispensa estatística — essa matemática o professor da Aula 8 faz com vocês, com esses mesmos 900 TPS na mão. Hoje eu entrego o mecanismo calibrado para a direção segura.

**"Rollback automático me assusta: e se a métrica de guarda der falso positivo e o sistema ficar revertendo release boa?"**

Acontece, e o custo desse falso positivo é deliberadamente baixo — essa é a chave do desenho. Reverter uma release boa custa: a rota antiga (que funcionava) volta, o time perde algumas horas e tenta de novo. Não reverter uma release ruim custa: clientes com Pix degradado até um humano acordar, olhar, decidir. A assimetria é brutal, e ela justifica calibrar a guarda para o lado sensível. Dito isso, falso positivo em série é um sintoma que a gente monitora: se a mesma release reverte duas vezes sem causa encontrada, o runbook manda parar e investigar a *guarda* — janela curta demais, baseline contaminado, métrica com cardinalidade errada. E reparem no detalhe de ordem: reverte primeiro, notifica depois. O humano nunca está no caminho crítico da segurança; ele está no caminho da melhoria. Prefiro explicar de manhã por que a máquina foi conservadora do que explicar por que ninguém agiu às 3h.

**"Feature flag acumula: daqui a um ano vocês vão ter cinquenta flags mortas e ninguém vai saber o que pode apagar."**

Verdade — flag é dívida técnica com juros, e quem diz o contrário nunca operou um sistema com flags. A disciplina da TechPix tem três pontos. Primeiro: toda flag de lançamento nasce com data de expiração e dono; flag expirada aparece em relatório semanal, e remover a flag (e a rota morta que ela guardava) é parte da definição de pronto da extração — está no runbook, na seção de saída. Segundo: kill switches são a exceção — são permanentes por natureza, então são poucos, nomeados, documentados no Contrato de Integração da aresta e testados em game day para não apodrecerem. Terceiro: a fitness function ajuda — flag sem avaliação nos últimos 30 dias gera alerta de limpeza. O estado terminal saudável de uma flag de lançamento é *não existir*; o de um kill switch é existir e ser ensaiado. Cinquenta flags mortas não são um destino, são uma escolha de não ter processo.

**"O warm-up de cache no readiness resolve o cold start — mas não mascara o problema real, que é o serviço depender de cache quente para cumprir o orçamento?"**

Excelente objeção, e a resposta é: sim, a dependência existe e foi *aceita por escrito*, não mascarada. O orçamento de ~100 ms p99 da aresta com inferência de modelo dentro só fecha com a feature store respondendo de cache — ir ao banco a cada consulta não cabe, e fingir que cabe seria o mascaramento de verdade. A decisão registrada no Contrato de Integração é: cache é componente de primeira classe do caminho crítico, com as consequências tratadas — warm-up no readiness (instância nova não recebe tráfego fria), e o comportamento sob miss coberto pelo fallback de negócio (análise indisponível dentro do prazo → fail-closed para valor alto). O que as 9h17 ensinaram não foi "cache é perigoso"; foi que o W da Lei de Little tem que ser medido no sistema real, incluindo o cache frio do pior momento. A alternativa estrutural — feature store com latência de banco no p99 — existe, custa outra arquitetura de dados, e ninguém demonstrou que o preço vale. Dependência explícita e orçada, de novo, ganha de dependência negada.

## Sobre o processo e o custo

**"Dual-run, backfill, reconciliação, canary de dias... isso dobra o custo de infra e triplica o prazo. Como eu justifico para a diretoria?"**

Com a conta do outro lado, que ninguém apresenta junto. O custo do processo é visível e finito: semanas de infra duplicada para o contexto em migração (não para o sistema inteiro), e um prazo maior por extração. O custo que ele substitui é invisível até acontecer e ilimitado quando acontece: o erro de fuso horário decidindo antifraude errado em produção por semanas, o pool subdimensionado derrubando o caminho de Pix no pico — cada um desses, num PSP, é prejuízo direto mais exposição regulatória, e o dia 5 da Aula 2 já mostrou o tamanho disso. A moldura para a diretoria não é "processo caro vs processo barato"; é "pagar um seguro com preço de tabela vs correr risco com cauda aberta". E tem o argumento de velocidade que parece paradoxal e é o mais forte: a segunda extração, do Pagamentos — a mais delicada do sistema —, saiu em dias e sem drama *por causa* do runbook que a primeira pagou. Processo de validação não é o freio; é o que permite pisar no acelerador sem medo. Rotina é mais rápida que heroísmo.

**"Noventa segundos de rollback ainda são noventa segundos de p99 ruim para os clientes do canary. Isso não é 'afetar cliente'?"**

É — e eu não vou maquiar: durante aquelas janelas, uma fração dos 5% viu a análise de risco lenta, e alguns Pix atravessaram o timeout da aresta e caíram no fallback. O ponto não é que o canary zera o impacto; é que ele *limita e distribui* o impacto por desenho. Façam a conta: 5% do tráfego, por ~4 minutos entre início da degradação e fim do rollback, com o fallback de negócio funcionando (nenhuma transação decidida errado — as de valor alto falharam fechado, as pequenas passaram com limite baixo, conforme a política da Aula 4). Comparem com a alternativa: a mesma regressão a 100%, descoberta no pico do almoço, sem rota antiga para voltar. O canary não é a promessa de que ninguém sente nada; é a garantia de que o pior caso tem teto baixo e reversão automática. Em sistema de dinheiro, honestidade sobre isso importa: a gente não vende risco zero — vende risco com contorno desenhado e pago conscientemente.
