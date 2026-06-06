import { type Page, type Locator, expect } from '@playwright/test';

export class ProdutoListaPage {
  readonly page: Page;
  readonly tituloPagina: Locator;
  readonly btnAdicionarProduto: Locator;
  readonly listaProdutos: Locator;
  readonly toastMensagem: Locator;

  constructor(page: Page) {
    this.page = page;
    this.tituloPagina = page.getByRole('heading', { name: 'Lista de Produtos' });
    this.btnAdicionarProduto = page.getByRole('link', { name: 'Adicionar produto' });
    this.listaProdutos = page.locator('.collection');
    this.toastMensagem = page.locator('#toast-container');
  }

  async abrir() {
    await this.page.goto('produto');
  }

  async validarNaPagina() {
    await expect(this.tituloPagina, 'Título "Lista de Produtos" deve estar visível').toBeVisible();
  }

  async clicarAdicionarProduto() {
    await this.btnAdicionarProduto.click();
    await this.page.waitForURL(/\/produto\/novo/);
  }

  async clicarEditarProduto(nomeProduto: string) {
    await this.page.getByRole('link', { name: nomeProduto }).click();
    await this.page.waitForURL(/\/produto\/editar\//);
  }

  async clicarExcluirProduto(nomeProduto: string) {
    const item = this.listaProdutos.locator('.collection-item').filter({ hasText: nomeProduto });
    await item.locator('a.secondary-content').click();
    await this.page.waitForURL(/\/produto/);
  }

  async validarProdutoNaLista(nomeProduto: string) {
    await expect(
      this.page.getByRole('link', { name: nomeProduto }).first(),
      `Produto "${nomeProduto}" deve aparecer na lista`
    ).toBeVisible();
  }

  async validarProdutoRemovidoDaLista(nomeProduto: string) {
    await expect(
      this.page.getByRole('link', { name: nomeProduto }).first(),
      `Produto "${nomeProduto}" não deve mais aparecer na lista`
    ).not.toBeVisible();
  }

  async validarMensagemSucesso(mensagem: string) {
    await expect(
      this.toastMensagem,
      `Toast deve exibir: "${mensagem}"`
    ).toContainText(mensagem);
  }

  async validarMensagemErro(mensagem: string) {
    await expect(
      this.toastMensagem,
      `Toast de erro deve exibir: "${mensagem}"`
    ).toContainText(mensagem);
  }
}
