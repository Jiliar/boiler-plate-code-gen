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
        self.output_dir = Path("projects") / project_config['project']['general']['name']
        self.base_package = project_config['project']['params']['configOptions']['basePackage']
        self.openapi_specs = self._load_openapi_specs()
        self.target_packages = self._define_target_packages()
        self.mustache_context = self._build_mustache_context()
        
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
    
    def _load_openapi_specs(self) -> List[Dict[str, Any]]:
        """
        Load all OpenAPI specifications from Smithy build output.

        Returns:
            List of dictionaries containing OpenAPI specifications with metadata
            
        Raises:
            FileNotFoundError: If no OpenAPI spec files are found
        """
        project_folder = self.project_config['project']['general']['folder']
        openapi_files = glob.glob(f"build/smithy/{project_folder}/openapi/*.openapi.json")
        
        # Also check for additional projections (e.g., back-ms-users-location)
        additional_projections = glob.glob(f"build/smithy/{project_folder}-*/openapi/*.openapi.json")
        openapi_files.extend(additional_projections)
        
        if not openapi_files:
            raise FileNotFoundError(f"No OpenAPI spec found for project {project_folder}. Run 'smithy build' first.")
        
        specs = []
        for file_path in openapi_files:
            with open(file_path, 'r') as f:
                spec_data = json.load(f)
                service_name = self._extract_service_name_from_path(file_path)
                specs.append({
                    'spec': spec_data,
                    'file_path': file_path,
                    'service_name': service_name
                })
        
        return specs
    
    def _extract_service_name_from_path(self, file_path: str) -> str:
        """
        Extract service name from OpenAPI file path.
        
        Args:
            file_path: Path to the OpenAPI file
            
        Returns:
            Service name in lowercase (e.g., 'user' from 'UserService.openapi.json')
        """
        file_name = Path(file_path).stem  # Gets 'UserService.openapi' from path
        service_name = file_name.replace('.openapi', '')  # Gets 'UserService'
        
        # Remove 'Service' suffix if present and convert to lowercase
        if service_name.endswith('Service'):
            service_name = service_name[:-7]  # Remove 'Service'
        
        return service_name.lower()
    
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
    

    def _build_mustache_context(self) -> Dict[str, Any]:
        """
        Build global Mustache context with all configuration options.

        Returns:
            Dictionary containing all template variables and configuration
        """
        context = self.project_config.copy()
        context.update(self.project_config['project']['params']['configOptions'])
        context.update(self.target_packages)
        
        # Add project parameters from project config
        if 'project' in self.project_config:
            context['author'] = self.project_config['project']['general'].get('author', 'Generator')
            context['version'] = self.project_config['project']['general'].get('version', '1.0.0')
            context['artifactVersion'] = self.project_config['project']['params'].get('artifactVersion', '1.0.0')
            context['project'] = self.project_config['project']['general']
            context.update(self.project_config['project']['params'])
        
        # Add infrastructure configuration
        if 'infra' in self.project_config:
            context['infra'] = self.project_config['infra']
        
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
            # Use correct email pattern for validation
            pattern = prop_data['pattern']
            if 'email' in prop_name.lower() or pattern == '^[^@]+@[^@]+\.[^@]+$':
                pattern = '^[^@]+@[^@]+\\\\.[^@]+$'
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
    
    def generate_dto(self, schema_name: str, schema_data: Dict[str, Any], service_name: str):
        """
        Generate application DTOs from OpenAPI schema.

        Args:
            schema_name: Name of the DTO class
            schema_data: OpenAPI schema definition
            service_name: Service name for DTO organization
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
        
        # Create service-specific DTO package
        dto_package = f"{self.target_packages['application_dto']}.{service_name}"
        
        context.update({
            'packageName': dto_package,
            'classname': schema_name,
            'vars': vars_list,
            'imports': [{'import': imp} for imp in sorted(imports)],
            'models': [{'model': {'classname': schema_name, 'vars': vars_list}}],
            'useBeanValidation': True,
            'useJackson': True
        })
        
        content = self._render_template('pojo.mustache', context)
        file_path = self.output_dir / self._get_package_path(dto_package) / f"{schema_name}.java"
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
    
    def generate_jpa_repository(self, entity_name: str, entity_schema: Dict[str, Any] = None):
        """
        Generate Spring Data JPA repository with pagination and smart search.

        Args:
            entity_name: Name of the entity for the repository
            entity_schema: OpenAPI schema for determining search fields
        """
        # Determine search fields based on schema
        search_fields = []
        if entity_schema:
            properties = entity_schema.get('properties', {})
            # Priority order for search fields
            field_priorities = ['name', 'title', 'description']
            for field in field_priorities:
                if field in properties:
                    search_fields.append(field)
        
        # Build search query conditions
        search_conditions = []
        if search_fields:
            for field in search_fields:
                search_conditions.append(f"LOWER(e.{field}) LIKE LOWER(CONCAT('%', :search, '%'))")
        else:
            # Fallback to ID search if no text fields found
            search_conditions.append("LOWER(CAST(e.id AS string)) LIKE LOWER(CONCAT('%', :search, '%'))")
        
        search_query = " OR ".join(search_conditions)
        
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['infra_repository'],
            'classname': f"Jpa{entity_name}Repository",
            'entityName': entity_name,
            'searchFields': search_fields,
            'searchQuery': search_query,
            'hasSearchFields': len(search_fields) > 0,
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
    
    def generate_use_case_port(self, operation_name: str, service_name: str = None):
        """
        Generate use case port (domain input interface).

        Args:
            operation_name: Name of the operation (e.g., 'CreateUser')
            service_name: Service name for DTO organization
        """
        context = self.mustache_context.copy()
        
        # Determine request/response types based on operation
        request_type = f"{operation_name}RequestContent" if operation_name.startswith(('Create', 'Update')) else "String"
        response_type = f"{operation_name}ResponseContent"
        
        # Extract service name from operation if not provided
        if not service_name:
            # Default service name extraction logic
            for entity in ['User', 'Movie', 'Location']:
                if entity in operation_name:
                    service_name = entity.lower()
                    break
            if not service_name:
                service_name = 'default'
        
        # Check if types are Java native types
        java_types = {'String', 'Integer', 'Long', 'Boolean', 'Double', 'Float', 'Object', 'Void'}
        request_is_java_type = request_type in java_types
        response_is_java_type = response_type in java_types
        
        context.update({
            'packageName': self.target_packages['domain_ports_input'],
            'classname': f"{operation_name}UseCase",
            'operationName': operation_name,
            'requestType': request_type,
            'returnType': response_type,
            'serviceName': service_name,
            'requestIsJavaType': request_is_java_type,
            'responseIsJavaType': response_is_java_type,
            'interfaceOnly': True,
            'isUseCasePort': True,
            'isUpdateOperation': operation_name.startswith('Update')
        })
        
        content = self._render_template('interface.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['domain_ports_input']) / f"{operation_name}UseCase.java"
        self._write_file(file_path, content)
    
    def generate_consolidated_service(self, entity_name: str, operations: List[Dict[str, Any]], complex_operations: List[str] = None, service_name: str = None):
        """
        Generate consolidated application service with CRUD and complex operations for an entity.

        Args:
            entity_name: Name of the entity
            operations: List of operation dictionaries for this entity
            complex_operations: List of complex operation IDs for this entity
            service_name: Service name for DTO organization
        """
        context = self.mustache_context.copy()
        entity_var_name = entity_name.lower()
        
        # Extract service name from operations if not provided
        if not service_name:
            service_name = operations[0]['service'] if operations else entity_var_name
        
        # Analyze available operations
        has_create = any(op['id'].startswith('Create') and entity_name in op['id'] for op in operations)
        has_get = any(op['id'].startswith('Get') and entity_name in op['id'] for op in operations)
        has_update = any(op['id'].startswith('Update') and entity_name in op['id'] for op in operations)
        has_delete = any(op['id'].startswith('Delete') and entity_name in op['id'] for op in operations)
        has_list = any(op['id'] == f'List{entity_name}s' for op in operations)
        
        # Build complex operations info
        complex_ops_info = []
        if complex_operations:
            for op in complex_operations:
                method_name = op[0].lower() + op[1:] if op else ''
                complex_ops_info.append({
                    'operationId': op,
                    'methodName': method_name,
                    'responseType': f'{op}ResponseContent'
                })
        
        context.update({
            'packageName': self.target_packages['application_service'],
            'classname': f"{entity_name}Service",
            'entityName': entity_name,
            'entityVarName': entity_var_name,
            'serviceName': service_name,
            'hasCreate': has_create,
            'hasGet': has_get,
            'hasUpdate': has_update,
            'hasDelete': has_delete,
            'hasList': has_list,
            'hasComplexOperations': len(complex_ops_info) > 0,
            'complexOperations': complex_ops_info,
            'isApplicationService': True
        })
        
        # Add type information for each operation
        if has_create:
            context.update({
                'createRequestType': f'Create{entity_name}RequestContent',
                'createReturnType': f'Create{entity_name}ResponseContent',
                'createRequestIsJavaType': False,
                'createResponseIsJavaType': False
            })
        
        if has_get:
            context.update({
                'getReturnType': f'Get{entity_name}ResponseContent',
                'getResponseIsJavaType': False
            })
        
        if has_update:
            context.update({
                'updateRequestType': f'Update{entity_name}RequestContent',
                'updateReturnType': f'Update{entity_name}ResponseContent',
                'updateRequestIsJavaType': False,
                'updateResponseIsJavaType': False
            })
        
        if has_delete:
            context.update({
                'deleteReturnType': f'Delete{entity_name}ResponseContent',
                'deleteResponseIsJavaType': False
            })
        
        if has_list:
            context.update({
                'listRequestType': f'List{entity_name}sRequestContent',
                'listReturnType': f'List{entity_name}sResponseContent',
                'listRequestIsJavaType': False,
                'listResponseIsJavaType': False
            })
        
        content = self._render_template('consolidatedService.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['application_service']) / f"{entity_name}Service.java"
        self._write_file(file_path, content)
    
    def generate_consolidated_use_cases(self, entity_name: str, operations: List[Dict[str, Any]], complex_operations: List[str] = None, service_name: str = None):
        """
        Generate consolidated use case interfaces for an entity.

        Args:
            entity_name: Name of the entity
            operations: List of operation dictionaries for this entity
            complex_operations: List of complex operation IDs for this entity
            service_name: Service name for DTO organization
        """
        # Extract service name from operations if not provided
        if not service_name:
            service_name = operations[0]['service'] if operations else entity_name.lower()
        
        # Analyze available operations
        has_create = any(op['id'].startswith('Create') and entity_name in op['id'] for op in operations)
        has_get = any(op['id'].startswith('Get') and entity_name in op['id'] for op in operations)
        has_update = any(op['id'].startswith('Update') and entity_name in op['id'] for op in operations)
        has_delete = any(op['id'].startswith('Delete') and entity_name in op['id'] for op in operations)
        has_list = any(op['id'] == f'List{entity_name}s' for op in operations)
        
        # Generate consolidated use case interface
        self._generate_consolidated_use_case_interface(entity_name, operations, complex_operations, service_name)
    
    def _generate_consolidated_use_case_interface(self, entity_name: str, operations: List[Dict[str, Any]], complex_operations: List[str] = None, service_name: str = None):
        """
        Generate consolidated use case interface for an entity.

        Args:
            entity_name: Name of the entity
            operations: List of operation dictionaries for this entity
            complex_operations: List of complex operation IDs for this entity
            service_name: Service name for DTO organization
        """
        # Extract service name from operations if not provided
        if not service_name:
            service_name = operations[0]['service'] if operations else entity_name.lower()
        
        # Check which DTOs actually exist
        dto_base_path = self.output_dir / self._get_package_path(self.target_packages['application_dto']) / service_name
        
        # Check for each operation's DTOs
        has_create = self._check_dto_exists(dto_base_path, f'Create{entity_name}RequestContent') and self._check_dto_exists(dto_base_path, f'Create{entity_name}ResponseContent')
        has_get = self._check_dto_exists(dto_base_path, f'Get{entity_name}ResponseContent')
        has_update = self._check_dto_exists(dto_base_path, f'Update{entity_name}RequestContent') and self._check_dto_exists(dto_base_path, f'Update{entity_name}ResponseContent')
        has_delete = self._check_dto_exists(dto_base_path, f'Delete{entity_name}ResponseContent')
        # For List operations, only ResponseContent is required (GET operations with query parameters don't need RequestContent)
        has_list = self._check_dto_exists(dto_base_path, f'List{entity_name}sResponseContent')
        
        # Build complex operations info
        complex_ops_info = []
        if complex_operations:
            for op in complex_operations:
                if self._check_dto_exists(dto_base_path, f'{op}ResponseContent'):
                    method_name = op[0].lower() + op[1:] if op else ''
                    complex_ops_info.append({
                        'operationId': op,
                        'methodName': method_name,
                        'responseType': f'{op}ResponseContent'
                    })
        
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['domain_ports_input'],
            'classname': f'{entity_name}UseCase',
            'entityName': entity_name,
            'entityVarName': entity_name.lower(),
            'serviceName': service_name,
            'hasCreate': has_create,
            'hasGet': has_get,
            'hasUpdate': has_update,
            'hasDelete': has_delete,
            'hasList': has_list,
            'hasComplexOperations': len(complex_ops_info) > 0,
            'complexOperations': complex_ops_info
        })
        
        content = self._render_template('consolidatedUseCase.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['domain_ports_input']) / f'{entity_name}UseCase.java'
        self._write_file(file_path, content)
    
    def _check_dto_exists(self, dto_base_path: Path, dto_name: str) -> bool:
        """
        Check if a DTO file exists.

        Args:
            dto_base_path: Base path to the DTO directory
            dto_name: Name of the DTO class
            
        Returns:
            True if the DTO file exists, False otherwise
        """
        dto_file_path = dto_base_path / f'{dto_name}.java'
        return dto_file_path.exists()
    
    def generate_rest_controller(self, api_name: str, available_operations: List[str], service_name: str = None):
        """
        Generate REST controller (input adapter) with CRUD and complex operations.

        Args:
            api_name: Name of the API/entity for the controller
            available_operations: List of operation IDs available for this entity
            service_name: Service name for DTO imports
        """
        # Find service name from operations if not provided
        if not service_name:
            for op in available_operations:
                for spec_info in self.openapi_specs:
                    if any(op in paths_data.get('operationId', '') for paths_data in 
                          [method_data for path_data in spec_info['spec'].get('paths', {}).values() 
                           for method_data in path_data.values() if isinstance(method_data, dict)]):
                        service_name = spec_info['service_name']
                        break
                if service_name:
                    break
        
        if not service_name:
            service_name = api_name.lower()
        
        # Separate CRUD and complex operations
        crud_operations = [op for op in available_operations if any(op.startswith(prefix + api_name) for prefix in ['Create', 'Get', 'Update', 'Delete']) or op == f'List{api_name}s']
        complex_operations = [op for op in available_operations if op not in crud_operations]
        
        # Generate specific DTO imports for CRUD operations
        dto_imports = []
        if f'Create{api_name}' in available_operations:
            dto_imports.extend([
                f'{self.target_packages["application_dto"]}.{service_name}.Create{api_name}RequestContent',
                f'{self.target_packages["application_dto"]}.{service_name}.Create{api_name}ResponseContent'
            ])
        if f'Get{api_name}' in available_operations:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.Get{api_name}ResponseContent')
        if f'Update{api_name}' in available_operations:
            dto_imports.extend([
                f'{self.target_packages["application_dto"]}.{service_name}.Update{api_name}RequestContent',
                f'{self.target_packages["application_dto"]}.{service_name}.Update{api_name}ResponseContent'
            ])
        if f'Delete{api_name}' in available_operations:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.Delete{api_name}ResponseContent')
        if f'List{api_name}s' in available_operations:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.List{api_name}sResponseContent')
        
        # Add DTO imports for complex operations
        for op in complex_operations:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.{op}ResponseContent')
        
        # Generate consolidated UseCase import
        usecase_imports = [f'{self.target_packages["domain_ports_input"]}.{api_name}UseCase']
        
        # Build complex operations info for template
        complex_ops_info = []
        for op in complex_operations:
            # Extract method info from operation name (e.g., GetCitiesByRegion -> getCitiesByRegion)
            method_name = op[0].lower() + op[1:] if op else ''
            path_segment = op.lower().replace('get', '').replace('by', '-by-') if op.startswith('Get') else op.lower()
            complex_ops_info.append({
                'operationId': op,
                'methodName': method_name,
                'pathSegment': path_segment,
                'responseType': f'{op}ResponseContent'
            })
        
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['infra_adapters_input_rest'],
            'classname': f"{api_name}Controller",
            'entityName': api_name,
            'entityVarName': api_name.lower(),
            'entityPath': api_name.lower() + 's',
            'entityIdPath': f'{{{api_name.lower()}Id}}',
            'hasCreate': f'Create{api_name}' in available_operations,
            'hasGet': f'Get{api_name}' in available_operations,
            'hasUpdate': f'Update{api_name}' in available_operations,
            'hasDelete': f'Delete{api_name}' in available_operations,
            'hasList': f'List{api_name}s' in available_operations,
            'hasComplexOperations': len(complex_operations) > 0,
            'complexOperations': complex_ops_info,
            'serviceName': service_name,
            'dtoImports': dto_imports,
            'useCaseImports': usecase_imports,
            'isController': True,
            'useSpringWeb': True
        })
        
        content = self._render_template('apiController.mustache', context)
        file_path = self.output_dir / self._get_package_path(self.target_packages['infra_adapters_input_rest']) / f"{api_name}Controller.java"
        self._write_file(file_path, content)
    
    def generate_mapper(self, entity_name: str, service_name: str = None):
        """
        Generate mapper for entity transformations.

        Args:
            entity_name: Name of the entity for mapping operations
            service_name: Service name for DTO imports
        """
        # Check if DTOs exist for this entity
        dto_base_path = self.output_dir / self._get_package_path(self.target_packages['application_dto'])
        
        # Find service name if not provided
        if not service_name:
            for spec_info in self.openapi_specs:
                service_name = spec_info['service_name']
                break
        
        if not service_name:
            service_name = entity_name.lower()
        
        # Check for specific DTOs
        create_dto_name = f"Create{entity_name}RequestContent"
        update_dto_name = f"Update{entity_name}RequestContent"
        response_dto_name = f"{entity_name}Response"
        list_response_dto_name = f"List{entity_name}sResponseContent"
        
        # Check if DTOs exist in any service folder
        has_create_dto = False
        has_update_dto = False
        has_response_dto = False
        has_list_response_dto = False
        has_get_dto = False
        
        for service_folder in dto_base_path.iterdir():
            if service_folder.is_dir():
                if (service_folder / f"{create_dto_name}.java").exists():
                    has_create_dto = True
                    service_name = service_folder.name
                if (service_folder / f"{update_dto_name}.java").exists():
                    has_update_dto = True
                    service_name = service_folder.name
                if (service_folder / f"{response_dto_name}.java").exists():
                    has_response_dto = True
                    service_name = service_folder.name
                if (service_folder / f"{list_response_dto_name}.java").exists():
                    has_list_response_dto = True
                    service_name = service_folder.name
                if (service_folder / f"Get{entity_name}ResponseContent.java").exists():
                    has_get_dto = True
                    service_name = service_folder.name
        
        # Build imports for DTOs
        dto_imports = []
        if has_create_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.{create_dto_name}')
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.Create{entity_name}ResponseContent')
        if has_update_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.{update_dto_name}')
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.Update{entity_name}ResponseContent')
        if has_response_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.{response_dto_name}')
        if has_list_response_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.{list_response_dto_name}')
        if has_get_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service_name}.Get{entity_name}ResponseContent')
        
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['application_mapper'],
            'classname': f"{entity_name}Mapper",
            'entityName': entity_name,
            'entityVarName': entity_name.lower(),
            'dboName': f"{entity_name}Dbo",
            'serviceName': service_name,
            'hasCreateDto': has_create_dto,
            'hasUpdateDto': has_update_dto,
            'hasResponseDto': has_response_dto,
            'hasListResponseDto': has_list_response_dto,
            'hasGetDto': has_get_dto,
            'createDtoName': create_dto_name,
            'updateDtoName': update_dto_name,
            'responseDtoName': response_dto_name,
            'listResponseDtoName': list_response_dto_name,
            'dtoImports': dto_imports,
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
        main_class_name = self.project_config['project']['params']['configOptions']['mainClass']  # UserServiceApplication
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
        Generate complete Hexagonal Architecture project from OpenAPI specs.

        Orchestrates the generation of all project components including domain models,
        application services, infrastructure adapters, and supporting files.
        """
        print("Generating Hexagonal Architecture Spring Boot project from OpenAPI specs...")
        
        all_schemas = {}
        all_operations = []
        all_entities = set()
        
        # Process each OpenAPI spec
        for spec_info in self.openapi_specs:
            openapi_spec = spec_info['spec']
            service_name = spec_info['service_name']
            
            print(f"Processing {service_name} service...")
            
            # Extract data from OpenAPI spec
            schemas = openapi_spec.get('components', {}).get('schemas', {})
            paths = openapi_spec.get('paths', {})
            
            # Store schemas with service context
            for schema_name, schema_data in schemas.items():
                all_schemas[f"{service_name}_{schema_name}"] = {
                    'data': schema_data,
                    'service': service_name,
                    'original_name': schema_name
                }
            
            # Extract operations
            for path, methods in paths.items():
                for method, operation_data in methods.items():
                    if 'operationId' in operation_data:
                        all_operations.append({
                            'id': operation_data['operationId'],
                            'service': service_name
                        })
            
            # Extract entities from schemas (look for Response schemas)
            for schema_name in schemas.keys():
                if schema_name.endswith('Response') or schema_name.endswith('ResponseContent'):
                    entity_name = schema_name.replace('Response', '').replace('ResponseContent', '')
                    if entity_name.startswith('Get'):
                        entity_name = entity_name[3:]  # Remove 'Get' prefix
                    
                    if entity_name:
                        all_entities.add(entity_name)
        
        # Generate DTOs from all schemas (excluding Error DTOs)
        for schema_key, schema_info in all_schemas.items():
            if schema_info['data'].get('type') == 'object' and 'Error' not in schema_info['original_name']:
                self.generate_dto(schema_info['original_name'], schema_info['data'], schema_info['service'])
        
        # Generate EntityStatus enum
        self.generate_entity_status_enum()
        
        # Generate domain models for all entities
        for entity in all_entities:
            # Find the main response schema for this entity
            entity_schema = None
            for schema_key, schema_info in all_schemas.items():
                original_name = schema_info['original_name']
                if original_name == f'{entity}Response' or original_name == f'Get{entity}ResponseContent':
                    entity_schema = schema_info['data']
                    break
            
            if entity_schema:
                self.generate_domain_model(entity, entity_schema)
                self.generate_domain_port_output(entity)
        
        # Generate application layer mappers (only for domain entities, not DTOs)
        domain_entities = set()
        for entity in all_entities:
            # Only generate mappers for entities that have domain models (not DTOs)
            if ('Error' not in entity and 'Content' not in entity and 
                not entity.startswith(('Create', 'Get', 'Update', 'Delete', 'List'))):
                domain_entities.add(entity)
        
        for entity in domain_entities:
            # Find service name for this entity
            entity_service = None
            for spec_info in self.openapi_specs:
                if any(entity in schema_name for schema_name in spec_info['spec'].get('components', {}).get('schemas', {})):
                    entity_service = spec_info['service_name']
                    break
            self.generate_mapper(entity, entity_service)
        
        # Group operations by entity for consolidated services
        entity_operations = {}
        for operation_info in all_operations:
            # Extract entity name from operation - only for basic CRUD operations
            entity_name = None
            op_id = operation_info['id']
            
            # Only process basic CRUD operations that match domain entities
            for entity in all_entities:
                if (op_id == f'Create{entity}' or op_id == f'Get{entity}' or 
                    op_id == f'Update{entity}' or op_id == f'Delete{entity}' or 
                    op_id == f'List{entity}s'):
                    entity_name = entity
                    break
            
            if entity_name:
                if entity_name not in entity_operations:
                    entity_operations[entity_name] = []
                entity_operations[entity_name].append(operation_info)
        
        # Generate consolidated services and use cases for each entity
        for entity_name, operations in entity_operations.items():
            # Find complex operations for this entity
            complex_operations = []
            for op in all_operations:
                op_id = op['id']
                if (op_id not in [o['id'] for o in operations] and 
                    (op_id.startswith('Get') and 'By' in op_id and 
                     (entity_name.lower() in op_id.lower() or 
                      any(related in op_id for related in ['Cities', 'Countries', 'Regions', 'Neighborhoods']) and entity_name == 'Location'))):
                    complex_operations.append(op_id)
            
            # Generate consolidated use case interfaces
            self.generate_consolidated_use_cases(entity_name, operations, complex_operations)
            # Generate consolidated service
            self.generate_consolidated_service(entity_name, operations, complex_operations)
        
        # Generate infrastructure layer
        for entity in all_entities:
            # Find entity schema
            entity_schema = None
            for schema_key, schema_info in all_schemas.items():
                original_name = schema_info['original_name']
                if original_name == f'{entity}Response' or original_name == f'Get{entity}ResponseContent':
                    entity_schema = schema_info['data']
                    break
            
            if entity_schema:
                self.generate_entity(entity, entity_schema)
                self.generate_jpa_repository(entity, entity_schema)
                self.generate_repository_adapter(entity)
        
        # Generate REST controllers for entities with consolidated use cases + complex operations
        for entity_name in entity_operations.keys():
            if ('Error' not in entity_name and 'Content' not in entity_name and 
                not entity_name.startswith(('Create', 'Get', 'Update', 'Delete', 'List'))):
                # Find CRUD operations for this entity
                crud_operations = [op['id'] for op in entity_operations[entity_name]]
                
                # Find complex operations related to this entity
                complex_operations = []
                for op in all_operations:
                    op_id = op['id']
                    # Check if operation is related to this entity but not a basic CRUD
                    if (op_id not in crud_operations and 
                        (op_id.startswith('Get') and 'By' in op_id and 
                         (entity_name.lower() in op_id.lower() or 
                          any(related in op_id for related in ['Cities', 'Countries', 'Regions', 'Neighborhoods']) and entity_name == 'Location'))):
                        complex_operations.append(op_id)
                
                # Combine CRUD and complex operations
                all_available_operations = crud_operations + complex_operations
                
                # Get service name from first operation
                service_name = entity_operations[entity_name][0]['service'] if entity_operations[entity_name] else entity_name.lower()
                self.generate_rest_controller(entity_name, all_available_operations, service_name)
        
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
        project_info = self.project_config.get('project', {}).get('general', {})
        print(f"Project: {project_info.get('name', 'generated-project')} v{project_info.get('version', '1.0.0')}")
        print(f"Description: {project_info.get('description', 'Generated project')}")
        print(f"Generated {len(all_schemas)} DTOs from {len(self.openapi_specs)} OpenAPI specs")
        print(f"Generated {len(all_operations)} use cases from operations")
        print(f"Generated {len(all_entities)} entities: {', '.join(sorted(all_entities))}")
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
    
    # Clean and create projects directory
    projects_dir = Path("projects")
    if projects_dir.exists():
        import shutil
        shutil.rmtree(projects_dir)
        print(f"🗑️ Cleaned existing projects directory")
    projects_dir.mkdir(exist_ok=True)
    print(f"📁 Created projects directory")

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python hexagonal-architecture-generator.py [templates_dir]")
        print("Example: python hexagonal-architecture-generator.py templates/java")
        print("Config: libs/config/params.json (array of project configurations)")
        sys.exit(0)
    
    config_path = "libs/config/params.json"
    templates_dir = sys.argv[1] if len(sys.argv) > 1 else "templates/java"
    
    try:
        # Load all project configurations
        projects_config = HexagonalArchitectureGenerator.load_projects_config(config_path)
        
        print(f"Found {len(projects_config)} project(s) to generate...")
        
        # Generate each project
        for i, project_config in enumerate(projects_config, 1):
            project_name = project_config['project']['general']['name']
            print(f"\n[{i}/{len(projects_config)}] Generating project: {project_name}")
            
            generator = HexagonalArchitectureGenerator(config_path, templates_dir, project_config)
            generator.generate_complete_project()
            
        print(f"\n✅ Successfully generated {len(projects_config)} project(s)!")
        
    except Exception as e:
        print(f"Error generating projects: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()