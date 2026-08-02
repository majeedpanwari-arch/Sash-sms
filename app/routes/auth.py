from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.activity import ActivityLog
from datetime import datetime, timedelta
from functools import wraps
import re
import random

from app.services.rate_limiter import rate_limiter, rate_limit_auth, rate_limit_public, rate_limit_authenticated

auth_bp = Blueprint('auth', __name__)


def _refresh_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    session['captcha_question'] = f"{a} + {b}"
    session['captcha_answer']   = a + b


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit_auth
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'GET':
        _refresh_captcha()
        return render_template('auth/login.html')

    # POST handler
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    captcha  = request.form.get('capt', '')

    # 1. Exponential Backoff Check (per-IP and per-Account)
    is_blocked, remaining = rate_limiter.check_auth_exponential_backoff(username=username)
    if is_blocked:
        flash(f'Exponential backoff active due to recent failed attempts. Please wait {remaining} second(s) before trying again.', 'danger')
        _refresh_captcha()
        res = make_response(render_template('auth/login.html'), 429)
        res.headers['Retry-After'] = str(remaining)
        return res

    if not username or not password:
        flash('Please enter username and password.', 'danger')
        _refresh_captcha()
        return render_template('auth/login.html')

    # Verify captcha
    correct_answer = session.get('captcha_answer', -9999)
    try:
        if int(captcha) != correct_answer:
            rate_limiter.record_auth_failure(username=username)
            flash('Incorrect captcha answer.', 'danger')
            _refresh_captcha()
            return render_template('auth/login.html')
    except ValueError:
        rate_limiter.record_auth_failure(username=username)
        flash('Invalid captcha — please enter a number.', 'danger')
        _refresh_captcha()
        return render_template('auth/login.html')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        if not user.is_active:
            flash('Your account has been deactivated.', 'warning')
            _refresh_captcha()
            return render_template('auth/login.html')

        if not user.api_token:
            user.generate_api_token()

        user.login_attempts = 0
        user.locked_until   = None
        user.last_login     = datetime.utcnow()
        db.session.commit()

        # Reset exponential backoff on successful login
        rate_limiter.record_auth_success(username=username)

        ActivityLog.log(
            user.id, 'login', 'User logged in',
            ip_address=ip, user_agent=request.user_agent.string
        )

        login_user(user, remember=True)
        session.permanent = True

        flash(f'Welcome back, {user.username}!', 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/') and not next_page.startswith('//'):
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))

    else:
        # Failed login — record exponential backoff failure per-IP & per-Account
        rate_limiter.record_auth_failure(username=username)
        if user:
            user.login_attempts += 1
            db.session.commit()

        flash('Invalid username or password. Exponential delay applied.', 'danger')

    _refresh_captcha()
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    ActivityLog.log(current_user.id, 'logout', 'User logged out', ip_address=ip)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration page - only allows Agent or Client roles.
    Admin cannot be created through registration.
    """
    if not current_app.config.get('REGISTRATION_ENABLED', False):
        flash('Public registration is disabled. Contact an administrator.', 'warning')
        return redirect(url_for('auth.login'))

    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username         = request.form.get('username', '').strip()
        email            = request.form.get('email', '').strip()
        password         = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        account_type     = request.form.get('account_type', 'client')  # 'agent' or 'client'

        errors = []

        if len(username) < 4:
            errors.append('Username must be at least 4 characters.')
        if len(username) > 80:
            errors.append('Username must be less than 80 characters.')
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')

        if not re.match(r'^[\w\.\-]+@[\w\.\-]+\.\w+$', email):
            errors.append('Please enter a valid email address.')

        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        if password != password_confirm:
            errors.append('Passwords do not match.')

        # Only allow agent or client roles
        if account_type not in ['agent', 'client']:
            errors.append('Invalid account type. Please select Agent or Client.')

        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        # Block test123 registration
        if username.lower() == 'test123':
            errors.append('This username is reserved.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')

        from app.models.user import Role
        role = Role.query.filter_by(name=account_type).first()
        if not role:
            role = Role(name=account_type, display_name=account_type.capitalize(), permissions='[]')
            db.session.add(role)
            db.session.commit()

        user = User(
            username=username,
            email=email,
            role=role,
            is_active=True
        )
        user.set_password(password)
        user.generate_api_token()

        db.session.add(user)
        db.session.commit()

        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        ActivityLog.log(user.id, 'register', f'New {account_type} account registered', ip_address=ip)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ── Error handlers ────────────────────────────────────────────────────────────

@auth_bp.app_errorhandler(401)
def unauthorized(e):
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('auth.login', next=request.path))


@auth_bp.app_errorhandler(403)
def forbidden(e):
    flash('You do not have permission to access this page.', 'danger')
    return redirect(url_for('main.dashboard'))


@auth_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@auth_bp.app_errorhandler(500)
def server_error(e):
    db.session.rollback()
    flash('An internal error occurred. Please try again later.', 'danger')
    return redirect(url_for('main.dashboard'))
