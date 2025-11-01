$version: "2"

namespace com.example.userservice

use aws.protocols#restJson1

@title("Location Service API")
@cors(origin: "*")
@restJson1
@documentation("A service for managing user locations including countries, regions, cities, addresses, and neighborhoods.")
service LocationService {
    version: "2023-01-01",
    operations: [
        CreateLocation,
        GetLocation,
        UpdateLocation,
        DeleteLocation,
        ListLocations,
        GetCountries,
        GetRegionsByCountry,
        GetCitiesByRegion,
        GetNeighborhoodsByCity
    ]
}

// Location Operations
@http(method: "POST", uri: "/locations")
operation CreateLocation {
    input: CreateLocationRequest,
    output: CreateLocationResponse,
    errors: [ValidationError, ConflictError]
}

@http(method: "GET", uri: "/locations/{locationId}")
operation GetLocation {
    input: GetLocationRequest,
    output: GetLocationResponse,
    errors: [NotFoundError]
}

@http(method: "PUT", uri: "/locations/{locationId}")
operation UpdateLocation {
    input: UpdateLocationRequest,
    output: UpdateLocationResponse,
    errors: [ValidationError, NotFoundError]
}

@http(method: "DELETE", uri: "/locations/{locationId}")
operation DeleteLocation {
    input: DeleteLocationRequest,
    output: DeleteLocationResponse,
    errors: [NotFoundError]
}

@http(method: "GET", uri: "/locations")
operation ListLocations {
    input: ListLocationsRequest,
    output: ListLocationsResponse
}

// Geographic Data Operations
@http(method: "GET", uri: "/countries")
operation GetCountries {
    input: GetCountriesRequest,
    output: GetCountriesResponse
}

@http(method: "GET", uri: "/countries/{countryId}/regions")
operation GetRegionsByCountry {
    input: GetRegionsByCountryRequest,
    output: GetRegionsByCountryResponse,
    errors: [NotFoundError]
}

@http(method: "GET", uri: "/regions/{regionId}/cities")
operation GetCitiesByRegion {
    input: GetCitiesByRegionRequest,
    output: GetCitiesByRegionResponse,
    errors: [NotFoundError]
}

@http(method: "GET", uri: "/cities/{cityId}/neighborhoods")
operation GetNeighborhoodsByCity {
    input: GetNeighborhoodsByCityRequest,
    output: GetNeighborhoodsByCityResponse,
    errors: [NotFoundError]
}

// Location Structures
structure CreateLocationRequest {
    @httpPayload
    body: CreateLocationRequestContent
}

structure CreateLocationRequestContent {
    @required
    userId: String,
    
    @required
    countryId: String,
    
    @required
    regionId: String,
    
    @required
    cityId: String,
    
    neighborhoodId: String,
    
    @required
    address: String,
    
    postalCode: String,
    
    latitude: Double,
    
    longitude: Double,
    
    @required
    locationType: LocationType
}

structure CreateLocationResponse {
    @httpPayload
    body: CreateLocationResponseContent
}

structure CreateLocationResponseContent {
    @required
    locationId: String,
    
    @required
    userId: String,
    
    @required
    countryId: String,
    
    @required
    regionId: String,
    
    @required
    cityId: String,
    
    neighborhoodId: String,
    
    @required
    address: String,
    
    postalCode: String,
    
    latitude: Double,
    
    longitude: Double,
    
    @required
    locationType: LocationType,
    
    @required
    createdAt: String,
    
    @required
    status: String
}

structure GetLocationRequest {
    @httpLabel
    @required
    locationId: String
}

structure GetLocationResponse {
    @httpPayload
    body: GetLocationResponseContent
}

structure GetLocationResponseContent {
    @required
    locationId: String,
    
    @required
    userId: String,
    
    @required
    country: CountryInfo,
    
    @required
    region: RegionInfo,
    
    @required
    city: CityInfo,
    
    neighborhood: NeighborhoodInfo,
    
    @required
    address: String,
    
    postalCode: String,
    
    latitude: Double,
    
    longitude: Double,
    
    @required
    locationType: LocationType,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String,
    
    @required
    status: String
}

structure UpdateLocationRequest {
    @httpLabel
    @required
    locationId: String,
    
    @httpPayload
    body: UpdateLocationRequestContent
}

structure UpdateLocationRequestContent {
    countryId: String,
    regionId: String,
    cityId: String,
    neighborhoodId: String,
    address: String,
    postalCode: String,
    latitude: Double,
    longitude: Double,
    locationType: LocationType
}

structure UpdateLocationResponse {
    @httpPayload
    body: UpdateLocationResponseContent
}

structure UpdateLocationResponseContent {
    @required
    locationId: String,
    
    @required
    userId: String,
    
    @required
    country: CountryInfo,
    
    @required
    region: RegionInfo,
    
    @required
    city: CityInfo,
    
    neighborhood: NeighborhoodInfo,
    
    @required
    address: String,
    
    postalCode: String,
    
    latitude: Double,
    
    longitude: Double,
    
    @required
    locationType: LocationType,
    
    @required
    updatedAt: String,
    
    @required
    status: String
}

structure DeleteLocationRequest {
    @httpLabel
    @required
    locationId: String
}

structure DeleteLocationResponse {
    @httpPayload
    body: DeleteLocationResponseContent
}

structure DeleteLocationResponseContent {
    @required
    deleted: Boolean,
    
    @required
    message: String
}

structure ListLocationsRequest {
    @httpQuery("page")
    page: Integer,
    
    @httpQuery("size")
    size: Integer,
    
    @httpQuery("userId")
    userId: String,
    
    @httpQuery("locationType")
    locationType: LocationType
}

structure ListLocationsResponse {
    @httpPayload
    body: ListLocationsResponseContent
}

structure ListLocationsResponseContent {
    @required
    locations: LocationList,
    
    @required
    page: Integer,
    
    @required
    size: Integer,
    
    @required
    total: Integer,
    
    @required
    totalPages: Integer
}

// Geographic Data Structures
structure GetCountriesRequest {
    @httpQuery("search")
    search: String
}

structure GetCountriesResponse {
    @httpPayload
    body: GetCountriesResponseContent
}

structure GetCountriesResponseContent {
    @required
    countries: CountryList
}

structure GetRegionsByCountryRequest {
    @httpLabel
    @required
    countryId: String
}

structure GetRegionsByCountryResponse {
    @httpPayload
    body: GetRegionsByCountryResponseContent
}

structure GetRegionsByCountryResponseContent {
    @required
    regions: RegionList
}

structure GetCitiesByRegionRequest {
    @httpLabel
    @required
    regionId: String
}

structure GetCitiesByRegionResponse {
    @httpPayload
    body: GetCitiesByRegionResponseContent
}

structure GetCitiesByRegionResponseContent {
    @required
    cities: CityList
}

structure GetNeighborhoodsByCityRequest {
    @httpLabel
    @required
    cityId: String
}

structure GetNeighborhoodsByCityResponse {
    @httpPayload
    body: GetNeighborhoodsByCityResponseContent
}

structure GetNeighborhoodsByCityResponseContent {
    @required
    neighborhoods: NeighborhoodList
}

// Common Structures
structure LocationResponse {
    @required
    locationId: String,
    
    @required
    userId: String,
    
    @required
    country: CountryInfo,
    
    @required
    region: RegionInfo,
    
    @required
    city: CityInfo,
    
    neighborhood: NeighborhoodInfo,
    
    @required
    address: String,
    
    postalCode: String,
    
    latitude: Double,
    
    longitude: Double,
    
    @required
    locationType: LocationType,
    
    @required
    status: String
}

structure CountryInfo {
    @required
    countryId: String,
    
    @required
    name: String,
    
    @required
    code: String,
    
    @required
    status: String,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String
}

structure RegionInfo {
    @required
    regionId: String,
    
    @required
    name: String,
    
    @required
    code: String,
    
    @required
    status: String,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String
}

structure CityInfo {
    @required
    cityId: String,
    
    @required
    name: String,
    
    @required
    status: String,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String
}

structure NeighborhoodInfo {
    @required
    neighborhoodId: String,
    
    @required
    name: String,
    
    @required
    status: String,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String
}

structure CountryResponse {
    @required
    countryId: String,
    
    @required
    name: String,
    
    @required
    code: String,
    
    @required
    status: String,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String
}

structure RegionResponse {
    @required
    regionId: String,
    
    @required
    name: String,
    
    @required
    code: String,
    
    @required
    countryId: String,
    
    @required
    status: String,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String
}

structure CityResponse {
    @required
    cityId: String,
    
    @required
    name: String,
    
    @required
    regionId: String,
    
    @required
    status: String,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String
}

structure NeighborhoodResponse {
    @required
    neighborhoodId: String,
    
    @required
    name: String,
    
    @required
    cityId: String,
    
    @required
    status: String,
    
    @required
    createdAt: String,
    
    @required
    updatedAt: String
}

// Lists
list LocationList {
    member: LocationResponse
}

list CountryList {
    member: CountryResponse
}

list RegionList {
    member: RegionResponse
}

list CityList {
    member: CityResponse
}

list NeighborhoodList {
    member: NeighborhoodResponse
}

// Enums
enum LocationType {
    HOME = "HOME",
    WORK = "WORK",
    BILLING = "BILLING",
    SHIPPING = "SHIPPING",
    OTHER = "OTHER"
}

// Error Structures
@error("client")
@httpError(400)
structure ValidationError {
    @required
    message: String,
    
    @required
    field: String
}

@error("client")
@httpError(404)
structure NotFoundError {
    @required
    message: String
}

@error("client")
@httpError(409)
structure ConflictError {
    @required
    message: String
}

structure ValidationErrorResponseContent {
    @required
    message: String,
    
    @required
    field: String
}

structure NotFoundErrorResponseContent {
    @required
    message: String
}

structure ConflictErrorResponseContent {
    @required
    message: String
}