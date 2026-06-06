# Setup do Ambiente — Lojinha

> Conhecimento acumulado na sessão de 05/06/2026
> Usar como contexto inicial em qualquer nova sessão

---

## URLs

| Recurso | URL |
|---------|-----|
| Web (frontend) | http://165.227.93.41/lojinha-web/v2/ |
| API (backend) | http://165.227.93.41/lojinha |
| Contrato OpenAPI | http://165.227.93.41/lojinha/lojinha-v2.yml |

## Credenciais

```
usuarioLogin: admin
usuarioSenha: admin
```

⚠️ A senha é `admin` (não `adminadmin` — esse foi o chute inicial errado).
O contrato OpenAPI confirmou o valor correto.

## Dependências por projeto

### Web — Playwright TypeScript
```bash
npm init playwright@latest
npx playwright install chromium
```

### API — RestAssured Java
```
Java 17+
Gradle 8.7 (wrapper incluso no projeto)
RestAssured 5.4
JUnit 5.10
AssertJ
```

### Performance — k6
```bash
# macOS
brew install k6

# Windows
choco install k6
```

### Performance — JMeter
```bash
# macOS
brew install jmeter

# Windows
# Baixar em: https://jmeter.apache.org/download_jmeter.cgi
# Extrair em C:\jmeter
# Adicionar C:\jmeter\bin ao PATH
```

## Verificação rápida do ambiente

```bash
# Confirma que a API está respondendo
curl -s -X POST http://165.227.93.41/lojinha/v2/login \
  -H "Content-Type: application/json" \
  -d '{"usuarioLogin":"admin","usuarioSenha":"admin"}' \
  -w "\nHTTP: %{http_code}"

# Resposta esperada: HTTP 200 + token no body
```

## Estrutura de pastas do projeto

```
qa-agents/
  agents/                    ← system prompts dos 7 agentes
  knowledge_base/
    lojinha/                 ← este RAG
    julio-de-lima/           ← 684 vídeos coletados
    fernando-papito/         ← 19 vídeos coletados
    qazando/                 ← 39 vídeos coletados
    vinicius-pessoni/        ← 124 vídeos coletados
    walmyr-talkingabouttesting/ ← adicionar via collect.py
  lojinha-tests/             ← Playwright TypeScript (17 testes)
  lojinha-api-tests/         ← RestAssured Java (17 testes)
  lojinha-performance/
    k6/                      ← smoke, load, stress
    jmeter/                  ← smoke, load, stress + run.sh
  reports/
    relatorio-poc-final.md   ← relatório executivo SIGMA
  tools/
    collect.py               ← coleta YouTube
    sources.json             ← configuração dos canais
    requirements.txt         ← yt-dlp, whisper, tqdm, rich
```
