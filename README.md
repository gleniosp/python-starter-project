# Python Project Template

This repository can act as a base for new Python projects.

## Suggested workflow

1. Create a project from this template: make a local copy with the bootstrap script, or
   create a GitHub repository from the template and bootstrap it in place.
2. In the new project, run `pixi run --environment dev setup-dev` to prepare the
   development environment and install its Git hook.
3. Develop and run checks in `dev`; use `default` as the production runtime environment.

The two ways to create a project are described below.

## Generate a local project

From the root of this repository, run:

```bash
pixi run --environment dev python scripts/bootstrap_project.py my-new-project ../my-new-project
```

The script copies the repository to the destination, skips local state such as `.git`,
`.pixi`, caches, and `pixi.lock`, renames the Python package under `src/`, rewrites
project references in text files such as `pyproject.toml` and `.vscode/launch.json`, and
initializes a fresh Git repository by default.

The package name is derived from the project name: `my-new-project` becomes
`my_new_project`. Names that start with a digit are prefixed with `_` so the package
stays importable.

By default, the author name and email come from your Git config when available. Override
them with `--author-name` and `--author-email`:

```bash
pixi run --environment dev python scripts/bootstrap_project.py my-new-project ../my-new-project \
	--author-name "Jane Doe" \
	--author-email "jane@example.com"
```

To choose a different package name, pass `--package-name`:

```bash
pixi run --environment dev python scripts/bootstrap_project.py 3d-demo ../3d-demo --package-name three_d_demo
```

Pass `--no-git-init` if you do not want the script to initialize a Git repository.

## Use as a GitHub template

This repository includes a GitHub Actions workflow in `.github/workflows/ci.yml` that
validates the template and a freshly generated project.

To use the repository as a GitHub template:

1. In GitHub, enable the repository's `Template repository` setting.
2. Create a new repository from this template and clone it locally.
3. Run the bootstrap script in place:

```bash
pixi run --environment dev python scripts/bootstrap_project.py my-new-project --in-place \
	--author-name "Jane Doe" \
	--author-email "jane@example.com"
```

In-place mode renames the package, rewrites metadata, and removes generated state such as
`pixi.lock` and `.pixi`, so the new repository can regenerate its own environment.

## Generated project naming

The bootstrap script updates the package and project names for the current layout. When
adding files with project-specific strings, keep these canonical names in the template so
the script can rewrite them:

- Distribution name: `python-starter-project`
- Package name: `python_starter_project`

Keeping these names consistent makes the bootstrap rewrite predictable.

## Pixi environments and dependencies

The project supports Python 3.14.x and selects the regular CPython build. `pixi.lock`
records exact resolved versions, including the Python patch release.

The `default` environment contains Python, the project, and runtime dependencies; use it
for production. The `dev` environment adds Ruff, mypy, pytest, and prek for local
development and checks.

Use Pixi to manage both Conda and PyPI packages. Conda often provides ready-to-use native
or GPU builds for scientific libraries such as PyTorch; add their channels in
`[tool.pixi.workspace].channels` when needed. Pixi uses uv to resolve and install PyPI
packages.

Add runtime packages to the default feature, shared by `default` and `dev`. Add
development-only packages to a feature included in `dev`, such as `test` or `lint`:

```bash
pixi add pytorch                         # Conda, runtime
pixi add --pypi requests                 # PyPI, runtime
pixi add --feature test pytest-timeout    # Conda, test environment
pixi add --feature test --pypi pytest-cov # PyPI, test environment
```

`pixi add` updates `pyproject.toml` and `pixi.lock`. See the [Pixi dependency
commands](https://pixi.sh/latest/reference/cli/pixi/add/) for more options.

Hook definitions live in [`prek.toml`](prek.toml). The `setup-dev` task prepares the
development environment and installs the Git hook, which runs the configured hooks on
staged files at commit time. To run them on all tracked files:

```bash
pixi run --environment dev hooks
```

The hooks cover file hygiene and Ruff formatting/linting. Mypy and tests remain separate
commands and CI checks, so commits do not run the full test suite.

Set up and run the local development environment with:

```bash
pixi run --environment dev setup-dev
pixi run --environment dev main
pixi run --environment dev hooks
pixi run --environment dev mypy
pixi run --environment dev test
```

Set up and run the production runtime environment with:

```bash
pixi install --environment default
pixi run --environment default main
```
