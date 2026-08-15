# SentinelRAG

An evidence-grounded cybersecurity investigation assistant built with
large language models, retrieval-augmented generation, and the Model
Context Protocol.

## Project status

SentinelRAG is currently under active development as a portfolio and
learning project.

## Goals

- Retrieve information from trusted cybersecurity sources
- Generate answers with verifiable citations
- Distinguish evidence, assumptions, and recommendations
- Use safe, read-only security tools through MCP
- Evaluate retrieval quality, groundedness, and refusal behavior

## Safety

SentinelRAG is intended for defensive security education and authorized
analysis. It will not provide autonomous exploitation, destructive
actions, or unauthorized scanning capabilities.

## Documentation

- [Project specification](PROJECT_SPEC.md)
- [Development tracker](PROJECT_TRACKER.md)

## Trusted knowledge sources

SentinelRAG uses a versioned source manifest at
[`data/sources.yaml`](data/sources.yaml) to control which documents may
enter the knowledge base.

Each source records:

- Publisher and authoritative URL
- Source type and security topics
- Trust tier
- Licensing and attribution requirements
- Whether ingestion is enabled

The manifest currently includes OWASP, NIST, CISA, and MITRE ATT&CK
sources. Collection pages are disabled until individual documents are
selected.

Validate the manifest locally:

```powershell
sentinelrag-sources data/sources.yaml
```

Expected result:

```text
Valid manifest: 4 sources, 3 enabled.
```

## Document ingestion

SentinelRAG downloads only enabled sources from the validated source
manifest. Web documents are normalized by removing navigation, scripts,
styles, headers, footers, and other page boilerplate.

Each processed document preserves:

- Stable source ID
- Publisher and authoritative URL
- Retrieval timestamp
- Security topics
- Licensing metadata
- Normalized content
- SHA-256 content hash

Ingest one approved source:

```powershell
sentinelrag-ingest owasp-top-10-2021
```

Generated records are written to `data/processed/` and are excluded from
Git because they can be reproduced from the source manifest.

## Metadata-aware chunking

Normalized documents are divided into deterministic, overlapping chunks
before embedding. Each chunk preserves its source URL, publisher, topics,
character offsets, parent-document hash, and its own SHA-256 content hash.

Chunk a normalized document locally:

```powershell
sentinelrag-chunk data/processed/owasp-top-10-2021.json --output data/chunks --max-chars 1000 --overlap-chars 150
```

Generated chunk records are written to `data/chunks/` and excluded from Git
because they can be reproduced from normalized documents. The current OWASP
sample produces 19 validated chunks.
