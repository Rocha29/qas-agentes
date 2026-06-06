# HIST-001 — Login no app mobile e web com expiração de sessão

**Tipo:** negócio
**Sprint:** 1
**Criado por:** Time de negócio (gerado pela IA da ferramenta interna)
**Data:** 2026-06-06

---

## História

Como **usuário registrado**,
quero **fazer login no app e no site com meu e-mail e senha**
para **acessar minha conta e ter minha sessão encerrada automaticamente após 30 minutos de inatividade**.

---

## Critérios de Aceite

- [ ] Login com e-mail e senha válidos redireciona para a home
- [ ] Login com senha incorreta exibe mensagem de erro sem revelar qual campo está errado
- [ ] Após 3 tentativas incorretas, conta é bloqueada por 5 minutos
- [ ] Sessão expira após 30 minutos de inatividade e redireciona para o login
- [ ] Token JWT é renovado automaticamente se o usuário estiver ativo
- [ ] Funciona identicamente no web, Android e iOS

---

## BDDs (gerados pela ferramenta interna)

### Cenário 1 — Login com sucesso

```gherkin
Dado que o usuário está na tela de login
Quando ele preenche e-mail "usuario@teste.com" e senha "Senha@123"
E clica no botão "Entrar"
Então ele é redirecionado para a tela Home
E o token JWT é armazenado na sessão
```

### Cenário 2 — Login com senha incorreta

```gherkin
Dado que o usuário está na tela de login
Quando ele preenche e-mail "usuario@teste.com" e senha "senhaErrada"
E clica no botão "Entrar"
Então uma mensagem de erro genérica é exibida
E o usuário permanece na tela de login
```

### Cenário 3 — Bloqueio após 3 tentativas

```gherkin
Dado que o usuário falhou no login 2 vezes consecutivas
Quando ele tenta login com senha incorreta pela terceira vez
Então a conta é bloqueada por 5 minutos
E uma mensagem informa o tempo de bloqueio
```

---

## Superfícies afetadas

- [x] Web (browser)
- [x] Mobile Android
- [x] Mobile iOS
- [ ] WebView dentro do app
- [x] API / endpoint  ← endpoint de autenticação POST /auth/login
- [ ] BFF

---

## Risco estimado

- [x] Alto — fluxo crítico (login, sessão, bloqueio de conta)

---

## Contexto adicional / dependências

- Design: [Figma - tela de login v2]
- Endpoint: `POST /api/v1/auth/login`
- Resposta esperada: `{ token, refreshToken, expiresIn }`
- SLA do endpoint de login: p95 < 300ms

---

## Notas para os agentes

- NEXUS-API: validar contrato do endpoint, incluindo cenário de conta bloqueada (HTTP 429)
- FLUX-PERF: simular 100 logins simultâneos — risco de bottleneck na geração de JWT
- ARIA-WEB: focar no comportamento do token no browser (sessionStorage vs localStorage)
- KAUE-MOBILE: testar em Android 12+ e iOS 16+ — comportamento de teclado pode variar
