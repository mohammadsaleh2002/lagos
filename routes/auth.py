from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required

from app import get_db
from models.user import User
from translations import get_text

auth_bp = Blueprint('auth', __name__)


def _t(key, **kwargs):
    lang = session.get('lang', 'fa')
    return get_text(key, lang, **kwargs)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()

        user = User.find_by_username(db, username)
        if user and user.verify_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))

        flash(_t('invalid_credentials'), 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    """Initial setup: create the first admin user."""
    db = get_db()
    if db.users.count_documents({}) > 0:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        email = request.form.get('email', '').strip()

        if not username or not password:
            flash(_t('username_password_required'), 'danger')
        elif password != password2:
            flash(_t('passwords_no_match'), 'danger')
        else:
            User.create(db, username, password, email)
            flash(_t('admin_created'), 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/setup.html')
