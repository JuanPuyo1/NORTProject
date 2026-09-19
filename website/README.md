# NORT Official Website

Django site for the NORT research project — HTMX, Alpine.js, Tailwind CSS, DaisyUI, and GSAP.

## Setup

Copy environment variables and fill in your Gmail App Password and Analytics ID:

```bash
cd website
copy .env.example .env
```

```bash
..\.venv\Scripts\pip install -r requirements.txt
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py seed_blog_posts
..\.venv\Scripts\python manage.py createsuperuser
npm install
npm run build:css
```

## Development

```bash
..\.venv\Scripts\python manage.py runserver
npm run watch:css
```

Open http://127.0.0.1:8000/

## Admin

Publish lab notes at `/admin/` using the **Blog posts** model. Set **Is published** to make posts visible. Mark one post as **Is featured** for the blog hero card.

Collaboration form submissions appear under **Collaboration inquiries** and trigger an email to `COLLABORATION_NOTIFICATION_EMAIL`.

## Email & analytics

| Variable | Purpose |
|----------|---------|
| `EMAIL_HOST_USER` | Gmail address used for SMTP |
| `EMAIL_HOST_PASSWORD` | Gmail App Password (not your login password) |
| `DEFAULT_FROM_EMAIL` | Sender address on outbound mail |
| `COLLABORATION_NOTIFICATION_EMAIL` | Inbox that receives form submissions |
| `GOOGLE_ANALYTICS_ID` | e.g. `G-9K7QWGXXGM`; leave empty locally to disable tracking |

Without SMTP credentials, emails print to the console instead of sending.

## Docker

Build and run locally (uses PostgreSQL in Docker; SQLite is still used when `POSTGRES_HOST` is unset):

```bash
cd website
copy .env.example .env
docker compose up --build
```

Build a Linux image from Windows or macOS (for a VPS on `linux/amd64`):

```bash
cd website
docker buildx build --platform linux/amd64 -t nort-website:local .
```

Production on the VPS (pull image from Docker Hub):

```bash
cd website
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

Set `DOCKER_IMAGE=yourdockerhubuser/nort-website:latest` in `.env` on the server.

### GitHub Actions

Add repository secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN` (Docker Hub access token)

Pushes to `main` that touch `website/` build and push:

- `yourdockerhubuser/nort-website:latest`
- `yourdockerhubuser/nort-website:<git-sha>`
