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
    def __init__(self, config_path: str, templates_dir: str, project_config: Dict[str, Any]):
        """
        Initialize the Hexagonal Architecture Generator.
        
        Args:
            config_path: Path to the configuration JSON file
            templates_dir: Directory containing Mustache templates
            project_config: Single project configuration from the array
        """
        self.config_path = config_path
        self.templates_dir = Path(templates_dir)
        self.project_config = project_config
        self.output_dir = Path(project_config['project']['name'])
        self.base_package = project_config['configOptions']['basePackage']
        self.target_packages = self._define_target_packages()
        self.mustache_context = self._build_mustache_context()
        self.openapi_spec = self._load_openapi_spec()
        
    @staticmethod
    def load_projects_config(config_path: str) -> List[Dict[str, Any]]:
        """
        Load projects configuration from JSON file.
        
        Returns:
            List of project configurations
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If configuration file is invalid JSON
        """
        with open(config_path, 'r') as f:
            return json.load(f)
    

    
    def _define_target_packages(self) -> Dict[str, str]:
        """
        Define Hexagonal Architecture package structure.
        
        Returns:
            Dictionary mapping package types to their full package names
        """
        return {
            "root": self.base_package,
            
            # Utils Layer
            "utils": f"{self.base_package}.utils",
            
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
            "infra_config_exceptions": f"{self.base_package}.infrastructure.config.exceptions",
            "infra_adapters_input_rest": f"{self.base_package}.infrastructure.adapters.input.rest",
            "infra_adapters_output_persistence": f"{self.base_package}.infrastructure.adapters.output.persistence",
            "infra_entity": f"{self.base_package}.infrastructure.adapters.output.persistence.entity",
            "infra_repository": f"{self.base_package}.infrastructure.adapters.output.persistence.repository",
            "infra_adapter": f"{self.base_package}.infrastructure.adapters.output.persistence.adapter",
        }
    
    def _load_openapi_spec(self) -> Dict[str, Any]:
        """
        Load OpenAPI specification from Smithy build output.
        
        Returns:
            Dictionary containing the OpenAPI specification
            
        Raises:
            FileNotFoundError: If no OpenAPI spec files are found
        """
        project_folder = self.project_config['project']['folder']
        openapi_files = glob.glob(f"build/smithy/{project_folder}/openapi/*.openapi.json")
        if not openapi_files:
            raise FileNotFoundError(f"No OpenAPI spec found for project {project_folder}. Run 'smithy build' first.")
        
        with open(openapi_files[0], 'r') as f:
            return json.load(f)
    
    def _build_mustache_context(self) -> Dict[str, Any]:
        """
        Build global Mustache context with all configuration options.
        
        Returns:
            Dictionary containing all template variables and configuration
        """
        context = self.project_config.copy()
        context.update(self.project_config['configOptions'])
        context.update(self.target_packages)
        
        # Add project parameters from project config
        if 'project' in self.project_config:
            context['author'] = self.project_config['project'].get('author', 'Generator')
            context['version'] = self.project_config['project'].get('version', '1.0.0')
            context['artifactVersion'] = self.project_config['project'].get('version', '1.0.0')
        
        # Set database type flags for conditional rendering - default to H2 if empty
        db_config = self.project_config.get('database', {})
        db_type = db_config.get('sgbd', 'h2').lower() if db_config else 'h2'
        context.update({
            'database': {
                **db_config,
                'postgresql': db_type == 'postgresql',
                'mysql': db_type == 'mysql', 
                'oracle': db_type == 'oracle',
                'sqlserver': db_type == 'sqlserver' or db_type == 'msserver',
                'h2': not db_type or db_type == 'h2'  # Default to H2 if empty
            },
            'smithyModel': 'user-service.smithy',
            'generatorVersion': '1.0.0'
        })
        
        return context
    
    def _get_package_path(self, package_name: str) -> Path:
        """
        Convert package name to file system path.
        
        Args:
            package_name: Java package name (e.g., 'com.example.service')
            
        Returns:
            Path object representing the directory structure
        """
        return Path("src/main/java") / package_name.replace(".", "/")
    
    def _ensure_directory(self, path: Path):
        """
        Create directory if it doesn't exist.
        
        Args:
            path: Path object representing the directory to create
        """
        path.mkdir(parents=True, exist_ok=True)
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render Mustache template with given context.
        
        Args:
            template_name: Name of the template file
            context: Dictionary containing template variables
            
        Returns:
            Rendered template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
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
        """
        Write content to file, creating directories as needed.
        
        Args:
            file_path: Path where the file will be written
            content: String content to write to the file
        """
        self._ensure_directory(file_path.parent)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Generated: {file_path}")
    
    def _convert_openapi_property(self, prop_name: str, prop_data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        Convert OpenAPI property to Java property.
        
        Args:
            prop_name: Name of the property
            prop_data: OpenAPI property definition
            required_fields: List of required field names
            
        Returns:
            Dictionary containing Java property information
        """
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
        """
        Generate EntityStatus enum for domain layer.
        
        Creates an enum class representing entity status values.
        """
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['domain_model'],
            'classname': 'EntityStatus'
        })
        
        content = self._render_template('EntityStatus.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['domain_model']) / "EntityStatus.java"
        self._write_file(file_path, content)
    
    def generate_domain_model(self, entity_name: str, schema_data: Dict[str, Any]):
        """
        Generate domain model (pure POJO) from OpenAPI schema.
        
        Args:
            entity_name: Name of the entity (e.g., 'User')
            schema_data: OpenAPI schema definition for the entity
        """
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
        """
        Generate application DTOs from OpenAPI schema.
        
        Args:
            schema_name: Name of the DTO class
            schema_data: OpenAPI schema definition
        """
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
        """
        Generate JPA entity (DBO) from OpenAPI schema.
        
        Args:
            entity_name: Name of the entity
            schema_data: Optional OpenAPI schema definition
        """
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
        """
        Generate domain repository port (interface).
        
        Args:
            entity_name: Name of the entity for which to create the port
        """
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
        """
        Generate Spring Data JPA repository.
        
        Args:
            entity_name: Name of the entity for the repository
        """
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
        """
        Generate repository adapter (implements domain port).
        
        Args:
            entity_name: Name of the entity for the adapter
        """
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
        """
        Generate use case port (domain input interface).
        
        Args:
            operation_name: Name of the operation (e.g., 'CreateUser')
        """
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
        """
        Generate application service (use case implementation).
        
        Args:
            operation_name: Name of the operation to implement
        """
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
            'isListOperation': operation_name.startswith('List') or 'List' in operation_name,
            'isApplicationService': True
        })
        
        content = self._render_template('apiService.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['application_service']) / f"{operation_name}Service.java"
        self._write_file(file_path, content)
    
    def generate_rest_controller(self, api_name: str):
        """
        Generate REST controller (input adapter).
        
        Args:
            api_name: Name of the API/entity for the controller
        """
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
        """
        Generate mapper for entity transformations.
        
        Args:
            entity_name: Name of the entity for mapping operations
        """
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['application_mapper'],
            'classname': f"{entity_name}Mapper",
            'entityName': entity_name,
            'entityVarName': entity_name.lower(),
            'dboName': f"{entity_name}Dbo",
            'isMapper': True
        })
        
        content = self._render_template('apiMapper.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['application_mapper']) / f"{entity_name}Mapper.java"
        self._write_file(file_path, content)
    
    def generate_main_application(self):
        """
        Generate Spring Boot main application class.
        
        Creates the main entry point class with @SpringBootApplication annotation.
        """
        context = self.mustache_context.copy()
        main_class_name = self.project_config['configOptions']['mainClass']  # UserServiceApplication
        context.update({
            'packageName': self.target_packages['root'],
            'classname': main_class_name  # UserServiceApplication (no extra Application)
        })
        
        content = self._render_template('Application.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['root']) / f"{main_class_name}.java"  # UserServiceApplication.java
        self._write_file(file_path, content)
    
    def generate_configuration(self):
        """
        Generate Spring configuration classes.
        
        Creates multiple configuration classes including security, OpenAPI,
        exception handling, and application configuration.
        """
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
            'packageName': self.target_packages['infra_config_exceptions'],
            'classname': 'GlobalExceptionHandler'
        })
        
        content = self._render_template('GlobalExceptionHandler.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_config_exceptions']) / "GlobalExceptionHandler.java"
        self._write_file(file_path, content)
        
        # Generate NotFoundException
        context.update({
            'packageName': self.target_packages['infra_config_exceptions'],
            'classname': 'NotFoundException'
        })
        
        content = self._render_template('NotFoundException.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_config_exceptions']) / "NotFoundException.java"
        self._write_file(file_path, content)
        
        # Generate LoggingUtils
        context.update({
            'packageName': self.target_packages['utils'],
            'classname': 'LoggingUtils'
        })
        
        content = self._render_template('LoggingUtils.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['utils']) / "LoggingUtils.java"
        self._write_file(file_path, content)
    
    def generate_pom_xml(self):
        """
        Generate Maven POM file.
        
        Creates the project's Maven configuration with dependencies and build settings.
        """
        content = self._render_template('pom.xml.mustache', self.mustache_context)
        file_path = self.output_dir / "pom.xml"
        self._write_file(file_path, content)
    
    def generate_application_properties(self):
        """
        Generate application.properties file.
        
        Creates Spring Boot configuration properties including database settings.
        """
        content = self._render_template('application.properties.mustache', self.mustache_context)
        file_path = self.output_dir / "src/main/resources/application.properties"
        self._write_file(file_path, content)
    
    def generate_readme(self):
        """
        Generate project README file.
        
        Creates documentation with project information and usage instructions.
        """
        content = self._render_template('README.md.mustache', self.mustache_context)
        file_path = self.output_dir / "README.md"
        self._write_file(file_path, content)
    
    def generate_docker_compose(self):
        """
        Generate docker-compose.yml file for database deployment.
        
        Creates Docker Compose configuration for running the database container.
        """
        content = self._render_template('docker-compose.yml.mustache', self.mustache_context)
        file_path = self.output_dir / "docker-compose.yml"
        self._write_file(file_path, content)
    
    def generate_dockerfile(self):
        """
        Generate Dockerfile for service containerization.
        
        Creates Docker configuration for building and running the application container.
        """
        content = self._render_template('Dockerfile.mustache', self.mustache_context)
        file_path = self.output_dir / "Dockerfile"
        self._write_file(file_path, content)
    
    def generate_maven_wrapper(self):
        """
        Generate Maven wrapper scripts and properties.
        
        Creates mvnw scripts and .mvn/wrapper/maven-wrapper.properties.
        """
        # Generate Unix/Linux/macOS wrapper
        content = self._render_template('mvnw.mustache', self.mustache_context)
        file_path = self.output_dir / "mvnw"
        self._write_file(file_path, content)
        # Make mvnw executable
        import os
        os.chmod(file_path, 0o755)
        
        # Generate Windows wrapper
        content = self._render_template('mvnw.cmd.mustache', self.mustache_context)
        file_path = self.output_dir / "mvnw.cmd"
        self._write_file(file_path, content)
        
        # Generate Maven wrapper properties
        wrapper_dir = self.output_dir / ".mvn" / "wrapper"
        self._ensure_directory(wrapper_dir)
        content = self._render_template('maven-wrapper.properties.mustache', self.mustache_context)
        file_path = wrapper_dir / "maven-wrapper.properties"
        self._write_file(file_path, content)
    
    def generate_complete_project(self):
        """
        Generate complete Hexagonal Architecture project from OpenAPI spec.
        
        Orchestrates the generation of all project components including domain models,
        application services, infrastructure adapters, and supporting files.
        """
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
        self.generate_docker_compose()
        self.generate_dockerfile()
        self.generate_maven_wrapper()
        
        print(f"\nHexagonal Architecture project generated successfully in: {self.output_dir}")
        project_info = self.project_config.get('project', {})
        print(f"Project: {project_info.get('name', 'generated-project')} v{project_info.get('version', '1.0.0')}")
        print(f"Description: {project_info.get('description', 'Generated project')}")
        print(f"Generated {len(schemas)} DTOs from OpenAPI schemas")
        print(f"Generated {len(operations)} use cases from operations")
        print("\nProject structure follows Hexagonal Architecture principles:")
        print("- Domain: Pure business logic and ports")
        print("- Application: Use case implementations and DTOs")
        print("- Infrastructure: External adapters (REST, JPA, Config)")


def run_command(cmd):
    """
    Execute a shell command and return its output.
    
    Args:
        cmd: Shell command to execute
        
    Returns:
        Command output as string
        
    Raises:
        SystemExit: If command fails
    """
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    return result.stdout

def main():
    """
    Main entry point for the generator.
    
    Handles command line arguments, loads configuration, and orchestrates
    the project generation process for multiple projects.
    """
    print("📝 Generating OpenAPI from Smithy...")
    run_command("smithy clean")
    run_command("smithy build")

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python hexagonal-architecture-generator.py [templates_dir]")
        print("Example: python hexagonal-architecture-generator.py templates/java")
        print("Config: scripts/config/params.json (array of project configurations)")
        sys.exit(0)
    
    config_path = "scripts/config/params.json"
    templates_dir = sys.argv[1] if len(sys.argv) > 1 else "templates/java"
    
    try:
        # Load all project configurations
        projects_config = HexagonalArchitectureGenerator.load_projects_config(config_path)
        
        print(f"Found {len(projects_config)} project(s) to generate...")
        
        # Generate each project
        for i, project_config in enumerate(projects_config, 1):
            project_name = project_config['project']['name']
            print(f"\n[{i}/{len(projects_config)}] Generating project: {project_name}")
            
            generator = HexagonalArchitectureGenerator(config_path, templates_dir, project_config)
            generator.generate_complete_project()
            
        print(f"\n✅ Successfully generated {len(projects_config)} project(s)!")
        
    except Exception as e:
        print(f"Error generating projects: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()