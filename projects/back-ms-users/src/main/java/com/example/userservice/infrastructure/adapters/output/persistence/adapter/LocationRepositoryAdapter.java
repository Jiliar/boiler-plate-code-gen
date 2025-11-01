
package com.example.userservice.infrastructure.adapters.output.persistence.adapter;

import com.example.userservice.domain.ports.output.LocationRepositoryPort;
import com.example.userservice.domain.model.Location;
import com.example.userservice.infrastructure.adapters.output.persistence.entity.LocationDbo;
import com.example.userservice.infrastructure.adapters.output.persistence.repository.JpaLocationRepository;
import com.example.userservice.application.mapper.LocationMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;

/**
 * Repository adapter implementing the Location domain port.
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
public class LocationRepositoryAdapter implements LocationRepositoryPort {

    private final JpaLocationRepository jpaRepository;
    private final LocationMapper mapper;

    @Override
    public Location save(Location location) {
        log.debug("Saving Location: {}", location);
        LocationDbo dbo = mapper.toDbo(location);
        LocationDbo savedDbo = jpaRepository.save(dbo);
        return mapper.toDomain(savedDbo);
    }

    @Override
    public Optional<Location> findById(String id) {
        log.debug("Finding Location by id: {}", id);
        return jpaRepository.findById(id)
                .map(mapper::toDomain);
    }

    @Override
    public List<Location> findAll() {
        log.debug("Finding all Locations");
        return mapper.toDomainList(jpaRepository.findAll());
    }

    @Override
    public void deleteById(String id) {
        log.debug("Deleting Location by id: {}", id);
        jpaRepository.deleteById(id);
    }

    @Override
    public boolean existsById(String id) {
        log.debug("Checking if Location exists by id: {}", id);
        return jpaRepository.existsById(id);
    }

    // Additional business methods with pagination
    public Page<Location> findBySearchTerm(String search, Pageable pageable) {
        log.debug("Searching Locations with term: {} and pagination: {}", search, pageable);
        return jpaRepository.findBySearchTerm(search, pageable)
                .map(mapper::toDomain);
    }
    
    public Page<Location> findAllPaged(Pageable pageable) {
        log.debug("Finding all Locations with pagination: {}", pageable);
        return jpaRepository.findAllPaged(pageable)
                .map(mapper::toDomain);
    }
}
