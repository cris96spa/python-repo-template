---
name: new-config
description: Add a configuration class with its YAML file and round-trip test, following the template's config conventions. Use when asked to add, define, or scaffold a config.
allowed-tools: Read, Edit, Write, Bash(uv:*), Bash(make:*)
---

# New Config

## Pick the base class

- **`YamlBaseSettings`** — one instance per process, and environment variables
  may override the YAML. Process-wide settings only, such as the log level.
- **`YamlBaseModel`** — many instances loaded from different files, never
  reading the environment. Everything else.

When in doubt use `YamlBaseModel`. Environment variables are a flat,
process-global namespace and cannot express per-instance overrides.

## Write the class

Add it to `utils/configs.py` unless it belongs to a specific package module.
Every field carries a `Field(description=...)`. Set `DEFAULT_CONFIG_PATH` only
when the config has one canonical file.

```python
class ReportConfig(YamlBaseModel):
    """Configuration for the report generator."""

    DEFAULT_CONFIG_PATH: ClassVar[Path] = Path("configs/report.yaml")

    output_dir: Path = Field(description="Directory the report is written to.")
    include_charts: bool = Field(
        description="Whether to render charts alongside the tables.",
        default=True,
    )
```

## Write the YAML

Create `configs/<name>.yaml` with every field populated, defaults included, so
the file doubles as documentation:

```yaml
output_dir: artifacts/reports
include_charts: true
```

## Write the test

Add to `tests/test_configs.py`, creating it if absent. Test that the default
path loads and that a round trip preserves the data — not that pydantic works.

```python
def test_report_config_round_trips(tmp_path):
    config = ReportConfig.from_yaml()
    destination = tmp_path / "report.yaml"

    config.to_yaml(destination)

    assert ReportConfig.from_yaml(destination) == config
```

If the class defines no `DEFAULT_CONFIG_PATH`, assert instead that `from_yaml()`
with no argument raises `ValueError`.

## Verify

```bash
uv run ruff format utils/configs.py tests/test_configs.py
make lint && make lint-doc && make test
```

## Conventions that trip people up

- Types belong in the signature, never in the docstring.
- A docstring longer than one summary line must document every parameter.
- `YamlBaseSettings` subclasses set `model_config = SettingsConfigDict(yaml_file=...)`;
  `YamlBaseModel` subclasses set `DEFAULT_CONFIG_PATH`. They are not interchangeable.
