# PyJava Backend CodeGen - Architecture Documentation

This directory contains the architectural documentation for the PyJava Backend Code Generator library.

## Diagrams

### Component Diagram (`component-diagram.puml`)
Shows the static structure of the library including:
- Core components and their responsibilities
- Dependencies between components
- External dependencies (pystache, json, pathlib, subprocess)
- File system interactions (templates, config, OpenAPI specs, output)

### Sequence Diagram (`sequence-diagram.puml`)
Illustrates the dynamic behavior during code generation:
- Complete flow from user execution to project generation
- Interactions between all components
- File operations and template rendering process
- Multi-project generation loop

## How to View Diagrams

### Online PlantUML Editor
1. Copy the content of `.puml` files
2. Paste into [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
3. View the rendered diagram

### VS Code Extension
1. Install "PlantUML" extension
2. Open `.puml` files in VS Code
3. Use `Alt+D` to preview diagrams

### Command Line
```bash
# Install PlantUML
brew install plantuml  # macOS
# or
sudo apt-get install plantuml  # Ubuntu

# Generate PNG images
plantuml component-diagram.puml
plantuml sequence-diagram.puml
```

## Architecture Highlights

- **Modular Design**: Each component has a single responsibility
- **Loose Coupling**: Components interact through well-defined interfaces
- **Separation of Concerns**: Business logic separated from infrastructure
- **Template-Driven**: Uses Mustache templates for flexible code generation
- **Configuration-Based**: Driven by JSON configuration files