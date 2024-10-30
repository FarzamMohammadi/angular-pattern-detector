from typing import Dict, Any
from .cli_reporter import CLIReporter
from .json_exporter import JSONExporter
from pathlib import Path

class ReportGenerator:
    def __init__(self, output_format: str = 'both', export_path: Path = None):
        self.output_format = output_format
        self.cli_reporter = CLIReporter()
        self.json_exporter = JSONExporter(export_path or Path('./pattern-report.json'))

    def generate_report(self, analysis_results: Dict[str, Any]):
        """
        Generates reports based on the specified output format
        """
        if self.output_format in ['cli', 'both']:
            self.cli_reporter.generate_report(analysis_results)
        
        if self.output_format in ['json', 'both']:
            self.json_exporter.export_report(analysis_results)
