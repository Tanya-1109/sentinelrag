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
