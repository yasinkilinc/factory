"""
Tests for spec validator
"""

import pytest
from src.validators import SpecValidator, ValidationResult


def test_valid_spec():
    """Test with valid spec"""
    spec_data = {
        "specVersion": "1.0.0",
        "project": {
            "name": "test-service",
            "description": "Test service"
        },
        "modules": [
            {
                "name": "user",
                "entities": [
                    {
                        "name": "User",
                        "fields": [
                            {"name": "id", "type": "uuid", "primary": True},
                            {"name": "email", "type": "string"}
                        ]
                    }
                ],
                "endpoints": []
            }
        ]
    }
    
    result = SpecValidator.validate_dict(spec_data)
    assert result.valid
    assert len(result.errors) == 0


def test_invalid_spec_version():
    """Test with invalid spec version"""
    spec_data = {
        "specVersion": "2.0.0",  # Not supported
        "project": {"name": "test"},
        "modules": []
    }
    
    result = SpecValidator.validate_dict(spec_data)
    assert not result.valid
    assert len(result.errors) > 0


def test_missing_primary_key():
    """Test entity without primary key"""
    spec_data = {
        "specVersion": "1.0.0",
        "project": {"name": "test"},
        "modules": [
            {
                "name": "user",
                "entities": [
                    {
                        "name": "User",
                        "fields": [
                            {"name": "email", "type": "string"}
                        ]
                    }
                ],
                "endpoints": []
            }
        ]
    }
    
    result = SpecValidator.validate_dict(spec_data)
    assert not result.valid


def test_nesting_depth_warning():
    """Test nesting depth warning"""
    spec_data = {
        "specVersion": "1.0.0",
        "project": {"name": "test"},
        "modules": [
            {
                "name": "level1",
                "entities": [],
                "endpoints": [],
                "submodules": [
                    {
                        "name": "level2",
                        "entities": [],
                        "endpoints": [],
                        "submodules": [
                            {
                                "name": "level3",
                                "entities": [
                                    {
                                        "name": "Entity",
                                        "fields": [
                                            {"name": "id", "type": "uuid", "primary": True}
                                        ]
                                    }
                                ],
                                "endpoints": []
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    result = SpecValidator.validate_dict(spec_data)
    assert result.valid
    assert len(result.warnings) > 0


def test_duplicate_entity_names():
    """Test duplicate entity names"""
    spec_data = {
        "specVersion": "1.0.0",
        "project": {"name": "test"},
        "modules": [
            {
                "name": "mod1",
                "entities": [
                    {
                        "name": "User",
                        "fields": [{"name": "id", "type": "uuid", "primary": True}]
                    }
                ],
                "endpoints": []
            },
            {
                "name": "mod2",
                "entities": [
                    {
                        "name": "User",  # Duplicate
                        "fields": [{"name": "id", "type": "uuid", "primary": True}]
                    }
                ],
                "endpoints": []
            }
        ]
    }
    
    result = SpecValidator.validate_dict(spec_data)
    assert not result.valid
    assert any("duplicate" in str(e).lower() for e in result.errors)
