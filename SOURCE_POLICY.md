# Source Policy

## Scope

This policy applies to public web pages, public PDFs, manufacturer portals, distributor libraries, manual uploads, APIs, licensed feeds, component datasheets, service bulletins, parts catalogs, engineering data, AHRI records, and training media metadata.

## Source priority

Use sources in this order unless applicability or revision evidence indicates otherwise:

1. Manufacturer-issued document for the exact model and revision
2. Manufacturer service bulletin or engineering notice
3. Manufacturer family-level document with explicit applicability
4. Original component-manufacturer datasheet
5. Certification or regulatory record
6. Authorized distributor copy traceable to the manufacturer original
7. Qualified technician or instructor review
8. Secondary reference material

AI output is never a source.

## Required source-registry fields

Every source record must include:

- Stable source ID, owner, domain, and source type
- Expected document types
- Access level and authentication requirements
- Terms, robots, copyright, redistribution, and extraction review status
- Approved collection method and rate limit
- Last review date and reviewer
- Reliability ranking
- Collection approval state
- Removal contact or procedure when known

## Approval gate

Automated discovery or downloading is prohibited unless all of the following are true:

- The exact domain or endpoint is registered.
- Access is public or expressly authorized.
- Terms and robots policies have been reviewed.
- Copyright, extraction, storage, and redistribution classifications are recorded.
- Authentication use is authorized.
- A conservative rate limit is configured.
- `approved_for_collection` is `true`.

A crawler must fail closed when a source is absent, expired, or unapproved.

## Collection controls

- Identify the application with an honest user agent and contact where appropriate.
- Respect robots rules, crawl delays, rate limits, and retry limits.
- Do not bypass authentication, paywalls, bot controls, or access restrictions.
- Download only allowlisted MIME types and bounded file sizes.
- Hash content before storing a second binary.
- Record discovery and download timestamps, HTTP metadata, redirects, and final URL.
- Quarantine unexpected, encrypted, executable, or malformed files.
- Stop collection when terms, robots, ownership, or access behavior changes.

## Publication controls

The platform may publish approved factual data, normalized records, original drawings, and original explanations. Complete source documents, substantial source excerpts, and source diagrams remain restricted unless redistribution rights are expressly recorded.

## Review expiry

Source approvals expire after 180 days or immediately upon a material change to the domain, terms, robots policy, ownership, authentication, or collection behavior.
