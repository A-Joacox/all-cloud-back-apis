package com.cinema.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import io.swagger.v3.oas.models.tags.Tag;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Arrays;

@Configuration
public class SwaggerConfig {

    @Value("${server.port:3003}")
    private String serverPort;

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Reservations API")
                        .description("Cinema Reservations Microservice - PostgreSQL based API for managing users, reservations and payments")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Cinema API Team")
                                .email("api@cinema.com"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")))
                .servers(Arrays.asList(
                        new Server()
                                .url("http://localhost:" + serverPort)
                                .description("Development server"),
                        new Server()
                                .url("https://api.cinema.com")
                                .description("Production server")
                ))
                .tags(Arrays.asList(
                        new Tag()
                                .name("Users")
                                .description("User management operations"),
                        new Tag()
                                .name("Reservations")
                                .description("Reservation management operations"),
                        new Tag()
                                .name("Payments")
                                .description("Payment processing operations"),
                        new Tag()
                                .name("Health")
                                .description("Health check operations")
                ));
    }
}