from pathlib import Path
from typing import List, Dict
import asyncio


class PathHandler:
    def __init__(self):
        self.angular_extensions = ['.ts', '.html', '.scss', '.css']

    def validate_project_path(self, path: Path) -> bool:
        """Validates if the given path contains Angular components."""
        if not path.exists():
            return False

        # For sample projects, just check if we have component files
        component_files = list(path.rglob("*.component.ts"))
        return len(component_files) > 0

    def find_component_files(self, base_path: Path) -> List[Path]:
        """Finds all Angular component files"""
        # First, get all TypeScript files
        all_ts_files = list(base_path.rglob("*.component.ts"))
        if not all_ts_files:
            print(f"No .component.ts files found in {base_path}")
            return []

        print(f"Found {len(all_ts_files)} potential component files")

        component_files = []
        for file_path in all_ts_files:
            if self._is_valid_component(file_path):
                component_files.append(file_path)
                print(f"Valid component found: {file_path}")

        if not component_files:
            print("No valid Angular components found after validation")
        else:
            print(f"Found {len(component_files)} valid Angular components")

        return component_files

    def _is_valid_component(self, file_path: Path) -> bool:
        """Validates if a file is an Angular component file"""
        try:
            # Read the file content directly for small files
            content = file_path.read_text()

            # Debug output
            print(f"Validating component: {file_path}")
            has_component = '@Component' in content
            print(f"Has @Component decorator: {has_component}")

            return has_component

        except Exception as e:
            print(f"Error validating component {file_path}: {str(e)}")
            return False

    def get_related_files(self, component_file: Path) -> Dict[str, Path]:
        """Gets related template, style, and spec files for a component."""
        base_name = component_file.stem.replace('.component', '')
        parent_dir = component_file.parent

        related_files = {'typescript': component_file, 'template': None, 'styles': [], 'spec': None}

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

    def _debug_path_search(self, base_path: Path):
        """Debug method to print file search results"""
        print(f"\nDebug: Searching in {base_path}")
        print("Found files:")
        for ext in ['*.component.ts', '*.component.html', '*.component.scss', '*.component.css']:
            files = list(base_path.rglob(ext))
            print(f"{ext}: {len(files)} files")
            for f in files[:5]:  # Show first 5 files of each type
                print(f"  - {f}")

    async def get_related_files_async(self, component_file: Path) -> Dict[str, Path]:
        """Asynchronous file operations"""
        related_files = {'typescript': None, 'template': None, 'styles': [], 'spec': None}

        tasks = []
        for ext in ['.ts', '.html', '.scss', '.css']:
            tasks.append(self._check_file_exists_async(component_file, ext))

        results = await asyncio.gather(*tasks)
        # Process results...
        return related_files
