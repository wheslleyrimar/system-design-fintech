---
layout: default
title: "Aula 4 — Guia de perguntas difíceis"
---

# Aula 4 — Guia de perguntas difíceis
*Munição de embasamento para quando a plateia técnica empurrar.*

---

## Sobre o incidente de abertura

**"Renomear campo sem versionar é erro de estagiário. Isso é problema de arquitetura ou de code review?"**

É a pergunta certa, e a resposta é: se a sua arquitetura depende de todo code review pegar todo erro humano, a sua arquitetura é "torcida organizada". O time do Diego passou por revisão — o revisor viu uma renomeação semanticamente correta, alinhada à linguagem ubíqua da Aula 3, com testes verdes. O que nenhum humano tinha como ver era o **inventário de consumidores** daquele evento — informação que não morava em lugar nenhum. Arquitetura é exatamente o que transforma classes de erro humano em impossibilidade mecânica: o schema registry teria recusado a publicação no CI, sem depender da memória de ninguém. A régua que eu uso: erro que aconteceu uma vez é lição; erro que **pode** acontecer de novo do mesmo jeito é falha de arquitetura. Depois do registry, esse erro específico é impossível — isso é o que "resolver" significa.

**"Por que não fizeram rollback do deploy do Antifraude em vez de corrigir o consumidor?"**

Porque rollback de produtor de eventos tem uma pegadinha que quase ninguém enxerga no calor do momento: os eventos no formato novo **já estavam publicados**. O log é imutável — princípio da Aula 1. Se o Rafael revertesse o produtor às 20h27, a fila conteria trinta e cinco minutos de eventos com `carteiraId` no meio de eventos com `contaId`, e o consumidor antigo quebraria nos novos do mesmo jeito — o veneno já estava dentro. Corrigir o consumidor para aceitar **os dois formatos** era o único caminho que drenava a fila inteira, e de quebra é exatamente o primeiro passo do expand/contract que deveria ter existido desde o início — só que executado de madrugada, sob pressão, na ordem errada. Rollback resolve estado de código; não resolve estado de dados já emitidos. Em sistemas de eventos, isso muda o playbook de incidente.

## Sobre síncrono vs assíncrono

**"Se assíncrono desacopla tanto, por que não fazer tudo assíncrono, inclusive a validação de limites?"**

Porque a validação de limites responde uma pergunta que **bloqueia a decisão seguinte**: posso enviar este Pix ao SPI? Fazer isso assíncrono significa uma de duas coisas: ou o fluxo vira uma saga — reservo, envio, e se a validação reprovar depois eu compenso um Pix que já liquidou de forma irrevogável no SPI, o que é juridicamente e operacionalmente um pesadelo —, ou eu seguro o Pix numa fila esperando o veredito, o que é uma chamada síncrona com passos extras e mais latência. Assíncrono brilha quando a resposta **não muda o próximo passo** — extrato, notificação, recálculo. Quando muda, o acoplamento temporal é intrínseco ao domínio, não à implementação. A honestidade arquitetural é distinguir o acoplamento que vocês criaram (elimine-o) do que o negócio impõe (gerencie-o com timeout, breaker e fallback).

**"gRPC dentro de um monólito modular é over-engineering, não é?"**

Dentro do monólito, hoje, a chamada entre módulos é chamada de função — e deve continuar sendo; ninguém sensato põe serialização entre módulos do mesmo processo. O que a gente define agora é o **contrato** dessas fronteiras no formato que sobrevive à extração: a interface de `ValidarLimites` já descrita como se fosse um `.proto`, com orçamento e política declarados. Quando a Aula 6 extrair o Antifraude, a fronteira já existe, testada e documentada — só troca o transporte. O professor da Aula 2 chamou o monólito modular de "ensaio" das fronteiras de serviço; eu estou dizendo com o que se ensaia: com o contrato escrito. Over-engineering seria pagar o custo de rede antes de precisar. Escrever o contrato antes de precisar custa uma tarde e é a diferença entre extração de rotina e reescrita de fronteira sob pressão.

**"Quatro elos síncronos em série a 99,9% cada dão 99,6%. O BACEN exige mais. Como vocês fecham essa conta?"**

Primeiro, concedo: a multiplicação é essa mesma e não tem mágica que a desfaça — todo elo síncrono no caminho crítico é um imposto de disponibilidade. A conta fecha por três vias somadas. Um: nem todo elo conta igual — o cache disciplinado de chaves do DICT tira uma fração relevante das consultas do caminho, e fallback segmentado no Antifraude transforma indisponibilidade total em degradação parcial (Pix de valor baixo seguem passando). Dois: os números individuais não são fixos — pool dedicado, timeout derivado e breaker existem para que a *sua* fatia de falha seja menor que a genérica. Três: o índice do BACEN mede a disponibilidade do serviço ao usuário, e é exatamente por isso que fail-open segmentado é discussão de disponibilidade regulatória, não só de UX. A lição permanente: disponibilidade composta se **projeta**, elo a elo — não se descobre no relatório mensal.

## Sobre eventos e consumidores

**"O Kafka tem transações e 'exactly-once semantics'. Isso não torna o consumidor idempotente desnecessário?"**

O EOS do Kafka é real e valioso, mas cobre um perímetro específico: pipelines que leem e escrevem **dentro do próprio Kafka** (padrão consume-transform-produce, tipicamente com Kafka Streams). O projetor de extrato do TechPix sai desse perímetro: ele lê do Kafka e escreve **num banco de dados externo** — e a atomicidade entre "commitei o offset" e "gravei a projeção" volta a ser problema seu, porque são dois sistemas transacionais distintos. É o dual write da Aula 2, agora do lado do consumidor. As soluções são as mesmas de sempre: idempotência por upsert, ou guardar o offset processado na mesma transação do banco de destino. A regra que eu dou aos times: "exactly-once" de fornecedor é uma garantia com perímetro — leiam onde o perímetro termina, porque o seu incidente vai morar exatamente um metro depois dele.

**"A DLQ quebra a ordenação que vocês mesmos disseram ser sagrada por conta. Isso não é contradição?"**

É tensão real, e eu prefiro chamar de trade-off documentado a fingir que não existe. As opções na prática são três. Retry infinito preserva ordem e paralisa tudo — foi a sexta-feira, inaceitável. DLQ simples destrava tudo e quebra a ordem da chave afetada — aceitável para consumidores cuja projeção é upsert de estado absoluto ("status do E2E tal = liquidado"), porque a mensagem estacionada, quando reprocessada, converge. Pausa por chave preserva ordem da chave afetada e destrava o resto — necessária quando a projeção é incremental e ordem importa de verdade. O projetor de extrato do TechPix usa a terceira, e o custo é complexidade real de implementação. O ponto pedagógico: nenhuma das três é "a certa" — mas o consumidor que não sabe **qual** delas implementa descobre durante o incidente, e aí já pagou o preço das três.

**"Qual número de consumer lag deve alertar? Me dá um número."**

Não existe número universal, e desconfie de quem der um — existe **método**: o alerta deriva da promessa do contrato, não do folclore da ferramenta. O contrato do extrato promete convergência em 100–300 ms; a 900 TPS de pico, cada segundo de fila parada são ~900 eventos de atraso e ~1 segundo de promessa quebrada. Um alerta razoável ali dispara quando o atraso projetado (lag ÷ taxa de consumo) passa de alguns segundos por mais de um minuto — sensível o bastante para pegar a sexta-feira em dois minutos em vez de vinte, tolerante o bastante para ignorar soluços de rebalanceamento. Já o consumidor que recalcula limites tolera minutos de lag sem drama. Mesma métrica, alertas diferentes, porque **as promessas são diferentes**. Lag se alerta em unidade de promessa (tempo até convergir), não em unidade de fila (mensagens acumuladas).

## Sobre mudanças de contrato

**"Expand/contract triplica o trabalho de uma mudança trivial. Como eu justifico isso pro meu tech lead apressado?"**

Com a conta honesta dos dois lados. O passo único custa: quarenta minutos de incidente, trezentas ligações, um postmortem, e — o mais caro e menos visível — a erosão da confiança que faz o time seguinte pedir "janela de manutenção coordenada" para qualquer mudança, que é como a velocidade morre de verdade numa empresa. Os três passos custam: um campo duplicado por algumas semanas e dois deploys extras que não exigem coordenação nenhuma — cada um sai quando quer. Reparem que expand/contract não é lentidão: é **remoção da necessidade de sincronizar times**, que é o que torna mudança frequente possível. E para mudança genuinamente trivial existe atalho legítimo: mudança retrocompatível pura (adicionar campo opcional) é um passo só, e o registry confirma isso mecanicamente. O processo pesa exatamente onde o risco pesa.

**"O schema registry não vira um ponto de veto burocrático — o novo comitê de arquitetura?"**

Vira, se vocês configurarem como comitê: aprovação manual, exceção por abertura de chamado, dono político. A versão saudável é o oposto: **regra mecânica, resposta em segundos, zero humano no caminho feliz**. Mudança compatível passa sem ninguém olhar; mudança incompatível falha no CI com a mensagem "isso quebra os consumidores X e Y — o caminho é expand/contract, doc aqui". Não é um portão com porteiro; é um corrimão. A diferença prática entre burocracia e automação de disciplina é o tempo de resposta e a previsibilidade da regra: comitê decide caso a caso em dias; fitness function decide pela mesma regra em segundos. Se algum dia o registry do TechPix precisar de "abrir exceção com o time de plataforma", aí sim vocês terão construído burocracia com roupa de ferramenta — e a culpa não será do padrão.

**"Pact num time de dez pessoas que almoçam juntas — não basta conversar?"**

Hoje, talvez baste — dez pessoas, um corredor, contexto compartilhado. Mas reparem no que o contrato executável captura que a conversa não captura: a conversa de hoje não protege o refactor de daqui a oito meses, feito por alguém que não almoçava com vocês. O Pact é memória institucional executável — "o consumidor lê estes campos" deixa de ser lore tribal e vira teste que roda em todo build, para sempre. E o custo de adotar cedo é baixo justamente porque o sistema é pequeno: três contratos, meia tarde. Adotar depois, com trinta arestas e times que já não se conhecem, é projeto de trimestre. Minha régua honesta: se vocês têm certeza de que nunca passarão de um time e um serviço, pulem. O TechPix já tem seis contextos e um plano de extração na Aula 6 — para ele, "conversar" já é o método que produziu a sexta-feira.

## Sobre resiliência e fallback

**"Fail-open até R$ 200 é literalmente um manual público de como fraudar vocês por R$ 199,90, não é?"**

Concedo o mecanismo: se a política vazar e o fraudador conseguir **provocar ou detectar** a degradação do Antifraude, ele tem uma janela de valor baixo. Agora as atenuantes que fazem a política ainda ser a certa. Primeiro, a janela é curta e anômala — breaker aberto é evento raro e monitorado; explorar isso exige o timing do adversário coincidir com a falha de vocês. Segundo, "aprova com flag de análise posterior" não é "aprova e esquece": os casos passam por revisão, alimentam o grafo de fraude, e o MED da Aula 1 existe — recuperar R$ 199,90 rastreável é bem diferente de perdê-lo. Terceiro, a alternativa fail-closed tem custo certo e imediato: 100% dos clientes legítimos recusados durante toda degradação. A política não é "impossível fraudar"; é **prejuízo esperado limitado e mensurado contra receita e reputação preservadas** — e o número exato, R$ 200 ou R$ 50, é calibrável com dados, revisado por Risco, e nunca hardcoded num catch.

**"Circuit breaker na chamada ao SPI? Vocês vão 'proteger' o Banco Central de vocês?"**

A ironia é boa, mas o breaker ali não protege o BACEN — protege **vocês** de vocês mesmos. Quando o SPI degrada (raro, mas o índice de disponibilidade dele é 99,9%, não 100%), o comportamento ingênuo é seguir despejando `pacs.008` com timeout estourando: cada tentativa segura uma conexão do pool por 6 segundos, o pool esgota — é o mecanismo exato da Aula 2, com o SPI no papel do DICT —, e o TechPix inteiro trava por causa de uma dependência que estava *parcialmente* degradada. O breaker aberto converte isso em modo de contingência explícito: Pix novos entram em fila de reapresentação com comunicação honesta ao cliente ("em processamento"), o pool respira, e a reconciliação por E2E ID resolve os que ficaram no limbo. Detalhe importante: o estado do breaker do SPI é, na prática, um detector de incidente nacional — e deve estar no dashboard com essa dignidade.

**"Quem assina a decisão de fallback — engenharia ou negócio? Na prática isso sempre sobra pro dev."**

Sobra pro dev quando a pergunta chega **durante** o incidente — aí qualquer `catch` vira política de risco por omissão, assinada por ninguém. O único jeito que eu conheço de inverter isso é o que o contrato de integração institucionaliza: a pergunta é feita **antes**, em tempo de paz, no fórum certo — engenharia apresenta os cenários e os custos ("se o Antifraude cair 10 minutos no pico, fail-closed recusa ~540 mil reais em Pix legítimos; fail-open expõe X de fraude esperada"), e Risco/Produto escolhem e **assinam com data**, como está na entrada da Seção 6. Engenharia detém o *como* (breaker, timeout, segmentação por valor); negócio detém o *quanto* (R$ 200, e por quê). Se na sua empresa isso "sempre sobra pro dev", o problema não é cultural e vago — é a ausência concreta de um artefato onde a assinatura do negócio é obrigatória. Criem o artefato; a conversa acontece.

## Sobre o artefato e o processo

**"Documento vivo morre em wiki. Por que o Contrato de Integração seria diferente?"**

Porque a diferença entre documento vivo e obituário não é disciplina — é **acoplamento a coisas que executam**. O contrato do TechPix aponta para o schema registry que valida todo publish no CI; para o broker de Pact que roda em todo build do provedor; para os dashboards de lag e taxa de fallback que alertam de verdade. Quando a realidade diverge do documento, alguma esteira **quebra** — e aí alguém atualiza o documento, porque é o caminho de menor resistência para destravar o build. Wiki morre porque divergir dela é grátis; contrato amarrado a CI morre não, porque divergir dele custa um build vermelho. A heurística de auditoria que eu deixo: para cada afirmação do documento, perguntem "o que fica vermelho se isso mentir?". Afirmação sem resposta é a parte que já está morta — ou corta, ou instrumenta.

**"Por que isso não é um ADR? Vocês adoram ADR nesse curso."**

Porque são espécies diferentes de registro, e confundi-las estraga os dois. O ADR, como o professor das primeiras aulas definiu por Nygard, é **imutável e pontual**: registra uma decisão, seu contexto e suas consequências, numa data; nunca se edita, só se substitui. O contrato de integração é **vivo por natureza**: timeout recalibrado, versão de schema, fallback reajustado pelo Risco — ele muda porque a aresta muda, e sua utilidade está em refletir o presente, não em preservar o passado. A relação entre eles é de fundação e prédio: o ADR-001 (consistência forte) e o ADR-002 (Outbox) são as decisões imutáveis **sobre as quais** os contratos de aresta se apoiam; nenhuma entrada do contrato pode contradizê-los. E repito o que eu disse em aula: o ADR-003 continua não existindo — ele está reservado, na prática, para o dia em que alguém mexer na escrita do ledger. A pendência do ADR-002 segue aberta, e não fui eu que a fechei.
