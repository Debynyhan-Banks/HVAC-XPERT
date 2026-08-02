# Contributing

## Before starting

Read the governance files listed in `README.md`, review `CURRENT_STATE.md`, and confirm the source and model revision are in scope.

## Change requirements

- Keep changes focused and reversible.
- Preserve stable identifiers and source attribution.
- Add or update tests for validation, normalization, or simulator behavior.
- Include migration notes for schema changes.
- Record architecture decisions that affect multiple modules.
- Never add secrets, credentials, unlicensed source binaries, or personal data.

## Data contributions

Every technical assertion must conform to `schemas/provenance.schema.json`. Manual knowledge is not exempt from provenance: identify the reviewer, evidence, date, and validation level.

Do not commit manufacturer documents until source storage, access, retention, and licensing are approved. Golden-document fixtures must be legally approved, minimal, access-controlled when needed, and accompanied by expected structured output.

## Review expectations

Reviewers check technical applicability, model and revision boundaries, provenance coverage, schema validity, source permissions, safety impact, and regression results.

## Completion

Update `CURRENT_STATE.md` whenever work changes the project phase, completed deliverables, blockers, or next action.

After validation, inspect the staged file list, commit the completed work, and push the current branch to `origin`. Do not stage private source documents, credentials, local environment files, or temporary output. Prefer a focused branch and pull request for normal changes. A synchronization failure is a blocker and must be reported explicitly.

Every completion report must state:

- `Done`: what was completed, validated, committed, and pushed.
- `Next`: the immediate next work unit.
- `Blocked`: decisions, permissions, reviews, or synchronization failures preventing progress.
