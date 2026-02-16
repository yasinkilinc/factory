"""
Tests for generators
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.models import SpecModel
from src.generators import OpenAPIGenerator


def test_openapi_generation():
    """Test OpenAPI generation"""
    spec_data = {
        "specVersion": "1.0.0",
        "project": {
            "name": "test-api",
            "version": "1.0.0",
            "port": 8080
        },
        "modules": [
            {
                "name": "user",
                "entities": [
                    {
                        "name": "User",
                        "fields": [
                            {"name": "id", "type": "uuid", "primary": True},
                            {"name": "email", "type": "string", "nullable": False}
                        ]
                    }
                ],
                "endpoints": [
                    {
                        "path": "/users",
                        "method": "GET",
                        "handler": "getUsers",
                        "response_body": "User"
                    }
                ]
            }
        ]
    }
    
    spec = SpecModel(**spec_data)
    openapi_doc = OpenAPIGenerator.generate(spec)
    
    assert openapi_doc["openapi"] == "3.0.0"
    assert openapi_doc["info"]["title"] == "test-api"
    assert "/user/users" in openapi_doc["paths"]
    assert "User" in openapi_doc["components"]["schemas"]


def test_openapi_schemas():
    """Test OpenAPI schema generation"""
    spec_data = {
        "specVersion": "1.0.0",
        "project": {"name": "test", "port": 8080},
        "modules": [
            {
                "name": "product",
                "entities": [
                    {
                        "name": "Product",
                        "fields": [
                            {"name": "id", "type": "uuid", "primary": True},
                            {"name": "name", "type": "string", "nullable": False, "max_length": 100},
                            {"name": "price", "type": "float", "nullable": False},
                            {"name": "stock", "type": "integer", "default": 0}
                        ]
                    }
                ],
                "endpoints": []
            }
        ]
    }
    
    spec = SpecModel(**spec_data)
    openapi_doc = OpenAPIGenerator.generate(spec)
    
    schema = openapi_doc["components"]["schemas"]["Product"]
    assert "name" in schema["properties"]
    assert "price" in schema["properties"]
    assert "name" in schema["required"]
    assert "price" in schema["required"]


def test_backend_generator_initialization():
    """Test backend generator initialization"""
    from src.generators import BackendGenerator
    
    # Test valid backend types
    gen_spring = BackendGenerator("spring-boot")
    assert gen_spring.backend_type == "spring-boot"
    
    gen_python = BackendGenerator("python")
    assert gen_python.backend_type == "python"
    
    # Test invalid backend type
    with pytest.raises(ValueError):
        BackendGenerator("invalid-type")
