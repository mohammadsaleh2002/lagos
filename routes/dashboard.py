from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

from app import get_db
from models.project import get_all_projects
from models.content import get_project_stats
from services.scheduler import get_job_status

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    db = get_db()

    # Check if setup needed
    if db.users.count_documents({}) == 0:
        return redirect(url_for('auth.setup'))

    projects = get_all_projects(db)
    project_stats = []
    for p in projects:
        stats = get_project_stats(db, str(p['_id']))
        stats['project'] = p
        project_stats.append(stats)

    api_keys_count = db.api_keys.count_documents({})
    active_keys = db.api_keys.count_documents({'is_active': True})
    jobs = get_job_status()

    return render_template('dashboard/index.html',
                           project_stats=project_stats,
                           api_keys_count=api_keys_count,
                           active_keys=active_keys,
                           jobs=jobs)
