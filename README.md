# Python service

Minimal FastAPI service with health check, containerized for Docker and published to Docker Hub via GitHub Actions.

## Run locally

```bash
pip install -r requirements.txt
uvicorn src.app.main:app --reload
```

Service listens on http://localhost:8000. Optional: set `PORT` to use another port.

## Run with Docker

```bash
docker build -t python-service .
docker run -p 8000:8000 python-service
```

Or use the image from Docker Hub (after CI has run):

```bash
docker run -p 8000:8000 <your-dockerhub-username>/<repo-name>:latest
```

## Endpoints

- `GET /` — Hello message
- `GET /health` — Health check (returns `{"status": "ok"}`)

## GitHub Actions and Docker Hub

The workflow in `.github/workflows/docker-publish.yml` runs on push to `main` and on version tags `v*`. It builds the image, runs the container and tests `/health`, then pushes to Docker Hub.

**Required secrets** (Settings → Secrets and variables → Actions):

- `DOCKERHUB_USERNAME` — Your Docker Hub username
- `DOCKERHUB_TOKEN` — Docker Hub Access Token (Account → Security → Access Tokens) with Read, Write, Delete

Create the Docker Hub repository (e.g. same name as this GitHub repo) before the first push.

## Jenkins (Generic Webhook)

A `Jenkinsfile` is provided that does the same build → run/test health → push flow. To use it with **Generic Webhook Trigger**:

1. Create a Pipeline job and set "Pipeline script from SCM" to this repo.
2. In **Build Triggers**, enable **Generic Webhook Trigger**. Add a post-content parameter, e.g. `ref` with JSON path `$.ref` (for GitHub push events).
3. In Jenkins, add a **Username and password** credential with your Docker Hub login and set its ID to `dockerhub-credentials`.
4. Set the job’s parameters or environment: `DOCKERHUB_USERNAME`, and optionally `DOCKER_IMAGE_REPO` (default `python-service`). You can also pass `ref` via the webhook so tag is derived from the branch/tag (e.g. `refs/tags/v1.0.0` → tag `v1.0.0`).
5. Point your GitHub repo webhook URL to `https://<jenkins>/generic-webhook-trigger/invoke` (or the path shown in the trigger config).
