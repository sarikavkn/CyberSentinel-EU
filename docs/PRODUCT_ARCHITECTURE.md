# CyberSentinel EU Product Architecture

Core traceability:
Regulation -> Version -> Jurisdiction -> Applicability -> Requirement -> Control -> Evidence -> Test -> Finding -> Remediation -> Verification -> Audit.

Production planes:
1. Regulatory knowledge and versioning
2. Applicability and jurisdiction
3. Control library and assessments
4. Evidence and assurance
5. Cyber risk
6. Technical integrations
7. Audit and reporting
8. Identity and platform security

Production evolution should use PostgreSQL, secured object storage, enterprise IAM/MFA, secrets management, immutable audit storage, queue/event processing, monitored backups and secure deployment.
