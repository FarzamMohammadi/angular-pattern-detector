from typing import List, Dict, Any
from collections import defaultdict
from ..extractor.component_extractor import UIPattern
import re

class PatternAnalyzer:
    def __init__(self):
        self.pattern_registry = defaultdict(list)
        self.similarity_threshold = 0.7  # Configurable similarity threshold

    def analyze_patterns(self, components_patterns: List[List[UIPattern]]) -> Dict[str, Any]:
        """
        Analyzes patterns across all components to identify trends and relationships
        """
        # Flatten and categorize patterns
        self._register_patterns(components_patterns)
        
        return {
            'summary': self._generate_summary(),
            'patterns': self._analyze_pattern_usage(),
            'relationships': self._analyze_pattern_relationships(),
            'recommendations': self._generate_recommendations()
        }

    def _register_patterns(self, components_patterns: List[List[UIPattern]]):
        """
        Registers patterns from all components for analysis
        """
        for component_patterns in components_patterns:
            for pattern in component_patterns:
                self.pattern_registry[pattern.name].append(pattern)

    def _generate_summary(self) -> Dict[str, Any]:
        """
        Generates a high-level summary of pattern usage
        """
        total_patterns = sum(len(patterns) for patterns in self.pattern_registry.values())
        most_common = sorted(
            self.pattern_registry.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]

        return {
            'total_patterns_detected': total_patterns,
            'unique_pattern_types': len(self.pattern_registry),
            'most_common_patterns': [
                {
                    'name': name,
                    'frequency': len(patterns),
                    'components': len(set().union(*[set(p.components) for p in patterns]))
                }
                for name, patterns in most_common
            ]
        }

    def _analyze_pattern_usage(self) -> Dict[str, Any]:
        """
        Analyzes detailed pattern usage and variations
        """
        pattern_analysis = {}
        
        for pattern_name, patterns in self.pattern_registry.items():
            variations = self._analyze_variations(patterns)
            components = set().union(*[set(p.components) for p in patterns])
            
            pattern_analysis[pattern_name] = {
                'total_usage': len(patterns),
                'component_coverage': len(components),
                'components': list(components),
                'variations': variations,
                'complexity_score': self._calculate_complexity_score(patterns)
            }
        
        return pattern_analysis

    def _analyze_variations(self, patterns: List[UIPattern]) -> List[Dict[str, Any]]:
        """
        Analyzes different variations of the same pattern type
        """
        variation_groups = defaultdict(list)
        
        for pattern in patterns:
            for variation in pattern.variations:
                normalized = self._normalize_structure(variation)
                variation_groups[normalized].append(variation)

        return [
            {
                'structure': key,
                'frequency': len(variations),
                'examples': variations[:3]  # Limit examples for brevity
            }
            for key, variations in variation_groups.items()
        ]

    def _analyze_pattern_relationships(self) -> Dict[str, List[str]]:
        """
        Analyzes relationships and co-occurrences between patterns
        """
        relationships = defaultdict(list)
        
        for pattern_name, patterns in self.pattern_registry.items():
            component_set = set().union(*[set(p.components) for p in patterns])
            
            for other_name, other_patterns in self.pattern_registry.items():
                if pattern_name != other_name:
                    other_components = set().union(*[set(p.components) for p in other_patterns])
                    overlap = len(component_set & other_components)
                    
                    if overlap > 0:
                        relationships[pattern_name].append({
                            'related_pattern': other_name,
                            'co_occurrence_strength': overlap / len(component_set),
                            'shared_components': list(component_set & other_components)
                        })

        return dict(relationships)

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generates recommendations based on pattern analysis
        """
        recommendations = []
        
        # Analyze pattern complexity
        for pattern_name, patterns in self.pattern_registry.items():
            complexity_score = self._calculate_complexity_score(patterns)
            if complexity_score > 0.7:  # Threshold for complexity warning
                recommendations.append({
                    'type': 'complexity_warning',
                    'pattern': pattern_name,
                    'message': f"High complexity detected in {pattern_name} pattern usage",
                    'suggestion': "Consider simplifying or breaking down into smaller components"
                })

        # Analyze pattern consistency
        for pattern_name, patterns in self.pattern_registry.items():
            if len(self._analyze_variations(patterns)) > 3:  # Threshold for variation warning
                recommendations.append({
                    'type': 'consistency_warning',
                    'pattern': pattern_name,
                    'message': f"Multiple variations of {pattern_name} pattern detected",
                    'suggestion': "Consider standardizing the implementation"
                })

        return recommendations

    def _calculate_complexity_score(self, patterns: List[UIPattern]) -> float:
        """
        Calculates a complexity score for a pattern based on its structure and usage
        """
        if not patterns:
            return 0.0

        # Factors considered for complexity:
        # 1. Depth of nesting
        # 2. Number of structural directives
        # 3. Number of variations
        
        total_score = 0
        for pattern in patterns:
            nesting_depth = pattern.template_structure.count('<')
            directive_count = len(re.findall(r'\*ng[A-Za-z]+', pattern.template_structure))
            variation_count = len(pattern.variations)
            
            pattern_score = (
                (nesting_depth * 0.4) +
                (directive_count * 0.3) +
                (variation_count * 0.3)
            ) / 10  # Normalize to 0-1 range
            
            total_score += pattern_score

        return total_score / len(patterns)

    def _normalize_structure(self, structure: str) -> str:
        """
        Normalizes a template structure for comparison
        """
        # Remove whitespace and normalize quotes
        normalized = re.sub(r'\s+', ' ', structure).strip()
        normalized = re.sub(r'[\'"]', '"', normalized)
        
        #
