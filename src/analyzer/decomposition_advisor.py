"""
Decomposition advisor for microservice analysis.
Deterministic scoring, no AI inference.
"""

from typing import Dict, List
from src.models import SpecModel, ModuleModel, DecompositionPolicy


class DecompositionReport:
    """Decomposition analysis report"""
    
    def __init__(self, spec: SpecModel):
        self.policy = spec.decomposition_policy
        self.complexity_score = 0
        self.recommendation = "modular-monolith"
        self.reasoning: List[str] = []
        self.candidates: List[Dict] = []
        self.metrics: Dict = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "policy": self.policy.value,
            "complexity_score": self.complexity_score,
            "recommendation": self.recommendation,
            "reasoning": self.reasoning,
            "candidates": self.candidates,
            "metrics": self.metrics
        }


class DecompositionAdvisor:
    """
    Analyze spec for microservice decomposition opportunities.
    Deterministic scoring based on metrics.
    """
    
    @staticmethod
    def analyze(spec: SpecModel) -> DecompositionReport:
        """Analyze spec and generate report"""
        report = DecompositionReport(spec)
        
        if spec.decomposition_policy == DecompositionPolicy.DISABLED:
            report.reasoning.append("Decomposition policy is disabled")
            return report
        
        # Calculate metrics
        metrics = DecompositionAdvisor._calculate_metrics(spec)
        report.metrics = metrics
        
        # Calculate complexity score (0-100)
        score = DecompositionAdvisor._calculate_complexity_score(metrics)
        report.complexity_score = score
        
        # Generate recommendation
        if score < 30:
            report.recommendation = "modular-monolith"
            report.reasoning.append(
                f"Low complexity score ({score}) - modular monolith is optimal"
            )
            report.reasoning.append(
                "Benefits: Simple deployment, easier debugging, lower overhead"
            )
        elif score < 60:
            report.recommendation = "modular-monolith-with-options"
            report.reasoning.append(
                f"Medium complexity score ({score}) - stay with modular monolith"
            )
            report.reasoning.append(
                "Consider microservices only if: scaling needs differ, "
                "team structure requires it, or bounded contexts are very clear"
            )
            # Identify potential candidates
            report.candidates = DecompositionAdvisor._identify_candidates(spec)
        else:
            report.recommendation = "microservices-consideration"
            report.reasoning.append(
                f"High complexity score ({score}) - microservices may be beneficial"
            )
            report.reasoning.append(
                "Indicators: Multiple bounded contexts, different scaling needs, "
                "large team structure"
            )
            report.candidates = DecompositionAdvisor._identify_candidates(spec)
        
        return report
    
    @staticmethod
    def _calculate_metrics(spec: SpecModel) -> Dict:
        """Calculate various complexity metrics"""
        metrics = {
            "total_modules": 0,
            "total_entities": 0,
            "total_endpoints": 0,
            "max_nesting_depth": 0,
            "avg_entities_per_module": 0,
            "avg_endpoints_per_module": 0,
            "cross_module_dependencies": 0,
        }
        
        all_modules = []
        DecompositionAdvisor._collect_all_modules(spec.modules, all_modules)
        
        metrics["total_modules"] = len(all_modules)
        
        for module in all_modules:
            metrics["total_entities"] += len(module.entities)
            metrics["total_endpoints"] += len(module.endpoints)
            depth = module.get_nesting_depth()
            metrics["max_nesting_depth"] = max(metrics["max_nesting_depth"], depth)
        
        if metrics["total_modules"] > 0:
            metrics["avg_entities_per_module"] = \
                metrics["total_entities"] / metrics["total_modules"]
            metrics["avg_endpoints_per_module"] = \
                metrics["total_endpoints"] / metrics["total_modules"]
        
        return metrics
    
    @staticmethod
    def _calculate_complexity_score(metrics: Dict) -> int:
        """
        Calculate complexity score (0-100).
        Higher score = more complex = more likely to benefit from microservices.
        """
        score = 0
        
        # Module count (0-20 points)
        module_count = metrics["total_modules"]
        if module_count > 10:
            score += 20
        elif module_count > 5:
            score += 15
        elif module_count > 2:
            score += 10
        else:
            score += 5
        
        # Entity count (0-20 points)
        entity_count = metrics["total_entities"]
        if entity_count > 50:
            score += 20
        elif entity_count > 30:
            score += 15
        elif entity_count > 15:
            score += 10
        else:
            score += 5
        
        # Endpoint count (0-20 points)
        endpoint_count = metrics["total_endpoints"]
        if endpoint_count > 100:
            score += 20
        elif endpoint_count > 50:
            score += 15
        elif endpoint_count > 25:
            score += 10
        else:
            score += 5
        
        # Nesting depth (0-20 points)
        max_depth = metrics["max_nesting_depth"]
        if max_depth >= 4:
            score += 20
        elif max_depth >= 3:
            score += 15
        elif max_depth >= 2:
            score += 10
        else:
            score += 5
        
        # Entities per module (0-20 points)
        avg_entities = metrics["avg_entities_per_module"]
        if avg_entities > 10:
            score += 20
        elif avg_entities > 7:
            score += 15
        elif avg_entities > 4:
            score += 10
        else:
            score += 5
        
        return min(score, 100)
    
    @staticmethod
    def _identify_candidates(spec: SpecModel) -> List[Dict]:
        """Identify potential microservice candidates"""
        candidates = []
        
        all_modules = []
        DecompositionAdvisor._collect_all_modules(spec.modules, all_modules)
        
        for module in all_modules:
            # Criteria for good candidate:
            # 1. Has sufficient entities (>3)
            # 2. Has sufficient endpoints (>5)
            # 3. Low expected cross-module dependencies
            
            entity_count = len(module.entities)
            endpoint_count = len(module.endpoints)
            
            if entity_count >= 3 and endpoint_count >= 5:
                candidates.append({
                    "module_name": module.name,
                    "entity_count": entity_count,
                    "endpoint_count": endpoint_count,
                    "rationale": f"Self-contained domain with {entity_count} entities "
                                f"and {endpoint_count} endpoints"
                })
        
        return candidates
    
    @staticmethod
    def _collect_all_modules(modules: List[ModuleModel], result: List[ModuleModel]):
        """Recursively collect all modules"""
        for module in modules:
            result.append(module)
            DecompositionAdvisor._collect_all_modules(module.submodules, result)
