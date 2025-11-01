# PyJava Backend Code Generator

A modular Python library for generating Java Spring Boot applications following Hexagonal Architecture principles from Smithy service definitions.

## Architecture

The library is structured following clean separation of concerns:

### Core Components

- **`config_loader.py`**: Handles project configuration loading and package structure definition
- **`openapi_processor.py`**: Processes OpenAPI specifications and extracts schemas/operations
- **`template_renderer.py`**: Renders Mustache templates with context data
- **`file_manager.py`**: Manages file system operations and directory structure
- **`property_converter.py`**: Converts OpenAPI properties to Java types with validation
- **`code_generator.py`**: Main orchestrator that coordinates the entire generation process

### Design Principles

- **Single Responsibility**: Each component has a single, well-defined purpose
- **Dependency Injection**: Components are loosely coupled and easily testable
- **Separation of Concerns**: Business logic is separated from infrastructure concerns
- **Modularity**: Each component can be used independently or replaced

## Usage

### As a Library

```python
from pyjava_backend_codegen import CodeGenerator, ConfigLoader

# Load configuration
config = ConfigLoader.load_projects_config("config/params.json")

# Generate project
for project_config in config:
    generator = CodeGenerator("templates/java", project_config)
    generator.generate_complete_project()
```

### As a Module

```bash
python -m pyjava_backend_codegen templates/java
```

### Using the Bridge Script

```bash
python libs/hexagonal-architecture-generator-v2.py templates/java
```

## Components Overview

### ConfigLoader
- Loads JSON configuration files
- Builds package structures for hexagonal architecture
- Creates Mustache template contexts

### OpenApiProcessor
- Loads OpenAPI specifications from Smithy build output
- Extracts schemas, operations, and entities
- Groups operations by entity for consolidated services

### TemplateRenderer
- Renders Mustache templates with context data
- Handles HTML entity escaping
- Provides clean template rendering interface

### FileManager
- Manages file system operations
- Creates directory structures
- Handles Java package path conversions

### PropertyConverter
- Converts OpenAPI properties to Java types
- Generates validation annotations
- Handles type mapping and imports

### CodeGenerator
- Main orchestrator for the generation process
- Coordinates all components
- Manages the complete project generation workflow

## Benefits of This Architecture

1. **Maintainability**: Each component is focused and easy to understand
2. **Testability**: Components can be unit tested in isolation
3. **Extensibility**: New features can be added without affecting existing code
4. **Reusability**: Components can be reused in different contexts
5. **Debugging**: Issues can be isolated to specific components

## Migration from Monolithic Script

The original monolithic script has been refactored into this modular library while maintaining the same functionality and API compatibility. The new architecture provides better code organization and maintainability.