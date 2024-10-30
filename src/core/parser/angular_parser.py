from pathlib import Path
from typing import Dict, Any
import re

class AngularParser:
    def __init__(self):
        self.component_metadata_pattern = re.compile(r'@Component\s*\(\s*{([^}]+)}\s*\)')
        self.class_pattern = re.compile(r'export\s+class\s+(\w+)')

    def parse_component(self, component_files: Dict[str, Path]) -> Dict[str, Any]:
        """
        Parses an Angular component and its related files
        """
        result = {
            'metadata': {},
            'template': '',
            'styles': [],
            'class_name': '',
            'properties': [],
            'methods': []
        }

        # Parse TypeScript file
        if component_files['typescript']:
            ts_content = component_files['typescript'].read_text()
            result.update(self._parse_typescript(ts_content))

        # Parse template
        if component_files['template']:
            result['template'] = component_files['template'].read_text()

        # Parse styles
        for style_file in component_files['styles']:
            result['styles'].append(style_file.read_text())

        return result

    def _parse_typescript(self, content: str) -> Dict[str, Any]:
        """
        Parses TypeScript content to extract component information
        """
        result = {
            'metadata': {},
            'class_name': '',
            'properties': [],
            'methods': []
        }

        # Extract component metadata
        metadata_match = self.component_metadata_pattern.search(content)
        if metadata_match:
            metadata_str = metadata_match.group(1)
            result['metadata'] = self._parse_metadata(metadata_str)

        # Extract class name
        class_match = self.class_pattern.search(content)
        if class_match:
            result['class_name'] = class_match.group(1)

        # Extract properties and methods (basic implementation)
        result['properties'] = self._extract_properties(content)
        result['methods'] = self._extract_methods(content)

        return result

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        """
        Parses component metadata string into a dictionary
        """
        metadata = {}
        # Basic parsing of selector, templateUrl, and styleUrls
        selector_match = re.search(r'selector\s*:\s*[\'"]([^\'"]+)[\'"]', metadata_str)
        if selector_match:
            metadata['selector'] = selector_match.group(1)

        template_match = re.search(r'templateUrl\s*:\s*[\'"]([^\'"]+)[\'"]', metadata_str)
        if template_match:
            metadata['templateUrl'] = template_match.group(1)

        return metadata

    def _extract_properties(self, content: str) -> list:
        """
        Extracts component properties
        """
        # Basic property extraction (can be enhanced)
        property_pattern = re.compile(r'@Input\(\)\s+(\w+)')
        return property_pattern.findall(content)

    def _extract_methods(self, content: str) -> list:
        """
        Extracts component methods
        """
        # Basic method extraction (can be enhanced)
        method_pattern = re.compile(r'(\w+)\s*\([^)]*\)\s*{')
        return method_pattern.findall(content)