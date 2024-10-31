angular-pattern-detector/
├── src/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── cli_interface.py
│   │   └── path_handler.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── parser/
│   │   │   ├── __init__.py
│   │   │   └── angular_parser.py
│   │   ├── extractor/
│   │   │   ├── __init__.py
│   │   │   └── component_extractor.py
│   │   ├── analyzer/
│   │   │   ├── __init__.py
│   │   │   ├── pattern_analyzer.py
│   │   │   ├── usage_counter.py
│   │   │   └── pattern_matcher.py
│   │   ├── profiler/
│   │   │   ├── __init__.py
│   │   │   └── pattern_profiler.py
│   │   └── output/
│   │       ├── templates/
│   │       │   ├── assets/
│   │       │   │   ├── styles.css
│   │       │   │   ├── main.js
│   │       │   │   └── d3.min.js
│   │       │   ├── patterns/
│   │       │   │   ├── index.html
│   │       │   │   ├── pattern.html
│   │       │   │   └── relationships.html
│   │       │   ├── __init__.py
│   │       │   ├── catalog_generator.py
│   │       │   ├── cli_reporter.py
│   │       │   ├── json_exporter.py
│   │       │   └── report_generator.py
│   └── tests/
│       └── __init__.py
├── README.md
├── requirements.txt
└── main.py
