from pathlib import Path


class PathHandler:
    def __init__(self):
        self.angular_extensions = ['.ts', '.html', '.scss', '.css']

    def validate_project_path(self, path: Path) -> bool:
        """Validates if the given path is a valid Angular project directory."""
        if not path.exists():
            return False

        # Check for key Angular project indicators
        package_json = path / 'package.json'
        angular_json = path / 'angular.json'

        return package_json.exists() and angular_json.exists()

    def find_component_files(self, base_path: Path) -> List[Path]:
        """Finds all Angular component files in the given directory."""
        component_files = []

        if not base_path.exists():
            return component_files

        # Find all .ts files that follow Angular component naming pattern
        for file_path in base_path.rglob("*.component.ts"):
            if self._is_valid_component(file_path):
                component_files.append(file_path)

        return component_files

    def get_related_files(self, component_path: Path) -> dict:
        """Gets related template, style, and spec files for a component."""
        base_name = component_path.stem.replace('.component', '')
        parent_dir = component_path.parent

        related_files = {'typescript': component_path, 'template': None, 'styles': [], 'spec': None}

        # Find template file
        template = parent_dir / f"{base_name}.component.html"
        if template.exists():
            related_files['template'] = template

        # Find style files
        for ext in ['.scss', '.css']:
            style = parent_dir / f"{base_name}.component{ext}"
            if style.exists():
                related_files['styles'].append(style)

        # Find spec file
        spec = parent_dir / f"{base_name}.component.spec.ts"
        if spec.exists():
            related_files['spec'] = spec

        return related_files

    def _is_valid_component(self, file_path: Path) -> bool:
        """Validates if a file is an Angular component file."""
        try:
            content = file_path.read_text()
            return '@Component' in content
        except Exception:
            return False
