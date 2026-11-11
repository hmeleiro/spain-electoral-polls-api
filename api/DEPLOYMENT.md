# API Deployment

## Remote Requirements

- Docker installed.
- SSH access for the GitHub Actions deploy user.
- Repository cloned or otherwise available at `REMOTE_APP_DIR`.
- Production environment file present at `API_ENV_FILE_PATH`.
- PostgreSQL reachable from the API container.
- API port available on the host.
- Optional Docker network available if PostgreSQL runs in another container.

The production `.env` file lives only on the server and must contain `DATABASE_URL`, `API_ENV`, `API_HOST`, `API_PORT`, `CORS_ORIGINS`, and `ENABLE_ADMIN_ENDPOINTS`.

To let the documentation site's browser-based explorer call the API from GitHub Pages, include
`https://hmeleiro.github.io` in the comma-separated production `CORS_ORIGINS`. If the documentation
later uses a custom domain, add that exact origin as well.

## GitHub Secrets

Required:

- `REMOTE_HOST`
- `REMOTE_USER`
- `REMOTE_SSH_KEY`
- `REMOTE_PORT`
- `REMOTE_APP_DIR`
- `API_ENV_FILE_PATH`

Optional variables or secrets:

- `REMOTE_DOCKER_NETWORK`
- `API_CONTAINER_NAME`
- `API_IMAGE_NAME`
- `API_PORT`

## Manual Workflow

Run the `deploy-api` workflow from GitHub Actions. It will:

1. Install API dependencies.
2. Run tests against PostgreSQL.
3. Connect to the remote server over SSH.
4. Pull the latest code.
5. Build `./api` into a Docker image.
6. Replace the running container.
7. Check `/health`.

## Verify Service

```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/openapi.json
```

## Logs

```bash
docker logs -f spain-electoral-polls-api
```

## Manual Restart

```bash
docker restart spain-electoral-polls-api
```

## Basic Rollback

On the remote server:

```bash
cd "$REMOTE_APP_DIR"
git checkout <previous-good-commit>
docker build -t spain-electoral-polls-api:latest ./api
docker stop spain-electoral-polls-api || true
docker rm spain-electoral-polls-api || true
docker run -d \
  --name spain-electoral-polls-api \
  --restart unless-stopped \
  --env-file "$API_ENV_FILE_PATH" \
  -p 8000:8000 \
  spain-electoral-polls-api:latest
curl -f http://localhost:8000/health
```
