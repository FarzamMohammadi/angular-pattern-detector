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
│   │   └── analyzer/
│   │       ├── __init__.py
│   │       ├── pattern_analyzer.py
│   │       ├── usage_counter.py
│   │       └── pattern_matcher.py
│   └── output/
│       ├── __init__.py
│       ├── report_generator.py
│       ├── cli_reporter.py
│       └── json_exporter.py
├── tests/
│   └── __init__.py
├── README.md
├── requirements.txt
└── main.py
