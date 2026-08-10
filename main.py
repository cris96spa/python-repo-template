import argparse
import logging

from python_repo_template.func import random_sum
from utils.console import (
    metrics_panel,
    new_progress_bar,
    section_header,
    summary_panel,
    two_column_panel,
)
from utils.logger import setup_logger

SAMPLE_COUNT = 5

logger = logging.getLogger(__name__)


def main(number: int) -> None:
    """Draw random sums for the given number and report them through the console helpers.

    Args:
        number: The number each random draw is added to.
    """
    section_header("Random sum demo")
    summary_panel(
        {"Input number": number, "Samples": SAMPLE_COUNT},
        title="Run configuration",
    )

    samples: list[int] = []
    with new_progress_bar() as progress:
        task = progress.add_task("sampling", total=SAMPLE_COUNT)
        for _ in range(SAMPLE_COUNT):
            samples.append(random_sum(number))
            progress.advance(task)

    logger.info("Drew %d samples", SAMPLE_COUNT)

    metrics_panel(
        {
            "min": min(samples),
            "mean": sum(samples) / len(samples),
            "max": max(samples),
        }
    )
    two_column_panel(
        {"Input": str(number), "Samples": ", ".join(str(sample) for sample in samples)},
        title="Draws",
    )


if __name__ == "__main__":
    setup_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("--number", type=int, required=True, help="Input number")
    main(parser.parse_args().number)
