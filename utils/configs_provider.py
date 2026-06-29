from functools import cached_property

from utils.configs import GlobalConfig, MlflowLoggerConfig
from utils.singleton import SingletonMeta


class BaseConfigProvider(metaclass=SingletonMeta):
    """Singleton class to provide configs for the application.

    Each config is loaded lazily on first access and cached, so a missing or
    invalid file for one config does not break access to the others.
    """

    @cached_property
    def global_config(self) -> GlobalConfig:
        """Global configuration settings."""
        return GlobalConfig()

    @cached_property
    def mlflow_configs(self) -> MlflowLoggerConfig:
        """MLflow logger configuration settings, loaded from the default file."""
        return MlflowLoggerConfig.from_yaml()
