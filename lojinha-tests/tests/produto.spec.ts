import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { ProdutoFormPage } from '../pages/ProdutoFormPage';
import { ProdutoListaPage } from '../pages/ProdutoListaPage';

const ERRO_VALOR = 'O valor do produto deve estar entre R$ 0,01 e R$ 7.000,00';

// IDs criados durante os testes são limpos pelo próprio fluxo de exclusão.
// Produtos de setup são removidos no afterEach via API de exclusão.

test.describe('Produtos — CRUD', () => {
  let loginPage: LoginPage;
  let formPage: ProdutoFormPage;
  let listaPage: ProdutoListaPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    formPage = new ProdutoFormPage(page);
    listaPage = new ProdutoListaPage(page);

    await loginPage.abrir();
    await loginPage.fazerLogin('admin', 'admin');
    await expect(page).toHaveURL(/\/produto/);
  });

  // ── CREATE ──────────────────────────────────────────────────────────────

  test.describe('Criar produto', () => {
    test('deve criar produto com dados válidos', async ({ page }) => {
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario('Smartphone XYZ', '250000', 'Preto,Branco');
      await formPage.salvar();
      await formPage.validarSalvoComSucesso();

      const id = await formPage.obterIdDoProduto();
      await formPage.removerProduto(id);
    });

    test('deve criar produto com valor mínimo (R$ 0,01)', async ({ page }) => {
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario('Produto Centavo', '1', 'Verde');
      await formPage.salvar();
      await formPage.validarSalvoComSucesso();

      const id = await formPage.obterIdDoProduto();
      await formPage.removerProduto(id);
    });

    test('deve criar produto com valor máximo (R$ 7.000,00)', async ({ page }) => {
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario('Produto Premium', '700000', 'Ouro');
      await formPage.salvar();
      await formPage.validarSalvoComSucesso();

      const id = await formPage.obterIdDoProduto();
      await formPage.removerProduto(id);
    });

    test('deve exibir erro ao criar produto com valor zero', async () => {
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario('Produto Zero', '000', 'Azul');
      await formPage.salvar();
      await formPage.validarErroDeValidacao(ERRO_VALOR);
    });

    test('deve exibir erro ao criar produto com valor acima de R$ 7.000,00', async () => {
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario('Produto Caro', '700001', 'Prata');
      await formPage.salvar();
      await formPage.validarErroDeValidacao(ERRO_VALOR);
    });

    test('deve exibir erro ao criar produto sem preencher nenhum campo', async () => {
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario('', '', '');
      await formPage.salvar();
      await formPage.validarErroDeValidacao(ERRO_VALOR);
    });
  });

  // ── READ ────────────────────────────────────────────────────────────────

  test.describe('Listar produtos', () => {
    test('deve exibir a lista de produtos após login', async () => {
      await listaPage.validarNaPagina();
      await expect(listaPage.btnAdicionarProduto, 'Botão "Adicionar produto" deve estar visível').toBeVisible();
    });

    test('deve exibir produto recém-criado na lista', async ({ page }) => {
      const nomeProduto = `ProdutoNaLista-${Date.now()}`;
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario(nomeProduto, '50000', 'Roxo');
      await formPage.salvar();
      await formPage.validarSalvoComSucesso();
      const id = await formPage.obterIdDoProduto();

      await listaPage.abrir();
      await listaPage.validarProdutoNaLista(nomeProduto);

      await formPage.removerProduto(id);
    });
  });

  // ── UPDATE ──────────────────────────────────────────────────────────────

  test.describe('Editar produto', () => {
    let produtoId: string;

    test.beforeEach(async ({ page }) => {
      // Cria um produto para usar nos testes de edição
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario('ProdutoParaEditar', '100000', 'Cinza');
      await formPage.salvar();
      await formPage.validarSalvoComSucesso();
      produtoId = await formPage.obterIdDoProduto();
    });

    test.afterEach(async () => {
      await formPage.removerProduto(produtoId);
    });

    test('deve editar produto com dados válidos', async ({ page }) => {
      await page.goto(`http://165.227.93.41/lojinha-web/v2/produto/editar/${produtoId}`);
      await formPage.preencherFormulario('ProdutoEditado', '200000', 'Amarelo,Verde');
      await formPage.salvar();
      await formPage.validarAlteradoComSucesso();
    });

    test('deve exibir os dados salvos ao abrir edição', async ({ page }) => {
      await page.goto(`http://165.227.93.41/lojinha-web/v2/produto/editar/${produtoId}`);
      await expect(formPage.campoNome, 'Nome deve estar preenchido').toHaveValue('ProdutoParaEditar');
      await expect(formPage.campoCores, 'Cores devem estar preenchidas').toHaveValue('Cinza');
    });

    test('deve exibir erro ao salvar edição com valor acima do limite', async ({ page }) => {
      await page.goto(`http://165.227.93.41/lojinha-web/v2/produto/editar/${produtoId}`);
      await formPage.campoValor.clear();
      await formPage.campoValor.fill('700001');
      await formPage.salvar();
      await formPage.validarErroDeValidacao(ERRO_VALOR);
    });
  });

  // ── DELETE ──────────────────────────────────────────────────────────────

  test.describe('Excluir produto', () => {
    test('deve excluir produto e removê-lo da lista', async ({ page }) => {
      // Cria o produto que será excluído
      await formPage.abrirNovoProduto();
      await formPage.preencherFormulario('ProdutoParaExcluir', '30000', 'Laranja');
      await formPage.salvar();
      await formPage.validarSalvoComSucesso();

      await listaPage.abrir();
      await listaPage.clicarExcluirProduto('ProdutoParaExcluir');

      await listaPage.validarMensagemSucesso('Produto removido com sucesso');
      await listaPage.validarProdutoRemovidoDaLista('ProdutoParaExcluir');
    });
  });
});
