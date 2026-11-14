[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue?style=flat-square&logo=github)](https://cris96spa.github.io/python-repo-template/)

# Python Repository Template

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

The code is a simple example that takes a number as input, draws `SAMPLE_COUNT` random sums with it, and reports the min, mean and max of those draws through the console helpers in `utils/console.py`.
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

The template includes three Github Actions workflows.

The first one runs tests and linters on every push on the main and dev branches. You can find the workflow file in `.github/workflows/main-validate.yaml`.

The second one is triggered on every tag push and can also be triggered manually. It builds the distribution and uploads it to PyPI. You can find the workflow file in `.github/workflows/publish.yaml`.

The third one builds the documentation and deploys it to GitHub Pages on every push to `main`. You can find the workflow file in `.github/workflows/pages.yml`.

## Working with AI Agents

Agent context lives in `CLAUDE.md` at the repository root (`AGENTS.md` is a symlink to it, for agents that look for that name). Repo-local skills live in `.claude/skills/`. `coding-guidelines`, `review-guidelines` and `writing-guidelines` hold the standard for code, reviews and prose; `new-config`, `push-to-pr`, `sync-template` and `update-pr-body` walk through recurring tasks.

## Diagrams

`diagrams/` is an optional module for generating figures — TikZ for schematics, `xy` for data charts. Build it with:

```bash
make install-diagrams   # install the optional diagram toolchain
make diagrams           # build every diagram
make diagrams-clean     # remove generated diagram output
```

If a project does not need it, remove it entirely by following the checklist in `diagrams/README.md`.

## Configuration

The template separates configuration into two kinds, each with its own base class in `utils/configs.py`:

- **Process settings** — `YamlBaseSettings`, layered over the environment so environment variables can override the YAML file. Best for singular, per-process settings such as the global log level.
- **Instance configs** — `YamlBaseModel`, plain data models loaded explicitly from a file. The same class can be loaded many times from different files, with no shared environment state between instances.

### Default path with per-instance override

Instance configs are loaded through `from_yaml`. A config class may set a `DEFAULT_CONFIG_PATH`, which is used whenever no path is given — so the common case takes no arguments, while any case that needs a different file simply passes one:

```python
from utils.configs import MlflowLoggerConfig

config = MlflowLoggerConfig.from_yaml()                      # default file
config = MlflowLoggerConfig.from_yaml("configs/other.yaml")  # this instance only
```

Classes without a `DEFAULT_CONFIG_PATH` require an explicit path.

## Greetings
A big thank you to [Giovanni Giacometti](https://github.com/GiovanniGiacometti) for creating this template and sharing it with the community. This template is a fork of his original work, which can be found at [giovannigiacometti/python-repository-template](https://github.com/GiovanniGiacometti/python-repo-template).
