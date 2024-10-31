from typing import Dict, Any
import json
from pathlib import Path
from datetime import datetime


class JSONExporter:
    def __init__(self, export_path: Path):
        self.export_path = export_path

    def export_report(self, analysis_results: Dict[str, Any]):
        """
        Exports analysis results to a JSON file
        """
        export_data = {'timestamp': datetime.now().isoformat(), 'analysis_results': analysis_results}

        with self.export_path.open('w') as f:
            json.dump(export_data, f, indent=2)
