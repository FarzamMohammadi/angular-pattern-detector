from typing import Dict, Any, List
import re
from dataclasses import dataclass


@dataclass
class UIPattern:
    name: str
    frequency: int
    variations: List[str]
    components: List[str]
    template_structure: str


class ComponentExtractor:
    def __init__(self):
        self.patterns = {}
        self.structural_patterns = {
            'list': r'\*ngFor\s*=\s*"[^"]*"',
            'conditional': r'\*ngIf\s*=\s*"[^"]*"',
            'form': r'<form[^>]*>.*?</form>',
            'input': r'<input[^>]*>',
            'button': r'<button[^>]*>.*?</button>',
        }

    def extract_patterns(self, component_data: Dict[str, Any]) -> List[UIPattern]:
        """
        Extracts UI patterns from a parsed component
        """
        patterns = []
        template = component_data.get('template', '')

        if not template:
            return patterns

        # Extract structural patterns
        for pattern_name, pattern_regex in self.structural_patterns.items():
            matches = re.finditer(pattern_regex, template, re.DOTALL)
            variations = [match.group(0) for match in matches]

            if variations:
                pattern = UIPattern(
                    name=pattern_name,
                    frequency=len(variations),
                    variations=variations,
                    components=[component_data.get('class_name', 'Unknown')],
                    template_structure=self._extract_template_structure(variations[0]),
                )
                patterns.append(pattern)

        # Extract component composition patterns
        composition_patterns = self._extract_composition_patterns(template)
        patterns.extend(composition_patterns)

        return patterns

    def _extract_template_structure(self, template_fragment: str) -> str:
        """
        Extracts the basic structure of a template fragment
        """
        # Remove attributes but keep structural directives
        structure = re.sub(r'\s+(?![\*ngIf|\*ngFor])[a-zA-Z0-9-]+="[^"]*"', '', template_fragment)
        # Remove content but keep element structure
        structure = re.sub(r'>([^<]+)<', '><', structure)
        return structure

    def _extract_composition_patterns(self, template: str) -> List[UIPattern]:
        """
        Extracts patterns related to component composition
        """
        patterns = []

        # Find custom components (elements with dash in name)
        custom_components = re.finditer(r'<([a-z]+-[a-z-]+)[^>]*>', template)

        component_usage = {}
        for match in custom_components:
            component_name = match.group(1)
            component_usage[component_name] = component_usage.get(component_name, 0) + 1

        for component_name, frequency in component_usage.items():
            pattern = UIPattern(
                name=f"component-usage-{component_name}",
                frequency=frequency,
                variations=[],
                components=[component_name],
                template_structure=f"<{component_name}></{component_name}>",
            )
            patterns.append(pattern)

        return patterns

    def analyze_pattern_relationships(self, patterns: List[UIPattern]) -> Dict[str, List[str]]:
        """
        Analyzes relationships between different patterns
        """
        relationships = {}

        for pattern in patterns:
            related_patterns = []
            for other_pattern in patterns:
                if pattern != other_pattern and self._are_patterns_related(pattern, other_pattern):
                    related_patterns.append(other_pattern.name)

            if related_patterns:
                relationships[pattern.name] = related_patterns

        return relationships

    def _are_patterns_related(self, pattern1: UIPattern, pattern2: UIPattern) -> bool:
        """
        Determines if two patterns are related based on their structure and usage
        """
        # Check if patterns are used together in the same components
        common_components = set(pattern1.components) & set(pattern2.components)
        if common_components:
            return True

        # Check if one pattern's structure contains the other
        return (
            pattern1.template_structure in pattern2.template_structure
            or pattern2.template_structure in pattern1.template_structure
        )
