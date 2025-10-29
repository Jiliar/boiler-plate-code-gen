package com.example.userservice.application.service;

import com.example.userservice.domain.ports.input.ListUsersUseCase;
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
 * Application service implementing ListUsers use case.
 * <p>
 * This service contains the business logic for ListUsers operation,
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
public class ListUsersService implements ListUsersUseCase {

    private final UserRepositoryPort userRepositoryPort;
    private final UserMapper userMapper;

    @Override
    public ListUsersResponseContent execute(String request) {
        log.info("Executing ListUsers with request: {}", request);
        
        try {
            
            // List operation
            List<User> users = userRepositoryPort.findAll();
            
            // Build the list response manually
            List<UserResponse> responseList = userMapper.toResponseList(users);
            
            return ListUsersResponseContent.builder()
                .users(responseList)
                .page(BigDecimal.valueOf(1))
                .size(BigDecimal.valueOf(users.size()))
                .total(BigDecimal.valueOf(users.size()))
                .totalPages(BigDecimal.valueOf(1))
                .build();
            
        } catch (com.example.userservice.infrastructure.config.NotFoundException e) {
            log.error("User not found in ListUsers: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error in ListUsers: {}", e.getMessage(), e);
            throw e;
        }
    }
}