# Source Registry

`source-registry.yaml` is the allowlist and policy record for document acquisition. A source with `approved_for_collection: false` must never be crawled or downloaded automatically.

Candidate domains are intentionally marked `domain_verification: pending`, have no approved base URLs, and use zero collection rates until a reviewer completes the required terms, robots, access, and rights checks.
