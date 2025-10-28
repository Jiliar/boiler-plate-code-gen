# Clean Architecture Spring Boot Generator

## Overview

This project generates complete Java Spring Boot applications following **Clean Architecture principles** from Smithy service definitions. It automatically creates a fully functional backend with proper layer separation and dependency inversion.

## Features

- ✅ **Clean Architecture Structure** with Domain, Application, and Infrastructure layers
- ✅ **Smithy Integration** - Generates OpenAPI specs from Smithy definitions
- ✅ **Complete Code Generation** - DTOs, Services, Controllers, Repositories, Entities
- ✅ **Dependency Inversion** - All dependencies point toward the domain layer
- ✅ **Spring Boot 3** with Jakarta EE support
- ✅ **MapStruct** for entity transformations
- ✅ **JPA/Hibernate** for persistence
- ✅ **Bean Validation** with proper annotations
- ✅ **Lombok** for boilerplate reduction

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
poetry install

# Install Java and Maven (if not already installed)
brew install maven
sdk install java 21.0.2-tem
sdk use java 21.0.2-tem
```

### 2. Generate Project

```bash
# Make script executable
chmod +x scripts/run-clean-architecture-generator.sh

# Run generator
./scripts/run-clean-architecture-generator.sh
```

### 3. Run Generated Project

```bash
cd generated-project

# Build and run
mvn spring-boot:run
```

### 4. Test API

```bash
# Create user
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123",
    "firstName": "John",
    "lastName": "Doe"
  }'

# Get user
curl http://localhost:8080/users/{userId}

# List users
curl http://localhost:8080/users
```

## Prerequisites

### System Requirements
- **Java 21** (recommended with SDKMAN)
- **Maven 3.8+**
- **Python 3.6+**
- **Smithy CLI** (optional, can use Maven plugin)

### Java Installation with SDKMAN
```bash
sdk install java 21.0.2-tem
sdk use java 21.0.2-tem
```

### Maven Installation
```bash
# Using Homebrew (macOS)
brew install maven

# Using SDKMAN
sdk install maven

# Verify installation
mvn -version
```

### Python Dependencies
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

The project uses `pyproject.toml` for dependency management:
```toml
[tool.poetry.dependencies]
python = "^3.8"
pystache = "^0.6.8"
```

### Smithy CLI (Optional)
```bash
# Using Homebrew
brew tap smithy-lang/tap
brew install smithy-cli

# Verify installation
smithy --version
```

## Project Structure

```
boiler-plate-code-gen/
├── scripts/
│   ├── clean-architecture-generator.py    # Main generator script
│   └── run-clean-architecture-generator.sh # Execution script
├── openapi-templates/
│   └── java/
│       ├── pojo.mustache                  # DTOs and Domain Models
│       ├── apiService.mustache            # Application Services
│       ├── apiMapper.mustache             # MapStruct Mappers
│       ├── interface.mustache             # Use Cases and Ports
│       ├── apiController.mustache         # REST Controllers
│       ├── apiRepository.mustache         # JPA Repositories & Adapters
│       ├── apiEntity.mustache             # JPA Entities
│       ├── Application.mustache           # Main Spring Boot Class
│       ├── Configuration.mustache         # Spring Configuration
│       ├── pom.xml.mustache              # Maven POM
│       ├── application.properties.mustache # Spring Properties
│       ├── README.md.mustache            # Project README
│       └── template-config.json          # Generator Configuration
├── smithy/
│   └── user-service.smithy               # Smithy Service Definition
├── build/
│   └── smithy/
│       └── user_service/
│           └── openapi/
│               └── UserService.openapi.json # Generated OpenAPI Spec
└── generated-project/                    # Output Directory
```

## Generator Usage

### Basic Usage

```bash
python3 scripts/clean-architecture-generator.py <config_path> <templates_dir> <output_dir>
```

### Example

```bash
python3 scripts/clean-architecture-generator.py \
  openapi-templates/java/template-config.json \
  openapi-templates/java \
  generated-project
```

### Using the Shell Script

```bash
./scripts/run-clean-architecture-generator.sh
```

## Generated Architecture

The generator creates a complete Clean Architecture project with proper package structure:

```
generated-project/
├── src/main/java/com/example/userservice/
│   ├── domain/
│   │   ├── model/User.java                    # Pure domain entities
│   │   └── ports/
│   │       ├── input/CreateUserUseCase.java   # Use case interfaces
│   │       └── output/UserRepositoryPort.java # Repository interfaces
│   ├── application/
│   │   ├── dto/CreateUserRequestContent.java  # Data transfer objects
│   │   ├── service/CreateUserService.java     # Use case implementations
│   │   └── mapper/UserMapper.java             # Entity mappers
│   └── infrastructure/
│       ├── config/ApplicationConfiguration.java # Spring configuration
│       └── adapters/
│           ├── input/rest/UserController.java   # REST controllers
│           └── output/persistence/
│               ├── entity/UserDbo.java         # JPA entities
│               ├── repository/JpaUserRepository.java # Spring Data repos
│               └── adapter/UserRepositoryAdapter.java # Repository implementations
└── pom.xml
```

### Architecture Layers

#### Domain Layer (`domain/`)
- **Models**: Pure POJOs without framework dependencies
- **Input Ports**: Use case interfaces (e.g., `CreateUserUseCase`)
- **Output Ports**: Repository interfaces (e.g., `UserRepositoryPort`)

#### Application Layer (`application/`)
- **Services**: Use case implementations with business logic
- **DTOs**: Request/Response objects with validation
- **Mappers**: MapStruct interfaces for transformations

#### Infrastructure Layer (`infrastructure/`)
- **REST Controllers**: HTTP endpoints and request handling
- **JPA Entities**: Database entities with annotations
- **JPA Repositories**: Spring Data repositories
- **Repository Adapters**: Implementations of domain ports
- **Configuration**: Spring Boot configuration classes

## Template Mapping Strategy

The generator intelligently maps existing templates to Clean Architecture layers:

| Template | Domain Layer | Application Layer | Infrastructure Layer |
|----------|-------------|-------------------|---------------------|
| `pojo.mustache` | Domain Model | DTO | - |
| `apiEntity.mustache` | - | - | JPA Entity |
| `interface.mustache` | Use Case Port | - | - |
| `apiService.mustache` | - | Use Case Implementation | - |
| `apiController.mustache` | - | - | REST Controller |
| `apiRepository.mustache` | Repository Port | - | JPA Repository + Adapter |

## Configuration

### Template Configuration (`openapi-templates/java/template-config.json`)

Key configuration options:
```json
{
  "configOptions": {
    "basePackage": "com.example.userservice",
    "mainClass": "UserServiceApplication",
    "useSpringBoot3": "true",
    "useJakartaEe": "true",
    "useBeanValidation": "true",
    "java21": "true"
  }
}
```

## Smithy Service Definition

### 1. Define Your Service in Smithy

Create or modify `smithy/user-service.smithy`:

```smithy
@title("User Service API")
@cors(origin: "*")
@restJson1
@documentation("A service for managing user accounts.")
service UserService {
    version: "2023-01-01",
    operations: [
        CreateUser,
        GetUser, 
        UpdateUser,
        DeleteUser,
        ListUsers
    ]
}

@http(method: "POST", uri: "/users")
operation CreateUser {
    input: CreateUserRequest,
    output: CreateUserResponse,
    errors: [ValidationError, ConflictError]
}

// Define your structures, operations, etc.
```

## Generated Components

### Example Generated Files

1. **Domain Model** (`domain/model/User.java`)
```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {
    private String userId;
    private String username;
    private String email;
    // ... other fields
}
```

2. **Use Case Interface** (`domain/ports/input/CreateUserUseCase.java`)
```java
public interface CreateUserUseCase {
    CreateUserResponseContent execute(CreateUserRequestContent request);
}
```

3. **Application Service** (`application/service/CreateUserService.java`)
```java
@Service
@RequiredArgsConstructor
public class CreateUserService implements CreateUserUseCase {
    private final UserRepositoryPort userRepositoryPort;
    
    @Override
    public CreateUserResponseContent execute(CreateUserRequestContent request) {
        // Business logic implementation
    }
}
```

4. **REST Controller** (`infrastructure/adapters/input/rest/UserController.java`)
```java
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {
    private final CreateUserUseCase createUserUseCase;
    
    @PostMapping
    public ResponseEntity<CreateUserResponseContent> createUser(@Valid @RequestBody CreateUserRequestContent request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(createUserUseCase.execute(request));
    }
}
```

## Generated Dependencies

The generated `pom.xml` includes:
- Spring Boot 3.x (Web, Data JPA, Validation)
- Jakarta EE APIs
- MapStruct for mapping
- Lombok for boilerplate reduction
- H2/PostgreSQL for database
- JUnit 5 for testing

## API Endpoints

Generated REST API endpoints:
- `POST /users` - Create user
- `GET /users/{userId}` - Get user by ID
- `PUT /users/{userId}` - Update user
- `DELETE /users/{userId}` - Delete user
- `GET /users` - List users with pagination and search

## Architecture Principles

The generator ensures:

1. **Dependency Rule**: Dependencies point inward toward the domain
2. **Interface Segregation**: Small, focused interfaces for each use case
3. **Single Responsibility**: Each class has one reason to change
4. **Dependency Inversion**: High-level modules don't depend on low-level modules

## Development Workflow

1. **Define Service**: Create/modify Smithy service definition
2. **Generate Code**: Run the generator script
3. **Implement Business Logic**: Add specific business rules in services
4. **Add Tests**: Create unit and integration tests
5. **Configure Database**: Update `application.properties` for your database
6. **Deploy**: Build and deploy the Spring Boot application

## Customization

### Adding New Operations
1. Add operation to Smithy service definition
2. Run generator to create new use cases and endpoints
3. Implement business logic in generated services

### Adding New Entities

Modify the `entities` list in the `generate_complete_project()` method:

```python
entities = ["User", "Product", "Order"]
```

### Adding New Operations

Modify the `operations` list:

```python
operations = ["CreateUser", "GetUser", "UpdateUser", "DeleteUser", "SearchUsers"]
```

### Modifying Templates
1. Edit Mustache templates in `openapi-templates/java/`
2. Regenerate project to apply changes

### Extending Entities
1. Add fields to Smithy structures
2. Regenerate to update DTOs, entities, and mappers

## Best Practices

1. **Keep Domain Pure**: Domain layer should have no external dependencies
2. **Use Ports and Adapters**: All external communication goes through interfaces
3. **Test Each Layer**: Unit test domain logic, integration test adapters
4. **Follow Naming Conventions**: UseCase, Port, Adapter, Dbo suffixes
5. **Maintain Dependency Direction**: Always point toward the domain

## Troubleshooting

### Common Issues

1. **Python Dependencies Missing**
   ```bash
   poetry install
   ```

2. **Smithy Build Fails**
   ```bash
   smithy build --debug
   ```

3. **Generated Code Compilation Errors**
   - Check Java version (requires Java 21)
   - Verify Maven dependencies
   - Ensure proper package structure

4. **Template Rendering Issues**
   - Verify Mustache template syntax
   - Check context variables in generator script

5. **Missing Templates**: Ensure all required `.mustache` files exist
6. **Package Conflicts**: Check that `basePackage` is correctly set
7. **Permission Errors**: Ensure output directory is writable

## Extension Points

The generator can be extended to:

- Parse OpenAPI specifications directly
- Generate test classes
- Add more architectural patterns
- Support different frameworks (Quarkus, Micronaut)
- Generate documentation

## Contributing

1. Fork the repository
2. Create feature branch
3. Add/modify templates or generator logic
4. Test with sample Smithy services
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review generated code structure
3. Verify Smithy service definition
4. Check Python and Java versions