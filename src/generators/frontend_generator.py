"""
Frontend code generator for React + TypeScript.
Template-driven, deterministic output.
"""

from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader
from src.models import SpecModel, EntityModel, ModuleModel

class FrontendGenerator:
    """Generate React + TypeScript frontend code from spec"""
    
    def __init__(self, frontend_type: str = "react"):
        self.frontend_type = frontend_type
        self.template_dir = Path(__file__).parent.parent / "templates" / frontend_type
        
        if not self.template_dir.exists():
            raise ValueError(f"Template directory not found: {self.template_dir}")
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=False,
            lstrip_blocks=False
        )
        
        # Add custom filters (consistent with backend)
        self.env.filters['python_type'] = self._ts_type_filter
        self.env.filters['ts_type'] = self._ts_type_filter

    def generate(self, spec: SpecModel, output_dir: str):
        """Generate React + TS frontend code"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. Project structure
        src_dir = output_path / "src"
        components_dir = src_dir / "components"
        api_dir = src_dir / "api"
        pages_dir = src_dir / "pages"
        
        for d in [src_dir, components_dir, api_dir, pages_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        # 2. Base project files (package.json, tsconfig.json, etc.)
        self._generate_base_files(spec, output_path)
        
        # 3. API Client generation (authoritative source)
        self._generate_api_client(spec, api_dir)
        
        # 4. Component & Page generation for each module/entity
        all_modules = self._flatten_modules(spec.modules)
        for module in all_modules:
            for entity in module.entities:
                self._generate_entity_components(entity, components_dir)
                self._generate_entity_pages(entity, pages_dir)
        
        # 5. Main App & Layout
        self._generate_app_main(spec, src_dir)

    def _generate_base_files(self, spec: SpecModel, output_path: Path):
        """Generate common React TS boilerplate"""
        base_files = {
            "package.json.j2": "package.json",
            "tsconfig.json.j2": "tsconfig.json",
            "vite.config.ts.j2": "vite.config.ts",
            "index.html.j2": "index.html"
        }
        for tpl, out in base_files.items():
            self._render_template(tpl, output_path / out, {"project": spec.project})

    def _generate_api_client(self, spec: SpecModel, api_dir: Path):
        """Generate API client from spec (authoritative source)"""
        self._render_template(
            "api/client.ts.j2",
            api_dir / "client.ts",
            {"project": spec.project, "modules": spec.modules}
        )

    def _generate_entity_components(self, entity: EntityModel, components_dir: Path):
        """Generate CRUD components for an entity"""
        entity_dir = components_dir / entity.name
        entity_dir.mkdir(exist_ok=True)
        
        components = {
            "Form.tsx.j2": f"{entity.name}Form.tsx",
            "List.tsx.j2": f"{entity.name}List.tsx",
            "View.tsx.j2": f"{entity.name}View.tsx"
        }
        for tpl, out in components.items():
            self._render_template(f"components/entity/{tpl}", entity_dir / out, {"entity": entity})

    def _generate_entity_pages(self, entity: EntityModel, pages_dir: Path):
        """Generate pages for an entity"""
        self._render_template(
            "pages/EntityPage.tsx.j2",
            pages_dir / f"{entity.name}Page.tsx",
            {"entity": entity}
        )

    def _generate_app_main(self, spec: SpecModel, src_dir: Path):
        """Generate main App index and styles"""
        self._render_template("App.tsx.j2", src_dir / "App.tsx", {"spec": spec})
        self._render_template("main.tsx.j2", src_dir / "main.tsx", {"project": spec.project})
        self._render_template("index.css.j2", src_dir / "index.css", {})

    def _render_template(self, template_name: str, output_file: Path, context: Dict):
        """Render Jinja2 template to file"""
        try:
            template = self.env.get_template(template_name)
            content = template.render(**context)
            output_file.write_text(content, encoding='utf-8')
        except Exception as e:
            # We use warning since some templates might not exist yet during incremental development
            print(f"Warning: Failed to render {template_name}: {e}")

    def _flatten_modules(self, modules: List[ModuleModel]) -> List[ModuleModel]:
        """Flatten nested modules into a list"""
        result = []
        for module in modules:
            result.append(module)
            result.extend(self._flatten_modules(module.submodules))
        return result

    @staticmethod
    def _ts_type_filter(field_type: str) -> str:
        """Convert Internal FieldType to TypeScript type"""
        type_mapping = {
            "string": "string",
            "integer": "number",
            "float": "number",
            "boolean": "boolean",
            "uuid": "string",
            "datetime": "string",
            "date": "string",
            "json": "any",
            "text": "string",
            "enum": "string"
        }
        return type_mapping.get(field_type, "any")
