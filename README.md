# Python Repository Template

The ultimate 2025 Python repository template.

## Features

- [x] [`UV`](https://docs.astral.sh/uv/) as package manager.
- [X] [`Just`](https://github.com/casey/just) as command runner, with many useful shortcuts.
- [x] [`Ruff`](https://docs.astral.sh/ruff/) and [`Mypy`](https://mypy.readthedocs.io/en/stable/) for efficient linting, formatting and type checking.
- [x] [`Pytest`](https://docs.pytest.org/en/stable/) for testing.
- [x] [`Loguru`](https://loguru.readthedocs.io/en/stable/) setup for logging.
- [x] [`Docker`](https://www.docker.com/) support, with a multi stage Dockerfile.
- [x] [`Github Actions CI\CD`] setup, with a workflow that runs tests and linters on every push on the main branch.

## Usage

The templated is based on [UV](https://docs.astral.sh/) as package manager and [Just](https://github.com/casey/just) as command runner. You need to have both installed in your system to use this template.

Once you have those, you can just run

```bash
just dev-sync
```

to create a virtual environment and install all the dependencies, including the development ones. If instead you want to build a "production-like" environment, you can run

```bash
just prod-sync
```

In both cases, all extra dependencies will be installed (notice that the current pyproject.toml file has no extra dependencies).

### Formatting, Linting and Testing

Format your code:

```bash
just format
```

Run linters (ruff and mypy):

```bash
just lint
```

Run tests:

```bash
just test
```

Do all of the above:

```bash
just validate
```

### Executing

The code is a simple hello world example, which just requires a number as input. It will output the sum of the provided number with a random number.
You can run the code with:

```bash
just run 5
```

### Docker

The template includes a multi stage Dockerfile, which produces an image with the code and the dependencies installed. You can build the image with:

```bash
just dockerize
```

### Github Actions

The template includes a Github Actions workflow that runs tests and linters on every push on the main branch. You can find the workflow file in `.github/workflows/main.yml`.




