import { test } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

const MENSAGEM_ERRO_LOGIN = 'Falha ao fazer o login';

test.describe('Login — Lojinha Web', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.abrir();
  });

  test('deve fazer login com credenciais válidas', async () => {
    await loginPage.fazerLogin('admin', 'admin');
    await loginPage.validarLoginSucesso();
  });

  test('deve exibir erro ao fazer login com senha incorreta', async () => {
    await loginPage.fazerLogin('admin', 'senhaerrada');
    await loginPage.validarMensagemErro(MENSAGEM_ERRO_LOGIN);
    await loginPage.validarPermaneceNaTelaDeLogin();
  });

  test('deve exibir erro ao fazer login com usuário vazio', async () => {
    await loginPage.fazerLogin('', 'admin');
    await loginPage.validarMensagemErro(MENSAGEM_ERRO_LOGIN);
    await loginPage.validarPermaneceNaTelaDeLogin();
  });

  test('deve exibir erro ao fazer login com senha vazia', async () => {
    await loginPage.fazerLogin('admin', '');
    await loginPage.validarMensagemErro(MENSAGEM_ERRO_LOGIN);
    await loginPage.validarPermaneceNaTelaDeLogin();
  });

  test('deve exibir erro ao fazer login com usuário e senha vazios', async () => {
    await loginPage.fazerLogin('', '');
    await loginPage.validarMensagemErro(MENSAGEM_ERRO_LOGIN);
    await loginPage.validarPermaneceNaTelaDeLogin();
  });
});
