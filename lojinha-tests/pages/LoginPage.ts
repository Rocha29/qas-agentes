import { type Page, type Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly campoUsuario: Locator;
  readonly campoSenha: Locator;
  readonly btnEntrar: Locator;
  readonly toastMensagem: Locator;

  constructor(page: Page) {
    this.page = page;
    this.campoUsuario = page.getByLabel('Usuário');
    this.campoSenha = page.getByLabel('Senha');
    this.btnEntrar = page.getByRole('button', { name: 'Entrar' });
    this.toastMensagem = page.locator('#toast-container');
  }

  async abrir() {
    await this.page.goto('');
  }

  async fazerLogin(usuario: string, senha: string) {
    await this.campoUsuario.fill(usuario);
    await this.campoSenha.fill(senha);
    await this.btnEntrar.click();
  }

  async validarLoginSucesso() {
    await expect(this.page, 'Deve redirecionar para a lista de produtos após login válido')
      .toHaveURL(/\/produto/);
    await expect(
      this.page.getByText('Boas vindas, admin!'),
      'Mensagem de boas vindas deve estar visível'
    ).toBeVisible();
  }

  async validarMensagemErro(mensagemEsperada: string) {
    await expect(
      this.toastMensagem,
      `Toast de erro deve exibir: "${mensagemEsperada}"`
    ).toContainText(mensagemEsperada);
  }

  async validarPermaneceNaTelaDeLogin() {
    await expect(this.page, 'Deve permanecer na tela de login')
      .toHaveURL(/\/((\?.*)?$|login)/);
    await expect(this.btnEntrar, 'Botão Entrar deve continuar visível').toBeVisible();
  }
}
