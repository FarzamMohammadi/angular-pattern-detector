angular-pattern-detector/
├── src/
│   ├── cli/
│   │   ├── cli_interface.py        # Handles command line interactions and progress display
│   │   └── path_handler.py         # Manages file system operations and path resolution
│   ├── core/
│   │   ├── parser/
│   │   │   └── angular_parser.py   # Parses Angular components and extracts metadata
│   │   ├── extractor/
│   │   │   └── component_extractor.py  # Extracts UI patterns from component templates
│   │   ├── analyzer/
│   │   │   ├── pattern_analyzer.py     # Analyzes patterns for complexity and relationships
│   │   │   ├── usage_counter.py        # Tracks pattern usage across components
│   │   │   └── pattern_matcher.py      # Matches similar patterns and variations
│   │   └── output/
│   │       ├── templates/
│   │       │   ├── patterns/
│   │       │   │   ├── index.html          # Main catalog page template
│   │       │   │   ├── pattern.html        # Individual pattern page template
│   │       │   │   └── relationships.html   # Pattern relationships view template
│   │       │   ├── catalog_generator.py     # Generates HTML pattern catalog
│   │       │   └── report_generator.py      # Generates analysis reports
├── pattern-catalog/                         # Generated catalog output
│   ├── assets/
│   │   ├── styles.css                      # Catalog styling
│   │   └── main.js                         # Interactive features
│   └── patterns/
│       └── index.html                      # Generated catalog index
└── main.py                                 # Application entry point