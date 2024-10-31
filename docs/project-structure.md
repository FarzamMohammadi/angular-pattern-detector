```plaintext
angular-pattern-detector/
├── src/
│   ├── cli/
│   │   ├── cli_interface.py        # CLI interactions and progress tracking
│   │   └── path_handler.py         # File system operations and path resolution
│   ├── core/
│   │   ├── parser/
│   │   │   └── angular_parser.py   # Angular component parsing
│   │   ├── extractor/
│   │   │   └── component_extractor.py  # Pattern extraction from templates
│   │   ├── analyzer/
│   │   │   └── pattern_analyzer.py     # Analyzes usage, complexity, relationships, maintainability, and accessibility
│   │   └── output/
│   │       ├── templates/
│   │       │   ├── assets/
│   │       │   │   ├── styles.css      # Catalog styling
│   │       │   │   └── main.js         # Interactive features
│   │       │   └── patterns/
│   │       │       ├── index.html      # Catalog main page
│   │       │       ├── pattern.html    # Individual pattern pages
│   │       │       └── relationships.html  # Pattern relationship view
│   │       ├── catalog_generator.py    # HTML catalog generation
│   │       └── report_generator.py     # Analysis reports
├── docs/
│   ├── progress.md                 # Implementation status
│   ├── project-structure.md        # Project documentation
│   └── system.md                   # System architecture
├── pattern-catalog/               # Generated output
│   ├── assets/
│   │   ├── styles.css            # Generated styles
│   │   ├── main.js              # Generated scripts
│   │   └── d3.min.js            # D3.js for visualizations
│   └── patterns/
│       ├── index.html           # Generated catalog
│       ├── *.html              # Generated pattern pages
│       └── relationships.html   # Generated relationship view
├── requirements.txt             # Python dependencies
├── README.md                   # Project documentation
└── main.py                     # Application entry point
```