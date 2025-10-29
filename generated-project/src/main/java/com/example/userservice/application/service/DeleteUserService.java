package com.example.userservice.application.service;

import com.example.userservice.domain.ports.input.DeleteUserUseCase;
import com.example.userservice.domain.ports.output.UserRepositoryPort;
import com.example.userservice.application.dto.*;
import com.example.userservice.domain.model.User;
import com.example.userservice.application.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.math.BigDecimal;

/**
 * Application service implementing DeleteUser use case.
 * <p>
 * This service contains the business logic for DeleteUser operation,
 * orchestrating domain objects and repository interactions. It serves as
 * the application layer in Clean Architecture, implementing use case interfaces
 * defined in the domain layer.
 * </p>
 * 
 * @author Jiliar Silgado
 * @version 1.0
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class DeleteUserService implements DeleteUserUseCase {

    private final UserRepositoryPort userRepositoryPort;
    private final UserMapper userMapper;

    @Override
    public DeleteUserResponseContent execute(String request) {
        log.info("Executing DeleteUser with request: {}", request);
        
        try {
            // Verify user exists before deletion
            User user = userRepositoryPort.findById(request)
                .orElseThrow(() -> new com.example.userservice.infrastructure.config.NotFoundException("User not found"));
            
            userRepositoryPort.deleteById(request);
            
            return DeleteUserResponseContent.builder()
                .deleted(true)
                .message("User deleted successfully")
                .build();
            
        } catch (com.example.userservice.infrastructure.config.NotFoundException e) {
            log.error("User not found in DeleteUser: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error in DeleteUser: {}", e.getMessage(), e);
            throw e;
        }
    }
}