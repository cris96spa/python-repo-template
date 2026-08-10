import subprocess
from pathlib import Path

import pytest

from utils.post_checkout import dependency_files_changed, main

BRANCH_CHECKOUT = "1"
FILE_CHECKOUT = "0"


def run_git(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture(autouse=True)
def clear_pre_commit_environment(monkeypatch):
    monkeypatch.delenv("PRE_COMMIT_FROM_REF", raising=False)
    monkeypatch.delenv("PRE_COMMIT_TO_REF", raising=False)
    monkeypatch.delenv("PRE_COMMIT_CHECKOUT_TYPE", raising=False)


@pytest.fixture
def repository(tmp_path, monkeypatch):
    run_git(tmp_path, "init", "-q")
    run_git(tmp_path, "config", "user.email", "test@example.com")
    run_git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
    (tmp_path / "README.md").write_text("first\n")
    run_git(tmp_path, "add", "-A")
    run_git(tmp_path, "commit", "-q", "-m", "chore: first")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_detects_a_changed_dependency_file(repository):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")

    assert dependency_files_changed(before, after) == ["pyproject.toml"]


def test_ignores_unrelated_changes(repository):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "README.md").write_text("second\n")
    run_git(repository, "commit", "-q", "-am", "docs: edit")
    after = run_git(repository, "rev-parse", "HEAD")

    assert dependency_files_changed(before, after) == []


def test_file_checkout_prints_nothing(repository, capsys):
    head = run_git(repository, "rev-parse", "HEAD")

    assert main([head, head, FILE_CHECKOUT]) == 0
    assert capsys.readouterr().out == ""


def test_branch_checkout_with_a_changed_dependency_file_prints_a_notice(repository, capsys):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")

    assert main([before, after, BRANCH_CHECKOUT]) == 0
    assert "make dev" in capsys.readouterr().out


def test_missing_arguments_exit_zero_without_raising(capsys):
    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_unknown_revisions_exit_zero_without_raising(repository, capsys):
    assert main(["deadbeef", "cafebabe", BRANCH_CHECKOUT]) == 0
    assert capsys.readouterr().out == ""


def test_branch_checkout_via_environment_prints_a_notice(repository, monkeypatch, capsys):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")
    monkeypatch.setenv("PRE_COMMIT_FROM_REF", before)
    monkeypatch.setenv("PRE_COMMIT_TO_REF", after)
    monkeypatch.setenv("PRE_COMMIT_CHECKOUT_TYPE", BRANCH_CHECKOUT)

    assert main([]) == 0
    assert "make dev" in capsys.readouterr().out


def test_file_checkout_type_via_environment_prints_nothing(repository, monkeypatch, capsys):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")
    monkeypatch.setenv("PRE_COMMIT_FROM_REF", before)
    monkeypatch.setenv("PRE_COMMIT_TO_REF", after)
    monkeypatch.setenv("PRE_COMMIT_CHECKOUT_TYPE", FILE_CHECKOUT)

    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_argv_takes_precedence_over_conflicting_environment_variables(
    repository, monkeypatch, capsys
):
    before = run_git(repository, "rev-parse", "HEAD")
    (repository / "pyproject.toml").write_text("[project]\nname = 'demo2'\n")
    run_git(repository, "commit", "-q", "-am", "chore: bump")
    after = run_git(repository, "rev-parse", "HEAD")
    monkeypatch.setenv("PRE_COMMIT_FROM_REF", before)
    monkeypatch.setenv("PRE_COMMIT_TO_REF", after)
    monkeypatch.setenv("PRE_COMMIT_CHECKOUT_TYPE", FILE_CHECKOUT)

    assert main([before, after, BRANCH_CHECKOUT]) == 0
    assert "make dev" in capsys.readouterr().out
