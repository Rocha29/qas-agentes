package tests;

import base.BaseTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.hamcrest.Matchers.*;

@DisplayName("Autenticação — POST /v2/login")
class AuthTest extends BaseTest {

    @Test
    @DisplayName("Deve autenticar com credenciais válidas e retornar token")
    void deveAutenticarComCredenciaisValidas() {
        comJson()
                .body("{\"usuarioLogin\":\"admin\",\"usuarioSenha\":\"admin\"}")
                .when()
                .post("/login")
                .then()
                .statusCode(200)
                .body("data.token", notNullValue())
                .body("data.token", not(emptyString()))
                .body("error", emptyString());
    }

    @Test
    @DisplayName("Deve retornar 401 com senha inválida")
    void deveRetornar401ComSenhaInvalida() {
        comJson()
                .body("{\"usuarioLogin\":\"admin\",\"usuarioSenha\":\"senhaErrada\"}")
                .when()
                .post("/login")
                .then()
                .statusCode(401);
    }

    @Test
    @DisplayName("Deve retornar Content-Type application/json")
    void deveRetornarContentTypeJson() {
        comJson()
                .body("{\"usuarioLogin\":\"admin\",\"usuarioSenha\":\"admin\"}")
                .when()
                .post("/login")
                .then()
                .statusCode(200)
                .contentType(containsString("application/json"));
    }

    @Test
    @DisplayName("Deve retornar 401 com usuário inexistente")
    void deveRetornar401ComUsuarioInexistente() {
        comJson()
                .body("{\"usuarioLogin\":\"usuario_nao_existe_xyz\",\"usuarioSenha\":\"qualquer\"}")
                .when()
                .post("/login")
                .then()
                .statusCode(401);
    }
}
