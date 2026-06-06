# Quickstart — Primeiro agente rodando em 5 minutos

Você vai ativar o agente **ARIA-WEB** e rodar os 17 testes E2E da Lojinha. Nenhuma configuração avançada necessária.

---

## Pré-requisitos (verifique antes de começar)

```bash
node --version   # precisa ser 18+
git --version    # qualquer versão
```

Se não tiver o Claude Code CLI:
```bash
npm install -g @anthropic-ai/claude-code
```

---

## Passo 1 — Clone o repositório (30 segundos)

```bash
git clone https://github.com/Rocha29/qas-agentes.git
cd qas-agentes
```

---

## Passo 2 — Instale as dependências dos testes web (1 minuto)

```bash
cd lojinha-tests
npm install
npx playwright install chromium
cd ..
```

---

## Passo 3 — Ative o agente ARIA-WEB (30 segundos)

```bash
claude --system-prompt agents/ARIA-WEB.md
```

O terminal abre o chat com ARIA-WEB ativa. Ela já conhece Playwright, Page Objects e as regras de ouro de automação web.

---

## Passo 4 — Rode os testes (1 minuto)

Dentro do chat com ARIA-WEB, peça:

```
Rode os testes da Lojinha em lojinha-tests/ e me diga o resultado.
```

Ou rode diretamente no terminal (em outro terminal):

```bash
cd lojinha-tests
npx playwright test
```

Resultado esperado: **17/17 testes passando** em ~30 segundos.

---

## Passo 5 — Veja o relatório (30 segundos)

```bash
npx playwright show-report
```

Abre o relatório HTML no browser com screenshots, tempo de cada teste e rastreabilidade completa.

---

## Próximos passos

Agora que ARIA-WEB está rodando, você pode:

**Testar a API (NEXUS-API):**
```bash
claude --system-prompt agents/NEXUS-API.md
# "Rode os testes de API da Lojinha e valide o contrato OpenAPI"
```

**Planejar uma história completa (SIGMA-LEAD):**
```bash
# Crie historias/HIST-001.md a partir do template
cp historias/_template-negocio.md historias/MINHA-HIST-001.md
# Edite o arquivo com sua história
claude --system-prompt agents/SIGMA-LEAD.md
# Digite: MINHA-HIST-001
```

**Ver o fluxo completo:**
→ Consulte [`WORKFLOW.md`](WORKFLOW.md)

---

> **App de referência:** Lojinha API em `http://165.227.93.41` — já configurada nos projetos de teste. Nenhum setup de servidor necessário.
