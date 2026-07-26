import treqna

json_data = '[{"id": 101, "name": "Alice"}]'

detection = treqna.detect(json_data)
print(f"Format: {detection.detected_format} (confidence: {detection.confidence_score})")

inspection = treqna.inspect(json_data)
print(f"Schema Info: {inspection.schema_info}")

validation = treqna.validate(json_data)
print(f"Validation: {'VALID' if validation.is_valid else 'INVALID'}")
