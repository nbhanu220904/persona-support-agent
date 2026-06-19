# Webhook delivery guide

Webhook endpoints must accept HTTPS POST requests and return a 2xx status within 10 seconds. Lumina signs each payload with HMAC-SHA256 in the `X-Lumina-Signature` header. Compute the digest from the raw request body and the endpoint signing secret using a constant-time comparison.

Failed deliveries retry with exponential backoff for up to 24 hours. Do not perform slow work before returning 2xx; acknowledge first and process asynchronously. Use the event ID for idempotency. Rotate a compromised signing secret in Settings > Developers > Webhooks.

