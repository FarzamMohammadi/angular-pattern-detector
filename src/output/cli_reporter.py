from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class CLIReporter:
    def __init__(self):
        self.console = Console()

    def generate_report(self, analysis_results: Dict[str, Any]):
        """
        Generates a CLI-based report of the analysis results
        """
        self._print_header()
        self._print_summary(analysis_results['summary'])
        self._print_pattern_details(analysis_results['patterns'])
        self._print_recommendations(analysis_results['recommendations'])

    def _print_header(self):
        self.console.print("\n[bold blue]Angular UI Pattern Analysis Report[/bold blue]\n")

    def _print_summary(self, summary: Dict[str, Any]):
        panel = Panel.fit(
            f"Total Patterns: {summary['total_patterns_detected']}\n"
            f"Unique Pattern Types: {summary['unique_pattern_types']}\n",
            title="Summary",
            border_style="blue",
        )
        self.console.print(panel)

        # Print most common patterns
        table = Table(title="Most Common Patterns")
        table.add_column("Pattern", style="cyan")
        table.add_column("Frequency", justify="right")
        table.add_column("Component Coverage", justify="right")

        for pattern in summary['most_common_patterns']:
            table.add_row(pattern['name'], str(pattern['frequency']), str(pattern['components']))

        self.console.print(table)

    def _print_pattern_details(self, patterns: Dict[str, Any]):
        self.console.print("\n[bold]Pattern Details[/bold]")

        for name, details in patterns.items():
            panel = Panel.fit(
                f"Usage: {details['total_usage']}\n"
                f"Component Coverage: {details['component_coverage']}\n"
                f"Complexity Score: {details['complexity_score']:.2f}\n"
                f"Variations: {len(details['variations'])}",
                title=name,
                border_style="cyan",
            )
            self.console.print(panel)

    def _print_recommendations(self, recommendations: List[Dict[str, Any]]):
        if not recommendations:
            return

        self.console.print("\n[bold red]Recommendations[/bold red]")
        for rec in recommendations:
            self.console.print(
                f"[yellow]• {rec['pattern']}:[/yellow] {rec['message']}\n"
                f"  [green]Suggestion:[/green] {rec['suggestion']}"
            )
