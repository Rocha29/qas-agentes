package utils;

import io.restassured.http.ContentType;

import static io.restassured.RestAssured.given;

public class AuthHelper {

    // Contrato: POST /v2/login (não /v2/usuarios/login)
    private static final String LOGIN_ENDPOINT = "/login";

    public static String obterToken(String login, String senha) {
        return given()
                .contentType(ContentType.JSON)
                .body(String.format("{\"usuarioLogin\":\"%s\",\"usuarioSenha\":\"%s\"}", login, senha))
                .when()
                .post(LOGIN_ENDPOINT)
                .then()
                .statusCode(200)
                .extract()
                .path("data.token");
    }

    public static String obterTokenAdmin() {
        String login = System.getenv().getOrDefault("LOJINHA_LOGIN", "admin");
        String senha  = System.getenv().getOrDefault("LOJINHA_SENHA", "admin");
        return obterToken(login, senha);
    }
}
