# Planning System Architecture

The **Planning System** decides *how* a transformation request should execute without performing execution itself.

## Planner Decision Diagram

```mermaid
graph TD
    Request[Planning Request] --> Policy[Planning Policy & Rules]
    Policy --> Evaluator[Path Evaluator & Cost Estimator]
    Evaluator --> Scorer[Path Scorer & Quality Estimator]
    Scorer --> Matcher[Capability Matcher & Constraint Solver]
    Matcher --> Plan[Transformation Plan]
    Plan --> Fingerprint[Pipeline Fingerprint]
```

## Core Planning Primitives

- `Planner`: Facade managing route discovery and cost scoring.
- `TransformationPlan`: Immutable plan containing plan nodes, edges, cost metrics, quality scores, and stable `PipelineFingerprint`.
- `CostEstimator` & `QualityEstimator`: Abstract estimators rating execution cost and metadata preservation scores.
- `ConstraintSolver`: Solves format compatibility constraints.
