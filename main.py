from pathlib import Path
import argparse
from src.cli.cli_interface import CLIInterface
from src.cli.path_handler import PathHandler
from src.core.parser.angular_parser import AngularParser
from src.core.extractor.component_extractor import ComponentExtractor
from src.core.analyzer.pattern_analyzer import PatternAnalyzer
from src.output.report_generator import ReportGenerator
from src.output.catalog_generator import CatalogGenerator
from src.output.documentation_generator import DocumentationGenerator
from typing import List, Dict, Any
import asyncio
import re


async def process_project(project_path: Path):
    path_handler = PathHandler()
    component_files = await path_handler.find_component_files_async(project_path)

    # Process in batches
    batch_size = 100
    for i in range(0, len(component_files), batch_size):
        batch = component_files[i : i + batch_size]
        # Process batch


def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description='Angular UI Pattern Detector')
    parser.add_argument('--project-path', required=True, help='Path to Angular project')
    parser.add_argument('--output-format', choices=['cli', 'json', 'both', 'all'], default='both', help='Output format')
    parser.add_argument('--export-path', help='Path for JSON export', default='./pattern-report.json')
    parser.add_argument('--generate-catalog', action='store_true', help='Generate HTML pattern catalog')

    args = parser.parse_args()

    # Initialize components
    cli = CLIInterface()
    path_handler = PathHandler()
    parser = AngularParser()
    extractor = ComponentExtractor()
    analyzer = PatternAnalyzer()

    try:
        cli.display_progress("Analyzing Angular project...")

        # Find and parse components
        path_handler.validate_project_path(Path(args.project_path))  # Validate first
        path_handler._debug_path_search(Path(args.project_path))  # Debug output
        component_files = path_handler.find_component_files(Path(args.project_path))

        if not component_files:
            cli.display_error("No Angular components found in the project")
            return 1

        cli.display_progress(f"Found {len(component_files)} components")

        # Initialize patterns list
        patterns = []

        # Process components in batches
        batch_size = 50
        for i in range(0, len(component_files), batch_size):
            batch = component_files[i : i + batch_size]
            batch_patterns = []

            for component_file in batch:
                related_files = path_handler.get_related_files(component_file)
                component_data = parser.parse_component(related_files)
                if related_files['template']:
                    component_patterns = extractor.extract_patterns(component_data)
                    batch_patterns.extend(component_patterns)

            patterns.extend(batch_patterns)
            print(f"Processed batch {i//batch_size + 1}, found {len(batch_patterns)} patterns")

        cli.display_progress("Analyzing patterns...")
        analysis_results = analyzer.analyze_patterns(patterns)

        # Debug print
        print("\nAnalysis results:")
        print(f"Total patterns: {len(patterns)}")
        print(f"Unique pattern types: {len(analysis_results['patterns'])}")
        print(f"Pattern types found: {list(analysis_results['patterns'].keys())}")

        # Generate catalog
        if args.generate_catalog:
            cli.display_progress("Generating pattern catalog...")
            output_dir = Path('./pattern-catalog')
            catalog_generator = CatalogGenerator(output_dir=output_dir)
            catalog_generator.generate_catalog(analysis_results=analysis_results)

        # Verify the output
        output_dir = Path("output/pattern-catalog")
        if output_dir.exists():
            print("\nGenerated files:")
            for file in output_dir.rglob('*'):
                if file.is_file():
                    print(f"- {file.relative_to(output_dir)}")

        # Generate reports
        cli.display_progress("Generating reports...")
        report_generator = ReportGenerator(output_format=args.output_format, export_path=Path(args.export_path))
        report_generator.generate_report(analysis_results)

        cli.display_progress("Analysis complete!", complete=True)
        return 0

    except Exception as e:
        cli.display_error(str(e))
        return 1


if __name__ == "__main__":
    exit(main())
