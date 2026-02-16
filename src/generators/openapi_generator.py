"""
OpenAPI 3.0 contract generator.
Deterministic output from spec.
"""

from typing import Dict, Any
from src.models import SpecModel, EntityModel, FieldType, HttpMethod
import yaml


class OpenAPIGenerator:
    """Generate OpenAPI 3.0 specification"""
    
    @staticmethod
    def generate(spec: SpecModel) -> Dict[str, Any]:
        """Generate OpenAPI document from spec"""
        
        openapi_doc = {
            "openapi": "3.0.0",
            "info": {
                "title": spec.project.name,
                "version": spec.project.version,
                "description": spec.project.description or "",
            },
            "servers": [
                {
                    "url": f"http://localhost:{spec.project.port}",
                    "description": "Development server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            }
        }
        
        # Collect all entities as schemas
        all_entities = {}
        OpenAPIGenerator._collect_entities(spec.modules, all_entities)
        
        # Generate schemas
        for entity_name, entity in all_entities.items():
            openapi_doc["components"]["schemas"][entity_name] = \
                OpenAPIGenerator._entity_to_schema(entity)
        
        # Generate paths from endpoints
        OpenAPIGenerator._generate_paths(spec.modules, openapi_doc)
        
        return openapi_doc
    
    @staticmethod
    def _collect_entities(modules, entities_dict):
        """Recursively collect all entities"""
        for module in modules:
            for entity in module.entities:
                entities_dict[entity.name] = entity
            OpenAPIGenerator._collect_entities(module.submodules, entities_dict)
    
    @staticmethod
    def _entity_to_schema(entity: EntityModel) -> Dict[str, Any]:
        """Convert entity to OpenAPI schema"""
        properties = {}
        required = []
        
        for field in entity.fields:
            properties[field.name] = OpenAPIGenerator._field_to_property(field)
            if not field.nullable and not field.primary:
                required.append(field.name)
        
        schema = {
            "type": "object",
            "properties": properties,
        }
        
        if required:
            schema["required"] = required
        
        if entity.description:
            schema["description"] = entity.description
        
        return schema
    
    @staticmethod
    def _field_to_property(field) -> Dict[str, Any]:
        """Convert field to OpenAPI property"""
        type_mapping = {
            FieldType.STRING: {"type": "string"},
            FieldType.INTEGER: {"type": "integer"},
            FieldType.FLOAT: {"type": "number", "format": "float"},
            FieldType.BOOLEAN: {"type": "boolean"},
            FieldType.UUID: {"type": "string", "format": "uuid"},
            FieldType.DATETIME: {"type": "string", "format": "date-time"},
            FieldType.DATE: {"type": "string", "format": "date"},
            FieldType.TEXT: {"type": "string"},
            FieldType.JSON: {"type": "object"},
            FieldType.ENUM: {
                "type": "string",
                "enum": field.enum_values or []
            },
        }
        
        prop = type_mapping.get(field.type, {"type": "string"})
        
        if field.description:
            prop["description"] = field.description
        
        if field.min_length is not None:
            prop["minLength"] = field.min_length
        
        if field.max_length is not None:
            prop["maxLength"] = field.max_length
        
        if field.default is not None:
            prop["default"] = field.default
        
        return prop
    
    @staticmethod
    def _generate_paths(modules, openapi_doc, base_path=""):
        """Generate OpenAPI paths from endpoints"""
        for module in modules:
            module_path = f"{base_path}/{module.name}"
            
            for endpoint in module.endpoints:
                full_path = f"{module_path}{endpoint.path}"
                method = endpoint.method.value.lower()
                
                if full_path not in openapi_doc["paths"]:
                    openapi_doc["paths"][full_path] = {}
                
                operation = {
                    "operationId": endpoint.handler,
                    "summary": endpoint.description or endpoint.handler,
                    "responses": {
                        "200": {
                            "description": "Successful response"
                        }
                    }
                }
                
                # Add request body
                if endpoint.request_body:
                    operation["requestBody"] = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{endpoint.request_body}"
                                }
                            }
                        }
                    }
                
                # Add response body
                if endpoint.response_body:
                    operation["responses"]["200"]["content"] = {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{endpoint.response_body}"
                            }
                        }
                    }
                
                # Add parameters
                parameters = []
                for param in endpoint.path_params:
                    parameters.append({
                        "name": param,
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    })
                
                for param in endpoint.query_params:
                    parameters.append({
                        "name": param,
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"}
                    })
                
                if parameters:
                    operation["parameters"] = parameters
                
                # Add security
                if endpoint.authenticated:
                    operation["security"] = [{"bearerAuth": []}]
                
                openapi_doc["paths"][full_path][method] = operation
            
            # Process submodules
            OpenAPIGenerator._generate_paths(
                module.submodules, openapi_doc, module_path
            )
        
        # Add security scheme if any endpoint is authenticated
        if any(OpenAPIGenerator._has_authenticated_endpoint(m) for m in modules):
            openapi_doc["components"]["securitySchemes"]["bearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
    
    @staticmethod
    def _has_authenticated_endpoint(module) -> bool:
        """Check if module has any authenticated endpoint"""
        if any(e.authenticated for e in module.endpoints):
            return True
        return any(
            OpenAPIGenerator._has_authenticated_endpoint(sub)
            for sub in module.submodules
        )
    
    @staticmethod
    def save_yaml(openapi_doc: Dict[str, Any], output_path: str):
        """Save OpenAPI document as YAML"""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(openapi_doc, f, default_flow_style=False, sort_keys=False)
    
    @staticmethod
    def save_json(openapi_doc: Dict[str, Any], output_path: str):
        """Save OpenAPI document as JSON"""
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(openapi_doc, f, indent=2)
