# Resume Roaster - Claude Code Instructions

## Project Overview
Resume Roaster is a Django + Vue 3 web app that lets users upload resumes and job descriptions, then uses AI (Claude) to score the match, rewrite weak bullets, flag ATS issues, and generate cover letters.

## Tech Stack
- **Backend**: Django 5 + Django REST Framework
- **Frontend**: Vue 3 (Composition API) + Vite + Pinia + Vue Router
- **Storage**: Local filesystem in dev, AWS S3 in production (django-storages + boto3)
- **AI**: Anthropic Claude API (`claude-sonnet-4-6` default)
- **Auth**: JWT via `djangorestframework-simplejwt`
- **Payments**: Stripe
- **DB**: PostgreSQL (prod), SQLite (dev)
- **Task Queue**: Celery + Redis (for async AI processing)

## Security - ALWAYS PRIORITIZE
- Never commit secrets. All secrets in `.env` (never committed).
- Validate and sanitize ALL file uploads: allowed types (PDF, DOCX only), max 5MB, virus-scan stub.
- Use S3 presigned URLs — never expose raw S3 URLs or bucket names publicly.
- Rate-limit AI endpoints (per user, per hour).
- Enforce authentication on all non-public endpoints.
- Use Django's CSRF protection; configure CORS tightly.
- Parameterized queries only — never raw SQL string formatting.
- Sanitize AI prompt inputs to prevent prompt injection.
- Use `SECURE_*` Django settings in production (HTTPS, HSTS, secure cookies).
- User files are private — users may only access their own uploads.

## Project Structure
```
resume_roaster/          # repo root
├── backend/             # Django project
│   ├── config/          # settings, urls, wsgi
│   ├── apps/
│   │   ├── accounts/    # user auth, profiles, subscriptions
│   │   ├── resumes/     # resume upload, storage, parsing
│   │   ├── analysis/    # AI analysis tasks
│   │   └── payments/    # Stripe integration
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   └── manage.py
├── frontend/            # Vue 3 app
│   ├── src/
│   │   ├── api/         # axios API clients
│   │   ├── components/
│   │   ├── stores/      # Pinia stores
│   │   ├── views/
│   │   └── router/
│   └── vite.config.js
├── .env.example         # template — never commit .env
├── docker-compose.yml   # dev environment
└── CLAUDE.md
```

## Development Workflow
- Run backend: `cd backend && python manage.py runserver`
- Run frontend: `cd frontend && npm run dev`
- Run tests: `cd backend && python manage.py test` / `cd frontend && npm run test`
- Always run tests before considering a feature complete.

## Key Conventions
- API versioned at `/api/v1/`
- DRF serializers validate all input.
- Never return raw file paths or S3 keys to the frontend — use presigned URLs with short TTL (15 min).
- AI calls are async (Celery tasks) — return a job ID immediately, poll for results.
- Use Django's `get_object_or_404` with ownership checks: `Resume.objects.get(id=id, user=request.user)`.
- Log errors but never log PII or file contents.
