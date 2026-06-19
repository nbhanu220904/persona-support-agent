# Service API and extension points

The assessment UI calls the Python service layer directly. `SupportService` is the stable application API and can be mounted behind FastAPI without changing domain logic.

## `SupportService.respond(message, history)`

Input:

```json
{"message":"Our API returns 401. What should I check?","history":[]}
```

Output shape:

```json
{
  "response":"Grounded persona-adapted answer",
  "persona":{"persona":"Technical Expert","confidence":0.91,"reasoning":"...","sentiment":"neutral"},
  "sources":[{"text":"...","source":"api-authentication.md","section":"Troubleshooting","page":null,"score":0.72}],
  "escalation":{"escalated":false,"reasons":[],"priority":"normal"},
  "handoff":null
}
```

Validation errors are raised as `ValueError`. Provider or storage failures surface as exceptions for the UI boundary to log and convert into a safe user message. Production HTTP deployments should map validation to 422, rate limits to 429, provider failures to 503, and unexpected failures to 500 with a request ID.

## Operational endpoints

Streamlit exposes `/_stcore/health` for container health checks. For a future multi-service deployment, expose `/health/live`, `/health/ready`, `POST /v1/messages`, and `POST /v1/feedback` around the existing service methods.

