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
npm run build
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

Pushes to **`prod`** that touch `website/` build and push:

- `yourdockerhubuser/nort-website:latest`
- `yourdockerhubuser/nort-website:<git-sha>`

`main` is for research and project work; production deploys only from `prod`.

## Releasing after an achievement on main

1. Finish the milestone on **`main`** (wiki log, code, results).
2. Merge into **`prod`**: `git checkout prod && git merge main`
3. Add a public lab note in `blog/management/commands/seed_blog_posts.py` → `POSTS` list (new entry at the top, unique `slug`).
4. Commit and push **`prod`**.
5. GitHub Actions builds and pushes the Docker image.
6. On the VPS (`/opt/nort`): `docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d`

On container start, `seed_blog_posts` runs automatically (creates new posts, updates existing slugs, sets one featured post). No manual admin step required unless you prefer it.

### New post template

```python
{
    "title": "Short public headline",
    "slug": "unique-kebab-case-slug",
    "category": BlogPost.Category.STATUS,  # software | hardware | methods | status
    "published_at": datetime(2026, 9, 20, 12, 0),
    "is_featured": True,  # only one; clears featured on other posts
    "excerpt": "One or two sentences for cards and SEO.",
    "content": """## Summary

Public-facing write-up. Link to deeper wiki notes on main if useful.""",
},
```
