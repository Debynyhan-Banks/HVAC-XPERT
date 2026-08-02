# Security Policy

## Security principles

- Use least-privilege access for source documents, credentials, review tools, and publication systems.
- Store credentials only in an approved secret manager or local ignored environment file.
- Treat downloaded documents and extracted content as untrusted input.
- Separate acquisition, review, and publication permissions.
- Maintain audit logs for collection, extraction, review, and publication events.

## Ingestion controls

- Allowlist schemes, domains, redirects, MIME types, and maximum file sizes.
- Reject private-network, loopback, link-local, and metadata-service destinations in remote fetchers.
- Scan or quarantine unexpected and malformed files.
- Parse files in constrained workers with bounded CPU, memory, and execution time.
- Do not execute embedded scripts, macros, attachments, or document actions.
- Normalize filenames and generate storage keys independently of source paths.

## Application controls

- Validate every external payload against a schema.
- Enforce authorization server-side.
- Escape or sanitize source-derived text before rendering.
- Protect state-changing requests against cross-site request forgery where applicable.
- Rate-limit authentication, search, AI, and document endpoints.
- Log security-sensitive events without logging secrets or complete restricted content.

## AI controls

Source documents may contain prompt-injection text. Extraction systems must treat document content only as data, use fixed system instructions, constrain output to schemas, and never grant model output authority to invoke tools, alter source policy, or publish records.

## Reporting

Do not open public issues containing vulnerabilities, credentials, private source URLs, or licensed documents. Report security concerns privately to the project owner until a dedicated security contact is established.

## Current limitation

A dedicated security owner and disclosure contact have not yet been assigned. This is a blocker before external launch.
