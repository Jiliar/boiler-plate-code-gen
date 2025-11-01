
package com.example.movieservice.infrastructure.adapters.output.persistence.adapter;

import com.example.movieservice.domain.ports.output.MovieRepositoryPort;
import com.example.movieservice.domain.model.Movie;
import com.example.movieservice.infrastructure.adapters.output.persistence.entity.MovieDbo;
import com.example.movieservice.infrastructure.adapters.output.persistence.repository.JpaMovieRepository;
import com.example.movieservice.application.mapper.MovieMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;

/**
 * Repository adapter implementing the Movie domain port.
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
public class MovieRepositoryAdapter implements MovieRepositoryPort {

    private final JpaMovieRepository jpaRepository;
    private final MovieMapper mapper;

    @Override
    public Movie save(Movie movie) {
        log.debug("Saving Movie: {}", movie);
        MovieDbo dbo = mapper.toDbo(movie);
        MovieDbo savedDbo = jpaRepository.save(dbo);
        return mapper.toDomain(savedDbo);
    }

    @Override
    public Optional<Movie> findById(String id) {
        log.debug("Finding Movie by id: {}", id);
        return jpaRepository.findById(id)
                .map(mapper::toDomain);
    }

    @Override
    public List<Movie> findAll() {
        log.debug("Finding all Movies");
        return mapper.toDomainList(jpaRepository.findAll());
    }

    @Override
    public void deleteById(String id) {
        log.debug("Deleting Movie by id: {}", id);
        jpaRepository.deleteById(id);
    }

    @Override
    public boolean existsById(String id) {
        log.debug("Checking if Movie exists by id: {}", id);
        return jpaRepository.existsById(id);
    }

    // Additional business methods with pagination
    public Page<Movie> findBySearchTerm(String search, Pageable pageable) {
        log.debug("Searching Movies with term: {} and pagination: {}", search, pageable);
        return jpaRepository.findBySearchTerm(search, pageable)
                .map(mapper::toDomain);
    }
    
    public Page<Movie> findAllPaged(Pageable pageable) {
        log.debug("Finding all Movies with pagination: {}", pageable);
        return jpaRepository.findAllPaged(pageable)
                .map(mapper::toDomain);
    }
}
