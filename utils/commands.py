import inspect
import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Callable

from utils.exceptions import (
    MissingCommandParameterAnnotationError,
    MissingCommandParameterError,
)

logger = logging.getLogger(__name__)


def command(function: Callable) -> Callable:
    """Decorator that turns a function into a CLI command.

    The decorated function must have at least one parameter (after ``self``,
    if it is a method) whose type annotation is a config class with a
    ``from_yaml`` class method.  At runtime the decorator parses
    ``--config <path>`` from the CLI, loads the YAML into the annotated
    config class, and calls the original function with it.

    Args:
        function (Callable): The function to decorate.

    Returns:
        Callable: The decorated function that can be called from the CLI.

    Raises:
        MissingCommandParameterError: If the function has no parameters (after dropping ``self``).
        MissingCommandParameterAnnotationError: If the first parameter has no type annotation.
    """
    signature = inspect.signature(function)
    parameters = dict(signature.parameters)

    if parameters:
        first_param_name = next(iter(parameters))
        if first_param_name == "self":
            del parameters["self"]

    if not parameters:
        raise MissingCommandParameterError()

    _, config_param = next(iter(parameters.items()))

    if config_param.annotation is inspect.Parameter.empty:
        raise MissingCommandParameterAnnotationError()

    target_config_class = config_param.annotation

    def wrapper(*args, **kwargs):
        logger.info(getattr(function, "__name__", repr(function)))
        logger.info(target_config_class)

        parser = ArgumentParser()
        parser.add_argument("--config", type=Path, help="Path to the config file")
        parsed_args = parser.parse_args()

        if getattr(target_config_class, "from_yaml", None) is None:
            error_msg = (
                f"The target config class {target_config_class} does not have a from_yaml method."
            )
            logger.error(error_msg)
            raise TypeError(error_msg)

        config = target_config_class.from_yaml(parsed_args.config)
        function(config)

    return wrapper
