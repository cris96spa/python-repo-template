from __future__ import annotations

import functools
import importlib.metadata
import logging
import os
import tempfile
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, override

import dotenv
import mlflow
import mlflow.data.polars_dataset
import polars as pl

from utils.configs import MlflowLoggerConfig

logger = logging.getLogger(__name__)


class BaseExperimentLogger(ABC):
    """Abstract base class for experiment logging."""

    @abstractmethod
    def log_input(self, input_path: Path) -> None:
        """Log the input dataset to the experiment tracking system."""

    @abstractmethod
    def log_local_directory(self, local_dir: Path) -> None:
        """Log all files under a local directory."""

    @abstractmethod
    def __enter__(self) -> BaseExperimentLogger:
        """Enter the context manager for the experiment logger."""

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager for the experiment logger."""


class MlflowLogger(BaseExperimentLogger):
    """MLflow-backed experiment logger."""

    def __init__(self, config: MlflowLoggerConfig) -> None:
        self._config = config
        self._experiment_name = config.experiment_name
        self._run_name = config.run_name
        self._configure_tracking()

    @override
    def __enter__(self) -> MlflowLogger:
        if self._run_name is None:
            self._run_name = self._generate_run_name()
        mlflow.start_run(run_name=self._run_name)
        logger.info("Started MLflow run with name: %s", self._run_name)
        active_run = mlflow.active_run()
        if active_run is not None:
            logger.info("Active run ID: %s", active_run.info.run_id)
        self._log_run_metadata()
        return self

    @override
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        active_run = mlflow.active_run()
        if active_run is not None:
            logger.info("Result logged to MLflow.")
            logger.info("MLflow run ID: %s", active_run.info.run_id)
        status = "FAILED" if exc_type is not None else "FINISHED"
        mlflow.end_run(status=status)

    def __getattr__(self, name: str) -> Any:
        """Fall through to `mlflow` for attributes not defined on the logger.

        Run-scoped logging calls (`log_*` / `set_tag*`) are guarded:
        they are skipped with a warning when no run is active.

        Args:
            name: The attribute name being accessed.

        Returns:
            The attribute from `mlflow`, or a guarded version of it if it's a
            run-scoped logging call.

        Raises:
            AttributeError: If the attribute name starts with an underscore.
        """
        if name.startswith("_"):
            raise AttributeError(name)
        attr = getattr(mlflow, name)
        if not (callable(attr) and (name.startswith("log_") or name.startswith("set_tag"))):
            return attr

        @functools.wraps(attr)
        def run_guarded(*args: Any, **kwargs: Any) -> Any:
            if mlflow.active_run() is None:
                logger.warning("No active MLflow run. '%s' call ignored.", name)
                return None
            return attr(*args, **kwargs)

        return run_guarded

    @override
    def log_input(self, input_path: Path) -> None:
        """Log the input dataset to MLflow.

        Supports `.json`, `.csv` and `.parquet` files.

        Args:
            input_path: The file path of the input dataset to log.

        Raises:
            FileNotFoundError: If `input_path` does not exist.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"The input path {input_path} does not exist.")
        logger.info("Loading input data from %s", input_path)
        input_data = self._read_dataframe(input_path)
        dataset = mlflow.data.polars_dataset.from_polars(
            input_data,
            source=str(input_path),
            name=input_path.stem,
        )
        mlflow.log_input(dataset=dataset)

    @override
    def log_local_directory(self, local_dir: Path) -> None:
        """Iterate over every file under `local_dir` and push it to MLflow.

        Args:
            local_dir: The local directory whose contents to log.
        """
        local_dir = Path(local_dir)
        if not local_dir.exists():
            logger.warning("Local directory %s does not exist, skipping logging.", local_dir)
            return
        local_dir_resolved = local_dir.resolve()
        for file_path in sorted(local_dir.rglob("*")):
            if not file_path.is_file():
                continue
            try:
                rel_path = file_path.resolve().relative_to(local_dir_resolved)
            except ValueError:
                rel_path = Path(file_path.name)
            self._dispatch_local_file(file_path, rel_path)

    def _configure_tracking(self) -> str:
        """Configure MLflow tracking from `self._config`."""
        dotenv.load_dotenv(override=True)
        uri = str(self._config.tracking_uri)
        logger.info("Setting MLflow tracking URI to: %s", uri)
        mlflow.set_tracking_uri(uri)
        mlflow.config.enable_async_logging(enable=True)  # type: ignore  # noqa: PGH003
        if self._config.trace:
            mlflow.openai.autolog()
            logger.info("MLflow OpenAI autologging enabled.")
        mlflow.set_experiment(self._experiment_name)
        logger.info("MLflow logging enabled with async mode on %s", uri)
        return uri

    def _log_run_metadata(self) -> None:
        """Tag the active MLflow run with project, git and host metadata."""
        mlflow.set_tag("project_name", self._config.project_name)
        try:
            version = importlib.metadata.version(self._config.project_name)
            mlflow.set_tag("project_version", version)
        except Exception:
            pass
        try:
            from git import Repo

            repo = Repo(search_parent_directories=True)
            mlflow.set_tag("git_commit", repo.head.object.hexsha)
            mlflow.set_tag("git_branch", repo.active_branch.name)
        except Exception:
            pass
        mlflow.set_tag("run_host", os.uname().nodename)
        mlflow.set_tag("run_datetime", datetime.now().isoformat())

    def _dispatch_local_file(self, file_path: Path, rel_path: Path) -> None:
        """Send a single file to MLflow using the right call for its extension."""
        suffix = file_path.suffix.lower()
        artifact_dir = rel_path.parent.as_posix()
        artifact_path = artifact_dir if artifact_dir not in ("", ".") else None

        if suffix == ".json" and self._try_log_json_as_table(file_path, rel_path):
            return
        if suffix == ".jinja2":
            self._log_jinja_as_text(file_path, rel_path, artifact_path)
            return
        mlflow.log_artifact(str(file_path), artifact_path=artifact_path)
        logger.info("Logged file artifact: %s", rel_path.as_posix())

    def _try_log_json_as_table(self, file_path: Path, rel_path: Path) -> bool:
        """Try to log `file_path` as an MLflow table.

        The frame is read with polars but converted to pandas before logging,
        since :func:`mlflow.log_table` only accepts `dict` or pandas frames.

        Args:
            file_path: The path to the JSON file to log.
            rel_path: The relative path to use for the logged artifact.

        Returns:
            `True` on success, `False` otherwise.
        """
        try:
            dataset = pl.read_json(file_path)
        except Exception as e:
            logger.debug("File %s is not a records-oriented JSON: %s", file_path, e)
            return False
        if dataset.is_empty() or dataset.width == 0:
            logger.debug("File %s read as empty dataframe; skipping table logging.", file_path)
            return False
        try:
            mlflow.log_table(dataset.to_pandas(), artifact_file=rel_path.as_posix())
        except Exception as e:
            logger.error("Error logging %s as MLflow table: %s", file_path, e)
            return False
        logger.info("Logged table: %s", rel_path.as_posix())
        return True

    def _log_jinja_as_text(
        self, file_path: Path, rel_path: Path, artifact_path: str | None
    ) -> None:
        """Copy a Jinja2 template to a `.txt` sibling and log it as an artifact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir) / f"{file_path.name}.txt"
            txt_path.write_text(file_path.read_text())
            mlflow.log_artifact(str(txt_path), artifact_path=artifact_path)
            logger.info("Logged jinja template as text: %s.txt", rel_path.as_posix())

    @staticmethod
    def _generate_run_name() -> str:
        """Build a default run name of the form `run_<timestamp>_<rand>`."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_id = uuid.uuid4().hex[:6]
        return f"run_{timestamp}_{random_id}"

    @staticmethod
    def _read_dataframe(input_path: Path) -> pl.DataFrame:
        """Read `input_path` into a DataFrame based on its suffix.

        Supports `.json` (records-oriented), `.csv` and `.parquet`.

        Args:
            input_path: The path to the input file.

        Returns:
            The loaded DataFrame.

        Raises:
            ValueError: If the file suffix is not one of the supported formats.
        """
        suffix = input_path.suffix.lower()
        if suffix == ".json":
            return pl.read_json(input_path)
        if suffix == ".csv":
            return pl.read_csv(input_path)
        if suffix == ".parquet":
            return pl.read_parquet(input_path)
        raise ValueError(
            f"Unsupported file format: {suffix!r}. Only .json, .csv, and .parquet are supported."
        )
