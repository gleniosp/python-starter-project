---
name: bootstrap-project
description: Create a local copy of this Python starter template or bootstrap a repository created from it.
---

# Bootstrap a project

Use this skill when asked to create or initialize a project from this template. Read the
bootstrap options in `README.md` when the requested destination or package naming needs
special handling.

- Run `scripts/bootstrap_project.py` through the Pixi `dev` environment so it uses the
  project-supported Python: `pixi run --environment dev python scripts/bootstrap_project.py ...`.
- For a local copy, pass the project name and a new destination. The script refuses an
  existing destination; do not remove or overwrite it to make the command succeed.
- Use `--in-place` only when the user asks to bootstrap the current repository in place.
  This renames package metadata and removes generated state, including `pixi.lock`.
- Preserve the script's default fresh Git initialization unless the user asks for
  `--no-git-init`. Supply author flags only when the user provides those values; otherwise
  the script reads available Git configuration.
- Summarize the created destination and the next setup command,
  `pixi run --environment dev setup-dev`.
