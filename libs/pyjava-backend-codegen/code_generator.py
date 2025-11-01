"""
Main code generator orchestrating the entire generation process.
"""
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any

from config_loader import ConfigLoader
from openapi_processor import OpenApiProcessor
from template_renderer import TemplateRenderer
from file_manager import FileManager
from property_converter import PropertyConverter


class CodeGenerator:
    """Main code generator for Hexagonal Architecture Spring Boot projects."""
    
    def __init__(self, config_path: str, templates_dir: str, project_config: Dict[str, Any]):
        self.config_path = config_path
        self.templates_dir = Path(templates_dir)
        self.project_config = project_config
        self.output_dir = Path("projects") / project_config['project']['general']['name']
        self.base_package = project_config['project']['params']['configOptions']['basePackage']
        
        # Initialize components
        self.config_loader = ConfigLoader()
        self.openapi_processor = OpenApiProcessor(project_config['project']['general']['folder'])
        self.template_renderer = TemplateRenderer(templates_dir)
        self.file_manager = FileManager(self.output_dir)
        self.property_converter = PropertyConverter()
        
        # Build context
        self.openapi_specs = self.openapi_processor.load_openapi_specs()
        self.target_packages = self.config_loader.build_package_structure(self.base_package)
        self.mustache_context = self.config_loader.build_mustache_context(project_config, self.target_packages)
    
    def generate_complete_project(self):
        """Generate complete Hexagonal Architecture project from OpenAPI specs."""
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
                self._generate_dto(schema_info['original_name'], schema_info['data'], schema_info['service'])
        
        # Generate EntityStatus enum
        self._generate_entity_status_enum()
        
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
                self._generate_domain_model(entity, entity_schema)
                self._generate_domain_port_output(entity)
        
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
            self._generate_mapper(entity, entity_service)
        
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
            self._generate_consolidated_use_cases(entity_name, operations, complex_operations)
            # Generate consolidated service
            self._generate_consolidated_service(entity_name, operations, complex_operations)
        
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
                self._generate_entity(entity, entity_schema)
                self._generate_jpa_repository(entity, entity_schema)
                self._generate_repository_adapter(entity)
        
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
                self._generate_rest_controller(entity_name, all_available_operations, service_name)
        
        # Generate supporting files
        self._generate_main_application()
        self._generate_configuration()
        self._generate_pom_xml()
        self._generate_application_properties()
        self._generate_readme()
        self._generate_docker_compose()
        self._generate_dockerfile()
        self._generate_maven_wrapper()
        
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
    
    def _generate_dtos(self, all_schemas: Dict[str, Any]):
        """Generate DTOs from all schemas."""
        for schema_key, schema_info in all_schemas.items():
            if schema_info['data'].get('type') == 'object' and 'Error' not in schema_info['original_name']:
                self._generate_dto(schema_info['original_name'], schema_info['data'], schema_info['service'])
    
    def _generate_dto(self, schema_name: str, schema_data: Dict[str, Any], service_name: str):
        """Generate application DTOs from OpenAPI schema."""
        context = self.mustache_context.copy()
        
        properties = schema_data.get('properties', {})
        required_fields = schema_data.get('required', [])
        
        vars_list = []
        imports = set()
        
        for prop_name, prop_data in properties.items():
            var_info = self.property_converter.convert_openapi_property(prop_name, prop_data, required_fields)
            vars_list.append(var_info)
            if var_info.get('import'):
                imports.add(var_info['import'])
        
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
        
        content = self.template_renderer.render_template('pojo.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(dto_package) / f"{schema_name}.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_domain_layer(self, all_entities: List[str], all_schemas: Dict[str, Any]):
        """Generate domain layer components."""
        # Generate EntityStatus enum
        self._generate_entity_status_enum()
        
        # Generate domain models and ports
        for entity in all_entities:
            entity_schema = self._find_entity_schema(entity, all_schemas)
            if entity_schema:
                self._generate_domain_model(entity, entity_schema)
                self._generate_domain_port_output(entity)
    
    def _generate_application_layer(self, entity_operations: Dict[str, List[Dict[str, Any]]], 
                                  entity_complex_ops: Dict[str, List[str]], openapi_specs: List[Dict[str, Any]]):
        """Generate application layer components."""
        # Generate mappers for all domain entities
        domain_entities = set()
        for entity in all_entities:
            if ('Error' not in entity and 'Content' not in entity and 
                not entity.startswith(('Create', 'Get', 'Update', 'Delete', 'List'))):
                domain_entities.add(entity)
        
        for entity in domain_entities:
            entity_service = self._find_entity_service(entity, openapi_specs)
            self._generate_mapper(entity, entity_service)
        
        # Generate consolidated services and use cases
        for entity_name, operations in entity_operations.items():
            complex_operations = entity_complex_ops.get(entity_name, [])
            self._generate_consolidated_use_cases(entity_name, operations, complex_operations)
            self._generate_consolidated_service(entity_name, operations, complex_operations)
    
    def _generate_infrastructure_layer(self, all_entities: List[str], all_schemas: Dict[str, Any],
                                     entity_operations: Dict[str, List[Dict[str, Any]]], 
                                     entity_complex_ops: Dict[str, List[str]]):
        """Generate infrastructure layer components."""
        # Generate persistence layer
        for entity in all_entities:
            entity_schema = self._find_entity_schema(entity, all_schemas)
            if entity_schema:
                self._generate_entity(entity, entity_schema)
                self._generate_jpa_repository(entity, entity_schema)
                self._generate_repository_adapter(entity)
        
        # Generate REST controllers
        for entity_name in entity_operations.keys():
            if self._is_domain_entity(entity_name):
                crud_operations = [op['id'] for op in entity_operations[entity_name]]
                complex_operations = entity_complex_ops.get(entity_name, [])
                all_available_operations = crud_operations + complex_operations
                service_name = entity_operations[entity_name][0]['service'] if entity_operations[entity_name] else entity_name.lower()
                self._generate_rest_controller(entity_name, all_available_operations, service_name)
    
    def _generate_supporting_files(self):
        """Generate supporting files like main class, configuration, etc."""
        self._generate_main_application()
        self._generate_configuration()
        self._generate_pom_xml()
        self._generate_application_properties()
        self._generate_readme()
        self._generate_docker_compose()
        self._generate_dockerfile()
        self._generate_maven_wrapper()
    
    # Helper methods for template generation (simplified versions of original methods)
    def _find_entity_schema(self, entity: str, all_schemas: Dict[str, Any]) -> Dict[str, Any]:
        """Find the main response schema for an entity."""
        for schema_key, schema_info in all_schemas.items():
            original_name = schema_info['original_name']
            if original_name == f'{entity}Response' or original_name == f'Get{entity}ResponseContent':
                return schema_info['data']
        return None
    
    def _filter_domain_entities(self, entities) -> List[str]:
        """Filter entities to only include domain entities."""
        return [entity for entity in entities 
                if ('Error' not in entity and 'Content' not in entity and 
                    not entity.startswith(('Create', 'Get', 'Update', 'Delete', 'List')))]
    
    def _find_entity_service(self, entity: str, openapi_specs: List[Dict[str, Any]]) -> str:
        """Find service name for an entity."""
        for spec_info in openapi_specs:
            if any(entity in schema_name for schema_name in spec_info['spec'].get('components', {}).get('schemas', {})):
                return spec_info['service_name']
        return entity.lower()
    
    def _is_domain_entity(self, entity_name: str) -> bool:
        """Check if entity is a domain entity."""
        return ('Error' not in entity_name and 'Content' not in entity_name and 
                not entity_name.startswith(('Create', 'Get', 'Update', 'Delete', 'List')))
    
    def _print_generation_summary(self, all_schemas: Dict[str, Any], all_operations: List[Dict[str, Any]], all_entities: List[str]):
        """Print generation summary."""
        project_info = self.project_config.get('project', {}).get('general', {})
        print(f"\nHexagonal Architecture project generated successfully in: {self.output_dir}")
        print(f"Project: {project_info.get('name', 'generated-project')} v{project_info.get('version', '1.0.0')}")
        print(f"Description: {project_info.get('description', 'Generated project')}")
        print(f"Generated {len(all_schemas)} DTOs from {len(self.openapi_processor.load_openapi_specs())} OpenAPI specs")
        print(f"Generated {len(all_operations)} use cases from operations")
        print(f"Generated {len(all_entities)} entities: {', '.join(sorted(all_entities))}")
        print("\nProject structure follows Hexagonal Architecture principles:")
        print("- Domain: Pure business logic and ports")
        print("- Application: Use case implementations and DTOs")
        print("- Infrastructure: External adapters (REST, JPA, Config)")
    
    # Implementation methods from original generator
    def _generate_dto(self, schema_name: str, schema_data: Dict[str, Any], service_name: str):
        """Generate application DTOs from OpenAPI schema."""
        context = self.mustache_context.copy()
        
        properties = schema_data.get('properties', {})
        required_fields = schema_data.get('required', [])
        
        vars_list = []
        imports = set()
        
        for prop_name, prop_data in properties.items():
            var_info = self.property_converter.convert_openapi_property(prop_name, prop_data, required_fields)
            vars_list.append(var_info)
            if var_info.get('import'):
                imports.add(var_info['import'])
        
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
        
        content = self.template_renderer.render_template('pojo.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(dto_package) / f"{schema_name}.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_entity_status_enum(self):
        """Generate EntityStatus enum for domain layer."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['domain_model'],
            'classname': 'EntityStatus'
        })
        
        content = self.template_renderer.render_template('EntityStatus.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['domain_model']) / "EntityStatus.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_domain_model(self, entity: str, schema: Dict[str, Any]):
        """Generate domain model (pure POJO) from OpenAPI schema."""
        context = self.mustache_context.copy()
        
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        vars_list = []
        imports = set()
        
        for prop_name, prop_data in properties.items():
            var_info = self.property_converter.convert_openapi_property(prop_name, prop_data, required_fields)
            var_info['hasValidation'] = False
            var_info['validationAnnotations'] = []
            vars_list.append(var_info)
            if var_info.get('import'):
                imports.add(var_info['import'])
        
        context.update({
            'packageName': self.target_packages['domain_model'],
            'classname': entity,
            'vars': vars_list,
            'imports': [{'import': imp} for imp in sorted(imports)],
            'models': [{'model': {'classname': entity, 'vars': vars_list}}],
            'isDomainModel': True,
            'useJPA': False,
            'useLombok': True
        })
        
        content = self.template_renderer.render_template('pojo.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['domain_model']) / f"{entity}.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_domain_port_output(self, entity: str):
        """Generate domain repository port (interface)."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['domain_ports_output'],
            'classname': f"{entity}RepositoryPort",
            'entityName': entity,
            'entityVarName': entity.lower(),
            'interfaceOnly': True,
            'isDomainPort': True
        })
        
        content = self.template_renderer.render_template('interface.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['domain_ports_output']) / f"{entity}RepositoryPort.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_mapper(self, entity: str, service: str):
        """Generate mapper for entity transformations."""
        dto_base_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['application_dto'])
        
        if not service:
            # Find service from openapi specs
            openapi_specs = self.openapi_processor.load_openapi_specs()
            for spec_info in openapi_specs:
                if any(entity in schema_name for schema_name in spec_info['spec'].get('components', {}).get('schemas', {})):
                    service = spec_info['service_name']
                    break
        
        if not service:
            service = entity.lower()
        
        # Check for specific DTOs
        create_dto_name = f"Create{entity}RequestContent"
        update_dto_name = f"Update{entity}RequestContent"
        response_dto_name = f"{entity}Response"
        list_response_dto_name = f"List{entity}sResponseContent"
        
        has_create_dto = False
        has_update_dto = False
        has_response_dto = False
        has_list_response_dto = False
        has_get_dto = False
        
        # Check if DTOs exist in service folders
        if dto_base_path.exists():
            for service_folder in dto_base_path.iterdir():
                if service_folder.is_dir():
                    if (service_folder / f"{create_dto_name}.java").exists():
                        has_create_dto = True
                        service = service_folder.name
                    if (service_folder / f"{update_dto_name}.java").exists():
                        has_update_dto = True
                        service = service_folder.name
                    if (service_folder / f"{response_dto_name}.java").exists():
                        has_response_dto = True
                        service = service_folder.name
                    if (service_folder / f"{list_response_dto_name}.java").exists():
                        has_list_response_dto = True
                        service = service_folder.name
                    if (service_folder / f"Get{entity}ResponseContent.java").exists():
                        has_get_dto = True
                        service = service_folder.name
        
        # Build DTO imports
        dto_imports = []
        if has_create_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.{create_dto_name}')
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.Create{entity}ResponseContent')
        if has_update_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.{update_dto_name}')
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.Update{entity}ResponseContent')
        if has_response_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.{response_dto_name}')
        if has_list_response_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.{list_response_dto_name}')
        if has_get_dto:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.Get{entity}ResponseContent')
        
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['application_mapper'],
            'classname': f"{entity}Mapper",
            'entityName': entity,
            'entityVarName': entity.lower(),
            'dboName': f"{entity}Dbo",
            'serviceName': service,
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
        
        content = self.template_renderer.render_template('apiMapper.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['application_mapper']) / f"{entity}Mapper.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_consolidated_use_cases(self, entity: str, operations: List[Dict[str, Any]], complex_ops: List[str]):
        """Generate consolidated use case interfaces for an entity."""
        service_name = operations[0]['service'] if operations else entity.lower()
        
        dto_base_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['application_dto']) / service_name
        
        has_create = self.file_manager.check_dto_exists(dto_base_path, f'Create{entity}RequestContent') and self.file_manager.check_dto_exists(dto_base_path, f'Create{entity}ResponseContent')
        has_get = self.file_manager.check_dto_exists(dto_base_path, f'Get{entity}ResponseContent')
        has_update = self.file_manager.check_dto_exists(dto_base_path, f'Update{entity}RequestContent') and self.file_manager.check_dto_exists(dto_base_path, f'Update{entity}ResponseContent')
        has_delete = self.file_manager.check_dto_exists(dto_base_path, f'Delete{entity}ResponseContent')
        has_list = self.file_manager.check_dto_exists(dto_base_path, f'List{entity}sResponseContent')
        
        complex_ops_info = []
        if complex_ops:
            for op in complex_ops:
                if self.file_manager.check_dto_exists(dto_base_path, f'{op}ResponseContent'):
                    method_name = op[0].lower() + op[1:] if op else ''
                    complex_ops_info.append({
                        'operationId': op,
                        'methodName': method_name,
                        'responseType': f'{op}ResponseContent'
                    })
        
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['domain_ports_input'],
            'classname': f'{entity}UseCase',
            'entityName': entity,
            'entityVarName': entity.lower(),
            'serviceName': service_name,
            'hasCreate': has_create,
            'hasGet': has_get,
            'hasUpdate': has_update,
            'hasDelete': has_delete,
            'hasList': has_list,
            'hasComplexOperations': len(complex_ops_info) > 0,
            'complexOperations': complex_ops_info
        })
        
        content = self.template_renderer.render_template('consolidatedUseCase.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['domain_ports_input']) / f'{entity}UseCase.java'
        self.file_manager.write_file(file_path, content)
    
    def _generate_consolidated_service(self, entity: str, operations: List[Dict[str, Any]], complex_ops: List[str]):
        """Generate consolidated application service."""
        entity_var_name = entity.lower()
        service_name = operations[0]['service'] if operations else entity_var_name
        
        has_create = any(op['id'].startswith('Create') and entity in op['id'] for op in operations)
        has_get = any(op['id'].startswith('Get') and entity in op['id'] for op in operations)
        has_update = any(op['id'].startswith('Update') and entity in op['id'] for op in operations)
        has_delete = any(op['id'].startswith('Delete') and entity in op['id'] for op in operations)
        has_list = any(op['id'] == f'List{entity}s' for op in operations)
        
        complex_ops_info = []
        if complex_ops:
            for op in complex_ops:
                method_name = op[0].lower() + op[1:] if op else ''
                complex_ops_info.append({
                    'operationId': op,
                    'methodName': method_name,
                    'responseType': f'{op}ResponseContent'
                })
        
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['application_service'],
            'classname': f"{entity}Service",
            'entityName': entity,
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
        
        content = self.template_renderer.render_template('consolidatedService.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['application_service']) / f"{entity}Service.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_entity(self, entity: str, schema: Dict[str, Any]):
        """Generate JPA entity (DBO) from OpenAPI schema."""
        context = self.mustache_context.copy()
        
        if schema:
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])
            
            vars_list = []
            imports = set()
            
            for prop_name, prop_data in properties.items():
                if prop_name not in ['createdAt', 'updatedAt', 'status'] and not prop_name.endswith('Id'):
                    var_info = self.property_converter.convert_openapi_property(prop_name, prop_data, required_fields)
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
            'classname': f"{entity}Dbo",
            'entityName': entity,
            'entityVarName': entity.lower(),
            'tableName': entity.lower() + 's',
            'isEntity': True,
            'useJPA': True,
            'useLombok': True
        })
        
        content = self.template_renderer.render_template('apiEntity.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_entity']) / f"{entity}Dbo.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_jpa_repository(self, entity: str, schema: Dict[str, Any]):
        """Generate Spring Data JPA repository."""
        search_fields = []
        if schema:
            properties = schema.get('properties', {})
            field_priorities = ['name', 'title', 'description']
            for field in field_priorities:
                if field in properties:
                    search_fields.append(field)
        
        search_conditions = []
        if search_fields:
            for field in search_fields:
                search_conditions.append(f"LOWER(e.{field}) LIKE LOWER(CONCAT('%', :search, '%'))")
        else:
            search_conditions.append("LOWER(CAST(e.id AS string)) LIKE LOWER(CONCAT('%', :search, '%'))")
        
        search_query = " OR ".join(search_conditions)
        
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['infra_repository'],
            'classname': f"Jpa{entity}Repository",
            'entityName': entity,
            'searchFields': search_fields,
            'searchQuery': search_query,
            'hasSearchFields': len(search_fields) > 0,
            'isJpaRepository': True,
            'isAdapter': False
        })
        
        content = self.template_renderer.render_template('apiRepository.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_repository']) / f"Jpa{entity}Repository.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_repository_adapter(self, entity: str):
        """Generate repository adapter."""
        context = self.mustache_context.copy()
        context.update({
            'packageName': self.target_packages['infra_adapter'],
            'classname': f"{entity}RepositoryAdapter",
            'entityName': entity,
            'entityVarName': entity.lower(),
            'dboName': f"{entity}Dbo",
            'portName': f"{entity}RepositoryPort",
            'jpaRepositoryName': f"Jpa{entity}Repository",
            'isJpaRepository': False,
            'isAdapter': True
        })
        
        content = self.template_renderer.render_template('apiRepository.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_adapter']) / f"{entity}RepositoryAdapter.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_rest_controller(self, entity: str, operations: List[str], service: str):
        """Generate REST controller."""
        crud_operations = [op for op in operations if any(op.startswith(prefix + entity) for prefix in ['Create', 'Get', 'Update', 'Delete']) or op == f'List{entity}s']
        complex_operations = [op for op in operations if op not in crud_operations]
        
        dto_imports = []
        if f'Create{entity}' in operations:
            dto_imports.extend([
                f'{self.target_packages["application_dto"]}.{service}.Create{entity}RequestContent',
                f'{self.target_packages["application_dto"]}.{service}.Create{entity}ResponseContent'
            ])
        if f'Get{entity}' in operations:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.Get{entity}ResponseContent')
        if f'Update{entity}' in operations:
            dto_imports.extend([
                f'{self.target_packages["application_dto"]}.{service}.Update{entity}RequestContent',
                f'{self.target_packages["application_dto"]}.{service}.Update{entity}ResponseContent'
            ])
        if f'Delete{entity}' in operations:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.Delete{entity}ResponseContent')
        if f'List{entity}s' in operations:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.List{entity}sResponseContent')
        
        for op in complex_operations:
            dto_imports.append(f'{self.target_packages["application_dto"]}.{service}.{op}ResponseContent')
        
        usecase_imports = [f'{self.target_packages["domain_ports_input"]}.{entity}UseCase']
        
        complex_ops_info = []
        for op in complex_operations:
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
            'classname': f"{entity}Controller",
            'entityName': entity,
            'entityVarName': entity.lower(),
            'entityPath': entity.lower() + 's',
            'entityIdPath': f'{{{entity.lower()}Id}}',
            'hasCreate': f'Create{entity}' in operations,
            'hasGet': f'Get{entity}' in operations,
            'hasUpdate': f'Update{entity}' in operations,
            'hasDelete': f'Delete{entity}' in operations,
            'hasList': f'List{entity}s' in operations,
            'hasComplexOperations': len(complex_operations) > 0,
            'complexOperations': complex_ops_info,
            'serviceName': service,
            'dtoImports': dto_imports,
            'useCaseImports': usecase_imports,
            'isController': True,
            'useSpringWeb': True
        })
        
        content = self.template_renderer.render_template('apiController.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_adapters_input_rest']) / f"{entity}Controller.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_main_application(self):
        """Generate Spring Boot main application class."""
        context = self.mustache_context.copy()
        main_class_name = self.project_config['project']['params']['configOptions']['mainClass']
        context.update({
            'packageName': self.target_packages['root'],
            'classname': main_class_name
        })
        
        content = self.template_renderer.render_template('Application.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['root']) / f"{main_class_name}.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_configuration(self):
        """Generate Spring configuration classes."""
        context = self.mustache_context.copy()
        
        # Main application configuration
        context.update({
            'packageName': self.target_packages['infra_config'],
            'classname': 'ApplicationConfiguration'
        })
        content = self.template_renderer.render_template('Configuration.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_config']) / "ApplicationConfiguration.java"
        self.file_manager.write_file(file_path, content)
        
        # Security configuration
        context.update({'classname': 'SecurityConfiguration', 'entityPath': 'users'})
        content = self.template_renderer.render_template('SecurityConfiguration.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_config']) / "SecurityConfiguration.java"
        self.file_manager.write_file(file_path, content)
        
        # OpenAPI configuration
        context.update({'classname': 'OpenApiConfiguration', 'entityName': 'User'})
        content = self.template_renderer.render_template('OpenApiConfiguration.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_config']) / "OpenApiConfiguration.java"
        self.file_manager.write_file(file_path, content)
        
        # Global exception handler
        context.update({
            'packageName': self.target_packages['infra_config_exceptions'],
            'classname': 'GlobalExceptionHandler'
        })
        content = self.template_renderer.render_template('GlobalExceptionHandler.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_config_exceptions']) / "GlobalExceptionHandler.java"
        self.file_manager.write_file(file_path, content)
        
        # NotFoundException
        context.update({'classname': 'NotFoundException'})
        content = self.template_renderer.render_template('NotFoundException.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['infra_config_exceptions']) / "NotFoundException.java"
        self.file_manager.write_file(file_path, content)
        
        # LoggingUtils
        context.update({
            'packageName': self.target_packages['utils'],
            'classname': 'LoggingUtils'
        })
        content = self.template_renderer.render_template('LoggingUtils.mustache', context)
        file_path = self.output_dir / self.file_manager.get_package_path(self.target_packages['utils']) / "LoggingUtils.java"
        self.file_manager.write_file(file_path, content)
    
    def _generate_pom_xml(self):
        """Generate Maven POM file."""
        content = self.template_renderer.render_template('pom.xml.mustache', self.mustache_context)
        file_path = self.output_dir / "pom.xml"
        self.file_manager.write_file(file_path, content)
    
    def _generate_application_properties(self):
        """Generate application.properties file."""
        content = self.template_renderer.render_template('application.properties.mustache', self.mustache_context)
        file_path = self.output_dir / "src/main/resources/application.properties"
        self.file_manager.write_file(file_path, content)
    
    def _generate_readme(self):
        """Generate project README file."""
        content = self.template_renderer.render_template('README.md.mustache', self.mustache_context)
        file_path = self.output_dir / "README.md"
        self.file_manager.write_file(file_path, content)
    
    def _generate_docker_compose(self):
        """Generate docker-compose.yml file."""
        content = self.template_renderer.render_template('docker-compose.yml.mustache', self.mustache_context)
        file_path = self.output_dir / "docker-compose.yml"
        self.file_manager.write_file(file_path, content)
    
    def _generate_dockerfile(self):
        """Generate Dockerfile."""
        content = self.template_renderer.render_template('Dockerfile.mustache', self.mustache_context)
        file_path = self.output_dir / "Dockerfile"
        self.file_manager.write_file(file_path, content)
    
    def _generate_maven_wrapper(self):
        """Generate Maven wrapper scripts."""
        # Unix/Linux/macOS wrapper
        content = self.template_renderer.render_template('mvnw.mustache', self.mustache_context)
        file_path = self.output_dir / "mvnw"
        self.file_manager.write_file(file_path, content)
        import os
        os.chmod(file_path, 0o755)
        
        # Windows wrapper
        content = self.template_renderer.render_template('mvnw.cmd.mustache', self.mustache_context)
        file_path = self.output_dir / "mvnw.cmd"
        self.file_manager.write_file(file_path, content)
        
        # Maven wrapper properties
        wrapper_dir = self.output_dir / ".mvn" / "wrapper"
        self.file_manager.ensure_directory(wrapper_dir)
        content = self.template_renderer.render_template('maven-wrapper.properties.mustache', self.mustache_context)
        file_path = wrapper_dir / "maven-wrapper.properties"
        self.file_manager.write_file(file_path, content)