# Official Treqna Excel Driver Plugin

The **Excel Driver Plugin** is the official Treqna plugin providing production-grade Excel (.xlsx) format parsing (XLSX -> UDM), writing (UDM -> XLSX), detection, inspection, and validation using pure Python standard library OpenXML processing without external dependencies.

## Features

- **Format to UDM Parsing**: Reads `.xlsx` workbooks, shared strings, cell types (string, boolean, integer, float, date), and header rows into `UDMDocument` representations (`UDMTabular`, `UDMCollection`, `UDMPrimitive`).
- **UDM to Format Writing**: Serializes UDM structures into OpenXML `.xlsx` ZIP archives containing `xl/workbook.xml`, `xl/sharedStrings.xml`, and `xl/worksheets/sheet1.xml`.
- **Options**: Configurable `worksheet_name`, `header_row`, `create_missing_sheet`, `overwrite_file`, `date_format`, `datetime_format`, `auto_column_width`, `freeze_header`, `preserve_empty_rows`, and `encoding`.
- **Auto-Detection**: Auto-detects Excel `.xlsx` binary ZIP headers (`PK\x03\x04`) and OpenXML manifest structures.
- **Inspection & Validation**: Inspects workbook sheet names, active sheet, sheet count, and validates OpenXML ZIP integrity.

## Usage Example

```python
import treqna

# Transform CSV to Excel (.xlsx)
excel_result = treqna.transform("data.csv").to("excel").execute()

# Save generated Excel binary data to disk
with open("output.xlsx", "wb") as f:
    f.write(excel_result.output)

# Transform Excel back to JSON
json_result = treqna.transform("output.xlsx").to("json").execute()
print(json_result.output)
```

## Options Configuration

Configure options using `ExcelOptions`:

```python
from treqna.plugins.excel import ExcelOptions

options = ExcelOptions(
    worksheet_name="Data",
    header_row=0,
    auto_column_width=True,
    freeze_header=True,
)
```
