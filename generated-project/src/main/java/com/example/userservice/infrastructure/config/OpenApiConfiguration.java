package com.example.userservice.infrastructure.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

/**
 * OpenAPI configuration for Swagger documentation.
 * <p>
 * This configuration customizes the OpenAPI specification for the service,
 * including API information, contact details, and server configuration.
 * </p>
 * 
 * @author Jiliar Silgado
 * @version 1.0
 */
@Configuration
public class OpenApiConfiguration {

    @Bean
    public OpenAPI userServiceOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("User Service API")
                        .description("Generated Spring Boot application from Smithy model")
                        .version("1.0.0"));
    }
}