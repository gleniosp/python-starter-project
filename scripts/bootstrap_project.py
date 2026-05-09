import argparse
import re
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

TEMPLATE_DIST_NAME = "python-starter-project"
TEMPLATE_PACKAGE_NAME = "python_starter_project"
TEMPLATE_AUTHOR_NAME = "gleniosp"
TEMPLATE_AUTHOR_EMAIL = "11273108+gleniosp@users.noreply.github.com"
DEFAULT_INITIAL_BRANCH = "main"
EXCLUDED_NAMES = {
    ".git",
    ".mypy_cache",
    ".pixi",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "pixi.lock",
}
CLEANUP_PATHS = (
    Path(".mypy_cache"),
    Path(".pixi"),
    Path(".pytest_cache"),
    Path(".ruff_cache"),
    Path("pixi.lock"),
)


class BootstrapResult(NamedTuple):
    destination_root: Path
    rewritten_files: list[Path]
    removed_paths: list[Path]
    git_initialized: bool
    in_place: bool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a new project from this repository template."
    )
    parser.add_argument(
        "project_name",
        help="Distribution name for the generated project, for example 'my-new-project'.",
    )
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        help="Directory to create for the generated project. Omit with --in-place.",
    )
    parser.add_argument(
        "--package-name",
        help=(
            "Python package name to use in src/. Defaults to a sanitized version of "
            "the project name."
        ),
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help=(
            "Rewrite the current repository in place instead of copying it. Use this "
            "after creating a new repository from a GitHub template."
        ),
    )
    parser.add_argument(
        "--author-name",
        help="Author name to write into project metadata. Defaults to git config.",
    )
    parser.add_argument(
        "--author-email",
        help="Author email to write into project metadata. Defaults to git config.",
    )
    parser.add_argument(
        "--no-git-init",
        action="store_true",
        help="Skip git initialization when copying the template to a new directory.",
    )
    parser.add_argument(
        "--initial-branch",
        default=DEFAULT_INITIAL_BRANCH,
        help="Initial branch name to use with git init.",
    )
    return parser


def resolve_destination_root(
    parser: argparse.ArgumentParser, args: argparse.Namespace, source_root: Path
) -> Path:
    if args.in_place:
        if args.destination is not None:
            parser.error("Do not pass a destination when using --in-place.")
        return source_root

    if args.destination is None:
        parser.error("destination is required unless --in-place is used.")
    destination = Path(args.destination)
    return destination.expanduser().resolve()


def normalize_project_name(project_name: str) -> str:
    value = project_name.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"[-_.]{2,}", "-", value)
    value = value.strip("-._")
    if not value:
        raise ValueError("Project name must contain at least one letter or digit.")
    return value


def normalize_package_name(project_name: str) -> str:
    value = project_name.strip().lower().replace("-", "_").replace(".", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        raise ValueError("Package name must contain at least one letter or digit.")
    if value[0].isdigit():
        value = f"_{value}"
    return value


def normalize_optional_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def get_git_config_value(source_root: Path, key: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "config", "--get", key],
            check=True,
            capture_output=True,
            cwd=source_root,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    return normalize_optional_value(completed.stdout)


def resolve_author_value(
    explicit_value: str | None, source_root: Path, git_key: str
) -> str | None:
    value = normalize_optional_value(explicit_value)
    if value is not None:
        return value
    return get_git_config_value(source_root, git_key)


def build_replacements(
    project_name: str,
    package_name: str,
    author_name: str | None,
    author_email: str | None,
) -> dict[str, str]:
    replacements = {
        TEMPLATE_DIST_NAME: project_name,
        TEMPLATE_PACKAGE_NAME: package_name,
    }
    if author_name is not None:
        replacements[TEMPLATE_AUTHOR_NAME] = author_name
    if author_email is not None:
        replacements[TEMPLATE_AUTHOR_EMAIL] = author_email
    return replacements


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDED_NAMES for part in path.parts)


def copy_template(source_root: Path, destination_root: Path) -> None:
    if destination_root.exists():
        raise FileExistsError(f"Destination already exists: {destination_root}")

    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in EXCLUDED_NAMES}

    shutil.copytree(source_root, destination_root, ignore=ignore)


def rename_package_dir(destination_root: Path, package_name: str) -> None:
    package_dir = destination_root / "src" / TEMPLATE_PACKAGE_NAME
    if not package_dir.exists():
        raise FileNotFoundError(f"Template package directory is missing: {package_dir}")
    target_dir = destination_root / "src" / package_name
    if package_dir == target_dir:
        return
    if target_dir.exists():
        raise FileExistsError(f"Target package directory already exists: {target_dir}")
    package_dir.rename(target_dir)


def rewrite_text_files(
    destination_root: Path, replacements: dict[str, str]
) -> list[Path]:
    rewritten_files: list[Path] = []
    ordered_replacements = sorted(
        replacements.items(), key=lambda item: len(item[0]), reverse=True
    )
    for path in destination_root.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        updated = content
        for source_text, replacement_text in ordered_replacements:
            updated = updated.replace(source_text, replacement_text)
        if updated == content:
            continue

        path.write_text(updated, encoding="utf-8")
        rewritten_files.append(path)

    return rewritten_files


def remove_path(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    return True


def cleanup_project_state(project_root: Path) -> list[Path]:
    removed_paths: list[Path] = []

    for relative_path in CLEANUP_PATHS:
        path = project_root / relative_path
        if remove_path(path):
            removed_paths.append(path)

    for path in sorted(project_root.rglob("__pycache__")):
        if ".git" in path.parts:
            continue
        shutil.rmtree(path)
        removed_paths.append(path)

    return removed_paths


def initialize_git_repository(destination_root: Path, initial_branch: str) -> bool:
    if (destination_root / ".git").exists():
        return False

    try:
        subprocess.run(
            ["git", "init", "--initial-branch", initial_branch],
            check=True,
            capture_output=True,
            cwd=destination_root,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git is required to initialize a repository.") from exc
    except subprocess.CalledProcessError as exc:
        error_message = exc.stderr.strip() or "git init failed."
        raise RuntimeError(error_message) from exc

    return True


def bootstrap_copy(
    source_root: Path,
    destination_root: Path,
    package_name: str,
    replacements: dict[str, str],
    initialize_git: bool,
    initial_branch: str,
) -> BootstrapResult:
    copy_template(source_root, destination_root)
    rename_package_dir(destination_root, package_name)
    rewritten_files = rewrite_text_files(destination_root, replacements)

    git_initialized = False
    if initialize_git:
        git_initialized = initialize_git_repository(destination_root, initial_branch)

    return BootstrapResult(
        destination_root=destination_root,
        rewritten_files=rewritten_files,
        removed_paths=[],
        git_initialized=git_initialized,
        in_place=False,
    )


def bootstrap_in_place(
    project_root: Path, package_name: str, replacements: dict[str, str]
) -> BootstrapResult:
    rename_package_dir(project_root, package_name)
    rewritten_files = rewrite_text_files(project_root, replacements)
    removed_paths = cleanup_project_state(project_root)
    return BootstrapResult(
        destination_root=project_root,
        rewritten_files=rewritten_files,
        removed_paths=removed_paths,
        git_initialized=False,
        in_place=True,
    )


def print_summary(
    result: BootstrapResult, project_name: str, package_name: str
) -> None:
    if result.in_place:
        print(f"Initialized project in place at {result.destination_root}")
    else:
        print(f"Created project at {result.destination_root}")

    print(f"Distribution name: {project_name}")
    print(f"Package name: {package_name}")

    if result.rewritten_files:
        print("Updated files:")
        for path in sorted(result.rewritten_files):
            print(f"  - {path.relative_to(result.destination_root)}")

    if result.removed_paths:
        print("Removed files and directories:")
        for path in sorted(result.removed_paths):
            print(f"  - {path.relative_to(result.destination_root)}")

    if result.git_initialized:
        print("Initialized a fresh git repository.")

    print("Next steps:")
    if not result.in_place:
        print(f"  cd {result.destination_root}")
    print("  pixi install")
    print("  pixi run main")
    if result.git_initialized:
        print("  git add .")
        print('  git commit -m "Initial commit"')


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    source_root = Path(__file__).resolve().parents[1]
    destination_root = resolve_destination_root(parser, args, source_root)
    project_name = normalize_project_name(args.project_name)
    package_name = (
        normalize_package_name(args.package_name)
        if args.package_name
        else normalize_package_name(project_name)
    )
    author_name = resolve_author_value(args.author_name, source_root, "user.name")
    author_email = resolve_author_value(args.author_email, source_root, "user.email")
    replacements = build_replacements(
        project_name=project_name,
        package_name=package_name,
        author_name=author_name,
        author_email=author_email,
    )

    if args.in_place:
        result = bootstrap_in_place(destination_root, package_name, replacements)
    else:
        result = bootstrap_copy(
            source_root=source_root,
            destination_root=destination_root,
            package_name=package_name,
            replacements=replacements,
            initialize_git=not args.no_git_init,
            initial_branch=args.initial_branch,
        )

    print_summary(result, project_name, package_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
