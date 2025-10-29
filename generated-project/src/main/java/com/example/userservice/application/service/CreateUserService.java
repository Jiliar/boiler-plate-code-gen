package com.example.userservice.application.service;

import com.example.userservice.domain.ports.input.CreateUserUseCase;
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
 * Application service implementing CreateUser use case.
 * <p>
 * This service contains the business logic for CreateUser operation,
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
public class CreateUserService implements CreateUserUseCase {

    private final UserRepositoryPort userRepositoryPort;
    private final UserMapper userMapper;

    @Override
    public CreateUserResponseContent execute(CreateUserRequestContent request) {
        log.info("Executing CreateUser with request: {}", request);
        
        try {
            // Convert request to domain model using mapper
            User user = userMapper.fromCreateRequest(request);
            
            User savedUser = userRepositoryPort.save(user);
            
            return userMapper.toCreateResponse(savedUser);
            
        } catch (com.example.userservice.infrastructure.config.NotFoundException e) {
            log.error("User not found in CreateUser: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error in CreateUser: {}", e.getMessage(), e);
            throw e;
        }
    }
}