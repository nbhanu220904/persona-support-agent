# Deployment

## Streamlit Community Cloud

1. Push this directory to a public GitHub repository.
2. Create an app at Streamlit Community Cloud and select `app.py`.
3. Add `GEMINI_API_KEY` in app secrets/environment settings. Do not commit `.env`.
4. Deploy and verify all demo scenarios plus the health endpoint.

Chroma persistence on ephemeral free hosting is rebuilt from committed documents after a restart. For durable production storage, mount `chroma_db` on a persistent volume or replace the repository with managed Qdrant/Pinecone.

## Docker

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

Open `http://localhost:8501`. Terminate with `docker compose down`; the named Chroma volume remains intact.

## Production checklist

- Store API keys in the platform secret manager and rotate them regularly.
- Terminate TLS at the load balancer and restrict application origins.
- Add centralized structured logs, provider latency metrics, and alerting.
- Pin a reviewed dependency lockfile in regulated deployments.
- Back up the vector index or rebuild it deterministically from versioned documents.
- Run the test suite and a five-scenario smoke test before promoting a release.

