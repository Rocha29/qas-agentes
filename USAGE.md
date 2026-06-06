# 🚀 Como Usar os Agentes — Guia Prático

## Ativando um Agente no Claude Code

```bash
# Opção 1: via flag no Claude Code
claude --system-prompt agents/ARIA.md "Cria um teste E2E para o fluxo de login"

# Opção 2: via CLAUDE.md do projeto
# Adicione no início do seu CLAUDE.md:
# @include agents/ARIA.md

# Opção 3: copiar o conteúdo diretamente no system prompt
cat agents/NEXUS.md | pbcopy   # macOS — cola no Claude
```

---

## 🎯 Qual agente usar em cada situação?

| Situação | Agente |
|----------|--------|
| "Criar teste E2E no Playwright" | **ARIA** 🌐 |
| "Automatizar teste no app mobile" | **KAUÊ** 📱 |
| "Testar endpoint REST com Java" | **NEXUS** 🔌 |
| "Medir performance da API" | **FLUX** ⚡ |
| "Qual framework usar? Como estruturar?" | **ATLAS** 🏗️ |
| "O que estamos deixando de testar?" | **HELIX** 🔭 |
| "Como apresentar qualidade para o gestor?" | **SIGMA** 💼 |

---

## 🃏 Exemplo de Workflow Completo no Kanban

```
Tarefa: "Implementar testes para o novo fluxo de checkout"

Board:
┌──────────┬─────────────────────────────┬───────────────────────────┐
│  BACKLOG │       IN PROGRESS           │          DONE             │
├──────────┼─────────────────────────────┼───────────────────────────┤
│          │ 🔭 HELIX                    │                           │
│          │ Explorando checkout         │                           │
│          │ → Mapeou 14 cenários        │                           │
│          ├─────────────────────────────┤                           │
│          │ 🏗️ ATLAS                    │                           │
│          │ Definindo arquitetura       │                           │
│          │ → POM + Feature Actions     │                           │
│          ├─────────────────────────────┤                           │
│          │ 🌐 ARIA                     │                           │
│          │ Automação web checkout      │                           │
│          │ → 8 testes Playwright       │                           │
│          ├─────────────────────────────┤                           │
│          │ 🔌 NEXUS                    │                           │
│          │ Testes API /checkout        │                           │
│          │ → 12 testes RestAssured     │                           │
│          ├─────────────────────────────┤                           │
│          │ ⚡ FLUX                     │                           │
│          │ Load test /checkout         │                           │
│          │ → p95: 380ms ✅             │                           │
│          ├─────────────────────────────┤                           │
│          │ 💼 SIGMA                    │                           │
│          │ Relatório para liderança    │                           │
│          │ → Dashboard atualizado      │                           │
└──────────┴─────────────────────────────┴───────────────────────────┘
```

---

## 📋 Receita de Bolo — Validação de Cada Agente

### 🌐 ARIA — Validação
```bash
# Tarefa de validação
"Crie um teste Playwright que:
1. Acesse uma página de login
2. Preencha email e senha
3. Submeta o formulário
4. Valide o redirecionamento
Use Page Object Model e TypeScript."

# Critérios de avaliação:
✅ Usou getByRole/getByLabel (não CSS/XPath)
✅ Sem sleep() ou waitForTimeout()
✅ Criou Page Object separado
✅ Assertions claras com mensagens de erro
✅ Configuração em playwright.config.ts
```

### 📱 KAUÊ — Validação
```bash
# Tarefa de validação
"Crie um flow Maestro que:
1. Abra o app
2. Faça login
3. Navegue para o perfil
4. Valide o nome do usuário"

# Critérios de avaliação:
✅ Sem sleep() — usou assertVisible com await nativo
✅ YAML legível e comentado
✅ AppId correto no topo
✅ Sugeriu config.yaml para variáveis
✅ Mencionou execução via Maestro Cloud
```

### 🔌 NEXUS — Validação
```bash
# Tarefa de validação
"Escreva testes RestAssured para o endpoint POST /users:
- Happy path
- Email duplicado (409)
- Payload sem campo obrigatório (422)
- Sem autenticação (401)"

# Critérios de avaliação:
✅ Given/When/Then em todos os testes
✅ Validou status code E body
✅ JSON Schema em pelo menos um teste
✅ Base URL via variável de ambiente
✅ Nomes de método em PT-BR descritivos
```

### ⚡ FLUX — Validação
```bash
# Tarefa de validação
"Crie um script k6 para:
- 50 usuários por 3 minutos
- Endpoint GET /products
- SLA: p95 < 500ms, erro < 1%"

# Critérios de avaliação:
✅ Stages definidos (ramp-up, sustentado, ramp-down)
✅ Thresholds configurados
✅ check() com validação de status E tempo
✅ Mencionou integração com Grafana
✅ Comando de execução em modo CI
```

### 🏗️ ATLAS — Validação
```bash
# Tarefa de validação
"Nosso time tem 3 QAs, usa Java, 
faz testes manuais hoje. 
Qual arquitetura implementar nos próximos 3 meses?"

# Critérios de avaliação:
✅ Perguntou sobre contexto antes de responder
✅ Recomendou evolução incremental (não big bang)
✅ Justificou escolhas técnicas com prós/contras
✅ Incluiu CI/CD no plano
✅ Definiu métricas de sucesso por fase
```

### 🔭 HELIX — Validação
```bash
# Tarefa de validação
"Explore estes cenários para o formulário de cadastro:
campos: nome, email, telefone, CEP"

# Critérios de avaliação:
✅ Aplicou pelo menos 3 heurísticas
✅ Testou boundary values (max chars, especiais)
✅ Pensou em segurança (XSS, SQL injection)
✅ Considerou acessibilidade
✅ Documentou em formato de charter
```

### 💼 SIGMA — Validação
```bash
# Tarefa de validação
"O gestor quer saber se devemos 
investir 200h em automação de regressão.
Como apresentar isso?"

# Critérios de avaliação:
✅ Calculou ROI com números reais
✅ Apresentou em formato executivo
✅ Incluiu riscos de não automatizar
✅ Propôs métricas de acompanhamento
✅ Estimativa de break-even clara
```

---

## 🔌 Configuração MCP para os Agentes

```json
// .claude/mcp.json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<seu-token>"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  }
}
```

---

## 📁 Estrutura Final do Projeto

```
qa-agents/
├── README.md                    ← visão geral
├── USAGE.md                     ← este arquivo
├── agents/
│   ├── ARIA.md                  ← 🌐 Web
│   ├── KAUE.md                  ← 📱 Mobile
│   ├── NEXUS.md                 ← 🔌 API
│   ├── FLUX.md                  ← ⚡ Performance
│   ├── ATLAS.md                 ← 🏗️ Arquitetura
│   ├── HELIX.md                 ← 🔭 Exploratório
│   └── SIGMA.md                 ← 💼 Negócio
├── knowledge_base/              ← (próximo passo: base RAG)
│   ├── julio-de-lima/
│   ├── fernando-papito/
│   ├── qazando/
│   └── vinicius-pessoni/
└── tools/
    ├── collect.py               ← (próximo passo: coleta YouTube)
    └── mcp.json                 ← configuração MCP
```
