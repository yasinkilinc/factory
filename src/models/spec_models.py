"""
Pydantic models for spec validation.
Deterministic, fail-fast validation.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class FieldType(str, Enum):
    """Supported field types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    UUID = "uuid"
    DATETIME = "datetime"
    DATE = "date"
    JSON = "json"
    TEXT = "text"
    ENUM = "enum"


class HttpMethod(str, Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class DecompositionPolicy(str, Enum):
    """Decomposition policy options"""
    DISABLED = "disabled"
    ADVISORY = "advisory"
    ENFORCED = "enforced"


class FieldModel(BaseModel):
    """Entity field definition"""
    name: str = Field(..., min_length=1, max_length=100)
    type: FieldType
    primary: bool = False
    unique: bool = False
    nullable: bool = True
    default: Optional[Any] = None
    enum_values: Optional[List[str]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_field_name(cls, v: str) -> str:
        """Validate field name (snake_case recommended)"""
        if not v.replace('_', '').isalnum():
            raise ValueError(f"Field name must be alphanumeric: {v}")
        return v

    @field_validator('enum_values')
    @classmethod
    def validate_enum(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """Validate enum values when type is enum"""
        field_type = info.data.get('type')
        if field_type == FieldType.ENUM and not v:
            raise ValueError("enum_values required when type is enum")
        return v


class RelationModel(BaseModel):
    """Entity relationship definition"""
    name: str
    type: Literal["one-to-one", "one-to-many", "many-to-one", "many-to-many"]
    target_entity: str
    foreign_key: Optional[str] = None
    cascade_delete: bool = False


class EntityModel(BaseModel):
    """Entity/Model definition"""
    name: str = Field(..., min_length=1, max_length=100)
    fields: List[FieldModel] = Field(..., min_length=1)
    relations: List[RelationModel] = []
    table_name: Optional[str] = None
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_entity_name(cls, v: str) -> str:
        """Validate entity name (PascalCase recommended)"""
        if not v[0].isupper():
            raise ValueError(f"Entity name should start with uppercase: {v}")
        if not v.replace('_', '').isalnum():
            raise ValueError(f"Entity name must be alphanumeric: {v}")
        return v

    @field_validator('fields')
    @classmethod
    def validate_primary_key(cls, v: List[FieldModel]) -> List[FieldModel]:
        """Ensure exactly one primary key"""
        primary_keys = [f for f in v if f.primary]
        if len(primary_keys) != 1:
            raise ValueError("Entity must have exactly one primary key field")
        return v


class EndpointModel(BaseModel):
    """API endpoint definition"""
    path: str = Field(..., pattern=r'^/.*')
    method: HttpMethod
    handler: str
    request_body: Optional[str] = None  # Entity name or inline schema
    response_body: Optional[str] = None
    query_params: List[str] = []
    path_params: List[str] = []
    description: Optional[str] = None
    authenticated: bool = False


class ModuleModel(BaseModel):
    """Module/Domain definition (max nesting: 4 levels)"""
    name: str = Field(..., min_length=1, max_length=100)
    entities: List[EntityModel] = []
    endpoints: List[EndpointModel] = []
    submodules: List["ModuleModel"] = []
    description: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_module_name(cls, v: str) -> str:
        """Validate module name (lowercase, snake_case)"""
        if not v.replace('_', '').islower():
            raise ValueError(f"Module name should be lowercase: {v}")
        if not v.replace('_', '').isalnum():
            raise ValueError(f"Module name must be alphanumeric: {v}")
        return v

    def get_nesting_depth(self) -> int:
        """Calculate nesting depth"""
        if not self.submodules:
            return 1
        return 1 + max(sub.get_nesting_depth() for sub in self.submodules)


class ProjectModel(BaseModel):
    """Project metadata"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    version: str = "1.0.0"
    base_package: Optional[str] = None  # For Java: com.example
    port: int = Field(default=8080, ge=1000, le=65535)


class MetadataModel(BaseModel):
    """Optional metadata for debugging/tracking"""
    author: Optional[str] = None
    created_at: Optional[str] = None
    tags: List[str] = []
    custom: Dict[str, Any] = {}


class SpecModel(BaseModel):
    """Main specification model"""
    spec_version: str = Field(..., alias="specVersion", pattern=r'^\d+\.\d+\.\d+$')
    project: ProjectModel
    modules: List[ModuleModel] = Field(..., min_length=1)
    decomposition_policy: DecompositionPolicy = Field(
        default=DecompositionPolicy.DISABLED,
        alias="decompositionPolicy"
    )
    metadata: Optional[MetadataModel] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator('spec_version')
    @classmethod
    def validate_spec_version(cls, v: str) -> str:
        """Validate spec version (semver)"""
        parts = v.split('.')
        major = int(parts[0])
        if major != 1:
            raise ValueError(f"Only spec version 1.x.x supported, got: {v}")
        return v

    @field_validator('modules')
    @classmethod
    def validate_nesting_depth(cls, v: List[ModuleModel]) -> List[ModuleModel]:
        """Validate max nesting depth (4 levels)"""
        for module in v:
            depth = module.get_nesting_depth()
            if depth > 4:
                raise ValueError(
                    f"Module '{module.name}' exceeds max nesting depth (4): {depth}"
                )
        return v


# Allow forward references for recursive models
ModuleModel.model_rebuild()
