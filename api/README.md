# Spain Electoral Polls API

Read-only FastAPI service for the Spain Electoral Polls PostgreSQL database. It serves JSON for a future dashboard and for external users working from curl, Python, R, browsers, or other applications.

The API is independent from the R ETL. It does not scrape, mutate data, run migrations, or modify the SQL schema.

## Handoff Sources

Read these before changing API behavior:

- `docs/api-handoff/README.md`
- `docs/api-handoff/database-schema-summary.md`
- `docs/api-handoff/database-dictionary.md`
- `docs/api-handoff/entity-relationship.md`
- `docs/api-handoff/business-rules.md`
- `docs/api-handoff/api-use-cases.md`
- `docs/api-handoff/api-contract-draft.md`
- `docs/api-handoff/sample-data.md`
- `docs/api-handoff/implementation-notes.md`
- `sql/001_schema.sql`, `sql/002_indexes.sql`, and `sql/003_publication_sources.sql`

## Configuration

Copy `.env.example` to `.env` for local development and set:

```text
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/spainelectoralpollsdb
API_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://polls.spainelectoralproject.com
ENABLE_ADMIN_ENDPOINTS=false
```

`ENABLE_ADMIN_ENDPOINTS` is reserved for a future admin surface. No admin endpoints are implemented in v1.

## Local Development

```bash
cd api
python -m venv .venv
. .venv/Scripts/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open:

- API health: `http://localhost:8000/health`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Swagger UI: `http://localhost:8000/docs`

## Endpoints

- `GET /health`
- `GET /api/v1/elections`
- `GET /api/v1/pollsters`
- `GET /api/v1/parties`
- `GET /api/v1/polls`
- `GET /api/v1/polls/{poll_id}`
- `GET /api/v1/results`
- `GET /api/v1/timeseries`

Paginated endpoints return:

```json
{ "items": [], "limit": 100, "offset": 0, "total": 0 }
```

Default public filters exclude `polls.is_active = false` and `polls.identity_status = 'manual_review'`. Use `include_inactive=true` or `include_manual_review=true` to request them explicitly.

## Programmatic Examples

curl:

```bash
curl "https://polls.spainelectoralproject.com/api/v1/polls?election_key=congreso_espana_2027&limit=10"
```

Python:

```python
import requests

url = "https://polls.spainelectoralproject.com/api/v1/results"
params = {
    "election_key": "congreso_espana_2027",
    "party": "psoe",
    "limit": 100,
}

data = requests.get(url, params=params, timeout=30).json()
```

R:

```r
library(httr2)

resp <- request("https://polls.spainelectoralproject.com/api/v1/results") |>
  req_url_query(
    election_key = "congreso_espana_2027",
    party = "psoe",
    limit = 100
  ) |>
  req_perform()

data <- resp_body_json(resp)
```

Timeseries:

```bash
curl "http://localhost:8000/api/v1/timeseries?election_key=congreso_espana_2027&party=psoe&date_field=auto"
```

`date_field=auto` uses `coalesce(fieldwork_end, publication_date)`.

## Tests And Linting

Tests expect a PostgreSQL database reachable through `DATABASE_URL`.

```bash
cd api
ruff check .
pytest
```

The GitHub Actions workflow runs tests against a PostgreSQL service.

## Docker

Build:

```bash
docker build -t spain-electoral-polls-api:latest ./api
```

Run:

```bash
docker run -d \
  --name spain-electoral-polls-api \
  --restart unless-stopped \
  --env-file ./api/.env \
  -p 8000:8000 \
  spain-electoral-polls-api:latest
```

## Deployment

Deployment uses strategy A: the remote server builds the image locally after `git pull`. This avoids a registry and is simple for a self-managed server.

The manual workflow is `.github/workflows/deploy-api.yml`. Required GitHub Secrets:

- `REMOTE_HOST`
- `REMOTE_USER`
- `REMOTE_SSH_KEY`
- `REMOTE_PORT`
- `REMOTE_APP_DIR`
- `API_ENV_FILE_PATH`

Optional repository variables or secrets:

- `REMOTE_DOCKER_NETWORK`
- `API_CONTAINER_NAME`
- `API_IMAGE_NAME`
- `API_PORT`

The remote machine must already have Docker, SSH access, the repo path prepared, a production `.env` file, network access to PostgreSQL, and an available API port. Nginx or another reverse proxy is assumed to be managed outside this repo.

See `DEPLOYMENT.md` for operational commands.

## Current Limitations

- Admin endpoints are postponed.
- There is no `parties` table; `/api/v1/parties` is derived from `poll_results`.
- There is no persisted `media_key`; media filtering uses `polls.media`.
- The API does not include authentication in v1 because all implemented endpoints are public and read-only.

## Documented Discrepancies

- `sql/003_publication_sources.sql` is also part of the SQL truth.
- Health examples differ between prompt and handoff; v1 returns `status`, `service`, and `database`.
- `date_field` defaults differ in docs; v1 uses `auto = coalesce(fieldwork_end, publication_date)`.
- Party and media catalog tables do not exist in SQL.
