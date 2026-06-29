# Python Repository Template
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue?style=flat-square&logo=github)](https://cris96spa.github.io/python-repo-template/)
The ultimate 2026 Python repository template. Simple, fast, customizable, and ready to use.

## 🎯 Core Features

### Development Tools

- 📦 UV - Ultra-fast Python package manager
- 🚀 Make - Command runner
- 💅 Ruff - Lightning-fast linter and formatter
- 🧪 Pytest - Testing framework with fixtures and plugins
- 🧾 Rich - Elegant logging via standard `logging` module

### Infrastructure

- 🛫 Pre-commit hooks
- 🐳 Docker support with multi-stage builds
- 🔄 GitHub Actions CI/CD pipeline


## Usage

The template is based on [UV](https://docs.astral.sh/) as package manager and [Make](https://www.gnu.org/software/make/) as command runner. You need to have both installed in your system to use this template.

Once you have those, you can run

```bash
make dev
```

to create a virtual environment and install all the dependencies, including the development ones, and set up pre-commit hooks. If instead you want to install only production dependencies, you can run

```bash
make install
```

You can see all available targets with:

```bash
make help
```

### Formatting, Linting and Testing

You can configure Ruff by editing the `[tool.ruff]` section in `pyproject.toml`.

Format your code:

```bash
make format
```

Run linters:

```bash
make lint
```

Check formatting without modifying files:

```bash
make format-check
```

### Executing

The code is a simple hello world example, which just requires a number as input. It will output the sum of the provided number with a random number.
You can run the code with:

```bash
uv run python main.py --number 5
```

### Docker

The template includes a multi-stage Dockerfile, which produces an image with the code and the dependencies installed. You can build the image with:

```bash
docker build -t python-repo-template .
```

### Documentation

Build and serve the documentation locally:

```bash
make doc
```

### Github Actions

The template includes two Github Actions workflows.

The first one runs tests and linters on every push on the main and dev branches. You can find the workflow file in `.github/workflows/main-list-test.yml`.

The second one is triggered on every tag push and can also be triggered manually. It builds the distribution and uploads it to PyPI. You can find the workflow file in `.github/workflows/publish.yaml`.

## Greetings
A big thank you to [Giovanni Giacometti](https://github.com/GiovanniGiacometti) for creating this template and sharing it with the community. This template is a fork of his original work, which can be found at [giovannigiacometti/python-repository-template](https://github.com/GiovanniGiacometti/python-repo-template).
