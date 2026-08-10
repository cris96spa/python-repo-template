"""Render the example chart shipped with the diagrams module."""

import argparse
from pathlib import Path

import xy

CHART_NAME = "example_chart"


def build_chart():
    """Build the example line chart."""
    return xy.line_chart(xy.line([1, 2, 3, 4, 5], [120, 180, 165, 240, 310]))


def main() -> None:
    """Parse arguments and write the example chart to disk."""
    parser = argparse.ArgumentParser(description="Render the example chart.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write to.")
    parser.add_argument(
        "--format",
        choices=["png", "svg"],
        default="png",
        help="Output format.",
    )
    arguments = parser.parse_args()

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    destination = arguments.output_dir / f"{CHART_NAME}.{arguments.format}"

    chart = build_chart()
    writers = {"png": chart.to_png, "svg": chart.to_svg}
    writers[arguments.format](str(destination))


if __name__ == "__main__":
    main()
