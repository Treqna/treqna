# Practical Examples & Recipes

Below are practical code recipes for integrating Treqna into Python applications.

## Custom Options and Tab Delimiters

```python
import treqna

tsv_data = "name\tscore\nAlice\t98\nBob\t92\n"

result = (
    treqna.transform(tsv_data)
    .to("csv")
    .with_options({
        "delimiter": "\t",
        "has_header": True,
    })
    .execute()
)

print(result.output)
```

## Validating Input Payloads before Execution

```python
import treqna

raw_data = "col1,col2\nval1,val2\n"

validation = treqna.validate(raw_data)
if validation.is_valid:
    result = treqna.transform(raw_data).to("csv").execute()
    print("Transformed Output:")
    print(result.output)
else:
    print(f"Validation Error: {validation.validation_issues}")
```
