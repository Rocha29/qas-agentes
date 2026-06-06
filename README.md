# QA Agents — Time de Agentes Especializados em Qualidade de Software

Base de conhecimento e system prompts para 7 agentes QA especializados, construídos sobre o conteúdo de referências brasileiras de qualidade de software e validados em uma POC completa com automação Web, API e Performance.

---

## O Time de Agentes

| Agente | Área | Arquivo | Tecnologias principais |
|--------|------|---------|----------------------|
| **ARIA** | Automação Web | `agents/ARIA.md` | Playwright, Cypress, Robot Framework |
| **KAUÊ** | Automação Mobile | `agents/KAUE.md` | Maestro, Appium, Robot Framework AppiumLibrary |
| **NEXUS** | Testes de API | `agents/NEXUS.md` | RestAssured, Postman, k6 |
| **FLUX** | Performance & Observabilidade | `agents/FLUX.md` | k6, JMeter, Grafana |
| **ATLAS** | Arquitetura de Qualidade | `agents/ATLAS.md` | Estratégia, CI/CD, métricas |
| **HELIX** | Exploratório & Tendências | `agents/HELIX.md` | IA aplicada, testing emergente |
| **SIGMA** | Negócios & Qualidade Estratégica | `agents/SIGMA.md` | Relatórios executivos, OKRs de QA |

---

## Como Ativar um Agente

```bash
# Ativar diretamente no Claude Code CLI
claude --system-prompt agents/ARIA.md

# Ou carregar como contexto dentro de uma sessão
cat agents/NEXUS.md | pbcopy   # macOS — cole no campo de system prompt
```

Consulte `USAGE.md` para a matriz completa de decisão (qual agente para qual tarefa) e checklists de validação por agente.

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
