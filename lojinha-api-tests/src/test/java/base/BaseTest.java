package base;

import io.restassured.RestAssured;
import io.restassured.filter.log.RequestLoggingFilter;
import io.restassured.filter.log.ResponseLoggingFilter;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import org.junit.jupiter.api.BeforeAll;

import static io.restassured.RestAssured.given;

public abstract class BaseTest {

    protected static final String BASE_URI = System.getenv()
            .getOrDefault("LOJINHA_BASE_URI", "http://165.227.93.41/lojinha");

    @BeforeAll
    static void configurarRestAssured() {
        RestAssured.baseURI = BASE_URI;
        RestAssured.basePath = "/v2";
        RestAssured.filters(new RequestLoggingFilter(), new ResponseLoggingFilter());
    }

    protected static RequestSpecification comJson() {
        return given().contentType(ContentType.JSON);
    }

    protected static RequestSpecification comToken(String token) {
        return comJson().header("token", token);
    }
}
