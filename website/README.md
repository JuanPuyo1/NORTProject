# NORT Official Website

Django site for the NORT research project — HTMX, Alpine.js, Tailwind CSS, DaisyUI, and GSAP.

## Setup

```bash
cd website
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

Collaboration form submissions appear under **Collaboration inquiries**.
