package com.example.userservice.domain.ports.input;

import com.example.userservice.application.dto.*;

/**
 * Use case interface for DeleteUser operation.
 * <p>
 * This interface defines the contract for the DeleteUser use case,
 * serving as an input port in the Clean Architecture. It encapsulates
 * the business logic interface without implementation details.
 * </p>
 * 
 * @author Jiliar Silgado
 * @version 1.0
 */
public interface DeleteUserUseCase {
    
    DeleteUserResponseContent execute(String request);
}

