# Nestora Builder v0.1

Nestora Builder is a guarded autonomous development agent for the Nestora AI repository.

## v0.1 goal

Automate one safe development loop:

1. Read `ROADMAP.md`, `AGENTS.md`, and architecture guidance.
2. Select one small approved task.
3. Create an `agent/<task>` feature branch from `develop`.
4. Inspect only files relevant to that task.
5. Generate and apply a change plan.
6. Run backend and frontend verification commands.
7. Retry bounded fixes when checks fail.
8. Commit only when all required checks pass.
9. Write progress to `builder/state.json`.
10. Stop before merge or deployment.

## Hard safety boundaries

- Never push directly to `main` or `develop`.
- Never merge a pull request automatically.
- Never deploy automatically.
- Never read, print, edit, or commit secrets.
- Never run destructive database commands.
- Never delete migrations or production configuration.
- Stop after the configured retry limit.
- Require an explicit approval gate for migrations, auth/security changes, billing, deployment, and destructive refactors.

## Initial operating mode

v0.1 runs in `dry_run` mode by default. It may inspect the project and produce a plan, but it will not modify application code until `mode` is deliberately changed in `builder/config.json`.

The first milestone is proving the planner, state machine, Git guardrails, and verification command detection before allowing autonomous edits.
