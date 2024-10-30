from src.cli.cli_interface import CLIInterface
from src.cli.path_handler import PathHandler


def main():
    # Initialize CLI interface
    cli = CLIInterface()

    try:
        # Parse arguments
        args = cli.parse_arguments()

        # Display initial progress
        cli.display_progress("Analyzing Angular project...")

        # Initialize path handler
        path_handler = PathHandler()

        # Find component files
        component_files = path_handler.find_component_files(args['project_path'])

        if not component_files:
            cli.display_error("No Angular components found in the project")
            return

        cli.display_progress(f"Found {len(component_files)} components", complete=True)

        # TODO: Continue with pattern analysis

    except Exception as e:
        cli.display_error(str(e))
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
