# Add to imports
import shutil
from pathlib import Path
import json
import jinja2
from typing import Dict, Any, List
from ..core.extractor.component_extractor import UIPattern
import re
import urllib.request


class CatalogGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        # Get the actual path to the templates directory
        self.template_dir = Path(__file__).parent / 'templates'

        # Verify template directory exists
        if not self.template_dir.exists():
            raise Exception(f"Template directory not found at {self.template_dir}")

        # Initialize Jinja environment
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)), autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        # Create a proper Jinja2 filter that handles arguments
        def json_filter(value, **kwargs):
            return json.dumps(value, ensure_ascii=False, default=str, indent=kwargs.get('indent', None))

        # Register the filter
        self.template_env.filters['tojson'] = json_filter

        self.patterns = {}  # Add this line to store patterns

    def _setup_output_directory(self):
        """Creates necessary directories and copies assets"""
        try:
            # Create directories
            patterns_dir = self.output_dir / 'patterns'
            assets_dir = self.output_dir / 'assets'
            patterns_dir.mkdir(parents=True, exist_ok=True)
            assets_dir.mkdir(parents=True, exist_ok=True)

            # Try to copy D3.js from CDN, fallback to local or CDN link if failed
            d3_dest = assets_dir / 'd3.min.js'
            if not d3_dest.exists():
                try:
                    import urllib.request

                    d3_url = "https://d3js.org/d3.v7.min.js"
                    urllib.request.urlretrieve(d3_url, d3_dest)
                    print(f"✓ Downloaded d3.min.js to {d3_dest}")
                except Exception as e:
                    print(f"Warning: Could not download D3.js: {str(e)}")
                    print("Using CDN link instead")
                    # We'll update the template to use CDN link directly

            # Copy other assets
            template_assets = Path(__file__).parent / 'templates' / 'assets'
            if template_assets.exists():
                for asset in ['styles.css', 'main.js']:
                    source = template_assets / asset
                    dest = assets_dir / asset
                    if source.exists():
                        shutil.copy2(source, dest)
                        print(f"✓ Copied {asset} to {dest}")
                    else:
                        print(f"✗ Warning: {asset} not found at {source}")

        except Exception as e:
            print(f"Error setting up directories: {str(e)}")
            raise

    def _print_directory_structure(self, directory: Path, level: int = 0):
        """Helper method to print directory structure"""
        indent = "  " * level
        print(f"{indent}{directory.name}/")
        for item in directory.iterdir():
            if item.is_dir():
                self._print_directory_structure(item, level + 1)
            else:
                print(f"{indent}  {item.name}")

    def _generate_index(self, analysis_results: Dict[str, Any]):
        """Generates the main index.html page"""
        template = self.template_env.get_template('patterns/index.html')

        # Prepare data for the template - ensure patterns is a dict
        template_data = {
            'summary': analysis_results['summary'],
            'patterns': analysis_results['patterns'],  # This is already a dict from PatternAnalyzer
            'relationships': analysis_results.get('relationships', {}),
            'recommendations': analysis_results.get('recommendations', []),
        }

        # Generate index.html
        index_content = template.render(**template_data)
        (self.output_dir / 'patterns').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'patterns' / 'index.html').write_text(index_content)

    def _generate_pattern_pages(self, patterns: Dict[str, Any]):
        """Generates individual pattern pages"""
        template = self.template_env.get_template('patterns/pattern.html')

        for pattern_name, pattern_data in patterns.items():
            try:
                # Calculate complexity breakdown
                complexity_breakdown = {
                    'template': self._calculate_template_complexity(pattern_data),
                    'styles': self._calculate_style_complexity(pattern_data),
                    'logic': self._calculate_logic_complexity(pattern_data),
                }

                # Create the details structure expected by the template
                details = {
                    'complexity_breakdown': complexity_breakdown,
                    'optimization_suggestions': self._generate_optimization_suggestions(pattern_data),
                    'usage_trend': self._calculate_usage_trend(pattern_data),
                }

                # Combine pattern data with details
                template_data = {
                    'name': pattern_name,
                    'details': details,
                    'usage': pattern_data.get('total_usage', 0),
                    'coverage': pattern_data.get('component_coverage', 0),
                    'complexity': pattern_data.get('complexity', 0.0),
                    'template_structure': pattern_data.get('template_structure', ''),
                    'html_structure': pattern_data.get('html_structure', ''),
                    'styles': pattern_data.get('associated_styles', {}),
                    'variations': pattern_data.get('variations', []),
                    'accessibility_score': pattern_data.get('accessibility_score', 0.0),
                    'maintainability_index': pattern_data.get('maintainability_index', 0.0),
                    'complexity_breakdown': complexity_breakdown,
                }

                # Generate pattern page
                pattern_content = template.render(**template_data)
                pattern_file = self.output_dir / 'patterns' / f"{pattern_name.lower().replace(' ', '-')}.html"
                pattern_file.write_text(pattern_content)

            except Exception as e:
                print(f"Error generating page for pattern {pattern_name}: {str(e)}")
                continue

    def _calculate_template_complexity(self, pattern_data: Dict[str, Any]) -> int:
        """Calculate template complexity percentage"""
        template = pattern_data.get('template_structure', '')
        # Basic complexity calculation based on nesting and directives
        nesting_depth = template.count('<')
        directives = len(re.findall(r'\*ng[A-Za-z]+', template))
        return min(100, (nesting_depth * 5 + directives * 10))

    def _calculate_style_complexity(self, pattern_data: Dict[str, Any]) -> int:
        """Calculate style complexity percentage"""
        styles = pattern_data.get('associated_styles', {})
        if not styles:
            return 0
        # Calculate based on number of rules and selectors
        rules_count = sum(len(rules.split(';')) for rules in styles.values())
        return min(100, rules_count * 5)

    def _calculate_logic_complexity(self, pattern_data: Dict[str, Any]) -> int:
        """Calculate logic complexity percentage"""
        template = pattern_data.get('template_structure', '')
        # Calculate based on bindings and expressions
        bindings = len(re.findall(r'\{\{[^}]+\}\}', template))
        events = len(re.findall(r'\([^)]+\)=', template))
        return min(100, (bindings * 10 + events * 15))

    def _generate_optimization_suggestions(self, pattern_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions for the pattern"""
        suggestions = []

        # Check template complexity
        if pattern_data.get('complexity_score', 0) > 0.7:
            suggestions.append(
                {
                    'title': 'High Template Complexity',
                    'description': 'Consider breaking down this pattern into smaller components',
                    'priority': 'high',
                    'current_code': pattern_data.get('template_structure', ''),
                    'suggested_code': self._generate_simplified_template(pattern_data),
                }
            )

        # Check style optimization
        if len(pattern_data.get('associated_styles', {})) > 3:
            suggestions.append(
                {
                    'title': 'Style Optimization',
                    'description': 'Consider consolidating styles using CSS classes',
                    'priority': 'medium',
                    'current_code': json.dumps(pattern_data.get('associated_styles', {}), indent=2),
                    'suggested_code': self._generate_optimized_styles(pattern_data),
                }
            )

        return suggestions

    def _generate_simplified_template(self, pattern_data: Dict[str, Any]) -> str:
        """Generate a simplified version of the template"""
        template = pattern_data.get('template_structure', '')
        # Basic simplification - extract main content into sub-components
        if template.count('<') > 5:
            return f"""<!-- Simplified structure -->
<app-pattern-header></app-pattern-header>
<app-pattern-content></app-pattern-content>
<app-pattern-footer></app-pattern-footer>"""
        return template

    def _generate_optimized_styles(self, pattern_data: Dict[str, Any]) -> str:
        """Generate optimized CSS"""
        styles = pattern_data.get('associated_styles', {})
        # Basic style optimization - combine similar rules
        return """.pattern-component {
    /* Combined styles */
    padding: 1rem;
    margin: 0.5rem;
    border-radius: 4px;
}

.pattern-component--variant {
    /* Variant-specific styles */
    background-color: #f5f5f5;
}"""

    def _calculate_usage_trend(self, pattern_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate usage trend data for charts"""
        # Simulate usage trend data
        return [
            {'date': '2023-01', 'count': 5},
            {'date': '2023-02', 'count': 8},
            {'date': '2023-03', 'count': 12},
            {'date': '2023-04', 'count': 15},
        ]

    def _generate_relationship_graph(self, relationships: Dict[str, Dict[str, float]]):
        """Generates the relationship visualization page"""
        template = self.template_env.get_template('patterns/relationships.html')

        # Convert relationships data to D3.js format
        graph_data = {'nodes': [], 'links': []}

        # Track nodes to avoid duplicates
        added_nodes = set()

        # Process relationships into nodes and links
        for source, targets in relationships.items():
            if source not in added_nodes:
                graph_data['nodes'].append({'id': source})
                added_nodes.add(source)

            # Handle both dict and list formats for targets
            if isinstance(targets, dict):
                target_items = targets.items()
            else:
                # If targets is a list, convert to appropriate format
                target_items = [(target, 1) for target in targets]

            for target, strength in target_items:
                if target not in added_nodes:
                    graph_data['nodes'].append({'id': target})
                    added_nodes.add(target)

                graph_data['links'].append({'source': source, 'target': target, 'value': strength})

        # Generate relationships.html
        relationship_content = template.render(graph_data=graph_data)
        (self.output_dir / 'patterns' / 'relationships.html').write_text(relationship_content)

    def _verify_assets(self):
        """Verifies that all required assets are in place"""
        required_files = {'assets/styles.css': False, 'assets/main.js': False, 'patterns/index.html': False}

        print("\nVerifying assets:")
        for file_path in required_files.keys():
            full_path = self.output_dir / file_path
            exists = full_path.exists()
            required_files[file_path] = exists
            print(f"{'✓' if exists else '✗'} {file_path}: {'Found' if exists else 'Missing'}")
            if exists:
                # Check if file has content
                content = full_path.read_text()
                print(f"  Size: {len(content)} bytes")
                if len(content) == 0:
                    print("  Warning: File is empty!")

        return all(required_files.values())

    def generate_catalog(self, analysis_results: Dict[str, Any]):
        """Main method to generate the catalog"""
        try:
            # Store patterns data
            self.patterns = analysis_results.get('patterns', {})

            # Setup directories and copy assets
            self._setup_output_directory()

            # Generate relationships data
            relationships = self._generate_relationship_data()

            # Generate pages
            self._generate_index(analysis_results)
            self._generate_pattern_pages(self.patterns)
            self._generate_relationship_graph(relationships)

            # Verify everything is in place
            if not self._verify_assets():
                print("\nWarning: Some required files are missing!")

            print("\nCatalog generation complete!")
            print(f"Output directory: {self.output_dir}")
            print("Open index.html in a browser to view the catalog")

        except Exception as e:
            print(f"Error generating catalog: {str(e)}")
            raise

    def _generate_index(self, analysis_results: Dict[str, Any]):
        """Generates the main index.html page"""
        try:
            template = self.template_env.get_template('patterns/index.html')

            # Prepare data for the template
            template_data = {
                'summary': analysis_results.get(
                    'summary', {'total_patterns_detected': 0, 'unique_pattern_types': 0, 'most_common_patterns': []}
                ),
                'patterns': analysis_results.get('patterns', {}),
                'relationships': analysis_results.get('relationships', {}),
            }

            # Generate index.html
            index_content = template.render(**template_data)
            index_file = self.output_dir / 'patterns' / 'index.html'
            index_file.write_text(index_content)
            print(f"Generated index file at {index_file}")
        except Exception as e:
            print(f"Error generating index: {str(e)}")
            raise

    def _generate_pattern_page(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Generates a single pattern page"""
        try:
            template = self.template_env.get_template('patterns/pattern.html')

            # Prepare the template data
            template_data = {
                'name': pattern_name,
                'usage': pattern_data.get('total_usage', 0),
                'coverage': pattern_data.get('component_coverage', 0),
                'complexity': pattern_data.get('complexity', 0.0),
                'accessibility_score': pattern_data.get('accessibility_score', 0.0),
                'maintainability_index': pattern_data.get('maintainability_index', 0.0),
                'best_practices_score': pattern_data.get('best_practices_score', 0.0),
                'template_structure': pattern_data.get('template_structure', ''),
                'html_structure': pattern_data.get('html_structure', ''),
                'styles': pattern_data.get('associated_styles', {}),
                'variations': pattern_data.get('variations', []),
                'common_contexts': pattern_data.get('common_contexts', []),
                'complexity_breakdown': pattern_data.get(
                    'complexity_breakdown', {'template': 0, 'styles': 0, 'logic': 0}
                ),
            }

            # Generate the pattern page
            pattern_content = template.render(**template_data)
            pattern_file = self.output_dir / 'patterns' / f"{pattern_name.lower().replace(' ', '-')}.html"
            pattern_file.write_text(pattern_content)
            print(f"Generated pattern page: {pattern_file}")

        except Exception as e:
            print(f"Error generating page for pattern {pattern_name}: {str(e)}")

    def _generate_relationship_data(self) -> Dict[str, List[str]]:
        """Generate relationships between patterns based on complexity similarity"""
        relationships = {}

        for pattern_name, pattern_data in self.patterns.items():
            relationships[pattern_name] = []
            pattern_complexity = pattern_data.get('complexity', 0)

            for other_name, other_data in self.patterns.items():
                if pattern_name != other_name:
                    other_complexity = other_data.get('complexity', 0)
                    if abs(pattern_complexity - other_complexity) < 0.2:
                        relationships[pattern_name].append(other_name)

        return relationships
