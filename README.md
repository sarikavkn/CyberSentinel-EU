# 🛡️ CyberSentinel EU

**Cybersecurity Compliance & Risk Management Platform — Portfolio Project**

CyberSentinel EU is a functional portfolio application that explores how cybersecurity governance, EU regulatory requirements, controls, evidence, risks, findings, assets and audit activity can be managed in one workflow.

> **Project status:** Active portfolio / learning project. It is not a certification product, legal-advice service, or production-ready enterprise security platform.

## 🎥 Demo

A walkthrough is included in [`demo/CyberSentinel_EU_Tool_Walkthrough.mp4`](demo/CyberSentinel_EU_Tool_Walkthrough.mp4).

## What the application demonstrates

- **Compliance dashboard** — overview of assessments, findings, evidence, risks and assets.
- **Organisation & applicability** — captures organisation context and supports regulatory applicability screening.
- **Regulatory assessments** — records applicability, implementation status, maturity, ownership and notes.
- **Control library** — maps security controls to compliance requirements.
- **Evidence vault** — uploads evidence and records SHA-256 hashes to support integrity checking.
- **Findings & remediation** — tracks gaps, severity, owners, due dates and remediation actions.
- **Risk register** — records likelihood, impact, residual risk and treatment information.
- **Asset inventory** — tracks systems/assets, criticality, exposure and personal-data indicators.
- **Audit trail** — records important user and application actions.
- **CSV reporting** — exports assessment information for further analysis.

## EU cybersecurity scope

The project currently contains a starter regulatory knowledge base covering concepts from **NIS2**, **GDPR**, the **Cyber Resilience Act (CRA)**, **DORA**, and the **EU Cybersecurity Act**. Regulatory content must be independently validated before use in a real compliance programme. Member-State implementation and sector-specific requirements can create additional obligations.

## Technology

`Python` · `FastAPI` · `SQLAlchemy` · `Jinja2` · `SQLite/PostgreSQL-ready configuration` · `Docker` · `Pytest`

Security concepts demonstrated include password hashing, session-based authentication, CSRF validation, role checks, evidence hashing, audit logging and environment-based configuration.

## Architecture

```text
Organisation Context
        ↓
Applicability Assessment
        ↓
EU Regulatory Requirements
        ↓
Security Controls
        ↓
Assessment + Risk Management
        ↓
Evidence + Technical Validation
        ↓
Findings + Remediation
        ↓
Audit Trail + Reporting
```

Additional architecture documentation is available in [`docs/PRODUCT_ARCHITECTURE.md`](docs/PRODUCT_ARCHITECTURE.md).

## Run locally on Windows

### Prerequisite

Install **Python 3.12**.

### Start

Double-click:

```text
run_windows.bat
```

The launcher creates a virtual environment, installs dependencies and starts the application at:

```text
http://127.0.0.1:8000
```

For local demonstration, the default bootstrap account is `admin` / `ChangeMe!2026`. These values can be overridden with the `CYBERSENTINEL_ADMIN_USER` and `CYBERSENTINEL_ADMIN_PASSWORD` environment variables. **Never use the demonstration password for an internet-facing deployment.**

## Testing

```bash
python -m pytest
```

## Security and production limitations

This repository is intended for local demonstration and portfolio use. A production deployment would require additional controls including enterprise identity/SSO and MFA, secure user lifecycle management, HTTPS, secret management, encrypted evidence/object storage, malware scanning, tenant isolation, rate limiting, database migrations, immutable/externally protected audit storage, backup and disaster recovery, monitoring, secure deployment pipelines and independent security testing.

Do not upload real confidential, personal, regulated or customer evidence to the local demo build.

## Roadmap

Planned areas include stronger regulatory-content governance, Member-State NIS2 implementation mapping, expanded DORA/CRA content, PostgreSQL migrations, enterprise authentication, workflow/approval capabilities, continuous control monitoring and integrations with SIEM, EDR, IAM, vulnerability-management and cloud-security tooling.

## Regulatory references

The regulatory research notes and source links used during development are documented in [`docs/REGULATORY_RESEARCH.md`](docs/REGULATORY_RESEARCH.md). CyberSentinel EU does not guarantee compliance or replace professional legal/compliance advice.

## Author

**Sarika Vijayakumar**  
Cybersecurity portfolio project  
GitHub: **sarikavkn**

## License

MIT License. See [`LICENSE`](LICENSE).
