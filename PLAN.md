# Resume Roaster — Implementation Plan

## Context
Greenfield Django 5 + Vue 3 app. Users upload a resume (PDF/DOCX) and paste a job description; the AI scores the match, rewrites weak bullets, flags ATS issues, calculates hire probability, and generates a cover letter. Monetized via **per-upload Stripe payments**. Resume files stored locally in dev, on AWS S3 in production. Security is the primary constraint throughout.

---

## Key Decisions (from planning session)
- **Payments**: Per-upload Stripe payment (not subscription). Price and currency come from env vars.
- **AI model**: Configurable via env var `ANTHROPIC_MODEL` (not hardcoded). Defaults to `claude-sonnet-4-6`.
- **Frontend UI**: Vue 3 + **Vuetify 3** (Material Design component library).
- **Auth**: JWT (djangorestframework-simplejwt), email-based login.
- **Async**: Celery + Redis for AI tasks (fire-and-forget, poll for results).

---

## Project Structure
```
resume_roaster/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   ├── asgi.py
│   │   └── __init__.py
│   ├── apps/
│   │   ├── accounts/   # User, Profile, JWT auth
│   │   ├── resumes/    # Upload, MIME validation, text extraction
│   │   ├── analysis/   # AI pipeline, Celery tasks, rate limiting
│   │   └── payments/   # Stripe per-upload checkout + webhook
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── api/         # axios client + per-resource helpers
│   │   ├── components/  # reusable Vuetify-based components
│   │   ├── stores/      # Pinia: auth, resume, analysis, payment
│   │   ├── views/       # page-level components
│   │   └── router/      # Vue Router with auth guards
│   ├── vite.config.js
│   └── package.json
├── docker-compose.yml   # postgres + redis for dev
├── .env.example
└── CLAUDE.md
```

---

## Environment Variables (`.env.example`)
```
# Django
DJANGO_SECRET_KEY=change-me
DJANGO_SETTINGS_MODULE=config.settings.dev
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Redis / Celery
REDIS_URL=redis://localhost:6379/0

# AWS S3 (leave blank in dev — uses local filesystem)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Anthropic — model is configurable, not hardcoded
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-4-6

# Stripe per-upload pricing
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_UPLOAD_PRICE_USD=2.00      # price per resume analysis, e.g. 2.00
STRIPE_CURRENCY=usd                # ISO currency code, e.g. usd, gbp, eur

# CORS (prod only)
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_STRIPE_PUBLISHABLE_KEY=
```

---

## Phase 0 — Scaffolding & Infrastructure ✅

**Goal**: Directory skeleton, Docker, dependency manifests, `.env.example`. No application code yet.

### Files to create
- `docker-compose.yml` — postgres:16 + redis:7-alpine services
- `.env.example` — full template (see above), never commit `.env`
- `backend/requirements/base.txt`
- `backend/requirements/dev.txt`: `-r base.txt` + `factory-boy`, `pytest-django`, `coverage`
- `backend/requirements/prod.txt`: `-r base.txt` + `gunicorn`, `whitenoise`, `sentry-sdk`
- `frontend/package.json` dependencies: `vue@3`, `vue-router@4`, `pinia`, `vuetify@3`, `axios`, `@mdi/font`

---

## Phase 1 — Django Auth Backend ✅

**Goal**: Working Django project, custom User + Profile model, JWT endpoints, health check.

### Key files
- `backend/config/settings/base.py`:
  - `AUTH_USER_MODEL = 'accounts.User'`
  - `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticated']`
  - JWT: access 60 min, refresh 7 days, `ROTATE_REFRESH_TOKENS = True`
  - `FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024`
  - `ANTHROPIC_MODEL = config('ANTHROPIC_MODEL', default='claude-sonnet-4-6')` ← from env
  - Global throttle: `anon: 20/hour`, `user: 100/hour`, `ai_endpoints: 10/hour`
  - `STRIPE_UPLOAD_PRICE_USD = config('STRIPE_UPLOAD_PRICE_USD', default='2.00')`
  - `STRIPE_CURRENCY = config('STRIPE_CURRENCY', default='usd')`

- `backend/config/settings/dev.py`: SQLite, local `MEDIA_ROOT`, `CORS_ALLOWED_ORIGINS = ['http://localhost:5173']`

- `backend/config/settings/prod.py`:
  - `DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'`
  - `AWS_QUERYSTRING_AUTH = True`, `AWS_QUERYSTRING_EXPIRE = 900` (15-min presigned URLs)
  - `AWS_DEFAULT_ACL = None` (objects private, no public ACL)
  - `AWS_S3_SIGNATURE_VERSION = 's3v4'`
  - `SECURE_SSL_REDIRECT`, `HSTS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `X_FRAME_OPTIONS = 'DENY'`

- `backend/apps/accounts/models.py`: `User(AbstractUser)` with `USERNAME_FIELD = 'email'`; `Profile` with `subscription_tier`, `credits_remaining`

- `backend/apps/accounts/serializers.py`: `RegisterSerializer` with password confirmation + `validate_password`

- `backend/apps/accounts/urls.py`:
  - `POST /api/v1/auth/register/` — `AllowAny`
  - `POST /api/v1/auth/token/` — `AllowAny`
  - `POST /api/v1/auth/token/refresh/` — `AllowAny`
  - `GET/PATCH /api/v1/auth/me/` — authenticated

- `backend/config/celery.py`: standard Celery setup, `autodiscover_tasks()`

### Test checklist
- [ ] Register creates User + Profile (via signal)
- [ ] Login returns access + refresh tokens
- [ ] Token refresh rotates tokens
- [ ] `GET /auth/me/` without token → 401
- [ ] `GET /health/` → 200 (no auth)

---

## Phase 2 — Resume Upload & Storage

**Goal**: Secure file upload with MIME validation, text extraction, per-user storage paths, presigned URL serving.

### Key files
- `backend/apps/resumes/models.py`:
  ```python
  def resume_upload_path(instance, filename):
      ext = filename.rsplit('.', 1)[-1].lower()
      return f"resumes/{instance.user.id}/{uuid.uuid4()}.{ext}"

  class Resume(models.Model):
      user, file, original_filename, file_size, mime_type,
      parsed_text, uploaded_at, is_paid (BooleanField default=False)
  ```
  `is_paid` tracks whether the user has paid for analysis of this resume.

- `backend/apps/resumes/validators.py`:
  - `validate_resume_file(file)` — reads first 2048 bytes via `python-magic` to detect MIME type
  - Rejects anything not `application/pdf` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - Rejects files > 5MB
  - **Extension alone is never trusted**

- `backend/apps/resumes/parsers.py`: `extract_text_from_pdf()` via `pypdf`, `extract_text_from_docx()` via `python-docx`

- `backend/apps/resumes/views.py`:
  - `ResumeListCreateView`: `get_queryset()` always filters `user=request.user`
  - `ResumeDetailView`: `get_object_or_404(Resume, id=pk, user=request.user)` — ownership enforced at query level
  - On delete: `instance.file.delete(save=False)` removes from storage before DB deletion

- `backend/apps/resumes/serializers.py`:
  - `get_download_url()` calls `storage.url(obj.file.name)` — S3Boto3Storage auto-generates presigned URL; local dev uses Django's serve

### Security controls
- MIME checked via magic bytes, not extension
- Files stored at unpredictable UUIDs under `resumes/{user_id}/...`
- Never return raw S3 key or bucket name to frontend
- Presigned URL TTL: 15 minutes in prod

### Test checklist
- [ ] Upload valid PDF → 201
- [ ] Upload `.exe` renamed `.pdf` → 400 (MIME rejected)
- [ ] Upload 6MB file → 400
- [ ] Other user's resume → 404
- [ ] Download URL is presigned (not raw S3 path) in prod

---

## Phase 3 — AI Analysis Pipeline

**Goal**: Submit analysis → immediate 202 response → Celery runs AI → poll for result. Rate limited. Prompt injection mitigated.

### Key files
- `backend/apps/analysis/models.py`:
  - `JobDescription`: user FK, title, company, raw_text
  - `AnalysisResult`: UUID PK, resume FK, job_desc FK, status (pending/processing/done/failed), match_score, ats_flags (JSON), rewritten_bullets (JSON), hire_probability (Float), cover_letter (Text)

- `backend/apps/analysis/ai_service.py`:
  - `sanitize_text(text, max_length)`: truncates, HTML-encodes `<>`, strips known injection patterns
  - `build_analysis_prompt(resume_text, jd_text)`: structured XML-tagged prompt requesting JSON-only response
  - `run_analysis(resume_text, jd_text)`: reads model from `settings.ANTHROPIC_MODEL`

- `backend/apps/analysis/tasks.py`: Celery task with `max_retries=2`, `default_retry_delay=30`

- `backend/apps/analysis/throttles.py`: `AIAnalysisThrottle(UserRateThrottle)` — scope `ai_endpoints`, rate `10/hour`

- `backend/apps/analysis/views.py`:
  - `AnalysisCreateView`: checks `is_paid=True` before enqueueing; returns 202 immediately
  - `AnalysisDetailView`: ownership via FK traversal `resume__user=request.user`

### Test checklist
- [ ] `POST /api/v1/analysis/` → 202 with analysis_id
- [ ] Celery worker transitions status pending → processing → done
- [ ] `GET /api/v1/analysis/{id}/` returns live status
- [ ] Another user's analysis → 404
- [ ] Unpaid resume → 402/403
- [ ] >10 requests/hour → 429
- [ ] Injection string in JD → sanitized in DB

---

## Phase 4 — Stripe Per-Upload Payments

**Goal**: User pays per resume analysis via Stripe Checkout. Price and currency from env. Webhook marks resume as paid.

### Flow
1. User uploads resume → `is_paid = False`
2. User selects resume for analysis → frontend calls `POST /api/v1/payments/checkout/` with `resume_id`
3. Backend creates Stripe Checkout Session (amount from `STRIPE_UPLOAD_PRICE_USD`, currency from `STRIPE_CURRENCY`)
4. Frontend redirects to Stripe-hosted checkout page
5. On payment success, Stripe sends webhook → backend sets `resume.is_paid = True`
6. User redirected back to app → can now submit analysis

### Key files
- `backend/apps/payments/stripe_service.py`: `create_upload_checkout_session()` — price/currency 100% from env
- `backend/apps/payments/views.py`:
  - `CreateCheckoutView`: validates resume ownership, returns `{checkout_url}`
  - `stripe_webhook`: `@csrf_exempt`, verifies Stripe signature before processing; sets `is_paid=True`

### Test checklist
- [ ] `POST /api/v1/payments/checkout/` with valid resume → returns Stripe URL
- [ ] Checkout with another user's resume_id → 404
- [ ] Webhook with bad signature → 400
- [ ] Webhook with valid signature → `resume.is_paid = True`
- [ ] `POST /api/v1/analysis/` on paid resume → 202
- [ ] `POST /api/v1/analysis/` on unpaid resume → 402

---

## Phase 5 — Vue 3 + Vuetify Frontend

**Goal**: Full SPA with Vuetify 3 Material Design components, auth guards, upload flow, payment redirect, polling result display.

### Key views
| View | Vuetify components |
|---|---|
| `LoginView.vue` | `v-card`, `v-text-field`, `v-btn` |
| `RegisterView.vue` | `v-card`, `v-text-field`, `v-btn`, `v-alert` |
| `DashboardView.vue` | `v-data-table`, `v-chip` (status), `v-btn` |
| `UploadResumeView.vue` | `v-file-input`, `v-progress-linear`, `v-btn` |
| `NewAnalysisView.vue` | `v-select` (resume picker), `v-textarea` (JD), `v-btn` |
| `AnalysisResultView.vue` | `v-progress-circular` (match score), `v-expansion-panels`, `v-chip` (ATS), `v-alert` (hire probability), `v-card` (cover letter) |
| `AccountView.vue` | `v-list`, `v-btn` |

### Pinia stores
- `stores/auth.js`: tokens, login/refresh/logout
- `stores/resume.js`: list, upload, delete
- `stores/analysis.js`: submit + poll every 3s (max 60 attempts)
- `stores/payment.js`: `initiateCheckout(resumeId)` → redirect to Stripe URL

### Test checklist
- [ ] Unauthed visit to `/dashboard` redirects to `/login`
- [ ] Login persists tokens in localStorage
- [ ] Token refresh happens transparently on 401
- [ ] Upload triggers Stripe checkout redirect
- [ ] Polling spinner visible while AI processes
- [ ] Result page renders score ring, ATS chips, bullet diffs, cover letter
- [ ] Logout clears tokens

---

## Phase 6 — Production Hardening ✅ (merged into prod.py)

**Goal**: S3 storage wiring, logging config, security headers, gunicorn/celery config.

### Deployment
- `uvicorn config.asgi:application --workers 4`
- `celery -A config worker --loglevel=warning --concurrency=4`

### Minimal IAM policy
```json
{
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
    "Resource": "arn:aws:s3:::YOUR-BUCKET/resumes/*"
  }]
}
```

---

## Security Audit Summary

| Requirement | Implementation |
|---|---|
| No secrets in code | `python-decouple` reads all values from `.env` |
| File: PDF/DOCX only, max 5MB | `validators.py` — `python-magic` reads magic bytes |
| MIME validation (not extension) | Magic byte inspection, not filename extension |
| S3 presigned URLs, 15-min TTL | `AWS_QUERYSTRING_AUTH=True`, `EXPIRE=900` |
| Raw S3 paths never exposed | `get_download_url()` always calls `storage.url()` |
| Per-user AI rate limiting | `AIAnalysisThrottle`: 10/hour |
| Auth on all endpoints | DRF `IsAuthenticated` default; `AllowAny` explicit only on register/login/webhook |
| CORS restricted | `CORS_ALLOWED_ORIGINS` from env, no wildcard |
| CSRF enabled | Django middleware; only Stripe webhook is `@csrf_exempt` |
| Parameterized queries | ORM only; never `format()`/`%` in SQL |
| Prompt injection prevention | `sanitize_text()`: truncate, encode `<>`, strip known patterns |
| Ownership on every query | All querysets: `filter(user=request.user)` or FK traversal |
| Production security headers | `prod.py` settings |
| AI model configurable | `ANTHROPIC_MODEL` from env; never hardcoded |
| Price and currency configurable | `STRIPE_UPLOAD_PRICE_USD` + `STRIPE_CURRENCY` from env |
| Stripe webhook verified | Signature check before any processing; 400 on failure |

---

## Implementation Status
```
Phase 0: Scaffolding         ✅ Complete
Phase 1: Auth Backend        ✅ Complete
Phase 2: Resume Upload       ⏳ Next
Phase 3: AI Analysis         ⏳ Pending
Phase 4: Stripe Payments     ⏳ Pending
Phase 5: Vue + Vuetify SPA   ⏳ Pending
Phase 6: Prod Hardening      ✅ Complete (merged into prod.py)
```
