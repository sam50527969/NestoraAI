# Nestora Builder Rules

## Mission
Continue the Nestora roadmap autonomously in small, verifiable packages while preserving the current product architecture and keeping human control over high-risk actions.

## Task selection
- Prefer the smallest incomplete Version 1.0 roadmap item that can be implemented independently.
- Do not start more than one task at a time.
- Do not reinterpret completed roadmap items as unfinished unless tests or repository evidence show a regression.
- If requirements are materially ambiguous, stop and record `approval_required` instead of inventing product behavior.

## Coding rules
- Follow existing repository patterns before introducing new abstractions.
- Keep changes scoped to the selected task.
- Add or update tests for behavior changes.
- Preserve backwards compatibility unless the task explicitly requires otherwise.
- Do not weaken authentication, authorization, workspace isolation, validation, or tests to make checks pass.

## Git rules
- Base all work on `develop`.
- Work only on branches beginning with `agent/`.
- Never commit generated secrets, local databases, virtual environments, build output, or dependency directories.
- Never push directly to `develop` or `main`.
- Do not merge automatically.

## Verification gate
A task may be marked complete only when all configured checks pass. A failing check must trigger diagnosis and a bounded repair attempt. After the retry limit, mark the task blocked and stop.

## Mandatory approval gates
Stop before making changes involving database migrations, authentication/authorization policy, billing, production deployment, secret management, destructive data changes, or broad architectural rewrites.
