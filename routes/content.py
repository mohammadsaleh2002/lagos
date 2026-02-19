from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required

from app import get_db, get_fernet
from models.project import get_project, get_all_projects
from models.content import get_project_stats, get_articles, get_article
from services.content_generator import ContentGenerator
from translations import get_text

content_bp = Blueprint('content', __name__)


def _t(key, **kwargs):
    lang = session.get('lang', 'fa')
    return get_text(key, lang, **kwargs)


@content_bp.route('/')
@login_required
def overview():
    db = get_db()
    projects = get_all_projects(db)
    project_data = []
    for p in projects:
        stats = get_project_stats(db, str(p['_id']))
        stats['project'] = p
        project_data.append(stats)
    return render_template('content/overview.html', project_data=project_data)


@content_bp.route('/<project_id>/articles')
@login_required
def articles(project_id):
    db = get_db()
    project = get_project(db, project_id)
    if not project:
        flash(_t('project_not_found'), 'danger')
        return redirect(url_for('content.overview'))

    filter_type = request.args.get('filter', 'all')
    published = None
    if filter_type == 'published':
        published = True
    elif filter_type == 'unpublished':
        published = False

    article_list = get_articles(db, project_id, published=published)
    stats = get_project_stats(db, project_id)

    return render_template('content/articles.html',
                           project=project, articles=article_list,
                           stats=stats, filter_type=filter_type)


@content_bp.route('/<project_id>/articles/<article_id>')
@login_required
def article_detail(project_id, article_id):
    db = get_db()
    project = get_project(db, project_id)
    article = get_article(db, article_id)
    if not project or not article:
        flash(_t('project_not_found'), 'danger')
        return redirect(url_for('content.overview'))
    return render_template('content/article_detail.html', project=project, article=article)


@content_bp.route('/<project_id>/keywords')
@login_required
def keywords(project_id):
    db = get_db()
    project = get_project(db, project_id)
    if not project:
        flash(_t('project_not_found'), 'danger')
        return redirect(url_for('content.overview'))

    kw_list = list(db.keywords.find({'project_id': project_id}).sort('created_at', -1).limit(200))
    titles = list(db.blog_titles.find({'project_id': project_id}).sort('created_at', -1).limit(200))

    return render_template('content/keywords.html',
                           project=project, keywords=kw_list, titles=titles)


@content_bp.route('/<project_id>/generate', methods=['POST'])
@login_required
def generate(project_id):
    db = get_db()
    project = get_project(db, project_id)
    if not project:
        flash(_t('project_not_found'), 'danger')
        return redirect(url_for('content.overview'))

    action = request.form.get('action', '')
    gen = ContentGenerator(db, get_fernet())

    try:
        if action == 'keywords':
            count = gen.generate_keywords(project)
            flash(_t('generated_keywords', count=count), 'success')
        elif action == 'titles':
            b, a = gen.generate_titles(project)
            flash(_t('generated_titles', b=b, a=a), 'success')
        elif action == 'article':
            aid = gen.generate_article(project)
            if aid:
                flash(_t('article_generated'), 'success')
            else:
                flash(_t('no_titles_available'), 'warning')
        elif action == 'ads':
            gen.generate_ads_content(project)
            flash(_t('ads_generated'), 'success')
        elif action == 'supplementary':
            b = gen.generate_bein_paragraphs(project)
            i = gen.generate_info_blocks(project)
            bl = gen.generate_bullet_items(project)
            flash(_t('supplementary_generated', b=b, i=i, bl=bl), 'success')
        elif action == 'full':
            gen.run_full_pipeline(project)
            flash(_t('pipeline_completed'), 'success')
        else:
            flash(_t('unknown_action'), 'danger')
    except Exception as e:
        flash(_t('generation_error', e=e), 'danger')

    return redirect(url_for('content.articles', project_id=project_id))
