#!/usr/bin/env python3
"""
Hexagonal Architecture Spring Boot Code Generator

Generates a complete Java Spring Boot project following Hexagonal Architecture (Ports and Adapters) principles
from Mustache templates and configuration.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import pystache
import subprocess
import glob

class HexagonalArchitectureGenerator:
    def __init__(self, config_path: str, templates_dir: str, output_dir: str):
        self.config_path = config_path
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.config = self._load_config()
        self.base_package = self.config['configOptions']['basePackage']
        self.target_packages = self._define_target_packages()
        self.mustache_context = self._build_mustache_context()
        self.openapi_spec = self._load_openapi_spec()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load template configuration from JSON file."""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _define_target_packages(self) -> Dict[str, str]:
        """Define Hexagonal Architecture package structure."""
        return {
            "root": self.base_package,
            
            # Domain Layer
            "domain_model": f"{self.base_package}.domain.model",
            "domain_ports_input": f"{self.base_package}.domain.ports.input",
            "domain_ports_output": f"{self.base_package}.domain.ports.output",
            
            # Application Layer
            "application_service": f"{self.base_package}.application.service",
            "application_dto": f"{self.base_package}.application.dto",
            "application_mapper": f"{self.base_package}.application.mapper",
            
            # Infrastructure Layer
            "infra_config": f"{self.base_package}.infrastructure.config",
            "infra_adapters_input_rest": f"{self.base_package}.infrastructure.adapters.input.rest",
            "infra_adapters_output_persistence": f"{self.base_package}.infrastructure.adapters.output.persistence",
            "infra_entity": f"{self.base_package}.infrastructure.adapters.output.persistence.entity",
            "infra_repository": f"{self.base_package}.infrastructure.adapters.output.persistence.repository",
            "infra_adapter": f"{self.base_package}.infrastructure.adapters.output.persistence.adapter",
        }
    
    def _load_openapi_spec(self) -> Dict[str, Any]:
        """Load OpenAPI specification from Smithy build output."""
        openapi_files = glob.glob("build/smithy/*/openapi/*.openapi.json")
        if not openapi_files:
            raise FileNotFoundError("No OpenAPI spec found. Run 'smithy build' first.")
        
        with open(openapi_files[0], 'r') as f:
            return json.load(f)
    
    def _build_mustache_context(self) -> Dict[str, Any]:
        """Build global Mustache context with all configuration options."""
        context = self.config.copy()
        context.update(self.config['configOptions'])
        context.update(self.target_packages)
        return context
    
    def _get_package_path(self, package_name: str) -> Path:
        """Convert package name to file system path."""
        return Path("src/main/java") / package_name.replace(".", "/")
    
    def _ensure_directory(self, path: Path):
        """Create directory if it doesn't exist."""
        path.mkdir(parents=True, exist_ok=True)
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render Mustache template with given context."""
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Render with HTML escaping disabled to prevent &lt; &gt; encoding
        renderer = pystache.Renderer(escape=lambda u: u)
        rendered = renderer.render(template_content, context)
        
        # Fix HTML entities that might still appear
        rendered = rendered.replace('&quot;', '"')
        rendered = rendered.replace('&lt;', '<')
        rendered = rendered.replace('&gt;', '>')
        rendered = rendered.replace('&amp;', '&')
        
        return rendered
    
    def _write_file(self, file_path: Path, content: str):
        """Write content to file, creating directories as needed."""
        self._ensure_directory(file_path.parent)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Generated: {file_path}")
    
    def _convert_openapi_property(self, prop_name: str, prop_data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Convert OpenAPI property to Java property."""
        prop_type = prop_data.get('type', 'string')
        prop_format = prop_data.get('format')
        
        # Map OpenAPI types to Java types
        java_type = 'String'
        import_type = None
        
        if prop_type == 'string':
            if prop_format == 'date-time':
                java_type = 'OffsetDateTime'
                import_type = 'java.time.OffsetDateTime'
            else:
                java_type = 'String'
        elif prop_type == 'number':
            if prop_format == 'double':
                # For timestamp fields, use String consistently across all layers
                if prop_name in ['createdAt', 'updatedAt']:
                    java_type = 'String'
                else:
                    java_type = 'Double'
            else:
                java_type = 'BigDecimal'
                import_type = 'java.math.BigDecimal'
        elif prop_type == 'integer':
            java_type = 'Integer'
        elif prop_type == 'boolean':
            java_type = 'Boolean'
        elif prop_type == 'array':
            # Handle array types - check if it has items with $ref
            items = prop_data.get('items', {})
            if '$ref' in items:
                # Extract type from $ref (e.g., "#/components/schemas/UserResponse" -> "UserResponse")
                ref_type = items['$ref'].split('/')[-1]
                java_type = f'List<{ref_type}>'
            else:
                java_type = 'List<String>'
            import_type = 'java.util.List'
        
        # Build validation annotations
        validation_annotations = []
        if prop_name in required_fields:
            validation_annotations.append('@NotNull')
        
        if 'minLength' in prop_data:
            validation_annotations.append(f'@Size(min = {prop_data["minLength"]})')
        if 'maxLength' in prop_data:
            if 'minLength' in prop_data:
                validation_annotations[-1] = f'@Size(min = {prop_data["minLength"]}, max = {prop_data["maxLength"]})'  
            else:
                validation_annotations.append(f'@Size(max = {prop_data["maxLength"]})')
        
        if 'pattern' in prop_data:
            # Escape backslashes in regex patterns for Java
            pattern = prop_data['pattern'].replace('\\', '\\\\')
            validation_annotations.append(f'@Pattern(regexp = "{pattern}")')
        
        return {
            'name': prop_name,
            'dataType': java_type,
            'datatypeWithEnum': java_type,
            'baseName': prop_name,
            'getter': f'get{prop_name.capitalize()}',
            'setter': f'set{prop_name.capitalize()}',
            'jsonProperty': prop_name,
            'required': prop_name in required_fields,
            'hasValidation': len(validation_annotations) > 0,
            'validationAnnotations': validation_annotations,
            'import': import_type
        }
    
    def generate_entity_status_enum(self):
        """Generate EntityStatus enum for domain layer."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['domain_model'],
            'classname': 'EntityStatus'
        })
        
        content = self._render_template('EntityStatus.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['domain_model']) / "EntityStatus.java"
        self._write_file(file_path, content)
    
    def generate_domain_model(self, entity_name: str, schema_data: Dict[str, Any]):
        """Generate domain model (pure POJO) from OpenAPI schema."""
        context = self.mustache_context.copy()
        
        # Extract properties and build vars (without validation annotations for domain)
        properties = schema_data.get('properties', {})
        required_fields = schema_data.get('required', [])
        
        vars_list = []
        imports = set()
        
        for prop_name, prop_data in properties.items():
            var_info = self._convert_openapi_property(prop_name, prop_data, required_fields)
            # Remove validation annotations for domain model
            var_info['hasValidation'] = False
            var_info['validationAnnotations'] = []
            vars_list.append(var_info)
            if var_info.get('import'):
                imports.add(var_info['import'])
        
        context.update({
            'packageName': self.target_packages['domain_model'],
            'classname': entity_name,
            'vars': vars_list,
            'imports': [{'import': imp} for imp in sorted(imports)],
            'models': [{'model': {'classname': entity_name, 'vars': vars_list}}],
            'isDomainModel': True,
            'useJPA': False,
            'useLombok': True
        })
        
        content = self._render_template('pojo.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['domain_model']) / f"{entity_name}.java"
        self._write_file(file_path, content)
    
    def generate_dto(self, schema_name: str, schema_data: Dict[str, Any]):
        """Generate application DTOs from OpenAPI schema."""
        context = self.mustache_context.copy()
        
        # Extract properties and build vars
        properties = schema_data.get('properties', {})
        required_fields = schema_data.get('required', [])
        
        vars_list = []
        imports = set()
        
        for prop_name, prop_data in properties.items():
            var_info = self._convert_openapi_property(prop_name, prop_data, required_fields)
            vars_list.append(var_info)
            if var_info.get('import'):
                imports.add(var_info['import'])
        
        context.update({
            'packageName': self.target_packages['application_dto'],
            'classname': schema_name,
            'vars': vars_list,
            'imports': [{'import': imp} for imp in sorted(imports)],
            'models': [{'model': {'classname': schema_name, 'vars': vars_list}}],
            'useBeanValidation': True,
            'useJackson': True
        })
        
        content = self._render_template('pojo.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['application_dto']) / f"{schema_name}.java"
        self._write_file(file_path, content)
    
    def generate_entity(self, entity_name: str, schema_data: Dict[str, Any] = None):
        """Generate JPA entity (DBO) from OpenAPI schema."""
        context = self.mustache_context.copy()
        
        if schema_data:
            # Extract properties and build vars with JPA annotations
            properties = schema_data.get('properties', {})
            required_fields = schema_data.get('required', [])
            
            vars_list = []
            imports = set()
            
            for prop_name, prop_data in properties.items():
                if prop_name not in ['createdAt', 'updatedAt', 'status'] and not prop_name.endswith('Id'):  # Skip timestamp, status and ID fields
                    var_info = self._convert_openapi_property(prop_name, prop_data, required_fields)
                    var_info['isIdField'] = prop_name.endswith('Id')
                    var_info['isTimestampField'] = prop_name in ['createdAt', 'updatedAt']
                    var_info['isStatusField'] = prop_name == 'status'
                    vars_list.append(var_info)
                    if var_info.get('import'):
                        imports.add(var_info['import'])
            
            context.update({
                'vars': vars_list,
                'imports': [{'import': imp} for imp in sorted(imports)],
            })
        
        context.update({
            'packageName': self.target_packages['infra_entity'],
            'classname': f"{entity_name}Dbo",
            'entityName': entity_name,
            'entityVarName': entity_name.lower(),
            'tableName': entity_name.lower() + 's',
            'isEntity': True,
            'useJPA': True,
            'useLombok': True
        })
        
        content = self._render_template('apiEntity.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_entity']) / f"{entity_name}Dbo.java"
        self._write_file(file_path, content)
    
    def generate_domain_port_output(self, entity_name: str):
        """Generate domain repository port (interface)."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['domain_ports_output'],
            'classname': f"{entity_name}RepositoryPort",
            'entityName': entity_name,
            'entityVarName': entity_name.lower(),
            'interfaceOnly': True,
            'isDomainPort': True
        })
        
        content = self._render_template('interface.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['domain_ports_output']) / f"{entity_name}RepositoryPort.java"
        self._write_file(file_path, content)
    
    def generate_jpa_repository(self, entity_name: str):
        """Generate Spring Data JPA repository."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['infra_repository'],
            'classname': f"Jpa{entity_name}Repository",
            'entityName': entity_name,
            'isJpaRepository': True,
            'isAdapter': False
        })
        
        content = self._render_template('apiRepository.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_repository']) / f"Jpa{entity_name}Repository.java"
        self._write_file(file_path, content)
    
    def generate_repository_adapter(self, entity_name: str):
        """Generate repository adapter (implements domain port)."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['infra_adapter'],
            'classname': f"{entity_name}RepositoryAdapter",
            'entityName': entity_name,
            'entityVarName': entity_name.lower(),
            'dboName': f"{entity_name}Dbo",
            'portName': f"{entity_name}RepositoryPort",
            'jpaRepositoryName': f"Jpa{entity_name}Repository",
            'isJpaRepository': False,
            'isAdapter': True
        })
        
        content = self._render_template('apiRepository.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_adapter']) / f"{entity_name}RepositoryAdapter.java"
        self._write_file(file_path, content)
    
    def generate_use_case_port(self, operation_name: str):
        """Generate use case port (domain input interface)."""
        context = self.mustache_context.copy()
        
        # Determine request/response types based on operation
        request_type = f"{operation_name}RequestContent" if operation_name.startswith(('Create', 'Update')) else "String"
        response_type = f"{operation_name}ResponseContent"
        
        context.update({
            'packageName': self.target_packages['domain_ports_input'],
            'classname': f"{operation_name}UseCase",
            'operationName': operation_name,
            'requestType': request_type,
            'returnType': response_type,
            'interfaceOnly': True,
            'isUseCasePort': True,
            'isUpdateOperation': operation_name.startswith('Update')
        })
        
        content = self._render_template('interface.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['domain_ports_input']) / f"{operation_name}UseCase.java"
        self._write_file(file_path, content)
    
    def generate_application_service(self, operation_name: str):
        """Generate application service (use case implementation)."""
        context = self.mustache_context.copy()
        
        # Determine operation type and entity
        entity_name = "User"  # Could be extracted from operation_name
        entity_var_name = entity_name.lower()
        
        # Determine request/response types based on operation
        request_type = f"{operation_name}RequestContent" if operation_name.startswith(('Create', 'Update')) else "String"
        response_type = f"{operation_name}ResponseContent"
        
        context.update({
            'packageName': self.target_packages['application_service'],
            'classname': f"{operation_name}Service",
            'operationName': operation_name,
            'entityName': entity_name,
            'entityVarName': entity_var_name,
            'requestType': request_type,
            'returnType': response_type,
            'isCreate': operation_name.startswith('Create'),
            'isGet': operation_name.startswith('Get'),
            'isUpdate': operation_name.startswith('Update'),
            'isDelete': operation_name.startswith('Delete'),
            'isApplicationService': True
        })
        
        content = self._render_template('apiService.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['application_service']) / f"{operation_name}Service.java"
        self._write_file(file_path, content)
    
    def generate_rest_controller(self, api_name: str):
        """Generate REST controller (input adapter)."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['infra_adapters_input_rest'],
            'classname': f"{api_name}Controller",
            'entityName': api_name,
            'entityVarName': api_name.lower(),
            'entityPath': api_name.lower() + 's',
            'entityIdPath': f'{{{api_name.lower()}Id}}',
            'isController': True,
            'useSpringWeb': True
        })
        
        content = self._render_template('apiController.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_adapters_input_rest']) / f"{api_name}Controller.java"
        self._write_file(file_path, content)
    
    def generate_mapper(self, entity_name: str):
        """Generate mapper for entity transformations."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['application_mapper'],
            'classname': f"{entity_name}Mapper",
            'entityName': entity_name,
            'dboName': f"{entity_name}Dbo",
            'isMapper': True
        })
        
        content = self._render_template('apiMapper.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['application_mapper']) / f"{entity_name}Mapper.java"
        self._write_file(file_path, content)
    
    def generate_main_application(self):
        """Generate Spring Boot main application class."""
        context = self.mustache_context.copy()
        main_class_name = self.config['configOptions']['mainClass']  # UserServiceApplication
        context.update({
            'packageName': self.target_packages['root'],
            'classname': main_class_name  # UserServiceApplication (no extra Application)
        })
        
        content = self._render_template('Application.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['root']) / f"{main_class_name}.java"  # UserServiceApplication.java
        self._write_file(file_path, content)
    
    def generate_configuration(self):
        """Generate Spring configuration classes."""
        # Generate main application configuration
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['infra_config'],
            'classname': 'ApplicationConfiguration'
        })
        
        content = self._render_template('Configuration.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_config']) / "ApplicationConfiguration.java"
        self._write_file(file_path, content)
        
        # Generate security configuration
        context.update({
            'classname': 'SecurityConfiguration',
            'entityPath': 'users'  # Default entity path
        })
        
        content = self._render_template('SecurityConfiguration.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_config']) / "SecurityConfiguration.java"
        self._write_file(file_path, content)
        
        # Generate OpenAPI configuration
        context.update({
            'classname': 'OpenApiConfiguration',
            'entityName': 'User'  # Default entity name
        })
        
        content = self._render_template('OpenApiConfiguration.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_config']) / "OpenApiConfiguration.java"
        self._write_file(file_path, content)
        
        # Generate global exception handler
        context.update({
            'classname': 'GlobalExceptionHandler'
        })
        
        content = self._render_template('GlobalExceptionHandler.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_config']) / "GlobalExceptionHandler.java"
        self._write_file(file_path, content)
        
        # Generate NotFoundException
        context.update({
            'classname': 'NotFoundException'
        })
        
        content = self._render_template('NotFoundException.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_config']) / "NotFoundException.java"
        self._write_file(file_path, content)
    
    def generate_pom_xml(self):
        """Generate Maven POM file."""
        content = self._render_template('pom.xml.mustache', self.mustache_context)
        file_path = self.output_dir / "pom.xml"
        self._write_file(file_path, content)
    
    def generate_application_properties(self):
        """Generate application.properties file."""
        content = self._render_template('application.properties.mustache', self.mustache_context)
        file_path = self.output_dir / "src/main/resources/application.properties"
        self._write_file(file_path, content)
    
    def generate_readme(self):
        """Generate project README file."""
        content = self._render_template('README.md.mustache', self.mustache_context)
        file_path = self.output_dir / "README.md"
        self._write_file(file_path, content)
    
    def generate_complete_project(self):
        """Generate complete Hexagonal Architecture project from OpenAPI spec."""
        print("Generating Hexagonal Architecture Spring Boot project from OpenAPI spec...")
        
        # Extract data from OpenAPI spec
        schemas = self.openapi_spec.get('components', {}).get('schemas', {})
        paths = self.openapi_spec.get('paths', {})
        
        # Extract operations
        operations = []
        for path, methods in paths.items():
            for method, operation_data in methods.items():
                if 'operationId' in operation_data:
                    operations.append(operation_data['operationId'])
        
        # Generate DTOs from schemas
        for schema_name, schema_data in schemas.items():
            if schema_data.get('type') == 'object':
                self.generate_dto(schema_name, schema_data)
        
        # Generate EntityStatus enum
        self.generate_entity_status_enum()
        
        # Generate domain models (extract core entities)
        core_entities = ['User']  # Could be extracted from schema analysis
        for entity in core_entities:
            # Find the main response schema for this entity
            entity_schema = schemas.get(f'{entity}Response', schemas.get(f'Get{entity}ResponseContent', {}))
            if entity_schema:
                self.generate_domain_model(entity, entity_schema)
                self.generate_domain_port_output(entity)
        
        # Generate application layer
        for entity in core_entities:
            self.generate_mapper(entity)
        
        for operation in operations:
            self.generate_use_case_port(operation)
            self.generate_application_service(operation)
        
        # Generate infrastructure layer
        for entity in core_entities:
            entity_schema = schemas.get(f'{entity}Response', schemas.get(f'Get{entity}ResponseContent', {}))
            if entity_schema:
                self.generate_entity(entity, entity_schema)
                self.generate_jpa_repository(entity)
                self.generate_repository_adapter(entity)
        
        # Generate REST controllers (one per main entity)
        for entity in core_entities:
            self.generate_rest_controller(entity)
        
        # Generate supporting files
        self.generate_main_application()
        self.generate_configuration()
        self.generate_pom_xml()
        self.generate_application_properties()
        self.generate_readme()
        
        print(f"\nHexagonal Architecture project generated successfully in: {self.output_dir}")
        print(f"Generated {len(schemas)} DTOs from OpenAPI schemas")
        print(f"Generated {len(operations)} use cases from operations")
        print("\nProject structure follows Hexagonal Architecture principles:")
        print("- Domain: Pure business logic and ports")
        print("- Application: Use case implementations and DTOs")
        print("- Infrastructure: External adapters (REST, JPA, Config)")


def run_command(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    return result.stdout

def main():

    print("📝 Generating OpenAPI from Smithy...")
    run_command("smithy clean")
    run_command("smithy build")

    if len(sys.argv) != 4:
        print("Usage: python hexagonal-architecture-generator.py <config_path> <templates_dir> <output_dir>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    templates_dir = sys.argv[2]
    output_dir = sys.argv[3]
    
    try:
        generator = HexagonalArchitectureGenerator(config_path, templates_dir, output_dir)
        generator.generate_complete_project()
    except Exception as e:
        print(f"Error generating project: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()