# Quick Start Guide

This 5-minute interactive tutorial demonstrates format detection, schema inspection, validation, and transformation.

## 1. Format Detection

```python
import treqna

payload = "id,name,score\n1,Alice,95.5\n2,Bob,88.0\n"
detection = treqna.detect(payload)

print(f"Format: {detection.detected_format}")
print(f"Confidence: {detection.confidence_score}")
```

## 2. Schema Inspection

```python
inspection = treqna.inspect(payload)
print(f"Columns: {inspection.schema_info['columns']}")
print(f"Column Count: {inspection.schema_info['column_count']}")
```

## 3. Structural Validation

```python
validation = treqna.validate(payload)
print(f"Is Valid: {validation.is_valid}")
```

## 4. Fluent Transformation

```python
result = (
    treqna.transform(payload)
    .to("csv")
    .validate()
    .optimize()
    .execute()
)

print(result.output)
```
