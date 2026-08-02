# Document Manifests

This directory contains versioned metadata and provenance manifests for privately stored source documents.

Source PDF binaries are stored under `sources/private/documents/` and excluded from Git. Durable references use the manifest's `document_id`, SHA-256 fingerprint, source URL, page number, and section rather than an attachment path or original filename.

Every manifest must validate against `schemas/document.schema.json`. A manifest records document identity and source visibility only; it does not grant collection, redistribution, or publication rights.
