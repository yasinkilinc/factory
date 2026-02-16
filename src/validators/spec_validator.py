"""
Deterministic fail-fast validator.
No AI inference, pure rule-based validation.
"""

import json
from typing import Dict, List, Tuple
from pathlib import Path
from pydantic import ValidationError
from src.models import SpecModel


class ValidationResult:
    """Validation result container"""
    
    def __init__(self):
        self.valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.spec: SpecModel = None
    
    def add_error(self, message: str):
        """Add critical error (fail-fast)"""
        self.valid = False
        self.errors.append(message)
    
    def add_warning(self, message: str):
        """Add non-critical warning"""
        self.warnings.append(message)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "spec_version": self.spec.spec_version if self.spec else None,
        }


class SpecValidator:
    """Deterministic spec validator"""
    
    @staticmethod
    def validate_file(spec_path: str) -> ValidationResult:
        """
        Validate spec from file path.
        Fail-fast on critical errors.
        """
        result = ValidationResult()
        
        # 1. File existence check
        path = Path(spec_path)
        if not path.exists():
            result.add_error(f"Spec file not found: {spec_path}")
            return result
        
        # 2. JSON parsing
        try:
            with open(path, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON: {str(e)}")
            return result
        except Exception as e:
            result.add_error(f"Failed to read file: {str(e)}")
            return result
        
        return SpecValidator.validate_dict(spec_data)
    
    @staticmethod
    def validate_dict(spec_data: Dict) -> ValidationResult:
        """
        Validate spec from dictionary.
        Fail-fast on critical errors.
        """
        result = ValidationResult()
        
        # 3. Pydantic validation (deterministic)
        try:
            spec = SpecModel(**spec_data)
            result.spec = spec
        except ValidationError as e:
            for error in e.errors():
                loc = " -> ".join(str(x) for x in error['loc'])
                result.add_error(f"{loc}: {error['msg']}")
            return result
        except Exception as e:
            result.add_error(f"Validation failed: {str(e)}")
            return result
        
        # 4. Additional semantic validations
        SpecValidator._validate_semantics(spec, result)
        
        return result
    
    @staticmethod
    def _validate_semantics(spec: SpecModel, result: ValidationResult):
        """Additional semantic validations"""
        
        # Check nesting depth warnings
        for module in spec.modules:
            depth = module.get_nesting_depth()
            if depth == 4:
                result.add_warning(
                    f"Module '{module.name}' at max nesting depth (4/4) - "
                    "consider refactoring"
                )
            elif depth >= 3:
                result.add_warning(
                    f"Module '{module.name}' nesting depth {depth}/4"
                )
        
        # Check entity references in endpoints
        SpecValidator._validate_entity_references(spec, result)
        
        # Check for duplicate names
        SpecValidator._validate_unique_names(spec, result)
        
        # Check module complexity
        SpecValidator._validate_module_complexity(spec, result)
    
    @staticmethod
    def _validate_entity_references(spec: SpecModel, result: ValidationResult):
        """Validate entity references in endpoints"""
        all_entities = set()
        
        def collect_entities(modules):
            for module in modules:
                for entity in module.entities:
                    all_entities.add(entity.name)
                collect_entities(module.submodules)
        
        collect_entities(spec.modules)
        
        def check_endpoints(modules, module_path=""):
            for module in modules:
                path = f"{module_path}/{module.name}" if module_path else module.name
                for endpoint in module.endpoints:
                    # Check request body
                    if endpoint.request_body and endpoint.request_body not in all_entities:
                        result.add_error(
                            f"Endpoint {path}{endpoint.path} references "
                            f"unknown entity: {endpoint.request_body}"
                        )
                    # Check response body
                    if endpoint.response_body and endpoint.response_body not in all_entities:
                        result.add_error(
                            f"Endpoint {path}{endpoint.path} references "
                            f"unknown entity: {endpoint.response_body}"
                        )
                check_endpoints(module.submodules, path)
        
        check_endpoints(spec.modules)
    
    @staticmethod
    def _validate_unique_names(spec: SpecModel, result: ValidationResult):
        """Check for duplicate entity and module names"""
        entity_names = []
        module_names = []
        
        def collect_names(modules):
            for module in modules:
                module_names.append(module.name)
                for entity in module.entities:
                    entity_names.append(entity.name)
                collect_names(module.submodules)
        
        collect_names(spec.modules)
        
        # Check duplicates
        entity_dups = [name for name in entity_names if entity_names.count(name) > 1]
        if entity_dups:
            result.add_error(f"Duplicate entity names: {set(entity_dups)}")
        
        module_dups = [name for name in module_names if module_names.count(name) > 1]
        if module_dups:
            result.add_error(f"Duplicate module names: {set(module_dups)}")
    
    @staticmethod
    def _validate_module_complexity(spec: SpecModel, result: ValidationResult):
        """Check module complexity"""
        def check_module(module, path=""):
            full_path = f"{path}/{module.name}" if path else module.name
            
            # Too many entities in single module
            if len(module.entities) > 10:
                result.add_warning(
                    f"Module '{full_path}' has {len(module.entities)} entities "
                    "(>10) - consider splitting"
                )
            
            # Too many endpoints
            if len(module.endpoints) > 20:
                result.add_warning(
                    f"Module '{full_path}' has {len(module.endpoints)} endpoints "
                    "(>20) - consider splitting"
                )
            
            for submodule in module.submodules:
                check_module(submodule, full_path)
        
        for module in spec.modules:
            check_module(module)


def validate_spec(spec_path: str) -> Tuple[bool, ValidationResult]:
    """
    Main validation entry point.
    
    Returns:
        (is_valid, validation_result)
    """
    result = SpecValidator.validate_file(spec_path)
    return result.valid, result
