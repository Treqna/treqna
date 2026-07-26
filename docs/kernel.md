# Kernel Engine Architecture

The **Transformation Engine Kernel** coordinates sessions, pipeline execution, and lifecycle management.

## 8-Stage Pipeline Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Engine as TransformationEngine
    participant Session as TransformationSession
    participant Pipeline as PipelineExecutor
    participant Plugin as Format Plugins

    User->>Engine: transform(request)
    Engine->>Session: create_session(request)
    Session->>Pipeline: execute_pipeline(context, request, stages)
    
    rect rgb(240, 248, 255)
        note right of Pipeline: 8-Stage Execution Loop
        Pipeline->>Plugin: 1. DetectStage
        Pipeline->>Plugin: 2. InspectStage
        Pipeline->>Plugin: 3. ParseStage (Format -> UDM)
        Pipeline->>Pipeline: 4. GenerateUDMStage
        Pipeline->>Pipeline: 5. TransformStage
        Pipeline->>Plugin: 6. ValidateStage
        Pipeline->>Plugin: 7. WriteStage (UDM -> Format)
        Pipeline->>Pipeline: 8. FinalizeStage
    end
    
    Pipeline-->>Session: TransformationResult
    Session-->>Engine: TransformationResult
    Engine-->>User: TransformationResult
```

## Kernel Modules

- `TransformationEngine`: Engine entry point managing configuration, discovery, and sessions.
- `PipelineExecutor`: Runs sequence of 8 pipeline stages.
- `LifecycleManager`: Tracks active sessions and memory cleanup.

