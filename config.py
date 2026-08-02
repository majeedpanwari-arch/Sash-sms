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

    # ── Rate limiting ────────────────────────────────────────────────────────
    LOGIN_ATTEMPT_LIMIT  = 5
    LOGIN_ATTEMPT_WINDOW = 300

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
