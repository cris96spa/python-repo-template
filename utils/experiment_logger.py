from __future__ import annotations

import json
import os
import tempfile
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import override

import dotenv
import mlflow
import mlflow.data.pandas_dataset
import pandas as pd

from utils.configs import MlflowLoggerConfig
from utils.logger import logger

logger.bind("app", "Experiment Logger")


class BaseExperimentLogger(ABC):
    """Abstract base class for experiment logging."""

    @abstractmethod
    def log_dict(self, data: dict) -> None:
        """Log a dictionary to the experiment tracking system."""
        pass

    @abstractmethod
    def log_experiment_data(self, data_paths: list[Path]):
        """Logs experiment data."""

    @abstractmethod
    def log_input(self, input_path: Path) -> None:
        """Log the input dataset to the experiment tracking system."""
        pass

    @abstractmethod
    def __enter__(self) -> BaseExperimentLogger:
        """Enter the context manager for the experiment logger."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager for the experiment logger."""
        pass


class MlflowLogger(BaseExperimentLogger):
    def __init__(
        self,
        config: MlflowLoggerConfig,
    ) -> None:
        self._config = config
        self._experiment_name = config.experiment_name
        self._run_name = config.run_name
        self._artifact_path = config.artifact_path
        self._templates_path = config.templates_path

        self._setup()

    def _setup(self) -> None:
        dotenv.load_dotenv(override=True)
        if self._config.remote_flag:
            uri = self._config.remote_tracking_uri.unicode_string()
            logger.info("Using remote MLflow tracking URI: %s", uri)

        else:
            uri = self._config.tracking_uri.unicode_string()
            logger.info("Using local MLflow tracking URI: %s", uri)

        mlflow.set_tracking_uri(uri)
        mlflow.config.enable_async_logging(enable=True)  # type: ignore  # noqa: PGH003
        if self._config.trace:
            mlflow.openai.autolog()
            logger.info("MLflow OpenAI autologging enabled.")
        logger.info(
            "MLflow logging enabled with async mode on %s", self._config.tracking_uri
        )

    @override
    def log_dict(self, data: dict) -> None:
        """Log a dictionary to MLflow as parameters or metrics."""
        for key, value in data.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, value)
            elif isinstance(value, str):
                mlflow.log_param(key, value)
            else:
                mlflow.log_param(key, json.dumps(value))

    @override
    def log_experiment_data(self, data_paths: list[Path]):
        """Logs experiment data files as MLflow artifacts and, if applicable, as tables.

        For each path in `data_paths`, this method:
          - Checks if the file exists; if not, logs a warning and skips it.
          - Logs the file as an MLflow artifact under a subdirectory named after its parent folder.
          - If the file is JSON, attempts to read it into a pandas DataFrame and logs it as a table.
          - If the JSON file contains a single record, logs its contents as a dictionary.
          - Logs an info message upon successful artifact logging.

        Args:
            data_paths (list[Path]): List of file paths to be logged as experiment artifacts.

        Notes:
            - If reading a JSON file fails, the exception is silently ignored.
            - Requires `mlflow`, `pandas`, and a configured logger.
        """
        for data_path in data_paths:
            if not data_path.exists():
                logger.warning(
                    "Data path %s does not exist, skipping logging.", data_path
                )
                continue

            # Note that MLFlow does not allow csv files to be logged as tables
            if data_path.suffix.lower() == ".json":
                # Attempt to read the JSON file and log it as a table
                try:
                    df = pd.read_json(data_path, orient="records")
                    mlflow.log_table(df, artifact_file=data_path.name)
                    if df.shape[0] == 1:
                        self.log_dict(df.iloc[0].to_dict())
                        return
                except BaseException as e:
                    logger.error("Error reading JSON file %s: %s", data_path, e)
                    pass
            elif data_path.suffix.lower() == ".jinja2":
                return self._log_jinja_templates(data_path)
            # Log the data file as an artifact
            mlflow.log_artifact(
                str(data_path),
                artifact_path=os.path.join(self._artifact_path, data_path.parent.name),
            )
            logger.info("Logged artifact: %s", data_path)

    def _log_jinja_templates(self, file_path: Path) -> None:
        """Logs Jinja2 template fileas text artifacts to MLflow.

        Args:
            file_path (str): The path to the local directory containing Jinja2 template files.

        """
        if os.path.exists(file_path):
            logger.info("Logging template from: %s", file_path)
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert Jinja2 templates to text files for logging
                dest_path = Path(os.path.join(temp_dir, file_path.name + ".txt"))
                with open(file_path, "r") as src_file:
                    content = src_file.read()
                with open(dest_path, "w") as dest_file:
                    dest_file.write(content)

                mlflow.log_artifact(
                    str(dest_path),
                    artifact_path=os.path.join(
                        self._artifact_path, file_path.parent.name
                    ),
                )

    @override
    def log_input(self, input_path: Path) -> None:
        """Logs the input dataset to MLflow after loading it from the specified file path.

        Supports loading data from JSON, CSV, and Parquet files. The loaded data is converted
        into an MLflow pandas dataset and logged as an input artifact.

        Args:
            input_path (Path): The path to the input data file.

        Raises:
            FileNotFoundError: If the specified input path does not exist.
            ValueError: If the file format is not one of .json, .csv, or .parquet.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"The input path {input_path} does not exist.")
        logger.info("Loading input data from %s", input_path)
        format = input_path.suffix.lower()
        if format == ".json":
            input_data = pd.read_json(input_path, orient="records")
        elif format == ".csv":
            input_data = pd.read_csv(input_path)
        elif format == ".parquet":
            input_data = pd.read_parquet(input_path)
        else:
            raise ValueError(
                f"Unsupported file format: {format}. Only .json, .csv, and .parquet are supported."
            )

        dataset = mlflow.data.pandas_dataset.from_pandas(
            input_data,
            source=str(input_path),
            name=input_path.stem,
            # targets=AssessmentColumnNames.GROUND_TRUTH.value,
        )

        mlflow.log_input(
            dataset=dataset,
        )

    def _log_metadata(self) -> None:
        """Log root-level metadata (project version, git commit, etc)."""
        mlflow.set_tag("project_name", self._config.project_name)
        try:
            import importlib.metadata

            version = importlib.metadata.version(self._config.project_name)
            mlflow.set_tag("project_version", version)
        except Exception:
            pass

        try:
            from git import Repo

            repo = Repo(search_parent_directories=True)
            sha = repo.head.object.hexsha
            branch = repo.active_branch.name
            mlflow.set_tag("git_commit", sha)
            mlflow.set_tag("git_branch", branch)
        except Exception:
            pass

        mlflow.set_tag("run_host", os.uname().nodename)
        mlflow.set_tag("run_datetime", datetime.now().isoformat())

    @override
    def __enter__(self) -> MlflowLogger:
        if self._run_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = uuid.uuid4().hex[:6]
            self._run_name = f"run_{timestamp}_{random_id}"
        mlflow.set_experiment(self._experiment_name)
        mlflow.start_run(run_name=self._run_name)
        logger.info("Started MLflow run with name: %s", self._run_name)
        logger.info("Active run ID: %s", mlflow.active_run().info.run_id)  # type: ignore  # noqa: PGH003
        self._log_metadata()
        return self

    @override
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        logger.info("Result logged to MLflow.")
        logger.info("MLflow run ID: %s", mlflow.active_run().info.run_id)  # type: ignore  # noqa: PGH003
        mlflow.end_run()
