# Risk Register

| ID | Risk | Impact | Likelihood | Control | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | Copyright or terms prohibit collection or redistribution | High | Medium | Source-by-source legal review; metadata and derived facts separated from source binaries | Unassigned legal reviewer | Open |
| R-002 | AI invents or merges technical values | Critical | High | No-inference prompts, provenance requirements, schema checks, conflict detection, human review | Data governance owner | Controlled |
| R-003 | OCR corrupts pin labels, units, or fault codes | Critical | High | Source-page visibility, confidence flags, visual review, golden documents | Extraction owner | Open |
| R-004 | Different model revisions are merged | Critical | Medium | Required revision identifiers and document applicability records | Knowledge owner | Controlled |
| R-005 | Simulator behavior diverges from approved facts | Critical | Medium | Deterministic engine, traceable inputs, reviewer acceptance tests | Simulator owner | Open |
| R-006 | Unsafe field guidance is shown as authoritative | Critical | Medium | Validation labels, safety messaging, source links, expert review, no automatic repair authorization | Product safety owner | Open |
| R-007 | Source websites change or block automated access | Medium | High | Pluggable adapters, low rates, cached metadata, manual upload, partnership path | Acquisition owner | Open |
| R-008 | Sensitive credentials or licensed files leak | High | Medium | Secret management, access controls, audit logs, private source storage | Security owner | Open |
| R-009 | Validation backlog grows faster than extraction | High | High | Small pilot, publication gates, completeness metrics, reviewer capacity planning | Program owner | Open |
| R-010 | Source removal request cannot be fulfilled | High | Low | Source inventory, immutable IDs, dependency tracing, removal procedure | Data governance owner | Open |

## Review cadence

Review this register at every phase gate and whenever a new source, manufacturer, model family, AI model, or publication channel is introduced.
