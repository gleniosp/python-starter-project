---
name: pixi-dependency-management
description: Add, remove, or update dependencies in this Pixi-managed Python project while keeping runtime and development packages in the right environments.
---

# Manage Pixi dependencies

Use this skill when changing Conda or PyPI dependencies in the project.

- Check `pyproject.toml` and `README.md` before changing dependency placement.
- Add runtime Conda packages with `pixi add PACKAGE`; add runtime PyPI packages with
  `pixi add --pypi PACKAGE`.
- Put check-only dependencies in the appropriate existing feature: `--feature lint` or
  `--feature test`. Add PyPI packages to a feature with `--feature FEATURE --pypi`.
- Use Pixi commands to change dependencies and regenerate `pixi.lock`; do not edit the
  lockfile by hand or install project dependencies directly with pip/uv. Pixi uses uv
  internally for PyPI packages.
- The lockfile records resolutions for every platform in
  `[tool.pixi.workspace].platforms`. Keep that list and the native runner matrix in
  `.github/workflows/ci.yml` aligned when changing platform support.
- Use `pixi lock --check` to confirm the lockfile matches the manifest. If a dependency
  cannot resolve for a supported target, report the affected package and platform before
  proposing to drop platform support.
