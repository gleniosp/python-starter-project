# Agent instructions

This repository is a reusable Python project template, so changes may also affect
projects generated from it.

- Use Pixi with Python 3.14.x. Run development commands in `dev`; `default` is the
  runtime environment.
- Put runtime dependencies in the default feature and development tools in the existing
  `test` or `lint` features. Use Pixi to update `pixi.lock`.
- Keep `[tool.pixi.workspace].platforms` and the native-runner matrix in
  `.github/workflows/ci.yml` aligned.
- The distribution name `python-starter-project` and package name
  `python_starter_project` are bootstrap placeholders. Update the bootstrap script and
  its tests if those canonical names change.
- Follow `README.md` for setup, dependency, and bootstrap workflows.
