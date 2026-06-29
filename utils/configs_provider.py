from utils.configs import GlobalConfig
from utils.experiment_logger import MlflowLoggerConfig
from utils.singleton import SingletonMeta


class BaseConfigProvider(metaclass=SingletonMeta):
    """Singleton class to provide configs for the application."""

    def __init__(self):
        self._global_config = GlobalConfig()
        self._mlflow_config = MlflowLoggerConfig()  # type: ignore[call-arg]

    @property
    def global_config(self) -> GlobalConfig:
        """Global configuration settings."""
        return self._global_config

    @property
    def mlflow_configs(self) -> MlflowLoggerConfig:
        """MLflow logger configuration settings."""
        return self._mlflow_config
