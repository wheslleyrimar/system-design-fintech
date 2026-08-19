---
layout: default
title: "Aula 8 — Guia de perguntas difíceis"
---

# Aula 8 — Guia de perguntas difíceis
*Munição de embasamento para quando a plateia técnica empurrar. Esta é a aula que vai atrair mais ceticismo — e o ceticismo é saudável.*

---

## Sobre a premissa da aula

**"Isso é hype de IA vestido de arquitetura. Onde está a evidência de que agente propondo mudança de arquitetura funciona de verdade?"**

Recebam a pergunta bem, porque ela é justa. E a resposta honesta tem duas partes. Primeira: a parte **não** especulativa da aula é a maior parte dela — o Harness (flags, canary, guardrail, rollback automático) é prática de indústria consolidada há anos, independente de IA; a spec executável também. Segunda: a parte do agente é, sim, mais nova, e o desenho que eu apresentei é deliberadamente **conservador** por isso — leitura apenas, proposta apenas, revisão humana obrigatória, e nenhuma ferramenta capaz de causar dano irreversível. Se a IA não entregar o que promete, vocês perderam pouco: sobra um sistema com Harness rigoroso, spec executável e ADRs bem escritos, que é exatamente o que vocês deveriam ter de qualquer forma. **O investimento é assimétrico a favor de vocês** — e essa assimetria é a razão de eu ensinar assim.

**"Se o humano precisa revisar tudo, o agente economizou o quê? Ler o ADR e verificar a proposta dá o mesmo trabalho."**

Não dá, e a diferença é onde o esforço fica. O trabalho caro não é **avaliar** uma proposta bem formulada; é **descobrir que existe algo a investigar** e reunir o contexto — correlacionar meses de métrica, achar os ADRs relevantes, reconstruir por que a decisão original foi tomada. Isso é o que ninguém faz, porque ninguém tem tempo de olhar dashboard todos os dias procurando tendência lenta. O agente muda o custo de **originar** a investigação, não o de decidir. E vale dizer o contraponto honesto: se as propostas do agente forem ruins, ele **aumenta** o trabalho humano em vez de reduzir — e é justamente por isso que os evals do Bloco 6 existem, para medir isso em vez de supor.

## Sobre o rigor estatístico

**"Se eu preciso de centenas de milhares de transações no canary, e a 1% isso leva horas, o canary deixa de ser útil para deploy frequente. Como conciliar?"**

Conciliando com a distinção do Bloco 4, que é exatamente para isso. O canary não precisa provar que a mudança é **melhor** com significância estatística para ser liberado — ele precisa provar que ela não é **catastrófica**, e isso é muito mais rápido de verificar, porque os guardrails de segurança (invariante do ledger, erro 5xx, latência estourando o orçamento) são de detecção rápida ou de tolerância zero. A avaliação estatística rigorosa é para experimento de produto ("essa mudança melhora conversão?"), não para gate de deploy. Confundir os dois é o que produz tanto o canary teatral quanto o canary paralisante.

**"Nossa taxa de erro é muito menor que 0,1% — é 0,001%. Isso inviabiliza qualquer canary?"**

Inviabiliza usar **taxa de erro** como métrica de canary, sim — e essa é a conclusão correta a tirar. Com evento tão raro, vocês nunca terão amostra suficiente numa janela útil. A saída é a terceira do Bloco 4: escolher métricas de **alta frequência** como guardrail principal — distribuição de latência (um valor por requisição), taxa de resposta por código, profundidade de fila. E manter a taxa de erro como guardrail de **tolerância zero para categorias específicas**: um único erro de reconciliação do ledger dispara rollback, sem precisar de estatística. Métrica rara não serve para comparação; serve para alarme absoluto.

## Sobre o MCP e segurança

**"Você mencionou prompt injection. Mas se o agente só lê, qual é o dano real? Ele escrever um ADR bobo não machuca ninguém."**

Correto, e é exatamente esse o argumento — mas vale explorar dois cenários mais desconfortáveis que a plateia pode levantar. Primeiro: **exfiltração**. Se o agente lê dados de produção e depois escreve um ADR que alguém publica num repositório, uma injeção poderia tentar fazer o agente incluir dado sensível no texto do ADR. A defesa é a mesma da Seção 4.1 — não entregar dado bruto de usuário ao agente, só agregado — mais revisão humana do que é publicado. Segundo: **envenenamento do raciocínio a longo prazo**. Se o agente tem memória persistente, uma injeção poderia plantar uma "conclusão" falsa que influencia decisões futuras. A defesa é tratar memória de agente como dado não-confiável, com a mesma disciplina de qualquer entrada externa. Nenhum desses cenários move dinheiro — mas nenhum é inofensivo, e um arquiteto sênior está certo em levantá-los.

**"Quem audita o agente? Se ele propõe e um humano aprova, e depois dá problema, de quem é a responsabilidade?"**

Do humano que aprovou — e isso precisa ser dito com clareza, sem ambiguidade, porque ambiguidade de responsabilidade é o que faz processo de aprovação virar carimbo. O campo "Origem: proposto por agente / aprovado por humano" do ADR-003 existe justamente para deixar isso rastreável: quem aprovou, quando, com base em quais dados. Numa fintech, essa rastreabilidade não é boa prática — é o que permite responder ao regulador "por que essa mudança foi feita?". E o corolário cultural, que vale enunciar: se aprovar proposta de agente virar carimbo automático, vocês removeram a única defesa que não é técnica. O processo só funciona se a aprovação for real.

**"E se o agente tiver acesso de leitura a dados pessoais? Isso não é problema de LGPD?"**

É, e é uma razão adicional para a disciplina de agregação que eu recomendei. O princípio de minimização de dados da LGPD se aplica: se o propósito é analisar latência do ledger, o agente não precisa de nome, CPF ou descrição de transação — precisa de séries temporais agregadas. Desenhar o servidor MCP para expor **só o agregado** não é só defesa contra injeção; é conformidade por design. E, se em algum caso o dado individual for genuinamente necessário, aí entram as perguntas de sempre: qual a base legal, quem tem acesso, por quanto tempo, e isso está registrado.

## Sobre evals

**"LLM-as-judge me parece circular — usar um modelo para avaliar outro modelo. Por que isso funcionaria?"**

Você está certo em desconfiar, e é por isso que ele está no **último** lugar da hierarquia. Ele funciona razoavelmente para tarefas onde reconhecer qualidade é mais fácil que produzir qualidade — verificar se um texto seguiu um formato pedido, se uma resposta cita a fonte que deveria. Ele funciona mal quando a avaliação exige o mesmo raciocínio da tarefa original, porque aí o juiz herda os mesmos pontos cegos. E a regra que eu daria: se vocês não conseguiriam explicar a um auditor **por que** o juiz aprovou algo, o juiz não deveria ter poder de decisão. Triagem, sim; gate final sobre dinheiro, nunca.

**"Como eu monto um golden dataset para arquitetura? Não existe 'resposta certa' para uma decisão de design."**

Não existe resposta certa única, mas existem **respostas erradas identificáveis** — e é aí que o golden dataset funciona. O caso da TechPix é bom: dado o conjunto de métricas do dia 5, um agente que identifica "a contenção está no ledger" acertou; um que diz "precisamos de mais réplicas de leitura" errou de forma verificável, porque leitura não era o gargalo. O dataset não avalia se a solução proposta é ótima; avalia se o **diagnóstico** está certo. E diagnóstico é verificável a posteriori, porque vocês sabem o que realmente causou o incidente.

## Sobre o fecho do curso

**"Se a tese é 'IA só é segura com bons fundamentos', então essa aula é opcional para quem ainda não tem os fundamentos?"**

Não opcional — mas fora de ordem. Se um time não tem ledger auditável, idempotência, spec com invariantes e Harness, trazer agente para propor mudança de arquitetura é acelerar em direção ao muro. A recomendação honesta para esse time é: façam as Aulas 1 a 3 valerem primeiro. E a razão de eu ensinar a Aula 8 mesmo assim é que ela **explica por que os fundamentos importam** — muita gente investe em spec e Harness só quando entende que eles são o que torna possível a próxima coisa. A Aula 8 é o argumento de retorno sobre o investimento das outras três.
