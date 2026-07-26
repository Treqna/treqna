from pathlib import Path
import treqna


def run_csv_vertical_slice_example() -> None:
    csv_payload = "product,price,category\nLaptop,1200,Electronics\nChair,150,Furniture\n"

    det = treqna.detect(csv_payload)
    print(f"Format detected: {det.detected_format}")

    ins = treqna.inspect(csv_payload)
    print(f"Columns: {ins.schema_info.get('columns')}")

    val = treqna.validate(csv_payload)
    print(f"Valid CSV: {val.is_valid}")

    result = treqna.transform(csv_payload).to("csv").validate().optimize().execute()
    print("Transformed CSV Output:")
    print(result.output)


if __name__ == "__main__":
    run_csv_vertical_slice_example()
