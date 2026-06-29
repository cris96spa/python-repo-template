class MissingCommandParameterError(Exception):
    def __init__(self, *args, **kwargs):
        message = "Command functions must have at least one argument, the config object."
        super().__init__(message, *args, **kwargs)


class MissingCommandParameterAnnotationError(Exception):
    def __init__(self, *args, **kwargs):
        message = "First argument of command function must be annotated with target config class."
        super().__init__(message, *args, **kwargs)
