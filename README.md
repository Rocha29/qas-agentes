# QA Agents — Time de Agentes Especializados em Qualidade de Software

<p align="center">
  <img src="assets/agentes.png" alt="QA Agents — escritório pixel art" width="600"/>
</p>

Base de conhecimento e system prompts para **8 agentes QA especializados**, construídos sobre o conteúdo de referências brasileiras de qualidade de software e validados em uma POC completa com automação Web, API e Performance.

---

## O Time de Agentes

| Agente | Área | Arquivo | Tecnologias principais |
|--------|------|---------|----------------------|
| **SIGMA-LEAD** | Líder de Planejamento QA | `agents/SIGMA-LEAD.md` | Orquestra o time, lê histórias, monta o Plano de Sprint QA |
| **ARIA-WEB** | Automação Web & WebView | `agents/ARIA-WEB.md` | Playwright, Cypress, Robot Framework |
| **KAUE-MOBILE** | Automação Mobile & WebView | `agents/KAUE-MOBILE.md` | Maestro, Appium, Robot Framework AppiumLibrary |
| **NEXUS-API** | Testes de API & BFF | `agents/NEXUS-API.md` | RestAssured, Postman, k6 |
| **FLUX-PERF** | Performance & Observabilidade | `agents/FLUX-PERF.md` | k6, JMeter, Grafana |
| **ATLAS-ARCH** | Arquitetura de Qualidade | `agents/ATLAS-ARCH.md` | Estratégia, CI/CD, métricas |
| **HELIX-EXPLORE** | Exploratório & Tendências | `agents/HELIX-EXPLORE.md` | IA aplicada, testing emergente |
| **SIGMA-BIZ** | Negócios & Qualidade Estratégica | `agents/SIGMA-BIZ.md` | Relatórios executivos, OKRs de QA |

---

## Como Usar os Agentes

### Claude Code (CLI)

```bash
# Ativar um agente em qualquer projeto existente
claude --system-prompt /caminho/para/qa-agents/agents/ARIA.md

# Exemplo real dentro do seu projeto
claude --system-prompt ~/qa-agents/agents/NEXUS.md "Revise os testes de API deste projeto"
```

---

### GitHub Copilot — receita de bolo

**Funciona em:** VS Code, JetBrains, Visual Studio, GitHub.com, GitHub Mobile.

**Passo a passo:**

1. No projeto onde você quer o agente, crie a pasta `.github/` se não existir
2. Crie o arquivo `.github/copilot-instructions.md`
3. Cole o conteúdo do agente desejado (ex: `agents/ARIA.md`) nesse arquivo
4. Pronto — o Copilot Chat vai seguir o persona em todas as conversas do repo

```bash
# Exemplo: ativar ARIA (Web) em um projeto existente
mkdir -p meu-projeto/.github
cp ~/qa-agents/agents/ARIA.md meu-projeto/.github/copilot-instructions.md
```

**Dica importante:** O Copilot Code Review lê apenas os primeiros **4.000 caracteres** do arquivo. Se o prompt do agente for longo, coloque as instruções mais críticas no topo.

O arquivo `.github/copilot-instructions.md` é enviado automaticamente em toda mensagem do Copilot Chat — funciona como um system prompt persistente para o repositório.

---

### Devin (Cognition AI) — receita de bolo

> Não existe um "Devin CLI" oficial. O mecanismo correto é via **Playbook** (para tarefas repetidas) ou **Knowledge** (para contexto permanente de repo).

#### Opção 1 — Playbook (recomendado para tarefas QA específicas)

1. Acesse [preview.devin.ai](https://preview.devin.ai) → **Playbooks** → **New Playbook**
2. Cole o conteúdo do agente desejado (ex: `agents/FLUX.md`) no campo de instruções
3. Dê um nome (ex: `QA Performance — FLUX`) e salve
4. Na hora de usar: no prompt box, digite `!` e selecione o Playbook

**Alternativa rápida:** salve o conteúdo do agente como `flux-playbook.md` e arraste o arquivo para o chat do Devin ao iniciar uma sessão.

#### Opção 2 — Knowledge (contexto permanente por repo)

1. Acesse **Knowledge** → **New Knowledge**
2. Cole o conteúdo do agente
3. Em **Scope**, selecione o repositório específico onde quer que o agente seja sempre injetado
4. Salve — o Devin vai usar esse contexto automaticamente em todas as sessões daquele repo

---

### Qual agente usar em cada situação?

| Situação | Agente recomendado |
|----------|--------------------|
| Escrever/revisar testes E2E Web | ARIA |
| Testar APIs REST / contratos | NEXUS |
| Testes mobile (Android/iOS) | KAUÊ |
| Performance e carga | FLUX |
| Definir estratégia de QA | ATLAS |
| Exploratório, edge cases | HELIX |
| Relatório executivo / métricas | SIGMA |

Consulte `USAGE.md` para a matriz completa de decisão e checklists de validação por agente.

---

## VS Code — Setup para usar os Agentes

Configure o VS Code uma vez e qualquer projeto passa a ter o agente certo ativado automaticamente.

---

### Passo 1 — Extensões de IA recomendadas

| Extensão | ID no Marketplace | Para que serve |
|----------|------------------|----------------|
| **GitHub Copilot** | `GitHub.copilot` | Autocomplete e chat com suporte a instruções de repo (`.github/copilot-instructions.md`) |
| **GitHub Copilot Chat** | `GitHub.copilot-chat` | Chat contextual inline — ideal para conversar com o agente dentro do editor |
| **Pixel Agents** | *(sua extensão atual)* | Visualização e gerenciamento de agentes no estilo pixel art |
| **Continue** | `Continue.continue` | Chat local/remoto com qualquer LLM; suporta system prompt por projeto via `config.json` — ótima alternativa open-source ao Copilot |
| **Cline** | `saoudrizwan.claude-dev` | Agente autônomo que lê, edita e executa código; integra com Claude API diretamente |
| **Roo Code** | `RooVeterinaryInc.roo-cline` | Fork do Cline com modos especializados por papel (Architect, Code, Debug, Ask) |
| **GitLens** | `eamodio.gitlens` | Essencial para QA: blame, histórico de arquivo, comparação entre branches |
| **Playwright Test for VS Code** | `ms-playwright.playwright` | Runner visual de testes Playwright com debug point-and-click |
| **Extension Pack for Java** | `vscjava.vscode-java-pack` | Java + Gradle para o projeto `lojinha-api-tests` |
| **Robot Framework LSP** | `robocorp.robotframework-lsp` | Autocomplete e diagnóstico para arquivos `.robot` |

---

### Passo 2 — Ativar um agente por projeto (Copilot)

```bash
# Dentro do projeto onde quer o agente:
mkdir -p .github
cp ~/qa-agents/agents/ARIA.md .github/copilot-instructions.md
```

A partir daí o Copilot Chat daquele repo responde como ARIA (ou o agente que você copiar). Nenhuma configuração adicional necessária.

---

### Passo 3 — Ativar um agente no Continue (open-source)

O **Continue** permite definir um system prompt por perfil no arquivo `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "NEXUS — API QA Agent",
      "provider": "anthropic",
      "model": "claude-sonnet-4-6",
      "apiKey": "sua-chave-aqui",
      "systemMessage": "<cole aqui o conteúdo de agents/NEXUS.md>"
    }
  ]
}
```

Você pode ter um perfil por agente e trocar pelo seletor de modelo no chat.

---

### Passo 4 — Ativar um agente no Cline / Roo Code

O **Cline** e o **Roo Code** têm um campo de **Custom Instructions** direto nas configurações da extensão:

1. Abra as configurações da extensão (`Ctrl+,` → busque "Cline" ou "Roo")
2. Cole o conteúdo do agente desejado em **Custom Instructions**
3. Selecione o modelo (`claude-sonnet-4-6` recomendado)

O **Roo Code** vai além: tem modos separados por papel (Architect, Code, Debug, Ask) — ideal para mapear cada modo a um agente diferente.

---

### Dica — workspace settings por projeto

Salve as preferências de agente por projeto criando `.vscode/settings.json`:

```json
{
  "continue.defaultModel": "NEXUS — API QA Agent",
  "github.copilot.chat.codeGeneration.useInstructionFiles": true
}
```

Assim cada repositório abre já com o agente certo sem você precisar reconfigurar nada.

---

## Fontes de Conhecimento

Os prompts dos agentes são fundamentados no conteúdo de cinco referências brasileiras de QA:

### Júlio de Lima
- Estratégia de testes, API REST (RestAssured + Java), Postman, BDD/Cucumber, Performance com JMeter, IA aplicada a testes
- YouTube: `@JuliodeLimas` | Site: juliodelima.com.br

### Fernando Papito
- Playwright, Cypress, Robot Framework, CI/CD, Page Objects, Feature Actions, arquitetura de frameworks, fintechs
- YouTube: Fernando Papito | Site: fernandopapito.com

### QAzando
- Automação mobile (iFood, IBM, Banco Neon), automação web, API, gestão de equipes QA, diversidade de stacks
- YouTube: QAzando | Site: qazando.com.br

### Vinícius Pessoni
- Java + RestAssured + JUnit 5 + Gradle (níveis jr/pl/sr), CTFL, liderança técnica, carreira internacional
- YouTube: pessonizando | GitHub: github.com/vinnypessoni

### Walmyr (Talking About Testing)
- Cypress, Playwright, práticas modernas de automação, cultura de qualidade, conteúdo em português e inglês
- YouTube: Talking About Testing | Site: talkingabouttesting.com

---

## Estrutura do Repositório

```
qa-agents/
├── agents/                        # System prompts dos 7 agentes
│   ├── ARIA.md
│   ├── KAUE.md
│   ├── NEXUS.md
│   ├── FLUX.md
│   ├── ATLAS.md
│   ├── HELIX.md
│   └── SIGMA.md
│
├── knowledge_base/                # Base de conhecimento por autor
│   ├── julio-de-lima/
│   ├── fernando-papito/
│   ├── qazando/
│   ├── vinicius-pessoni/
│   ├── walmyr-talkingabouttesting/
│   └── lojinha/                   # Contexto da aplicação de referência
│
├── lojinha-tests/                 # Testes E2E Web — Playwright + TypeScript
│   ├── pages/                     # Page Objects
│   ├── tests/                     # Specs
│   ├── playwright.config.ts
│   └── package.json
│
├── lojinha-api-tests/             # Testes de API — RestAssured + Java 17 + JUnit 5
│   ├── src/test/java/
│   ├── build.gradle
│   └── gradlew
│
├── lojinha-performance/
│   ├── k6/                        # Scripts de performance k6
│   │   ├── smoke.js
│   │   ├── stress.js
│   │   ├── login-load.js
│   │   └── produtos-load.js
│   └── jmeter/                    # Planos de teste JMeter (.jmx)
│
├── mobile/
│   └── android/
│       ├── maestro/flows/         # Flows YAML para Maestro
│       └── robot/                 # Robot Framework + AppiumLibrary
│
├── reports/                       # Relatórios da POC
├── USAGE.md                       # Matriz de decisão e checklists
└── CLAUDE.md                      # Instruções para o Claude Code
```

---

## Pré-requisitos

| Ferramenta | Versão mínima | Usado em |
|------------|--------------|----------|
| Node.js | 18+ | lojinha-tests (Playwright) |
| Java JDK | 17 | lojinha-api-tests (Gradle) |
| k6 | latest | lojinha-performance/k6 |
| JMeter | 5.6+ | lojinha-performance/jmeter |
| Python | 3.9+ | mobile/android/robot |
| Appium | 2.x | mobile/android/robot |
| Maestro CLI | latest | mobile/android/maestro |
| Android SDK / emulador | API 30+ | mobile (ambos) |

---

## Como Rodar os Projetos

### lojinha-tests — Playwright (Web E2E)

```bash
cd lojinha-tests
npm install
npx playwright install chromium

# Rodar todos os testes
npx playwright test

# Rodar com UI interativa
npx playwright test --ui

# Gerar relatório HTML
npx playwright show-report
```

### lojinha-api-tests — RestAssured + Java 17

```bash
cd lojinha-api-tests

# Rodar todos os testes
./gradlew test

# Relatório HTML gerado em:
# build/reports/tests/test/index.html
```

### lojinha-performance/k6

```bash
cd lojinha-performance/k6

# Smoke test (verificação rápida)
k6 run smoke.js

# Load test — login
k6 run login-load.js

# Load test — produtos
k6 run produtos-load.js

# Stress test
k6 run stress.js
```

### lojinha-performance/jmeter

```bash
cd lojinha-performance/jmeter

# Rodar via script (requer JMETER_HOME configurado)
chmod +x run.sh
./run.sh

# Ou diretamente com JMeter CLI
jmeter -n -t lojinha-smoke.jmx -l results/smoke.jtl -e -o results/report
```

### mobile/android/maestro

```bash
# Instalar Maestro CLI
curl -Ls "https://get.maestro.mobile.dev" | bash

# Iniciar emulador Android e instalar o APK antes de rodar

# Rodar um flow específico
maestro test mobile/android/maestro/flows/login.yaml

# Rodar todos os flows
maestro test mobile/android/maestro/flows/
```

### mobile/android/robot — Robot Framework + AppiumLibrary

```bash
cd mobile/android/robot

# Instalar dependências Python
pip install robotframework robotframework-appiumlibrary

# Iniciar o servidor Appium antes de rodar
appium

# Rodar os testes
robot tests/login_tests.robot
robot tests/

# Resultados gerados em results/
```

---

## Resultados da POC

A POC demonstrou automação ponta a ponta com três agentes (ARIA, NEXUS, FLUX) em uma única sessão:

| Camada | Tecnologia | Testes | Resultado |
|--------|-----------|--------|-----------|
| Web E2E | Playwright + TypeScript | 17 | 17/17 passando |
| API | RestAssured + Java 17 | 17 | 17/17 passando |
| Performance | k6 + JMeter | 2 suítes | 1 verde / 1 com alerta de SLA |

Relatório executivo completo: `reports/relatorio-poc-final.md`

---

## Contribuindo

1. Cada agente tem seu prompt em `agents/<NOME>.md`
2. Material de referência vai em `knowledge_base/<autor>/`
3. Novos projetos de teste seguem a estrutura existente por camada
4. Consulte `CLAUDE.md` antes de trabalhar no repo com Claude Code
