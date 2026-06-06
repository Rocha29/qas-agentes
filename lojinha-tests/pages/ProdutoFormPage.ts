import { type Page, type Locator, expect } from '@playwright/test';

export class ProdutoFormPage {
  readonly page: Page;
  readonly campoNome: Locator;
  readonly campoValor: Locator;
  readonly campoCores: Locator;
  readonly btnSalvar: Locator;
  readonly btnListaDeProdutos: Locator;
  readonly toastMensagem: Locator;

  constructor(page: Page) {
    this.page = page;
    this.campoNome = page.locator('#produtonome');
    this.campoValor = page.locator('#produtovalor');
    this.campoCores = page.locator('#produtocores');
    this.btnSalvar = page.getByRole('button', { name: 'Salvar' });
    this.btnListaDeProdutos = page.getByRole('link', { name: 'Lista de Produtos' });
    this.toastMensagem = page.locator('#toast-container');
  }

  async abrirNovoProduto() {
    await this.page.goto('produto/novo');
    await expect(
      this.page.getByRole('heading', { name: 'Adicionar produto' }),
      'Formulário de novo produto deve estar visível'
    ).toBeVisible();
  }

  async preencherFormulario(nome: string, valor: string, cores: string) {
    await this.campoNome.fill(nome);
    // O campo valor usa máscara jQuery — limpa antes para evitar concatenação
    await this.campoValor.clear();
    await this.campoValor.fill(valor);
    await this.campoCores.fill(cores);
  }

  async salvar() {
    await this.btnSalvar.click();
    await this.page.waitForLoadState('networkidle');
  }

  async validarSalvoComSucesso(mensagem = 'Produto adicionado com sucesso') {
    await expect(this.page, 'Deve redirecionar para edição após salvar').toHaveURL(/\/produto\/editar\//);
    await expect(
      this.toastMensagem,
      `Toast deve exibir: "${mensagem}"`
    ).toContainText(mensagem);
  }

  async validarAlteradoComSucesso() {
    await expect(this.page, 'Deve permanecer na tela de edição após alterar').toHaveURL(/\/produto\/editar\//);
    await expect(
      this.toastMensagem,
      'Toast deve exibir "Produto alterado com sucesso"'
    ).toContainText('Produto alterado com sucesso');
  }

  async validarErroDeValidacao(mensagemEsperada: string) {
    await expect(this.page, 'Deve redirecionar para lista com erro').toHaveURL(/\/produto\?error=/);
    await expect(
      this.toastMensagem,
      `Toast de erro deve exibir: "${mensagemEsperada}"`
    ).toContainText(mensagemEsperada);
  }

  async obterIdDoProduto(): Promise<string> {
    const url = this.page.url();
    const match = url.match(/editar\/(\d+)/);
    if (!match) throw new Error(`ID não encontrado na URL: ${url}`);
    return match[1];
  }

  async removerProduto(id: string) {
    // A app usa //produto/remover/ (barra dupla) — usamos URL absoluta para evitar ambiguidade
    await this.page.goto(`http://165.227.93.41/lojinha-web/v2//produto/remover/${id}`);
    await this.page.waitForLoadState('networkidle');
  }

  async validarValorExibido(valorEsperado: string) {
    await expect(
      this.campoValor,
      `Campo valor deve exibir "${valorEsperado}"`
    ).toHaveValue(valorEsperado);
  }
}
