import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any, cast

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bootstrap_project.py"


def load_bootstrap_project_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("bootstrap_project", SCRIPT_PATH)
    assert spec is not None
    loader = spec.loader
    assert loader is not None

    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


bootstrap_project = cast(Any, load_bootstrap_project_module())


def write_template_repo(root: Path) -> None:
    (root / "scripts").mkdir(parents=True)
    (root / "src" / "python_starter_project").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / ".vscode").mkdir()

    (root / "src" / "python_starter_project" / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )
    (root / "src" / "python_starter_project" / "main.py").write_text(
        'def main() -> None:\n    print("Hello word!")\n',
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        "[project]\n"
        "authors = [\n"
        '    { name = "gleniosp", email = "11273108+gleniosp@users.noreply.github.com" },\n'
        "]\n"
        'name = "python-starter-project"\n'
        "\n"
        "[tool.hatch.build.targets.wheel]\n"
        'packages = ["src/python_starter_project"]\n'
        "\n"
        "[tool.pixi.pypi-dependencies]\n"
        '"python-starter-project" = { path = ".", editable = true }\n'
        "\n"
        "[tool.pixi.tasks]\n"
        'main = "python -m python_starter_project.main"\n',
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "python-starter-project python_starter_project gleniosp 11273108+gleniosp@users.noreply.github.com\n",
        encoding="utf-8",
    )
    (root / ".vscode" / "launch.json").write_text(
        '{"configurations": [{"module": "python_starter_project.main"}]}\n',
        encoding="utf-8",
    )
    (root / "pixi.lock").write_text(
        "name: python-starter-project\n",
        encoding="utf-8",
    )


def test_bootstrap_copy_rewrites_metadata_and_initializes_git(tmp_path: Path) -> None:
    source_root = tmp_path / "template"
    destination_root = tmp_path / "demo-project"
    write_template_repo(source_root)

    result = bootstrap_project.bootstrap_copy(
        source_root=source_root,
        destination_root=destination_root,
        package_name="demo_project",
        replacements=bootstrap_project.build_replacements(
            project_name="demo-project",
            package_name="demo_project",
            author_name="Jane Doe",
            author_email="jane@example.com",
        ),
        initialize_git=True,
        initial_branch="trunk",
    )

    assert result.git_initialized is True
    assert (destination_root / ".git").is_dir()
    assert (destination_root / "src" / "demo_project").is_dir()
    assert not (destination_root / "src" / "python_starter_project").exists()
    assert not (destination_root / "pixi.lock").exists()

    pyproject = (destination_root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "demo-project"' in pyproject
    assert 'packages = ["src/demo_project"]' in pyproject
    assert "Jane Doe" in pyproject
    assert "jane@example.com" in pyproject
    assert (destination_root / ".git" / "HEAD").read_text(
        encoding="utf-8"
    ) == "ref: refs/heads/trunk\n"


def test_bootstrap_in_place_rewrites_project_and_cleans_state(tmp_path: Path) -> None:
    project_root = tmp_path / "template-derived-project"
    write_template_repo(project_root)
    package_root = project_root / "src" / "python_starter_project"
    (project_root / ".pixi").mkdir()
    (project_root / ".pixi" / "state.txt").write_text(
        "template state",
        encoding="utf-8",
    )
    (project_root / ".git").mkdir()
    (project_root / ".git" / "HEAD").write_text(
        "ref: refs/heads/main\n",
        encoding="utf-8",
    )
    pycache_dir = package_root / "__pycache__"
    pycache_dir.mkdir()
    pycache_file = pycache_dir / "main.pyc"
    pycache_file.write_bytes(b"placeholder")

    result = bootstrap_project.bootstrap_in_place(
        project_root=project_root,
        package_name="demo_project",
        replacements=bootstrap_project.build_replacements(
            project_name="demo-project",
            package_name="demo_project",
            author_name="Jane Doe",
            author_email="jane@example.com",
        ),
    )

    assert result.in_place is True
    assert result.git_initialized is False
    assert (project_root / "src" / "demo_project").is_dir()
    assert not (project_root / "src" / "python_starter_project").exists()
    assert not (project_root / ".pixi").exists()
    assert not (project_root / "pixi.lock").exists()
    assert (project_root / ".git" / "HEAD").read_text(encoding="utf-8") == (
        "ref: refs/heads/main\n"
    )

    readme = (project_root / "README.md").read_text(encoding="utf-8")
    assert "demo-project" in readme
    assert "demo_project" in readme
    assert "Jane Doe" in readme
    assert "jane@example.com" in readme
