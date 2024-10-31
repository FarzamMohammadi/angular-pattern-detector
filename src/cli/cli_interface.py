import argparse
from pathlib import Path
from .path_handler import PathHandler


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
            '--output', type=str, choices=['json', 'cli', 'both'], default='both', help='Output format (default: both)'
        )

        parser.add_argument('--export-path', type=str, help='Path for JSON export (default: ./pattern-report.json)')

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
