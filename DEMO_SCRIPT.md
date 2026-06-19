# 4-minute demo script

1. **Structure (30s):** Show `src`, `data`, `tests`, configuration, and deployment files.
2. **Ingestion (30s):** Run `python cli.py`; point out the persistent knowledge chunk count and PDF metadata.
3. **Three personas (90s):** Use the API authentication, loading failure, and operational impact sidebar examples. Highlight the persona badge, confidence, response style, and sources.
4. **Two more queries (45s):** Ask about SAML login loops and webhook signatures.
5. **Escalation (45s):** Use the duplicate charge example. Expand and download the handoff JSON.
6. **Design decision (30s):** Explain the provider abstraction: Gemini is the production semantic/generative path; deterministic local embeddings and extractive responses keep the repository testable without secrets.

Do not pre-record outputs. Run each query live and show the current result.

