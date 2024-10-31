from typing import Dict, Any, List
import re
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from functools import lru_cache
from pathlib import Path


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
        # Precompile regular expressions
        self.compiled_patterns = {
            name: re.compile(pattern, re.DOTALL) for name, pattern in self.structural_patterns.items()
        }

    def extract_patterns(self, component_data: Dict[str, Any]) -> List[UIPattern]:
        """Extracts UI patterns from a parsed component using chunking"""
        patterns = []
        template = component_data.get('template', '')
        class_name = component_data.get('class_name', 'Unknown')

        if not template:
            return patterns

        # Process template in chunks
        chunk_size = 5000
        chunks = [template[i : i + chunk_size] for i in range(0, len(template), chunk_size)]

        for chunk in chunks:
            chunk_patterns = self._extract_chunk_patterns(chunk, class_name)
            patterns.extend(chunk_patterns)

        # Process styles in bulk after pattern detection
        if patterns:
            styles = component_data.get('styles', [])
            self._bulk_process_styles(patterns, styles)

        return patterns

    @lru_cache(maxsize=500)
    def _extract_chunk_patterns(self, template_chunk: str, component_class_name: str = "Unknown") -> List[UIPattern]:
        """Cached pattern extraction for template chunks"""
        patterns = []
        for pattern_name, compiled_regex in self.compiled_patterns.items():
            matches = compiled_regex.finditer(template_chunk)
            for match in matches:
                pattern_html = match.group(0)

                # Create pattern with minimal processing
                pattern = UIPattern(
                    name=pattern_name,
                    frequency=1,
                    variations=tuple([pattern_html]),
                    components=tuple([component_class_name]),
                    template_structure=pattern_html,  # Defer complex processing
                    html_structure=pattern_html,
                    associated_styles={},
                    isolated_template='',  # Defer template isolation
                    selector_path='',  # Defer selector extraction
                )
                patterns.append(pattern)
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

    def validate_project_path(self, path: Path) -> bool:
        """Validates if the given path contains Angular components."""
        if not path.exists():
            return False

        # For sample projects, just check if we have component files
        component_files = list(path.rglob("*.component.ts"))
        return len(component_files) > 0

    def find_component_files(self, base_path: Path) -> List[Path]:
        """Finds all Angular component files"""
        # First, get all TypeScript files
        all_ts_files = list(base_path.rglob("*.component.ts"))
        if not all_ts_files:
            print(f"No .component.ts files found in {base_path}")
            return []

        print(f"Found {len(all_ts_files)} potential component files")

        component_files = []
        for file_path in all_ts_files:
            if self._is_valid_component(file_path):
                component_files.append(file_path)
                print(f"Valid component found: {file_path}")

        if not component_files:
            print("No valid Angular components found after validation")
        else:
            print(f"Found {len(component_files)} valid Angular components")

        return component_files

    def _is_valid_component(self, file_path: Path) -> bool:
        """Validates if a file is an Angular component file"""
        try:
            # Read the file content directly for small files
            content = file_path.read_text()

            # Debug output
            print(f"Validating component: {file_path}")
            has_component = '@Component' in content
            print(f"Has @Component decorator: {has_component}")

            return has_component

        except Exception as e:
            print(f"Error validating component {file_path}: {str(e)}")
            return False

    def get_related_files(self, component_file: Path) -> Dict[str, Path]:
        """Gets related template, style, and spec files for a component."""
        base_name = component_file.stem.replace('.component', '')
        parent_dir = component_file.parent

        related_files = {'typescript': component_file, 'template': None, 'styles': [], 'spec': None}

        # Find template file
        template = parent_dir / f"{base_name}.component.html"
        if template.exists():
            related_files['template'] = template

        # Find style files
        for ext in ['.scss', '.css']:
            style = parent_dir / f"{base_name}.component{ext}"
            if style.exists():
                related_files['styles'].append(style)

        # Find spec file
        spec = parent_dir / f"{base_name}.component.spec.ts"
        if spec.exists():
            related_files['spec'] = spec

        return related_files

    def _bulk_process_styles(self, patterns: List[UIPattern], styles: List[str]):
        """Process styles for all patterns at once"""
        if not styles:
            return

        # Create a mapping of selector paths to patterns
        selector_map = {}
        for pattern in patterns:
            if pattern.selector_path:
                selector_map[pattern.selector_path] = pattern

        # Process all styles at once
        for style in styles:
            for selector, pattern in selector_map.items():
                css_rules = re.findall(rf'{selector}\s*\{{([^}}]+)\}}', style)
                for rules in css_rules:
                    pattern.associated_styles[selector] = rules.strip()
