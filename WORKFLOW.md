# WORKFLOW — Como usar os Agentes QA no dia a dia

---

## Os 8 Agentes

| Agente | Arquivo | Especialidade |
|--------|---------|--------------|
| **SIGMA-LEAD** | `agents/SIGMA-LEAD.md` | Lê a história, monta o Plano de Sprint QA, distribui para os agentes certos |
| **ARIA-WEB** | `agents/ARIA-WEB.md` | Testes E2E Web (Playwright, Cypress) e WebView |
| **KAUE-MOBILE** | `agents/KAUE-MOBILE.md` | Testes Mobile Android, iOS e WebView (Maestro, Appium, Robot) |
| **NEXUS-API** | `agents/NEXUS-API.md` | Testes de API REST e BFF (RestAssured, Postman, k6) |
| **FLUX-PERF** | `agents/FLUX-PERF.md` | Performance e carga (k6, JMeter) — valida SLAs |
| **ATLAS-ARCH** | `agents/ATLAS-ARCH.md` | Arquitetura de qualidade — entra em histórias grandes ou de alto risco |
| **HELIX-EXPLORE** | `agents/HELIX-EXPLORE.md` | Testes exploratórios, edge cases, cenários não mapeados |
| **SIGMA-BIZ** | `agents/SIGMA-BIZ.md` | Relatório executivo, métricas de negócio, comunicação com gestão |

---

## Modo 1 — Orquestrado (SIGMA-LEAD decide tudo)

Use quando a história acabou de chegar e você quer o plano completo antes de começar.

### Passo 1 — Salve a história

Crie o arquivo na pasta `historias/`:
```
historias/HIST-042.md
```

Use um dos templates:
- `historias/_template-negocio.md` — histórias do time de negócio (com BDD)
- `historias/_template-tecnico.md` — histórias técnicas do Tech Lead (BFF, API, infra)

### Passo 2 — Ative o SIGMA-LEAD

```bash
# Claude Code CLI
claude --system-prompt agents/SIGMA-LEAD.md

# Copilot → .github/copilot-instructions.md
cp agents/SIGMA-LEAD.md .github/copilot-instructions.md

# Continue / Cline → cole o conteúdo em Custom Instructions
```

### Passo 3 — Informe o número da história

No chat, simplesmente digite:
```
HIST-042
```

O SIGMA-LEAD vai:
1. Ler `historias/HIST-042.md`
2. Identificar o tipo (negócio ou técnica)
3. Mapear as superfícies afetadas (web, mobile, API, WebView...)
4. Completar BDDs faltantes
5. Retornar o **Plano de Sprint QA** com agentes, ordem e mandato de cada um

### Passo 4 — Execute os agentes na ordem indicada

O SIGMA-LEAD vai indicar algo como:

```
1. NEXUS-API  → testar e validar o contrato do endpoint
2. FLUX-PERF  → validar SLA do endpoint
3. ARIA-WEB   → cobrir os fluxos web com Playwright
4. KAUE-MOBILE → cobrir os fluxos Android e iOS
5. SIGMA-BIZ  → gerar relatório executivo da história
```

Ative cada agente com o arquivo `.md` correspondente e passe a instrução específica que o SIGMA-LEAD gerou.

---

## Modo 2 — Direto (você sabe quem chamar)

Use quando você já sabe qual camada precisa cobrir.

```bash
# Preciso cobrir o BFF novo
claude --system-prompt agents/NEXUS-API.md

# Preciso automatizar o fluxo de login no Android
claude --system-prompt agents/KAUE-MOBILE.md

# Preciso validar performance do checkout
claude --system-prompt agents/FLUX-PERF.md

# Preciso cobrir a tela de produto no web
claude --system-prompt agents/ARIA-WEB.md
```

No chat, cole o contexto da história ou descreva o que precisa diretamente — sem precisar do SIGMA-LEAD.

---

## Fluxo de decisão rápida

```
Nova história chegou?
        │
        ▼
É grande ou você não sabe por onde começar?
    Sim → MODO ORQUESTRADO (SIGMA-LEAD)
    Não → MODO DIRETO (agente específico)
        │
        ├── Tem tela web?        → ARIA-WEB
        ├── Tem app mobile?      → KAUE-MOBILE
        ├── Tem API ou BFF?      → NEXUS-API
        ├── Tem SLA ou carga?    → FLUX-PERF
        ├── Tem edge cases?      → HELIX-EXPLORE
        ├── História complexa?   → ATLAS-ARCH
        └── Precisa reportar?    → SIGMA-BIZ
```

---

## WebView — quando dois agentes atuam juntos

Quando a história envolve WebView embutido em app mobile:

| Agente | Responsabilidade |
|--------|-----------------|
| **KAUE-MOBILE** | Navegar até o ponto onde o WebView aparece, fazer a troca de contexto (NATIVE → WEBVIEW) |
| **ARIA-WEB** | Cobrir o conteúdo dentro do WebView (formulários, navegação, validações) |

Ative os dois agentes em sequência: KAUE-MOBILE primeiro (contexto nativo), ARIA-WEB em seguida (conteúdo web).

---

## Estrutura da pasta `historias/`

```
historias/
├── _template-negocio.md   ← template para histórias do time de negócio
├── _template-tecnico.md   ← template para histórias técnicas do Tech Lead
├── HIST-001.md            ← exemplo preenchido
├── HIST-002.md
└── HIST-NNN.md
```

**Convenção de nome:** `HIST-[número com 3 dígitos].md`
Se sua ferramenta usa outro prefixo (ex: `PD-`, `PROJ-`), mantenha o mesmo — SIGMA-LEAD aceita qualquer número informado.

---

## Ordem recomendada de execução dos agentes

```
ATLAS-ARCH    ← só se história for grande / decisão de arquitetura necessária
      │
NEXUS-API     ← API/BFF precisa estar estável antes dos testes de interface
      │
FLUX-PERF     ← valida SLA da API enquanto ainda é barato corrigir
      │
ARIA-WEB      ← interface web quando a API já está testada
      │
KAUE-MOBILE   ← app mobile quando web e API estão validadas
      │
HELIX-EXPLORE ← exploratório após os fluxos principais cobertos
      │
SIGMA-BIZ     ← relatório executivo da história para a gestão
```

---

## Exemplos de uso rápido

### Exemplo 1 — História de negócio com BDD

```
1. Preencha: historias/HIST-015.md (use _template-negocio.md)
2. Ative: claude --system-prompt agents/SIGMA-LEAD.md
3. Digite: HIST-015
4. Receba o plano e siga a ordem dos agentes
```

### Exemplo 2 — Tech Lead criou um BFF novo

```
1. Preencha: historias/HIST-022.md (use _template-tecnico.md)
   → inclua os endpoints, SLA, consumidores (web/Android/iOS)
2. Ative: claude --system-prompt agents/SIGMA-LEAD.md
3. Digite: HIST-022
4. SIGMA-LEAD vai gerar os BDDs técnicos e acionar NEXUS-API + FLUX-PERF
```

### Exemplo 3 — Correção rápida de bug em endpoint

```
# Direto ao ponto — sem orquestração
claude --system-prompt agents/NEXUS-API.md
> "O endpoint POST /produtos está retornando 500 quando o campo 'preco' é zero.
>  Escreva um teste que reproduza esse bug e valide a correção."
```
