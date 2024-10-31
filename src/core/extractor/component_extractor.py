from typing import Dict, Any, List
import re
from dataclasses import dataclass, field
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class UIPattern:
    name: str
    frequency: int
    variations: tuple
    components: tuple
    template_structure: str
    html_structure: str = ''
    associated_styles: Dict[str, str] = field(default_factory=dict)
    isolated_template: str = ''
    selector_path: str = ''

    def __hash__(self):
        """Make UIPattern hashable"""
        return hash((self.name, self.template_structure, self.html_structure, self.selector_path))

    def __eq__(self, other):
        """Define equality for UIPattern"""
        if not isinstance(other, UIPattern):
            return False
        return (
            self.name == other.name
            and self.template_structure == other.template_structure
            and self.html_structure == other.html_structure
            and self.selector_path == other.selector_path
        )


class ComponentExtractor:
    def __init__(self):
        self.structural_patterns = {
            'data-list': r'\*ngFor\s*=\s*"[^"]*"',
            'conditional-content': r'\*ngIf\s*=\s*"[^"]*"',
            'form-group': r'<form[^>]*>.*?</form>',
            'input-field': r'<input[^>]*>',
            'action-button': r'<button[^>]*>.*?</button>',
            'data-binding': r'\{\{[^}]+\}\}',
            'event-binding': r'\([^)]+\)="[^"]+"',
        }

    def extract_patterns(self, component_data: Dict[str, Any]) -> List[UIPattern]:
        """Extracts UI patterns from a parsed component"""
        patterns = []
        template = component_data.get('template', '')
        styles = component_data.get('styles', [])

        if not template:
            return patterns

        print(f"Analyzing template:\n{template[:200]}...")  # Debug print

        # Extract structural patterns with visual context
        for pattern_name, pattern_regex in self.structural_patterns.items():
            matches = re.finditer(pattern_regex, template, re.DOTALL)
            for match in matches:
                pattern_html = match.group(0)
                print(f"Found pattern {pattern_name}: {pattern_html[:100]}...")  # Debug print

                isolated_template = self._isolate_template(pattern_html)
                selector_path = self._extract_selector_path(pattern_html)
                associated_styles = self._extract_associated_styles(selector_path, styles)

                pattern = UIPattern(
                    name=pattern_name,
                    frequency=1,
                    variations=tuple([pattern_html]),
                    components=tuple([component_data.get('class_name', 'Unknown')]),
                    template_structure=self._extract_template_structure(pattern_html),
                    html_structure=pattern_html,
                    associated_styles=associated_styles,
                    isolated_template=isolated_template,
                    selector_path=selector_path,
                )
                patterns.append(pattern)

        print(f"Found {len(patterns)} patterns in component")  # Debug print
        return patterns

    def _isolate_template(self, html: str) -> str:
        """Isolates a pattern template by removing external dependencies"""
        # Remove component-specific bindings
        isolated = re.sub(r'\[(\w+)\]="[^"]*"', r'\1=""', html)
        # Replace complex bindings with placeholders
        isolated = re.sub(r'\{\{[^}]+\}\}', '{{placeholder}}', isolated)
        return isolated

    def _extract_selector_path(self, html: str) -> str:
        """Extracts CSS selector path for the pattern"""
        soup = BeautifulSoup(html, 'html.parser')
        selectors = []
        for element in soup.find_all():
            classes = element.get('class', [])
            if classes:
                selectors.append(f".{'.'.join(classes)}")
        return ' '.join(selectors)

    def _extract_associated_styles(self, selector_path: str, styles: List[str]) -> Dict[str, str]:
        """Extracts styles associated with the pattern"""
        associated_styles = {}
        for style in styles:
            # Basic CSS parsing - could be enhanced with a proper CSS parser
            for selector in selector_path.split():
                css_rules = re.findall(rf'{selector}\s*\{{([^}}]+)\}}', style)
                for rules in css_rules:
                    associated_styles[selector] = rules.strip()
        return associated_styles

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
                variations=(),
                components=(component_name,),
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
