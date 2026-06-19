# Database and integration troubleshooting

Integration failures should be isolated by testing credentials, network reachability, and permissions separately. Confirm the database host resolves from the connector region, TLS 1.2 or newer is enabled, and the service account can read only the required schemas.

For connection timeouts, allowlist the current connector egress addresses shown in Settings > Integrations. For authentication failures, rotate the stored secret and test it directly with the database client. Include the integration ID, timestamp, sanitized error code, and connector region in a support case. Never include raw credentials.

