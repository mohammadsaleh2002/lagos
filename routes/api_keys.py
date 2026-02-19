from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required

from app import get_db, get_fernet
from models.api_key import (
    PROVIDERS, create_api_key, get_all_api_keys, get_api_key,
    delete_api_key, toggle_api_key, reset_key_errors,
)
from translations import get_text

api_keys_bp = Blueprint('api_keys', __name__)


def _t(key, **kwargs):
    lang = session.get('lang', 'fa')
    return get_text(key, lang, **kwargs)


@api_keys_bp.route('/')
@login_required
def list_keys():
    db = get_db()
    keys = get_all_api_keys(db)
    # Mask actual key values
    for k in keys:
        k['key_masked'] = '***' + k['key'][-8:] if len(k['key']) > 8 else '***'
    return render_template('api_keys/list.html', keys=keys, providers=PROVIDERS)


@api_keys_bp.route('/add', methods=['POST'])
@login_required
def add_key():
    db = get_db()
    provider = request.form.get('provider', '')
    key = request.form.get('api_key', '').strip()
    name = request.form.get('name', '').strip()

    if provider not in PROVIDERS:
        flash(_t('invalid_provider'), 'danger')
    elif not key:
        flash(_t('api_key_required'), 'danger')
    else:
        create_api_key(db, get_fernet(), provider, key, name)
        flash(_t('api_key_added'), 'success')

    return redirect(url_for('api_keys.list_keys'))


@api_keys_bp.route('/<key_id>/toggle', methods=['POST'])
@login_required
def toggle(key_id):
    db = get_db()
    toggle_api_key(db, key_id)
    flash(_t('key_toggled'), 'success')
    return redirect(url_for('api_keys.list_keys'))


@api_keys_bp.route('/<key_id>/reset-errors', methods=['POST'])
@login_required
def reset_errors(key_id):
    db = get_db()
    reset_key_errors(db, key_id)
    flash(_t('errors_reset'), 'success')
    return redirect(url_for('api_keys.list_keys'))


@api_keys_bp.route('/<key_id>/delete', methods=['POST'])
@login_required
def delete(key_id):
    db = get_db()
    delete_api_key(db, key_id)
    flash(_t('key_deleted'), 'success')
    return redirect(url_for('api_keys.list_keys'))
