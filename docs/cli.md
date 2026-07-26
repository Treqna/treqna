# Command Line Interface (CLI)

Treqna includes a command-line interface for terminal usage and shell automation.

## Subcommands

### `treqna detect`
Detects the format of an input file.

```bash
treqna detect data.csv
```

Output:
```text
Format: csv (confidence: 1.0)
```

### `treqna inspect`
Inspects structural schema metadata and column details.

```bash
treqna inspect data.csv
```

Output:
```text
Schema Info: {'columns': ('id', 'name', 'score'), 'column_count': 3, 'has_header': True, 'delimiter': ',', 'sample_row_count': 100}
```

### `treqna validate`
Validates input file syntax and structural integrity.

```bash
treqna validate data.csv
```

Output:
```text
Validation: VALID
```

### `treqna transform`
Transforms an input file to a target format.

```bash
treqna transform data.csv --to csv --out output.csv
```

Output:
```text
Transformation Output written to output.csv
```

### Display Version

```bash
treqna --version
```
