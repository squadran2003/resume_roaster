from .base import *  # noqa: F401, F403
import dj_database_url
from decouple import config, Csv

DEBUG = False

_db_url = config("DATABASE_URL")

DATABASES = {
    "default": dj_database_url.config(
        default=_db_url,
        conn_max_age=600,
        # Railway internal connections (.railway.internal) don't use SSL;
        # only require SSL for external/public database URLs.
        ssl_require="railway.internal" not in _db_url,
    )
}

# --- Railway Object Storage (S3-compatible) ---
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = config("RAILWAY_BUCKET_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("RAILWAY_BUCKET_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("RAILWAY_BUCKET_NAME")
AWS_S3_REGION_NAME = config("RAILWAY_BUCKET_REGION", default="auto")
AWS_S3_ENDPOINT_URL = config("RAILWAY_BUCKET_ENDPOINT_URL")
AWS_QUERYSTRING_AUTH = True          # presigned URLs
AWS_DEFAULT_ACL = None               # objects private; no public ACL
AWS_QUERYSTRING_EXPIRE = 900         # 15-min TTL
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_FILE_OVERWRITE = False
AWS_S3_ADDRESSING_STYLE = "path"     # required for non-AWS S3-compatible endpoints

# --- Security headers ---
# Railway terminates TLS at its proxy; SSL redirect is handled there.
# Enabling SECURE_SSL_REDIRECT here breaks Railway's internal HTTP health checks.
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# --- CORS ---
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# --- CSRF trusted origins (required by Django 4+ when behind a proxy) ---
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv())

# Railway terminates TLS at its proxy — trust the forwarded header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Static files via WhiteNoise ---
MIDDLEWARE = [  # noqa: F405
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
] + MIDDLEWARE[1:]  # noqa: F405

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Logging (prod) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
