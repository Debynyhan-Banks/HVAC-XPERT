# AI Handoff Instructions

## Required reading order

Before performing work:

1. Read `PROJECT_CHARTER.md`.
2. Read `CURRENT_STATE.md`.
3. Read `DECISIONS.md`.
4. Read `DATA_GOVERNANCE.md`.
5. Read `SOURCE_POLICY.md` and `VALIDATION_POLICY.md`.
6. Read the schemas and source records relevant to the task.
7. Check the worktree and preserve unrelated user changes.

## Mandatory behavior

- Never invent manufacturer data.
- Keep unknown values as `null`.
- Attach provenance to every extracted fact.
- Preserve exact model and revision boundaries.
- Treat OCR and AI output as unvalidated assertions.
- Surface source conflicts instead of silently choosing a value.
- Use manufacturer documents over inferred domain knowledge.
- Keep deterministic simulation logic separate from AI explanation.
- Update `CURRENT_STATE.md` after completing material work.
- Record cross-project architecture choices in `DECISIONS.md`.
- Record newly discovered material risks in `RISKS.md`.
- After each validated work unit, commit the intended changes and push the current branch to `origin`.
- End every handoff with `Done`, `Next`, and `Blocked` status sections.

## Prohibited behavior

- Do not guess connector pinouts, wire colors, voltages, fault logic, or sequence behavior.
- Do not infer applicability from a similar model number alone.
- Do not merge different model or document revisions.
- Do not treat confidence scores as validation.
- Do not remove source attribution or validation labels.
- Do not publish unreviewed extraction.
- Do not crawl a source unless its registry record is current and approved.
- Do not bypass authentication, terms, robots controls, or technical access controls.
- Do not publicly redistribute source diagrams or complete manuals without recorded permission.

## Task completion checklist

Before handing off work:

- Run the most specific available validation or test.
- Confirm new records conform to the canonical schemas.
- Confirm all technical assertions have provenance.
- State unresolved unknowns, conflicts, assumptions, and blockers.
- Update `CURRENT_STATE.md` with completed work and the next concrete action.
- Include exact file paths and commands needed by the next contributor.
- Inspect the staged file list and confirm that no private documents, credentials, secrets, or generated artifacts are included.
- Commit the completed work with a focused message and push the current branch to `origin`.
- Verify that the remote accepted the commit; if synchronization fails, report it as a blocker rather than claiming completion.
- When a pull request exists, include its clickable GitHub merge/review link in the final handoff.

## Repository synchronization protocol

- Canonical repository: `https://github.com/Debynyhan-Banks/HVAC-XPERT.git`.
- A work unit is complete only after its validation passes, project state is updated when material, and its intended files are committed and pushed.
- Use a focused branch and pull request for normal changes when the repository supports that workflow. The initial repository publication may establish `main` directly.
- Never bypass failed validation merely to create a commit or push.
- Never push files excluded by `.gitignore`, especially `sources/private/`, source PDFs, credentials, local environment files, or temporary extraction output.
- If GitHub authentication, network access, branch protection, or review requirements prevent a push, keep the local work intact and report the exact blocker.
- Never omit the pull-request link when a merge is pending. If work was published directly because no pull request was applicable, state that explicitly.

## Current authorized scope

Governance, schema validation, and source review preparation are authorized. Automated collection is not authorized until a source reviewer sets `approved_for_collection: true` for the exact source.
