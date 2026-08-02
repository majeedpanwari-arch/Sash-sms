import os
import secrets
from datetime import timedelta

# Environment detection
IS_VERCEL = bool(
    os.environ.get('VERCEL') or
    os.environ.get('VERCEL_ENV') or
    os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
)


def _get_db_uri():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        if db_url.startswith('postgres://'):
            return db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    if IS_VERCEL:
        return 'sqlite:////tmp/sash_sms.db'
    return 'sqlite:///abyss_sms.db'


class Config:
    # ── Secret key ──────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sash_sms_prod_secret_key_9981247128934'

    # ── Database ─────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = _get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Session & Cookies ────────────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE   = False
    REMEMBER_COOKIE_SECURE  = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ── CSRF ────────────────────────────────────────────────────────────────
    WTF_CSRF_ENABLED    = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ── Tiered Rate Limiting & Exponential Backoff Configuration ───────────────
    # Auth Routes (Stricter limits)
    RATELIMIT_AUTH_LIMIT          = int(os.environ.get('RATELIMIT_AUTH_LIMIT', 5))          # max 5 attempts
    RATELIMIT_AUTH_WINDOW         = int(os.environ.get('RATELIMIT_AUTH_WINDOW', 60))        # per 60s
    # Public Endpoints (Moderate limits)
    RATELIMIT_PUBLIC_LIMIT        = int(os.environ.get('RATELIMIT_PUBLIC_LIMIT', 60))        # max 60 requests
    RATELIMIT_PUBLIC_WINDOW       = int(os.environ.get('RATELIMIT_PUBLIC_WINDOW', 60))      # per 60s
    # Authenticated User Actions (Looser limits)
    RATELIMIT_AUTHENTICATED_LIMIT = int(os.environ.get('RATELIMIT_AUTHENTICATED_LIMIT', 300))# max 300 requests
    RATELIMIT_AUTHENTICATED_WINDOW= int(os.environ.get('RATELIMIT_AUTHENTICATED_WINDOW', 60)) # per 60s

    # Exponential Backoff Parameters for Auth Routes (Per-IP & Per-Account)
    AUTH_BACKOFF_INITIAL_DELAY    = float(os.environ.get('AUTH_BACKOFF_INITIAL_DELAY', 2.0)) # Initial delay in seconds
    AUTH_BACKOFF_FACTOR           = float(os.environ.get('AUTH_BACKOFF_FACTOR', 2.0))        # Multiplier (2s, 4s, 8s, 16s...)
    AUTH_BACKOFF_MAX_DELAY        = float(os.environ.get('AUTH_BACKOFF_MAX_DELAY', 300.0))    # Maximum delay cap (5 minutes)
    AUTH_BACKOFF_WINDOW_SECONDS   = int(os.environ.get('AUTH_BACKOFF_WINDOW_SECONDS', 900))   # Memory window (15 mins)

    # ── Registration ─────────────────────────────────────────────────────────
    REGISTRATION_ENABLED = os.environ.get('REGISTRATION_ENABLED', 'true').lower() == 'true'

    # ── Webhook secret ───────────────────────────────────────────────────────
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')

    # ── Telegram Bot API Secret ─────────────────────────────────────────────
    BOT_API_SECRET = os.environ.get('BOT_API_SECRET', 'bot_secret_key_12345')

    # ── Bulk SMS cap ─────────────────────────────────────────────────────────
    BULK_SMS_MAX_DESTINATIONS = int(os.environ.get('BULK_SMS_MAX_DESTINATIONS', '500'))

    # ── CORS whitelist ───────────────────────────────────────────────────────
    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get('CORS_ORIGINS', '').split(',')
        if o.strip()
    ]


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = False if IS_VERCEL else True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SESSION_COOKIE_SECURE = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}
