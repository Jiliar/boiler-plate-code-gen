
package com.example.userservice.infrastructure.adapters.output.persistence.adapter;

import com.example.userservice.domain.ports.output.UserRepositoryPort;
import com.example.userservice.domain.model.User;
import com.example.userservice.infrastructure.adapters.output.persistence.entity.UserDbo;
import com.example.userservice.infrastructure.adapters.output.persistence.repository.JpaUserRepository;
import com.example.userservice.application.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;

/**
 * Repository adapter implementing the User domain port.
 * <p>
 * This adapter serves as the output adapter in Clean Architecture,
 * implementing the domain repository interface and delegating to
 * Spring Data JPA repository. It handles the conversion between
 * domain objects and database entities using MapStruct.
 * </p>
 * 
 * @author Jiliar Silgado <jiliar.silgado@gmail.com>
 * @version 1.0.0
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class UserRepositoryAdapter implements UserRepositoryPort {

    private final JpaUserRepository jpaRepository;
    private final UserMapper mapper;

    @Override
    public User save(User user) {
        log.debug("Saving User: {}", user);
        UserDbo dbo = mapper.toDbo(user);
        UserDbo savedDbo = jpaRepository.save(dbo);
        return mapper.toDomain(savedDbo);
    }

    @Override
    public Optional<User> findById(String id) {
        log.debug("Finding User by id: {}", id);
        return jpaRepository.findById(id)
                .map(mapper::toDomain);
    }

    @Override
    public List<User> findAll() {
        log.debug("Finding all Users");
        return mapper.toDomainList(jpaRepository.findAll());
    }

    @Override
    public void deleteById(String id) {
        log.debug("Deleting User by id: {}", id);
        jpaRepository.deleteById(id);
    }

    @Override
    public boolean existsById(String id) {
        log.debug("Checking if User exists by id: {}", id);
        return jpaRepository.existsById(id);
    }

    // Additional business methods with pagination
    public Page<User> findBySearchTerm(String search, Pageable pageable) {
        log.debug("Searching Users with term: {} and pagination: {}", search, pageable);
        return jpaRepository.findBySearchTerm(search, pageable)
                .map(mapper::toDomain);
    }
    
    public Page<User> findAllPaged(Pageable pageable) {
        log.debug("Finding all Users with pagination: {}", pageable);
        return jpaRepository.findAllPaged(pageable)
                .map(mapper::toDomain);
    }
}
