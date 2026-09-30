---
layout: default
title: "Aula 9 — Roteiro (fonte)"
---

# Aula 9 — Segurança em Sistemas Financeiros
## Roteiro de condução (~120 min)

> **Duração-alvo:** 2h.
> **Aula autocontida:** todo conceito é definido no ponto em que aparece; não depende das Aulas 1–8 (só pressupõe a TechPix: Pix sobre ledger, em serviços).
> **Companions:** `aula9-conteudo-completo.md` (texto integral, 19 diagramas) · `aula9-perguntas-dificeis.md`.
> **Os três momentos que não podem ser cortados:** o incidente do Bruno (Bloco 1), a diferença entre *identidade* e *autorização* (Blocos 3–4) e o **golpe autorizado** que nenhum controle de permissão pega (Bloco 8).
> **Fio condutor:** "Autenticação estabelece identidade. Autorização limita poder." Cada bloco responde a uma versão dessa frase.

## Visão de relance

| Bloco | Tempo | Título | Diagrama (no quadro / Excalidraw) |
|---|---|---|---|
| 1 | 0–10 | Cold open: o Bruno e o `contaOrigemId` | Requisição antes/depois |
| 2 | 10–25 | Modelagem de ameaças: ativos, adversários, fronteiras, STRIDE | Zonas de confiança |
| 3 | 25–42 | Identidade: JWT por dentro, OAuth × OIDC, PKCE, MFA, step-up | Anatomia do JWT; fluxo PKCE |
| 4 | 42–58 | **Autorização: BOLA, RBAC/ABAC/ReBAC, Gateway × domínio** | Fluxo com PEP/PDP; espectro |
| 5 | 58–75 | Segurança leste-oeste: workload identity, mTLS, mesh, policy | mTLS handshake; sidecar |
| 6 | 75–88 | Dados e segredos: envelope encryption, crypto-shredding, HMAC | KEK/DEK; cadeia LGPD × ledger |
| 7 | 88–96 | Cadeia de suprimentos + segredos dinâmicos (relâmpago) | Ciclo de vida do segredo |
| 8 | 96–104 | **Antifraude: o ataque que não viola permissão** | Pipeline de decisão |
| 9 | 104–110 | Insiders + auditoria imutável | Maker-checker; cadeia de hashes |
| 10 | 110–120 | Detecção, fitness functions, trade-offs, ADR-004 | Camadas + tabela de custos |

---

## Bloco 1 · [0–10] · Cold open: o Bruno e o `contaOrigemId`

- **Conte a cena em voz alta**, sem slide: o Bruno copia a requisição, troca **uma string**, recebe `200 OK` com R$ 4.800 saindo da conta de um estranho.
- **Frase-âncora:** "O token era válido. Cada componente fez exatamente o que foi projetado para fazer. E o dinheiro saiu."
- **Pergunte:** "Onde está o bug?" Deixe 2 minutos. Respostas típicas: "no Gateway", "no JWT". Ambas erradas — o bug é a **pergunta que ninguém fez**.
- **Desenhe:** a requisição com `sub` no token e `contaOrigemId` no body, com uma seta vermelha entre os dois — "ninguém cruzou".
- **Fale a tese:** "Segurança não é ter JWT. É garantir que cada identidade execute só as operações permitidas, sobre os recursos permitidos — e conseguir provar."
- **Armadilha:** não entregue ainda o nome BOLA. Deixe a plateia chegar em "autenticado ≠ autorizado" sozinha.

---

## Bloco 2 · [10–25] · Modelagem de ameaças

- **Ordem:** ativos (dinheiro, ledger, dados, chaves) → adversários (a tabela de 7 perfis) → fronteiras de confiança → STRIDE.
- **Desenhe o Diagrama de zonas** (Internet / Edge / Cluster / Externo regulado). Marque **norte-sul** e **leste-oeste**.
- **Fala-chave:** "O erro clássico é abrir o catálogo de ferramentas. O ofício começa com: o que protejo, de quem, por onde ele entra?"
- **Destaque dois adversários:** o **golpista de engenharia social** (nenhum controle de identidade o vê — spoiler do Bloco 8) e o **insider** (já tem a chave — spoiler do Bloco 9).
- **STRIDE:** aplique só ao fluxo do Pix; mostre que o bug do Bruno ocupa **duas células** (Tampering → Elevation of privilege).
- **Defina Zero Trust** em uma frase e desmonte o "castelo com fosso".
- **Pergunte:** "Se um pod do cluster for comprometido, o que ele consegue alcançar hoje?" (deixe a pergunta pendurada até o Bloco 5).

---

## Bloco 3 · [25–42] · Identidade

- **Abra um JWT no quadro.** Header/payload/signature. Para cada claim, dê **a armadilha**: `iss` (aceitar só o esperado), `aud` (token confusion), `sub` (**o ponto do incidente**), `exp` (vida curta), `acr` (força do login).
- **Desenhe:** "o que a assinatura garante × o que NÃO garante" — o body viaja ao lado, fora da assinatura.
- **JWT é stateless → difícil de revogar.** Apresente o trade-off e a saída: access curto + refresh revogável + introspecção só para alto valor.
- **OAuth × OIDC pela régua das perguntas:** OAuth = "o que o portador pode fazer"; OIDC = "quem é o usuário". **Escopo é granular em tipo de operação, não em instância de recurso.**
- **PKCE:** desenhe a sequência de 9 passos; o momento "aha" é o passo ⑤ (interceptar o code é inútil sem o verifier).
- **MFA de verdade:** SMS é segundo fator fraco (SIM swap). **Device binding** = chave no enclave; a biometria destrava a chave.
- **Step-up + assinatura da transação (WYSIWYS).** Mostre que a assinatura **também barraria o Bruno**, por caminho independente → defesa em profundidade.
- **Armadilha:** não deixe a turma sair achando que "OAuth resolve autorização". Ele resolve delegação.

---

## Bloco 4 · [42–58] · Autorização (o coração da aula)

- **Agora sim, o nome:** BOLA/IDOR. "Não é ataque sofisticado; é uma requisição legítima com um valor diferente." Por isso scanners genéricos não acham.
- **Desenhe o antes/depois** com **PEP/PDP**. Cinco passos: token → sujeito **do token** → recurso → ownership com dado **do servidor** → só então a regra.
- **Mostre o código** (`@PreAuthorize` + `ContaPolicy`). Frase: "o que o cliente não envia, o cliente não pode adulterar" — derive a conta do `sub` quando possível.
- **403 × 404:** decisão consciente (enumeração).
- **Espectro RBAC → ownership → ReBAC → ABAC.** Pergunta: "`CLIENTE pode transferir`… de qual conta?" A TechPix combina os três, cada um onde cabe. **Aviso:** política complexa demais vira o próprio risco.
- **Gateway × domínio:** "O Gateway sabe que a `acc-2207` pertence ao `cli-8420`?" Não — e não deve. Tabela edge/domínio/plataforma.
- **Pergunta-chave:** "O JWT validado no Gateway torna o `accountId` do body confiável?" **Não, nunca.**
- **Teste adversarial:** projete as três asserções (403, efeito zero, rastro). "Um 403 que ainda debitou é o pior dos mundos."
- **Pergunte:** "Como provamos que a vulnerabilidade não volta?" (resposta no Bloco 10).

---

## Bloco 5 · [58–75] · Segurança leste-oeste

- **Retome a pergunta pendurada do Bloco 2.** "Quando o Antifraude recebe 'sou o Pagamentos', como sabe?" — "porque veio de dentro da rede" = castelo com fosso. Defina **movimento lateral**.
- **Identidade de usuário ≠ de workload.** Dois erros: `backend-admin` global; reaproveitar token do usuário (**confused deputy**).
- **Dois padrões:** Client Credentials (serviço age em nome próprio, escopo `risco:avaliar`) e Token Exchange (`sub` + `act`). Nos dois: estreito, curto, com audiência.
- **mTLS:** desenhe TLS comum (só o cliente verifica) e depois os dois sentidos. CA interna, certificado de horas, SPIFFE. Mostre o **pod invasor recusado no handshake**.
- **Pergunta obrigatória:** "mTLS resolve autorização?" **Não** — prova *quem*, não *o quê*.
- **A dor da repetição:** 30 serviços × 3 linguagens × rotação de certificado. → **Service mesh** (data plane + control plane).
- **Seja honesto sobre o custo do mesh:** +ms por salto, complexidade; alternativas (ambient, network policies, mTLS por biblioteca). Regra: **primeiro sinta a dor da repetição, depois compre a plataforma.**
- **AuthorizationPolicy** em YAML; **default deny**; menor privilégio: "O Antifraude precisa escrever no Ledger?" Raio de explosão.
- **Policy de plataforma ≠ regra de negócio.** Kafka: ACL por tópico — "quem publica num tópico forja verdade para os consumidores".

---

## Bloco 6 · [75–88] · Dados e segredos

- **Três estados do dado** (trânsito, repouso, uso). O terceiro é o que mais vaza: "nunca logue o que não mostraria num telão."
- **Por que cifrar disco não basta:** o banco em execução vê o claro. Criptografia de campo. **"Criptografia move o problema para a chave."**
- **Desenhe o envelope encryption** (KEK/DEK). Consequências: rotação barata, revogação por política, uso da KEK auditado.
- **Tokenização × criptografia:** "a melhor proteção para um dado é não tê-lo"; redução de escopo (PCI).
- **O conflito LGPD × ledger imutável** — o momento de maior valor do bloco. Desenhe o antes/depois do **crypto-shredding**. Duas ressalvas: quem decide o *quando* é o jurídico; e a separação contábil/pessoal tem que estar no modelo **desde o dia 1**.
- **Webhook com HMAC:** os quatro passos de validação. Explique **replay** ("a mensagem é autêntica; só o contexto a denuncia") e **timing attack**. HMAC × assinatura assimétrica = **não-repúdio**.
- **Rate limit** por identidade, não só por IP.

---

## Bloco 7 · [88–96] · Cadeia de suprimentos e segredos (relâmpago)

- **Incidente:** segredo no `application.yml`. Pergunta: "qual o raio de explosão e em quanto tempo o segredo pode ser tornado inútil?"
- **Ciclo de vida** (emitir → entregar → usar → rotacionar → revogar) e o que produz vazamento.
- **Segredo dinâmico** com identidade de workload: "ninguém conhece a senha; ela nasce e morre com o pod."
- **Cadeia de suprimentos em 4 linhas:** SBOM, assinatura de imagem, versões travadas, imagem mínima. **Fecho:** "você não impede todo comprometimento; desenha para que custe pouco" (*assume breach*).
- **Se faltar tempo,** corte a cadeia de suprimentos para 2 minutos e mantenha o ciclo do segredo.

---

## Bloco 8 · [96–104] · Antifraude: o ataque que não viola permissão

- **Retome a Ana:** autenticada com MFA, dona da conta, dentro do limite, assinatura impecável — pagando a um golpista. "Todos os controles dizem sim e o dinheiro está sendo roubado."
- **Troque a pergunta:** de "pode?" para "isso parece certo?".
- **Sinais** (dispositivo, comportamento, velocidade, relacionamento, grafo, contexto). **Pipeline:** enriquecimento → motor (regras + modelo) → ALLOW / STEP-UP / DENY em ~100 ms.
- **Regras × modelo:** explicabilidade, *concept drift*. **Fail-open × fail-closed graduado por valor.**
- **Trade-off central:** falso positivo (confiança) × falso negativo (dinheiro irreversível). O limiar é decisão de **negócio**.
- **O antifraude também é alvo:** *structuring*. **Limites** como disjuntor de prejuízo (noturno, conta nova).
- **Fala-âncora:** "A segurança financeira não termina no bloquear. Termina no recuperar o que der."

---

## Bloco 9 · [104–110] · Insiders e auditoria

- **O adversário já tem a chave.** Quatro controles: maker-checker, JIT, segregação de funções, break-glass. Reenquadre: "não é desconfiança da pessoa; é proteção da pessoa."
- **Log ≠ trilha de auditoria:** tabela comparativa. Os sete campos. **Negativas são eventos de primeira classe.**
- **Cadeia de hashes + âncora WORM:** "sem âncora externa, quem controla o sistema recalcula a cadeia e ninguém vê." Segregação também vale aqui: quem opera não administra a trilha.
- **Pergunte:** "Como provamos que o `cli-5519` tentou a `acc-2207`?"

---

## Bloco 10 · [110–120] · Detecção, fitness functions, trade-offs, ADR

- **Assumir o comprometimento:** MTTD/MTTR; regras de SIEM que **consomem os sinais das negativas** — "controle que só bloqueia é meio controle; o que bloqueia e alerta é sensor."
- **Runbook de 5 passos.** "A velocidade da contenção é decidida meses antes."
- **Regulatório, sem cravar prazos:** política de segurança cibernética (CMN/BACEN) e LGPD/ANPD — "consultem a versão vigente e o jurídico; a arquitetura garante a capacidade."
- **Fitness functions:** mostre 3–4 linhas da tabela. Fechamento do incidente: **todo incidente real vira uma linha na tabela.**
- **Trade-offs:** projete a tabela de custos. Dois princípios: **proporcionalidade** e **falhar de forma previsível**.
- **ADR-004** em 2 minutos. **Feche com as cinco frases** e o gancho: "cada camada é rápida; somadas, são centenas de ms — e quem enxerga onde o tempo foi?"

---

## Se o tempo apertar (ordem de corte)

1. Cadeia de suprimentos (Bloco 7) → 2 min.
2. Tokenização e PCI → 1 frase.
3. ReBAC → citar sem detalhar.
4. ADR-004 → só as decisões 1–3 e a "Revisão".

**Nunca cortar:** Blocos 1, 4 e 8.

## Checklist de quadro

- [ ] Requisição: `sub` no token × `contaOrigemId` no body.
- [ ] 4 zonas de confiança + eixos norte-sul/leste-oeste.
- [ ] Fluxo BOLA com PEP/PDP.
- [ ] Handshake mTLS + pod invasor recusado.
- [ ] KEK/DEK e crypto-shredding.
- [ ] Pipeline do antifraude com 3 saídas.
- [ ] Cadeia de hashes com âncora externa.
- [ ] Pilha "um Pix, dez perguntas".
