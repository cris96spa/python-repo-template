import ast
import importlib
import logging
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ImportErrorDetails(BaseModel):
    """Container for import error information."""

    file_path: Path = Field(description="Path to the file with the import error")
    line_number: int = Field(description="Line number of the import statement")
    module_name: str = Field(description="Name of the module being imported")
    error_type: str = Field(description="Type of the import error")
    error_message: str = Field(description="Error message from the import failure")
    import_statement: str = Field(description="The full import statement as a string")


class ImportValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors: list[ImportErrorDetails] = []

    def scan_package(self, package_name: str) -> None:
        package_path = self.project_root / package_name
        if not package_path.exists():
            logger.warning("Package not found: %s (%s)", package_name, package_path)
            return

        python_files = sorted(package_path.rglob("*.py"))
        logger.info("Scanning %d files in '%s'", len(python_files), package_name)

        for py_file in python_files:
            self._validate_file_imports(py_file)

    def _validate_file_imports(self, file_path: Path) -> None:
        tree = self._parse_file_ast(file_path)
        if tree is None:
            return

        try_block_node_ids = self._try_block_node_ids(tree)

        for node in ast.walk(tree):
            if id(node) in try_block_node_ids:
                continue

            self._validate_import_node(file_path, node)

    @staticmethod
    def _parse_file_ast(file_path: Path) -> ast.AST | None:
        try:
            source = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error("Could not read %s: %s", file_path, e)
            return None

        try:
            return ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            logger.error("Syntax error in %s: %s", file_path, e)
            return None

    def _validate_import_node(self, file_path: Path, node: ast.AST) -> None:
        if isinstance(node, ast.Import):
            self._validate_direct_imports(file_path, node)
            return

        if isinstance(node, ast.ImportFrom):
            self._validate_from_imports(file_path, node)

    def _validate_direct_imports(self, file_path: Path, node: ast.Import) -> None:
        for alias in node.names:
            self._try_import(
                file_path=file_path,
                line_number=node.lineno,
                module_name=alias.name,
                import_statement=f"import {alias.name}",
                is_attribute=False,
            )

    def _validate_from_imports(self, file_path: Path, node: ast.ImportFrom) -> None:
        if node.module is None:
            return

        module_name = node.module

        self._try_import(
            file_path=file_path,
            line_number=node.lineno,
            module_name=module_name,
            import_statement=f"from {module_name} import ...",
            is_attribute=False,
        )

        for alias in node.names:
            if alias.name == "*":
                continue

            self._try_import(
                file_path=file_path,
                line_number=node.lineno,
                module_name=f"{module_name}.{alias.name}",
                import_statement=f"from {module_name} import {alias.name}",
                is_attribute=True,
            )

    @staticmethod
    def _try_block_node_ids(tree: ast.AST) -> set[int]:
        """Return IDs of nodes that are inside try blocks (try body only)."""
        ids: set[int] = set()
        for t in ast.walk(tree):
            if isinstance(t, ast.Try):
                for stmt in t.body:
                    for n in ast.walk(stmt):
                        ids.add(id(n))
        return ids

    def _try_import(
        self,
        file_path: Path,
        line_number: int,
        module_name: str,
        import_statement: str,
        *,
        is_attribute: bool,
    ) -> None:
        try:
            if not is_attribute:
                importlib.import_module(module_name)
                return

            parent, _, attr = module_name.rpartition(".")
            if not parent or not attr:
                importlib.import_module(module_name)
                return

            mod = importlib.import_module(parent)
            if hasattr(mod, attr):
                return

            importlib.import_module(module_name)

        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            self.errors.append(
                ImportErrorDetails(
                    file_path=file_path,
                    line_number=line_number,
                    module_name=module_name,
                    import_statement=import_statement,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
            )

    def log_report(self) -> None:
        if not self.errors:
            logger.info("All imports validated successfully.")
            return

        grouped: dict[Path, list[ImportErrorDetails]] = {}
        for err in self.errors:
            grouped.setdefault(err.file_path, []).append(err)

        logger.error(
            "IMPORT VALIDATION FAILED: %d error(s) in %d file(s)",
            len(self.errors),
            len(grouped),
        )

        for file_path in sorted(grouped):
            rel = file_path.relative_to(self.project_root)
            errs = sorted(grouped[file_path], key=lambda e: e.line_number)
            logger.error("File: %s (%d error(s))", rel, len(errs))
            for e in errs:
                jump = f"{file_path}:{e.line_number}"
                logger.error(
                    "  L%d | %s | %s: %s | %s",
                    e.line_number,
                    e.import_statement,
                    e.error_type,
                    e.error_message,
                    jump,
                )


def format_failure(
    errors: Iterable[ImportErrorDetails], project_root: Path, limit: int = 25
) -> str:
    errs = list(errors)
    lines: list[str] = [f"{len(errs)} import error(s) found. Showing up to {limit}:"]
    for e in errs[:limit]:
        rel = e.file_path.relative_to(project_root)
        lines.append(
            f"- {rel}:{e.line_number}  {e.import_statement}  -> {e.error_type}: {e.error_message}"
        )
    if len(errs) > limit:
        lines.append(f"... and {len(errs) - limit} more.")
    return "\n".join(lines)
