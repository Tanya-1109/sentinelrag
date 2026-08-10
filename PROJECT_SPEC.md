# SentinelRAG Project Specification

## 1. Problem

Security information is distributed across vulnerability databases,
security standards, vendor advisories, and internal documentation.
Junior analysts may struggle to retrieve the relevant information
quickly and distinguish evidence from an LLM's assumptions.

## 2. Target User

Primary user:
- Junior SOC analyst or security engineer

Secondary user:
- Software developer investigating a vulnerability or security alert

## 3. Primary Use Case

A user submits a security question, vulnerability identifier, code
snippet, or sanitized log sample.

SentinelRAG:
1. Identifies the investigation type.
2. Retrieves relevant trusted security documents.
3. Produces a concise analysis.
4. Cites the evidence used.
5. Separates facts, assumptions, and recommendations.
6. Suggests safe next investigation steps.

## 4. Initial Knowledge Sources

The first version will use:
- OWASP Top 10
- OWASP Cheat Sheet Series
- NIST incident-response guidance
- CISA cybersecurity advisories

Later versions may add:
- CVE and NVD records
- MITRE ATT&CK
- Organization-specific security playbooks

## 5. Core Questions

The first version must answer:
1. What does this vulnerability or security concept mean?
2. Which trusted sources support the answer?
3. What is the likely risk?
4. What mitigations should be considered?
5. What information is missing before reaching a conclusion?

## 6. Non-Goals

SentinelRAG will not:
- Exploit vulnerabilities
- Run destructive commands
- Scan systems without authorization
- Claim that an incident occurred without sufficient evidence
- Replace a qualified security professional
- Accept secrets or unsanitized production data

## 7. Success Criteria

A successful answer:
- Includes at least one valid source citation
- Clearly identifies retrieved evidence
- Does not invent CVEs, controls, or source content
- Communicates uncertainty
- Provides defensive and actionable recommendations
- Responds appropriately when the knowledge base lacks an answer

## 8. Example User Questions

- Explain SQL injection and cite the relevant OWASP guidance.
- Which OWASP category applies to exposed API credentials?
- Summarize CVE-XXXX-XXXX and list evidence-based mitigations.
- Analyze this sanitized failed-login log for suspicious patterns.
- Create an investigation checklist for a suspected credential-stuffing alert.