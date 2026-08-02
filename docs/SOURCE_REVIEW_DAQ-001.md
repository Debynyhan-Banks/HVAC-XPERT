# DAQ-001 Source Review

## Review status

- Review date: 2026-08-02
- Scope: Read-only investigation of official Daikin Comfort Technologies, Goodman, Amana, and Daikin City sources
- Pilot: Amana S-Series inverter outdoor unit `ASXS6S4810AA`
- Collection performed: None
- Documents downloaded: None
- Decision: Automated collection remains blocked

This report records operational findings and is not legal advice.

## Executive finding

The official North American terms apply to `GoodmanMFG.com`, `DaikinComfort.com`, `Amana-HAC.com`, and associated sites. They expressly prohibit automated systems from monitoring or copying site content. Therefore, HVAC XPERT must not run a crawler against these sources without written permission or a separate agreement, even where a robots file is permissive.

Manual access to public documents may support a user-supplied pilot, but storage, factual extraction, commercial use, derivative publication, and retention still require a rights determination.

## Official sources found

| Source | Official entry point | Access observation | Status |
| --- | --- | --- | --- |
| Daikin Resource Center | https://www.daikincomfort.com/resource-center | Public index for manuals, literature, submittals, and specifications | Crawler blocked by terms |
| Amana Literature Library | https://www.amana-hac.com/resources/literature-library | Public product-literature index | Crawler blocked by terms and robots restrictions |
| Daikin City Library | https://library.daikincity.com | FAQ states product documents may be available without login; additional assets are credential-controlled | Separate permission required |
| Goodman product documents | https://www.goodmanmfg.com | Exact public pilot-document index not confirmed | Crawler blocked by terms and robots restrictions |

## Terms evidence

- Terms: https://backend.daikincomfort.com/docs/default-source/default-document-library/general/ggh_terms.pdf
- Last-modified date shown in the document: 2020-01-12
- Covered sites include Goodman, Daikin Comfort, and Amana HAC, plus associated linked sites.
- Automated monitoring or copying is prohibited.
- Site access does not grant ownership or a license to site content.
- Questions about the terms are directed to `IP@DaikinComfort.com`.

Operational classification: `prohibited` for crawler collection until written authorization is recorded.

## Robots evidence

| Domain | Evidence | Observation | Classification |
| --- | --- | --- | --- |
| `daikincomfort.com` | https://www.daikincomfort.com/robots.txt | Current general rule allows crawling | Approved robots policy only; terms still block collection |
| `goodmanmfg.com` | https://www.goodmanmfg.com/robots.txt | `/docs/*` and `/api` are disallowed | Restricted |
| `amana-hac.com` | https://www.amana-hac.com/robots.txt | `/docs/*` and `/api` are disallowed | Restricted |
| `library.daikincity.com` | https://library.daikincity.com/robots.txt | Path returns the web application rather than a usable robots policy | Unresolved |

Robots permission does not establish copyright, contract, storage, extraction, or redistribution rights.

## Candidate pilot documents

These records were identified through public search and metadata only. They have not been acquired or accepted into the knowledge base.

| Candidate | Document type | Current evidence | Status |
| --- | --- | --- | --- |
| `IM-3P731493-2_amana.pdf` | Installation instructions | Official Daikin CDN URL: https://cdn.daikincloud.io/PIM/Assets/Documents/IM-3P731493-2_amana.pdf | Candidate; applicability review required |
| `SiUS612213E` | Service instructions | Manufacturer-issued document code appears in public search and distributor copies | Official public asset URL not confirmed |
| `RP-A4353` | Repair parts | Manufacturer-issued document code appears in public search and distributor copies | Official public asset URL not confirmed |
| `SS-ASXS6` | Product specifications | ASXS6 product literature is referenced by official Amana/Daikin resources | Exact current asset URL not confirmed |

Third-party mirrors are discovery leads only. They cannot establish authoritative provenance until matched to an official or licensed source and exact revision.

## Credential and confidentiality boundary

Daikin City contains public, credential-controlled, and potentially confidential assets. HVAC XPERT must never use account credentials, distributor-only materials, or confidential documents unless a separate agreement explicitly authorizes collection, storage, extraction, and publication for this project.

## Approved next paths

1. Request written permission from Daikin Comfort Technologies using `docs/DAIKIN_PERMISSION_REQUEST.md`.
2. Ask whether an API, licensed feed, document export, or manufacturer partnership is available.
3. While permission is pending, accept only documents manually supplied by an authorized user who lawfully possesses them.
4. Keep manually supplied source files private and do not publicly redistribute them.
5. Build and test ingestion against synthetic fixtures or authorized manual uploads, not live manufacturer websites.

## Publication posture

No complete manual, manufacturer diagram, substantial excerpt, or credential-controlled asset may be published. Proposed public output remains limited to separately approved factual assertions, source metadata, original normalized models, original SVG redraws, and original explanations.

## Manual import follow-up

On 2026-08-02, the user manually supplied four pilot PDFs. They were copied into the private, Git-excluded document vault with restrictive local permissions. Versioned manifests now record stable document IDs, SHA-256 fingerprints, source URLs, page counts, applicability, and source-visible document identity.

- Product specifications: `DOC-AMANA-ASXS6-SPEC-SS-ASXS6`
- Installation instructions: `DOC-AMANA-ASXS6-INSTALL-3P731493-2`
- Service instructions: `DOC-AMANA-ASXS6-SERVICE-SIUS612213E`
- Repair parts: `DOC-AMANA-ASXS6-PARTS-RP-A4353`

This import does not change the crawler prohibition or establish public redistribution rights.
