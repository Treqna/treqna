import treqna

csv_data = "id,name,role\n101,Alice,Engineer\n102,Bob,Architect\n"

excel_result = treqna.transform(csv_data).to("excel").execute()
print(f"Generated Excel binary payload size: {len(excel_result.output)} bytes")

json_result = treqna.transform(excel_result.output).to("json").execute()
print("Excel -> JSON:")
print(json_result.output)
