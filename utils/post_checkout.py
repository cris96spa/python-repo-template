"""Post-checkout hook that flags dependency drift after a branch switch."""

import subprocess
import sys
from collections.abc import Sequence

from utils.console import STYLE_HEADER, console

DEPENDENCY_FILES = ("pyproject.toml", "uv.lock")
BRANCH_CHECKOUT_FLAG = "1"


def dependency_files_changed(previous: str, current: str) -> list[str]:
    """List the dependency files that differ between two revisions.

    Args:
        previous: Revision checked out before the switch.
        current: Revision checked out after the switch.

    Returns:
        The changed dependency file paths, empty when nothing relevant changed.
    """
    completed = subprocess.run(
        ["git", "diff", "--name-only", previous, current, "--", *DEPENDENCY_FILES],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line]


def main(argv: Sequence[str]) -> int:
    """Print a notice when a branch switch changed the dependency files.

    Args:
        argv: The previous revision, the new revision, and git's branch-checkout flag.

    Returns:
        Always zero, so a checkout never looks broken because of this hook.
    """
    if len(argv) < 3 or argv[2] != BRANCH_CHECKOUT_FLAG:
        return 0

    try:
        changed = dependency_files_changed(argv[0], argv[1])
    except (subprocess.CalledProcessError, OSError):
        return 0

    if changed:
        console.print(
            f"[bold {STYLE_HEADER}]{', '.join(changed)} changed on this branch — "
            f"run `make dev` to resync dependencies.[/]"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
