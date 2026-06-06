# lojinha-tests — Testes E2E Web com Playwright

Suíte de testes de interface web para a Lojinha API, implementada com **Playwright + TypeScript** seguindo o padrão **Page Object Model**.

## Pré-requisitos

- Node.js 18+
- Lojinha API rodando em `http://165.227.93.41`

## Instalação

```bash
npm install
npx playwright install chromium
```

## Execução

```bash
# Todos os testes (headless)
npx playwright test

# Com UI interativa
npx playwright test --ui

# Um arquivo específico
npx playwright test tests/login.spec.ts

# Relatório HTML
npx playwright show-report
```

## Estrutura

```
lojinha-tests/
├── pages/          # Page Objects (LoginPage, ProdutoFormPage, ProdutoListaPage)
├── tests/          # Specs de teste
│   ├── login.spec.ts
│   └── produto.spec.ts
├── playwright.config.ts
└── package.json
```

## Resultados da POC

17/17 testes passando — cobertura de login, cadastro, listagem e validações de produto.
