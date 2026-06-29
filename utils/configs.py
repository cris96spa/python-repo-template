from pathlib import Path
from typing import ClassVar, Self

import yaml
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class YamlBaseSettings(BaseSettings):
    """Base for process-level settings layered over the environment.

    Use this for configuration that is singular per process (e.g. logging),
    where environment variables should be able to override the YAML file.
    For configs that can be instantiated many times from different files, use
    `YamlBaseModel` instead — env vars are a flat, process-global namespace and
    cannot represent per-instance overrides.
    """

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources: tuple[PydanticBaseSettingsSource, ...] = (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

        yaml_path = cls.model_config.get("yaml_file", None)
        if yaml_path:
            sources += (
                YamlConfigSettingsSource(
                    settings_cls=settings_cls,
                    yaml_file=yaml_path,
                    yaml_file_encoding=cls.model_config.get("yaml_file_encoding", "utf-8"),
                ),
            )
        return sources

    @classmethod
    def from_yaml(cls, file_path: str | Path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, file_path: str | Path):
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(mode="json"), f)


class YamlBaseModel(BaseModel):
    """Base for configs loaded explicitly from a single YAML file.

    Unlike `YamlBaseSettings`, this never reads from the environment, so the
    same class can be instantiated many times from different files without the
    instances sharing a process-global env namespace. `from_yaml` reads
    `DEFAULT_CONFIG_PATH` when no path is given, or the provided path otherwise
    — one load path, one precedence, with the disk read made explicit at the
    call site.
    """

    DEFAULT_CONFIG_PATH: ClassVar[Path | None] = None

    @classmethod
    def from_yaml(cls, path: str | Path | None = None) -> Self:
        """Load and validate the config from a YAML file.

        Args:
            path: Path to the YAML file. When ``None``, ``DEFAULT_CONFIG_PATH``
                is used.

        Returns:
            The validated config instance.

        Raises:
            ValueError: If no ``path`` is given and the class defines no
                ``DEFAULT_CONFIG_PATH``.
        """
        if path is None:
            if cls.DEFAULT_CONFIG_PATH is None:
                raise ValueError(
                    f"{cls.__name__} defines no DEFAULT_CONFIG_PATH; "
                    "a path must be provided to from_yaml()."
                )
            path = cls.DEFAULT_CONFIG_PATH
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return cls.model_validate(data)

    def to_yaml(self, path: str | Path) -> None:
        """Serialize the config to a YAML file.

        Args:
            path: Destination path for the YAML file.
        """
        Path(path).write_text(
            yaml.safe_dump(self.model_dump(mode="json")),
            encoding="utf-8",
        )


class GlobalConfig(YamlBaseSettings):
    log_level: str = Field(description="Global logging level.", default="INFO")

    model_config = SettingsConfigDict(
        yaml_file="configs/global.yaml",
        case_sensitive=False,
        extra="allow",
        yaml_file_encoding="utf-8",
    )


class BaseExperimentLoggerConfig(YamlBaseModel):
    """Base configuration for experiment logger implementations.

    Uses ``extra="allow"`` so that concrete-logger fields (e.g. MLflow's
    ``tracking_uri``) are preserved when this base type is used as the
    field type in command configs.  The command layer can then pass the
    raw data to the concrete config class for full validation.
    """

    project_name: str = Field(description="Name of the project.")
    experiment_name: str = Field(description="Name of the experiment.")
    files_to_exclude_from_logging: list[str] = Field(
        description="Shell wildcards for file names to exclude from logging.",
        default_factory=list,
    )

    model_config = ConfigDict(extra="allow")


class MlflowLoggerConfig(BaseExperimentLoggerConfig):
    """Configuration for the MLflow logger implementation."""

    DEFAULT_CONFIG_PATH: ClassVar[Path] = Path("configs/mlflow_logger.yaml")

    tracking_uri: AnyHttpUrl = Field(description="MLflow tracking URI.")
    trace: bool = Field(
        description="Whether to enable MLflow OpenAI autologging.",
        default=False,
    )
    run_name: str | None = Field(
        description="Optional name for the MLflow run. If not provided, a "
        "default name will be generated.",
        default=None,
    )
