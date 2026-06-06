# Lojinha — Ambiente, Dependências e Comandos

## Pré-requisitos do Sistema

| Ferramenta | Versão mínima | Verificar com |
|-----------|--------------|---------------|
| Node.js | 18+ | `node --version` |
| Java | 17 | `java --version` |
| Gradle | 8.7 (wrapper incluso) | `./gradlew --version` |
| k6 | qualquer recente | `k6 version` |
| JMeter | 5.x | `jmeter --version` |
| Playwright browsers | automático | `npx playwright install` |

---

## Projeto 1 — lojinha-tests/ (Playwright TypeScript)

### Dependências (package.json)

```json
{
  "devDependencies": {
    "@playwright/test": "^1.60.0",
    "typescript": "^6.0.3"
  }
}
```

### Setup

```bash
cd lojinha-tests
npm install
npx playwright install chromium   # instalar browser
```

### Executar testes

```bash
# Todos os testes
npx playwright test

# Só login
npx playwright test tests/login.spec.ts

# Só produto
npx playwright test tests/produto.spec.ts

# Com interface visual (headed)
npx playwright test --headed

# Relatório HTML após execução
npx playwright show-report
```

### Configuração (playwright.config.ts)

```typescript
baseURL:    'http://165.227.93.41/lojinha-web/v2/'  // com barra final
testDir:    './tests'
browser:    chromium (Desktop Chrome)
parallel:   false (testes sequenciais — estado compartilhado)
retries:    0
screenshot: only-on-failure
video:      retain-on-failure
trace:      retain-on-failure
```

---

## Projeto 2 — lojinha-api-tests/ (RestAssured Java 17)

### Dependências (build.gradle)

```groovy
testImplementation 'io.rest-assured:rest-assured:5.4.0'
testImplementation 'io.rest-assured:json-path:5.4.0'
testImplementation 'io.rest-assured:json-schema-validator:5.4.0'
testImplementation 'org.junit.jupiter:junit-jupiter:5.10.2'
testImplementation 'com.fasterxml.jackson.core:jackson-databind:2.17.0'
testImplementation 'org.assertj:assertj-core:3.25.3'
testRuntimeOnly  'org.junit.platform:junit-platform-launcher'
```

### Setup

```bash
cd lojinha-api-tests
# Gradle wrapper já está incluído — não precisa instalar Gradle separado
chmod +x gradlew
```

### Executar testes

```bash
# Todos os testes
./gradlew test

# Com output detalhado
./gradlew test --info

# Apenas uma classe
./gradlew test --tests "tests.AuthTest"
./gradlew test --tests "tests.ProdutoApiTest"

# Relatório HTML gerado em:
# build/reports/tests/test/index.html
```

### Variáveis de ambiente (opcionais)

```bash
# Apontar para outro ambiente
export LOJINHA_BASE_URI=http://outro-servidor/lojinha
export LOJINHA_LOGIN=meu_usuario
export LOJINHA_SENHA=minha_senha

./gradlew test
```

### Estrutura de arquivos relevantes

```
lojinha-api-tests/
├── build.gradle
├── settings.gradle
├── lojinha-v2.yml                          ← OpenAPI spec
├── gradle/wrapper/gradle-wrapper.properties ← Gradle 8.7
└── src/test/
    ├── java/
    │   ├── base/BaseTest.java              ← configuração RestAssured
    │   ├── utils/AuthHelper.java           ← helper de autenticação
    │   └── tests/
    │       ├── AuthTest.java               (4 testes)
    │       └── ProdutoApiTest.java         (13 testes — CRUD + validações)
    └── resources/
        └── schemas/produto-schema.json     ← JSON Schema Draft-07
```

---

## Projeto 3 — lojinha-performance/ (k6 + JMeter)

### k6

#### Instalação (macOS)

```bash
brew install k6
```

#### Arquivos

```
lojinha-performance/k6/
├── config.js       ← SLAs, credenciais, BASE_URL, helpers
├── smoke.js        ← 1 VU, 1 min — fluxo completo
├── stress.js       ← rampa crescente de carga
├── login-load.js   ← foco no endpoint de login
└── produtos-load.js← foco nos endpoints de produto
```

#### Executar

```bash
# Smoke test (sempre primeiro)
k6 run lojinha-performance/k6/smoke.js

# Com outro ambiente
k6 run -e BASE_URL=http://outro/lojinha lojinha-performance/k6/smoke.js

# Stress test
k6 run lojinha-performance/k6/stress.js

# Salvar resultados
k6 run --out json=results.json lojinha-performance/k6/smoke.js
```

#### SLAs configurados (config.js)

| Threshold | Valor |
|-----------|-------|
| p95 global | < 500ms |
| p99 global | < 1000ms |
| taxa de erro | < 1% |
| p95 login | < 300ms |
| p95 produtos | < 500ms |

---

### JMeter

#### Instalação (macOS)

```bash
brew install jmeter
```

#### Arquivos

```
lojinha-performance/jmeter/
├── lojinha-smoke.jmx   ← smoke (1 thread, 1 loop)
├── lojinha-load.jmx    ← carga moderada
├── lojinha-stress.jmx  ← stress (rampa)
├── lojinha-test-plan.jmx
└── results/
    ├── smoke-aggregate.csv
    └── smoke-report/   ← relatório HTML
```

#### Executar

```bash
# Smoke test em modo headless
jmeter -n \
  -t lojinha-performance/jmeter/lojinha-smoke.jmx \
  -l lojinha-performance/jmeter/results/smoke-results.jtl \
  -e -o lojinha-performance/jmeter/results/smoke-report/

# Abrir GUI para editar planos
jmeter
```

#### Resultado observado — smoke

| Métrica | Valor | SLA | Status |
|---------|-------|-----|--------|
| p95 geral | 475ms | <500ms | ✅ |
| Taxa de erro | 4,44% | <1% | ❌ |

> Erro relacionado ao BUG #2 (sem paginação). Corrigir antes de usar JMeter como baseline.

---

## Resultado Final da POC (referência rápida)

| Camada | Testes | Resultado |
|--------|--------|-----------|
| Web (Playwright) | 17 | ✅ 17/17 passando |
| API (RestAssured) | 17 | ✅ 17/17 passando |
| Performance (k6) | smoke | ✅ 4/5 endpoints dentro do SLA |
| Performance (JMeter) | smoke | ⚠️ p95 ok, taxa erro 4,44% |
