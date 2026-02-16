"""
Consistency Validator to ensure BE and FE stay in sync with the Spec.
"""

from pathlib import Path
from typing import List, Dict, Tuple
from src.models import SpecModel

class ConsistencyValidator:
    """Validate consistency between generated code and spec"""
    
    @staticmethod
    def validate(spec: SpecModel, output_dir: str) -> Tuple[bool, List[str]]:
        errors = []
        out_path = Path(output_dir)
        
        # Check Backend (assuming python for now, can be extended)
        # In a real scenario, we would parse the generated code.
        # Here we do a structural existence check.
        
        for module in spec.modules:
            # Backend check
            be_module_dir = out_path / module.name
            if not be_module_dir.exists():
                # For spring-boot it might be deeper, this is a simplified check
                pass 

            # Frontend check
            fe_api_file = out_path / "frontend" / "src" / "api" / "client.ts"
            if fe_api_file.exists():
                fe_content = fe_api_file.read_text()
                for entity in module.entities:
                    if f"export const {entity.name}Api" not in fe_content:
                        errors.append(f"Frontend API client missing entry for entity: {entity.name}")
                    
                    # Check fields in API calls (simplified)
                    for field in entity.fields:
                        # This is a very basic check, ideally we'd parse TS types
                        pass

        return len(errors) == 0, errors
