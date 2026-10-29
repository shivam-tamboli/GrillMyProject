# CLAUDE.md

GrillMyProject is an AI mock interview platform. See `SYSTEM_DESIGN.md` for the design. The backend lives in `backend/` (FastAPI, PostgreSQL, SQLAlchemy).

## Workflow

Every change follows the PR workflow, in this order:

1. Create an issue
2. Create a branch for the issue
3. Write the code
4. Open a PR
5. Merge the PR
6. Delete the branch

If the PR has merge conflicts, resolve them before merging. The PR body must include `Closes #<issue>` so the issue closes when it merges.

## Issues

- Write issues in clear, simple English. Keep them descriptive.
- Always assign the issue to me (`--assignee @me`).
- Always use labels. If a label does not exist, create it first.
- Use this format:

```
## What
## Why
## Tasks
## Done When
## Out of Scope
```

## Branches

Name the branch after the issue, e.g. `feature/2-fastapi-postgres-setup`. Use `feature/`, `fix/` or `docs/` as the prefix.

## Commits

- Short, plain, developer style. Lowercase is fine.
- Write them the way a developer would. Nothing that reads like AI wrote it.
- Never add `Co-Authored-By` lines or any contributor lines. Do not add Claude as a contributor anywhere.
