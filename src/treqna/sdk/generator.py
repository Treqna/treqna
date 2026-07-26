from pathlib import Path

from treqna.sdk.templates import (
    DriverTemplateOptions,
    render_benchmark_test,
    render_detector,
    render_doc_index,
    render_github_ci,
    render_init_py,
    render_inspector,
    render_integration_test,
    render_license,
    render_manifest,
    render_mkdocs_yml,
    render_options,
    render_parser,
    render_pyproject_toml,
    render_readme,
    render_unit_test,
    render_validator,
    render_writer,
)


class DriverGenerator:
    def sanitize_format_name(self, format_name: str) -> str:
        fn = format_name.lower().strip()
        fn = "".join(c if c.isalnum() else "_" for c in fn)
        return fn

    def compute_class_prefix(self, format_name: str) -> str:
        fn = self.sanitize_format_name(format_name)
        parts = fn.split("_")
        prefix = "".join(p.capitalize() for p in parts if p)
        return prefix if prefix else "CustomFormat"

    def generate_driver_project(
        self,
        format_name: str,
        output_dir: Path | str | None = None,
    ) -> Path:
        fn = self.sanitize_format_name(format_name)
        prefix = self.compute_class_prefix(fn)
        package_name = f"treqna-{fn.replace('_', '-')}"
        module_name = f"treqna_{fn}"

        base_dir = (
            Path(output_dir) if output_dir is not None else Path.cwd() / package_name
        )
        src_dir = base_dir / "src" / module_name
        tests_dir = base_dir / "tests"
        bench_dir = base_dir / "benchmarks"
        docs_dir = base_dir / "docs"
        workflows_dir = base_dir / ".github" / "workflows"

        src_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)
        bench_dir.mkdir(parents=True, exist_ok=True)
        docs_dir.mkdir(parents=True, exist_ok=True)
        workflows_dir.mkdir(parents=True, exist_ok=True)

        opts = DriverTemplateOptions(
            format_name=fn,
            class_prefix=prefix,
            package_name=package_name,
        )

        p_toml = render_pyproject_toml(opts)
        (base_dir / "pyproject.toml").write_text(p_toml, encoding="utf-8")
        (base_dir / "README.md").write_text(render_readme(opts), encoding="utf-8")
        (base_dir / "LICENSE").write_text(render_license(), encoding="utf-8")
        (base_dir / "mkdocs.yml").write_text(render_mkdocs_yml(opts), encoding="utf-8")

        (src_dir / "__init__.py").write_text(render_init_py(opts), encoding="utf-8")
        (src_dir / "manifest.py").write_text(render_manifest(opts), encoding="utf-8")
        (src_dir / "options.py").write_text(render_options(opts), encoding="utf-8")
        (src_dir / "parser.py").write_text(render_parser(opts), encoding="utf-8")
        (src_dir / "writer.py").write_text(render_writer(opts), encoding="utf-8")
        (src_dir / "detector.py").write_text(render_detector(opts), encoding="utf-8")
        (src_dir / "inspector.py").write_text(render_inspector(opts), encoding="utf-8")
        (src_dir / "validator.py").write_text(render_validator(opts), encoding="utf-8")

        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        unit_code = render_unit_test(opts)
        (tests_dir / f"test_{fn}_driver.py").write_text(unit_code, encoding="utf-8")
        integ_code = render_integration_test(opts)
        (tests_dir / f"test_{fn}_integration.py").write_text(
            integ_code, encoding="utf-8"
        )

        (bench_dir / "__init__.py").write_text("", encoding="utf-8")
        bench_code = render_benchmark_test(opts)
        (bench_dir / f"test_{fn}_benchmark.py").write_text(
            bench_code, encoding="utf-8"
        )

        (docs_dir / "index.md").write_text(render_doc_index(opts), encoding="utf-8")
        (workflows_dir / "ci.yml").write_text(render_github_ci(), encoding="utf-8")

        return base_dir

