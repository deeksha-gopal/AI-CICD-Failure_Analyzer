# Architecture and engineering decisions

## Request lifecycle

1. The user pastes a log or uploads a UTF-8 `.log` / `.txt` file through the React interface.
2. The frontend sends multipart form data (`file`, `mode`) to `POST /api/analyze`.
3. FastAPI caps size at 256 KiB, checks extension/encoding, and performs best-effort credential redaction.
4. **Demo mode:** Python regular expressions match common failure signatures, capturing an evidence line and a set of safe troubleshooting suggestions. **LLM mode:** The backend sends up to 7,000 characters of redacted text to an LLM with a strict JSON prompt, then validates the response with Pydantic.
5. The backend stores a truncated redacted excerpt and structured findings in SQLite via SQLAlchemy.
6. The frontend renders the report and history using plain React text nodes (never injects raw HTML).

## API endpoints

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Availability, LLM configuration flag, size limit |
| POST | `/api/analyze` | Analyze a log (multipart file + demo/llm mode) |
| GET | `/api/history` | List 25 most recent reports |
| GET | `/api/history/{id}` | Get report details |
| GET | `/docs` | FastAPI Swagger UI (local backend only) |

## Design choices

- **Rule-based default:** No credentials and no internet needed. The analyzer is intentionally deterministic and explainable.
- **Optional real LLM:** Keeps the cloud API key server-side. The response must be a JSON object and is validated before saving. LLM failures return an explicit error rather than quietly faking AI output.
- **SQLite:** Low setup cost for a portfolio example. For multi-user scale, use PostgreSQL, migrations, and access controls.
- **Docker Compose:** Frontend Nginx container reverse-proxies `/api/` to a separate FastAPI container. A named volume preserves SQLite analysis history.
- **CI:** GitHub Actions tests Python, type-checks/builds TypeScript, then builds both Docker images.

## Failure modes handled

- Invalid extension: HTTP 400.
- Empty file or non-UTF-8 log: HTTP 400.
- File bigger than 256 KiB: HTTP 413.
- LLM mode without a key: HTTP 400 with configuration guidance.
- LLM/network/provider failures: HTTP 502 without leaking provider internals.
- Missing history entry: HTTP 404.
- Frontend/backend connection issues: a visible error message.

## Known limitations and future work

- No authentication, tenant separation, authorization, safe public hosting, audit trail, or access control. **Do not expose this sample directly to the internet.**
- SQLite write contention and synchronous persistence limit multi-user scalability.
- Regex secret redaction is best-effort. Logs may still contain private information.
- Rule-based diagnoses rely on the first matching signature per rule; they do not prove causality.
- LLM answers are untrusted and may hallucinate or follow injected instructions. Add output evaluations, robust guardrails, user confirmation, and stronger data handling before production.
- No ingestion integrations for live Jenkins/GitHub webhooks. For production, validate webhook signatures, use job queues, and set upload retention policies.
- No end-to-end browser tests, rate limiting, monitoring/alerts, semantic search, or deployment to an internet-accessible cloud platform. These are appropriate future milestones.

## Suggested engineering extensions

1. Implement synthetic benchmark datasets and evaluate precision/recall of rule-based patterns.
2. Add integration tests with a mocked LLM provider and capture failure scenarios.
3. Add PostgreSQL and Alembic migrations; test concurrent requests.
4. Add OpenTelemetry and structured, redacted service logs.
5. Add secure user authentication, per-project access, quotas, and retention/deletion features.
6. Deploy behind HTTPS with secrets management and least-privilege infrastructure.
