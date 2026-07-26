import treqna

csv_data = "id,name,role\n101,Alice,Engineer\n102,Bob,Architect\n"

result_json = treqna.transform(csv_data).to("json").execute()
print("CSV -> JSON:")
print(result_json.output)

result_yaml = treqna.transform(result_json.output).to("yaml").execute()
print("\nJSON -> YAML:")
print(result_yaml.output)

