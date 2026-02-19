from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required

from app import get_db
from models.project import create_project, get_project, get_all_projects, update_project, delete_project
from services.scheduler import sync_project_jobs, remove_project_jobs
from translations import get_text

projects_bp = Blueprint('projects', __name__)


def _t(key, **kwargs):
    lang = session.get('lang', 'fa')
    return get_text(key, lang, **kwargs)


def _parse_project_form(form):
    """Extract project data from form submission."""
    return {
        'name': form.get('name', '').strip(),
        'db_key': form.get('db_key', '').strip(),
        'company_name': form.get('company_name', '').strip(),
        'business_field': form.get('business_field', '').strip(),
        'services_products': form.get('services_products', '').strip(),
        'about_company': form.get('about_company', '').strip(),
        'lang': form.get('lang', 'fa').strip(),
        'address': form.get('address', '').strip(),
        'phone': form.get('phone', '').strip(),
        'mobile_phone': form.get('mobile_phone', '').strip(),
        'email': form.get('email', '').strip(),
        'keyword': form.get('keyword', '').strip(),
        'bullet1': form.get('bullet1', '').strip(),
        'bullet2': form.get('bullet2', '').strip(),
        'bullet3': form.get('bullet3', '').strip(),
        'wordpress': {
            'url': form.get('wp_url', '').strip(),
            'username': form.get('wp_username', '').strip(),
            'app_password': form.get('wp_app_password', '').strip(),
            'category_id': int(form.get('wp_category_id', 0) or 0),
        },
        'telegram': {
            'bot_token': form.get('tg_bot_token', '').strip(),
            'chat_id': form.get('tg_chat_id', '').strip(),
        },
        'schedule': {
            'creation_enabled': form.get('creation_enabled') == 'on',
            'creation_interval_minutes': int(form.get('creation_interval', 60) or 60),
            'publish_enabled': form.get('publish_enabled') == 'on',
            'publish_interval_minutes': int(form.get('publish_interval', 20) or 20),
        },
        'content_settings': {
            'number_of_content': int(form.get('number_of_content', 100) or 100),
            'number_of_keyword': int(form.get('number_of_keyword', 20) or 20),
            'number_of_ads': int(form.get('number_of_ads', 50) or 50),
            'article_word_count': int(form.get('article_word_count', 3500) or 3500),
            'article_chapters': int(form.get('article_chapters', 10) or 10),
            'ads_word_count': int(form.get('ads_word_count', 800) or 800),
        },
    }


@projects_bp.route('/')
@login_required
def list_projects():
    db = get_db()
    projects = get_all_projects(db)
    return render_template('projects/list.html', projects=projects)


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        db = get_db()
        data = _parse_project_form(request.form)

        if not data['name'] or not data['db_key']:
            flash(_t('name_key_required'), 'danger')
            return render_template('projects/create.html', project=data)

        try:
            pid = create_project(db, data)
            project = get_project(db, pid)
            sync_project_jobs(project)
            flash(_t('project_created'), 'success')
            return redirect(url_for('projects.list_projects'))
        except Exception as e:
            flash(f'{_t("error")}: {e}', 'danger')
            return render_template('projects/create.html', project=data)

    return render_template('projects/create.html', project=None)


@projects_bp.route('/<project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    db = get_db()
    project = get_project(db, project_id)
    if not project:
        flash(_t('project_not_found'), 'danger')
        return redirect(url_for('projects.list_projects'))

    if request.method == 'POST':
        data = _parse_project_form(request.form)
        try:
            update_project(db, project_id, data)
            project = get_project(db, project_id)
            sync_project_jobs(project)
            flash(_t('project_updated'), 'success')
            return redirect(url_for('projects.list_projects'))
        except Exception as e:
            flash(f'{_t("error")}: {e}', 'danger')

    return render_template('projects/edit.html', project=project)


@projects_bp.route('/<project_id>/delete', methods=['POST'])
@login_required
def delete(project_id):
    db = get_db()
    remove_project_jobs(project_id)
    delete_project(db, project_id)
    flash(_t('project_deleted'), 'success')
    return redirect(url_for('projects.list_projects'))
