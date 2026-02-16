"""
Backend code generator.
Template-driven, deterministic output.
"""

from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, Template
from src.models import SpecModel, EntityModel, ModuleModel


class BackendGenerator:
    """Generate backend code from spec"""
    
    def __init__(self, backend_type: str = "spring-boot"):
        self.backend_type = backend_type
        # Normalize backend_type for template directory (replace - with _)
        template_backend_type = backend_type.replace('-', '_')
        self.template_dir = Path(__file__).parent.parent / "templates" / template_backend_type
        
        if not self.template_dir.exists():
            raise ValueError(f"Template directory not found: {self.template_dir}")
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=False,
            lstrip_blocks=False
        )
        
        # Add custom filters
        self.env.filters['java_type'] = self._java_type_filter
        self.env.filters['python_type'] = self._python_type_filter
    
    def generate(self, spec: SpecModel, output_dir: str):
        """Generate backend code"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if self.backend_type == "spring-boot":
            self._generate_spring_boot(spec, output_path)
        elif self.backend_type == "python":
            self._generate_python(spec, output_path)
        else:
            raise ValueError(f"Unknown backend type: {self.backend_type}")
    
    def _generate_spring_boot(self, spec: SpecModel, output_path: Path):
        """Generate Spring Boot project"""
        base_package = spec.project.base_package or "com.example.project"
        package_path = base_package.replace('.', '/')
        
        # Create directory structure
        src_main = output_path / "src" / "main"
        src_main_java = src_main / "java" / package_path
        src_main_resources = src_main / "resources"
        
        src_main_java.mkdir(parents=True, exist_ok=True)
        src_main_resources.mkdir(parents=True, exist_ok=True)
        
        # Generate Application.java
        self._render_template(
            "Application.java.j2",
            src_main_java / f"{self._to_pascal_case(spec.project.name)}Application.java",
            {
                "package": base_package,
                "class_name": f"{self._to_pascal_case(spec.project.name)}Application",
                "project": spec.project
            }
        )
        
        # Generate entities, repositories, services, controllers
        all_modules = self._flatten_modules(spec.modules)
        
        for module in all_modules:
            module_dir = src_main_java / module.name
            module_dir.mkdir(exist_ok=True)
            
            for entity in module.entities:
                # Entity
                self._render_template(
                    "Entity.java.j2",
                    module_dir / f"{entity.name}.java",
                    {
                        "package": f"{base_package}.{module.name}",
                        "entity": entity,
                        "imports": self._get_java_imports(entity)
                    }
                )
                
                # Repository
                self._render_template(
                    "Repository.java.j2",
                    module_dir / f"{entity.name}Repository.java",
                    {
                        "package": f"{base_package}.{module.name}",
                        "entity": entity
                    }
                )
                
                # Service
                self._render_template(
                    "Service.java.j2",
                    module_dir / f"{entity.name}Service.java",
                    {
                        "package": f"{base_package}.{module.name}",
                        "entity": entity
                    }
                )
                
                # Controller
                self._render_template(
                    "Controller.java.j2",
                    module_dir / f"{entity.name}Controller.java",
                    {
                        "package": f"{base_package}.{module.name}",
                        "entity": entity,
                        "module": module
                    }
                )
        
        # Generate pom.xml
        self._render_template(
            "pom.xml.j2",
            output_path / "pom.xml",
            {
                "project": spec.project,
                "base_package": base_package
            }
        )
        
        # Generate application.yml
        self._render_template(
            "application.yml.j2",
            src_main_resources / "application.yml",
            {"project": spec.project}
        )
    
    def _generate_python(self, spec: SpecModel, output_path: Path):
        """Generate Python FastAPI project"""
        
        # Create directory structure
        src_dir = output_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate main.py
        self._render_template(
            "main.py.j2",
            src_dir / "main.py",
            {"project": spec.project, "modules": spec.modules}
        )
        
        # Generate models, repositories, services, routes for each module
        all_modules = self._flatten_modules(spec.modules)
        
        for module in all_modules:
            module_dir = src_dir / module.name
            module_dir.mkdir(exist_ok=True)
            
            # __init__.py
            (module_dir / "__init__.py").write_text("")
            
            # models.py
            self._render_template(
                "models.py.j2",
                module_dir / "models.py",
                {"module": module}
            )
            
            # repositories.py
            self._render_template(
                "repositories.py.j2",
                module_dir / "repositories.py",
                {"module": module}
            )
            
            # services.py
            self._render_template(
                "services.py.j2",
                module_dir / "services.py",
                {"module": module}
            )
            
            # routes.py
            self._render_template(
                "routes.py.j2",
                module_dir / "routes.py",
                {"module": module}
            )
        
        # Generate requirements.txt
        self._render_template(
            "requirements.txt.j2",
            output_path / "requirements.txt",
            {}
        )
    
    def _render_template(self, template_name: str, output_file: Path, context: Dict):
        """Render Jinja2 template to file"""
        try:
            template = self.env.get_template(template_name)
            content = template.render(**context)
            output_file.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"Warning: Failed to render {template_name}: {e}")
    
    def _flatten_modules(self, modules: List[ModuleModel]) -> List[ModuleModel]:
        """Flatten nested modules into a list"""
        result = []
        for module in modules:
            result.append(module)
            result.extend(self._flatten_modules(module.submodules))
        return result
    
    @staticmethod
    def _to_pascal_case(text: str) -> str:
        """Convert to PascalCase"""
        return ''.join(word.capitalize() for word in text.replace('-', '_').split('_'))
    
    @staticmethod
    def _get_java_imports(entity: EntityModel) -> List[str]:
        """Get required Java imports for entity"""
        imports = [
            "javax.persistence.*",
            "lombok.Data",
            "lombok.NoArgsConstructor",
            "lombok.AllArgsConstructor"
        ]
        
        # Add UUID import if needed
        if any(f.type.value == "uuid" for f in entity.fields):
            imports.append("java.util.UUID")
        
        # Add Date/Time imports if needed
        if any(f.type.value in ["datetime", "date"] for f in entity.fields):
            imports.append("java.time.LocalDateTime")
            imports.append("java.time.LocalDate")
        
        return imports
    
    @staticmethod
    def _java_type_filter(field_type: str) -> str:
        """Convert FieldType to Java type"""
        type_mapping = {
            "string": "String",
            "integer": "Integer",
            "float": "Double",
            "boolean": "Boolean",
            "uuid": "UUID",
            "datetime": "LocalDateTime",
            "date": "LocalDate",
            "json": "String",  # Store as String, parse as needed
            "text": "String",
            "enum": "String"
        }
        return type_mapping.get(field_type, "String")
    
    @staticmethod
    def _python_type_filter(field_type: str) -> str:
        """Convert FieldType to Python type annotation"""
        type_mapping = {
            "string": "str",
            "integer": "int",
            "float": "float",
            "boolean": "bool",
            "uuid": "UUID",
            "datetime": "datetime",
            "date": "date",
            "json": "dict",
            "text": "str",
            "enum": "str"
        }
        return type_mapping.get(field_type, "str")

