from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required

from app import get_db
from models.project import get_project, get_all_projects
from models.content import get_articles, get_project_stats
from services.wordpress_publisher import WordPressPublisher
from services.scheduler import get_job_status
from translations import get_text

publishing_bp = Blueprint('publishing', __name__)


def _t(key, **kwargs):
    lang = session.get('lang', 'fa')
    return get_text(key, lang, **kwargs)


@publishing_bp.route('/')
@login_required
def queue():
    db = get_db()
    projects = get_all_projects(db)
    queue_data = []
    for p in projects:
        pid = str(p['_id'])
        unpublished = get_articles(db, pid, published=False, limit=10)
        published = get_articles(db, pid, published=True, limit=10)
        stats = get_project_stats(db, pid)
        queue_data.append({
            'project': p,
            'unpublished': unpublished,
            'published': published,
            'stats': stats,
        })

    jobs = get_job_status()
    return render_template('publishing/queue.html', queue_data=queue_data, jobs=jobs)


@publishing_bp.route('/<project_id>/publish', methods=['POST'])
@login_required
def publish(project_id):
    db = get_db()
    project = get_project(db, project_id)
    if not project:
        flash(_t('project_not_found'), 'danger')
        return redirect(url_for('publishing.queue'))

    article_id = request.form.get('article_id')
    publisher = WordPressPublisher(db)

    try:
        result = publisher.publish_article(project, article_id=article_id)
        if result:
            flash(_t('published_msg', title=result["article_title"], url=result["wp_post_url"]), 'success')
        else:
            flash(_t('no_articles_to_publish'), 'warning')
    except Exception as e:
        flash(_t('publishing_error', e=e), 'danger')

    return redirect(url_for('publishing.queue'))


@publishing_bp.route('/settings')
@login_required
def settings():
    db = get_db()
    projects = get_all_projects(db)
    jobs = get_job_status()
    return render_template('publishing/settings.html', projects=projects, jobs=jobs)
