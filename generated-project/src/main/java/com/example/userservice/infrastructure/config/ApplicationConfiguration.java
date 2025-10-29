package com.example.userservice.infrastructure.config;

import com.example.userservice.application.mapper.UserMapper;
import org.mapstruct.factory.Mappers;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

/**
 * Spring configuration class for application beans.
 * <p>
 * This configuration class defines beans required by the application,
 * including security components like password encoders and MapStruct mappers.
 * It serves as the infrastructure configuration in Clean Architecture.
 * </p>
 * 
 * @author Jiliar Silgado
 * @version 1.0
 */
@Configuration
@Import({SecurityConfiguration.class, OpenApiConfiguration.class})
public class ApplicationConfiguration {

    /**
     * Configures the password encoder bean for security operations.
     * 
     * @return BCryptPasswordEncoder instance for password hashing
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

}