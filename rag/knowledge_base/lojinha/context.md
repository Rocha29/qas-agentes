# Contexto da Lojinha — Injetar no início de cada sessão

> Versão compacta do RAG completo.
> Cole isso no início do prompt quando abrir uma nova sessão.

---

## Ambiente

- **Web:** http://165.227.93.41/lojinha-web/v2/
- **API:** http://165.227.93.41/lojinha (basePath: /lojinha)
- **Contrato:** http://165.227.93.41/lojinha/lojinha-v2.yml
- **Login:** `usuarioLogin: admin` / `usuarioSenha: admin`
- **Header auth:** `token: {valor}` (não Bearer)

## Endpoints principais

```
POST /v2/login           → autentica, retorna token
POST /v2/produtos        → cria produto (produtoValor: integer, 1-7000)
GET  /v2/produtos        → lista (⚠️ sem paginação, lento)
GET  /v2/produtos/{id}   → busca por id
PUT  /v2/produtos/{id}   → atualiza
DELETE /v2/produtos/{id} → remove (204)
POST /v2/produtos/{id}/componentes → adiciona componente
```

## Bugs conhecidos

- 🐛 **BUG #1:** `POST /v2/produtos` com token inválido → 500 (deveria ser 401)
- 🐛 **BUG #2:** `GET /v2/produtos` sem paginação → 41KB, max 643ms com 1 usuário

## Gotchas críticos

- **Playwright:** usar `goto('')` nunca `goto('/')` (baseURL tem subpath)
- **Playwright:** `getByLabel('Usuário')` com acento e U maiúsculo
- **Playwright:** URL de exclusão tem `//` — usar URL absoluta
- **RestAssured:** basePath é `/lojinha` (não `/lojinha-api`)
- **RestAssured:** endpoint de login é `POST /v2/login` (não `/v2/usuarios/login`)
- **JMeter:** DurationAssertion de 500ms inflaciona erro — usar 1000ms no ambiente de treinamento

## Projetos criados nesta POC

| Projeto | Stack | Testes | Status |
|---------|-------|--------|--------|
| `lojinha-tests/` | Playwright TypeScript | 17 | ✅ 17/17 |
| `lojinha-api-tests/` | RestAssured Java 17 | 17 | ✅ 17/17 |
| `lojinha-performance/k6/` | k6 JavaScript | smoke+load+stress | ✅ |
| `lojinha-performance/jmeter/` | JMeter | smoke+load+stress | ✅ |

## Como rodar cada projeto

```bash
# Web
cd lojinha-tests && npx playwright test --reporter=list

# API
cd lojinha-api-tests && ./gradlew test

# Performance k6
k6 run lojinha-performance/k6/smoke.js

# Performance JMeter
jmeter -n \
  -t lojinha-performance/jmeter/lojinha-smoke.jmx \
  -l results/smoke.jtl \
  -e -o results/smoke-report/
# Abre relatório:
open results/smoke-report/index.html
```

## Agentes disponíveis

```
ARIA   → agents/ARIA.md   (Web/Playwright)
KAUE   → agents/KAUE.md   (Mobile/Maestro/Appium)
NEXUS  → agents/NEXUS.md  (API/RestAssured)
FLUX   → agents/FLUX.md   (Performance/k6/JMeter)
ATLAS  → agents/ATLAS.md  (Arquitetura)
HELIX  → agents/HELIX.md  (Exploratório)
SIGMA  → agents/SIGMA.md  (Negócio/Relatórios)
```

## Como usar este contexto

No início de qualquer nova sessão no Claude Code:

```
Leia o arquivo .claude/lojinha-context.md antes de começar.
Esse arquivo contém o contexto completo do ambiente,
bugs conhecidos e gotchas já resolvidos.
Não redescubra o que já está documentado.
```
