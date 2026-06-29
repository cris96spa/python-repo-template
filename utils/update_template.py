import argparse
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path
from textwrap import dedent

DEFAULT_TEMPLATE_URL = "git@github.com:cris96spa/python-repo-template.git"
DEFAULT_TEMPLATE_BRANCH = "main"
UPDATE_BRANCH_NAME = "update-template"


def main(
    pyproject_path: str,
    template_reference_commit: str | None,
    template_remote_url: str,
    template_target_branch: str,
) -> None:
    """Main function to update template."""
    print(
        f"Starting template update. Template target branch: {template_target_branch}, "
        f"template reference commit: {template_reference_commit}"
    )
    print("Ensuring uv is already installed")
    ensure_uv_is_installed()

    print("Ensuring no previous graft commits exist")  # would break first project commit detection
    ensure_no_previous_graft_commits_exist()

    print("Getting project info: default branch and first project commit")
    project_base_branch = get_project_default_branch()
    print(f"Project default branch: {project_base_branch}")
    first_project_commit = get_first_project_commit(project_base_branch)

    print("Ensuring current branch correctness")
    ensure_current_branch_correctness(project_base_branch)

    if check_remote_exists("template"):
        print("Template remote already exists, skipping addition")
    else:
        print("Adding template remote")
        ret_code = subprocess.call(["git", "remote", "add", "template", template_remote_url])
        exit_on_nonzero_return_code(
            ret_code,
            "ERROR: git remote add command failed while adding template remote.",
        )

    merge_return_code = 1  # needed to check in finally block if merge was successful

    try:  # ensure cleanup of "template" remote
        git_set_remote_to_be_readonly("template", template_target_branch)
        fetch_return_code = subprocess.call(["git", "fetch", "template", template_target_branch])
        exit_on_nonzero_return_code(
            fetch_return_code,
            "ERROR: git fetch from the template remote failed.",
        )

        if not template_reference_commit:  # if no template reference commit specified, guess it
            print("No template reference commit specified, guessing the correct one")
            first_commit_date = get_command_output(
                f"git log --reverse --format=%cd --date=iso origin/{project_base_branch}"
            ).split("\n")[0]
            print(f"First commit date is: {first_commit_date}")
            template_reference_commit = get_command_output(
                f"git rev-list -n 1 --before='{first_commit_date}' template/{template_target_branch}"  # noqa: E501
            )
            print(f"Guessed template reference commit: {template_reference_commit}")

        print(
            "Linking project git graph with template git graph: a graft commit will be added to "
            f"pretend that project commit ({first_project_commit}) was committed as a child"
            f" of template reference commit ({template_reference_commit}). This graft commit is "
            "supposed to be temporary and will be removed by the script after the update."
        )
        create_graft_commit(
            child_commit=first_project_commit, parent_commit=template_reference_commit
        )

        try:
            print("Merging changes from template")
            merge_return_code = subprocess.call(
                [
                    "git",
                    "merge",
                    "--squash",
                    "--no-commit",
                    f"template/{template_target_branch}",
                ]
            )

            new_template_reference_commit = get_command_output(
                f"git rev-parse template/{template_target_branch}"
            )
            print(
                "Updating pyproject.toml with new template reference commit: "
                + new_template_reference_commit
            )
            update_template_references_in_pyproject(
                pyproject_path=pyproject_path,
                template_reference_commit=new_template_reference_commit,
                template_target_branch=template_target_branch,
            )
            print("Adding updated pyproject.toml to the staged changes")
            ret_code = subprocess.call(["git", "add", pyproject_path])
            exit_on_nonzero_return_code(
                ret_code,
                "ERROR: git add command failed while adding updated pyproject.toml.",
            )
        finally:
            print("Cleaning up temporary graft commit and remote")

            replace_delete_return_code = subprocess.call(
                [
                    "git",
                    "replace",
                    "-d",
                    first_project_commit,
                ]
            )
            exit_on_nonzero_return_code(
                replace_delete_return_code,
                (
                    "WARNING: cleanup of temporary graft commit failed. Please "
                    "remove graft commits manually to avoid pushing them on 'git push'. "
                    "You can use 'git replace --list' to display replace refs, "
                    "and then 'git replace -d <commit>' to delete them."
                ),
            )

    finally:
        remote_remove_return_code = subprocess.call(["git", "remote", "remove", "template"])
        exit_on_nonzero_return_code(
            remote_remove_return_code,
            (
                "WARNING: git remote remove command failed during cleanup. "
                "Please remove it manually."
            ),
        )
        exit_on_nonzero_return_code(
            merge_return_code,
            (
                "Template update completed with merge conflicts: resolve them manually, then "
                "commit and restart the update_template script."
            ),
        )
        # merge successful, no manual intervention needed
        if not is_git_staging_area_empty():
            # if there are staged changes, they are files added by this script, so commit them
            print("Committing automatically edited files")
            commit_return_code = subprocess.call(
                [
                    "git",
                    "commit",
                    "-m",
                    "chore: update_template auto-commit",
                ]
            )
            exit_on_nonzero_return_code(
                commit_return_code, "ERROR: git commit command failed while committing."
            )

        ret = subprocess.call(["git", "push", "--set-upstream", "origin", UPDATE_BRANCH_NAME])
        if ret != 0:
            print(
                "Template update completed successfully, but git push failed. Please push manually."
            )
            sys.exit(1)
        else:
            print("Template update completed successfully!")


def ensure_uv_is_installed() -> None:
    """Ensure uv is installed."""
    uv_found = True
    try:
        subprocess.call(["uv", "--version"])
    except FileNotFoundError:
        uv_found = False

    if uv_found:
        print("uv is already installed.")
        return

    print("uv is not installed.")
    uv_installation_command = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    if sys.platform == "win32":
        uv_installation_command = (
            'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
        )
    answer = None
    while answer not in ("y", "n", "no", "yes"):
        answer = (
            input("uv is required to manage dependencies. Do you want to install uv now? (Y/n): ")
            .strip()
            .lower()
        )
        if answer == "":
            answer = "y"
    if answer[0] == "n":
        print("uv installation declined. Please install uv manually and try again.")
        sys.exit(1)
    print("Installing uv")
    ret = subprocess.call(uv_installation_command, shell=True)
    if ret != 0:
        print("Failed to install uv. Please install it manually and try again.")
        sys.exit(1)
    print(
        "uv installed successfully. Please restart your terminal (or just add uv to your PATH)"
        " and try again the update."
    )
    sys.exit(0)


def ensure_no_previous_graft_commits_exist():
    graft_commits = get_command_output("git replace --list").strip().splitlines()
    if not graft_commits:
        return  # no graft commits exist, all good
    # existing graft commits found, ask user to remove them
    answer = None
    while answer not in ("y", "n", "no", "yes"):
        answer = (
            input(
                f"Previous graft commits detected in the repository: {graft_commits}. "
                "These would interfere with the template update process. "
                "Do you wish to remove all of them? (y/N): "
            )
            .strip()
            .lower()
        )
        if answer == "":
            answer = "n"
    if answer[0] == "y":
        failed_removals = []
        for graft_commit in graft_commits:
            print(f"Removing graft commit: {graft_commit}")
            remove_return_code = subprocess.call(["git", "replace", "-d", graft_commit])
            if remove_return_code != 0:
                failed_removals.append(graft_commit)
        if failed_removals:
            print(
                f"Failed to remove graft commits: {failed_removals}. "
                "Please remove graft commits manually and try again."
            )
            sys.exit(1)
    else:
        print("Please remove the graft commits manually and try again.")
        sys.exit(1)


def get_project_default_branch() -> str:
    """Determine the project's default branch.

    Reads the branch that ``origin/HEAD`` points to, falling back to the
    currently checked-out branch when ``origin/HEAD`` is not set.

    Returns:
        The name of the project's default branch.
    """
    try:
        ref = get_command_output("git symbolic-ref refs/remotes/origin/HEAD")
    except subprocess.CalledProcessError:
        return get_current_git_branch()
    return ref.rsplit("/", 1)[-1]


def get_first_project_commit(project_base_branch: str) -> str:
    try:
        first_project_commit = get_command_output(
            f"git rev-list --max-parents=0 --first-parent origin/{project_base_branch}"
        )
    except subprocess.CalledProcessError:
        first_project_commit = ""
    if not first_project_commit:
        print(
            f"Error: Could not determine the first commit of the project on "
            f"'origin/{project_base_branch}'. Ensure the branch exists and is pushed to origin."
        )
        sys.exit(1)
    return first_project_commit


def get_command_output(command: str) -> str:
    """Get output from a command.

    Args:
        command: The command to execute.

    Returns:
        The stdout output of the command as a stripped string.
    """
    result = subprocess.check_output(shlex.split(command)).decode().strip()
    return result


def ensure_current_branch_correctness(project_base_branch: str):
    """If this function completes successfully, the current branch will be UPDATE_BRANCH_NAME.

    If current branch is not already UPDATE_BRANCH_NAME, first ensure we are on a clean, up-to-date
    project base branch, then create and checkout a new temporary branch named UPDATE_BRANCH_NAME.
    """
    branch = get_current_git_branch()
    if branch == UPDATE_BRANCH_NAME:
        print(f"Already on '{UPDATE_BRANCH_NAME}' branch, no need to change branch.")
        ensure_current_branch_is_clean()
        return

    print(
        f"Current active branch is {branch}, not {UPDATE_BRANCH_NAME}: the project base branch "
        f"will be updated and used to create a new temporary branch {UPDATE_BRANCH_NAME}."
    )
    ensure_current_branch_is_project_base(project_base_branch)
    ensure_current_branch_is_clean()
    ensure_current_branch_is_updated()

    print(f"Creating temporary branch '{UPDATE_BRANCH_NAME}'")
    result = subprocess.run(["git", "checkout", "-b", UPDATE_BRANCH_NAME])
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        print(
            f"Failed to create temporary branch {UPDATE_BRANCH_NAME}, "
            f"please manually remove any existing {UPDATE_BRANCH_NAME} branch."
        )
        sys.exit(1)


def get_current_git_branch() -> str:
    """Get the current git branch name.

    Returns:
        The name of the current git branch.
    """
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()
    return branch


def ensure_current_branch_is_project_base(project_base_branch: str):
    """Ensure the current branch is the project base branch."""
    branch = get_current_git_branch()
    if branch != project_base_branch:
        print(
            f"to continue, you should be on '{project_base_branch}' branch: "
            "change branch and try again"
        )
        sys.exit(1)


def ensure_current_branch_is_clean():
    if not is_git_staging_area_empty():
        print("to continue, there must be no staged file: clear stage and try again")
        sys.exit(1)


def is_git_staging_area_empty() -> bool:
    """Check if git staging area is empty.

    Returns:
        True if the staging area has no staged changes, False otherwise.
    """
    ret = subprocess.call(["git", "diff", "--staged", "--quiet"])
    is_empty = ret == 0
    return is_empty


def ensure_current_branch_is_updated():
    ret = subprocess.call(["git", "pull"])
    if ret != 0:
        print("git pull did not run successfully, aborting")
        sys.exit(1)


def check_remote_exists(remote_name: str) -> bool:
    """Check if a git remote exists.

    Args:
        remote_name: The name of the remote to check.

    Returns:
        True if the remote exists, False otherwise.
    """
    try:
        return_code = subprocess.call(["git", "remote", "get-url", remote_name])
    except subprocess.CalledProcessError:
        return False
    return return_code == 0


def exit_on_nonzero_return_code(return_code: int, error_message: str) -> None:
    if return_code != 0:
        print(error_message)
        sys.exit(1)


def git_set_remote_to_be_readonly(remote_name: str, branch_name: str) -> None:
    subprocess.call(["git", "remote", "set-url", "--push", remote_name, "DISABLE"])
    subprocess.call(
        [
            "git",
            "config",
            f"remote.{remote_name}.fetch",
            f"+refs/heads/{branch_name}:refs/remotes/{remote_name}/{branch_name}",
        ]
    )


def create_graft_commit(child_commit: str, parent_commit: str) -> None:
    """Create a graft commit so that child_commit appears to descend from parent_commit."""
    replace_graft_return_code = subprocess.call(
        [
            "git",
            "replace",
            "--graft",
            child_commit,
            parent_commit,
        ]
    )
    if replace_graft_return_code != 0:
        print("ERROR: creation of graft commit failed.")
        sys.exit(1)


def update_template_references_in_pyproject(
    pyproject_path: str, template_reference_commit: str, template_target_branch: str
) -> None:
    """Update the template_commit in the pyproject.toml file."""
    content = Path(pyproject_path).read_text()
    # unfortunately, there is no obvious way to write the toml back, it has to be done manually

    if not content.endswith("\n"):
        content += "\n"

    new_template_section = dedent(f'''\
        [tool.template]
        template_commit = "{template_reference_commit}"
        template_branch = "{template_target_branch}"
        ''')

    section_identifier = "[tool.template]"
    if section_identifier not in content:
        # if [tool.template] section doesn't exists yet, add it at the end
        content += f"\n{new_template_section}"
        updated_content = content
    else:
        # the idea is to erase the existing template_commit section and replace it with the new one
        section_start = content.index(section_identifier)
        # find the end of the [tool.template] section
        next_section_match = re.search(
            r"^\[.*\]", content[section_start + len(section_identifier) :], re.M
        )
        # replace the whole section
        section_length = (
            next_section_match.start() if next_section_match else len(content) - section_start
        )
        updated_content = (
            content[:section_start]
            + new_template_section
            + "\n"
            + content[section_start + len(section_identifier) + section_length :]
        )

    # Write the updated content back to the file
    with open(pyproject_path, "w") as f:
        f.write(updated_content)

    print(
        f"Updated template reference commit to {template_reference_commit} and "
        f"template target branch to {template_target_branch}."
    )


def get_template_info_from_pyproject(
    pyproject_path: str,
) -> tuple[str | None, str | None]:
    """Get template reference commit and target branch from pyproject.toml.

    Args:
        pyproject_path: path to the pyproject.toml file

    Returns:
        A tuple of (template_reference_commit, template_target_branch), either of which may be None.
    """
    toml = tomllib.loads(Path(pyproject_path).read_text())
    template_properties = toml.get("tool", {}).get("template")

    if not template_properties:
        print("Info: [tool.template] section not found in pyproject.toml.")
        return None, None

    template_reference_commit = template_properties.get("template_commit")
    template_target_branch = template_properties.get("template_branch")
    return template_reference_commit, template_target_branch


def get_available_template_branches(template_url: str) -> list[str]:
    """Get the available template branches.

    Args:
        template_url: The URL of the template repository.

    Returns:
        A list of branch names available in the template repository.
    """
    try:
        result = (
            subprocess.check_output(["git", "ls-remote", "--heads", template_url]).decode().strip()
        )
    except subprocess.CalledProcessError:
        print(
            "Error: Unable to fetch branches from the template repository. "
            f"Please check the authentication for {template_url}"
        )
        sys.exit(1)
    branches = []
    for line in result.splitlines():
        match = re.match(r"^.*refs/heads/(.+)$", line)
        if match:
            branches.append(match.group(1))
    return branches


if __name__ == "__main__":
    # read default properties from [tool.template] section of pyproject.toml
    pyproject_path = "pyproject.toml"
    default_template_commit, template_branch_from_toml = get_template_info_from_pyproject(
        pyproject_path
    )
    default_template_branch = template_branch_from_toml or DEFAULT_TEMPLATE_BRANCH

    parser = argparse.ArgumentParser(description="Update project from template repository.")
    parser.add_argument(
        "-u",
        "--template-url",
        type=str,
        default=DEFAULT_TEMPLATE_URL,
        help=f'URL of the template repository. Default: "{DEFAULT_TEMPLATE_URL}".',
    )
    parser.add_argument(
        "-b",
        "--branch",
        type=str,
        default=default_template_branch,
        help="Template branch to target for the update: "
        "latest changes from this template branch will be downloaded. "
        f'Default: "{default_template_branch}".',
    )
    parser.add_argument(
        "-c",
        "--commit",
        type=str,
        default=default_template_commit,
        help="Template commit to use as reference: "
        "project will be treated as it was created from this template commit. "
        f'Default: "{default_template_commit}".',
    )

    args = parser.parse_args()

    available_branches = get_available_template_branches(args.template_url)
    if len(available_branches) == 0:
        print("Error: No branches found in the template repository.")
        sys.exit(1)

    # check the correctness of the template_branch
    if args.branch not in available_branches:
        print(
            f"Error: The specified template branch '{args.branch}' is not available. "
            f"Available branches are: {', '.join(available_branches)}."
        )
        sys.exit(1)

    main(
        pyproject_path=pyproject_path,
        template_reference_commit=args.commit,
        template_remote_url=args.template_url,
        template_target_branch=args.branch,
    )
