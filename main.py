from pathlib import Path
import argparse
from src.cli.cli_interface import CLIInterface
from src.cli.path_handler import PathHandler
from src.core.parser.angular_parser import AngularParser
from src.core.extractor.component_extractor import ComponentExtractor
from src.core.analyzer.pattern_analyzer import PatternAnalyzer
from src.output.report_generator import ReportGenerator

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description='Angular UI Pattern Detector')
    parser.add_argument('--project-path', required=True, help='Path to Angular project')
    parser.add_argument('--output-format', choices=['cli', 'json', 'both'], default='both', help='Output format')
    parser.add_argument('--export-path', help='Path for JSON export', default='./pattern-report.json')
    
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
        component_files = path_handler.find_component_files(Path(args.project_path))
        if not component_files:
            cli.display_error("No Angular components found in the project")
            return 1

        cli.display_progress(f"Found {len(component_files)} components")

        # Process components
        patterns = []
        for component_file in component_files:
            related_files = path_handler.get_related_files(component_file)
            component_data = parser.parse_component(related_files)
            component_patterns = extractor.extract_patterns(component_data)
            patterns.append(component_patterns)

        cli.display_progress("Analyzing patterns...")
        
        # Analyze patterns
        analysis_results = analyzer.analyze_patterns(patterns)

        # Generate reports
        cli.display_progress("Generating reports...")
        report_generator = ReportGenerator(
            output_format=args.output_format,
            export_path=Path(args.export_path)
        )
        report_generator.generate_report(analysis_results)

        cli.display_progress("Analysis complete!", complete=True)
        return 0

    except Exception as e:
        cli.display_error(str(e))
        return 1

if __name__ == "__main__":
    exit(main())
