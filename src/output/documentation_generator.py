from typing import Dict, Any
from pathlib import Path


class DocumentationGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.template_dir = Path(__file__).parent / 'templates' / 'docs'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_documentation(self, analysis_results: Dict[str, Any]):
        """Generates comprehensive documentation"""
        self._generate_overview()
        self._generate_pattern_guidelines(analysis_results['patterns'])
        self._generate_best_practices(analysis_results['profiles'])
        self._generate_migration_guide(analysis_results)
        self._generate_examples(analysis_results['patterns'])

    def _generate_overview(self):
        """Generates overview documentation"""
        content = """# UI Pattern Documentation

## Overview
This documentation provides guidelines for using UI patterns detected in your Angular application.

## Contents
1. Pattern Guidelines
2. Best Practices
3. Implementation Examples
4. Migration Guide
"""
        (self.output_dir / 'overview.md').write_text(content)

    def _generate_pattern_guidelines(self, patterns: Dict[str, Any]):
        """Generates specific guidelines for each pattern"""
        content = ["# Pattern Guidelines\n"]

        for pattern_name, pattern_data in patterns.items():
            content.append(f"## {pattern_name}\n")

            # Add practical usage guidelines
            content.append("### When to Use\n")
            content.append(self._generate_usage_guidelines(pattern_data))

            # Add best practices
            content.append("\n### Best Practices\n")
            content.append(self._generate_best_practices(pattern_data))

            # Add performance considerations
            content.append("\n### Performance Considerations\n")
            content.append(self._generate_performance_guidelines(pattern_data))

            # Add accessibility guidelines
            content.append("\n### Accessibility Guidelines\n")
            content.append(self._generate_accessibility_guidelines(pattern_data))

    def _generate_best_practices(self, profiles: Dict[str, Any]):
        """Generates best practices based on pattern profiles"""
        content = ["# Best Practices\n"]

        # General best practices
        content.append(
            """
## General Guidelines
1. Keep patterns simple and focused
2. Maintain consistent naming conventions
3. Reuse existing patterns when possible
4. Document pattern variations
"""
        )

        # Pattern-specific practices
        content.append("\n## Pattern-Specific Guidelines\n")
        for pattern_id, profile in profiles.items():
            content.append(f"\n### {pattern_id}\n")

            # Add optimization suggestions
            if profile.optimization_suggestions:
                content.append("\nOptimization Suggestions:\n")
                for suggestion in profile.optimization_suggestions:
                    content.append(f"- {suggestion['message']}")
                    content.append(f"  - Suggestion: {suggestion['suggestion']}\n")

        (self.output_dir / 'best-practices.md').write_text('\n'.join(content))

    def _generate_migration_guide(self, analysis_results: Dict[str, Any]):
        """Generates migration guidelines"""
        content = ["# Migration Guide\n"]

        content.append(
            """
## Migration Strategy
1. Identify patterns to be updated
2. Plan incremental migrations
3. Test thoroughly
4. Update documentation
"""
        )

        # Add pattern-specific migration guides
        content.append("\n## Pattern Migration Guidelines\n")
        for pattern_name, pattern_data in analysis_results['patterns'].items():
            if pattern_data.get('complexity_score', 0) > 0.7:
                content.append(f"\n### Migrating {pattern_name}\n")
                content.append("1. Current Implementation:\n")
                content.append("```html\n")
                content.append(pattern_data['template_structure'])
                content.append("\n```\n")

                content.append("\n2. Suggested Implementation:\n")
                content.append("```html\n")
                # Add simplified version if available
                content.append(pattern_data.get('suggested_structure', pattern_data['template_structure']))
                content.append("\n```\n")

        (self.output_dir / 'migration-guide.md').write_text('\n'.join(content))

    def _generate_examples(self, patterns: Dict[str, Any]):
        """Generates implementation examples"""
        content = ["# Implementation Examples\n"]

        for pattern_name, pattern_data in patterns.items():
            content.append(f"\n## {pattern_name}\n")

            # Basic implementation
            content.append("### Basic Implementation\n")
            content.append("```html\n")
            content.append(pattern_data['template_structure'])
            content.append("\n```\n")

            # With variations
            if pattern_data.get('variations'):
                content.append("\n### Variations\n")
                for i, variation in enumerate(pattern_data['variations'], 1):
                    content.append(f"\nVariation {i}:\n")
                    content.append("```html\n")
                    content.append(variation)
                    content.append("\n```\n")

        (self.output_dir / 'examples.md').write_text('\n'.join(content))

    def _generate_usage_guidelines(self, pattern_data: Dict[str, Any]) -> str:
        """Generates usage guidelines for a pattern"""
        guidelines = []

        # Add complexity-based recommendations
        complexity = pattern_data.get('complexity_score', 0)
        guidelines.append(f"Complexity Score: {complexity:.2f}\n")

        # Add usage statistics
        usage_count = pattern_data.get('total_usage', 0)
        guidelines.append(f"Usage Count: {usage_count}\n")

        # Add context-specific guidelines
        contexts = pattern_data.get('common_contexts', [])
        if contexts:
            guidelines.append("\nCommon Usage Contexts:")
            for context in contexts:
                guidelines.append(f"- {context}")

        # Add implementation example
        if pattern_data.get('template_structure'):
            guidelines.append("\n### Implementation\n")
            guidelines.append("```html\n")
            guidelines.append(pattern_data['template_structure'])
            guidelines.append("\n```")

        # Add style information if available
        if pattern_data.get('associated_styles'):
            guidelines.append("\n### Styles\n")
            guidelines.append("```scss\n")
            for selector, rules in pattern_data['associated_styles'].items():
                guidelines.append(f"\n{selector} {{\n  {rules}\n}}")
            guidelines.append("\n```")

        return '\n'.join(guidelines)

    def _generate_best_practices(self, pattern_data: Dict[str, Any]) -> str:
        """Generates best practices guidelines"""
        practices = []

        # Add maintainability recommendations
        maintainability = pattern_data.get('maintainability_index', 0)
        if maintainability < 0.5:
            practices.append("- Consider simplifying the template structure")
            practices.append("- Break down complex logic into smaller components")

        # Add accessibility recommendations
        accessibility = pattern_data.get('accessibility_score', 0)
        if accessibility < 0.7:
            practices.append("- Ensure proper ARIA attributes are used")
            practices.append("- Add meaningful labels and descriptions")

        # Add pattern-specific recommendations
        if 'form' in pattern_data.get('common_contexts', []):
            practices.append("- Use proper form validation")
            practices.append("- Include error handling")

        if 'list' in pattern_data.get('common_contexts', []):
            practices.append("- Consider pagination for large lists")
            practices.append("- Implement proper loading states")

        return '\n'.join(practices) if practices else "No specific best practices identified."

    def _generate_performance_guidelines(self, pattern_data: Dict[str, Any]) -> str:
        """Generates performance guidelines"""
        guidelines = []

        # Check template complexity
        if pattern_data.get('complexity_score', 0) > 0.7:
            guidelines.append("- High template complexity may impact rendering performance")
            guidelines.append("- Consider breaking down into smaller components")

        # Check binding usage
        if 'data-binding' in pattern_data.get('template_structure', ''):
            guidelines.append("- Use OnPush change detection strategy for better performance")
            guidelines.append("- Minimize two-way bindings")

        # Check style complexity
        if pattern_data.get('associated_styles'):
            guidelines.append("- Consider using CSS classes instead of inline styles")
            guidelines.append("- Minimize deep nesting in styles")

        return '\n'.join(guidelines) if guidelines else "No specific performance considerations identified."

    def _generate_accessibility_guidelines(self, pattern_data: Dict[str, Any]) -> str:
        """Generates accessibility guidelines"""
        guidelines = []

        # Basic accessibility checks
        if 'button' in pattern_data.get('template_structure', '').lower():
            guidelines.append("- Ensure buttons have meaningful labels")
            guidelines.append("- Add aria-label for icon-only buttons")

        if 'input' in pattern_data.get('template_structure', '').lower():
            guidelines.append("- Associate inputs with labels")
            guidelines.append("- Include proper aria-describedby for error messages")

        if 'form' in pattern_data.get('common_contexts', []):
            guidelines.append("- Implement proper form validation feedback")
            guidelines.append("- Ensure form controls are keyboard accessible")

        # Add score-based recommendations
        accessibility_score = pattern_data.get('accessibility_score', 0)
        if accessibility_score < 0.7:
            guidelines.append("\nAccessibility Improvements Needed:")
            guidelines.append("- Review WCAG guidelines for this pattern type")
            guidelines.append("- Add missing ARIA attributes")
            guidelines.append("- Ensure proper focus management")

        return '\n'.join(guidelines) if guidelines else "No specific accessibility guidelines identified."
