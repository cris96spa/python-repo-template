from pathlib import Path

import yaml
from pydantic import AnyHttpUrl, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class YamlBaseSettings(BaseSettings):
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


class GlobalConfig(YamlBaseSettings):
    log_level: str = Field(description="Global logging level.", default="INFO")

    model_config = SettingsConfigDict(
        yaml_file="configs/global.yaml",
        case_sensitive=False,
        extra="allow",
        yaml_file_encoding="utf-8",
    )


class BaseExperimentLoggerConfig(YamlBaseSettings):
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

    model_config = SettingsConfigDict(extra="allow")


class MlflowLoggerConfig(BaseExperimentLoggerConfig):
    """Configuration for the MLflow logger implementation."""

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

    model_config = SettingsConfigDict(
        yaml_file="configs/mlflow_logger.yaml",
        case_sensitive=False,
        extra="allow",
        yaml_file_encoding="utf-8",
    )
