package com.example.movieservice.domain.ports.output;


import com.example.movieservice.domain.model.Movie;
import java.util.List;
import java.util.Optional;

/**
 * Domain repository port for Movie operations.
 * <p>
 * This interface defines the contract for Movie persistence operations,
 * serving as an output port in the Clean Architecture. It abstracts
 * the persistence layer from the domain logic.
 * </p>
 * 
 * @author Jiliar Silgado <jiliar.silgado@gmail.com>
 * @version 1.0.0
 */
public interface MovieRepositoryPort {
    
    Movie save(Movie movie);
    
    Optional<Movie> findById(String id);
    
    List<Movie> findAll();
    
    void deleteById(String id);
    
    boolean existsById(String id);
}
