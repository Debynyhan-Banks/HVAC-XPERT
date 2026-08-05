# P-001 Ten-Minute Manual Entry

## Outcome

P-001 adds one private localhost workflow for recording an equipment identity, fault code, measurement, or diagnostic branch. Each submission retains exact equipment applicability, private manual or field context, owner confidence, safety category, and a fail-closed guidance status.

The workflow does not publish records, copy source content into Git, search prior entries, create a public listener, or activate a deterministic diagnostic rule automatically.

## Access checklist

| Requirement | P-001 decision |
| --- | --- |
| Documents or evidence | An existing private manual reference with page number, or private field context supplied by the owner |
| Owner technical decisions | Entry type, exact model, revision applicability, evidence context, confidence, and safety category |
| API, cloud, database, or hardware | None |
| Credentials | None |
| Paid services or material cost | None |
| Privacy boundary | Generated records remain under ignored `knowledge-base/private/personal-entries/` storage |
| Source-rights boundary | Store concise owner-authored facts and references; do not copy manual pages, diagrams, or long source wording into Git |
| Acceptance boundary | Owner verifies that one representative entry can be completed quickly and that blocked/eligible status is understandable |
| Current blocker | No implementation blocker; owner acceptance remains required before P-001 is complete |

## Entry contract

Every record contains:

- one entry kind: `EQUIPMENT`, `FAULT`, `MEASUREMENT`, or `DIAGNOSTIC_BRANCH`;
- manufacturer, brand, exact model number, and revision applicability;
- one owner-authored title and kind-specific details;
- either a private document identifier and positive page number or private field context;
- one personal confidence state: `UNVERIFIED`, `MANUAL_CONFIRMED`, `FIELD_CONFIRMED`, or `CONFLICTED`;
- one safety category, with non-actionable equipment and fault references kept separate from actionable measurement and branch entries;
- a derived guidance status; and
- immutable creation identity and timestamps.

Confirmed records require exact revision applicability. `MANUAL_CONFIRMED` requires manual evidence, and `FIELD_CONFIRMED` requires field evidence. Confirmed actionable entries require a specific safety category.

## Guidance boundary

| Guidance status | Meaning |
| --- | --- |
| `BLOCKED_UNVERIFIED` | Draft only; cannot drive guidance |
| `BLOCKED_CONFLICTED` | Conflicting evidence; cannot drive guidance |
| `BLOCKED_REVISION_UNKNOWN` | Exact revision is missing; cannot drive guidance |
| `BLOCKED_SAFETY_UNKNOWN` | Actionable safety boundary is incomplete; cannot drive guidance |
| `REFERENCE_ONLY_CONFIRMED` | Confirmed equipment or fault reference, but not an actionable rule |
| `ELIGIBLE_FOR_RULE_REVIEW` | Confirmed actionable entry may be translated into a deterministic rule in a separate reviewed step |

All P-001 records set `deterministic_guidance_active` to `false`. Confirmation establishes personal confidence but does not silently inject a new measurement or branch into the approved diagnostic engine.

## Local storage

The application writes one JSON file per entry to:

`knowledge-base/private/personal-entries/`

The directory is ignored by Git. The process creates the directory with owner-only permissions and writes records with owner read/write permissions. P-002 will add search, correction history, and local case persistence without changing this private-by-default boundary.

## Validation

Focused tests cover private JSON creation and permissions, confidence and evidence consistency, exact revision and actionable safety requirements, numeric expected-result validation, strict request fields, and browser application integration.
