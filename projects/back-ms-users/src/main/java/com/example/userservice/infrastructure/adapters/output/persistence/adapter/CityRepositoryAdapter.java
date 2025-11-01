
package com.example.userservice.infrastructure.adapters.output.persistence.adapter;

import com.example.userservice.domain.ports.output.CityRepositoryPort;
import com.example.userservice.domain.model.City;
import com.example.userservice.infrastructure.adapters.output.persistence.entity.CityDbo;
import com.example.userservice.infrastructure.adapters.output.persistence.repository.JpaCityRepository;
import com.example.userservice.application.mapper.CityMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;

/**
 * Repository adapter implementing the City domain port.
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
public class CityRepositoryAdapter implements CityRepositoryPort {

    private final JpaCityRepository jpaRepository;
    private final CityMapper mapper;

    @Override
    public City save(City city) {
        log.debug("Saving City: {}", city);
        CityDbo dbo = mapper.toDbo(city);
        CityDbo savedDbo = jpaRepository.save(dbo);
        return mapper.toDomain(savedDbo);
    }

    @Override
    public Optional<City> findById(String id) {
        log.debug("Finding City by id: {}", id);
        return jpaRepository.findById(id)
                .map(mapper::toDomain);
    }

    @Override
    public List<City> findAll() {
        log.debug("Finding all Citys");
        return mapper.toDomainList(jpaRepository.findAll());
    }

    @Override
    public void deleteById(String id) {
        log.debug("Deleting City by id: {}", id);
        jpaRepository.deleteById(id);
    }

    @Override
    public boolean existsById(String id) {
        log.debug("Checking if City exists by id: {}", id);
        return jpaRepository.existsById(id);
    }

    // Additional business methods with pagination
    public Page<City> findBySearchTerm(String search, Pageable pageable) {
        log.debug("Searching Citys with term: {} and pagination: {}", search, pageable);
        return jpaRepository.findBySearchTerm(search, pageable)
                .map(mapper::toDomain);
    }
    
    public Page<City> findAllPaged(Pageable pageable) {
        log.debug("Finding all Citys with pagination: {}", pageable);
        return jpaRepository.findAllPaged(pageable)
                .map(mapper::toDomain);
    }
}
