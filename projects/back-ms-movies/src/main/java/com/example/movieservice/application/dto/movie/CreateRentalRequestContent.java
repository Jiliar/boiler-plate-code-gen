package com.example.movieservice.application.dto.movie;

import java.math.BigDecimal;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import io.swagger.v3.oas.annotations.media.Schema;

/**
 * Data Transfer Object for CreateRentalRequestContent.
 * <p>
 * This class represents data transferred between the application layers,
 * containing validation annotations and JSON serialization configuration.
 * It serves as the contract for API communication in Clean Architecture.
 * </p>
 * 
 * @author Jiliar Silgado <jiliar.silgado@gmail.com>
 * @version 1.0.0
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Data Transfer Object for CreateRentalRequestContent")
public class CreateRentalRequestContent {

    @NotNull
    @JsonProperty("movieId")
    @Schema(description = "movieId field")
    private String movieId;

    @NotNull
    @JsonProperty("userId")
    @Schema(description = "userId field")
    private String userId;

    @NotNull
    @JsonProperty("rentalDays")
    @Schema(description = "rentalDays field")
    private BigDecimal rentalDays;
}
