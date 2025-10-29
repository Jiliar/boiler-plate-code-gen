package com.example.userservice.application.mapper;

import com.example.userservice.domain.model.User;
import com.example.userservice.infrastructure.adapters.output.persistence.entity.UserDbo;
import com.example.userservice.application.dto.*;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.factory.Mappers;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.math.BigDecimal;

/**
 * MapStruct mapper for User transformations between layers.
 * <p>
 * This mapper handles conversions between:
 * - Domain models (pure business objects)
 * - DTOs (data transfer objects for API communication)
 * - DBOs (database objects for persistence)
 * </p>
 * <p>
 * Includes custom methods for timestamp conversion between Double and LocalDateTime.
 * </p>
 * 
 * @author Jiliar Silgado
 * @version 1.0
 */
@Mapper(componentModel = "spring")
public interface UserMapper {

    UserMapper INSTANCE = Mappers.getMapper(UserMapper.class);

    // Domain to DBO mappings
    @Mapping(source = "userId", target = "id")
    UserDbo toDbo(User domain);
    
    @Mapping(source = "id", target = "userId")
    User toDomain(UserDbo dbo);
    List<User> toDomainList(List<UserDbo> dbos);

    // Domain to DTO mappings
    
    @Mapping(target = "userId", expression = "java(java.util.UUID.randomUUID().toString())")
    @Mapping(target = "status", constant = "ACTIVE")
    @Mapping(target = "createdAt", expression = "java(java.time.Instant.now().toString())")
    @Mapping(target = "updatedAt", ignore = true)
    User fromCreateRequest(CreateUserRequestContent request);
    @Mapping(target = "updatedAt", expression = "java(java.time.Instant.now().toString())")
    @Mapping(target = "userId", ignore = true)
    @Mapping(target = "status", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    User fromUpdateRequest(UpdateUserRequestContent request);
    
    // DTO to Domain mappings
    List<UserResponse> toResponseList(List<User> domains);
    
    // Individual response mapping
    UserResponse toResponse(User domain);
    
    // Response mappings for DTOs
    default CreateUserResponseContent toCreateResponse(User domain) {
        if (domain == null) return null;
        return CreateUserResponseContent.builder()
            .userId(domain.getUserId())
            .username(domain.getUsername())
            .email(domain.getEmail())
            .firstName(domain.getFirstName())
            .lastName(domain.getLastName())
            .status(domain.getStatus())
            .createdAt(domain.getCreatedAt())
            .updatedAt(domain.getUpdatedAt())
            .build();
    }
    
    default GetUserResponseContent toGetResponse(User domain) {
        if (domain == null) return null;
        return GetUserResponseContent.builder()
            .userId(domain.getUserId())
            .username(domain.getUsername())
            .email(domain.getEmail())
            .firstName(domain.getFirstName())
            .lastName(domain.getLastName())
            .status(domain.getStatus())
            .createdAt(domain.getCreatedAt())
            .updatedAt(domain.getUpdatedAt())
            .build();
    }
    
    default UpdateUserResponseContent toUpdateResponse(User domain) {
        if (domain == null) return null;
        return UpdateUserResponseContent.builder()
            .userId(domain.getUserId())
            .username(domain.getUsername())
            .email(domain.getEmail())
            .firstName(domain.getFirstName())
            .lastName(domain.getLastName())
            .status(domain.getStatus())
            .createdAt(domain.getCreatedAt())
            .updatedAt(domain.getUpdatedAt())
            .build();
    }

    // List response mapping
    default ListUsersResponseContent toListResponse(List<User> domains) {
        if (domains == null) return null;
        return ListUsersResponseContent.builder()
            .users(toResponseList(domains))
            .page(BigDecimal.valueOf(1))
            .size(BigDecimal.valueOf(domains.size()))
            .total(BigDecimal.valueOf(domains.size()))
            .totalPages(BigDecimal.valueOf(1))
            .build();
    }
    
    // No timestamp conversion needed - all layers use String
}