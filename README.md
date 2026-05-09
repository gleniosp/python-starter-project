# Python Project Template

This repository can act as a base project for new Python projects.

## Generate a new project

From the root of this repository, run:

```bash
pixi run python scripts/bootstrap_project.py my-new-project ../my-new-project
```

The script will:

- copy this repository into the destination directory
- skip local state such as `.git`, `.pixi`, caches, and `pixi.lock`
- rename the Python package under `src/`
- rewrite project references in text files such as `pyproject.toml` and `.vscode/launch.json`
- initialize a fresh git repository by default

By default, the Python package name is derived from the project name.

- `my-new-project` becomes `my_new_project`
- names that start with a digit are prefixed with `_` so the package stays importable

By default, the author name and email are taken from your git config when available.
You can override them explicitly:

```bash
pixi run python scripts/bootstrap_project.py my-new-project ../my-new-project \
	--author-name "Jane Doe" \
	--author-email "jane@example.com"
```

If you want to override the package name, pass `--package-name`:

```bash
pixi run python scripts/bootstrap_project.py 3d-demo ../3d-demo --package-name three_d_demo
```

If you do not want a new git repository to be created, pass `--no-git-init`.

## Use as a GitHub template

This repository now includes a GitHub Actions workflow in `.github/workflows/ci.yml`
that validates both the template itself and a freshly generated project.

To use the repository as a GitHub template:

1. In GitHub, enable the repository's `Template repository` setting.
2. Create a new repository from this template.
3. Clone the new repository locally.
4. Run the bootstrap script in place:

```bash
pixi run python scripts/bootstrap_project.py my-new-project --in-place \
	--author-name "Jane Doe" \
	--author-email "jane@example.com"
```

The in-place mode renames the package, rewrites metadata, and removes generated state
such as `pixi.lock` and `.pixi` so the new repository can regenerate its own environment.

## Suggested workflow

1. Keep this repository as your template/base project.
2. For a local copy, run the bootstrap script with a destination path.
3. For a GitHub template repo, clone the new repo and run the bootstrap script with `--in-place`.
4. Run `pixi install`.
5. Start working in the new project.

## What to rename in the generated project

The bootstrap script already updates the package and project names for the current layout.
If you later add more project-specific strings, keep using the same canonical template names inside this repo:

- distribution name: `python-starter-project`
- package name: `python_starter_project`

That keeps the bootstrap rewrite simple and predictable.
