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
