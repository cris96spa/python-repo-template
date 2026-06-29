from pathlib import Path

import mkdocs_gen_files

PROJECT_NAME = "python_repo_template"

SOURCE_ROOT = Path(PROJECT_NAME)
API_DIR = Path("api")


# Files to exclude from API documentation generation. By default, `__init__.py` and `__main__.py`
# are skipped. Add or remove entries as needed.
# NOTE: skipping `__init__.py` means package-level docstrings are not included. To include them,
# remove `__init__.py` from this set and ensure each package has a proper docstring.
SKIP_FILENAMES: set[str] = {
    "__init__.py",
    "__main__.py",
}

# Paths to exclude from API documentation generation. Use to omit modules or subpackages that are
# not part of the public API (e.g. legacy code, experimental features). Paths must be relative to
# SOURCE_ROOT and can be .py files or directories. For example:
# SKIP_PATHS = {f"{PROJECT_NAME}/legacy_module"}
SKIP_PATHS: set[str] = set()

# Maps a source path to a custom output path inside documentation structure.
# Use to rename or regroup pages that don't fit the default mirrored structure.
# Keys must be specified from SOURCE_ROOT (included) as .py files, values are the
# desired output path relative to API_DIR as .md files. For example:
# f"{PROJECT_NAME}/example_module/example_a.py": "examples/example_a.md"
SECTION_MAP: dict[str, str] = {}


def main() -> None:
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        if path.name in SKIP_FILENAMES:
            continue
        if any(path.is_relative_to(Path(p)) for p in SKIP_PATHS):
            continue

        module_name = ".".join(path.with_suffix("").parts)
        full_doc_path = API_DIR / _resolve_doc_page_path(path)

        with mkdocs_gen_files.open(full_doc_path, "w") as f:
            f.write(f"::: {module_name}\n")


def _resolve_doc_page_path(source_path: Path) -> Path:
    """Return the documentation page path for a source file."""
    if str(source_path) in SECTION_MAP:
        return Path(SECTION_MAP[str(source_path)])
    return source_path.relative_to(SOURCE_ROOT).with_suffix(".md")


main()
