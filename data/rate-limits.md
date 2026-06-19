# API rate limits

API limits are enforced per workspace and route. Standard plans allow 600 requests per minute for read routes and 120 per minute for write routes. Responses include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers.

A 429 response should be retried only after the `Retry-After` duration. Add exponential backoff with jitter and cap retries at five attempts. Batch reads when possible and avoid synchronized retry loops across workers.

