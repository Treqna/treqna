import importlib.util
import sys
from pathlib import Path
import pytest

from treqna.cli.main import main
from treqna.formats.registry import FormatRegistry
from treqna.plugins.registry import PluginRegistry
from treqna.sdk.generator import DriverGenerator


def test_driver_generator_structure(tmp_path: Path) -> None:
    generator = DriverGenerator()
    project_dir = generator.generate_driver_project("myformat", output_dir=tmp_path / "treqna-myformat")

    assert project_dir.exists()
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / "LICENSE").exists()
    assert (project_dir / "mkdocs.yml").exists()

    src_dir = project_dir / "src" / "treqna_myformat"
    assert (src_dir / "__init__.py").exists()
    assert (src_dir / "manifest.py").exists()
    assert (src_dir / "parser.py").exists()
    assert (src_dir / "writer.py").exists()
    assert (src_dir / "detector.py").exists()
    assert (src_dir / "inspector.py").exists()
    assert (src_dir / "validator.py").exists()
    assert (src_dir / "options.py").exists()

    tests_dir = project_dir / "tests"
    assert (tests_dir / "test_myformat_driver.py").exists()
    assert (tests_dir / "test_myformat_integration.py").exists()

    bench_dir = project_dir / "benchmarks"
    assert (bench_dir / "test_myformat_benchmark.py").exists()

    docs_dir = project_dir / "docs"
    assert (docs_dir / "index.md").exists()

    ci_file = project_dir / ".github" / "workflows" / "ci.yml"
    assert ci_file.exists()


def test_driver_sdk_generated_code_execution(tmp_path: Path) -> None:
    generator = DriverGenerator()
    project_dir = generator.generate_driver_project("dummyfmt", output_dir=tmp_path / "treqna-dummyfmt")
    src_dir = project_dir / "src"
    sys.path.insert(0, str(src_dir))

    try:
        manifest_path = src_dir / "treqna_dummyfmt" / "manifest.py"
        spec = importlib.util.spec_from_file_location("treqna_dummyfmt.manifest", manifest_path)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        register_func = getattr(mod, "register_dummyfmt_plugin")
        plugin_reg = PluginRegistry()
        format_reg = FormatRegistry()
        register_func(plugin_reg, format_reg)

        parser = plugin_reg.get_parser("dummyfmt")
        writer = plugin_reg.get_writer("dummyfmt")
        descriptor = format_reg.get_descriptor("dummyfmt")

        assert parser.metadata.name == "dummyfmt_parser"
        assert writer.metadata.name == "dummyfmt_writer"
        assert descriptor.name == "DUMMYFMT"
    finally:
        if str(src_dir) in sys.path:
            sys.path.remove(str(src_dir))


def test_cli_create_driver(tmp_path: Path) -> None:
    out_dir = tmp_path / "cli_driver"
    exit_code = main(["create-driver", "clifmt", "--output-dir", str(out_dir)])
    assert exit_code == 0
    assert (out_dir / "pyproject.toml").exists()
    assert (out_dir / "src" / "treqna_clifmt" / "parser.py").exists()

