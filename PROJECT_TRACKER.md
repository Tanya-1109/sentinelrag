# SentinelRAG — August 2026 Project Tracker

**Project window:** 9–31 August 2026  
**Target:** Portfolio-ready defensive security assistant using LLMs, RAG, and MCP  
**Working pace:** Approximately 2–3 focused hours per day

## Current status

- **Schedule health:** Behind by one milestone
- **Completed:** 6 of 23 daily milestones
- **Current milestone:** Step 6 complete; embedding generation is next
- **Next target:** Generate local embeddings and build the first vector index
- **Last reviewed:** 15 August 2026

## Daily milestones

| Date | Planned target | Status | Evidence / notes |
|---|---|---|---|
| 9 Aug | Define scope, users, safety boundaries, and success criteria | Complete | `PROJECT_SPEC.md` created |
| 10 Aug | Initialize Git repository and Python project environment | Complete | Python 3.11.5, `.venv`, package tooling, passing test, commits `93d43ed` and `7b47010`, and `origin/main` verified |
| 11 Aug | Build a basic non-RAG LLM assistant | Complete (12 Aug) | Local Ollama model, validated settings, HTTP client, defensive system prompt, CLI, mocked error handling, 7 passing tests, and three live behavior checks verified |
| 12 Aug | Finish basic assistant; begin trusted-source manifest if time permits | Complete | Step 3 carryover completed; source collection scheduled next |
| 12 Aug | Select trusted security sources and create source manifest | Complete | Four authoritative sources cataloged; strict Pydantic validation, CLI validation command, and 11 passing tests verified |
| 13 Aug | Implement document parsing and normalization | Complete | Controlled HTTPS fetch, HTML cleanup, provenance, SHA-256 change detection, JSON persistence, ingestion CLI, 24 passing tests, and a 16,139-character live OWASP record verified |
| 14 Aug | Implement metadata-aware chunking | Complete (15 Aug) | Deterministic word-aligned overlap, exact offsets, provenance, SHA-256 hashes, JSON persistence, `sentinelrag-chunk` CLI, 35 passing tests, and 19 validated OWASP chunks |
| 15 Aug | Generate embeddings and create vector index | Not started | One milestone behind; begin only after committing the completed chunking milestone |
| 16 Aug | Implement and test semantic retrieval | Not started | |
| 17 Aug | Complete first RAG flow with citations | Not started | |
| 18 Aug | Add hybrid semantic and keyword search | Not started | |
| 19 Aug | Add reranking and query routing | Not started | |
| 20 Aug | Add structured security finding output | Not started | |
| 21 Aug | Build a safe, read-only MCP security server | Not started | |
| 22 Aug | Integrate MCP tools with the assistant | Not started | |
| 23 Aug | Add prompt-injection and tool-safety controls | Not started | |
| 24 Aug | Create a 30-question evaluation dataset | Not started | |
| 25 Aug | Implement automated RAG evaluation | Not started | |
| 26 Aug | Improve weak areas using evaluation results | Not started | |
| 27 Aug | Build and test the FastAPI backend | Not started | |
| 28 Aug | Build the demonstration interface | Not started | |
| 29 Aug | Add Docker and GitHub Actions CI | Not started | |
| 30 Aug | Deploy and complete technical documentation | Not started | |
| 31 Aug | Polish portfolio, publish release, and prepare resume bullets | Not started | |

## Daily check-in

Complete this section at the end of each work session:

```text
Date:
Time spent:
Planned target:
What I completed:
What I learned:
Evidence (file, test, commit, or screenshot):
Blockers:
Tomorrow's first action:
Schedule status: Ahead / On schedule / At risk / Behind
```

## Checkpoint targets

| Deadline | Required outcome |
|---|---|
| 11 Aug | GitHub repository and basic LLM assistant |
| 17 Aug | End-to-end RAG with grounded citations |
| 22 Aug | Hybrid retrieval, reranking, and MCP tools |
| 26 Aug | Safety controls and measurable evaluation results |
| 29 Aug | API, interface, Docker, and CI |
| 31 Aug | Deployment, documentation, and portfolio-ready release |

## Tracking rules

1. A milestone is **Complete** only when it has visible evidence such as a file, passing test, commit, screenshot, or deployed feature.
2. Use **In progress**, **Blocked**, or **Deferred** instead of marking partial work complete.
3. If one day slips, move unfinished core work to the next day and defer an optional feature.
4. Do not sacrifice citations, evaluations, safety, or documentation to add extra features.
5. Record actual evaluation numbers and never invent portfolio metrics.

## Scope priority

If the schedule becomes tight, preserve work in this order:

1. Grounded RAG with citations
2. Evaluation and safety tests
3. One useful read-only MCP server
4. Clean API and reproducible setup
5. UI and deployment polish
6. Optional integrations and visual enhancements
