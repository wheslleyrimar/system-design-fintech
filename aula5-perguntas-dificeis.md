---
layout: default
title: "Aula 5 — Guia de perguntas difíceis"
---

# Aula 5 — Guia de perguntas difíceis
*Munição de embasamento para quando a plateia técnica empurrar.*

---

## Sobre regra vs. modelo

**"Se o modelo pegou o golpe dos R$ 49,90 retroativamente, por que não aposentar as regras de vez?"**

Porque as camadas resolvem problemas diferentes, com custos diferentes. Regra dura custa microssegundos e tem zero falso positivo sobre o que é proibido por definição — conta encerrada não transaciona, ponto; gastar inferência nisso é desperdício de orçamento de latência. Além disso, as regras são a rede de segurança do modelo: a loja online de features tem atraso eventual de centenas de milissegundos, e um ataque em rajada de segundos explora exatamente essa janela — o contador transacional simples da regra dura enxerga o que a feature agregada ainda não viu. E tem o argumento operacional que quem já carregou pager conhece: quando o modelo cai, o fallback é a política sobre as regras — se vocês as aposentarem, o modo degradado do sistema vira "nada". Camada rápida e burra na frente, camada lenta e esperta atrás; defesa em profundidade, não rivalidade.

**"O modelo virou uma caixa-preta no meio do meu caminho de pagamento. Como você audita isso?"**

Concedo o ponto de partida: os pesos do modelo são inauditáveis no sentido clássico — ninguém lê uma floresta de árvores em code review. Por isso a arquitetura cerca a caixa-preta com caixas de vidro: a lista de features é versionada e checada automaticamente a cada versão; o score que saiu é logado com versão do modelo, versão da política e EndToEndId; e a conversão de score em ação é uma tabela determinística que qualquer auditor lê em um minuto. Quando o BACEN pergunta "por que bloqueou?", a resposta é "score 912, política v14, linha 4" — reprodutível, datada, com dono. O que a gente NÃO promete é explicar por que o score foi 912 e não 870 — e a jogada regulatória honesta é essa: a explicabilidade exigível mora na decisão, e a decisão é da política. Quem promete explicar neurônio está vendendo o que não pode entregar.

**"E se o modelo simplesmente estiver errado — bloqueando gente inocente em massa?"**

Esse cenário tem três amortecedores, em ordem. Primeiro, ele teria aparecido em sombra: semanas comparando o veredito hipotético do modelo com o real das regras, com cada divergência indo para análise humana — bloqueio em massa de inocente é exatamente o tipo de padrão que essa comparação expõe antes da promoção. Segundo, a política limita o raio do estrago: o modelo sozinho não bloqueia — score alto abre desafio no app para valores médios e caso para analista nos altos; a Carla e a equipe dela são um circuit breaker humano, e um pico anômalo de casos abertos é alarme, não ruído. Terceiro, o kill switch operacional: a política tem linhas de fallback que funcionam com score indisponível — desligar o modelo devolve o sistema ao estado da Aula 4, degradado mas conhecido. O risco não é zero; é limitado, observável e reversível — que é o máximo que arquitetura honesta promete.

---

## Sobre a inferência no caminho crítico

**"Modelo de ML dentro de 100 ms no p99? Em pico de 900 TPS? Isso é slide de conferência, não produção."**

É produção — desde que se respeite o que a conta de guardanapo mostrou. O modelo de score não é um modelo de linguagem: é um classificador especializado que roda em 10–20 ms; a fatia perigosa é a busca de features, e é por isso que a feature store online existe — valores pré-agregados, consulta chave-valor de poucos milissegundos, alimentada assincronamente pelos eventos do Outbox. O desenho reserva ~60 ms de folga para o p99 justamente porque GC, fila e azar existem. E reparem no que o desenho NÃO faz: não varre histórico na hora, não chama serviço externo, não treina nada online. Quem estoura orçamento é quem computa feature na requisição. Antifraude síncrono em caminho de pagamento é prática corrente na indústria — a alternativa, decidir risco depois de liquidar um pagamento irrevogável, é que seria slide de terror.

**"O que acontece no seu p99.9? Você orçou o p99 e lavou as mãos para o resto?"**

Pergunta de quem leu a Aula 1 — a cauda manda, sempre. No p99.9 o orçamento estoura, e o desenho assume isso de frente em vez de fingir que não acontece: a chamada Pagamentos→Antifraude tem deadline propagado (Aula 4), e quando o deadline vence sem score, a política executa as linhas de fallback — segue até R$ 200, bloqueia acima. Ou seja: o pior caso não é lentidão acumulando na fila; é uma decisão degradada, tomada em tempo limitado, com viés conservador no valor alto. É a mesma filosofia do circuit breaker: transformar latência imprevisível em falha previsível. O número que a gente monitora com carinho é a taxa de acionamento desse fallback — se ela sai de "raríssima" para "rotineira", o problema não é a cauda, é o dimensionamento, e aí é capacidade, não arquitetura.

**"A feature store tem atraso eventual. Então o modelo decide sobre dados velhos — isso não invalida o score?"**

Invalida para o que muda em segundos; não invalida para o que muda em horas — e a arte está em saber qual feature é qual. "Idade da conta", "valor médio em 30 dias", "grafo de relacionamento": centenas de milissegundos de atraso são irrelevantes. "Quantas transações nos últimos 10 segundos": aí sim o atraso mata, e por isso essa classe de sinal mora nas regras duras, que consultam contadores transacionais na frente do modelo. O desenho de camadas não é decoração — é exatamente a resposta a essa objeção. E vale registrar o trade-off que a gente está comprando conscientemente: computar toda feature de forma transacional e síncrona daria consistência perfeita ao custo de reintroduzir leitura pesada no caminho de escrita — que foi a causa raiz do incidente do dia 5 da Aula 2. Preferimos features levemente atrasadas com camada rápida na frente a um ledger contencioso de novo.

---

## Sobre modelos abertos, LGPD e custo

**"Por que carregar o fardo de operar GPU e modelo aberto se a API de um provedor é melhor e mais barata de começar?"**

Para começar, ela é mesmo — e se o dado não for sensível, eu uso API sem culpa. O argumento do modelo aberto no núcleo é triplo e específico. LGPD: o dossiê do copiloto contém CPF, chave Pix, grafo de contas; mandar isso para fora do perímetro exige base legal, contrato, anonimização — e anonimizar um grafo de contas sem destruir sua utilidade é quase contradição em termos. Latência: numa API, o seu p99 inclui a fila dos outros clientes do provedor; no seu cluster, a fila é sua. Custo em escala: API cobra por chamada, e chamada no núcleo escala com TPS — a curva cruza rápido quando o volume é o do Pix. Notem que o critério não é ideologia nem soberania tecnológica: é sensibilidade do dado e criticidade da decisão. A mesma fintech pode — e deve — usar API na borda para o que não carrega dado de cliente.

**"Anonimiza os dados e usa a API. Resolvido, não?"**

Não tão rápido. Anonimização de verdade — a que a LGPD reconhece como tirando o dado do escopo — exige que o titular não seja reidentificável por meios razoáveis, e o dado útil para fraude é justamente o mais reidentificável que existe: padrão temporal de transações, grafo de relacionamentos, valores. Pseudonimizar (trocar CPF por hash) mantém o dado pessoal no escopo legal e ainda vaza estrutura — um grafo de contas pseudonimizado continua sendo o mapa de relacionamento financeiro de pessoas reais. Dá para anonimizar de verdade? Para treino offline com agregações, às vezes sim. Para o caso do copiloto — que precisa citar a conta específica, o histórico específico, a evidência verificável — anonimizar destrói exatamente o que o artefato precisa ter. O custo de operar modelo dentro de casa é real; ele compra a dispensa de uma ginástica jurídica que, no núcleo, não fecha.

**"Quantização degrada o modelo. Você está economizando GPU ao custo de errar fraude?"**

Está trocando, sim — e a pergunta certa é se a troca é medida ou é fé. A perda de qualidade por quantização bem-feita costuma ser pequena, mas "costuma" não é argumento em fintech: a versão quantizada passa pelo mesmo rito da versão original — avaliação offline comparada e, se a diferença for material, sombra antes de promover. O registro de modelos trata a variante quantizada como versão própria, com métricas próprias; se ela degradar além do aceitável, ela não sobe, e a conta de GPU sobe no lugar. O que eu não aceito é a versão invertida dessa objeção: rodar o modelo grande sem quantização, estourar o orçamento de latência do p99 e chamar isso de "qualidade" — score que chega depois do deadline vira fallback, e fallback decide pior que modelo quantizado. Latência é parte da qualidade quando a decisão tem prazo.

---

## Sobre shadow mode

**"Semanas de sombra é luxo. O golpe está acontecendo AGORA — você deixa sangrar enquanto acumula confiança?"**

A falsa premissa aqui é que sombra e resposta imediata competem. O que responde ao golpe de hoje é o que sempre respondeu: regra — o Diego escreveu a regra da rajada de valores repetidos no dia seguinte ao golpe, deploy em horas, porque regra é exatamente o instrumento de resposta rápida a padrão conhecido. A sombra não é o plantão de emergência; é o processo que constrói a defesa contra o padrão *desconhecido*, e esse processo não tem atalho honesto: promover um modelo sem comparação em tráfego real é trocar um risco conhecido (o golpe atual, já coberto por regra) por um desconhecido (falsos positivos em massa, cegueira sistemática) — e falso positivo em pagamento é cliente com Pix travado, dano de confiança imediato. A resposta operacional completa é: regra estanca hoje, MED recupera ontem, sombra prepara o modelo que pega o golpe de amanhã. Três instrumentos, três escalas de tempo.

**"Sombra dobra o custo de inferência. Quem paga?"**

Dobra o custo de computação do Antifraude durante a janela de sombra — e é bom dizer o número em voz alta na reunião, porque ele compra três coisas contadas em dinheiro. Um: a diferença entre descobrir falso positivo em massa numa comparação de logs versus descobrir no call center, com cliente furioso e dano de marca. Dois: a evidência regulatória — quando o compliance pergunta com que base o modelo foi promovido a decidir sobre transações, "semanas de comportamento observado em produção, com divergências analisadas caso a caso" é uma resposta; "as métricas de laboratório estavam boas" é uma esperança. Três: a calibração da própria política — os limiares de score da tabela de decisão foram ajustados olhando a distribuição real da sombra, não a do laboratório. E a janela termina: sombra é rito de promoção, não estado permanente. Custo temporário, dividendo permanente.

---

## Sobre o copiloto e MCP

**"Copiloto com LLM alucina. Você quer decisão de bloqueio de conta encostada em alucinação?"**

A decisão não encosta na alucinação — esse é o desenho inteiro. O copiloto produz um dossiê em que cada afirmação vem com a fonte linkada: a consulta MCP que a produziu, o registro que a sustenta. A Carla não confia no resumo; ela verifica as citações — e verificar citação linkada custa segundos, contra os vinte minutos de montar o contexto do zero. Alucinação nesse desenho é constrangimento detectável, não decisão errada: uma afirmação sem fonte verificável é descartada, e o caso segue com o que se sustenta. Comparem com a alternativa real, não com a perfeição: a Carla de setembro, às seis telas, sob fila de casos crescendo, também errava — por cansaço, por pressa, por contexto incompleto. A pergunta de engenharia não é "o copiloto erra?" — é "o par Carla+copiloto, com evidência citada e tempo sobrando para julgamento, erra menos que a Carla afogada?". A resposta operacional da TechPix foi sim.

**"Se o copiloto não tem ferramenta de escrita, um dia alguém adiciona 'só uma automaçãozinha' e a fronteira era. Como você impede a erosão?"**

Essa é a objeção mais madura da lista, porque o risco não é técnico — é organizacional, e erosão de fronteira acontece um pedido razoável por vez. As defesas são de governança com dente: o conjunto de ferramentas exposto a cada consumidor MCP é configuração versionada — mudança passa por revisão com dono nomeado, não por deploy silencioso; e uma checagem automática no pipeline (uma fitness function, no vocabulário da Aula 2) falha a build se o manifesto de ferramentas do copiloto contiver qualquer ferramenta de escrita. Aí a discussão muda de natureza: quem quiser a automaçãozinha precisa alterar um teste que existe para bloqueá-la, à luz do dia, com aprovação de risco — e não convencer um dev apressado numa sexta. Sobre automatizar ações de baixo risco em lote: pode ser um sistema legítimo — desde que seja *outro* consumidor, com outro cardápio, outra revisão, outro trilho de auditoria. O que não pode é a fronteira derreter por conveniência dentro do mesmo agente.

**"Vinte minutos para dois: você mediu isso ou é número de vendedor?"**

Concedo: número redondo demais merece desconfiança, e a medição honesta tem armadilhas. O que se mede com confiança é tempo de ciclo por caso (abertura→decisão) antes e depois, no mesmo mix de severidade — e o ganho concentrado na fase de montagem de contexto aparece limpo porque as fases são instrumentadas separadamente. As armadilhas que a gente admite: efeito novidade (analista caprichando porque está sendo medido), mix de casos mudando entre os períodos (outubro teve lote de fraude atípico), e o risco sutil de o copiloto acelerar o caso fácil e não mover o difícil — por isso a mediana e o p90 do tempo de ciclo são acompanhados separados. E o contrapeso de qualidade: taxa de reversão das decisões (casos reabertos ou revertidos depois) não pode subir com a velocidade. Velocidade com reversão subindo não é produtividade; é fila sendo empurrada para o futuro.

---

## Sobre governança e o Model Card

**"Vetar CEP não impede proxy de proxy — o modelo reconstrói geografia por outros sinais. Seu veto é cosmético?"**

Não é cosmético, mas também não é suficiente — e o Model Card diz isso com todas as letras na linha de limites conhecidos. O veto na lista de features é a camada barata e auditável: elimina o canal direto, é verificável por máquina a cada versão, e estabelece o princípio de que feature é decisão de governança. Que correlações residuais reconstroem parcialmente o sinal vetado — concedo, é matematicamente esperado. Por isso a governança não para na lista: análise de disparidade de resultados por grupo nas revisões de versão (o modelo bloqueia desproporcionalmente algum recorte?), com a comparação sombra×ativo fornecendo os dados, e a política de decisão como amortecedor final — score alto em valor médio vira desafio no app, não bloqueio seco, e caso de bloqueio passa por analista. Auditoria de viés é disciplina contínua, não checkbox. O que eu defendo é a honestidade do artefato: limites conhecidos escritos no documento valem mais que uma alegação de neutralidade que ninguém consegue sustentar.

**"Quem é o dono quando o modelo erra? O Diego? A Carla? O fornecedor da GPU? Vocês criaram difusão de responsabilidade."**

Ao contrário — o Model Card existe para que essa pergunta tenha resposta antes do erro, porque difusão de responsabilidade é o que acontece quando ninguém escreveu os donos. A divisão é por artefato: o time do Diego responde pelo modelo (features, treino, desempenho, drift); risco e negócio respondem pela política de decisão (os limiares, os fallbacks — inclusive a linha que decide o que acontece com score indisponível); a equipe da Carla responde pelas decisões individuais que tomou sobre os casos que revisou. Cada transação decidida loga versão do modelo, versão da política e ação — então "quem errou aqui?" é uma consulta, não uma reunião. E notem o desenho de incentivo: quem calibra limiar (risco) não é quem treina modelo (Antifraude), de propósito — se o mesmo time fizesse os dois, a tentação de afinar a política para esconder fraqueza do modelo não teria contrapeso. Responsabilidade nomeada por camada é o oposto de difusão.

**"Retreino mensal significa que o modelo de dezembro decide diferente do de novembro. Como você reproduz uma decisão antiga num processo judicial?"**

Essa pergunta paga a aula inteira de governança. Reprodução exige quatro coordenadas, e todas são retidas: a versão do modelo (pesos congelados no registro de modelos — retreino cria versão nova, nunca sobrescreve), a versão da política, o vetor de features que entrou na inferência (logado na decisão, com EndToEndId), e o score que saiu. Com as quatro, a decisão de 3 de outubro se reexecuta bit a bit em qualquer data futura — mesma entrada, mesmos pesos congelados, mesmo score, mesma linha da política. Reparem no paralelo com o que este curso fez desde a Aula 1: o ledger não guarda "o saldo", guarda os fatos que permitem reconstruir o saldo; a decisão de risco não guarda "bloqueou", guarda os fatos que permitem reconstruir o bloqueio. Retenção conforme prazo regulatório, como qualquer lançamento. O que seria indefensável é a versão ingênua: um modelo que retreina in-place e uma linha de log dizendo "bloqueado pelo antifraude".
