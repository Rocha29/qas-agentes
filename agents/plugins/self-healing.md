# Plugin: Self-Healing Locators para ARIA-WEB

**Tipo:** Plugin de arquitetura — carregue junto com `agents/ARIA-WEB.md`
**Gap competitivo:** Mabl, Testim e Momentic têm auto-healing nativo. Este plugin equipa o ARIA-WEB com estratégia equivalente usando Playwright puro.

---

## O Problema

Locators fixos quebram quando o frontend muda. Um `data-testid` renomeado, um label trocado ou um ID gerado dinamicamente derruba testes que eram válidos. Times sem self-healing gastam horas "consertando" testes que na verdade ainda cobrem comportamentos corretos.

---

## A Estratégia: Fallback Chain

Em vez de um único locator, defina uma **cadeia de fallbacks** em ordem de confiabilidade. O helper tenta cada um com timeout curto e registra qual funcionou — criando rastreabilidade de drift.

```
Nível 1 — Semântico (mais confiável)
  getByRole('button', { name: 'Confirmar' })

Nível 2 — TestId (estável se o time mantém)
  getByTestId('btn-confirm')

Nível 3 — Label / Placeholder
  getByLabel('Confirmar pedido')

Nível 4 — Texto visível (mais frágil, último recurso)
  getByText('Confirmar')

Nível 5 — CSS seletor (evitar, só como emergência)
  locator('.btn-primary')
```

---

## Implementação: `support/self-healing.ts`

Crie este arquivo em `lojinha-tests/support/self-healing.ts`:

```typescript
import { Page, Locator } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export interface HealingLocator {
  strategy: string;
  locator: Locator;
}

/**
 * Tenta cada locator na ordem fornecida.
 * Registra qual funcionou em healing-log.json para rastreamento de drift.
 */
export async function findWithHealing(
  page: Page,
  elementName: string,
  candidates: HealingLocator[],
  timeout = 3000
): Promise<Locator> {
  const attempts: string[] = [];

  for (const candidate of candidates) {
    try {
      await candidate.locator.waitFor({ state: 'visible', timeout });
      
      // Registra se não foi o primeiro locator (sinal de drift)
      if (candidates.indexOf(candidate) > 0) {
        logHealing(elementName, candidate.strategy, attempts);
      }

      return candidate.locator;
    } catch {
      attempts.push(candidate.strategy);
    }
  }

  throw new Error(
    `[self-healing] Nenhum locator funcionou para "${elementName}".\n` +
    `Tentativas: ${attempts.join(' → ')}`
  );
}

function logHealing(element: string, usedStrategy: string, failedStrategies: string[]) {
  const logPath = path.join(process.cwd(), 'test-results', 'healing-log.json');
  
  let log: object[] = [];
  if (fs.existsSync(logPath)) {
    log = JSON.parse(fs.readFileSync(logPath, 'utf-8'));
  }

  log.push({
    timestamp: new Date().toISOString(),
    element,
    primaryFailed: failedStrategies,
    healedWith: usedStrategy,
    action: 'REVIEW_LOCATOR — o locator primário pode estar desatualizado'
  });

  fs.mkdirSync(path.dirname(logPath), { recursive: true });
  fs.writeFileSync(logPath, JSON.stringify(log, null, 2));
}
```

---

## Como usar nos Page Objects

```typescript
// pages/LoginPage.ts — com self-healing
import { Page } from '@playwright/test';
import { findWithHealing } from '../support/self-healing';

export class LoginPage {
  constructor(private page: Page) {}

  async fillEmail(email: string) {
    const emailField = await findWithHealing(this.page, 'email-field', [
      { strategy: 'label',       locator: this.page.getByLabel('E-mail') },
      { strategy: 'placeholder', locator: this.page.getByPlaceholder('Digite seu e-mail') },
      { strategy: 'testId',      locator: this.page.getByTestId('input-email') },
      { strategy: 'css',         locator: this.page.locator('input[type="email"]') },
    ]);
    await emailField.fill(email);
  }

  async clickLogin() {
    const btn = await findWithHealing(this.page, 'login-button', [
      { strategy: 'role',   locator: this.page.getByRole('button', { name: 'Entrar' }) },
      { strategy: 'testId', locator: this.page.getByTestId('btn-login') },
      { strategy: 'text',   locator: this.page.getByText('Entrar') },
      { strategy: 'css',    locator: this.page.locator('button[type="submit"]') },
    ]);
    await btn.click();
  }
}
```

---

## Integração com o relatório do CI

Adicione ao `playwright.config.ts`:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    // Reporter customizado para incluir healing log no summary
    ['./support/healing-reporter.ts'],
  ],
});
```

Crie `support/healing-reporter.ts`:

```typescript
import { Reporter, TestCase, TestResult } from '@playwright/test/reporter';
import * as fs from 'fs';

class HealingReporter implements Reporter {
  onEnd() {
    const logPath = 'test-results/healing-log.json';
    if (!fs.existsSync(logPath)) return;

    const log = JSON.parse(fs.readFileSync(logPath, 'utf-8'));
    if (log.length === 0) return;

    console.log('\n⚠️  SELF-HEALING REPORT — Locators que precisam de atenção:');
    console.log('─'.repeat(60));
    log.forEach((entry: any) => {
      console.log(`  Elemento: ${entry.element}`);
      console.log(`  Falhou:   ${entry.primaryFailed.join(', ')}`);
      console.log(`  Usou:     ${entry.healedWith}`);
      console.log(`  Ação:     ${entry.action}`);
      console.log('─'.repeat(60));
    });
  }
}

export default HealingReporter;
```

---

## Regras de uso (ATLAS-ARCH)

1. **Máximo 4 candidatos por elemento** — mais que isso indica locators ruins, não self-healing insuficiente
2. **Nível semântico sempre primeiro** — `getByRole` e `getByLabel` raramente mudam
3. **Revise o healing-log semanalmente** — locator que cura 3 vezes seguidas precisa ser atualizado na fonte
4. **Nunca use somente CSS no nível 1** — é o mais frágil e o mais comum de mudar
5. **O log é o alerta, não a solução** — self-healing compra tempo, não substitui manutenção

---

## Comparativo competitivo

| Capacidade | Mabl | Testim | Este plugin |
|-----------|------|--------|-------------|
| Auto-healing sem código | ✅ nativo | ✅ nativo | ❌ requer implementação |
| Rastreabilidade de drift | ⚠️ parcial | ⚠️ parcial | ✅ healing-log.json |
| Controle total do fallback | ❌ caixa preta | ❌ caixa preta | ✅ você define a cadeia |
| Custo | 💰 licença | 💰 licença | ✅ open source |
| Integração com CI próprio | ⚠️ limitada | ⚠️ limitada | ✅ total |

**Conclusão ATLAS:** para times que já têm Playwright, este plugin entrega 80% do valor do self-healing comercial com controle e rastreabilidade superiores. A diferença real está na UX — Mabl e Testim são mais amigáveis para QAs não-devs.
