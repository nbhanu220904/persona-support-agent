# API authentication and 401 errors

Lumina API requests use OAuth 2.0 bearer tokens. Send the token as `Authorization: Bearer <access_token>` and `Content-Type: application/json`. Never place a token in a query string.

## Troubleshooting

A 401 response means the credential is missing, expired, malformed, or issued for a different environment. Confirm there is one space after `Bearer`, inspect the token expiry, and verify that sandbox tokens are not used against production. Rotate any token exposed in logs. A 403 means the credential is valid but lacks the required scope. Request IDs in the `X-Request-ID` response header should be included in support tickets.

## Token lifecycle

Access tokens expire after 60 minutes. Refresh tokens can request a new access token without user interaction. Retry one time after refresh; repeated automatic retries can trigger rate protection.

