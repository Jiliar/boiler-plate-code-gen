package com.example.userservice.infrastructure.adapters.input.rest;

import com.example.userservice.domain.ports.input.*;
import com.example.userservice.application.dto.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;

/**
 * REST Controller for User operations.
 * <p>
 * This controller serves as the input adapter in the Clean Architecture,
 * handling HTTP requests and delegating business logic to use cases.
 * It follows REST conventions and provides endpoints for CRUD operations.
 * </p>
 * 
 * @author Jiliar Silgado
 * @version 1.0
 */
@Slf4j
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
@Tag(name = "User", description = "User management operations")
public class UserController {

    private final CreateUserUseCase createUserUseCase;
    private final GetUserUseCase getUserUseCase;
    private final UpdateUserUseCase updateUserUseCase;
    private final DeleteUserUseCase deleteUserUseCase;
    private final ListUsersUseCase listUsersUseCase;

    @PostMapping
    @Operation(summary = "Create a new User", description = "Creates a new User with the provided information")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "User created successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid input data"),
        @ApiResponse(responseCode = "409", description = "User already exists")
    })
    public ResponseEntity<CreateUserResponseContent> createUser(
            @Parameter(description = "User creation request", required = true)
            @Valid @RequestBody CreateUserRequestContent request) {
        log.info("Creating user with request: {}", request);
        CreateUserResponseContent response = createUserUseCase.execute(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{userId}")
    @Operation(summary = "Get User by ID", description = "Retrieves a User by its unique identifier")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "User found"),
        @ApiResponse(responseCode = "404", description = "User not found")
    })
    public ResponseEntity<GetUserResponseContent> getUser(
            @Parameter(description = "User unique identifier", required = true)
            @PathVariable String userId) {
        log.info("Getting user with id: {}", userId);
        GetUserResponseContent response = getUserUseCase.execute(userId);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/{userId}")
    @Operation(summary = "Update User", description = "Updates an existing User with new information")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "User updated successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid input data"),
        @ApiResponse(responseCode = "404", description = "User not found")
    })
    public ResponseEntity<UpdateUserResponseContent> updateUser(
            @Parameter(description = "User unique identifier", required = true)
            @PathVariable String userId,
            @Parameter(description = "User update request", required = true)
            @Valid @RequestBody UpdateUserRequestContent request) {
        log.info("Updating user {} with request: {}", userId, request);
        UpdateUserResponseContent response = updateUserUseCase.execute(userId, request);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{userId}")
    @Operation(summary = "Delete User", description = "Deletes a User by its unique identifier")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "User deleted successfully"),
        @ApiResponse(responseCode = "404", description = "User not found")
    })
    public ResponseEntity<DeleteUserResponseContent> deleteUser(
            @Parameter(description = "User unique identifier", required = true)
            @PathVariable String userId) {
        log.info("Deleting user with id: {}", userId);
        DeleteUserResponseContent response = deleteUserUseCase.execute(userId);
        return ResponseEntity.ok(response);
    }

    @GetMapping
    @Operation(summary = "List Users", description = "Retrieves a paginated list of Users with optional search")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Users retrieved successfully")
    })
    public ResponseEntity<ListUsersResponseContent> listUsers(
            @Parameter(description = "Page number (1-based)", example = "1")
            @RequestParam(defaultValue = "1") Integer page,
            @Parameter(description = "Page size", example = "20")
            @RequestParam(defaultValue = "20") Integer size,
            @Parameter(description = "Search term for filtering")
            @RequestParam(required = false) String search) {
        log.info("Listing users with page: {}, size: {}, search: {}", page, size, search);
        // TODO: Create ListUsersRequest DTO
        ListUsersResponseContent response = listUsersUseCase.execute(""); // Placeholder
        return ResponseEntity.ok(response);
    }
}