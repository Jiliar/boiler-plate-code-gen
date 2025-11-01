package com.example.userservice.infrastructure.adapters.output.persistence.repository;

import com.example.userservice.infrastructure.adapters.output.persistence.entity.UserDbo;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

/**
 * Spring Data JPA Repository for User entities.
 * <p>
 * This interface extends JpaRepository to provide standard CRUD operations
 * and includes custom query methods for specific business requirements.
 * It operates on UserDbo entities for database persistence.
 * </p>
 * 
 * @author Jiliar Silgado <jiliar.silgado@gmail.com>
 * @version 1.0.0
 */
@Repository
public interface JpaUserRepository extends JpaRepository<UserDbo, String> {
    
    /**
     * Find entities with pagination and search functionality.
     * 
     * 
     * Searches by ID when no text fields are available.
     * 
     */
    @Query("SELECT e FROM UserDbo e WHERE " +
           "(:search IS NULL OR " +
           "LOWER(CAST(e.id AS string)) LIKE LOWER(CONCAT('%', :search, '%')))")
    Page<UserDbo> findBySearchTerm(@Param("search") String search, Pageable pageable);
    
    /**
     * Find all entities with pagination.
     */
    @Query("SELECT e FROM UserDbo e")
    Page<UserDbo> findAllPaged(Pageable pageable);
}

