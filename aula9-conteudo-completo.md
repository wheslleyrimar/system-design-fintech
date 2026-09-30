---
layout: default
title: "Aula 9 — Segurança em Sistemas Financeiros"
---

# Aula 9 — Segurança em Sistemas Financeiros
*Curso de Arquitetura de Sistemas Financeiros com IA*

> **Navegação:** [Índice](index.md) · [Aula 1](aula1-conteudo-completo.md) · [Aula 2](aula2-conteudo-completo.md) · [Aula 3](aula3-conteudo-completo.md) · [Aula 4](aula4-conteudo-completo.md) · [Aula 5](aula5-conteudo-completo.md) · [Aula 6](aula6-conteudo-completo.md) · [Aula 7](aula7-conteudo-completo.md) · [Aula 8](aula8-conteudo-completo.md) · **Aula 9 (você está aqui)**

> **Esta aula é autocontida.** Todo conceito que ela usa é definido aqui, no ponto em que aparece. Quem chegou sem ter visto as anteriores só precisa saber uma coisa: a **TechPix** é uma fintech fictícia que processa Pix — pagamentos instantâneos brasileiros, liquidados em segundos, **irreversíveis por natureza** — sobre um ledger (o livro-razão que registra cada centavo), organizada em serviços: *Pagamentos*, *Antifraude e Limites*, *Contas e Ledger*, *Identidade e Onboarding*.

Deixa eu começar com a coisa mais desconfortável que existe para quem constrói sistema financeiro: **o atacante não precisa quebrar nada.**

Terça-feira, 14h22. O Bruno, um cliente da TechPix, abre o app, faz login — senha, biometria, tudo certo — e manda um Pix de R$ 50 para a irmã. O app envia uma requisição para a API:

```http
POST /pix
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json

{ "contaOrigemId": "acc-8841", "chaveDestino": "irma@email.com", "valor": 50.00 }
```

`acc-8841` é a conta do Bruno. Funciona. Agora o Bruno — que trabalha com tecnologia e ficou curioso — abre o inspetor de rede do navegador do app web, copia a requisição, troca uma única string e reenvia:

```http
{ "contaOrigemId": "acc-2207", "chaveDestino": "bruno.laranja@email.com", "valor": 4800.00 }
```

`acc-2207` é a conta de **outra pessoa**. A resposta:

```http
HTTP/1.1 200 OK
{ "e2eId": "E1234567820260930142201abc...", "status": "LIQUIDADO" }
```

R$ 4.800 saíram da conta de um desconhecido, atravessaram o SPI em 2 segundos e não voltam mais — Pix não se desfaz com um *ctrl+Z*. E agora a parte que deve tirar o sono de vocês: **o token era válido.** Assinatura válida, não expirado, emitido pelo provedor de identidade correto, para a audiência correta. O Gateway conferiu tudo isso e deixou passar. Cada componente do caminho fez exatamente o que foi projetado para fazer. O sistema estava "seguro" por todos os checklists de autenticação que existem — e mesmo assim entregou dinheiro de A para B por ordem de um terceiro.

Guardem essa cena, porque ela é a tese da aula inteira, e eu vou enunciá-la já:

> **Segurança não é ter JWT. Segurança é garantir que cada identidade execute apenas as operações permitidas, sobre os recursos permitidos — e conseguir provar isso depois.**

Em sistema comum, um bug de segurança vaza dados. Em sistema financeiro, **vaza dinheiro — e dinheiro que sai por Pix não volta por conta própria**. Isso muda a economia da segurança: o custo de uma falha é imediato, monetário, irreversível e regulado. E muda também quem é o adversário: aqui existe gente cuja profissão é procurar exatamente a string que o Bruno trocou. Nas próximas duas horas a gente vai construir, camada por camada, a defesa da TechPix — e, mais importante, entender *por que cada camada existe*, o que ela **não** protege, e quanto ela custa.

**Mapa da aula:**

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 250" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9m-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <rect x="20" y="20" width="160" height="70" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="100" y="48" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#991b1b">1. Ameaças</text>
  <text x="100" y="68" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">quem ataca, o quê</text>
  <rect x="200" y="20" width="160" height="70" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="280" y="48" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">2. Identidade</text>
  <text x="280" y="68" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">AuthN · MFA · JWT</text>
  <rect x="380" y="20" width="160" height="70" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="460" y="48" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">3. Autorização</text>
  <text x="460" y="68" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">BOLA · RBAC/ABAC</text>
  <rect x="560" y="20" width="160" height="70" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="640" y="48" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">4. Workloads</text>
  <text x="640" y="68" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">mTLS · mesh · policy</text>
  <rect x="740" y="20" width="140" height="70" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="810" y="48" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">5. Dados</text>
  <text x="810" y="68" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">KMS · HSM · LGPD</text>
  <rect x="20" y="150" width="160" height="70" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="100" y="178" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">6. Segredos + APIs</text>
  <text x="100" y="198" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">HMAC · anti-replay</text>
  <rect x="200" y="150" width="160" height="70" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="280" y="178" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">7. Antifraude</text>
  <text x="280" y="198" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">sinais · decisão</text>
  <rect x="380" y="150" width="160" height="70" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="460" y="178" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">8. Insider</text>
  <text x="460" y="198" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">quatro olhos · JIT</text>
  <rect x="560" y="150" width="160" height="70" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="640" y="178" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">9. Auditoria</text>
  <text x="640" y="198" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">imutável · provável</text>
  <rect x="740" y="150" width="140" height="70" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="810" y="178" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">10. Resposta</text>
  <text x="810" y="198" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">incidente · testes</text>
  <line x1="180" y1="55" x2="198" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a9m-arrow)"/>
  <line x1="360" y1="55" x2="378" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a9m-arrow)"/>
  <line x1="540" y1="55" x2="558" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a9m-arrow)"/>
  <line x1="720" y1="55" x2="738" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a9m-arrow)"/>
  <line x1="810" y1="90" x2="810" y2="120" stroke="#888" stroke-width="1.5"/>
  <line x1="810" y1="120" x2="100" y2="120" stroke="#888" stroke-width="1.5"/>
  <line x1="100" y1="120" x2="100" y2="148" stroke="#888" stroke-width="1.5" marker-end="url(#a9m-arrow)"/>
  <line x1="180" y1="185" x2="198" y2="185" stroke="#4338ca" stroke-width="2" marker-end="url(#a9m-arrow)"/>
  <line x1="360" y1="185" x2="378" y2="185" stroke="#4338ca" stroke-width="2" marker-end="url(#a9m-arrow)"/>
  <line x1="540" y1="185" x2="558" y2="185" stroke="#4338ca" stroke-width="2" marker-end="url(#a9m-arrow)"/>
  <line x1="720" y1="185" x2="738" y2="185" stroke="#4338ca" stroke-width="2" marker-end="url(#a9m-arrow)"/>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Dez camadas, uma tese: nenhuma delas basta sozinha — segurança é defesa em profundidade, com cada camada assumindo que a anterior pode ter falhado.</p>
</div>

---

## 1. Antes de defender: modelar a ameaça

O erro clássico de quem começa em segurança é abrir o catálogo de tecnologias — OAuth, mTLS, WAF, criptografia — e ir "aplicando". Isso produz sistema com muita tecnologia e buracos exatamente onde ninguém olhou. O ofício sério começa com uma pergunta de arquitetura, não de ferramenta: **o que estamos protegendo, de quem, e por onde esse alguém consegue entrar?** Esse exercício se chama **modelagem de ameaças** (*threat modeling*), e é a fundação da aula.

### 1.1 O que a TechPix protege (os ativos)

Em ordem decrescente do que faz uma diretoria perder o sono:

1. **O dinheiro dos clientes** — o saldo no ledger e a capacidade de movimentá-lo. Ativo nº 1: quem controla uma ordem de pagamento controla dinheiro.
2. **A integridade do ledger** — se um registro pode ser alterado sem rastro, nada mais é confiável. Um ledger adulterado não vaza dinheiro: ele *apaga a verdade*.
3. **Dados pessoais e financeiros** — CPF, chaves Pix, extratos, padrões de gasto. Protegidos pela LGPD; valiosos no mercado clandestino.
4. **Credenciais e chaves** — a chave que assina mensagens para o SPI, as credenciais do banco de dados. Comprometer uma dessas é comprometer *tudo que ela protege* de uma vez.
5. **A disponibilidade e a confiança** — o sistema fora do ar viola metas regulatórias; o sistema fraudado perde a licença de operar na confiança do cliente e do regulador.

### 1.2 Quem ataca (os adversários)

Não existe "o hacker". Existem perfis com **capacidades e motivações diferentes**, e cada um exige uma defesa diferente. Vale nomeá-los, porque o Bruno lá do início é só o primeiro:

| Adversário | Como entra | O que quer | Defesa principal |
|---|---|---|---|
| **Cliente malicioso** (o Bruno) | Conta legítima; manipula requisições | Dinheiro de outras contas, burlar limites | Autorização por recurso, limites, antifraude |
| **Fraudador externo** | Phishing, credenciais vazadas, *SIM swap* | Assumir a conta de uma vítima (*account takeover*) | MFA, device binding, análise comportamental |
| **Golpista de engenharia social** | Convence a *própria vítima* a pagar | Dinheiro autorizado sob coação/engano | Fricção inteligente, limites noturnos, alertas |
| **Conta laranja (mula)** | Conta real, aberta para receber e dispersar | Lavar o produto da fraude | Análise de grafo, monitoramento do destino |
| **Insider** (funcionário, terceirizado) | Acesso legítimo, usado além da necessidade | Dinheiro, dados, sabotagem | Menor privilégio, quatro olhos, auditoria |
| **Atacante da cadeia de suprimentos** | Dependência ou imagem de container comprometida | Executar código dentro do perímetro | SBOM, assinatura de artefatos, isolamento |
| **Workload comprometido** | Vulnerabilidade em um serviço | Movimento lateral para outros serviços | Identidade de workload, mTLS, policies |

Reparem em duas linhas que **não** se resolvem com criptografia nem com token. O **golpista de engenharia social** é o caso mais perverso: a vítima está autenticada, a operação está autorizada, o token é impecável — e o dinheiro sai errado. Nenhum controle "clássico" de identidade detecta isso; quem detecta é o antifraude (§7). E o **insider** já *tem* credencial legítima — o modelo de ameaça dele é o oposto do de um invasor externo, e é por isso que ele ganha uma seção própria (§8).

### 1.3 Fronteiras de confiança: onde a desconfiança precisa acontecer

Uma **fronteira de confiança** (*trust boundary*) é uma linha no diagrama onde mudam o nível de confiança e quem controla o dado. A regra de ouro do modelo de ameaças: **tudo que cruza uma fronteira de confiança é entrada não confiável até ser validada do lado de dentro.** Não porque o outro lado seja "mau", mas porque *você não controla o que ele envia*.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9t-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a9t-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <!-- Zona 0: Internet -->
  <rect x="10" y="10" width="170" height="380" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="95" y="34" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#991b1b">ZONA 0 · Internet (hostil)</text>
  <rect x="30" y="60" width="130" height="50" rx="6" fill="#fff" stroke="#991b1b"/>
  <text x="95" y="90" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">App / Web do cliente</text>
  <rect x="30" y="130" width="130" height="50" rx="6" fill="#fff" stroke="#991b1b"/>
  <text x="95" y="160" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Atacante externo</text>
  <rect x="30" y="200" width="130" height="50" rx="6" fill="#fff" stroke="#991b1b"/>
  <text x="95" y="230" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Parceiro (webhook)</text>
  <!-- Zona 1: Edge -->
  <rect x="200" y="10" width="150" height="380" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="275" y="34" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">ZONA 1 · Edge (DMZ)</text>
  <rect x="220" y="60" width="110" height="50" rx="6" fill="#fff" stroke="#d4a017"/>
  <text x="275" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">WAF / DDoS</text>
  <text x="275" y="98" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">rate limit</text>
  <rect x="220" y="130" width="110" height="60" rx="6" fill="#fff" stroke="#d4a017"/>
  <text x="275" y="155" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">API Gateway</text>
  <text x="275" y="172" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">valida JWT (AuthN)</text>
  <!-- Zona 2: Cluster -->
  <rect x="370" y="10" width="330" height="380" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="535" y="34" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">ZONA 2 · Cluster (workloads)</text>
  <rect x="390" y="60" width="130" height="60" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="455" y="88" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Pagamentos</text>
  <text x="455" y="105" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">AuthZ do domínio</text>
  <rect x="550" y="60" width="130" height="60" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="615" y="88" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Antifraude</text>
  <text x="615" y="105" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">e Limites</text>
  <rect x="390" y="160" width="130" height="60" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="455" y="188" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Contas e Ledger</text>
  <rect x="550" y="160" width="130" height="60" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="615" y="188" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Identidade</text>
  <text x="615" y="205" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">(OIDC / MFA)</text>
  <rect x="390" y="260" width="130" height="50" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="455" y="290" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Kafka</text>
  <rect x="550" y="260" width="130" height="50" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="615" y="290" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Bancos (PostgreSQL)</text>
  <text x="535" y="345" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3730a3">tráfego leste-oeste: workload ↔ workload</text>
  <!-- Zona 3: Externo regulado -->
  <rect x="720" y="10" width="170" height="380" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="805" y="34" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">ZONA 3 · Externo regulado</text>
  <rect x="740" y="80" width="130" height="50" rx="6" fill="#fff" stroke="#166534"/>
  <text x="805" y="110" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">DICT / SPI (BACEN)</text>
  <rect x="740" y="160" width="130" height="50" rx="6" fill="#fff" stroke="#166534"/>
  <text x="805" y="190" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">KMS / HSM</text>
  <rect x="740" y="240" width="130" height="50" rx="6" fill="#fff" stroke="#166534"/>
  <text x="805" y="270" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Provedores / SaaS</text>
  <!-- Fluxos -->
  <line x1="160" y1="85" x2="218" y2="85" stroke="#4338ca" stroke-width="2" marker-end="url(#a9t-arrow)"/>
  <line x1="160" y1="155" x2="218" y2="155" stroke="#b91c1c" stroke-width="2" marker-end="url(#a9t-red)"/>
  <line x1="275" y1="110" x2="275" y2="128" stroke="#4338ca" stroke-width="2" marker-end="url(#a9t-arrow)"/>
  <line x1="330" y1="160" x2="388" y2="100" stroke="#4338ca" stroke-width="2" marker-end="url(#a9t-arrow)"/>
  <line x1="520" y1="90" x2="548" y2="90" stroke="#4338ca" stroke-width="2" marker-end="url(#a9t-arrow)"/>
  <line x1="455" y1="120" x2="455" y2="158" stroke="#4338ca" stroke-width="2" marker-end="url(#a9t-arrow)"/>
  <line x1="680" y1="105" x2="738" y2="105" stroke="#4338ca" stroke-width="2" marker-end="url(#a9t-arrow)"/>
  <line x1="680" y1="185" x2="738" y2="185" stroke="#4338ca" stroke-width="2" marker-end="url(#a9t-arrow)"/>
  <line x1="160" y1="225" x2="218" y2="165" stroke="#b91c1c" stroke-width="2" marker-end="url(#a9t-red)"/>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Modelo de fronteiras da TechPix. Cada linha tracejada é um lugar onde a confiança muda — e onde a validação precisa acontecer. As setas vermelhas são tráfego que a TechPix não controla.</p>
</div>

Duas observações sobre esse mapa, porque elas organizam o resto da aula. Primeira: existem **dois eixos de tráfego** com problemas de segurança diferentes. O tráfego **norte-sul** (de fora para dentro: cliente → Gateway → serviço) exige *autenticar e autorizar pessoas*. O tráfego **leste-oeste** (dentro do cluster: Pagamentos → Antifraude → Ledger) exige *autenticar e autorizar máquinas* — e é aí que muita empresa é surpreendida, porque tratou o interior da rede como território amigo. Segunda: a Zona 3 mostra que a TechPix também **depende** de partes que não controla (o BACEN, o provedor de chaves): elas são fronteiras de confiança no sentido inverso — a gente precisa provar quem *somos* para elas, e desconfiar do que elas devolvem.

Essa desconfiança do interior tem nome: **Zero Trust**. A premissa antiga era "perímetro forte, interior confiável" — o castelo com fosso. O problema do castelo é que, uma vez que alguém cruza o fosso (com uma credencial roubada, uma dependência infectada, um workload comprometido), ele circula livre. A premissa Zero Trust inverte: **"nunca confie, sempre verifique"** — nenhum chamador é confiável só por estar dentro da rede; toda requisição, em toda fronteira, carrega uma identidade verificada e passa por uma decisão explícita de autorização. Mais à frente veremos que isso não é um produto que se compra: é um conjunto de decisões de design, e cada uma tem custo.

### 1.4 STRIDE: um roteiro para não esquecer categorias de ameaça

Para não depender da criatividade de quem está na sala, existe um mnemônico clássico. **STRIDE** lista seis categorias de ameaça, cada uma violando uma propriedade de segurança. Aplicado a um único fluxo — "cliente envia um Pix" —, ele vira uma checklist de perguntas incômodas:

| Ameaça | Propriedade violada | No fluxo do Pix da TechPix | Controle que responde |
|---|---|---|---|
| **S**poofing (falsificar identidade) | Autenticidade | Alguém se passa por cliente (token roubado) ou por *Pagamentos* (workload falso) | MFA + device binding; identidade de workload + mTLS |
| **T**ampering (adulterar) | Integridade | Trocar `valor` ou `contaOrigemId` em trânsito ou no body; alterar registro no ledger | TLS; assinatura da transação; autorização por recurso; ledger append-only |
| **R**epudiation (negar autoria) | Não-repúdio | "Eu não fiz esse Pix" — e ninguém consegue provar o contrário | Trilha de auditoria imutável; assinatura de transação |
| **I**nformation disclosure (vazar) | Confidencialidade | CPF no log; extrato de outro cliente (BOLA de leitura); backup sem criptografia | Criptografia; mascaramento; autorização por recurso |
| **D**enial of service (indisponibilizar) | Disponibilidade | Inundar `/pix` para estourar a capacidade e derrubar o SLA regulatório | Rate limiting; WAF; limites por identidade; isolamento (bulkhead) |
| **E**levation of privilege (escalar) | Autorização | Cliente age como operador; workload de leitura escreve no ledger | Menor privilégio; policies; separação de funções |

O valor do STRIDE não é a sigla: é que ele **força a olhar cada aresta do diagrama seis vezes**, com seis lentes. E o incidente do Bruno cai na linha do meio: é *Tampering* do body (ele adulterou um campo) que vira *Elevation of privilege* (agiu com poder que não tinha) — duas células da tabela para um único bug. Nenhum controle isolado o cobriria; por isso o desenho é em camadas.

---

## 2. Quem é você? Identidade, autenticação e o que um token realmente diz

Vamos separar duas perguntas que o incidente do Bruno mostrou serem completamente diferentes — e que quase todo bug de segurança de API confunde:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 860 200" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9a-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <rect x="20" y="30" width="380" height="140" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="210" y="60" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#3730a3">AUTENTICAÇÃO (AuthN)</text>
  <text x="210" y="88" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">"Quem é você?"</text>
  <text x="210" y="112" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#555">senha · biometria · token · certificado</text>
  <text x="210" y="138" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">Bruno provou ser o Bruno ✔</text>
  <rect x="460" y="30" width="380" height="140" rx="10" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="650" y="60" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#991b1b">AUTORIZAÇÃO (AuthZ)</text>
  <text x="650" y="88" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#333">"Pode fazer ESTA ação sobre ESTE recurso?"</text>
  <text x="650" y="112" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#555">ownership · política · contexto</text>
  <text x="650" y="138" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">Bruno pode mexer em acc-2207? ✘ (ninguém perguntou)</text>
  <line x1="402" y1="100" x2="458" y2="100" stroke="#4338ca" stroke-width="2" marker-end="url(#a9a-arrow)"/>
  <text x="430" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">≠</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A pergunta que o sistema do Bruno respondeu (esquerda) não é a pergunta que o Bruno violou (direita). Autenticação forte não corrige autorização ausente.</p>
</div>

Autenticação estabelece **identidade**. Autorização limita **poder**. Uma sem a outra é ou inútil (sei quem é, deixo fazer tudo) ou impossível (sei o que pode, mas não sei quem está pedindo). E existe uma terceira, esquecida: a **prestação de contas** (*accountability*) — conseguir provar depois quem fez o quê. As três juntas são o que os profissionais chamam de **AAA**.

### 2.1 Um token por dentro: o que o JWT afirma — e o que ele não pode afirmar

O token que o Bruno carregava era um **JWT** (*JSON Web Token*): um envelope em três partes, separadas por ponto, cada uma codificada em Base64URL. Vale abrir o envelope, porque a maior parte da confusão de segurança nasce de achar que ele diz mais do que diz.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9j-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <rect x="20" y="20" width="250" height="150" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="145" y="44" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">HEADER</text>
  <text x="35" y="70" font-family="monospace" font-size="12" fill="#333">{ "alg": "RS256",</text>
  <text x="35" y="90" font-family="monospace" font-size="12" fill="#333">  "typ": "JWT",</text>
  <text x="35" y="110" font-family="monospace" font-size="12" fill="#333">  "kid": "chave-2026-09" }</text>
  <text x="145" y="145" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">como foi assinado; qual chave</text>
  <rect x="290" y="20" width="330" height="150" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="455" y="44" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">PAYLOAD (claims)</text>
  <text x="305" y="68" font-family="monospace" font-size="12" fill="#333">"iss": "https://id.techpix.com"</text>
  <text x="305" y="86" font-family="monospace" font-size="12" fill="#333">"sub": "cli-5519"      ← quem</text>
  <text x="305" y="104" font-family="monospace" font-size="12" fill="#333">"aud": "api.techpix.com"</text>
  <text x="305" y="122" font-family="monospace" font-size="12" fill="#333">"exp": 1790000000     ← validade</text>
  <text x="305" y="140" font-family="monospace" font-size="12" fill="#333">"scope": "pix:create"</text>
  <text x="305" y="158" font-family="monospace" font-size="12" fill="#333">"acr": "mfa"          ← força do login</text>
  <rect x="640" y="20" width="240" height="150" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="760" y="44" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">SIGNATURE</text>
  <text x="655" y="72" font-family="monospace" font-size="11" fill="#333">RSA-SHA256(</text>
  <text x="655" y="90" font-family="monospace" font-size="11" fill="#333">  base64(header) + "." +</text>
  <text x="655" y="108" font-family="monospace" font-size="11" fill="#333">  base64(payload),</text>
  <text x="655" y="126" font-family="monospace" font-size="11" fill="#333">  chavePrivadaDoEmissor)</text>
  <text x="760" y="153" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">prova: ninguém alterou 1 e 2</text>
  <rect x="20" y="200" width="860" height="110" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="450" y="226" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">O que a assinatura GARANTE</text>
  <text x="450" y="248" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#166534">✔ o emissor (iss) escreveu estes claims  ·  ✔ nada foi alterado desde então  ·  ✔ ainda não expirou</text>
  <text x="450" y="272" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#991b1b">O que ela NÃO GARANTE</text>
  <text x="450" y="294" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">✘ que o "contaOrigemId" do BODY pertence ao "sub"  ·  ✘ que o token não foi roubado  ·  ✘ que a operação é sensata</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A assinatura protege as três partes do token — não o corpo da requisição que viaja ao lado dele. O body é input controlado pelo cliente, sempre.</p>
</div>

Percorram os campos (*claims*), porque cada um tem uma armadilha própria:

- **`iss` (issuer)** — quem emitiu. O validador precisa checar que é *o emissor que ele espera*, não qualquer emissor com assinatura válida.
- **`aud` (audience)** — para quem o token foi emitido. Um token feito para `api.techpix.com` **não deve** ser aceito por um serviço interno que é outra audiência; sem essa checagem, um token de baixo poder, roubado num lugar, é usado noutro (*token confusion*).
- **`sub` (subject)** — o sujeito: aqui, `cli-5519`, o Bruno. **Este é o ponto exato de que o incidente dependia.** O `sub` diz quem chamou; o `contaOrigemId` no body diz *sobre quem* a chamada quer agir. Ninguém cruzou os dois.
- **`exp`** — validade. Token de vida curta limita o estrago de um roubo; por isso access tokens duram minutos, não dias.
- **`scope` / `acr`** — o que o token permite fazer (escopos) e com que **força** o usuário se autenticou (`acr`: *authentication context class* — login por senha só, ou senha + biometria?). O segundo será decisivo no *step-up* (§2.4).

E uma propriedade que precisa ficar gravada: **um JWT é *stateless* — o validador confere a assinatura sem consultar ninguém.** Isso é o que o torna barato e escalável (nenhuma ida ao banco por requisição); é também o que o torna **difícil de revogar**: um token válido continua válido até o `exp`, mesmo que o cliente tenha bloqueado o cartão, trocado a senha ou sido banido um minuto atrás. É um *trade-off* clássico — escala versus revogação — e a saída de engenharia é a combinação: **access token curto (5–15 min)** + **refresh token revogável** guardado do lado do servidor de identidade + **lista de revogação / introspecção** para operações de alto valor. Note o custo: cada checagem online reintroduz uma dependência de rede que o JWT queria evitar. Onde pagar esse preço é decisão de arquitetura, não de biblioteca.

### 2.2 OAuth 2.0 e OIDC: dois protocolos, duas perguntas

Toda documentação mistura os dois, então vamos separá-los com a régua das perguntas:

- **OAuth 2.0** resolve **delegação de acesso**: *"como eu deixo o aplicativo X agir em meu nome sobre a API Y, sem entregar minha senha a X?"* Ele emite **access tokens** (autorização para chamar APIs). Não diz quem é o usuário — diz *o que o portador do token pode fazer*.
- **OIDC (OpenID Connect)** é uma camada em cima do OAuth que resolve **identidade**: *"quem é o usuário que acabou de se autenticar?"* Ele emite o **ID token** (um JWT que afirma "este é o cli-5519, autenticado agora, com este nível de força").

A confusão perigosa é tomar um pelo outro: usar ID token para chamar API, ou usar access token para afirmar identidade. E a confusão mais perigosa de todas é achar que **qualquer um dos dois resolve autorização de domínio**. O OAuth entrega *escopos* — `pix:create` — que são granulares em *tipo de operação*, não em *instância de recurso*. Um escopo diz "pode criar Pix"; **não** diz "pode criar Pix a partir da conta acc-8841 e não da acc-2207". Essa pergunta — a única que importava no incidente — nunca esteve no protocolo. Ela pertence ao domínio, e é a §3.

**O fluxo que aplicativos móveis e web devem usar hoje** é o *Authorization Code com PKCE*. Vale entender o porquê de cada passo, porque é um dos desenhos mais elegantes da área:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9p-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <rect x="30" y="15" width="150" height="40" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="105" y="40" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">App (cliente)</text>
  <rect x="375" y="15" width="150" height="40" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="450" y="40" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">Servidor de Identidade</text>
  <rect x="720" y="15" width="150" height="40" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="795" y="40" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">API (Pix)</text>
  <line x1="105" y1="55" x2="105" y2="385" stroke="#bbb" stroke-dasharray="4 3"/>
  <line x1="450" y1="55" x2="450" y2="385" stroke="#bbb" stroke-dasharray="4 3"/>
  <line x1="795" y1="55" x2="795" y2="385" stroke="#bbb" stroke-dasharray="4 3"/>
  <text x="115" y="80" font-family="sans-serif" font-size="11" fill="#555">① gera segredo aleatório (code_verifier)</text>
  <text x="115" y="94" font-family="sans-serif" font-size="11" fill="#555">   e seu hash (code_challenge)</text>
  <line x1="105" y1="112" x2="448" y2="112" stroke="#4338ca" stroke-width="2" marker-end="url(#a9p-arrow)"/>
  <text x="277" y="106" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">② /authorize + code_challenge</text>
  <text x="460" y="140" font-family="sans-serif" font-size="11" fill="#555">③ usuário se autentica (senha + MFA)</text>
  <line x1="448" y1="162" x2="107" y2="162" stroke="#4338ca" stroke-width="2" marker-end="url(#a9p-arrow)"/>
  <text x="277" y="156" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">④ authorization code (curto, uso único)</text>
  <line x1="105" y1="204" x2="448" y2="204" stroke="#4338ca" stroke-width="2" marker-end="url(#a9p-arrow)"/>
  <text x="277" y="198" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">⑤ /token: code + code_verifier</text>
  <text x="460" y="232" font-family="sans-serif" font-size="11" fill="#555">⑥ confere: hash(verifier) == challenge?</text>
  <line x1="448" y1="254" x2="107" y2="254" stroke="#4338ca" stroke-width="2" marker-end="url(#a9p-arrow)"/>
  <text x="277" y="248" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">⑦ access token (curto) + refresh token + ID token</text>
  <line x1="105" y1="306" x2="793" y2="306" stroke="#4338ca" stroke-width="2" marker-end="url(#a9p-arrow)"/>
  <text x="450" y="300" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">⑧ POST /pix  Authorization: Bearer &lt;access token&gt;</text>
  <text x="640" y="340" font-family="sans-serif" font-size="11" fill="#555">⑨ API valida assinatura, iss, aud, exp</text>
  <text x="640" y="358" font-family="sans-serif" font-size="11" fill="#b91c1c">   …e AGORA a pergunta que faltou: pode agir neste recurso?</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Authorization Code + PKCE. O segredo nasce no cliente e nunca viaja antes da troca — interceptar o "code" no passo ④ é inútil sem o verifier do passo ⑤.</p>
</div>

**Por que PKCE existe:** num app móvel, o *authorization code* do passo ④ volta por um redirecionamento (esquema de URL) que outro app instalado no aparelho pode interceptar. Sem proteção, o atacante trocaria o code por token. Com PKCE, o app gera um segredo aleatório (o *verifier*) e envia só o **hash** dele no passo ②. O servidor guarda o hash; no passo ⑤ o app apresenta o verifier original, e o servidor confere. Quem interceptou o code no ④ **não tem o verifier**, porque ele nunca viajou. É prova de posse construída com uma função de hash — sem nenhum segredo pré-compartilhado, algo que app público (que não consegue guardar segredo) não teria de outro jeito.

### 2.3 O que autenticação forte realmente significa em dinheiro

Autenticar "com senha" em sistema financeiro é confessar antecipadamente que você aceita *account takeover*. Senha vaza, é reutilizada, é fisgada por phishing. A resposta é combinar **fatores independentes** — algo que você sabe (senha/PIN), algo que você tem (o aparelho, uma chave criptográfica) e algo que você é (biometria). **MFA** só ajuda se os fatores forem realmente independentes: um SMS, por exemplo, é um segundo fator fraco, porque o *SIM swap* (o golpista convence a operadora a transferir seu número) o derrota sem tocar no aparelho.

O padrão que hoje resolve melhor o problema é o **device binding**: no cadastro do aparelho, o app gera um par de chaves criptográficas dentro do enclave seguro do hardware (a chave privada **nunca sai**), e registra a chave pública no servidor. Dali em diante, "este aparelho" deixa de ser uma afirmação vaga e vira uma **prova criptográfica**: o servidor envia um desafio, o aparelho o assina com a chave privada, e a biometria local só *destrava o uso da chave*. O roubo da senha, sozinho, deixa de bastar — o atacante precisaria do aparelho *e* da biometria.

### 2.4 Step-up e a assinatura da transação: autenticar a *operação*, não só a sessão

Aqui aparece uma ideia que separa segurança financeira de segurança de aplicação comum. Estar autenticado na sessão às 14h não prova que **a pessoa quis** aquela transferência de R$ 4.800 às 14h22 — a sessão pode ter sido sequestrada, o app pode ter malware que muda o destino na tela. Por isso, operações de risco pedem **autenticação em nível de operação**:

- **Step-up authentication:** o sistema exige um fator adicional *no momento* da operação sensível. O claim `acr` do token (§2.1) diz com que força o usuário logou; a API, ao receber um Pix acima de R$ 1.000 ou para destinatário novo, **exige `acr` mais alto** — e, se o token só carrega `acr=senha`, responde "faça step-up" em vez de executar.
- **Assinatura da transação (*transaction signing*):** o aparelho assina criptograficamente **os detalhes da operação** — destino, valor, conta de origem — com a chave ligada ao device. O servidor verifica a assinatura sobre *exatamente esses campos*. Se um malware trocar o destino no caminho, a assinatura não confere. O princípio tem nome: **WYSIWYS** (*what you see is what you sign*) — o usuário confirma, numa tela confiável, os mesmos dados que serão assinados.

Percebam o efeito colateral elegante disso: uma assinatura sobre `{contaOrigemId, chaveDestino, valor, nonce}` **também teria barrado o Bruno**, mas por outro caminho — ele não consegue produzir uma assinatura válida da chave do dono da `acc-2207`. É uma segunda defesa independente contra o mesmo ataque, e ilustra o princípio da aula: *defesa em profundidade* significa que **cada camada pega uma variante do ataque que a outra deixaria passar**. Também é o que fornece **não-repúdio** (o R do STRIDE): "eu não fiz esse Pix" passa a ser refutável com a assinatura, que só aquele aparelho poderia ter gerado.

---

## 3. Autorização: o bug do Bruno tem nome e cura

### 3.1 BOLA/IDOR: a vulnerabilidade nº 1 de APIs

O incidente da abertura é o exemplar de livro-texto de uma classe de falha chamada **BOLA** (*Broken Object Level Authorization*) — também conhecida, em versões mais antigas do jargão, como **IDOR** (*Insecure Direct Object Reference*). A descrição cabe numa frase: **o usuário autenticado troca o identificador de um objeto na requisição (`contaOrigemId`, `/contas/2207/extrato`, `/pix/E123...`) e o servidor entrega ou executa sem checar se aquele objeto pertence a ele.** Ela lidera há anos a lista de riscos de segurança de APIs justamente por ser fácil de cometer: todo endpoint que recebe um ID é candidato, e o desenvolvedor, com o token validado, tem a falsa sensação de que "a segurança já foi feita".

Note que BOLA **não é um ataque sofisticado**. Não usa criptografia quebrada, nem injeção, nem exploit. É uma requisição legítima com um valor diferente. Por isso ferramenta de varredura genérica raramente acha: só quem entende *o que cada objeto significa no domínio* sabe que aquele valor está errado. Corolário incômodo: **BOLA não se resolve com infraestrutura; resolve-se com código de domínio e com teste.**

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 340" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9b-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a9b-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
    <marker id="a9b-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <text x="225" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#991b1b">ANTES: valida o token, confia no body</text>
  <text x="675" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">DEPOIS: valida o token E o recurso</text>
  <rect x="20" y="50" width="90" height="46" rx="6" fill="#fff" stroke="#333"/>
  <text x="65" y="70" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Bruno</text>
  <text x="65" y="85" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">sub=cli-5519</text>
  <rect x="150" y="50" width="100" height="46" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="200" y="70" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Gateway</text>
  <text x="200" y="85" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">token ✔</text>
  <rect x="290" y="50" width="110" height="46" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="345" y="70" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Pagamentos</text>
  <text x="345" y="85" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">lê body, executa</text>
  <rect x="290" y="180" width="110" height="46" rx="6" fill="#fff" stroke="#b91c1c" stroke-width="2"/>
  <text x="345" y="200" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Ledger</text>
  <text x="345" y="215" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#b91c1c">debita acc-2207 ✘</text>
  <line x1="110" y1="73" x2="148" y2="73" stroke="#b91c1c" stroke-width="2" marker-end="url(#a9b-red)"/>
  <line x1="250" y1="73" x2="288" y2="73" stroke="#b91c1c" stroke-width="2" marker-end="url(#a9b-red)"/>
  <line x1="345" y1="96" x2="345" y2="178" stroke="#b91c1c" stroke-width="2" marker-end="url(#a9b-red)"/>
  <text x="225" y="270" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">200 OK — dinheiro de terceiro sai</text>
  <rect x="470" y="50" width="90" height="46" rx="6" fill="#fff" stroke="#333"/>
  <text x="515" y="70" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Bruno</text>
  <text x="515" y="85" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">sub=cli-5519</text>
  <rect x="600" y="50" width="90" height="46" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="645" y="70" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Gateway</text>
  <text x="645" y="85" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#166534">token ✔</text>
  <rect x="730" y="50" width="150" height="46" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="805" y="70" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Pagamentos</text>
  <text x="805" y="85" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">PEP: consulta a política</text>
  <rect x="730" y="150" width="150" height="46" rx="6" fill="#fff" stroke="#166534" stroke-width="2"/>
  <text x="805" y="170" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Policy (PDP)</text>
  <text x="805" y="185" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">dono(acc-2207) == cli-5519?</text>
  <rect x="730" y="235" width="150" height="46" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="805" y="255" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">403 Forbidden</text>
  <text x="805" y="270" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">+ evento de auditoria</text>
  <line x1="560" y1="73" x2="598" y2="73" stroke="#4338ca" stroke-width="2" marker-end="url(#a9b-arrow)"/>
  <line x1="690" y1="73" x2="728" y2="73" stroke="#4338ca" stroke-width="2" marker-end="url(#a9b-arrow)"/>
  <line x1="805" y1="96" x2="805" y2="148" stroke="#4338ca" stroke-width="2" marker-end="url(#a9b-arrow)"/>
  <line x1="805" y1="196" x2="805" y2="233" stroke="#166534" stroke-width="2" marker-end="url(#a9b-green)"/>
  <text x="470" y="330" font-family="sans-serif" font-size="11" fill="#666">PEP = Policy Enforcement Point (quem aplica) · PDP = Policy Decision Point (quem decide)</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">A cura é uma pergunta a mais, no lugar certo: o serviço dono do recurso compara o sujeito do token com o dono do objeto — e nega, com registro, quando não bate.</p>
</div>

### 3.2 A cura: cinco passos, na ordem certa

A **autorização por recurso** (*resource-level authorization*) é um procedimento, e a ordem importa:

1. **Validar o token** — assinatura, `iss`, `aud`, `exp`. (Isso o sistema já fazia.)
2. **Extrair o sujeito do *token*** — nunca do body. `sub` é a única fonte confiável de "quem".
3. **Identificar o recurso alvo** — o `contaOrigemId` que o cliente *afirma*.
4. **Verificar ownership/política** — "o sujeito tem direito de executar *esta ação* sobre *este recurso*?", decidido a partir de **dados que o servidor controla** (a tabela que liga conta ao titular), não de dados que o cliente enviou.
5. **Só então executar a regra de negócio** — e registrar a decisão.

Em Java com Spring Security, o passo 4 costuma virar uma anotação no método — o ponto é que a decisão seja **declarativa, testável e impossível de esquecer** dentro do caso de uso:

```java
// Ruim: confia no body. O token foi validado no filtro, e é tudo.
public Pagamento criar(CriarPixRequest req) {
    return ledger.debitar(req.contaOrigemId(), req.valor());
}

// Bom: o "dono" vem do token; a conta vem do banco; a comparação é do servidor.
@PreAuthorize("@contaPolicy.podeMovimentar(authentication, #req.contaOrigemId())")
public Pagamento criar(CriarPixRequest req) {
    return ledger.debitar(req.contaOrigemId(), req.valor());
}

@Component
class ContaPolicy {
    boolean podeMovimentar(Authentication auth, String contaId) {
        String titular = contas.titularDe(contaId);          // dado do servidor
        return titular != null && titular.equals(auth.getName()); // sub do token
    }
}
```

Um refinamento importante de desenho: **a melhor defesa contra BOLA é não aceitar o ID do cliente quando ele não é necessário.** Se o cliente só tem uma conta, a API pode nem pedir `contaOrigemId` — deriva a conta do `sub`. O que o cliente não envia, o cliente não pode adulterar. Onde o ID é inevitável (cliente com várias contas), aplica-se a checagem do passo 4 sem exceção. E uma dica de resposta: retornar **403** (proibido) ou **404** (não encontrado) para recurso alheio é decisão consciente — 404 evita que o atacante *enumere* quais IDs existem; 403 é mais honesto para o cliente legítimo confuso. Escolham e sejam consistentes.

### 3.3 RBAC não resolve tudo: um espectro de modelos de autorização

A primeira reação de muita equipe é "vamos criar um papel `CLIENTE` que pode transferir". Isso é **RBAC** (*Role-Based Access Control*): permissões atreladas a **papéis**, papéis atrelados a usuários. É simples, auditável, ótimo para perguntas do tipo "operadores de suporte podem ver extrato". Mas repare no que o RBAC **não expressa**: `CLIENTE pode transferir` — *de qual conta?* O papel é o mesmo para o Bruno e para o dono da `acc-2207`; a diferença entre os dois é **a relação com o objeto**, e papel não modela relação.

Existe um espectro de modelos, e a escolha certa é *o mais simples que exprime a regra*, não o mais poderoso:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 290" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9r-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <line x1="40" y1="30" x2="860" y2="30" stroke="#4338ca" stroke-width="2" marker-end="url(#a9r-arrow)"/>
  <text x="40" y="20" font-family="sans-serif" font-size="11" fill="#666">mais simples · barato · menos expressivo</text>
  <text x="860" y="20" text-anchor="end" font-family="sans-serif" font-size="11" fill="#666">mais expressivo · caro · mais difícil de auditar</text>
  <rect x="20" y="55" width="200" height="215" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="120" y="80" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">RBAC</text>
  <text x="120" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">papel → permissão</text>
  <text x="32" y="130" font-family="sans-serif" font-size="11" fill="#333">Ex.: SUPORTE lê extrato.</text>
  <text x="32" y="152" font-family="sans-serif" font-size="11" fill="#333">Bom: acesso de equipes,</text>
  <text x="32" y="168" font-family="sans-serif" font-size="11" fill="#333">back-office.</text>
  <text x="32" y="198" font-family="sans-serif" font-size="11" fill="#b91c1c">Falha: "de qual conta?"</text>
  <text x="32" y="216" font-family="sans-serif" font-size="11" fill="#b91c1c">Explosão de papéis.</text>
  <rect x="245" y="55" width="200" height="215" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="345" y="80" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#3730a3">Ownership</text>
  <text x="345" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">dono(recurso) == sujeito</text>
  <text x="257" y="130" font-family="sans-serif" font-size="11" fill="#333">Ex.: só o titular movimenta</text>
  <text x="257" y="146" font-family="sans-serif" font-size="11" fill="#333">a própria conta.</text>
  <text x="257" y="176" font-family="sans-serif" font-size="11" fill="#333">Resolve o BOLA clássico</text>
  <text x="257" y="192" font-family="sans-serif" font-size="11" fill="#333">com uma comparação.</text>
  <text x="257" y="222" font-family="sans-serif" font-size="11" fill="#b91c1c">Falha: conta conjunta,</text>
  <text x="257" y="238" font-family="sans-serif" font-size="11" fill="#b91c1c">procurador, empresa.</text>
  <rect x="470" y="55" width="200" height="215" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="570" y="80" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#7a5c00">ReBAC</text>
  <text x="570" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">grafo de relações</text>
  <text x="482" y="130" font-family="sans-serif" font-size="11" fill="#333">Ex.: "Ana é PROCURADORA</text>
  <text x="482" y="146" font-family="sans-serif" font-size="11" fill="#333">da empresa E, dona da</text>
  <text x="482" y="162" font-family="sans-serif" font-size="11" fill="#333">conta C".</text>
  <text x="482" y="192" font-family="sans-serif" font-size="11" fill="#333">Modela conta conjunta,</text>
  <text x="482" y="208" font-family="sans-serif" font-size="11" fill="#333">delegação, hierarquia.</text>
  <text x="482" y="238" font-family="sans-serif" font-size="11" fill="#b91c1c">Custo: infra de grafo.</text>
  <rect x="695" y="55" width="185" height="215" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="787" y="80" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#991b1b">ABAC</text>
  <text x="787" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">atributos + contexto</text>
  <text x="707" y="130" font-family="sans-serif" font-size="11" fill="#333">Ex.: Pix &gt; R$ 1.000 só</text>
  <text x="707" y="146" font-family="sans-serif" font-size="11" fill="#333">com acr=mfa, de device</text>
  <text x="707" y="162" font-family="sans-serif" font-size="11" fill="#333">conhecido, das 6h às 20h.</text>
  <text x="707" y="192" font-family="sans-serif" font-size="11" fill="#333">Regra depende de valor,</text>
  <text x="707" y="208" font-family="sans-serif" font-size="11" fill="#333">hora, risco, dispositivo.</text>
  <text x="707" y="238" font-family="sans-serif" font-size="11" fill="#b91c1c">Custo: política complexa.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Não é uma escada a subir: os modelos se combinam. A TechPix usa RBAC para pessoas internas, ownership como base do Pix, e ABAC para os limites contextuais.</p>
</div>

A TechPix combina três, cada um onde faz sentido: **RBAC** para o back-office (papéis de suporte, risco, conciliação); **ownership/ReBAC** como piso de todo endpoint que recebe ID de conta (a relação titular–conta, incluindo conta conjunta e procurador); e **ABAC** para as regras contextuais — "Pix acima de R$ 1.000 exige `acr=mfa`", "limite noturno de R$ 1.000 entre 20h e 6h", "destinatário novo pede confirmação". Um aviso de engenharia: **política complexa demais vira o próprio risco** — regra que ninguém entende não é auditada, e regra não auditada não protege. Comecem com o ownership; adicionem contexto só onde a regra de negócio realmente pede.

### 3.4 Onde autorizar: o Gateway não conhece o negócio

Uma tentação arquitetural recorrente: "o Gateway já valida o JWT; por que não centralizar *toda* a autorização nele?" A resposta é uma pergunta: **o Gateway sabe que a `acc-2207` pertence ao `cli-8420`?** Não sabe — e não *deve* saber. Ownership é dado de domínio, vive no serviço de Contas, muda com regras de negócio (conta conjunta, procuração, encerramento). Levar esse conhecimento para o Gateway o transforma num monólito de regras — o mesmo acoplamento que a decomposição em serviços tentou evitar.

A divisão saudável de responsabilidades:

| Camada | Autoriza o quê | Não deve tentar |
|---|---|---|
| **Edge (WAF + Gateway)** | Token válido, `aud` correta, escopo grosso (`pix:create`), rate limit, tamanho de payload, formato | Ownership, regras de valor/limite, qualquer coisa que exija dado de domínio |
| **Serviço de domínio (Pagamentos)** | Ownership do recurso, limites, step-up por valor, estado do objeto (a conta está ativa?) | Reautenticar do zero — confia no que o edge verificou, *mas nunca no body* |
| **Plataforma (mesh/policy)** | Quais *workloads* podem chamar quais (§4) | Decidir se *aquele usuário* pode *aquele objeto* |

E o corolário que responde à pergunta clássica — *"o JWT validado no Gateway torna o `accountId` do body confiável?"* — é: **não, nunca.** O edge autentica o portador; o serviço dono do dado autoriza a ação. Isso é **defesa em profundidade** na sua forma mais pura: o serviço de Pagamentos **não pode assumir** que o Gateway fez tudo certo (o Gateway pode ter bug, ser contornado por um workload interno comprometido, ou estar mal configurado numa rota nova). Cada camada valida o que lhe compete *como se a camada anterior pudesse ter falhado*.

### 3.5 Como provar que a vulnerabilidade não volta: testes adversariais

Segurança que só existe na cabeça de quem a implementou desaparece na próxima refatoração. A cura do BOLA precisa virar **teste automatizado que falha se alguém a remover**. O teste é curto e sempre da mesma forma — *o atacante é um usuário legítimo tentando o objeto do outro*:

```java
@Test
void usuarioAnaoPodeMovimentarContaDoBruno() {
    var tokenDeAna = tokens.para("cli-1001");           // token legítimo e válido
    var resposta = api.post("/pix", tokenDeAna,
        Map.of("contaOrigemId", "acc-2207",              // conta do Bruno
               "chaveDestino", "x@email.com", "valor", 10.00));

    assertThat(resposta.status()).isEqualTo(403);        // negado
    assertThat(ledger.saldo("acc-2207")).isEqualTo(saldoAntes);  // nada se moveu
    assertThat(auditoria.ultimo()).matches(negacaoDe("cli-1001", "acc-2207")); // rastro
}
```

Três asserções, três garantias: a resposta é negativa, **o efeito colateral não ocorreu** (o teste mais importante — um 403 que ainda assim debitou é o pior dos mundos), e **a tentativa foi registrada** (voltaremos em §9). Esse teste deve rodar em CI para **cada endpoint que recebe um identificador de objeto**; e aqui a arquitetura ajuda: se a autorização é uma anotação declarativa, é possível escrever um teste de arquitetura que *falha o build* quando um método público de controller recebe um `*Id` sem anotação de política. Isso é uma **fitness function de segurança**, e voltamos a ela em §10.3.

---

## 4. Quem é *esse* serviço? Segurança leste-oeste

Consertamos o usuário. Agora olhem para dentro do cluster. Pagamentos chama Antifraude; Pagamentos chama Ledger; um job de conciliação lê o banco; consumidores leem o Kafka. São **dezenas de instâncias de dezenas de workloads**, conversando pela rede interna, em pods que nascem e morrem o dia inteiro.

A pergunta: **quando uma requisição chega ao Antifraude dizendo "sou o Pagamentos", como o Antifraude sabe que é verdade?** Em muita empresa a resposta honesta é *"porque veio de dentro da rede"*. É a premissa do castelo com fosso — e basta **um** pod comprometido (uma dependência infectada, uma vulnerabilidade de execução remota) para o atacante herdar essa confiança e chamar *qualquer* serviço como se fosse legítimo. Chama-se **movimento lateral**, e é como um incidente pequeno vira um grande.

### 4.1 Identidade de usuário ≠ identidade de workload

Existem **dois tipos de sujeito** no sistema, e misturá-los é fonte de incidentes:

- **Usuário** (o Bruno): pessoa, autenticada por MFA, com vida útil de sessão, agindo *por vontade própria*.
- **Workload** (o serviço Pagamentos): software, sem MFA, sem "sessão", que **age em nome próprio** *ou* **em nome de um usuário** — e essa distinção é sutil e importante.

Dois erros clássicos aparecem aqui. O primeiro é a **credencial global "backend-admin"**: uma senha ou chave única que todos os serviços usam para falar entre si, com poder total. Quando ela vaza (e vaza), o atacante tem o cluster inteiro — e, pior, o log não distingue *qual* serviço fez o quê. O segundo é o **token pessoal reutilizado**: Pagamentos repassa o token do usuário para o Ledger "porque já está na mão". Isso parece prático e cria um problema chamado **confused deputy** (o *deputado confuso*): o Ledger recebe um token de usuário e não tem como saber se o Pagamentos está agindo *legitimamente* ou sendo *usado* por um atacante para ampliar acesso.

A solução são identidades separadas, com dois padrões para dois casos:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 330" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9w-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <text x="225" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#3730a3">A) O serviço age em nome PRÓPRIO</text>
  <text x="675" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#7a5c00">B) O serviço age em nome do USUÁRIO</text>
  <rect x="20" y="50" width="120" height="50" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="80" y="80" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Pagamentos</text>
  <rect x="180" y="50" width="120" height="50" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="240" y="70" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Servidor de</text>
  <text x="240" y="85" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Identidade</text>
  <rect x="330" y="50" width="120" height="50" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="390" y="80" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Antifraude</text>
  <line x1="140" y1="68" x2="178" y2="68" stroke="#4338ca" stroke-width="2" marker-end="url(#a9w-arrow)"/>
  <text x="160" y="62" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">①</text>
  <line x1="180" y1="86" x2="142" y2="86" stroke="#4338ca" stroke-width="2" marker-end="url(#a9w-arrow)"/>
  <text x="160" y="100" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#666">②</text>
  <path d="M80 100 L80 140 L390 140 L390 102" fill="none" stroke="#4338ca" stroke-width="2" marker-end="url(#a9w-arrow)"/>
  <text x="235" y="134" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">③ chama com o token do PRÓPRIO serviço</text>
  <text x="20" y="180" font-family="sans-serif" font-size="11" fill="#333">① Client Credentials: "sou pagamentos-svc" + credencial</text>
  <text x="20" y="198" font-family="sans-serif" font-size="11" fill="#333">② token M2M (máquina-a-máquina), escopo mínimo:</text>
  <text x="20" y="216" font-family="monospace" font-size="11" fill="#166534">   scope = "risco:avaliar"   (não "*")</text>
  <text x="20" y="248" font-family="sans-serif" font-size="11" fill="#333">Uso: chamada de sistema que independe do usuário</text>
  <text x="20" y="264" font-family="sans-serif" font-size="11" fill="#333">(o Antifraude avalia risco, seja quem for o cliente).</text>
  <rect x="470" y="50" width="100" height="50" rx="6" fill="#fff" stroke="#333"/>
  <text x="520" y="80" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Usuário</text>
  <rect x="610" y="50" width="120" height="50" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="670" y="80" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Pagamentos</text>
  <rect x="770" y="50" width="110" height="50" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="825" y="80" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Ledger</text>
  <line x1="570" y1="75" x2="608" y2="75" stroke="#4338ca" stroke-width="2" marker-end="url(#a9w-arrow)"/>
  <line x1="730" y1="75" x2="768" y2="75" stroke="#4338ca" stroke-width="2" marker-end="url(#a9w-arrow)"/>
  <text x="750" y="122" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">token com DUAS identidades:</text>
  <text x="750" y="137" text-anchor="middle" font-family="monospace" font-size="10" fill="#7a5c00">sub = cli-5519   act = pagamentos-svc</text>
  <text x="470" y="180" font-family="sans-serif" font-size="11" fill="#333">Token Exchange: Pagamentos troca o token do usuário</text>
  <text x="470" y="198" font-family="sans-serif" font-size="11" fill="#333">por um novo, de audiência = Ledger, que registra</text>
  <text x="470" y="216" font-family="sans-serif" font-size="11" fill="#333">TANTO quem é o usuário (sub) QUANTO quem age por ele (act).</text>
  <text x="470" y="248" font-family="sans-serif" font-size="11" fill="#333">Uso: a operação só existe por vontade do usuário.</text>
  <text x="470" y="264" font-family="sans-serif" font-size="11" fill="#333">O Ledger vê a cadeia e autoriza ambas as pontas.</text>
  <rect x="20" y="285" width="860" height="35" rx="6" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="450" y="308" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1a1a1a">Nos dois casos: o token é <tspan font-weight="bold">estreito</tspan> (escopo mínimo), <tspan font-weight="bold">curto</tspan> (minutos) e <tspan font-weight="bold">com audiência</tspan> (só vale para o destino).</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Dois padrões para dois casos. Nenhum deles é "reaproveitar o token do usuário" nem "usar a senha de admin do backend".</p>
</div>

O padrão **A**, o **Client Credentials**, dá ao *serviço* uma identidade própria e um token com **escopos mínimos** — `risco:avaliar`, não `pagamentos:*`. O padrão **B**, o **Token Exchange**, resolve o *confused deputy*: o token novo carrega **as duas** identidades (o usuário em `sub`, o serviço intermediário em `act`), e o Ledger autoriza *ambas as pontas* — "o usuário `cli-5519` pode debitar esta conta *e* o `pagamentos-svc` pode agir em nome de usuários". Se um pod comprometido tentar usar esse token para outra coisa, a audiência e o escopo não deixam.

### 4.2 Client Credentials é identidade — mas ainda não resolve "quem está no fio"

O Client Credentials entrega um *token*, mas o token é um segredo portátil — e todo segredo portátil pode ser roubado e usado por outro. A pergunta seguinte é natural: **o que impede uma máquina qualquer da rede de apresentar esse token, ou de simplesmente fingir ser o Antifraude ao receber a chamada?** Precisamos autenticar **o próprio canal** — provar, em cada conexão, que os dois pontas são quem dizem ser. É o papel do **mTLS**.

Para entendê-lo, comecem pelo TLS comum, que vocês usam todo dia no HTTPS. No **TLS** o *cliente* verifica o *servidor*: o servidor apresenta um certificado, assinado por uma autoridade em que o cliente confia, e o cliente confere "este é mesmo o `api.techpix.com`". O servidor **não** verifica o cliente — qualquer um pode conectar. No **mTLS** (*mutual* TLS) a verificação é **nos dois sentidos**: o cliente também apresenta um certificado, e o servidor só aceita a conexão se ele for válido e emitido pela autoridade da organização.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9k-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a9k-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <rect x="330" y="10" width="240" height="70" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="450" y="34" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">CA interna (PKI da TechPix)</text>
  <text x="450" y="52" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">emite certificados de curta duração</text>
  <text x="450" y="68" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">(horas), um por workload</text>
  <rect x="40" y="150" width="200" height="70" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="140" y="178" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Pagamentos</text>
  <text x="140" y="196" text-anchor="middle" font-family="monospace" font-size="10" fill="#333">cert: spiffe://techpix/pagamentos</text>
  <rect x="660" y="150" width="200" height="70" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="760" y="178" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">Antifraude</text>
  <text x="760" y="196" text-anchor="middle" font-family="monospace" font-size="10" fill="#333">cert: spiffe://techpix/antifraude</text>
  <line x1="380" y1="80" x2="180" y2="148" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#a9k-arrow)"/>
  <line x1="520" y1="80" x2="720" y2="148" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#a9k-arrow)"/>
  <text x="250" y="105" font-family="sans-serif" font-size="10" fill="#7a5c00">assina</text>
  <text x="640" y="105" font-family="sans-serif" font-size="10" fill="#7a5c00">assina</text>
  <line x1="240" y1="170" x2="658" y2="170" stroke="#4338ca" stroke-width="2" marker-end="url(#a9k-arrow)"/>
  <text x="450" y="164" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">① "olá" + meu certificado</text>
  <line x1="658" y1="192" x2="242" y2="192" stroke="#4338ca" stroke-width="2" marker-end="url(#a9k-arrow)"/>
  <text x="450" y="186" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">② meu certificado + prova de posse da chave</text>
  <text x="450" y="216" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">③ cada lado valida o outro contra a CA · negocia chaves de sessão</text>
  <rect x="240" y="235" width="420" height="34" rx="6" fill="#dcfce7" stroke="#166534" stroke-width="2"/>
  <text x="450" y="257" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">canal cifrado + AMBAS as identidades verificadas</text>
  <rect x="40" y="310" width="190" height="60" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="135" y="335" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#991b1b">Pod invasor</text>
  <text x="135" y="353" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">sem certificado emitido pela CA</text>
  <line x1="230" y1="340" x2="640" y2="205" stroke="#b91c1c" stroke-width="2" marker-end="url(#a9k-red)"/>
  <text x="450" y="322" font-family="sans-serif" font-size="12" font-weight="bold" fill="#991b1b">✘ handshake recusado</text>
  <text x="450" y="340" font-family="sans-serif" font-size="11" fill="#666">não chega nem a enviar uma requisição HTTP</text>
  <text x="450" y="390" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">Certificado de vida curta: se vazar, envelhece sozinho em horas — a rotação é parte do desenho, não um projeto anual.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">mTLS: uma CA interna emite a cada workload um certificado com identidade verificável. O handshake autentica os dois lados antes de trafegar qualquer byte de aplicação.</p>
</div>

O que o mTLS entrega, em três propriedades: **confidencialidade** (o tráfego interno vai cifrado — quem espiona a rede vê ruído), **integridade** (não dá para adulterar bytes no meio) e **autenticação mútua** (cada lado sabe *quem* é o outro, criptograficamente). A identidade que o certificado carrega costuma seguir um padrão aberto chamado **SPIFFE** (`spiffe://techpix/pagamentos`): um nome estável de workload, independente de IP — o que importa num cluster em que IPs mudam a cada reinício de pod.

E agora a pergunta que o roteiro dessa aula insiste em fazer, porque o erro de resposta é comum e caro: **"mTLS resolve autorização?"** **Não.** O mTLS prova *quem* está do outro lado; **não diz o que ele pode fazer.** Um Antifraude autenticado por mTLS pode ainda assim chamar `POST /pix` no serviço de Pagamentos e criar transferência — a menos que uma *política de autorização* diga que ele não pode. Autenticação de peer é o *pré-requisito* da autorização de peer; não a substitui. Mesma tese da aula, agora no eixo leste-oeste: **identidade estabelece quem; política limita o quê.**

### 4.3 O custo de repetir isso em todo serviço — e o service mesh

Considerem o que mTLS exige de **cada** serviço, em **cada** linguagem: obter certificado da CA, renová-lo antes de expirar sem derrubar conexões, validar a cadeia do peer, rejeitar cifras fracas, expor telemetria da conexão — e ainda os retries, timeouts e políticas de autorização. Multipliquem por 30 serviços em 3 linguagens. Cada time reimplementando, cada um com um bug diferente, cada renovação de certificado uma bomba-relógio de "esquecemos de rotacionar, e às 3h da manhã metade dos serviços parou de se falar". A pergunta que a plataforma precisa fazer é: **isso é lógica de negócio de cada serviço, ou é infraestrutura transversal que devia sair do código?**

A resposta arquitetural é o **service mesh**: mover essas preocupações para uma camada de plataforma, com duas partes.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 380" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9s-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a9s-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <rect x="250" y="10" width="400" height="80" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="450" y="36" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#7a5c00">CONTROL PLANE (ex.: Istio)</text>
  <text x="450" y="56" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">CA interna · distribui certificados e políticas</text>
  <text x="450" y="74" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">"quem pode falar com quem" declarado uma vez, em YAML versionado</text>
  <rect x="30" y="150" width="380" height="180" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="220" y="172" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Pod: Pagamentos</text>
  <rect x="50" y="190" width="140" height="60" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="120" y="218" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">app Pagamentos</text>
  <text x="120" y="236" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">só regra de negócio</text>
  <rect x="235" y="190" width="155" height="60" rx="6" fill="#dcfce7" stroke="#166534" stroke-width="2"/>
  <text x="312" y="212" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">proxy (sidecar)</text>
  <text x="312" y="228" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">mTLS · retry · métricas</text>
  <text x="312" y="242" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">policy · rotação de cert</text>
  <line x1="190" y1="220" x2="233" y2="220" stroke="#4338ca" stroke-width="2" marker-end="url(#a9s-arrow)"/>
  <text x="220" y="285" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">app fala HTTP simples com o proxy local (localhost)</text>
  <text x="220" y="305" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">o proxy é quem "fala mTLS" com o mundo</text>
  <rect x="490" y="150" width="380" height="180" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2" stroke-dasharray="7 4"/>
  <text x="680" y="172" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Pod: Antifraude</text>
  <rect x="510" y="190" width="155" height="60" rx="6" fill="#dcfce7" stroke="#166534" stroke-width="2"/>
  <text x="587" y="212" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">proxy (sidecar)</text>
  <text x="587" y="228" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">termina mTLS · aplica</text>
  <text x="587" y="242" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">AuthorizationPolicy</text>
  <rect x="710" y="190" width="140" height="60" rx="6" fill="#fff" stroke="#166534"/>
  <text x="780" y="218" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">app Antifraude</text>
  <line x1="665" y1="220" x2="708" y2="220" stroke="#4338ca" stroke-width="2" marker-end="url(#a9s-arrow)"/>
  <line x1="390" y1="215" x2="508" y2="215" stroke="#166534" stroke-width="3" marker-end="url(#a9s-green)"/>
  <text x="450" y="205" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="#166534">mTLS</text>
  <line x1="350" y1="90" x2="312" y2="188" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a9s-arrow)"/>
  <line x1="550" y1="90" x2="587" y2="188" stroke="#d4a017" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#a9s-arrow)"/>
  <rect x="30" y="345" width="840" height="28" rx="6" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="450" y="364" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1a1a1a">O código de negócio <tspan font-weight="bold">não reinventa PKI</tspan>: a plataforma entrega identidade e canal seguro "de graça" para cada workload.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Data plane (proxies ao lado de cada app) + control plane (cérebro que emite certificados e distribui políticas). O tráfego entre proxies é mTLS; a aplicação nem sabe.</p>
</div>

O **data plane** são os proxies (o *sidecar* — um contêiner que acompanha cada aplicação no mesmo pod) que interceptam todo tráfego de entrada e saída. O **control plane** é o cérebro central: opera a CA interna, entrega e **rotaciona** certificados automaticamente, e distribui as políticas. O ganho não é só segurança: os mesmos proxies dão **telemetria uniforme, retries e timeouts padronizados** — o motivo pelo qual o mesh costuma ser vendido como plataforma, não como "feature de segurança".

Mas eu preciso ser honesto sobre o preço, porque service mesh é uma das tecnologias mais super-vendidas da área. **Ele não é obrigatório, e muitas vezes é prematuro.** Cada pod ganha um proxy — mais memória, mais CPU, **alguns milissegundos por salto** (que num orçamento de latência apertado, como o do Pix, importa), e uma camada inteira de operação nova: atualizar o mesh é atualizar a infra de rede de tudo. Há alternativas com menos peso — *mesh sem sidecar* (modo ambient), políticas de rede do próprio Kubernetes, ou bibliotecas de mTLS em poucos serviços críticos. A regra de decisão honesta: **o mesh faz sentido quando o custo transversal (certificados, rotação, políticas, telemetria em N serviços) já dói mais do que o custo de operar a plataforma.** Com 4 serviços, provavelmente não; com 40, provavelmente sim. A ordem correta é *primeiro sentir a dor da repetição, depois comprar a plataforma* — e não o contrário.

### 4.4 Políticas de autorização entre workloads — e o mínimo privilégio

Com identidade de workload garantida pelo mTLS, a plataforma pode responder em **política declarativa** à pergunta que o mTLS sozinho não responde. Em Istio isso é uma `AuthorizationPolicy` — um documento YAML versionado no repositório, revisado como código, aplicado por GitOps:

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: antifraude-aceita-somente-pagamentos, namespace: techpix }
spec:
  selector: { matchLabels: { app: antifraude } }
  action: ALLOW
  rules:
  - from:
    - source: { principals: ["cluster.local/ns/techpix/sa/pagamentos"] }
    to:
    - operation: { methods: ["POST"], paths: ["/v1/avaliar"] }
```

Leiam em português: *"Antifraude só aceita chamadas vindas da identidade `pagamentos`, e apenas `POST /v1/avaliar`."* Todo o resto — o serviço de Notificações tentando chamar, o próprio Pagamentos tentando acessar outro endpoint — é **negado por padrão**. Essa é a postura **default deny**: o que não foi explicitamente permitido está proibido. Ela inverte a lógica frágil do "libera tudo, bloqueia o que a gente lembrar".

Isso é o **princípio do menor privilégio** aplicado a workloads, e a régua para revisar cada permissão é uma pergunta desconfortável: **"esse serviço realmente precisa disso?"** O Antifraude precisa *ler* contexto de risco; ele **precisa escrever no Ledger?** Quase certamente não — então sua identidade não tem essa permissão, e se um atacante o comprometer, o **raio de explosão** (*blast radius*: o estrago máximo de um comprometimento) fica limitado a *avaliar risco*, e não a movimentar dinheiro. Toda permissão que um workload tem e não usa é dívida de segurança.

Uma distinção que vale enfatizar, porque é onde times se confundem: a policy de plataforma diz **"o workload Pagamentos pode chamar `/v1/avaliar` do Antifraude"**. Ela **não** diz **"o usuário Bruno pode avaliar a conta 2207"**. As duas camadas respondem perguntas diferentes e **se complementam**: a regra de plataforma limita *quais máquinas* falam com quais; a regra de domínio limita *quais sujeitos* agem sobre *quais objetos*. Policy de mesh nunca substitui autorização de negócio — só a torna mais difícil de contornar.

O mesmo raciocínio vale para o **Kafka**, que é outra fronteira: produtores e consumidores têm identidade, e **ACLs por tópico** dizem *quem publica onde e quem lê o quê*. O Antifraude consome `pagamentos.iniciados`; não deveria poder publicar em `ledger.lancamentos` nem ler `identidade.documentos`. Um tópico é uma superfície de ataque: quem publica nele pode *forjar eventos que outros serviços tratam como verdade*.

---

## 5. Proteger o dado: criptografia, chaves e o conflito com a lei

Até aqui protegemos *quem acessa*. Mas todo controle de acesso tem um limite: se alguém contorna a aplicação e chega **direto ao disco, ao backup ou à réplica do banco**, a autorização de domínio nunca é consultada. A última linha de defesa é o **próprio dado**: se ele estiver ilegível para quem não deveria lê-lo, o vazamento do armazenamento deixa de ser vazamento de informação.

### 5.1 Três estados do dado, três defesas

| Estado | Onde o dado está | Risco | Defesa |
|---|---|---|---|
| **Em trânsito** | Na rede (cliente ↔ edge; serviço ↔ serviço) | Espionagem, adulteração | TLS 1.2+ (preferencialmente 1.3); mTLS interno |
| **Em repouso** | Disco, backup, snapshot, réplica | Vazamento do armazenamento; disco descartado | Criptografia de volume + criptografia de campo |
| **Em uso** | Memória do processo, logs, traces, dumps | Vazamento por observabilidade; memória extraída | Minimização, mascaramento, não logar o que é sensível |

O terceiro estado é o mais esquecido — e é o que mais vaza na prática. O CPF que aparece no log de erro, o cabeçalho `Authorization` inteiro num trace de depuração, o payload de pagamento indexado numa ferramenta de logs que 200 pessoas consultam: nenhum criptógrafo salva isso. A defesa é disciplina de engenharia — **nunca logue o que você não poderia mostrar num telão**: filtros de mascaramento na saída do log, listas de campos proibidos e, de novo, um teste que falha o build se um token ou documento aparecer numa saída de log (§10.3).

### 5.2 Criptografia em repouso: por que só criptografar o disco não basta

**Criptografia de volume** (o disco inteiro cifrado) protege contra um cenário específico: alguém roubar fisicamente o disco ou o snapshot. Mas o banco, quando está rodando, vê os dados em claro — e **qualquer pessoa ou aplicação com acesso ao banco** também vê. Para o CPF, o número da conta, o extrato, o padrão exige uma camada adicional: **criptografia de campo** (*field-level*), em que o dado sensível é cifrado *pela aplicação* antes de chegar ao banco. Agora o DBA que faz uma consulta, ou um atacante com dump do banco, vê `CPF: 8fA3x...` — ruído — e só o serviço autorizado, que tem acesso à chave, decifra.

E aí entra a pergunta que define a maturidade de um sistema criptográfico: **onde estão as chaves?** Porque criptografia move o problema de *proteger o dado* para *proteger a chave* — e uma chave guardada ao lado do dado (no mesmo servidor, no mesmo `application.yml`) é uma porta trancada com a chave pendurada na maçaneta.

### 5.3 KMS, HSM e envelope encryption

Duas peças de infraestrutura resolvem isso, e vale distinguir:

- **HSM** (*Hardware Security Module*): um hardware dedicado e resistente a violação física que **gera, guarda e usa chaves sem nunca as revelar**. Você pede "assine isto" ou "cifre isto", e o HSM devolve o resultado; a chave em si **não sai** do equipamento. É o cofre de verdade — e é o que reguladores esperam para as chaves mais críticas (como a que assina mensagens para o SPI).
- **KMS** (*Key Management Service*): o serviço de gestão de chaves — geralmente apoiado por HSM — que oferece a API de "criar chave, cifrar, decifrar, rotacionar, revogar, auditar quem usou". Serviços de nuvem oferecem isso gerenciado.

Uma dificuldade prática: o HSM/KMS é remoto e relativamente lento. Cifrar **cada campo de cada registro** com uma chamada ao KMS seria proibitivo — e enviar gigabytes de dados para "cifrar no cofre" seria absurdo. A solução é um padrão elegante chamado **envelope encryption**:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 380" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9e-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <rect x="20" y="20" width="250" height="110" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="145" y="46" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">KMS / HSM</text>
  <rect x="45" y="60" width="200" height="50" rx="6" fill="#fff" stroke="#166534"/>
  <text x="145" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">KEK — chave-mestra</text>
  <text x="145" y="98" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">(Key Encryption Key) NUNCA sai</text>
  <rect x="330" y="20" width="250" height="110" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="455" y="46" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">Serviço (Contas)</text>
  <rect x="355" y="60" width="200" height="50" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="455" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">DEK — chave de dados</text>
  <text x="455" y="98" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">(Data Encryption Key) vive em RAM</text>
  <rect x="640" y="20" width="240" height="110" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="760" y="46" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">Banco de dados</text>
  <text x="760" y="72" text-anchor="middle" font-family="monospace" font-size="10" fill="#333">cpf_cifrado   = AES(DEK, cpf)</text>
  <text x="760" y="90" text-anchor="middle" font-family="monospace" font-size="10" fill="#333">dek_cifrada   = KEK(DEK)</text>
  <text x="760" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">a DEK só é guardada CIFRADA</text>
  <text x="20" y="165" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">Escrever:</text>
  <text x="20" y="188" font-family="sans-serif" font-size="12" fill="#333">① serviço pede ao KMS uma DEK nova   ② KMS devolve DEK em claro + a mesma DEK cifrada pela KEK</text>
  <text x="20" y="208" font-family="sans-serif" font-size="12" fill="#333">③ serviço cifra o dado com a DEK (rápido, local)   ④ grava dado cifrado + DEK cifrada   ⑤ descarta a DEK em claro</text>
  <text x="20" y="245" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">Ler:</text>
  <text x="20" y="268" font-family="sans-serif" font-size="12" fill="#333">① lê o dado cifrado + a DEK cifrada   ② pede ao KMS para decifrar a DEK (KMS confere: este serviço PODE?)</text>
  <text x="20" y="288" font-family="sans-serif" font-size="12" fill="#333">③ decifra o dado localmente   ④ usa   ⑤ descarta</text>
  <rect x="20" y="315" width="860" height="52" rx="6" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="450" y="337" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1a1a1a"><tspan font-weight="bold">Por que funciona:</tspan> só uma chamada minúscula (a DEK) vai ao cofre — o volume de dados fica local e rápido.</text>
  <text x="450" y="356" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1a1a1a">Vazou o banco? Só há dado cifrado e DEKs cifradas. Sem acesso ao KMS, é ruído. E cada uso da KEK fica <tspan font-weight="bold">auditado</tspan>.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Envelope encryption: uma chave-mestra (KEK) que nunca sai do cofre protege chaves de dados (DEKs) que protegem o dado. Dois níveis dão rapidez, rotação barata e trilha de auditoria.</p>
</div>

Duas consequências práticas valiosas. **Rotação barata:** para trocar a chave-mestra, você não re-cifra terabytes — só re-cifra as DEKs (pequenas) com a KEK nova. E **revogação de acesso por política**: se um serviço é comprometido, você revoga a permissão dele *no KMS* e ele perde a capacidade de decifrar — sem tocar em um único byte do banco.

### 5.4 Tokenização versus criptografia: substituir em vez de esconder

Existe uma alternativa à criptografia para dados muito sensíveis, como número de cartão: a **tokenização**. Em vez de guardar o dado cifrado, o sistema guarda um **substituto sem valor** (o *token*, ex.: `tok_9f31...`) e o dado real vive **num cofre único, isolado**. A diferença conceitual é fina e importante: dado cifrado ainda é *o dado*, matematicamente reversível por quem tiver a chave; um token não tem relação matemática com o original — só o cofre sabe o mapeamento.

O benefício regulatório é enorme: no padrão de segurança da indústria de cartões (**PCI DSS**), quanto **menos** sistemas tocam o dado real, **menor o escopo** de auditoria e de conformidade. Se só o cofre de tokens vê o número do cartão, os 40 outros serviços operam com `tok_9f31...` e ficam **fora do escopo**. Isso é **redução da superfície de ataque por desenho**: a melhor proteção para um dado é *não tê-lo*. (Observação: o Pix em si não usa cartão; mas uma fintech com conta digital quase sempre também emite ou processa cartões — e o princípio vale igual para CPF, número de conta e qualquer identificador sensível.)

### 5.5 A tensão que ninguém conta: LGPD versus ledger imutável

Aqui mora um dos conflitos mais interessantes de arquitetura financeira — e é o tipo de coisa que separa quem leu a lei de quem só leu o tutorial. Duas obrigações legais **apontam em direções opostas**:

- A **LGPD** (Lei Geral de Proteção de Dados) dá ao titular o **direito à eliminação** de seus dados pessoais e obriga a **minimização** — não guardar mais do que o necessário.
- A regulação financeira exige **retenção**: registros de transações precisam ser mantidos por anos (com prazos definidos por normas do setor e do BACEN) e, por natureza, o ledger é **append-only** — você não apaga nem reescreve o passado.

O cliente pede "apaguem meus dados"; o ledger imutável diz "eu não posso apagar". Como sair? Não com um `DELETE`. A saída de engenharia é uma técnica chamada **crypto-shredding** (*destruição criptográfica*): os dados pessoais do titular são cifrados com uma **chave dedicada àquele titular** (uma DEK por cliente). Quando chega o pedido de eliminação — e a base legal de retenção já expirou —, você **destrói a chave**. Os registros continuam no ledger (a integridade contábil e a trilha estão preservadas), mas os dados pessoais dentro deles viraram **ruído irrecuperável**.

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 320" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9c-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <text x="225" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#3730a3">ANTES do pedido de eliminação</text>
  <text x="675" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#991b1b">DEPOIS (a chave do titular destruída)</text>
  <rect x="20" y="40" width="410" height="150" rx="8" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="35" y="66" font-family="monospace" font-size="11" fill="#333">lancamento #88231</text>
  <text x="35" y="86" font-family="monospace" font-size="11" fill="#333">  valor: 4.800,00      hash: a91f…</text>
  <text x="35" y="106" font-family="monospace" font-size="11" fill="#333">  data:  2026-09-30T14:22Z</text>
  <text x="35" y="126" font-family="monospace" font-size="11" fill="#166534">  titular: AES(DEK-cli-5519, "Bruno S., CPF …")</text>
  <text x="35" y="150" font-family="sans-serif" font-size="11" fill="#666">DEK-cli-5519 existe no KMS → decifrável por serviço autorizado</text>
  <text x="35" y="172" font-family="sans-serif" font-size="11" fill="#666">valor, data e hash: dado contábil, NÃO pessoal</text>
  <rect x="470" y="40" width="410" height="150" rx="8" fill="#fff" stroke="#991b1b" stroke-width="2"/>
  <text x="485" y="66" font-family="monospace" font-size="11" fill="#333">lancamento #88231</text>
  <text x="485" y="86" font-family="monospace" font-size="11" fill="#333">  valor: 4.800,00      hash: a91f…</text>
  <text x="485" y="106" font-family="monospace" font-size="11" fill="#333">  data:  2026-09-30T14:22Z</text>
  <text x="485" y="126" font-family="monospace" font-size="11" fill="#b91c1c">  titular: AES(DEK-cli-5519, "▓▓▓▓▓▓▓▓")  ← ruído</text>
  <text x="485" y="150" font-family="sans-serif" font-size="11" fill="#666">DEK-cli-5519 DESTRUÍDA → irrecuperável, por qualquer um</text>
  <text x="485" y="172" font-family="sans-serif" font-size="11" fill="#166534">hash da cadeia intacto → integridade contábil preservada</text>
  <line x1="432" y1="115" x2="468" y2="115" stroke="#4338ca" stroke-width="2" marker-end="url(#a9c-arrow)"/>
  <rect x="20" y="215" width="860" height="85" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="450" y="238" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Pré-requisito de desenho (tem que existir DESDE O DIA 1):</text>
  <text x="450" y="259" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">separar o que é dado contábil (imutável, retido) do que é dado pessoal (cifrado por titular, eliminável).</text>
  <text x="450" y="279" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Não dá para "consertar" isso depois num ledger que já misturou os dois no mesmo campo.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Crypto-shredding: o dado pessoal é cifrado com uma chave por titular; destruir a chave "apaga" o dado sem tocar num ledger append-only.</p>
</div>

Duas ressalvas de honestidade. Primeira: **crypto-shredding não é decisão só de engenharia** — quando a lei *exige retenção* de um dado identificável (para fins de prevenção à fraude ou obrigação regulatória), a eliminação simplesmente **não é devida** naquele momento; o jurídico define o que pode ser eliminado e quando. A arquitetura oferece a *capacidade*; o direito diz *se e quando usar*. Segunda: o desenho só funciona se a separação **contábil vs. pessoal** foi feita **no modelo de dados desde o início** — um ledger que gravou o nome do titular em texto claro dentro do lançamento não tem correção elegante depois. Este é um exemplo perfeito de por que segurança e privacidade são **decisões de arquitetura inicial**, não camadas que se colam no fim.

---

## 6. Segredos, APIs e a cadeia de suprimentos

### 6.1 O incidente do segredo vazado

Sexta-feira, 17h40. Um desenvolvedor, depurando uma integração, coloca a credencial de produção do serviço de Pagamentos num `application.yml` e faz o commit — num repositório que, dois meses antes, foi aberto para colaboradores externos. Ou: a credencial entrou num *stack trace* impresso num log que uma ferramenta de observabilidade indexou. Não importa o caminho: **o segredo vazou**. Em minutos, bots que varrem repositórios públicos por padrões de credencial (isso é automático, contínuo e rápido) a encontram.

A pergunta que separa equipes maduras das demais: **qual é o raio de explosão, e em quanto tempo o segredo pode ser tornado inútil?** Se a credencial é estática, de vida longa, com poder total, e trocá-la exige reimplantar dez serviços com uma janela de manutenção — o incidente dura dias. Se é dinâmica, de vida curta e com poder mínimo, ele dura minutos e o estrago é limitado.

### 6.2 Ciclo de vida de um segredo

Um segredo (senha de banco, chave de API, certificado, chave de assinatura) tem um ciclo de vida, e cada etapa precisa de dono e de controle:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 300" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9v-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <rect x="20" y="30" width="150" height="80" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="95" y="58" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">1. Emitir</text>
  <text x="95" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">gerado pelo cofre,</text>
  <text x="95" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">nunca escolhido por humano</text>
  <rect x="200" y="30" width="150" height="80" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="275" y="58" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">2. Entregar</text>
  <text x="275" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">injetado em runtime,</text>
  <text x="275" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">só p/ a identidade certa</text>
  <rect x="380" y="30" width="150" height="80" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="455" y="58" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">3. Usar</text>
  <text x="455" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">em memória, nunca em</text>
  <text x="455" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">código, imagem ou log</text>
  <rect x="560" y="30" width="150" height="80" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="635" y="58" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">4. Rotacionar</text>
  <text x="635" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">automático, periódico,</text>
  <text x="635" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">sem downtime</text>
  <rect x="740" y="30" width="140" height="80" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="2"/>
  <text x="810" y="58" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#991b1b">5. Revogar</text>
  <text x="810" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">em minutos, ao vazar</text>
  <text x="810" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">ou ao mudar a equipe</text>
  <line x1="170" y1="70" x2="198" y2="70" stroke="#4338ca" stroke-width="2" marker-end="url(#a9v-arrow)"/>
  <line x1="350" y1="70" x2="378" y2="70" stroke="#4338ca" stroke-width="2" marker-end="url(#a9v-arrow)"/>
  <line x1="530" y1="70" x2="558" y2="70" stroke="#4338ca" stroke-width="2" marker-end="url(#a9v-arrow)"/>
  <line x1="710" y1="70" x2="738" y2="70" stroke="#4338ca" stroke-width="2" marker-end="url(#a9v-arrow)"/>
  <rect x="20" y="145" width="420" height="130" rx="8" fill="#fef2f2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="230" y="168" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#991b1b">O que produz vazamento</text>
  <text x="35" y="192" font-family="sans-serif" font-size="11" fill="#333">✘ segredo em application.yml / código / imagem Docker</text>
  <text x="35" y="210" font-family="sans-serif" font-size="11" fill="#333">✘ mesma credencial em todos os ambientes</text>
  <text x="35" y="228" font-family="sans-serif" font-size="11" fill="#333">✘ credencial estática de vida longa, poder total</text>
  <text x="35" y="246" font-family="sans-serif" font-size="11" fill="#333">✘ segredo em variável de ambiente impressa em erro</text>
  <text x="35" y="264" font-family="sans-serif" font-size="11" fill="#333">✘ ninguém sabe quem usa nem quando expira</text>
  <rect x="460" y="145" width="420" height="130" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="670" y="168" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">O que limita o dano</text>
  <text x="475" y="192" font-family="sans-serif" font-size="11" fill="#333">✔ cofre de segredos (Vault, KMS, Secrets Manager)</text>
  <text x="475" y="210" font-family="sans-serif" font-size="11" fill="#333">✔ credenciais DINÂMICAS: geradas sob demanda, TTL de minutos</text>
  <text x="475" y="228" font-family="sans-serif" font-size="11" fill="#333">✔ acesso por identidade do workload (não por senha)</text>
  <text x="475" y="246" font-family="sans-serif" font-size="11" fill="#333">✔ scanner de segredos no commit (pre-commit + CI)</text>
  <text x="475" y="264" font-family="sans-serif" font-size="11" fill="#333">✔ rotação automática testada regularmente</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O ciclo de vida do segredo. Equipe madura não "guarda bem" segredos — ela reduz o tempo de vida e o poder de cada um até que o vazamento seja um non-event.</p>
</div>

O salto conceitual está na palavra **dinâmicas**. Em vez de um usuário de banco fixo, com senha guardada em algum lugar, o serviço se autentica ao cofre **com sua identidade de workload** (a mesma do mTLS!) e o cofre **cria, na hora, um usuário de banco temporário** com TTL de uma hora e só as permissões necessárias. Ninguém "conhece" a senha; ela nasce e morre com o pod. O vazamento de uma credencial dessas é quase inofensivo: ela expira sozinha antes de alguém usá-la. E note o encaixe com o resto da aula: **identidade de workload é o que permite eliminar segredos estáticos** — é a raiz de confiança do cofre.

Três ressalvas: a chave "zero" (a credencial que autentica o workload ao cofre) precisa vir de algo que não seja um segredo digitado — do certificado do próprio pod, do token de conta de serviço do Kubernetes; um scanner de segredos no *pre-commit* e no CI é barato e pega o erro mais comum antes que ele chegue ao repositório; e o **Secret nativo do Kubernetes** é apenas Base64 — codificado, não cifrado — então só é seguro com criptografia de repouso do *etcd* habilitada e acesso restrito por RBAC.

### 6.3 Integridade e replay: proteger a mensagem, não só o canal

TLS protege o *canal*. Mas há mensagens que atravessam vários saltos, ficam armazenadas em filas, ou chegam de parceiros externos — e para elas o canal seguro não basta. Precisamos que **a própria mensagem** prove sua origem e sua integridade. O caso canônico é o **webhook**: o provedor de pagamentos avisa a TechPix "o Pix E123 foi liquidado" via `POST` para uma URL pública. Como a TechPix sabe que a chamada veio *mesmo* do provedor — e não de um atacante que descobriu a URL e forjou "liquidado"?

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 400" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9h-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a9h-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <rect x="20" y="15" width="180" height="50" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="110" y="38" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">Provedor (emissor)</text>
  <text x="110" y="54" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">compartilha segredo S</text>
  <rect x="700" y="15" width="180" height="50" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="790" y="38" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">TechPix (receptor)</text>
  <text x="790" y="54" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">também conhece S</text>
  <rect x="20" y="90" width="420" height="120" rx="8" fill="#fff" stroke="#d4a017" stroke-width="1.5"/>
  <text x="35" y="112" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Emissor monta e assina:</text>
  <text x="35" y="134" font-family="monospace" font-size="11" fill="#333">t   = 1790000123           (timestamp)</text>
  <text x="35" y="152" font-family="monospace" font-size="11" fill="#333">id  = evt_77a1             (único)</text>
  <text x="35" y="170" font-family="monospace" font-size="11" fill="#333">body= {"e2e":"E123...","st":"LIQUIDADO"}</text>
  <text x="35" y="192" font-family="monospace" font-size="11" fill="#166534">sig = HMAC-SHA256(S, t + "." + id + "." + body)</text>
  <line x1="440" y1="150" x2="700" y2="150" stroke="#4338ca" stroke-width="2" marker-end="url(#a9h-arrow)"/>
  <text x="570" y="142" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">POST + headers: t, id, sig</text>
  <rect x="20" y="230" width="860" height="150" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="35" y="254" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Receptor valida — nesta ordem:</text>
  <text x="35" y="276" font-family="sans-serif" font-size="12" fill="#333">① recalcula HMAC(S, t + "." + id + "." + body) e compara em tempo constante  →  integridade + autenticidade</text>
  <text x="35" y="298" font-family="sans-serif" font-size="12" fill="#333">② |agora − t| ≤ 5 minutos?  →  rejeita mensagem antiga (janela de replay curta)</text>
  <text x="35" y="320" font-family="sans-serif" font-size="12" fill="#333">③ id já foi processado?  →  descarta duplicata (anti-replay dentro da janela) — mesma ideia da idempotência</text>
  <text x="35" y="342" font-family="sans-serif" font-size="12" fill="#333">④ só então processa o efeito de negócio</text>
  <text x="35" y="366" font-family="sans-serif" font-size="11" fill="#b91c1c">Sem ②③, um atacante que capturou UMA mensagem legítima a reenvia mil vezes: assinatura perfeita, efeito duplicado.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Webhook assinado com HMAC, timestamp e id único. A assinatura prova origem e integridade; timestamp e id impedem o replay de mensagens legítimas capturadas.</p>
</div>

**HMAC** (*Hash-based Message Authentication Code*) é uma assinatura construída com um segredo compartilhado: só quem conhece `S` consegue produzir um `sig` válido para aquele conteúdo, e qualquer alteração de um byte muda o `sig`. Duas sutilezas de implementação que já derrubaram sistemas de verdade: **comparar o `sig` em tempo constante** (uma comparação `==` normal termina no primeiro byte diferente, e o tempo de resposta vaza informação byte a byte — o *timing attack*); e **assinar o timestamp junto**, porque um `sig` que cobre só o body permite que o atacante reenvie a mensagem *para sempre*. O **replay** — reenviar uma mensagem legítima capturada — é o ataque que a criptografia sozinha não vê, porque a mensagem *é* autêntica; só o contexto (tempo e unicidade) a denuncia. Percebam o parentesco com o mecanismo de **chave de idempotência**, que impede que uma mesma intenção produza efeito duplo: aqui, a mesma ideia serve à segurança.

Quando o parceiro é regulatório (o SPI), o padrão sobe de nível: em vez de segredo compartilhado, usa-se **assinatura digital com certificado** — a mensagem é assinada com a chave privada da TechPix (guardada no HSM) e o BACEN verifica com o certificado público. A diferença é o **não-repúdio**: com segredo compartilhado, qualquer das duas partes *poderia* ter gerado o HMAC; com assinatura assimétrica, só o dono da chave privada poderia — o que vale como prova.

Por fim, **limitação de taxa** (*rate limiting*) é controle de segurança e de disponibilidade ao mesmo tempo: limita quantas requisições cada *identidade* (não só cada IP) pode fazer numa janela, protegendo contra força bruta em login, enumeração de chaves Pix e esgotamento de capacidade. O algoritmo clássico é o *token bucket*: cada cliente tem um balde com N fichas que se reabastece a taxa fixa; cada requisição gasta uma; balde vazio, requisição recusada com `429`. Um detalhe específico de fintech: limitar por **identidade autenticada e por operação** (5 tentativas de consulta de chave Pix por minuto, por exemplo) e não só por IP — o atacante distribuído troca de IP, mas não troca de conta.

### 6.4 A cadeia de suprimentos: o código que você não escreveu

Um serviço moderno é 10% código próprio e 90% dependências — bibliotecas, imagens de container base, ferramentas de build. Cada uma é código **de terceiros rodando com os privilégios do seu serviço**, dentro da sua fronteira de confiança. Um atacante que compromete uma biblioteca popular — ou publica uma com nome parecido (*typosquatting*) — executa código dentro do Pagamentos sem tocar em uma linha da TechPix. As defesas são de processo e de artefato:

- **SBOM** (*Software Bill of Materials*): o inventário de tudo que compõe cada imagem. Quando uma vulnerabilidade nova é anunciada numa biblioteca, a pergunta "estamos expostos?" passa a ser uma consulta de segundos, e não uma caça de dias.
- **Assinatura e verificação de artefatos:** a imagem é assinada no pipeline de build, e o cluster **só executa imagem com assinatura válida** da sua própria cadeia. Uma imagem adulterada ou fabricada por fora do pipeline é recusada na admissão.
- **Versões fixadas e repositório interno:** dependências com versão e *hash* travados, vindas de um espelho interno, sem "puxe a mais recente" em produção.
- **Menor imagem possível:** menos software na imagem, menos superfície de ataque (imagens *distroless*, sem shell nem gerenciador de pacotes).
- **Isolamento como rede de segurança:** se, apesar de tudo, um workload é comprometido, as políticas de §4 e o mínimo privilégio limitam o alcance.

Repare que esta seção termina exatamente onde a §4 começou: **você não consegue impedir todo comprometimento — você desenha para que ele custe pouco.** É a mudança de mentalidade de "impedir a invasão" para "assumir a invasão" (*assume breach*), e ela organiza o resto da aula.

---

## 7. O antifraude como controle de segurança

Até aqui, todos os controles respondem a uma pergunta binária sobre **permissão**: *"este sujeito pode fazer isto?"* Mas a linha mais perigosa do nosso quadro de adversários não viola nenhuma permissão. O **golpista de engenharia social** convence a própria Ana a fazer um Pix "urgente" para uma "conta segura" — a Ana está autenticada com MFA, é dona da conta, o valor está dentro do limite, a assinatura da transação é impecável. **Todos os controles da §2 à §6 dizem "sim", e o dinheiro está sendo roubado.** O que falta é um controle que faça uma pergunta diferente: não *"pode?"*, mas *"isso parece certo?"*. É o **antifraude**: uma camada de decisão baseada em **risco**, não em permissão.

### 7.1 O que ele enxerga: sinais

Antifraude é um sistema de inferência sobre **sinais** — evidências de contexto, cada uma fraca sozinha, forte em combinação:

| Família de sinal | Exemplos | O que denuncia |
|---|---|---|
| **Dispositivo** | Aparelho novo, emulador, root/jailbreak, app adulterado | Account takeover; automação |
| **Comportamento** | Velocidade de digitação, padrão de navegação, hora habitual | Sessão operada por outra pessoa ou por script |
| **Velocidade (*velocity*)** | N Pix em M minutos; soma nas últimas horas | Esvaziamento rápido de conta |
| **Relacionamento** | Destinatário novo, primeiro Pix, valor atípico para o histórico | Golpe; conta laranja |
| **Grafo** | Destinatário recebe de dezenas de contas novas e repassa imediatamente | Conta laranja (mula) numa rede de dispersão |
| **Contexto da sessão** | Chamada de telefone ativa durante o Pix, acesso remoto ao aparelho, cola de chave | Coação / engenharia social em curso |

### 7.2 Como decide: do sinal à ação

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 380" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9f-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a9f-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
    <marker id="a9f-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#d4a017"/>
    </marker>
    <marker id="a9f-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <rect x="20" y="20" width="140" height="70" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="90" y="50" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Pedido de Pix</text>
  <text x="90" y="68" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">valor, destino, sessão</text>
  <rect x="200" y="20" width="200" height="70" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="300" y="46" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Enriquecimento (features)</text>
  <text x="300" y="64" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">histórico 24h · device · grafo</text>
  <text x="300" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">leitura em cache (~ms)</text>
  <rect x="440" y="20" width="190" height="70" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="535" y="46" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">Motor de decisão</text>
  <text x="535" y="64" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">regras (determinísticas)</text>
  <text x="535" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">+ modelo (score 0–1)</text>
  <rect x="670" y="20" width="210" height="70" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="775" y="46" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1a1a1a">Decisão em ~100 ms</text>
  <text x="775" y="64" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">tem que caber no orçamento</text>
  <text x="775" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">de latência do Pix</text>
  <line x1="160" y1="55" x2="198" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a9f-arrow)"/>
  <line x1="400" y1="55" x2="438" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a9f-arrow)"/>
  <line x1="630" y1="55" x2="668" y2="55" stroke="#4338ca" stroke-width="2" marker-end="url(#a9f-arrow)"/>
  <line x1="775" y1="90" x2="775" y2="130" stroke="#888" stroke-width="1.5"/>
  <line x1="150" y1="130" x2="775" y2="130" stroke="#888" stroke-width="1.5"/>
  <line x1="150" y1="130" x2="150" y2="160" stroke="#166534" stroke-width="2" marker-end="url(#a9f-green)"/>
  <line x1="450" y1="130" x2="450" y2="160" stroke="#d4a017" stroke-width="2" marker-end="url(#a9f-amber)"/>
  <line x1="750" y1="130" x2="750" y2="160" stroke="#b91c1c" stroke-width="2" marker-end="url(#a9f-red)"/>
  <rect x="30" y="162" width="240" height="90" rx="8" fill="#dcfce7" stroke="#166534" stroke-width="2"/>
  <text x="150" y="188" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">ALLOW · risco baixo</text>
  <text x="150" y="208" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">segue direto, sem fricção</text>
  <text x="150" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">(a grande maioria do tráfego)</text>
  <rect x="330" y="162" width="240" height="90" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="450" y="188" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">STEP-UP / RETER · risco médio</text>
  <text x="450" y="208" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">pede biometria, alerta anti-golpe,</text>
  <text x="450" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">atraso de segurança, revisão humana</text>
  <rect x="630" y="162" width="240" height="90" rx="8" fill="#fee2e2" stroke="#b91c1c" stroke-width="2"/>
  <text x="750" y="188" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#991b1b">DENY · risco alto</text>
  <text x="750" y="208" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">recusa, bloqueia a sessão,</text>
  <text x="750" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">abre caso para a equipe de fraude</text>
  <rect x="20" y="280" width="860" height="85" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="450" y="304" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1a1a1a">O trade-off que não some: fricção × perda</text>
  <text x="450" y="326" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Falso positivo (bloqueia cliente legítimo) custa confiança e churn. Falso negativo (deixa passar fraude) custa dinheiro irreversível.</text>
  <text x="450" y="346" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">O limiar do "amarelo" é uma decisão de NEGÓCIO com dado por trás, revisada continuamente — não uma constante no código.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Pipeline de decisão de risco. A saída não é só sim/não: o meio-termo (step-up, reter, alertar) é o que separa antifraude bom de antifraude que ou incomoda todo mundo ou deixa tudo passar.</p>
</div>

**Regras versus modelo** é uma falsa dicotomia — os dois convivem, por razões diferentes. **Regras** são determinísticas, explicáveis e instantâneas de mudar: "bloqueie Pix acima de R$ 5.000 de aparelho novo nas primeiras 24h" pode entrar em produção em minutos, quando surge um golpe novo, e um auditor consegue ler a regra. **Modelos de aprendizado de máquina** capturam padrões sutis e combinações que ninguém escreveria como regra, mas são probabilísticos, exigem dado rotulado e se degradam quando o comportamento dos golpistas muda (*concept drift* — o adversário se adapta ao modelo). Na prática: regras cobrem o conhecido e o urgente; o modelo cobre o difuso; e cada decisão precisa ser **explicável** — um bloqueio que a empresa não consegue justificar ao cliente ou ao regulador é um problema jurídico, não só técnico.

Duas armadilhas específicas de arquitetura. **Primeira: o antifraude está no caminho crítico do pagamento**, então sua latência e disponibilidade entram na conta do orçamento do Pix. Isso leva a uma decisão de projeto que todo sistema financeiro enfrenta, e que precisa ser explícita: quando o antifraude **não responde** a tempo, o sistema **falha aberto** (*fail-open*: deixa o pagamento passar sem avaliação, aceitando risco de fraude) ou **falha fechado** (*fail-closed*: recusa, aceitando risco de perder negócio legítimo)? Não existe resposta universal — a saída madura é **graduar por valor**: para valores baixos, fail-open com limite agregado (o risco máximo é conhecido e pequeno); para valores altos, fail-closed. **Segunda: o próprio antifraude é alvo.** Um atacante que descobre o limiar ("abaixo de R$ 1.000 não há step-up") fraciona o valor em várias transações (*structuring* / *smurfing*) — daí a importância de sinais agregados por janela, não só por operação isolada, e de manter as regras exatas fora do alcance de quem sonda.

### 7.3 Limites como controle de dano

Complementando o antifraude, os **limites transacionais** funcionam como **disjuntores de prejuízo**: mesmo que tudo o mais falhe, o dano máximo por janela é conhecido. Limite por transação, limite diário, **limite noturno reduzido** (golpes e sequestros se concentram à noite, quando a vítima está menos alerta e mais difícil de contatar) e **limite para conta nova** (contas laranja e fraudes de identidade são mais frequentes nas primeiras semanas). É o mesmo princípio do raio de explosão aplicado ao dinheiro: se um atacante toma uma conta, ele só consegue esvaziar até o limite, e o cliente ganha tempo para reagir. Além disso, permitir que **o próprio cliente reduza seus limites** é um controle de segurança barato e eficaz.

E, num sistema em que o dinheiro não se recupera sozinho, a defesa **posterior** também é parte do desenho: detecção rápida de padrões de dispersão (a conta laranja que recebe e repassa em segundos), integração com o mecanismo regulatório de devolução em caso de fraude, e cooperação entre instituições. A segurança financeira não termina no "bloquear": termina no "**recuperar o que der**".

---

## 8. O adversário que já tem a chave: insiders e controles humanos

Todo o desenho até aqui assume, no fundo, um invasor que precisa *entrar*. O **insider** — um engenheiro, um operador de suporte, um DBA, um terceirizado — **já está dentro**, com credenciais legítimas, conhecimento do sistema e, muitas vezes, acesso maior que o necessário. Pode ser malicioso (desviar dinheiro), coagido (um golpista o subornou ou ameaçou) ou apenas descuidado (rodou o script errado em produção). Em sistema financeiro, *o estrago do descuidado e do malicioso é idêntico*: dinheiro que sai sem que devesse.

Aqui a criptografia e o mTLS pouco ajudam — o insider é uma identidade autêntica. A defesa é **desenhar o processo para que nenhuma pessoa, sozinha, consiga causar dano grave sem ser notada**. São quatro controles complementares:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 420" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9i-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a9i-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#166534"/>
    </marker>
  </defs>
  <rect x="20" y="15" width="420" height="185" rx="10" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="230" y="40" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#3730a3">1. Maker-checker (quatro olhos)</text>
  <rect x="40" y="60" width="110" height="46" rx="6" fill="#fff" stroke="#4338ca"/>
  <text x="95" y="80" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Operador A</text>
  <text x="95" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">PROPÕE (maker)</text>
  <rect x="180" y="60" width="90" height="46" rx="6" fill="#fef9e7" stroke="#d4a017"/>
  <text x="225" y="80" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Pendente</text>
  <text x="225" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">nada executa</text>
  <rect x="300" y="60" width="120" height="46" rx="6" fill="#fff" stroke="#166534"/>
  <text x="360" y="80" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Operador B</text>
  <text x="360" y="95" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">APROVA (checker)</text>
  <line x1="150" y1="83" x2="178" y2="83" stroke="#4338ca" stroke-width="2" marker-end="url(#a9i-arrow)"/>
  <line x1="270" y1="83" x2="298" y2="83" stroke="#4338ca" stroke-width="2" marker-end="url(#a9i-arrow)"/>
  <text x="35" y="135" font-family="sans-serif" font-size="11" fill="#333">Regra dura: B ≠ A, verificado pelo sistema,</text>
  <text x="35" y="151" font-family="sans-serif" font-size="11" fill="#333">não por combinação verbal.</text>
  <text x="35" y="177" font-family="sans-serif" font-size="11" fill="#333">Para: ajuste manual de saldo, alteração de limite,</text>
  <text x="35" y="192" font-family="sans-serif" font-size="11" fill="#333">liberação de valor retido, mudança de chave de assinatura.</text>
  <rect x="460" y="15" width="420" height="185" rx="10" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="670" y="40" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#166534">2. Acesso JIT (just-in-time)</text>
  <text x="475" y="68" font-family="sans-serif" font-size="11" fill="#333">Ninguém tem acesso permanente à produção.</text>
  <text x="475" y="90" font-family="sans-serif" font-size="11" fill="#333">Precisa? Pede → justifica (ticket) → aprovador → recebe</text>
  <text x="475" y="106" font-family="sans-serif" font-size="11" fill="#333">credencial com TTL de 1h → expira sozinha → tudo gravado.</text>
  <text x="475" y="136" font-family="sans-serif" font-size="11" fill="#333">O privilégio "de repouso" é zero; o de trabalho é temporário.</text>
  <text x="475" y="162" font-family="sans-serif" font-size="11" fill="#b91c1c">Sem isso, cada conta de engenheiro é um alvo de valor</text>
  <text x="475" y="178" font-family="sans-serif" font-size="11" fill="#b91c1c">permanente — e a única coisa entre o atacante e produção.</text>
  <rect x="20" y="215" width="420" height="190" rx="10" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="230" y="240" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#7a5c00">3. Segregação de funções</text>
  <text x="35" y="268" font-family="sans-serif" font-size="11" fill="#333">Quem escreve o código ≠ quem aprova o deploy.</text>
  <text x="35" y="288" font-family="sans-serif" font-size="11" fill="#333">Quem opera o ledger ≠ quem concilia o ledger.</text>
  <text x="35" y="308" font-family="sans-serif" font-size="11" fill="#333">Quem administra o banco ≠ quem administra as chaves.</text>
  <text x="35" y="328" font-family="sans-serif" font-size="11" fill="#333">Quem cria um usuário ≠ quem lhe atribui permissão.</text>
  <text x="35" y="356" font-family="sans-serif" font-size="11" fill="#666">Princípio: para cometer fraude interna,</text>
  <text x="35" y="372" font-family="sans-serif" font-size="11" fill="#666">seria preciso o CONLUIO de pessoas de funções distintas —</text>
  <text x="35" y="388" font-family="sans-serif" font-size="11" fill="#666">o que sobe o custo e o risco de ser descoberto.</text>
  <rect x="460" y="215" width="420" height="190" rx="10" fill="#fee2e2" stroke="#b91c1c" stroke-width="2"/>
  <text x="670" y="240" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#991b1b">4. Break-glass (vidro de emergência)</text>
  <text x="475" y="268" font-family="sans-serif" font-size="11" fill="#333">Sempre haverá um incidente às 3h em que o fluxo</text>
  <text x="475" y="284" font-family="sans-serif" font-size="11" fill="#333">normal de aprovação é lento demais. A saída NÃO é</text>
  <text x="475" y="300" font-family="sans-serif" font-size="11" fill="#333">manter uma conta-mestra permanente. É um acesso de</text>
  <text x="475" y="316" font-family="sans-serif" font-size="11" fill="#333">emergência que:</text>
  <text x="475" y="336" font-family="sans-serif" font-size="11" fill="#333">• dispara alerta imediato para a segurança</text>
  <text x="475" y="352" font-family="sans-serif" font-size="11" fill="#333">• grava a sessão inteira (comandos, telas)</text>
  <text x="475" y="368" font-family="sans-serif" font-size="11" fill="#333">• expira em minutos e exige revisão obrigatória depois</text>
  <text x="475" y="388" font-family="sans-serif" font-size="11" fill="#666">Usá-lo é possível — usá-lo em silêncio, não.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Quatro controles humanos. Todos tratam pessoas como o que elas são: identidades com poder, sujeitas a erro, coação e má-fé — e por isso vigiadas pelo desenho, não pela confiança.</p>
</div>

**Uma observação de honestidade cultural.** Esses controles têm um custo real: fricção, lentidão, ressentimento ("vocês não confiam em mim?"). A resposta madura é reenquadrar: o quatro-olhos não é desconfiança *da pessoa* — é proteção *da pessoa*. Num sistema sem ele, se um valor some, **todos** os que tinham acesso são suspeitos; num sistema com ele, a trilha mostra exatamente quem fez o quê e quem aprovou. Os controles protegem o inocente tanto quanto barram o culpado.

---

## 9. Auditoria: provar, não apenas registrar

Chegamos à pergunta que amarra tudo: **"como provamos que o `cli-5519` tentou usar a `acc-2207`, e que o sistema o barrou?"** — ou, no caso ruim, **"como provamos quem aprovou aquele ajuste de saldo de R$ 80.000?"** Se a resposta depende de "vamos olhar os logs", provavelmente não há prova nenhuma.

### 9.1 Log de aplicação não é trilha de auditoria

São artefatos com propósitos diferentes, e confundi-los é um erro clássico:

| | **Log de aplicação** | **Trilha de auditoria** |
|---|---|---|
| **Serve para** | Depurar, operar, entender falhas | Provar quem fez o quê, quando, com que resultado |
| **Público** | Engenheiros, plantão | Segurança, compliance, reguladores, jurídico |
| **Conteúdo** | O que o programador achou útil imprimir | Estrutura *obrigatória*: sujeito, ação, recurso, decisão, resultado |
| **Garantias** | Nenhuma — pode ser truncado, rotacionado, perdido | **Completo, ordenado, imutável, retido por anos** |
| **Amostragem** | Comum (por custo) | **Proibida** — falta um evento, falta a prova |
| **Pode vazar dado?** | Não deveria; mas acontece | Contém identificadores; acesso restrito e ele próprio auditado |

Uma trilha de auditoria não é "mais logs". É um **registro estruturado, obrigatório, com garantias** — e cada evento responde a sete perguntas: **quem** (sujeito e, quando houver, o workload intermediário), **o quê** (ação), **sobre o quê** (recurso), **quando** (timestamp confiável), **de onde** (dispositivo, IP, sessão), **qual foi a decisão** (permitido/negado e *por qual regra*) e **qual foi o resultado**. Reparem que **negativas são eventos de primeira classe**: o `403` do Bruno é a evidência mais valiosa de todo o incidente — é a *tentativa* de ataque, e ela só existe na trilha se alguém decidiu registrá-la.

```json
{
  "evento": "PIX_NEGADO_AUTORIZACAO",
  "quando": "2026-09-30T14:22:01.482Z",
  "sujeito": { "id": "cli-5519", "acr": "mfa", "device": "dev-a41" },
  "atuando_via": "pagamentos-svc",
  "acao": "pix:criar",
  "recurso": { "tipo": "conta", "id": "acc-2207" },
  "decisao": "NEGAR",
  "regra": "ContaPolicy.podeMovimentar: titular(acc-2207)=cli-8420 ≠ sujeito",
  "correlacao": { "trace_id": "9f2c…", "e2e_id": null },
  "seq": 88231409,
  "hash_anterior": "a91f…c3d2"
}
```

### 9.2 Tornar a trilha à prova de adulteração

Uma trilha só tem valor de prova se **ninguém consegue alterá-la sem que se perceba** — inclusive quem administra o sistema. Um invasor esperto (ou um insider) que fez algo indevido tenta, antes de sair, **apagar a própria pegada**. Duas técnicas trabalham juntas:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 340" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9u-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <text x="450" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#3730a3">Cadeia de hashes: cada evento "sela" o anterior</text>
  <rect x="20" y="40" width="200" height="100" rx="8" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="120" y="62" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Evento #1</text>
  <text x="32" y="84" font-family="monospace" font-size="10" fill="#333">dados: PIX_OK …</text>
  <text x="32" y="102" font-family="monospace" font-size="10" fill="#333">prev:  0000…</text>
  <text x="32" y="124" font-family="monospace" font-size="10" fill="#166534">hash1 = H(dados+prev)</text>
  <rect x="350" y="40" width="200" height="100" rx="8" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="450" y="62" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Evento #2</text>
  <text x="362" y="84" font-family="monospace" font-size="10" fill="#333">dados: NEGADO …</text>
  <text x="362" y="102" font-family="monospace" font-size="10" fill="#333">prev:  hash1</text>
  <text x="362" y="124" font-family="monospace" font-size="10" fill="#166534">hash2 = H(dados+hash1)</text>
  <rect x="680" y="40" width="200" height="100" rx="8" fill="#fff" stroke="#4338ca" stroke-width="2"/>
  <text x="780" y="62" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#3730a3">Evento #3</text>
  <text x="692" y="84" font-family="monospace" font-size="10" fill="#333">dados: AJUSTE …</text>
  <text x="692" y="102" font-family="monospace" font-size="10" fill="#333">prev:  hash2</text>
  <text x="692" y="124" font-family="monospace" font-size="10" fill="#166534">hash3 = H(dados+hash2)</text>
  <line x1="220" y1="90" x2="348" y2="90" stroke="#4338ca" stroke-width="2" marker-end="url(#a9u-arrow)"/>
  <line x1="550" y1="90" x2="678" y2="90" stroke="#4338ca" stroke-width="2" marker-end="url(#a9u-arrow)"/>
  <rect x="20" y="170" width="860" height="70" rx="8" fill="#fee2e2" stroke="#b91c1c" stroke-width="1.5"/>
  <text x="450" y="194" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#991b1b">Se alguém altera ou apaga o Evento #2…</text>
  <text x="450" y="214" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">hash2 muda → o "prev" do #3 deixa de bater → a cadeia quebra dali em diante.</text>
  <text x="450" y="230" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Adulteração vira detectável — e o ponto exato da quebra aponta o que foi mexido.</text>
  <rect x="20" y="260" width="860" height="70" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="450" y="284" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#166534">…e o último hash é ANCORADO fora do alcance do administrador</text>
  <text x="450" y="304" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">armazenamento WORM (write-once, read-many) · conta separada · carimbo de tempo de terceiro · publicação periódica do hash.</text>
  <text x="450" y="320" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">Sem âncora externa, quem controla o sistema recalcula a cadeia inteira e ninguém vê.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Trilha inviolável: encadeamento por hash torna a adulteração evidente; ancoragem externa (WORM) impede que o próprio dono do sistema reescreva a história.</p>
</div>

A **cadeia de hashes** torna a adulteração *evidente*: como cada evento inclui o hash do anterior, mexer no passado obriga a recalcular tudo dali em diante. Mas quem administra o sistema pode recalcular. Por isso a segunda peça: **ancorar** o estado da cadeia num lugar que o administrador não controla — armazenamento **WORM** (*write once, read many*, que fisicamente recusa sobrescrita), numa conta separada da operação, com verificação periódica automatizada. Note o encaixe com a §8: a **segregação de funções** vale também aqui — *quem opera o sistema não administra a trilha de auditoria dele.* A mesma cadeia de hashes é, aliás, a base do próprio ledger contábil; auditar a segurança e auditar o dinheiro são o mesmo problema estrutural.

Um último ponto de tensão, para fechar o ciclo com a §5: a trilha contém identificadores de pessoas, então **ela própria é dado pessoal** — sujeita a acesso restrito, a auditoria dos acessos à auditoria (sim, isso é recursivo e é necessário), e a mascaramento. Registrar *que* `cli-5519` fez algo com `acc-2207` é diferente de registrar o CPF do cliente. **Identificadores estáveis, não dados sensíveis.**

---

## 10. Detectar, responder e transformar decisões em regras que não regridem

### 10.1 Assumir o comprometimento: detecção e resposta

Toda a §4 e §6 terminaram com a mesma ideia: **o comprometimento vai acontecer; o que decide o tamanho do incidente é a rapidez de detecção e a limitação do alcance.** A indústria mede isso em duas métricas: **MTTD** (*mean time to detect* — quanto tempo um invasor fica lá antes de ser visto) e **MTTR** (*mean time to respond* — quanto até estar contido). Em incidente financeiro, cada minuto de MTTD é dinheiro que sai; a diferença entre 5 minutos e 5 dias é a diferença entre um incidente e uma falência.

A detecção se apoia no que já construímos: a **trilha de auditoria** (§9) alimenta um **SIEM** (*Security Information and Event Management*) — o sistema que correlaciona eventos de todas as fontes e dispara alertas. Exemplos de regras que fazem sentido *nesta* arquitetura:

- Rajada de `PIX_NEGADO_AUTORIZACAO` de um mesmo sujeito → alguém está sondando IDs (BOLA em andamento).
- Uso do **break-glass** ou de acesso JIT fora do horário → revisão imediata.
- Um workload fazendo chamada **negada por policy** que nunca fez antes → possível movimento lateral.
- Uso da chave de assinatura no KMS fora do padrão de volume → possível abuso da chave.
- Um segredo **negado** ou uma credencial dinâmica pedida de um IP incomum.

Note a elegância: os controles de **prevenção** (policy, autorização) geram, ao negar, o **sinal** que a **detecção** consome. Um controle que apenas bloqueia é meio controle; um que bloqueia *e* alerta é um sensor.

### 10.2 O runbook do incidente

Resposta a incidente improvisada às 3h da manhã produz decisões ruins. O processo precisa estar **escrito e ensaiado**:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 280" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9d-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
  </defs>
  <rect x="15" y="30" width="150" height="120" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="2"/>
  <text x="90" y="55" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7a5c00">1. Detectar</text>
  <text x="90" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">alerta do SIEM /</text>
  <text x="90" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">antifraude / cliente</text>
  <text x="90" y="114" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">classifica a gravidade</text>
  <rect x="185" y="30" width="150" height="120" rx="8" fill="#fee2e2" stroke="#b91c1c" stroke-width="2"/>
  <text x="260" y="55" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#991b1b">2. Conter</text>
  <text x="260" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">revogar tokens/sessões,</text>
  <text x="260" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">isolar workload, travar</text>
  <text x="260" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">conta, girar segredo</text>
  <rect x="355" y="30" width="150" height="120" rx="8" fill="#eef2ff" stroke="#4338ca" stroke-width="2"/>
  <text x="430" y="55" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#3730a3">3. Erradicar</text>
  <text x="430" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">achar a causa-raiz,</text>
  <text x="430" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">corrigir a falha,</text>
  <text x="430" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">remover persistência</text>
  <rect x="525" y="30" width="150" height="120" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2"/>
  <text x="600" y="55" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">4. Recuperar</text>
  <text x="600" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">restaurar serviço,</text>
  <text x="600" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">acionar devolução dos</text>
  <text x="600" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">valores, reconciliar</text>
  <rect x="695" y="30" width="190" height="120" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>
  <text x="790" y="55" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">5. Comunicar + aprender</text>
  <text x="790" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">notificar regulador e</text>
  <text x="790" y="92" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">titulares nos prazos legais,</text>
  <text x="790" y="106" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">post-mortem sem culpados,</text>
  <text x="790" y="120" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">virar teste automatizado</text>
  <line x1="165" y1="90" x2="183" y2="90" stroke="#4338ca" stroke-width="2" marker-end="url(#a9d-arrow)"/>
  <line x1="335" y1="90" x2="353" y2="90" stroke="#4338ca" stroke-width="2" marker-end="url(#a9d-arrow)"/>
  <line x1="505" y1="90" x2="523" y2="90" stroke="#4338ca" stroke-width="2" marker-end="url(#a9d-arrow)"/>
  <line x1="675" y1="90" x2="693" y2="90" stroke="#4338ca" stroke-width="2" marker-end="url(#a9d-arrow)"/>
  <rect x="15" y="180" width="870" height="85" rx="8" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="450" y="204" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7a5c00">Contenção só é rápida se foi PROJETADA antes</text>
  <text x="450" y="224" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">É possível revogar em minutos porque: tokens são curtos, segredos são dinâmicos, policies são código (dá para negar por PR),</text>
  <text x="450" y="242" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">workloads têm identidade própria (dá para isolar um sem parar os outros). Cada decisão das seções anteriores paga aqui.</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">O ciclo de resposta. A velocidade da contenção é decidida meses antes do incidente, no desenho.</p>
</div>

Um ponto regulatório, sem entrar em detalhe que muda: instituições financeiras brasileiras estão sujeitas a **normas de política de segurança cibernética** do Conselho Monetário Nacional e do Banco Central, que exigem, entre outras coisas, plano de resposta a incidentes, registro e análise de incidentes relevantes, controles de acesso, testes periódicos e comunicação de incidentes relevantes ao regulador; e a **LGPD** obriga a comunicar incidentes com risco relevante à autoridade (ANPD) e aos titulares em prazo razoável. **Os textos e prazos exatos mudam — consultem a versão vigente e o jurídico**; o que a arquitetura precisa garantir é a *capacidade*: saber rapidamente **quais dados foram afetados**, **de quem**, **desde quando** — e isso só é possível com trilha de auditoria completa (§9) e inventário de dados (§5).

### 10.3 Segurança que regride não é segurança: security fitness functions

Voltamos ao começo. O bug do Bruno foi corrigido — mas o que impede que alguém, seis meses depois, num refactor apressado, crie um endpoint novo `POST /pix/agendado` que recebe `contaOrigemId` **sem** a checagem? Nada, exceto a memória de quem viveu o incidente — e pessoas saem da empresa. **Decisão arquitetural que não é verificável automaticamente é uma sugestão.**

Uma **fitness function** é um teste automatizado que verifica se o sistema ainda possui uma propriedade arquitetural desejada. As **security fitness functions** transformam cada decisão desta aula em regra que **quebra o build** quando violada:

| Decisão de arquitetura | Fitness function (roda no CI ou em produção) | O que falha se regredir |
|---|---|---|
| Todo endpoint com ID de objeto autoriza ownership | Teste de arquitetura: métodos de controller com parâmetro `*Id` sem `@PreAuthorize`/policy → falha | Novo endpoint sem checagem (BOLA de volta) |
| Ownership realmente barra estranhos | Suíte adversarial: para cada endpoint, "usuário A × objeto de B" deve dar `403` **e** efeito zero | Autorização quebrada por refactor |
| Token com `aud`/`exp`/`iss` corretos | Testes: token expirado, audiência errada, emissor desconhecido, `alg=none` → todos `401` | Validação de JWT afrouxada |
| Escopo mínimo | Token com escopo insuficiente → `403` | Endpoint aceitando escopo "*" |
| Workload só fala com quem deve | Teste de policy: Notificações → Antifraude é **negado**; Pagamentos → Antifraude `/avaliar` é **permitido** | Policy frouxa demais |
| Nenhum segredo no repositório | Scanner de segredos no CI; bloqueia PR | Credencial em `application.yml` |
| Nenhum dado sensível em log | Teste que dispara fluxo real e varre logs/traces por padrões (CPF, `Bearer`, número de cartão) | Vazamento por observabilidade |
| Imagem só de origem confiável | Verificação de assinatura na admissão do cluster; SBOM sem CVE crítica | Dependência comprometida em produção |
| Trilha de auditoria íntegra | Job periódico verifica a cadeia de hashes e a âncora WORM | Adulteração do histórico |
| Rotação de segredos funciona | Exercício automatizado: rotaciona em ambiente de teste e verifica que nada quebrou | Rotação que "nunca foi testada" |

Reparem em algo importante na tabela: **as fitness functions cobrem tanto o que falha *silenciosamente* quanto o que falha *ruidosamente*.** O `403` errado (deveria ser 200) é barulhento; o `200` errado (deveria ser 403) é silencioso — e é exatamente o perigoso. Por isso a suíte **adversarial** — que assume o papel do atacante e verifica que o ataque *falha* — é o coração da lista: a maioria dos testes escritos por desenvolvedores verifica que **o caminho feliz funciona**; a segurança vive no *caminho infeliz*, que ninguém testa por hábito.

E o último passo do ciclo de incidente (§10.2, etapa 5) fecha o laço: **todo incidente real vira uma linha nesta tabela.** O incidente do Bruno gerou a primeira. É assim que a segurança da TechPix *acumula* — cada falha vira imunidade permanente, em vez de lembrança.

---

## 11. Trade-offs: segurança tem custo, e o arquiteto é quem o negocia

Seria desonesto encerrar sem a parte que todo material de segurança omite: **cada controle desta aula custa alguma coisa.** Segurança absoluta não existe; existe segurança *proporcional ao risco*, e a função do arquiteto é tornar os custos visíveis para que sejam escolhidos, não sofridos.

| Controle | Custo real | Onde dói | Como mitigar |
|---|---|---|---|
| **mTLS + mesh** | +1–3 ms por salto; memória/CPU por pod; complexidade operacional | Caminho crítico com orçamento de latência apertado (Pix) | Reuso de conexão; mesh *ambient*; mTLS só nos serviços críticos |
| **Autorização por recurso** | Uma consulta extra a cada operação | Endpoints de alto volume | Cache curto e invalidável do vínculo titular–conta; resposta no mesmo serviço |
| **Antifraude em linha** | Até ~100 ms no caminho crítico; falsos positivos | Experiência do cliente; conversão | Cache de *features*; graduar por valor; step-up em vez de bloquear |
| **Step-up / MFA** | Fricção; abandono | Pagamentos frequentes de baixo valor | Exigir só acima de risco; confiança em device conhecido |
| **Token curto** | Mais renovações; carga no servidor de identidade | Picos de tráfego | Refresh token; cache de chaves públicas para validação local |
| **KMS por operação** | Latência e dependência de disponibilidade do KMS | Cada leitura de campo cifrado | Envelope encryption; cache curto de DEK em memória |
| **Quatro olhos / JIT** | Lentidão em operações legítimas; ressentimento | Resposta a incidente | Break-glass com alerta; automação da aprovação rotineira |
| **Auditoria completa** | Volume de armazenamento; retenção de anos | Custo de infraestrutura | Camadas quente/fria; compressão; retenção por classe |

E dois **princípios de decisão** que atravessam a tabela:

1. **Proporcionalidade ao risco.** O rigor de cada controle deve acompanhar o dano possível. Consultar saldo não merece o mesmo peso que criar um Pix de R$ 50.000 para destinatário novo às 3h. Um sistema em que *tudo* exige step-up treina o usuário a aprovar sem ler — e isso derrota o controle.
2. **Falhar de forma previsível.** Todo controle precisa ter uma resposta decidida para "e se ele mesmo falhar?" — o **fail-open/fail-closed** da §7 generaliza. O KMS indisponível: recusar a operação (fail-closed) ou operar com DEK em cache por N minutos? A CA do mesh caiu: os pods continuam se falando com certificados ainda válidos, mas quando expirarem…? **Decida antes do incidente, em ADR, com números.**

### 11.1 Registrando a decisão: ADR-004

Fechando no ritual do curso — uma decisão arquitetural registrada de forma que o próximo engenheiro entenda *por quê*:

```markdown
# ADR-004 — Modelo de identidade e autorização da TechPix

Status: Aceito · Data: 2026-09-30

## Contexto
Incidente BOLA: usuário autenticado moveu recurso de terceiro com JWT válido.
Novo tráfego leste-oeste entre workloads sem autenticação de peer.

## Decisão
1. Autorização por recurso obrigatória em todo endpoint que aceita ID de objeto
   (ownership como piso; ABAC para limites contextuais; RBAC só para back-office).
2. Sujeito SEMPRE derivado do token; nunca do body.
3. Identidade de workload via certificado de vida curta (SPIFFE); mTLS entre
   serviços; token M2M com escopo mínimo; Token Exchange quando age em nome de usuário.
4. Default-deny em policy de plataforma; Kafka com ACL por tópico.
5. Segredos dinâmicos em cofre; proibido segredo estático em código/imagem/log.
6. Dados pessoais cifrados por titular (envelope encryption; crypto-shredding).
7. Trilha de auditoria estruturada, encadeada por hash, ancorada em WORM.
8. Cada controle acima com fitness function no CI.

## Consequências
+ Raio de explosão de qualquer comprometimento limitado por desenho.
+ Contenção em minutos (tokens curtos, segredos dinâmicos, policy como código).
− +1–3 ms/salto (mTLS); consulta extra de ownership; operação do mesh/KMS.
− Fricção de step-up e do quatro-olhos em operações sensíveis.

## Revisão
Reavaliar o mesh se a latência de p99 do caminho crítico exceder o orçamento
(alternativa: mTLS via biblioteca só nos serviços críticos), e a cada incidente.
```

---

## 12. Fechando: um Pix atravessando todas as camadas

Para amarrar tudo, sigam um único Pix legítimo — o da irmã do Bruno, R$ 50 — por todos os controles, e depois o Pix malicioso de R$ 4.800. Cada seta é uma pergunta diferente sendo feita, e cada camada assume que a anterior pode ter falhado:

<div style="margin:24px 0;padding:16px;border:1px solid #ddd;border-radius:10px;background:#fafafa;overflow-x:auto;">
<svg viewBox="0 0 900 470" style="max-width:100%;height:auto;display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="a9z-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#4338ca"/>
    </marker>
    <marker id="a9z-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/>
    </marker>
  </defs>
  <text x="450" y="20" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1a1a1a">Defesa em profundidade: a mesma requisição, dez perguntas</text>
  <rect x="20" y="35" width="860" height="42" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="35" y="60" font-family="sans-serif" font-size="12" fill="#333"><tspan font-weight="bold">① Edge:</tspan> TLS válido? Rate limit ok? Payload no tamanho e formato esperados?</text>
  <rect x="20" y="85" width="860" height="42" rx="6" fill="#fef9e7" stroke="#d4a017" stroke-width="1.5"/>
  <text x="35" y="110" font-family="sans-serif" font-size="12" fill="#333"><tspan font-weight="bold">② Gateway:</tspan> token com assinatura, iss, aud, exp válidos? Escopo grosso pix:create presente?</text>
  <rect x="20" y="135" width="860" height="42" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="35" y="160" font-family="sans-serif" font-size="12" fill="#333"><tspan font-weight="bold">③ Pagamentos (AuthZ de domínio):</tspan> o sujeito do token é o titular desta conta? (o passo que faltou ao Bruno)</text>
  <rect x="20" y="185" width="860" height="42" rx="6" fill="#eef2ff" stroke="#4338ca" stroke-width="1.5"/>
  <text x="35" y="210" font-family="sans-serif" font-size="12" fill="#333"><tspan font-weight="bold">④ Pagamentos (contexto):</tspan> valor exige step-up? acr do token basta? assinatura da transação confere?</text>
  <rect x="20" y="235" width="860" height="42" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="35" y="260" font-family="sans-serif" font-size="12" fill="#333"><tspan font-weight="bold">⑤ Plataforma (mesh):</tspan> Pagamentos apresentou certificado válido? A policy permite Pagamentos → Antifraude /avaliar?</text>
  <rect x="20" y="285" width="860" height="42" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="35" y="310" font-family="sans-serif" font-size="12" fill="#333"><tspan font-weight="bold">⑥ Antifraude:</tspan> o padrão parece legítimo? device conhecido? destino novo? velocidade normal? → ALLOW / step-up / DENY</text>
  <rect x="20" y="335" width="860" height="42" rx="6" fill="#f0fdf4" stroke="#166534" stroke-width="1.5"/>
  <text x="35" y="360" font-family="sans-serif" font-size="12" fill="#333"><tspan font-weight="bold">⑦ Ledger + dados:</tspan> identidade do workload autorizada a debitar? Dado sensível lido via KMS, com uso auditado?</text>
  <rect x="20" y="385" width="860" height="42" rx="6" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
  <text x="35" y="410" font-family="sans-serif" font-size="12" fill="#333"><tspan font-weight="bold">⑧ Saída (SPI):</tspan> mensagem assinada com chave do HSM. ⑨ Auditoria: evento imutável, encadeado. ⑩ SIEM: alguma anomalia?</text>
  <text x="450" y="452" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#b91c1c">O Pix do Bruno de R$ 4.800 morre no ③ com 403 — e, se o ③ tivesse falhado, ainda enfrentaria ④, ⑥ e ⑨/⑩ (limite, antifraude, detecção).</text>
</svg>
<p style="text-align:center;color:#777;font-size:13px;margin:8px 0 0;">Nenhuma camada é "a" segurança. Cada uma pega o que a anterior deixaria passar — e o custo de cada uma é aceito porque nenhuma delas é a única barreira.</p>
</div>

Para levar para casa, cinco frases:

1. **Autenticação estabelece identidade; autorização limita poder.** Um token válido diz *quem*, nunca *sobre o quê*. O `sub` vem do token; o objeto, do servidor; a comparação, do domínio.
2. **Cada workload é um sujeito, com identidade própria e privilégio mínimo.** Credencial global de backend é um único ponto de falha do cluster inteiro; mTLS autentica o canal, policy autoriza a ação — e **nenhum dos dois substitui a regra de negócio**.
3. **Assuma o comprometimento.** Tokens curtos, segredos dinâmicos, dados cifrados por titular, raio de explosão limitado: você não impede toda invasão, você reduz seu custo e seu tempo de vida.
4. **Nem toda fraude viola permissão.** O golpe autorizado só cai num controle baseado em *risco* — e ele é uma decisão de negócio com trade-off explícito entre fricção e perda.
5. **Provar é mais difícil do que proteger.** Sem trilha imutável, sem fitness functions e sem runbook ensaiado, a segurança é uma crença. **Segurança que não é verificada automaticamente regride.**

---

## Apêndice — Termos novos desta aula

| Termo | O que é |
|---|---|
| **Modelagem de ameaças** | Exercício de mapear ativos, adversários e fronteiras de confiança para decidir onde defender antes de escolher tecnologia. |
| **Fronteira de confiança** | Linha onde muda o nível de confiança e o controle sobre o dado; tudo que a cruza é entrada não confiável até ser validada. |
| **Zero Trust** | Premissa de "nunca confie, sempre verifique": nenhum chamador é confiável só por estar na rede; toda requisição carrega identidade verificada e passa por decisão explícita. |
| **STRIDE** | Mnemônico de seis categorias de ameaça: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege. |
| **AuthN / AuthZ / AAA** | Autenticação (quem é), autorização (o que pode), *accountability* (prova do que fez). |
| **JWT** | Token assinado com header, payload (claims) e assinatura; *stateless*, difícil de revogar antes do `exp`. |
| **Claims `iss`, `aud`, `sub`, `exp`, `acr`** | Emissor, audiência, sujeito, expiração e força da autenticação. |
| **OAuth 2.0 / OIDC** | OAuth: delegação de acesso a APIs (access token). OIDC: camada de identidade sobre OAuth (ID token). |
| **PKCE** | Extensão do fluxo *authorization code* que prova que quem troca o code é quem o pediu, usando um segredo por requisição e seu hash. |
| **Device binding** | Vincular a sessão a um par de chaves guardado no hardware do aparelho; transforma "este aparelho" em prova criptográfica. |
| **Step-up authentication** | Exigir autenticação mais forte no momento de uma operação de risco. |
| **Assinatura de transação / WYSIWYS** | O aparelho assina os campos da operação; o que o usuário vê é o que assina. Dá não-repúdio. |
| **BOLA / IDOR** | Trocar o identificador de um objeto e acessá-lo sem ser dono; falha de autorização por objeto. |
| **RBAC / ABAC / ReBAC** | Autorização por papel / por atributos e contexto / por relações entre entidades. |
| **PEP / PDP** | Ponto que aplica a política / ponto que a decide. |
| **Confused deputy** | Serviço intermediário usado para ampliar acesso porque o destino não distingue quem realmente pede. |
| **Client Credentials / Token Exchange** | Identidade M2M própria do serviço / novo token que carrega usuário (`sub`) e serviço intermediário (`act`). |
| **mTLS** | TLS com autenticação nos dois sentidos, por certificados de curta duração. |
| **SPIFFE** | Padrão de identidade de workload independente de IP (`spiffe://dominio/serviço`). |
| **Service mesh** | Plataforma com proxies (data plane) e cérebro (control plane) que entrega mTLS, políticas e telemetria fora do código de negócio. |
| **Default deny / menor privilégio / raio de explosão** | Tudo proibido até liberado / cada identidade só o necessário / estrago máximo de um comprometimento. |
| **Envelope encryption (KEK/DEK)** | Chave-mestra que nunca sai do cofre cifra chaves de dados, que cifram o dado. |
| **HSM / KMS** | Hardware resistente a violação que usa chaves sem revelá-las / serviço de gestão de chaves apoiado nele. |
| **Tokenização** | Substituir o dado sensível por token sem relação matemática; o real vive num cofre único. Reduz escopo de conformidade. |
| **Crypto-shredding** | "Apagar" dado pessoal destruindo a chave que o cifra, preservando um ledger imutável. |
| **Segredo dinâmico** | Credencial gerada sob demanda com TTL curto e acesso mínimo; expira sozinha. |
| **HMAC / replay / timing attack** | Assinatura por segredo compartilhado / reenvio de mensagem legítima capturada / vazamento por diferença de tempo de comparação. |
| **SBOM** | Inventário de todos os componentes de uma imagem/artefato. |
| **Antifraude (score, regras, sinais)** | Decisão por risco em tempo real sobre sinais de dispositivo, comportamento, velocidade e grafo. |
| **Fail-open / fail-closed** | Quando o controle falha, deixar passar / recusar. |
| **Conta laranja / structuring** | Conta usada para receber e dispersar produto de fraude / fracionar valores para ficar abaixo de limiares. |
| **Maker-checker / JIT / segregação / break-glass** | Quatro olhos / acesso temporário sob demanda / funções incompatíveis em pessoas distintas / acesso de emergência ruidoso e temporário. |
| **Trilha de auditoria / cadeia de hashes / WORM** | Registro estruturado e obrigatório / encadeamento que torna adulteração evidente / armazenamento que recusa sobrescrita. |
| **SIEM / MTTD / MTTR** | Correlação de eventos e alertas / tempo médio para detectar / tempo médio para conter. |
| **Security fitness function** | Teste automatizado que verifica que uma propriedade de segurança arquitetural continua valendo; quebra o build quando regride. |

## Apêndice — Fecho e gancho

Construímos, nesta aula, uma defesa em camadas para um sistema em que o erro custa dinheiro irreversível: identidade forte, autorização por recurso, identidade de workload, dados cifrados por titular, segredos que expiram, decisão por risco, controle de insiders, auditoria à prova de adulteração e regras automatizadas que impedem a regressão. E, como toda boa arquitetura, cada camada veio com um custo declarado.

Mas fica um sintoma que **nenhum desses controles resolve** — e que qualquer arquiteto que já operou um sistema com essa quantidade de camadas conhece: agora cada requisição atravessa **proxy, policy, autorização, antifraude, KMS e trilha de auditoria**. Cada uma é rápida. Somadas, são dezenas de saltos e centenas de milissegundos. Quando o cliente disser *"o Pix demora"*, o painel de segurança estará todo verde — porque segurança verifica se o acesso foi **permitido**, não **quanto tempo cada camada custou**.

> Segurança acrescenta camadas. Camadas acrescentam latência. E **latência que ninguém enxerga** não é problema de segurança — é problema de observabilidade.

---

[← Aula 8](aula8-conteudo-completo.md) · [Índice](index.md)
