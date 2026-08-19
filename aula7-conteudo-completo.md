---
layout: default
title: "Aula 7 — Observabilidade e Operação Inteligente"
---

# Aula 7 — Observabilidade e Operação Inteligente
*Curso de Arquitetura de Sistemas Financeiros com IA*

> **Navegação:** [Índice](index.md) · [Aula 1](aula1-conteudo-completo.md) · [Aula 2](aula2-conteudo-completo.md) · [Aula 3](aula3-conteudo-completo.md) · [Aula 4](aula4-conteudo-completo.md) · [Aula 5](aula5-conteudo-completo.md) · [Aula 6](aula6-conteudo-completo.md) · **Aula 7 (você está aqui)** · [Aula 8](aula8-conteudo-completo.md)

Deixa eu começar essa aula de um jeito que nenhuma das anteriores começou: sem incidente.

É 5 de dezembro de 2025. Dia 5 — e vocês já sabem o que essa data significa nesse curso: foi num dia 5 que a TechPix afundou na areia, lá na Aula 2, com o pool de conexões esgotando e o retry storm comendo o sistema por dentro. Pois bem: o 5 de dezembro de 2025 entrou para a história do Pix por outro motivo — foi o dia do recorde nacional, **313,3 milhões de transações em 24 horas**, a primeira vez que o país passou de 300 milhões num único dia. É exatamente o número que hoje está registrado no material da Aula 1, na conta de guardanapo — o professor que esteve aqui antes de mim o manteve atualizado. E quando esse dia chegou, a TechPix estava rodando como microsserviços, com canary, com feature flags — tudo que a gente montou na Aula 6.

E aí eu quero contar como foi esse dia do lado de dentro. O Rafael — o engenheiro de plantão, o on-call daquela sexta-feira — passou o dia olhando para um painel. O tráfego subiu a manhã inteira, bateu o pico projetado na hora do almoço — **900 transações por segundo, cravado no número que a Lei de Little da Aula 1 tinha previsto** —, a utilização do caminho crítico encostou em 65% e parou ali, abaixo da regra dos 70% da Aula 2. Nenhuma página. Nenhum alerta. O extrato atrasava seus 100 a 300 milissegundos de sempre, o circuit breaker do DICT não abriu nem uma vez, o canary de uma mudança pequena do time de Devoluções progrediu de 1% para 100% no meio da tarde como se fosse um dia qualquer.

O dia 5 da Aula 2 e o dia 5 desta aula são o mesmo sistema de negócio, o mesmo perfil de tráfego, a mesma pressão. **A diferença entre aquele dia e este não é sorte — é que agora a gente enxerga.** E "enxergar" tem nome técnico, tem custo, tem disciplina, e é o assunto das próximas duas horas.

Só que eu não vou deixar vocês relaxarem. Porque no fim daquela tarde gloriosa, no meio dos dashboards verdes, chegou um ticket do atendimento. Uma cliente reclamando que o Pix dela tinha demorado. Uma cliente chamada — vocês vão rir — **Ana**.

A Ana, a mesma da Aula 1, a das 2h47 da Black Friday. Dessa vez ela pagou um fornecedor novo, uma confeitaria recém-aberta, e o pagamento levou **9 segundos** para confirmar. Não falhou. Não duplicou — a idempotência da Aula 1 continua fazendo o trabalho dela. Mas 9 segundos, para quem se acostumou com 2, é uma eternidade: deu tempo de a Ana achar que ia acontecer tudo de novo.

E aqui está o problema que vai carregar essa aula inteira: **eu fui olhar os painéis, e os painéis diziam que estava tudo bem.** Latência média do dia: 1,9 segundo. p99 interno: 3,4 segundos, dentro do objetivo. Taxa de erro: 0,08%, abaixo do 0,1% de baseline. Pelo agregado, o Pix de 9 segundos da Ana **não existia**. Mas a Ana existe, o ticket existe, e a reclamação é real.

A pergunta da aula é essa: **como se encontra uma agulha que a média jura que não está no palheiro?** A resposta vai exigir os três pilares, um ID que o Banco Central deu de presente para vocês sem cobrar nada, e uma mudança de mentalidade sobre o que significa "operar" um sistema. Vamos lá.

---

## 1. Monitorar não é observar

Primeiro, eu preciso desfazer uma confusão de vocabulário, porque o mercado usa essas duas palavras como sinônimos e elas não são.

**Monitoramento responde perguntas que você previu.** Você decidiu, em tempo de projeto, que queria saber a taxa de erro, o p99, o uso de CPU. Instalou os medidores, definiu os limiares, configurou os alertas. Quando a resposta de uma dessas perguntas fica feia, o alarme toca. Monitoramento é um questionário de múltipla escolha que o sistema preenche o dia inteiro.

**Observabilidade responde perguntas que você ainda não fez.** É a propriedade do sistema — e reparem, é uma propriedade *do sistema*, não da ferramenta — de permitir que você formule uma pergunta nova, depois do fato, e consiga respondê-la com os dados que já foram coletados. "Por que exatamente o Pix da Ana, das 16h41 do dia 5, levou 9 segundos?" — essa pergunta não estava em nenhum dashboard, porque ninguém desenha dashboard para uma transação específica de uma cliente específica. Se o sistema é observável, a resposta está lá dentro, esperando a pergunta. Se não é, a resposta se perdeu no momento em que a transação terminou.

O jargão da área chama isso de *unknown unknowns* — os desconhecidos que você nem sabia que desconhecia. Monitoramento cobre os *known unknowns*: "eu sei que a latência pode subir, não sei quando". Observabilidade cobre o resto: o modo de falha que ninguém imaginou, a combinação de condições que nunca apareceu em homologação. E numa fintech, com o regulador medindo o índice de disponibilidade de vocês — lembram da Aula 1, o ANS do DICT, a meta de 100%? —, os *unknown unknowns* não são curiosidade acadêmica: são o que separa "detectamos e explicamos em minutos" de "descobrimos pelo Twitter".

Os três pilares clássicos — métricas, logs e traces — eu quero que vocês guardem como **três perguntas diferentes sobre o mesmo evento**:

| Pilar | A pergunta que ele responde | Natureza | Custo relativo |
|---|---|---|---|
| **Métrica** | "Quanto? Quantos? Com que frequência?" | Número agregado ao longo do tempo | Barato — cardinalidade controlada |
| **Log** | "O que exatamente aconteceu *ali*?" | Evento discreto, com contexto | Médio — cresce com o tráfego |
| **Trace** | "Por onde essa requisição passou, e quanto custou cada parada?" | A jornada de *uma* requisição pelos serviços | Caro — por isso se amostra |

Nenhum dos três substitui os outros. A métrica disse "o dia está saudável" — e estava certa, no agregado. Vai ser o trace que vai encontrar a Ana. E vai ser o log que vai explicar o que o trace apontar. **Os três pilares não competem; eles se revezam na mesma investigação.** Guardem essa frase, porque a caça aos 9 segundos, daqui a pouco, vai usar os três em sequência.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 820 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a7p-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <!-- Pilar 1: Métrica -->
  <rect x="30" y="30" width="230" height="80" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="145" y="58" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#3730a3">MÉTRICA</text>
  <text x="145" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">"Quanto? Quantos?"</text>
  <text x="145" y="96" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">agregado · barata · aponta a região</text>
  <!-- Pilar 2: Trace -->
  <rect x="295" y="30" width="230" height="80" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="410" y="58" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#7a5c00">TRACE</text>
  <text x="410" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">"Por onde passou?"</text>
  <text x="410" y="96" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">1 requisição · caro · acha a jornada</text>
  <!-- Pilar 3: Log -->
  <rect x="560" y="30" width="230" height="80" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="675" y="58" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">LOG</text>
  <text x="675" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">"O que aconteceu ali?"</text>
  <text x="675" y="96" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">evento discreto · explica a causa</text>
  <!-- Revezamento arrows -->
  <line x1="260" y1="70" x2="290" y2="70" stroke="#4338ca" stroke-width="2" marker-end="url(#a7p-arrow)"/>
  <line x1="525" y1="70" x2="555" y2="70" stroke="#4338ca" stroke-width="2" marker-end="url(#a7p-arrow)"/>
  <!-- Convergence -->
  <line x1="145" y1="110" x2="360" y2="185" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>
  <line x1="410" y1="110" x2="410" y2="182" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>
  <line x1="675" y1="110" x2="460" y2="185" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>
  <rect x="240" y="190" width="340" height="60" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="410" y="215" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">A MESMA investigação</text>
  <text x="410" y="236" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#4338ca">costurada pelo e2e_id (EndToEndId do BACEN)</text>
  <text x="410" y="280" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">Caça aos 9s: métrica diz "dia saudável" → trace acha a Ana → log explica o cold start</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Três perguntas sobre o mesmo evento — os pilares se revezam, não competem.</p>
</div>

---

## 2. Métricas: o que medir, e o que nunca etiquetar

### 2.1 RED para serviços, USE para recursos

Depois da Aula 6, a TechPix tem serviços de verdade: Antifraude e Limites rodando fora, Pagamentos rodando fora, o monólito com Contas e Ledger dentro. Cada um deles precisa responder três perguntas o tempo todo, e essas três perguntas têm um acrônimo consagrado: **RED**.

- **R**ate — quantas requisições por segundo esse serviço está recebendo?
- **E**rrors — quantas estão falhando?
- **D**uration — quanto tempo as que respondem estão levando?

Só com RED por serviço, vocês reconstroem a saúde do sistema inteiro de relance: se o *rate* de Pagamentos sobe e o de Antifraude não acompanha, tem coisa se perdendo entre os dois; se os *errors* do monólito sobem junto com a *duration*, o gargalo é interno; se a *duration* de Pagamentos sobe mas a de todos os outros está estável, o problema é dele ou de uma dependência externa que só ele chama — DICT e SPI, como vocês sabem desde a Aula 1.

Para **recursos** — CPU, memória, disco, pool de conexões, a GPU do Antifraude que a gente provisionou na Aula 5 —, o acrônimo irmão é **USE**: **U**tilization (quão ocupado), **S**aturation (quanto trabalho esperando na fila) e **E**rrors. E reparem numa sutileza que vem direto da teoria de filas da Aula 2: **saturação avisa antes da utilização machucar**. A fila do pool de conexões começando a formar — saturação — aparece antes de o p99 estourar. O cotovelo da curva ρ/(1−ρ) que o outro professor desenhou para vocês é exatamente o ponto onde saturação vira dor; a métrica de saturação é o vigia desse cotovelo.

Duas métricas da TechPix que eu faço questão de elevar a cidadãs de primeira classe, porque elas são as duas cicatrizes das aulas anteriores: o **consumer lag** de cada consumidor de eventos — a distância entre o que o Outbox publicou e o que o consumidor processou, que foi o vilão silencioso do extrato congelado na Aula 4 — e a **taxa de contenção de lock na escrita do ledger**, o tempo que as transações passam esperando o lock da conta `pix_a_liquidar`, a cicatriz original do dia 5. Guardem essa segunda métrica. Ela volta no fim da aula, e não vai ser para coisa boa.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 430" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a7t-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a7t-arrow-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <text x="20" y="24" font-family="sans-serif" font-size="12" fill="#666">TechPix pós-Aula 6 — cada serviço com RED; externos tracejados; as duas métricas de 1ª classe em destaque</text>

  <!-- App -->
  <rect x="20" y="120" width="90" height="50" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="65" y="150" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">App Ana</text>

  <!-- Pagamentos -->
  <rect x="160" y="105" width="170" height="80" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="245" y="130" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Pagamentos</text>
  <text x="245" y="148" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">serviço (Aula 6)</text>
  <rect x="195" y="158" width="100" height="18" rx="5" fill="#fff" stroke="#4338ca"/>
  <text x="245" y="171" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">R · E · D</text>
  <line x1="110" y1="145" x2="155" y2="145" stroke="#4338ca" stroke-width="2" marker-end="url(#a7t-arrow)"/>

  <!-- DICT / SPI externos -->
  <rect x="420" y="20" width="130" height="50" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2" stroke-dasharray="6 3"/>
  <text x="485" y="42" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">DICT</text>
  <text x="485" y="58" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">externo · p99 ≤ 1s</text>
  <rect x="580" y="20" width="130" height="50" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2" stroke-dasharray="6 3"/>
  <text x="645" y="42" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">SPI</text>
  <text x="645" y="58" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">externo · p99 4,6s</text>
  <line x1="300" y1="105" x2="440" y2="72" stroke="#d4a017" stroke-width="2" marker-end="url(#a7t-arrow)"/>
  <line x1="330" y1="120" x2="590" y2="72" stroke="#d4a017" stroke-width="2" marker-end="url(#a7t-arrow)"/>

  <!-- Antifraude -->
  <rect x="160" y="240" width="170" height="90" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="245" y="264" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Antifraude e Limites</text>
  <text x="245" y="281" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">serviço · GPU (Aula 5)</text>
  <rect x="180" y="292" width="60" height="18" rx="5" fill="#fff" stroke="#4338ca"/>
  <text x="210" y="305" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">R · E · D</text>
  <rect x="248" y="292" width="70" height="18" rx="5" fill="#fff" stroke="#4338ca"/>
  <text x="283" y="305" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">score/drift</text>
  <line x1="245" y1="185" x2="245" y2="235" stroke="#4338ca" stroke-width="2" marker-end="url(#a7t-arrow)"/>
  <text x="255" y="215" font-family="sans-serif" font-size="10" fill="#666">síncrono ≤100ms</text>

  <!-- Monolito -->
  <rect x="430" y="120" width="230" height="110" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="545" y="145" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">Monólito: Contas e Ledger</text>
  <text x="545" y="163" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">escrita forte · conta pix_a_liquidar</text>
  <rect x="450" y="175" width="60" height="18" rx="5" fill="#fff" stroke="#4338ca"/>
  <text x="480" y="188" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">R · E · D</text>
  <rect x="520" y="175" width="122" height="18" rx="5" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="581" y="188" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">⚠ contenção de lock</text>
  <text x="545" y="218" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">métrica de 1ª classe — volta no fim da aula</text>
  <line x1="330" y1="150" x2="425" y2="150" stroke="#4338ca" stroke-width="2" marker-end="url(#a7t-arrow)"/>

  <!-- Outbox / consumidores -->
  <rect x="430" y="280" width="110" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="485" y="302" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Outbox</text>
  <text x="485" y="318" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">(ADR-002)</text>
  <line x1="545" y1="230" x2="490" y2="275" stroke="#166534" stroke-width="2" marker-end="url(#a7t-arrow-g)"/>
  <rect x="590" y="280" width="180" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="680" y="300" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">Consumidores (extrato, feed)</text>
  <rect x="612" y="306" width="136" height="17" rx="5" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="680" y="318" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">⚠ consumer lag (Aula 4)</text>
  <line x1="540" y1="305" x2="585" y2="305" stroke="#166534" stroke-width="2" marker-end="url(#a7t-arrow-g)"/>

  <!-- Devolucoes -->
  <rect x="700" y="120" width="170" height="60" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="785" y="145" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Devoluções e Disputas</text>
  <rect x="755" y="153" width="60" height="18" rx="5" fill="#fff" stroke="#4338ca"/>
  <text x="785" y="166" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3730a3">R · E · D</text>

  <rect x="20" y="380" width="850" height="34" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="445" y="402" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#3730a3">Saturação avisa antes da utilização machucar: a fila (USE) é o vigia do cotovelo ρ/(1−ρ) da Aula 2.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A topologia observada: RED em cada serviço, USE em cada recurso — e as duas cicatrizes do curso viram métricas de primeira classe.</p>
</div>

### 2.2 Percentis de verdade — e a mentira da média de percentis

O professor da Aula 1 avisou, na Seção 4.6 dele: **latência não é um número, é uma distribuição, e quem manda é a cauda.** Agora eu quero operacionalizar isso, porque tem uma pegadinha estatística que quase todo time comete no primeiro ano.

O jeito certo de coletar latência é em **histograma**: uma série de baldes ("quantas requisições terminaram em até 50ms? até 100ms? até 250ms? até 1s? até 5s?") que permite calcular qualquer percentil depois, no servidor de métricas. O padrão de fato do mercado para isso é o **Prometheus** — modelo de dados de séries temporais, coleta por *pull*, histogramas nativos — e é o que a TechPix usa.

A pegadinha: **percentil não se agrega por média.** Se a instância A de Pagamentos reporta p99 de 200ms e a instância B reporta p99 de 2 segundos, o p99 da frota **não é** 1,1 segundo — pode ser qualquer coisa, dependendo de quanto tráfego cada uma serviu. Média de percentis é um número que parece informação e não é. O jeito certo: agregar os **histogramas** (baldes se somam, matematicamente é honesto) e calcular o percentil sobre o histograma somado. Toda ferramenta séria faz isso — mas só se vocês coletarem histograma, e não o percentil já calculado na instância.

E o corolário que conecta com a Ana: **um p99 saudável esconde, por definição, 1% das requisições.** A 900 TPS de pico, 1% são 9 transações por segundo — 540 por minuto — vivendo além do p99, invisíveis para ele. O Pix da Ana estava nesse território: contas recém-criadas como a da confeitaria eram uma fração de 0,002% do tráfego. Nem o p99,9 se mexeu. **A média mente, o p99 esconde, o trace confessa** — mas calma, o trace é a Seção 4.

### 2.3 Cardinalidade: a conta que derruba o Prometheus

Toda métrica tem etiquetas — *labels*: `serviço`, `endpoint`, `código_http`. Cada combinação única de valores de etiquetas cria uma **série temporal** nova, armazenada e indexada separadamente. E aqui mora o erro clássico, que eu já vi derrubar o sistema de monitoramento — a ironia de morrer o vigia — em mais de uma empresa: etiquetar métrica com um identificador de alta cardinalidade.

Façam a conta comigo. `latencia_pix{endpoint, código}` com 10 endpoints e 5 códigos: 50 séries. Alguém, bem-intencionado, adiciona `conta_id` para "investigar por cliente": com 2 milhões de contas ativas, viraram **100 milhões de séries**. O Prometheus não morre por tráfego; morre por cardinalidade. A memória do servidor de métricas escala com o número de séries, não com o número de amostras.

A regra que eu deixo: **métrica é para agregado; identificador é para log e trace.** "Qual a latência por *tipo* de conta (nova/estabelecida)?" — etiqueta legítima, cardinalidade 2. "Qual a latência da conta 4711?" — isso é uma pergunta de trace, e é exatamente por isso que os pilares são três e não um. Quando alguém pedir `conta_id` numa métrica, a resposta não é "não pode"; é "essa pergunta se responde com outro pilar".

---

## 3. Logs estruturados: o presente que o BACEN deu para vocês

### 3.1 Log é evento, não frase

O log tradicional é uma frase para humanos: `"Pagamento processado com sucesso para a conta 4711"`. Isso funciona até o dia em que vocês precisam responder "quantos pagamentos entre 16h30 e 17h tiveram retry na feature store?" — e aí alguém escreve uma expressão regular às 3 da manhã, chorando.

Log estruturado é **evento em formato de máquina** — JSON, um registro por linha, campos nomeados:

```json
{
  "ts": "2025-12-05T16:41:07.312-03:00",
  "nivel": "WARN",
  "servico": "antifraude",
  "evento": "feature_store_retry",
  "tentativa": 3,
  "timeout_ms": 1500,
  "e2e_id": "E12345678202512051641a1b2c3d4e5f6",
  "conta_tipo": "recem_criada",
  "chave_pix": "[MASCARADO]",
  "duracao_ms": 1502
}
```

Reparem em dois campos desse exemplo, porque cada um carrega uma lição da aula.

### 3.2 O EndToEndId é o ID de correlação que vocês não precisaram inventar

Todo sistema distribuído maduro chega à mesma necessidade: um **ID de correlação** — um identificador único que nasce na entrada da requisição e viaja por todos os serviços que ela toca, carimbado em cada log, para que depois se possa juntar a história inteira com uma única busca.

E aqui vem a jogada de mestre que eu quero que vocês apreciem: **o Pix já tem esse ID, por desenho regulatório.** O **EndToEndId** da Aula 1 — os 32 caracteres que nascem com a transação, atravessam o SPI, chegam ao Banco Beta do Bruno e voltam na `pacs.002` — é, dentro da TechPix, o ID de correlação natural de todo o fluxo de pagamento. A mesma chave que garante a idempotência da Ana e que reconcilia o ledger com o BACEN é a chave que costura os logs de Pagamentos, Antifraude, Ledger e do ACL do SPI numa narrativa única.

**O regulador obrigou a TechPix a ter rastreamento distribuído antes de a gente saber o nome disso.** Quando o Banco Central exigiu um identificador único ponta a ponta, ele estava — sem usar essas palavras — exigindo correlação de logs e trace distribuído. Cabe a vocês só não desperdiçar o presente: o `e2e_id` entra em **todo** log de **todo** serviço que toca a transação, sem exceção. Para fluxos que não são Pix — onboarding, consulta de extrato —, a TechPix gera um ID de correlação próprio na borda, com a mesma disciplina. A regra é uma só: **nenhum evento de log órfão de correlação.**

### 3.3 O que nunca, jamais, entra num log

Agora o campo `"chave_pix": "[MASCARADO]"`. Numa fintech, o log é um risco de compliance andando. A chave Pix pode ser um CPF, um telefone, um e-mail — **dado pessoal sob LGPD**, como o professor da Aula 1 explicou quando mostrou por que o DICT tem anti-scraping. Logar chave Pix em texto claro é criar um segundo DICT, sem controle de acesso, espalhado por sistemas de log que metade da empresa consegue ler, com retenção de anos por exigência de auditoria.

A disciplina da TechPix: dado pessoal e credencial **nunca** entram em log — nem "só em DEBUG", porque DEBUG vaza para produção no primeiro incidente. O que entra é o dado mascarado ou um identificador interno opaco (`conta_tipo`, `cliente_ref` interno). O mascaramento acontece na **biblioteca de log**, centralizada, não na boa vontade de cada desenvolvedor — é uma fitness function, no sentido da Aula 2: um teste no CI varre os campos logados contra uma lista de proibidos, e PR que loga campo sensível não passa. Auditabilidade e privacidade, as duas exigências do regulador, na mesma decisão de engenharia.

### 3.4 Sampling: nem todo log merece viver

A 900 TPS, com cada transação gerando dezenas de eventos de log pelos serviços, a TechPix produz da ordem de dezenas de milhares de linhas por segundo. Guardar tudo, indexado, por anos? A conta de armazenamento passa a competir com a conta de infraestrutura do sistema que ele observa.

A resposta é **amostragem com viés inteligente**: eventos de erro e de warning, 100% — são raros e valiosos. Eventos de sucesso do caminho feliz, uma amostra — 1%, 10%, conforme o fluxo. E uma regra de ouro que antecipa a Seção 4: **se a transação foi amostrada para tracing, todos os logs dela são retidos** — trace sem log é um mapa sem legenda. O log de auditoria contábil — o ledger em si — está fora dessa conversa, claro: aquilo não é log operacional, é a fonte da verdade da Aula 1, com retenção regulatória integral. **Log operacional se amostra; registro contábil, jamais.**

---

## 4. Tracing distribuído: a caça aos 9 segundos

### 4.1 Spans, contexto, e a carona no deadline

Chegou a hora de achar o Pix da Ana. A ferramenta é o **tracing distribuído**, e o padrão aberto que o mercado consolidou — e que a TechPix usa — é o **OpenTelemetry**: uma especificação e um conjunto de bibliotecas, mantidos pela comunidade, para gerar e propagar telemetria de forma neutra de fornecedor.

O modelo mental é simples. Um **trace** é a história completa de uma requisição. Ele é composto de **spans** — segmentos nomeados, cada um com início, fim, duração e atributos, aninhados uns nos outros como uma pilha de chamadas distribuída: o span "processar Pix" de Pagamentos contém o span "consultar DICT", o span "avaliar risco" (que vive no serviço de Antifraude, em outro processo, em outra máquina), o span "reservar fundos" (no monólito), o span "enviar pacs.008".

Como o span do Antifraude sabe que pertence ao trace que começou em Pagamentos? **Propagação de contexto**: um cabeçalho padronizado (o `traceparent` do W3C) viaja em cada chamada gRPC e em cada evento publicado, carregando o ID do trace e do span pai. E aqui eu cobro o que ensinei na Aula 4: o **deadline propagation** que a gente instalou lá — aquele orçamento de tempo que viaja com a requisição — usa exatamente o mesmo mecanismo de metadados. O contexto de trace pega **carona na mesma infraestrutura**. Quem fez o dever de casa da Aula 4 ganhou o da Aula 7 quase de graça; é por isso que a ordem das aulas é essa.

Tracing custa caro — cada span é dado gerado, transmitido, armazenado — então se amostra, tipicamente 1 a 10% do tráfego. E aqui, uma decisão de projeto que vai salvar a investigação de hoje: amostragem **na cabeça** (decidir no início da requisição) é barata mas cega — ela não sabe, ao decidir, se a requisição vai ser interessante. Amostragem **na cauda** (*tail-based*: coletar tudo, decidir reter *depois* de ver como terminou) permite a política que a TechPix adotou: **reter 100% dos traces lentos ou com erro, e 1% do caminho feliz.** O Pix da Ana levou 9 segundos — lento — logo, o trace dele foi retido. A agulha já estava separada do palheiro no momento em que caiu.

Antes de abrir o trace da Ana, deixa eu desenhar num quadro só **onde toda essa telemetria mora** — porque até agora eu falei dos três pilares um por um, e em produção eles são um encanamento único, com stack de verdade em cada estágio:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a7s-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a7s-arrow-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>

  <!-- Producers -->
  <text x="105" y="26" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Quem produz</text>
  <rect x="30" y="40" width="150" height="52" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="105" y="61" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Pagamentos</text>
  <rect x="55" y="68" width="100" height="17" rx="4" fill="#eef2ff" stroke="#4338ca"/>
  <text x="105" y="80" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#3730a3">OTel SDK</text>

  <rect x="30" y="104" width="150" height="52" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="105" y="125" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Antifraude</text>
  <rect x="55" y="132" width="100" height="17" rx="4" fill="#eef2ff" stroke="#4338ca"/>
  <text x="105" y="144" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#3730a3">OTel SDK</text>

  <rect x="30" y="168" width="150" height="52" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="105" y="186" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#333">Monólito</text>
  <text x="105" y="199" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">Contas + Ledger</text>
  <rect x="55" y="203" width="100" height="14" rx="4" fill="#eef2ff" stroke="#4338ca"/>
  <text x="105" y="214" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#3730a3">OTel SDK</text>

  <text x="105" y="245" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">traceparent (W3C) viaja</text>
  <text x="105" y="258" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">no gRPC e nos eventos —</text>
  <text x="105" y="271" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">a mesma carona do deadline (Aula 4)</text>

  <!-- Arrows to collector -->
  <line x1="180" y1="66" x2="255" y2="120" stroke="#4338ca" stroke-width="2" marker-end="url(#a7s-arrow)"/>
  <line x1="180" y1="130" x2="255" y2="135" stroke="#4338ca" stroke-width="2" marker-end="url(#a7s-arrow)"/>
  <line x1="180" y1="194" x2="255" y2="150" stroke="#4338ca" stroke-width="2" marker-end="url(#a7s-arrow)"/>

  <!-- Collector -->
  <rect x="258" y="95" width="170" height="90" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2.5"/>
  <text x="343" y="118" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#26215C">OTel Collector</text>
  <text x="343" y="136" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">recebe · processa · exporta</text>
  <text x="343" y="151" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">amostragem tail-based:</text>
  <text x="343" y="165" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5a55a0">100% lentos/erro · 1% feliz</text>
  <text x="343" y="200" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">neutro de fornecedor: trocar</text>
  <text x="343" y="213" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">backend não muda o código</text>

  <!-- Arrows to backends -->
  <line x1="428" y1="115" x2="505" y2="70" stroke="#4338ca" stroke-width="2" marker-end="url(#a7s-arrow)"/>
  <line x1="428" y1="140" x2="505" y2="150" stroke="#4338ca" stroke-width="2" marker-end="url(#a7s-arrow)"/>
  <line x1="428" y1="165" x2="505" y2="230" stroke="#4338ca" stroke-width="2" marker-end="url(#a7s-arrow)"/>

  <!-- Backends -->
  <text x="595" y="26" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Onde mora cada pilar</text>
  <rect x="508" y="42" width="175" height="56" rx="8" fill="#fff" stroke="#166534" stroke-width="2"/>
  <text x="595" y="61" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Prometheus</text>
  <text x="595" y="76" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#166534">métricas · pull · histogramas</text>
  <text x="595" y="90" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">barato — cardinalidade controlada</text>

  <rect x="508" y="122" width="175" height="56" rx="8" fill="#fff" stroke="#d4a017" stroke-width="2"/>
  <text x="595" y="141" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Logs estruturados</text>
  <text x="595" y="156" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#7a5c00">JSON · e2e_id · mascarados</text>
  <text x="595" y="170" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">médio — cresce com o tráfego</text>

  <rect x="508" y="202" width="175" height="56" rx="8" fill="#fff" stroke="#b91c1c" stroke-width="2"/>
  <text x="595" y="221" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7f1d1d">Traces (Jaeger/Tempo)</text>
  <text x="595" y="236" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#7f1d1d">spans · jornada por requisição</text>
  <text x="595" y="250" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#666">caro — por isso se amostra</text>

  <!-- Grafana -->
  <line x1="683" y1="70" x2="758" y2="130" stroke="#166534" stroke-width="2" marker-end="url(#a7s-arrow-g)"/>
  <line x1="683" y1="150" x2="758" y2="150" stroke="#166534" stroke-width="2" marker-end="url(#a7s-arrow-g)"/>
  <line x1="683" y1="230" x2="758" y2="170" stroke="#166534" stroke-width="2" marker-end="url(#a7s-arrow-g)"/>
  <rect x="760" y="110" width="95" height="86" rx="9" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/>
  <text x="807" y="134" text-anchor="middle" font-family="sans-serif" font-size="12.5" font-weight="bold" fill="#166534">Grafana</text>
  <text x="807" y="152" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#166534">dashboards</text>
  <text x="807" y="166" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#166534">alerta = burn rate</text>
  <text x="807" y="180" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#166534">exemplar → trace</text>

  <!-- Bottom band -->
  <rect x="30" y="300" width="825" height="52" rx="8" fill="#fef9e7" stroke="#d4a017"/>
  <text x="442" y="322" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#7a5c00">Trade-off do encanamento: métrica é barata e agregada (perde o indivíduo) · trace é caro e individual (por isso tail-based) · log é o meio-termo —</text>
  <text x="442" y="339" text-anchor="middle" font-family="sans-serif" font-size="11.5" fill="#7a5c00">e o exemplar no Grafana é a ponte de um clique entre o agregado e a jornada da Ana</text>

  <text x="442" y="380" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">Instrumentar uma vez (OTel), exportar para onde quiser — o Collector desacopla o código dos backends</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O encanamento de observabilidade da TechPix, com a stack nomeada: OTel SDK → Collector → Prometheus / logs / traces → Grafana.</p>
</div>

### 4.2 O trace da Ana, span a span

O Rafael pegou o `e2e_id` do ticket — o atendimento consegue vê-lo na ferramenta interna, mascarado de dados pessoais —, colou na busca de traces, e a história inteira abriu na tela. Eu reproduzo aqui a estrutura, com as durações reais:

```
TRACE e2e_id=E1234...f6 · total: 9.214 ms                    05/12/2025 16:41:07
└─ pagamentos: processar_pix ............................ 9.214 ms
   ├─ validar_ordem ..................................... 11 ms
   ├─ dict: resolver_chave (cache hit) .................. 38 ms
   ├─ antifraude: avaliar_risco ......................... 6.917 ms  ⚠
   │  ├─ feature_store: get_features [tentativa 1] ...... 1.502 ms  (timeout 1.500 ms)
   │  ├─ backoff ........................................ 100 ms
   │  ├─ feature_store: get_features [tentativa 2] ...... 1.501 ms  (timeout)
   │  ├─ backoff ........................................ 200 ms
   │  ├─ feature_store: get_features [tentativa 3] ...... 1.503 ms  (timeout)
   │  ├─ backoff ........................................ 400 ms
   │  ├─ feature_store: get_features [tentativa 4] ...... 1.640 ms  (sucesso)
   │  └─ inferencia: modelo_risco_v3 .................... 41 ms
   ├─ ledger: reservar_fundos (FundosReservados) ........ 58 ms
   ├─ spi: enviar_pacs008 + aguardar_pacs002 ............ 2.130 ms
   └─ publicar_eventos + responder ...................... 39 ms
```

Leiam esse trace comigo, porque ele é a aula inteira condensada. O DICT: 38 milissegundos, cache da Aula 1 funcionando. O SPI: 2,1 segundos, dentro do p50 de 2,8s que o Banco Central publica. O ledger: 58 milissegundos. E no meio, um elefante: **6,9 segundos dentro do Antifraude — dos quais 6,8 são quatro tentativas contra a feature store e os backoffs entre elas.**

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="22" font-family="sans-serif" font-size="12" fill="#666">Trace e2e_id=E1234...f6 · total 9.214 ms · 05/12/2025 16:41 — cada barra na escala real do tempo</text>
  <!-- time axis -->
  <line x1="190" y1="40" x2="850" y2="40" stroke="#999" stroke-width="1"/>
  <g font-family="sans-serif" font-size="10" fill="#999">
    <line x1="190" y1="36" x2="190" y2="44" stroke="#999"/><text x="190" y="56" text-anchor="middle">0s</text>
    <line x1="333" y1="36" x2="333" y2="44" stroke="#999"/><text x="333" y="56" text-anchor="middle">2s</text>
    <line x1="476" y1="36" x2="476" y2="44" stroke="#999"/><text x="476" y="56" text-anchor="middle">4s</text>
    <line x1="620" y1="36" x2="620" y2="44" stroke="#999"/><text x="620" y="56" text-anchor="middle">6s</text>
    <line x1="763" y1="36" x2="763" y2="44" stroke="#999"/><text x="763" y="56" text-anchor="middle">8s</text>
    <line x1="850" y1="36" x2="850" y2="44" stroke="#999"/><text x="850" y="56" text-anchor="middle">9,2s</text>
  </g>
  <!-- rows -->
  <g font-family="sans-serif" font-size="11" fill="#333">
    <text x="180" y="82" text-anchor="end">processar_pix (total)</text>
    <rect x="190" y="70" width="660" height="16" rx="3" fill="#eef2ff" stroke="#4338ca"/>

    <text x="180" y="112" text-anchor="end">validar + DICT (cache)</text>
    <rect x="190" y="100" width="4" height="16" rx="1" fill="#4338ca"/>
    <text x="200" y="112" font-size="10" fill="#666">11 + 38 ms</text>

    <text x="180" y="142" text-anchor="end">antifraude: avaliar_risco</text>
    <rect x="194" y="130" width="495" height="16" rx="3" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
    <text x="440" y="127" text-anchor="middle" font-size="10" fill="#b91c1c" font-weight="bold">6.917 ms ⚠ — o elefante</text>

    <!-- attempts breakdown -->
    <text x="180" y="172" text-anchor="end">└ feature store (4 tentativas)</text>
    <rect x="194" y="160" width="107" height="16" fill="#b91c1c" opacity="0.75"/>
    <rect x="301" y="160" width="7" height="16" fill="#d4a017" opacity="0.7"/>
    <rect x="308" y="160" width="107" height="16" fill="#b91c1c" opacity="0.75"/>
    <rect x="415" y="160" width="14" height="16" fill="#d4a017" opacity="0.7"/>
    <rect x="429" y="160" width="108" height="16" fill="#b91c1c" opacity="0.75"/>
    <rect x="537" y="160" width="29" height="16" fill="#d4a017" opacity="0.7"/>
    <rect x="566" y="160" width="118" height="16" fill="#166534" opacity="0.75"/>
    <text x="248" y="192" text-anchor="middle" font-size="10" fill="#b91c1c">timeout 1,5s</text>
    <text x="362" y="192" text-anchor="middle" font-size="10" fill="#b91c1c">timeout 1,5s</text>
    <text x="483" y="192" text-anchor="middle" font-size="10" fill="#b91c1c">timeout 1,5s</text>
    <text x="625" y="192" text-anchor="middle" font-size="10" fill="#166534">sucesso 1,6s</text>
    <text x="700" y="172" font-size="10" fill="#7a5c00">backoffs 100/200/400ms</text>

    <text x="180" y="222" text-anchor="end">└ inferência modelo_v3</text>
    <rect x="684" y="210" width="4" height="16" fill="#166534"/>
    <text x="695" y="222" font-size="10" fill="#166534">41 ms — o modelo não é o problema</text>

    <text x="180" y="252" text-anchor="end">ledger: reservar_fundos</text>
    <rect x="689" y="240" width="5" height="16" fill="#4338ca"/>
    <text x="702" y="252" font-size="10" fill="#666">58 ms</text>

    <text x="180" y="282" text-anchor="end">SPI: pacs.008 → pacs.002</text>
    <rect x="694" y="270" width="152" height="16" rx="3" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
    <text x="770" y="282" text-anchor="middle" font-size="10" fill="#166534">2.130 ms — normal</text>
  </g>
  <rect x="20" y="300" width="860" height="26" rx="6" fill="#fef2f2" stroke="#b91c1c" stroke-dasharray="4 3"/>
  <text x="450" y="317" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">O orçamento da aresta era 100 ms — a biblioteca surda ao deadline gastou 69× isso em retries que o fallback nunca enxergou.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O waterfall dos 9 segundos: DICT, ledger e SPI saudáveis — 74% do tempo morreu em retries mal posicionados dentro do Antifraude.</p>
</div>

A causa-raiz, montada com os logs correlacionados pelo `e2e_id` (os três pilares se revezando, como prometido): a conta da confeitaria era **recém-criada**. As features online dela — "Pix recebidos na última hora", as janelas agregadas que a Aula 5 construiu sobre o rio de eventos — ainda não existiam no cache da feature store. O caminho de *cold start* ia montá-las sob demanda, e isso levava mais do que o normal. Só que o cliente da feature store dentro do Antifraude — uma biblioteca interna antiga, anterior à disciplina da Aula 4 — usava **timeout local próprio de 1,5 segundo e política de retry própria**, por fora do deadline propagation. O deadline global da requisição dizia "você tem 100 milissegundos para o risco"; a biblioteca, surda a isso, tentou 4 vezes de 1,5 segundo com backoff de 100/200/400 milissegundos no meio — os números da Aula 2, aplicados no lugar errado. E do lado de quem chamava, o mesmo pecado: o cliente que Pagamentos usava nessa rota também antecedia o Contrato da Aula 4 e não aplicava o timeout de 150 milissegundos declarado para a aresta — o postmortem lista os dois como o mesmo fator contribuinte, "bibliotecas fora da disciplina de deadline".

E o detalhe mais fino, que eu quero que vocês levem para casa: **o fallback fail-closed da Aula 5 nunca disparou.** Ele estava configurado para "feature store *falhou*" — e a feature store nunca falhou de vez; ela ficou *quase* respondendo, tentativa após tentativa, até responder na quarta. **O retry mal posicionado não só roubou 6,8 segundos do orçamento — ele escondeu a degradação exatamente do mecanismo desenhado para reagir a ela.** Retry esconde falha; deadline revela. Se o deadline de 100ms tivesse sido respeitado, o fallback teria assumido em 100 milissegundos, a política de decisão teria segurado a transação de valor alto ou liberado a de valor baixo — decisão de negócio, como definimos na Aula 4 — e a Ana teria a resposta dela em 2 segundos e pouco.

### 4.3 Por que nenhuma métrica gritou — e o que liga métrica a trace

Agora respondam vocês: por que os painéis estavam verdes? Porque contas recém-criadas eram ~0,002% do tráfego do dia. A 900 TPS, isso é uma transação a cada minuto, mais ou menos. O p99 precisa de 1% para se mexer; o p99,9, de 0,1%. **Uma população de 0,002% não move percentil nenhum — e cada cliente dentro dela teve uma experiência 4 vezes pior que o p99.** O agregado protege o sistema; não protege cada cliente. Numa fintech, onde cada transação lenta é alguém achando que perdeu dinheiro, essa distinção é o motivo de o tracing existir.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 860 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="22" font-family="sans-serif" font-size="12" fill="#666">Distribuição de latência do dia 5 — por que os painéis ficaram verdes</text>
  <!-- axis -->
  <line x1="60" y1="230" x2="830" y2="230" stroke="#999" stroke-width="1.5"/>
  <g font-family="sans-serif" font-size="10" fill="#999">
    <text x="60" y="248" text-anchor="middle">0s</text>
    <text x="215" y="248" text-anchor="middle">2s</text>
    <text x="370" y="248" text-anchor="middle">4s</text>
    <text x="525" y="248" text-anchor="middle">6s</text>
    <text x="680" y="248" text-anchor="middle">8s</text>
    <text x="820" y="248" text-anchor="middle">10s</text>
  </g>
  <!-- histogram bars (green mass) -->
  <g fill="#bbf7d0" stroke="#166534">
    <rect x="75" y="200" width="30" height="30"/>
    <rect x="110" y="130" width="30" height="100"/>
    <rect x="145" y="70" width="30" height="160"/>
    <rect x="180" y="60" width="30" height="170"/>
    <rect x="215" y="90" width="30" height="140"/>
    <rect x="250" y="140" width="30" height="90"/>
    <rect x="285" y="180" width="30" height="50"/>
    <rect x="320" y="210" width="30" height="20"/>
    <rect x="355" y="222" width="30" height="8"/>
  </g>
  <!-- média line -->
  <line x1="207" y1="45" x2="207" y2="230" stroke="#4338ca" stroke-width="2" stroke-dasharray="6 3"/>
  <text x="207" y="38" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#4338ca" font-weight="bold">média 1,9s</text>
  <!-- p99 line -->
  <line x1="323" y1="65" x2="323" y2="230" stroke="#7a5c00" stroke-width="2" stroke-dasharray="6 3"/>
  <text x="323" y="60" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7a5c00" font-weight="bold">p99 3,4s ✓</text>
  <!-- the sliver -->
  <rect x="750" y="218" width="14" height="12" fill="#b91c1c"/>
  <circle cx="757" cy="200" r="12" fill="none" stroke="#b91c1c" stroke-width="2"/>
  <line x1="757" y1="212" x2="757" y2="216" stroke="#b91c1c" stroke-width="2"/>
  <text x="757" y="178" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#b91c1c">a Ana está aqui</text>
  <text x="757" y="162" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">0,002% · contas recém-criadas</text>
  <rect x="60" y="264" width="770" height="28" rx="6" fill="#eef2ff" stroke="#c7d2fe"/>
  <text x="445" y="283" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#3730a3">p99 precisa de 1% para se mexer; p99,9, de 0,1%. Uma cauda de 0,002% é invisível ao agregado — só o trace a encontra.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A média mente, o p99 esconde, o trace confessa: o agregado protege o sistema, não cada cliente.</p>
</div>

A ponte de volta para as métricas tem nome: **exemplar**. Um exemplar é uma referência de trace anexada a um balde do histograma — "este balde de 5-10 segundos contém, entre outros, o trace tal". No dashboard, o balde alto da cauda vira um link clicável: da métrica agregada para a jornada individual em um clique. Depois do postmortem — já chego lá —, a TechPix também criou a métrica que faltava: `feature_store_cold_start` com etiqueta `conta_tipo="recem_criada"` — cardinalidade 2, dentro da regra da Seção 2.3. A pergunta que era *unknown unknown* no dia 5 virou *known* no dia 6. **É assim que observabilidade funciona: cada investigação transforma uma pergunta nova em um medidor permanente.**

---

## 5. Monitorando o que não é determinístico: o modelo em produção

### 5.1 Modelo não quebra — apodrece

Tudo que eu falei até aqui monitora código determinístico: ele quebra com erro, timeout, stack trace — eventos discretos, detectáveis. O modelo de risco da Aula 5 é um animal diferente. **Modelo não quebra com stack trace; ele apodrece em silêncio.** O mundo muda — os fraudadores da madrugada de outubro que inventaram o golpe dos R$ 49,90 não pararam de inventar —, os padrões que o modelo aprendeu vão ficando defasados, e a qualidade das decisões degrada sem nenhum erro aparecer em lugar nenhum. O serviço responde 200, o p99 está lindo, e o modelo está errando cada vez mais.

O nome disso é **drift** — deriva. Eu semeei essa palavra na Aula 5; agora ela vira métrica. Dois sabores que importam:

- **Drift de dados:** a distribuição das *entradas* mudou. As features que chegam hoje não se parecem com as do treino — o perfil de valor dos Pix mudou, o Pix Automático da Aula 1 trouxe um padrão de recorrência que não existia, uma campanha de marketing trouxe um público novo.
- **Drift de conceito:** a *relação* entre entrada e resposta certa mudou. As mesmas features que indicavam fraude em outubro indicam comportamento legítimo em dezembro — ou o contrário, que é pior.

### 5.2 O exame de sangue do modelo

Como se detecta apodrecimento sem esperar o prejuízo? **A métrica é o exame de sangue: você não espera o infarto para medir a pressão.** O painel de inferência da TechPix, que o Diego olha toda manhã, tem quatro famílias:

| O que | Como | O que denuncia |
|---|---|---|
| **Distribuição do score** | Histograma dos scores emitidos, comparado com janela de referência (um índice de estabilidade populacional) | Score médio deslizando = o mundo mudou na entrada do modelo |
| **Distribuição das features** | Mesma comparação, por feature crítica | *Qual* pedaço do mundo mudou — e se é bug de pipeline ou drift real |
| **Taxa de fallback e latência de inferência** | % de decisões que caíram no fail-closed; p99 da inferência dentro do orçamento de 100ms | Saúde operacional — foi essa métrica que faltou no caso da Ana |
| **Sombra × ativo** | O desafiante da Aula 5 continua rodando em sombra; divergência entre os dois, acompanhada no tempo | Divergência crescente = um dos dois está envelhecendo |

E o problema honesto, que uma plateia técnica vai apontar: **o rótulo verdadeiro demora.** Vocês só sabem que uma transação era fraude quando o MED chega, dias ou semanas depois — o *ground truth* é atrasado por natureza. Por isso as métricas acima são todas **indicadores antecedentes**: elas não medem "o modelo errou" (isso só o tempo diz), medem "o mundo saiu do lugar onde o modelo foi treinado" — que é o melhor preditor disponível de erro futuro. Quando os rótulos do MED chegam, fecham o ciclo: a precisão real do modelo, calculada em retrospecto, calibra a confiança nos indicadores antecedentes. Guardem o desenho desse ciclo — produção gera sinal, sinal vira avaliação, avaliação vira decisão — porque o professor que volta na Aula 8 vai generalizá-lo para o sistema inteiro, e vocês vão perceber que já o conheciam.

---

## 6. SLO e error budget: a moeda que compra velocidade

### 6.1 Da sopa de siglas à cadeia de decisão

Vocês já viram SLA nesse curso desde a Aula 1 — o do DICT, p99 ≤ 1 segundo, com consequência regulatória. Agora eu completo a família, porque cada sigla tem um papel distinto:

- **SLI** — *Service Level Indicator*: a **medição**. "Proporção de Pix confirmados em até 3,5 segundos, medida na borda, janela de 30 dias."
- **SLO** — *Service Level Objective*: a **meta interna** sobre o SLI. "99,95% dos Pix dentro desse tempo."
- **SLA** — *Service Level Agreement*: a **promessa externa com consequência** — contrato, multa, regulador.

A regra de sanidade: **o SLO interno é sempre mais apertado que o SLA externo.** A TechPix herda do BACEN o índice de disponibilidade da Aula 1 — meta 100%, valores de referência por categoria — e o teto de 40 segundos do Pix. Se a promessa externa é essa, o objetivo interno tem que soar o alarme muito antes: SLO de disponibilidade do fluxo Pix em 99,95%, SLO de latência em 3,5 segundos — margem larga para o teto normativo, coerente com a experiência-alvo de poucos segundos que o SPI real (p50 2,8s, p99 4,6s) permite.

### 6.2 Error budget: transformar meta em moeda

Agora a ideia que eu considero a mais elegante da engenharia de confiabilidade moderna. Um SLO de 99,95% em 30 dias significa que **0,05% de falha é aceitável por definição** — em minutos, cerca de **21,6 minutos de indisponibilidade por mês**. Esse é o **error budget**: o orçamento de erro. E a virada de chave é tratá-lo literalmente como orçamento — **uma moeda que se gasta**.

Gastou pouco este mês? O time tem lastro para ousar: extrair o próximo serviço, ligar o canary da mudança arriscada, testar o modelo desafiante em uma fatia real. Queimou o budget — um incidente comeu 18 dos 21 minutos? **Congela release arriscado até o budget se recuperar**, e a energia do time vai para confiabilidade. Reparem no que isso resolve: a guerra eterna entre "quem quer lançar" e "quem quer estabilidade" deixa de ser disputa de opinião e vira **aritmética combinada de antemão**. O canary da Aula 6 decidia com limiares fixos — taxa de erro sobre o baseline de 0,1%, p99. O error budget dá a esses limiares um contexto de negócio: o quanto de risco *este mês* ainda comporta. É a ponte entre operação e as decisões de release — e, uma aula adiante, entre operação e decisões de arquitetura.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a7b-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a7b-arrow-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
    <marker id="a7b-arrow-r" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- chain SLI -> SLO -> budget -->
  <rect x="20" y="30" width="190" height="60" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="115" y="55" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1a1a1a">SLI — a medição</text>
  <text x="115" y="75" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">% Pix confirmado ≤ 3,5s (30d)</text>
  <line x1="210" y1="60" x2="255" y2="60" stroke="#4338ca" stroke-width="2" marker-end="url(#a7b-arrow)"/>
  <rect x="260" y="30" width="180" height="60" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="350" y="55" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">SLO — a meta</text>
  <text x="350" y="75" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">99,95% (&lt; SLA externo)</text>
  <line x1="440" y1="60" x2="485" y2="60" stroke="#4338ca" stroke-width="2" marker-end="url(#a7b-arrow)"/>
  <rect x="490" y="30" width="200" height="60" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="590" y="55" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Error budget</text>
  <text x="590" y="75" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7a5c00">0,05% = 21,6 min/mês</text>
  <rect x="710" y="30" width="150" height="60" rx="8" fill="#fff" stroke="#999" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text x="785" y="55" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">SLA externo</text>
  <text x="785" y="73" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">BACEN · com multa</text>

  <!-- budget bar -->
  <text x="20" y="140" font-family="sans-serif" font-size="12" fill="#333">O budget do mês como moeda:</text>
  <rect x="230" y="125" width="460" height="26" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <rect x="230" y="125" width="290" height="26" rx="6" fill="#fecaca" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="375" y="143" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#7f1d1d">queimado: 13,5 min (incidente + canary)</text>
  <text x="605" y="143" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">restante: 8,1 min</text>
  <text x="720" y="143" font-family="sans-serif" font-size="10" fill="#666">21,6 min</text>

  <!-- two outcomes -->
  <line x1="450" y1="160" x2="250" y2="205" stroke="#166534" stroke-width="2" marker-end="url(#a7b-arrow-g)"/>
  <rect x="40" y="210" width="360" height="52" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="220" y="231" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Sobrando → pode ousar</text>
  <text x="220" y="250" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#166534">extrair o próximo serviço · canary arriscado · desafiante</text>
  <line x1="470" y1="160" x2="640" y2="205" stroke="#b91c1c" stroke-width="2" marker-end="url(#a7b-arrow-r)"/>
  <rect x="480" y="210" width="360" height="52" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="660" y="231" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">Queimado → congela release</text>
  <text x="660" y="250" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">energia vai para confiabilidade · alerta noturno só por burn rate</text>

  <text x="440" y="288" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">A guerra "lançar × estabilizar" vira aritmética combinada de antemão — não disputa de opinião.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">SLI mede, SLO promete por dentro, SLA promete por fora — e o error budget converte a diferença em moeda de decisão.</p>
</div>

### 6.3 Alertar no sintoma, não na causa

Última disciplina dessa seção, e a mais contraintuitiva para quem vem de operação tradicional: **alerta bom acorda gente por sintoma, não por causa.** CPU a 90% não é sintoma — é causa *possível* de um sintoma que talvez nem exista; a CPU do serviço de inferência vive alta por desenho, e está tudo bem. Alertar em CPU produz o pior dos mundos: páginas às 3h da manhã sem cliente sofrendo — e a fadiga de alerta que faz o Rafael ignorar a página verdadeira no mês seguinte.

O alerta de primeira classe da TechPix é o de **burn rate**: a velocidade de queima do error budget. Queimando na taxa "normal", o budget de 21,6 minutos dura o mês — ninguém acorda. Um alerta de queima rápida dispara quando a taxa recente, medida numa janela curta, consumiria uma fração relevante do budget mensal em poucas horas — aí sim, é incêndio, e acordar alguém se justifica *matematicamente*. Queima lenta — algo consumindo o budget aos poucos, dia após dia — vira ticket de horário comercial, não página. **Cada alerta noturno deve carregar a prova de que valia uma noite de sono.** Causas — CPU, fila, lag — continuam nos dashboards, como *diagnóstico* para quando o sintoma chamar. Alerta é para sofrimento real ou iminente de cliente; dashboard é para investigação.

---

## 7. Incidentes: operação como aprendizado

### 7.1 Do ticket ao postmortem

De volta ao dia 5, uma última vez. O caso da Ana não disparou alerta — e, pelo desenho da Seção 6, *não deveria*: 0,002% do tráfego não queima budget. Ele chegou pelo canal que pega o que os números não pegam: um ticket, uma cliente, uma reclamação real. Sistemas maduros tratam esses dois canais — o alerta quantitativo e a voz do cliente — como igualmente legítimos para abrir investigação.

A TechPix classifica incidentes por severidade — SEV1, dinheiro errado ou indisponibilidade do fluxo Pix, guerra declarada, todo mundo na sala; SEV2, degradação com cliente sofrendo; SEV3, o caso da Ana: dano individual, sem alastramento. Cada severidade tem um **runbook** — o passo a passo de diagnóstico escrito *antes*, de cabeça fria, porque às 3h da manhã ninguém raciocina bem — e papéis definidos: quem investiga, quem comunica, quem decide desligar o quê. O kill switch da Aula 6 é uma das armas do runbook: metade do valor do flag operacional é o on-call poder desarmar uma feature sem chamar ninguém.

### 7.2 Blameless: o postmortem é o ADR do incidente

Resolvido o incidente, começa a parte mais valiosa: o **postmortem**. E aqui eu vou usar a analogia que amarra essa prática ao resto do curso: **o postmortem é o ADR do incidente — imutável, datado, e sem culpados.** O professor das primeiras aulas ensinou que um ADR registra uma decisão com contexto e consequências, para que o sistema aprenda com o próprio passado. O postmortem faz o mesmo com uma falha: linha do tempo factual, minuto a minuto; **fatores contribuintes** — no plural, porque incidente de verdade nunca tem causa única; impacto medido; e ações com dono e prazo.

E a palavra **blameless** — sem culpa — não é gentileza de RH; é engenharia de informação. No caso da Ana, seria fácil parar em "o desenvolvedor da biblioteca antiga esqueceu o deadline". Só que punir essa pessoa produziria exatamente um resultado: **da próxima vez, ninguém conta o que sabe** — e a informação que previne o próximo incidente morre com o medo. O postmortem blameless parte de outro princípio: cada pessoa agiu razoavelmente com a informação que tinha; se o sistema permitiu o erro, **o defeito é do sistema**. Os fatores contribuintes do caso da Ana: uma biblioteca fora da disciplina de deadline da Aula 4 (fator técnico); nenhuma fitness function no CI proibindo cliente HTTP com retry próprio (fator de processo — e a ação virou: criar essa checagem, no espírito da Aula 2); fallback que só via falha total, cego a degradação (fator de desenho); e a métrica de cold start que não existia (fator de observabilidade). Quatro ações, quatro donos, quatro prazos. Nenhum nome no banco dos réus.

A filosofia por trás, que eu quero deixar explícita: num sistema distribuído com dependências externas — SPI, DICT, Banco Beta — **falha não é anomalia; é regime permanente**. A métrica que persegue perfeição é o MTBF, o tempo médio *entre* falhas; a métrica de sistemas maduros é o **MTTR**, o tempo médio de *recuperação*. Otimizar MTBF tem retorno decrescente; otimizar MTTR — detecção rápida, diagnóstico rápido via trace, reversão rápida via ArgoCD e kill switch — é o que transforma o incidente de catástrofe em rotina. **Não se opera um sistema para que ele nunca caia; opera-se para que a queda seja curta, contida e ensinável.**

---

## 8. O artefato da aula — e o sinal que ninguém está lendo

### 8.1 O Catálogo de SLOs

Como as aulas anteriores, essa termina com um artefato — e seguindo a tradição da casa desde a Aula 3, ele é da família da spec, não um ADR: **o Catálogo de SLOs da TechPix**, o documento vivo que registra, para cada fluxo e serviço, o que se mede, qual a meta, quanto custa errar, e quem é o dono:

```
CATÁLOGO DE SLOs · TechPix                        vigência: dez/2025 · revisão: trimestral

Fluxo/Serviço          SLI                                SLO (30d)    Budget      Dono
─────────────────────────────────────────────────────────────────────────────────────────
Pix ponta a ponta      % confirmado ≤ 3,5 s (borda)       99,95%      21,6 min    Pagamentos
Pix ponta a ponta      % sucesso (sem erro técnico)       99,9%       43,2 min    Pagamentos
Escrita no ledger      p99 de commit                      ≤ 80 ms     —           Contas e Ledger
Extrato (leitura)      lag do consumidor p99              ≤ 300 ms    —           Contas e Ledger
Antifraude             p99 avaliar_risco                  ≤ 100 ms    —           Antifraude e Limites
Antifraude             taxa de fallback fail-closed       ≤ 0,5%      —           Antifraude e Limites
Inferência (modelo)    estabilidade do score vs. ref.     sem desvio  —           Antifraude e Limites
Consulta DICT          p99 (herdado BACEN)                ≤ 1 s       regulatório Pagamentos
Disponibilidade SPB    índice BACEN (Aula 1, §5.4)        meta 100%   regulatório TechPix

Regras de uso: budget queimado ⇒ congela release arriscado do fluxo (Aula 6).
Alerta noturno só por burn rate. Revisão trimestral em reunião de arquitetura.
```

Reparem no que esse documento é: a **fronteira entre engenharia e negócio escrita em números**. Cada linha é um trade-off da Aula 1 — latência, consistência, custo, confiabilidade — transformado em compromisso mensurável com dono. E cada linha é, ao mesmo tempo, uma fitness function contínua no sentido da Aula 2: uma propriedade do sistema, verificada o tempo todo, com consequência automática quando violada.

### 8.2 A linha que sobe devagar

E agora eu quero fechar mostrando um dashboard de verdade — o último da aula. Olhem a terceira linha do catálogo: escrita no ledger, p99 ≤ 80 milissegundos. Está verde. Sempre esteve verde. Mas eu guardei a série histórica desde que assumi o curso, e ela conta uma história que nenhum alerta vai contar:

| Mês | p99 de escrita no ledger | Contenção de lock (`pix_a_liquidar`) | TPS médio |
|---|---|---|---|
| ago/2025 | 42 ms | 3,1% do tempo de commit | 410 |
| set/2025 | 45 ms | 3,8% | 460 |
| out/2025 | 49 ms | 4,7% | 530 |
| nov/2025 | 54 ms | 5,9% | 610 |
| dez/2025 | 58 ms | 7,2% | 700 |

Cinco meses, uma direção só. O p99 de escrita subiu 38%. A contenção no lock da conta única de liquidação — a mesma `pix_a_liquidar` da Aula 1, o mesmo ponto quente do dia 5 da Aula 2, que o Outbox do ADR-002 aliviou mas nunca eliminou — mais que dobrou. O volume cresce, e a fila invisível daquela conta cresce junto, exatamente como a teoria de filas da Aula 2 mandava esperar. A linha "Revisão" do ADR-002 dizia: *"se a contenção persistir, o próximo passo é reparticionar a própria escrita do ledger."* Ela está persistindo. Nos meus dashboards, agora, em produção — não mais como hipótese.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 260" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="22" font-family="sans-serif" font-size="12" fill="#666">Série de 5 meses — escrita do ledger (conta única pix_a_liquidar) · tudo verde, tudo subindo</text>

  <!-- Panel 1: p99 -->
  <rect x="30" y="40" width="230" height="150" rx="8" fill="#fff" stroke="#ddd"/>
  <text x="145" y="58" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">p99 de escrita</text>
  <line x1="45" y1="72" x2="250" y2="72" stroke="#b91c1c" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text x="150" y="68" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#b91c1c">SLO ≤ 80 ms</text>
  <polyline points="50,158 98,151 146,141 194,128 242,118" fill="none" stroke="#4338ca" stroke-width="2.5"/>
  <circle cx="50" cy="158" r="3" fill="#4338ca"/><circle cx="242" cy="118" r="3" fill="#4338ca"/>
  <text x="50" y="175" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">42 ms</text>
  <text x="242" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#4338ca">58 ms (+38%)</text>

  <!-- Panel 2: contenção -->
  <rect x="325" y="40" width="230" height="150" rx="8" fill="#fff" stroke="#ddd"/>
  <text x="440" y="58" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">contenção de lock</text>
  <polyline points="345,168 393,154 441,136 489,112 537,86" fill="none" stroke="#b91c1c" stroke-width="2.5"/>
  <circle cx="345" cy="168" r="3" fill="#b91c1c"/><circle cx="537" cy="86" r="3" fill="#b91c1c"/>
  <text x="345" y="184" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">3,1%</text>
  <text x="537" y="80" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#b91c1c">7,2% (2,3×)</text>

  <!-- Panel 3: TPS -->
  <rect x="620" y="40" width="230" height="150" rx="8" fill="#fff" stroke="#ddd"/>
  <text x="735" y="58" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">TPS médio</text>
  <polyline points="640,167 688,153 736,133 784,110 832,84" fill="none" stroke="#166534" stroke-width="2.5"/>
  <circle cx="640" cy="167" r="3" fill="#166534"/><circle cx="832" cy="84" r="3" fill="#166534"/>
  <text x="640" y="184" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">410</text>
  <text x="832" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">700 (+71%)</text>

  <!-- month labels -->
  <g font-family="sans-serif" font-size="9" fill="#999">
    <text x="50" y="202" text-anchor="middle">ago</text><text x="98" y="202" text-anchor="middle">set</text><text x="146" y="202" text-anchor="middle">out</text><text x="194" y="202" text-anchor="middle">nov</text><text x="242" y="202" text-anchor="middle">dez</text>
    <text x="345" y="202" text-anchor="middle">ago</text><text x="393" y="202" text-anchor="middle">set</text><text x="441" y="202" text-anchor="middle">out</text><text x="489" y="202" text-anchor="middle">nov</text><text x="537" y="202" text-anchor="middle">dez</text>
    <text x="640" y="202" text-anchor="middle">ago</text><text x="688" y="202" text-anchor="middle">set</text><text x="736" y="202" text-anchor="middle">out</text><text x="784" y="202" text-anchor="middle">nov</text><text x="832" y="202" text-anchor="middle">dez</text>
  </g>

  <rect x="30" y="216" width="820" height="32" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="440" y="237" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Não é incidente. Não viola SLO. Não acorda ninguém. Mas está subindo há 5 meses — quem lê esse sinal?</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A tendência lenta que nenhum alerta pega: a pendência do ADR-002, agora medida em produção — o gancho da Aula 8.</p>
</div>

E reparem no incômodo: **isso não é um incidente.** Não viola SLO nenhum. Não queima budget. Não acorda o Rafael. Nenhum mecanismo que a gente construiu nessa aula — burn rate, alerta, severidade — foi desenhado para *isso*: uma tendência lenta, meses de horizonte, que um dia vai cruzar um limiar e virar o incidente que a gente já sabe qual é. O sistema inteiro de operação responde à pergunta "o que está doendo agora?". Essa linha responde a outra pergunta: "o que vai doer em alguns meses?" — e essa pergunta, hoje, **não tem leitor**. Eu vou fazer o que a disciplina manda: deixar anotado, registrado, com a série histórica preservada. O próximo ADR numerado, o 003, só nasce quando alguém decidir mexer na escrita do ledger — **e hoje não é esse dia, nem sou eu que vou tomar essa decisão.**

Mas a pergunta fica armada, e ela é o gancho final do meu trecho do curso: **quem lê esse sinal?** Um humano olhando dashboard todo dia esquece; um alerta não dispara para tendência lenta; uma reunião trimestral de arquitetura olha para trás, não para frente. Existe hoje uma categoria nova de leitor para esse tipo de sinal — e o professor que abriu esse curso com vocês, o das decisões "na fé" da Aula 1, volta na próxima aula exatamente para apresentá-lo, com o sistema maduro, os dados que a gente acabou de aprender a coletar, e meses de série histórica esperando por um leitor que não pisca.

---

## 9. Para fechar: as três ideias-âncora

Primeiro: **observabilidade é responder perguntas que você ainda não fez.** Métrica diz quanto, log diz o quê, trace diz por onde — e a investigação real usa os três em revezamento. A média mente, o p99 esconde, o trace confessa: o agregado protege o sistema, mas só a jornada individual protege cada cliente — e o EndToEndId que o BACEN exigiu é o fio que costura tudo, de graça.

Segundo: **SLO transforma confiabilidade em aritmética combinada.** O error budget é a moeda que compra velocidade: sobrando, o time ousa; queimado, o time estabiliza — e a guerra entre lançar e estabilizar vira conta, não opinião. Alerta acorda gente por sintoma com prova matemática; causa é assunto de dashboard.

Terceiro: **operar é aprender em público.** Falha é regime permanente, não anomalia; MTTR vale mais que MTBF; o postmortem é o ADR do incidente — imutável, datado, blameless — porque punir quem conta a verdade é assassinar a informação que previne a próxima falha.

E o último retrato de plantão da minha parte no curso. Reparem no que esta aula acrescentou: nenhuma caixa nova processa um Pix sequer — todas elas **enxergam**. E reparem também na caixinha âmbar, porque ela é deliberada: tem um sinal ali dentro que ninguém tratou, e isso não é esquecimento — é a herança que eu deixo para a Aula 8.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 880 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <text x="440" y="22" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#333">A TechPix ao fim da Aula 7</text>

  <text x="20" y="44" font-family="sans-serif" font-size="10" font-weight="bold" fill="#a8a29e">JÁ EXISTIA — AULAS 1 A 6</text>
  <g font-family="sans-serif">
    <rect x="20" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="122" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Monólito Contas + Ledger</text>
    <text x="122" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">Postgres serializable · pix_a_liquidar · [A1]</text>
    <rect x="232" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="334" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Outbox → Kafka + CQRS</text>
    <text x="334" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">read models Redis/réplica · [A2]</text>
    <rect x="444" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="546" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Contextos + contratos</text>
    <text x="546" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">specs · gRPC · registry · DLQ · [A3·A4]</text>
    <rect x="656" y="52" width="204" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="758" y="71" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Antifraude com ML</text>
    <text x="758" y="87" text-anchor="middle" font-size="9.5" fill="#78716c">GPU · feature store Redis · [A5]</text>

    <rect x="20" y="104" width="416" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="228" y="123" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Serviços em Kubernetes (Antifraude · Pagamentos)</text>
    <text x="228" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">database-per-service · Ledger fica no monólito · [A6]</text>
    <rect x="444" y="104" width="416" height="46" rx="8" fill="#f5f5f4" stroke="#a8a29e" stroke-width="1.5"/>
    <text x="652" y="123" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#57534e">Entrega progressiva</text>
    <text x="652" y="139" text-anchor="middle" font-size="9.5" fill="#78716c">ArgoCD · canary via Envoy · Unleash · fitness functions · [A6]</text>
  </g>

  <text x="20" y="172" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">CONSTRUÍDO NESTA AULA</text>
  <g font-family="sans-serif">
    <rect x="20" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="101" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Métricas</text>
    <text x="101" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">OTel → Prometheus · Grafana</text>
    <rect x="192" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="273" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Logs estruturados</text>
    <text x="273" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">correlação por e2e_id · LGPD</text>
    <rect x="364" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="445" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Tracing distribuído</text>
    <text x="445" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">spans ponta a ponta · exemplars</text>
    <rect x="536" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="617" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">Monitoração do modelo</text>
    <text x="617" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">drift · fallback · sombra×ativo</text>
    <rect x="708" y="180" width="163" height="50" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
    <text x="789" y="200" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#166534">SLOs + error budget</text>
    <text x="789" y="217" text-anchor="middle" font-size="9.5" fill="#15803d">burn rate · postmortem blameless</text>
  </g>

  <rect x="192" y="246" width="496" height="42" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="440" y="264" text-anchor="middle" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="#7a5c00">Série do p99 de escrita do ledger: 42 → 58 ms em 5 meses — anotada, SEM AÇÃO</text>
  <text x="440" y="281" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#7a5c00">dentro do SLO · não dispara alerta · esperando um leitor — Aula 8</text>

  <text x="440" y="316" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">cinza = já existia · verde = construído nesta aula · âmbar = sinal anotado, herdado pela Aula 8</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A régua de evolução da TechPix: a Aula 7 não processa nada novo — ela dá olhos ao sistema. E deixa, de propósito, um sinal sem leitor.</p>
</div>

Essa aula encerra a minha parte no curso. Em quatro aulas, a TechPix saiu de um monólito com fronteiras bem desenhadas para um sistema distribuído com contratos explícitos, um modelo de risco servindo no caminho crítico, entrega progressiva com rede de validação, e — a partir de hoje — olhos para se ver por inteiro. Foi uma honra ser o professor da fase em que o sistema foi para a rua. Na próxima aula, vocês voltam para as mãos de quem começou tudo isso — e ele vai fechar o círculo que abriu na Aula 1: *da fé para a evidência*. O sistema agora produz evidência de sobra; a série histórica do ledger está lá, subindo devagarinho, esperando. O que falta é o leitor. Até lá.

---

## Apêndice — Termos novos desta aula

| Termo | O que é |
|---|---|
| **Observabilidade** | Propriedade do sistema de permitir responder perguntas não previstas com os dados já coletados; cobre os *unknown unknowns*. Monitoramento cobre só as perguntas previstas. |
| **RED** | Rate, Errors, Duration — as três métricas essenciais por *serviço*. |
| **USE** | Utilization, Saturation, Errors — as três métricas essenciais por *recurso*. Saturação avisa antes da utilização machucar. |
| **Histograma (de latência)** | Contagem por baldes de duração; permite calcular qualquer percentil e agregar entre instâncias com honestidade matemática. Percentil não se agrega por média. |
| **Cardinalidade** | Número de séries temporais únicas geradas pelas combinações de etiquetas de uma métrica. Identificador de alta cardinalidade (ex.: `conta_id`) pertence a log/trace, nunca a métrica. |
| **Prometheus** | Padrão de fato para métricas: séries temporais, coleta por pull, histogramas nativos. |
| **Log estruturado** | Evento em formato de máquina (JSON), com campos nomeados e ID de correlação obrigatório; dado pessoal nunca entra (LGPD), mascaramento na biblioteca, verificado por fitness function. |
| **ID de correlação** | Identificador que nasce na borda e carimba todos os logs de uma requisição. No fluxo Pix, o próprio **EndToEndId** do BACEN. |
| **Sampling (amostragem)** | Reter só parte da telemetria: 100% de erros/lentos, fração do caminho feliz. Log operacional se amostra; registro contábil, jamais. |
| **OpenTelemetry** | Padrão aberto de instrumentação: gera e propaga traces, métricas e logs de forma neutra de fornecedor. |
| **Trace / Span** | Trace = a jornada completa de uma requisição; span = cada segmento nomeado dela, com duração e atributos, aninhados como uma pilha de chamadas distribuída. |
| **Propagação de contexto** | O cabeçalho (`traceparent`, W3C) que viaja em cada chamada e evento, ligando spans ao trace — a mesma carona do deadline propagation da Aula 4. |
| **Amostragem na cauda (tail-based)** | Decidir reter o trace *depois* de ver como a requisição terminou — permite "100% dos lentos e com erro". |
| **Exemplar** | Referência de trace anexada a um balde de histograma: o clique que leva da métrica agregada à jornada individual. |
| **Drift (de dados / de conceito)** | Deriva: a distribuição das entradas mudou / a relação entre entrada e resposta certa mudou. Modelo não quebra — apodrece; a métrica é o exame de sangue. |
| **Indicador antecedente** | Métrica que prevê degradação antes do ground truth chegar (ex.: estabilidade da distribuição de score, com rótulos do MED fechando o ciclo depois). |
| **SLI / SLO / SLA** | A medição / a meta interna / a promessa externa com consequência. SLO interno sempre mais apertado que SLA externo. |
| **Error budget** | O erro permitido pelo SLO tratado como moeda: sobrando, o time ousa; queimado, congela release. Transforma a guerra lançar×estabilizar em aritmética. |
| **Burn rate** | Velocidade de queima do error budget; base do único alerta que merece acordar alguém. Sintoma acorda gente; causa fica no dashboard. |
| **Runbook** | Diagnóstico passo a passo escrito de cabeça fria, antes do incidente, por severidade. |
| **Postmortem blameless** | O ADR do incidente: linha do tempo, fatores contribuintes (plural), ações com dono — sem culpados, porque punir quem conta a verdade mata a informação. |
| **MTTR / MTBF** | Tempo médio de recuperação / entre falhas. Sistemas maduros otimizam MTTR: queda curta, contida e ensinável. |
| **SEV1/2/3** | Severidades de incidente: dinheiro errado ou fluxo indisponível / degradação com cliente sofrendo / dano individual contido. |
| **Catálogo de SLOs** | O artefato desta aula: por fluxo/serviço, o SLI, o SLO, o budget e o dono — a fronteira entre engenharia e negócio escrita em números, revisada trimestralmente. |

---

[← Aula 6](aula6-conteudo-completo.md) · [Índice](index.md) · [Aula 8 →](aula8-conteudo-completo.md)
