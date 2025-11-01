package com.example.userservice.application.mapper;

import com.example.userservice.domain.model.Region;
import com.example.userservice.infrastructure.adapters.output.persistence.entity.RegionDbo;
import com.example.userservice.application.dto.location.RegionResponse;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.IterableMapping;
import org.mapstruct.NullValuePropertyMappingStrategy;
import org.mapstruct.factory.Mappers;
import java.util.List;
import java.math.BigDecimal;

/**
 * MapStruct mapper for Region transformations between layers.
 * <p>
 * This mapper handles conversions between:
 * - Domain models (pure business objects)
 * - DTOs (data transfer objects for API communication)
 * - DBOs (database objects for persistence)
 * </p>
 * 
 * @author Jiliar Silgado <jiliar.silgado@gmail.com>
 * @version 1.0.0
 */
@Mapper(componentModel = "spring", nullValuePropertyMappingStrategy = org.mapstruct.NullValuePropertyMappingStrategy.IGNORE)
public interface RegionMapper {

    RegionMapper INSTANCE = Mappers.getMapper(RegionMapper.class);

    // Domain to DBO mappings
    @Mapping(source = "regionId", target = "id")
    @org.mapstruct.Named("domainToDbo")
    RegionDbo toDbo(Region domain);
    
    @Mapping(source = "id", target = "regionId")
    @org.mapstruct.Named("dboToDomain")
    Region toDomain(RegionDbo dbo);
    
    @IterableMapping(qualifiedByName = "dboToDomain")
    List<Region> toDomainList(List<RegionDbo> dbos);
    
    @IterableMapping(qualifiedByName = "domainToDbo")
    List<RegionDbo> toDboList(List<Region> domains);

    // DTO to Domain mappings for Create/Update operations
    

    // Basic mapping methods - MapStruct will handle field mapping automatically
    @org.mapstruct.Named("domainToDto")
    RegionResponse toDto(Region domain);
    
    @IterableMapping(qualifiedByName = "domainToDto")
    List<RegionResponse> toDtoList(List<Region> domains);

    // Specific response mapping methods
    
}