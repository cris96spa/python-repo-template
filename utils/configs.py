from pathlib import Path

from pydantic import AnyHttpUrl
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
        sources = (
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
                    yaml_file_encoding=cls.model_config.get(
                        "yaml_file_encoding", "utf-8"
                    ),
                ),
            )
        return sources


class GlobalConfig(YamlBaseSettings):
    log_level: str
    model_config = SettingsConfigDict(
        yaml_file="configs/global.yaml",
        case_sensitive=False,
        extra="allow",
        yaml_file_encoding="utf-8",
    )


class MlflowLoggerConfig(YamlBaseSettings):
    """Configuration for the Mlflow logger implementation."""

    tracking_uri: AnyHttpUrl | None = None
    remote_tracking_uri: AnyHttpUrl | None = None
    instance: str
    remote_flag: bool
    trace: bool
    templates_path: Path
    artifact_path: str
    run_name: str | None = None

    model_config = SettingsConfigDict(
        yaml_file="configs/mlflow_logger.yaml",
        case_sensitive=False,
        extra="allow",
        yaml_file_encoding="utf-8",
    )
