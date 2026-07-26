# Public Developer API Reference

The `treqna` package exposes 13 top-level functions and an immutable fluent builder interface.

## Core Functions

### `transform(source)`
Initiates a fluent transformation builder.

```python
import treqna

result = treqna.transform("input.csv").to("csv").validate().optimize().execute()
print(result.output)
```

### `detect(source)`
Detects format family, encoding, and dialect.

```python
detection = treqna.detect("a,b\n1,2\n")
print(detection.detected_format)  # 'csv'
print(detection.confidence_score) # 1.0
```

### `inspect(source)`
Extracts structural schema metadata.

```python
inspection = treqna.inspect("id,name\n1,Alice\n")
print(inspection.schema_info["columns"])  # ('id', 'name')
```

### `validate(source, schema=None)`
Validates structural syntax and column consistency.

```python
validation = treqna.validate("col1,col2\nval1,val2\n")
print(validation.is_valid)  # True
```

### `repair(source)`
Repairs structural syntax issues in payload.

```python
repaired = treqna.repair("col1,col2\nval1\n")
print(repaired.status)  # 'repaired'
```

### `normalize(source)`
Normalizes data payload representation.

```python
normalized = treqna.normalize("col1,col2\n1,2\n")
print(normalized.status)  # 'normalized'
```

### `preview(source)`
Generates textual preview of content.

```python
prev = treqna.preview("header1,header2\ndata1,data2\n")
print(prev.preview_content)
```

### `compare(source_a, source_b)`
Compares structural equivalency of two data sources.

```python
comp = treqna.compare("a,b\n1,2\n", "a,b\n1,2\n")
print(comp.identical)  # True
```

### `compress(source, algorithm="gzip")`
Compresses data payload.

```python
res = treqna.compress("data", algorithm="gzip")
print(res.status)  # 'compressed'
```

### `extract(source)`
Extracts payload from archive.

```python
res = treqna.extract("archive.zip")
print(res.extracted_items_count)
```

### `merge(sources)`
Combines multiple data sources.

```python
merged = treqna.merge(["data1.csv", "data2.csv"])
print(merged.merged_sources_count)  # 2
```

### `split(source, target_count=2)`
Splits data payload into target partitions.

```python
split_res = treqna.split("large_data.csv", target_count=4)
print(split_res.split_parts_count)  # 4
```
