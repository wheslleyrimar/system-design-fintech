---
layout: default
title: "Aula 9 — Guia de perguntas difíceis"
---

# Aula 9 — Guia de perguntas difíceis
*Munição para quando a plateia técnica empurrar. Segurança atrai dois tipos de ceticismo: "isso é exagero" e "isso não é suficiente". As duas objeções têm resposta.*

---

## Sobre a premissa

**"Isso tudo é caro demais para uma fintech pequena. Onde eu começo?"**

Comece pelo que tem melhor razão custo/benefício e pelo que o incidente já provou. Ordem prática: (1) **autorização por recurso + teste adversarial** — é código, custa dias e fecha a falha nº 1 de APIs; (2) **tokens curtos, segredos fora do repositório e scanner no CI** — quase de graça; (3) **MFA/device binding e limites transacionais** — barram takeover e limitam dano; (4) **trilha de auditoria estruturada**; (5) só depois, mesh, HSM próprio, antifraude com ML. A aula diz explicitamente que service mesh é prematuro com poucos serviços. O critério é **proporcionalidade ao risco**, não completude de checklist.

**"Não é mais simples só colocar um WAF e um bom API Gateway na frente?"**

WAF e Gateway pegam ataques **de formato** (injeção, payload gigante, token inválido). O incidente do Bruno é uma requisição **perfeitamente bem-formada** com um valor semanticamente errado — nenhum WAF sabe que `acc-2207` não é dele. Ownership é dado de domínio; levá-lo ao Gateway o transforma num monólito de regras. Edge é a primeira camada, não a única.

---

## Sobre identidade e tokens

**"JWT é stateless por definição. Se eu preciso consultar o servidor para revogar, não perdi a vantagem?"**

Perdeu parte, e a aula afirma isso. A resposta é graduar: token de vida curta (5–15 min) dispensa consulta na maioria das chamadas; refresh token revogável fica no servidor de identidade; e **introspecção/lista de revogação só para operações de alto valor**. Você paga a ida à rede onde o risco justifica, e não em toda requisição.

**"Por que não usar sessão em servidor e esquecer JWT?"**

É legítimo, especialmente para o canal web do próprio banco. O trade-off é escala e acoplamento: sessão de servidor exige estado compartilhado e um ponto central consultado a cada chamada — que vira dependência do caminho crítico. JWT curto + refresh é o compromisso mais comum para APIs distribuídas. O erro não é escolher um; é achar que qualquer dos dois resolve autorização de recurso.

**"SMS como segundo fator não é melhor que nada?"**

É, e ainda é melhor que só senha. Mas contra o adversário real — SIM swap, engenharia social na operadora — é fraco, e em contexto de dinheiro irreversível "melhor que nada" não é o critério. Device binding com chave em hardware resolve por outro princípio: a prova deixa de ser "sabe um número" e passa a ser "possui uma chave que nunca sai do aparelho".

**"Se a assinatura de transação já barra o Bruno, por que também precisamos de autorização por recurso?"**

Porque cada camada pega variantes que a outra deixa passar. A assinatura não protege endpoints que não a exigem (leitura de extrato, por exemplo — BOLA de leitura), nem chamadas de serviço-para-serviço, nem operações legítimas que o usuário assinou mas que o domínio proíbe (conta bloqueada, limite excedido). Defesa em profundidade significa não depender de que a camada anterior esteja correta.

---

## Sobre autorização

**"Devolver 403 não confirma que o recurso existe? Não deveria ser sempre 404?"**

Depende do modelo de ameaça, e a aula diz para decidir conscientemente. 404 evita enumeração de IDs (bom contra sondagem); 403 é mais claro para o cliente legítimo que errou. Para recursos cujo ID é adivinhável ou sequencial, prefira 404 **e** IDs não sequenciais (UUID). O que não pode acontecer é o comportamento variar de endpoint para endpoint.

**"Autorização em toda chamada não destrói a performance?"**

Custa uma consulta a mais, mas ela é barata se desenhada bem: o vínculo titular–conta muda raramente, então cabe cache curto e invalidável; e a checagem acontece **dentro** do serviço dono do dado, sem salto de rede extra. Compare com o custo da alternativa: no Pix, um erro dessa classe é dinheiro irreversível. E note: se o antifraude cabe em ~100 ms, uma consulta de ownership em microssegundos cabe.

**"ABAC/ReBAC parecem over-engineering. Por que não só RBAC + ownership?"**

Para muitos sistemas é exatamente isso, e a aula diz "o mais simples que exprime a regra". ABAC entra quando a regra depende de **contexto** (valor, hora, risco); ReBAC, quando há **relações** (conta conjunta, procuração). Se você não tem esses casos, não os implemente. O risco inverso também existe: política complexa demais que ninguém audita deixa de proteger.

---

## Sobre workloads, mTLS e mesh

**"Se já temos mTLS, por que precisamos de policy? O canal já é autenticado."**

Porque autenticar o peer só responde "quem é você". Sem policy, **qualquer workload autenticado pode chamar qualquer endpoint de qualquer outro**. Um Antifraude comprometido, com certificado perfeitamente válido, chamaria `POST /pix` no Pagamentos. Policy limita o *que* cada identidade pode fazer — é o menor privilégio no eixo leste-oeste.

**"Service mesh não é over-engineering? Meu time tem 6 pessoas."**

Muito provavelmente é, e a aula afirma que ele não é obrigatório. A regra de decisão: adote quando o custo transversal (certificados, rotação, policies, telemetria em N serviços) já dói mais do que operar a plataforma. Com poucos serviços críticos, mTLS por biblioteca, network policies do Kubernetes e um cofre de segredos entregam a maior parte do valor com uma fração da complexidade. **Primeiro sinta a dor da repetição, depois compre a plataforma.**

**"O sidecar adiciona latência. No Pix, cada milissegundo conta."**

Conta, e é por isso que o custo aparece na tabela de trade-offs (+1–3 ms/salto). Mitigações: reuso de conexão (o handshake caro acontece uma vez, não por requisição), modo *ambient* sem sidecar, e aplicar mTLS pleno só no caminho crítico. Se o p99 estourar o orçamento, a revisão do ADR-004 prevê a alternativa. Latência de segurança é um custo a orçar, não um tabu.

**"Client Credentials não é só uma senha de máquina? Muda o quê?"**

Muda três coisas: **escopo mínimo** (o token só permite `risco:avaliar`, não tudo), **vida curta** (minutos, não indefinida) e **rastreabilidade** (o log mostra *qual* serviço agiu). Uma senha global de backend tem poder total, vive para sempre e não distingue chamador. E, combinada com mTLS, o token deixa de ser o único elo: roubar o token sem o certificado do pod não basta.

---

## Sobre dados, chaves e a lei

**"Se o banco já é criptografado em disco, por que criptografar campos?"**

Criptografia de volume protege contra roubo do disco ou snapshot. Com o banco em execução, qualquer DBA, aplicação com acesso ao banco ou atacante com dump lógico vê o claro. Criptografia de campo protege contra **acesso legítimo demais**: o dado só é decifrável por quem tem permissão na chave — e o uso da chave é auditado.

**"Crypto-shredding é mesmo aceito juridicamente como eliminação?"**

Essa é a pergunta certa, e a resposta honesta é: **não é decisão só de engenharia.** A arquitetura fornece a *capacidade* de tornar o dado irrecuperável sem quebrar a integridade do ledger; se isso satisfaz a obrigação de eliminação, e *quando* a eliminação é devida (há bases legais de retenção, como prevenção à fraude e obrigações regulatórias), é interpretação jurídica. Levem ao jurídico com o desenho na mão. O que não tem correção elegante é um ledger que já misturou dado contábil e pessoal no mesmo campo — daí "desde o dia 1".

**"Tokenização e criptografia não são a mesma coisa?"**

Não. Dado cifrado ainda *é* o dado, reversível por quem tem a chave; um token não tem relação matemática com o original, e só o cofre sabe o mapeamento. A consequência prática é o **escopo de conformidade**: os sistemas que só veem tokens ficam fora da auditoria do dado real.

**"Por que HMAC no webhook e não simplesmente confiar em TLS e no IP de origem?"**

TLS protege o canal, não prova *quem* enviou a mensagem — qualquer um que conheça a URL pode abrir uma conexão TLS válida. IP de origem é falsificável ou muda (provedores usam faixas dinâmicas). O HMAC prova que quem enviou conhece o segredo, e o timestamp + id único impedem o **replay** de uma mensagem legítima capturada.

---

## Sobre antifraude

**"Antifraude com ML resolve tudo. Para que regras?"**

Regras entram em produção em minutos quando surge um golpe novo, são explicáveis a um auditor e a um cliente, e cobrem o urgente e o conhecido. O modelo cobre o difuso, mas é probabilístico, depende de dado rotulado e sofre *concept drift* — o fraudador se adapta. A combinação é a resposta; e cada decisão de bloqueio precisa ser explicável, porque um bloqueio injustificável é problema jurídico.

**"Fail-open no antifraude não é convidar o ataque?"**

Um atacante que descobrisse como derrubar o antifraude poderia explorar isso — por isso a aula defende **graduar por valor**: fail-open apenas com limite agregado baixo (perda máxima conhecida e pequena), fail-closed para valores altos. E o limite agregado é o que impede que a indisponibilidade do antifraude vire esvaziamento de contas. A decisão precisa estar num ADR, com números.

**"Como evitar que fraudador descubra meus limiares?"**

Não expor as regras exatas nas respostas de erro ("bloqueado por limite noturno de R$ 1.000" ensina o atacante), variar limiares com componentes aleatórios/contextuais, e sobretudo usar **sinais agregados por janela** — o *structuring* (fracionar abaixo do limite) é exatamente o que a agregação detecta.

---

## Sobre insiders e auditoria

**"Quatro olhos e acesso JIT deixam a operação lenta. Em incidente, isso mata."**

Por isso existe o **break-glass**: acesso de emergência que dispara alerta, grava a sessão e expira em minutos. A pergunta não é "acesso rápido ou seguro"; é "rápido *e visível*". E a operação rotineira (que é 95% do volume) tem aprovação automatizada por regra; o quatro-olhos pesa só nas operações que movem dinheiro ou alteram controles.

**"Se o administrador tem acesso ao banco de logs, não pode adulterar a trilha?"**

Pode — por isso a cadeia de hashes sozinha não basta. A âncora em armazenamento **WORM**, numa conta que o operador não administra, com verificação periódica automática, impede a reescrita silenciosa. E a segregação de funções vale aqui: quem opera o sistema não administra a auditoria dele.

**"A trilha de auditoria não é dado pessoal? Como guardar por anos?"**

É, e por isso ela guarda **identificadores estáveis, não dados sensíveis** (o id do cliente, não o CPF), com acesso restrito e os próprios acessos auditados. Retenção de anos é exigência de setor; o desenho de camadas quente/fria controla o custo.

---

## Sobre testes e regressão

**"Como eu testo que 'nenhum endpoint esquece a autorização' se são centenas?"**

Com uma **fitness function** estrutural: teste de arquitetura que varre os controllers e falha o build se um método público recebe parâmetro de identificador de objeto sem anotação de política. Complementada por uma suíte adversarial parametrizada (usuário A × objeto de B em cada rota). A verificação deixa de depender da memória de quem viveu o incidente.

**"Testes de segurança não são responsabilidade do time de pentest?"**

Pentest é valioso e complementar, mas é *pontual*: acha o que existe no dia. Fitness functions são *contínuas* — impedem que a falha volte na próxima refatoração. Um pentest que encontra um BOLA deveria gerar, como saída, um teste automatizado permanente.

---

## Perguntas de fechamento (para a plateia)

- "JWT válido significa operação autorizada?" — **Não: significa identidade verificada.**
- "Quem controla o `accountId` do body?" — **O cliente; logo, nunca é confiável.**
- "Quem é o Antifraude dentro do cluster?" — **A identidade do workload, provada por certificado — não o IP, não a rede.**
- "mTLS significa que o Antifraude pode fazer qualquer coisa?" — **Não: significa que sabemos quem ele é; a policy diz o que pode.**
- "Uma credencial válida pode ter poder demais?" — **Sim; e é o que o menor privilégio e o raio de explosão limitam.**
- "Como provamos que a vulnerabilidade não voltou?" — **Fitness function no CI que falha quando ela reaparece.**
- "O golpe em que a própria vítima paga passa por todos os controles de permissão?" — **Sim; só o controle baseado em risco o vê.**
