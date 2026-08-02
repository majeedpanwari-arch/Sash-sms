import time
import math
from functools import wraps
from flask import request, jsonify, render_template, flash, current_app, make_response

class TieredRateLimiter:
    """
    In-memory Rate Limiter with Sliding Window & Exponential Backoff.
    Handles per-IP and per-Account auth protection with configurable thresholds.
    """
    def __init__(self):
        # Sliding window requests tracking: { key: [timestamps] }
        self._requests = {}
        # Exponential backoff failures tracking:
        # { "ip:<ip>": { "count": N, "locked_until": timestamp, "last_failure": timestamp } }
        # { "user:<username>": { "count": N, "locked_until": timestamp, "last_failure": timestamp } }
        self._auth_failures = {}

    def _get_client_ip(self):
        if request.headers.getlist("X-Forwarded-For"):
            return request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
        return request.remote_addr or '127.0.0.1'

    def _clean_sliding_window(self, key, window_seconds):
        now = time.time()
        if key in self._requests:
            self._requests[key] = [t for t in self._requests[key] if now - t < window_seconds]
        else:
            self._requests[key] = []
        return self._requests[key]

    def is_rate_limited(self, key, limit, window_seconds):
        """Check sliding window request limit."""
        timestamps = self._clean_sliding_window(key, window_seconds)
        if len(timestamps) >= limit:
            return True
        timestamps.append(time.time())
        return False

    def check_auth_exponential_backoff(self, username=None):
        """
        Check if current attempt is blocked by exponential backoff (per-IP or per-Account).
        Returns (is_blocked, remaining_seconds).
        """
        ip = self._get_client_ip()
        now = time.time()
        window = current_app.config.get('AUTH_BACKOFF_WINDOW_SECONDS', 900)

        ip_key = f"ip:{ip}"
        account_key = f"user:{username.lower()}" if username else None

        remaining = 0.0

        for key in [ip_key, account_key]:
            if not key or key not in self._auth_failures:
                continue
            entry = self._auth_failures[key]
            # Expire old failures if beyond window
            if now - entry.get('last_failure', 0) > window:
                del self._auth_failures[key]
                continue

            if entry.get('locked_until', 0) > now:
                rem = entry['locked_until'] - now
                if rem > remaining:
                    remaining = rem

        if remaining > 0:
            return True, math.ceil(remaining)
        return False, 0

    def record_auth_failure(self, username=None):
        """
        Record a failed auth attempt for both IP and Account, applying exponential backoff delay.
        """
        ip = self._get_client_ip()
        now = time.time()
        
        initial = current_app.config.get('AUTH_BACKOFF_INITIAL_DELAY', 2.0)
        factor = current_app.config.get('AUTH_BACKOFF_FACTOR', 2.0)
        max_delay = current_app.config.get('AUTH_BACKOFF_MAX_DELAY', 300.0)

        ip_key = f"ip:{ip}"
        account_key = f"user:{username.lower()}" if username else None

        for key in [ip_key, account_key]:
            if not key:
                continue
            if key not in self._auth_failures:
                self._auth_failures[key] = {'count': 0, 'locked_until': 0, 'last_failure': now}
            
            entry = self._auth_failures[key]
            entry['count'] += 1
            entry['last_failure'] = now

            # Exponential backoff formula: initial * (factor ** (count - 1))
            delay = min(initial * (factor ** (entry['count'] - 1)), max_delay)
            entry['locked_until'] = now + delay

    def record_auth_success(self, username=None):
        """
        Reset failed attempt counters for IP and Account upon successful authentication.
        """
        ip = self._get_client_ip()
        ip_key = f"ip:{ip}"
        account_key = f"user:{username.lower()}" if username else None

        if ip_key in self._auth_failures:
            del self._auth_failures[ip_key]
        if account_key and account_key in self._auth_failures:
            del self._auth_failures[account_key]

rate_limiter = TieredRateLimiter()

def rate_limit_auth(f):
    """Stricter rate limiting decorator for authentication routes (e.g. login/register)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = rate_limiter._get_client_ip()
        limit = current_app.config.get('RATELIMIT_AUTH_LIMIT', 5)
        window = current_app.config.get('RATELIMIT_AUTH_WINDOW', 60)

        if rate_limiter.is_rate_limited(f"auth_window:{ip}", limit, window):
            if request.is_json:
                res = jsonify({'error': 'Rate limit exceeded on authentication. Please try again later.'})
                res.status_code = 429
                res.headers['Retry-After'] = str(window)
                return res
            flash(f'Rate limit exceeded for authentication. Please wait {window} seconds.', 'danger')
            return make_response(render_template('auth/login.html'), 429)
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_public(f):
    """Moderate rate limiting decorator for public endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = rate_limiter._get_client_ip()
        limit = current_app.config.get('RATELIMIT_PUBLIC_LIMIT', 60)
        window = current_app.config.get('RATELIMIT_PUBLIC_WINDOW', 60)

        if rate_limiter.is_rate_limited(f"public:{ip}", limit, window):
            res = jsonify({'error': 'Too many requests on public endpoint. Please slow down.'})
            res.status_code = 429
            res.headers['Retry-After'] = str(window)
            return res
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_authenticated(f):
    """Looser rate limiting decorator for authenticated user actions."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        user_id = str(current_user.id) if (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated) else rate_limiter._get_client_ip()
        limit = current_app.config.get('RATELIMIT_AUTHENTICATED_LIMIT', 300)
        window = current_app.config.get('RATELIMIT_AUTHENTICATED_WINDOW', 60)

        if rate_limiter.is_rate_limited(f"user_action:{user_id}", limit, window):
            if request.is_json:
                res = jsonify({'error': 'Rate limit exceeded for user actions. Please slow down.'})
                res.status_code = 429
                res.headers['Retry-After'] = str(window)
                return res
            flash('You are performing actions too quickly. Please slow down.', 'warning')
            return make_response('Rate limit exceeded', 429)
        return f(*args, **kwargs)
    return decorated_function
