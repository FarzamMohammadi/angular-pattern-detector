from typing import List
from pathlib import Path
import argparse
from .path_handler import PathHandler
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn


class CLIInterface:
    def __init__(self):
        self.path_handler = PathHandler()
        self.parser = self._setup_argument_parser()

    def _setup_argument_parser(self) -> argparse.ArgumentParser:
        """Sets up the command line argument parser."""
        parser = argparse.ArgumentParser(
            description='Angular UI Component Pattern Detector', formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument('project_path', type=str, help='Path to the Angular project root directory')

        parser.add_argument(
            '--output',
            type=str,
            choices=['json', 'cli', 'both', 'all'],
            default='both',
            help='Output format (default: both)',
        )

        parser.add_argument('--export-path', type=str, help='Path for JSON export (default: ./pattern-report.json)')

        parser.add_argument('--generate-catalog', action='store_true', help='Generate HTML pattern catalog')

        parser.add_argument('--generate-docs', action='store_true', help='Generate developer documentation')

        return parser

    def parse_arguments(self) -> dict:
        """Parses and validates command line arguments."""
        args = self.parser.parse_args()
        project_path = Path(args.project_path).resolve()

        if not self.path_handler.validate_project_path(project_path):
            self.parser.error(f"Invalid Angular project path: {project_path}")

        return {
            'project_path': project_path,
            'output_format': args.output,
            'export_path': Path(args.export_path) if args.export_path else Path('./pattern-report.json'),
            'generate_catalog': args.generate_catalog,
            'generate_docs': args.generate_docs,
        }

    def display_progress(self, message: str, complete: bool = False):
        """Displays progress messages to the user."""
        if complete:
            print(f"✓ {message}")
        else:
            print(f"⋯ {message}")

    def display_error(self, message: str):
        """Displays error messages to the user."""
        print(f"✗ Error: {message}")

    def analyze_with_progress(self, component_files: List[Path]):
        """Analyzes components with progress reporting"""
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
        ) as progress:
            total_files = len(component_files)
            task = progress.add_task("[cyan]Analyzing patterns...", total=total_files)

            patterns = []
            for component_file in component_files:
                related_files = self.path_handler.get_related_files(component_file)
                component_data = self.parser.parse_component(related_files)
                component_patterns = self.extractor.extract_patterns(component_data)
                patterns.extend(component_patterns)
                progress.update(task, advance=1)

            return patterns
