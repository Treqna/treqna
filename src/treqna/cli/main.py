import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from treqna._version import __version__
from treqna.api import detect, inspect, transform, validate
from treqna.sdk.generator import DriverGenerator


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="treqna",
        description="Treqna command line interface.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    detect_parser = subparsers.add_parser("detect", help="Detect input format")
    detect_parser.add_argument("source", help="Source file path")

    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect input schema and structure"
    )
    inspect_parser.add_argument("source", help="Source file path")

    validate_parser = subparsers.add_parser(
        "validate", help="Validate input file syntax"
    )
    validate_parser.add_argument("source", help="Source file path")

    transform_parser = subparsers.add_parser(
        "transform", help="Transform input file to target format"
    )
    transform_parser.add_argument("source", help="Source file path")
    transform_parser.add_argument(
        "--to",
        dest="target_format",
        required=True,
        help="Target output format",
    )
    transform_parser.add_argument(
        "--out",
        dest="output_file",
        required=False,
        help="Optional output file path",
    )

    create_driver_parser = subparsers.add_parser(
        "create-driver", help="Generate a new Treqna Driver plugin project"
    )
    create_driver_parser.add_argument(
        "format_name",
        help="Name of format (e.g. protobuf, parquet, toml, myformat)",
    )
    create_driver_parser.add_argument(
        "--output-dir",
        dest="output_dir",
        required=False,
        help="Optional output directory path for generated project",
    )

    return parser


def main(args: Sequence[str] | None = None) -> int:
    parser = create_parser()
    parsed = parser.parse_args(args=args)

    if not parsed.command:
        return 0

    if parsed.command == "detect":
        res_detect = detect(parsed.source)
        fmt = res_detect.detected_format
        conf = res_detect.confidence_score
        print(f"Format: {fmt} (confidence: {conf})")
        return 0 if res_detect.success else 1

    if parsed.command == "inspect":
        res_inspect = inspect(parsed.source)
        print(f"Schema Info: {res_inspect.schema_info}")
        return 0 if res_inspect.success else 1

    if parsed.command == "validate":
        res_val = validate(parsed.source)
        if res_val.is_valid:
            print("Validation: VALID")
            return 0
        print(f"Validation: INVALID ({', '.join(res_val.validation_issues)})")
        return 1

    if parsed.command == "transform":
        builder = transform(parsed.source).to(parsed.target_format)
        res_tx = builder.execute()
        if not res_tx.success:
            print(f"Transformation Error: {', '.join(res_tx.errors)}")
            return 1
        if parsed.output_file and res_tx.output:
            out_p = Path(parsed.output_file)
            out_p.write_text(str(res_tx.output), encoding="utf-8")
            print(f"Transformation Output written to {parsed.output_file}")
        else:
            print(res_tx.output)
        return 0

    if parsed.command == "create-driver":
        generator = DriverGenerator()
        out_path = generator.generate_driver_project(
            format_name=parsed.format_name,
            output_dir=parsed.output_dir,
        )
        print(f"Successfully generated Treqna driver project at {out_path}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

