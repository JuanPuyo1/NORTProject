# syntax=docker/dockerfile:1

FROM node:22-alpine AS assets

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

COPY tailwind.config.js postcss.config.js ./
COPY templates ./templates
COPY scripts ./scripts
COPY static ./static
RUN npm run build

FROM python:3.13-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=nort_site.settings

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=assets /app/static/css/site.css ./static/css/site.css
COPY --from=assets /app/static/js/vendor ./static/js/vendor

RUN SECRET_KEY=build-only-not-for-runtime \
    DEBUG=False \
    python manage.py collectstatic --noinput

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
