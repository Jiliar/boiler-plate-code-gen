package com.example.userservice.domain.ports.input;

import com.example.userservice.application.dto.location.CreateLocationRequestContent;
import com.example.userservice.application.dto.location.CreateLocationResponseContent;
import com.example.userservice.application.dto.location.GetLocationResponseContent;
import com.example.userservice.application.dto.location.UpdateLocationRequestContent;
import com.example.userservice.application.dto.location.UpdateLocationResponseContent;
import com.example.userservice.application.dto.location.DeleteLocationResponseContent;
import com.example.userservice.application.dto.location.ListLocationsResponseContent;
import com.example.userservice.application.dto.location.GetNeighborhoodsByCityResponseContent;
import com.example.userservice.application.dto.location.GetRegionsByCountryResponseContent;
import com.example.userservice.application.dto.location.GetCitiesByRegionResponseContent;

/**
 * Consolidated use case interface for all Location operations.
 * 
 * @author Jiliar Silgado <jiliar.silgado@gmail.com>
 * @version 1.0.0
 */
public interface LocationUseCase {
    
    CreateLocationResponseContent create(CreateLocationRequestContent request);

    GetLocationResponseContent get(String locationId);

    UpdateLocationResponseContent update(String locationId, UpdateLocationRequestContent request);

    DeleteLocationResponseContent delete(String locationId);

    ListLocationsResponseContent list(Integer page, Integer size, String search);

    GetNeighborhoodsByCityResponseContent getNeighborhoodsByCity();
    GetRegionsByCountryResponseContent getRegionsByCountry();
    GetCitiesByRegionResponseContent getCitiesByRegion();
}