```mermaid
flowchart TB
    subgraph Input
        CLI[CLI Interface] --> P[Path Handler]
        P --> AP[Angular Parser]
    end

    subgraph Core["Pattern Detection"]
        AP --> CE[Component Extractor]
        CE --> PA[Pattern Analyzer]
        
        subgraph Analytics
            PA --> UC[Usage Counter]
            PA --> PM[Pattern Matcher]
            PA --> PP[Pattern Profiler]
        end
    end

    subgraph Output
        PA --> RG[Report Generator]
        RG --> CR[CLI Report]
        RG --> JSON[JSON Export]
        RG --> CG[Catalog Generator]
        
        subgraph Catalog
            CG --> IX[Index Page]
            CG --> PP[Pattern Pages]
            CG --> RL[Relationship View]
        end
    end