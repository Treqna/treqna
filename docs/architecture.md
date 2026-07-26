# System Architecture

Treqna is designed as a layered, plugin-driven transformation engine centered around the Universal Data Model (UDM).

## High-Level Architecture Diagram

```mermaid
flowchart TD
    API[Public Developer API / CLI] --> Engine[Transformation Engine]
    Engine --> Session[Transformation Session]
    Session --> Planner[Planning Engine]
    Planner --> Pipeline[8-Stage Execution Pipeline]
    
    subgraph Pipeline Lifecycle
        Detect[1. Detect Stage] --> Inspect[2. Inspect Stage]
        Inspect --> Parse[3. Parse Stage]
        Parse --> GenUDM[4. Generate UDM Stage]
        GenUDM --> Transform[5. Transform Stage]
        Transform --> Validate[6. Validate Stage]
        Validate --> Write[7. Write Stage]
        Write --> Finalize[8. Finalize Stage]
    end
    
    Parse -.-> ParserPlugin[Parser Plugin: Format -> UDM]
    Write -.-> WriterPlugin[Writer Plugin: UDM -> Format]
```

## Architectural Principles

1. **No Direct Format Conversion**: All formats convert to and from UDM tree nodes.
2. **Immutable Objects**: Result objects, statistics, descriptors, and options are frozen dataclasses.
3. **Explicit Capability Registration**: Format descriptors declare exact MIME types, extension aliases, and features.
4. **Deterministic Pipeline**: Every transformation follows the identical 8-stage lifecycle.

