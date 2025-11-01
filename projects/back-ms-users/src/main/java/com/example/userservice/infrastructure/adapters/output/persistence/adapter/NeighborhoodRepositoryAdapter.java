
package com.example.userservice.infrastructure.adapters.output.persistence.adapter;

import com.example.userservice.domain.ports.output.NeighborhoodRepositoryPort;
import com.example.userservice.domain.model.Neighborhood;
import com.example.userservice.infrastructure.adapters.output.persistence.entity.NeighborhoodDbo;
import com.example.userservice.infrastructure.adapters.output.persistence.repository.JpaNeighborhoodRepository;
import com.example.userservice.application.mapper.NeighborhoodMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;

/**
 * Repository adapter implementing the Neighborhood domain port.
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
public class NeighborhoodRepositoryAdapter implements NeighborhoodRepositoryPort {

    private final JpaNeighborhoodRepository jpaRepository;
    private final NeighborhoodMapper mapper;

    @Override
    public Neighborhood save(Neighborhood neighborhood) {
        log.debug("Saving Neighborhood: {}", neighborhood);
        NeighborhoodDbo dbo = mapper.toDbo(neighborhood);
        NeighborhoodDbo savedDbo = jpaRepository.save(dbo);
        return mapper.toDomain(savedDbo);
    }

    @Override
    public Optional<Neighborhood> findById(String id) {
        log.debug("Finding Neighborhood by id: {}", id);
        return jpaRepository.findById(id)
                .map(mapper::toDomain);
    }

    @Override
    public List<Neighborhood> findAll() {
        log.debug("Finding all Neighborhoods");
        return mapper.toDomainList(jpaRepository.findAll());
    }

    @Override
    public void deleteById(String id) {
        log.debug("Deleting Neighborhood by id: {}", id);
        jpaRepository.deleteById(id);
    }

    @Override
    public boolean existsById(String id) {
        log.debug("Checking if Neighborhood exists by id: {}", id);
        return jpaRepository.existsById(id);
    }

    // Additional business methods with pagination
    public Page<Neighborhood> findBySearchTerm(String search, Pageable pageable) {
        log.debug("Searching Neighborhoods with term: {} and pagination: {}", search, pageable);
        return jpaRepository.findBySearchTerm(search, pageable)
                .map(mapper::toDomain);
    }
    
    public Page<Neighborhood> findAllPaged(Pageable pageable) {
        log.debug("Finding all Neighborhoods with pagination: {}", pageable);
        return jpaRepository.findAllPaged(pageable)
                .map(mapper::toDomain);
    }
}
