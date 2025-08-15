from utils.configs import GlobalConfig, MlflowLoggerConfig
from utils.singleton import SingletonMeta


class BaseConfigProvider(metaclass=SingletonMeta):
    """Singleton class to provide configs for the application."""

    def __init__(self):
        self._global_config = GlobalConfig()
        self._mlflow_config = MlflowLoggerConfig()

    @property
    def global_config(self) -> GlobalConfig:
        """Get the global config."""
        return self._global_config

    @property
    def mlflow_configs(self) -> MlflowLoggerConfig:
        """Get the MLflow logger config."""
        return self._mlflow_config
