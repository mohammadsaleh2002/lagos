import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
_app = None


def init_scheduler(app):
    global _app
    _app = app
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
    # Load existing project schedules
    _sync_all_jobs()


def _sync_all_jobs():
    if not _app:
        return
    try:
        with _app.app_context():
            from app import get_db
            db = get_db()
            projects = list(db.projects.find())
            for project in projects:
                sync_project_jobs(project)
    except Exception as e:
        logger.warning(f"Could not sync scheduler jobs: {e}")


def sync_project_jobs(project):
    """Create or update scheduler jobs for a project based on its settings."""
    pid = str(project['_id'])
    schedule = project.get('schedule', {})

    creation_job_id = f"creation_{pid}"
    publish_job_id = f"publish_{pid}"

    # Content creation job
    if schedule.get('creation_enabled'):
        interval = schedule.get('creation_interval_minutes', 60)
        if scheduler.get_job(creation_job_id):
            scheduler.reschedule_job(
                creation_job_id,
                trigger=IntervalTrigger(minutes=interval)
            )
        else:
            scheduler.add_job(
                _run_content_creation,
                trigger=IntervalTrigger(minutes=interval),
                id=creation_job_id,
                args=[pid],
                replace_existing=True,
                max_instances=1,
            )
        logger.info(f"Content creation job enabled for {pid} (every {interval} min)")
    else:
        if scheduler.get_job(creation_job_id):
            scheduler.remove_job(creation_job_id)
            logger.info(f"Content creation job disabled for {pid}")

    # Publishing job
    if schedule.get('publish_enabled'):
        interval = schedule.get('publish_interval_minutes', 20)
        if scheduler.get_job(publish_job_id):
            scheduler.reschedule_job(
                publish_job_id,
                trigger=IntervalTrigger(minutes=interval)
            )
        else:
            scheduler.add_job(
                _run_publish,
                trigger=IntervalTrigger(minutes=interval),
                id=publish_job_id,
                args=[pid],
                replace_existing=True,
                max_instances=1,
            )
        logger.info(f"Publishing job enabled for {pid} (every {interval} min)")
    else:
        if scheduler.get_job(publish_job_id):
            scheduler.remove_job(publish_job_id)
            logger.info(f"Publishing job disabled for {pid}")


def remove_project_jobs(project_id):
    """Remove all scheduler jobs for a project."""
    for prefix in ['creation_', 'publish_']:
        job_id = f"{prefix}{project_id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)


def _run_content_creation(project_id):
    """Background job: run content creation for a project."""
    if not _app:
        return
    with _app.app_context():
        from app import get_db, get_fernet
        from models.project import get_project
        from services.content_generator import ContentGenerator

        db = get_db()
        project = get_project(db, project_id)
        if not project:
            logger.error(f"Project {project_id} not found for content creation job")
            return

        gen = ContentGenerator(db, get_fernet())
        try:
            # Run individual steps (not full pipeline each time)
            gen.generate_article(project)
            logger.info(f"Scheduled content creation completed for {project_id}")
        except Exception as e:
            logger.error(f"Scheduled content creation failed for {project_id}: {e}")


def _run_publish(project_id):
    """Background job: publish an article to WordPress."""
    if not _app:
        return
    with _app.app_context():
        from app import get_db
        from models.project import get_project
        from services.wordpress_publisher import WordPressPublisher

        db = get_db()
        project = get_project(db, project_id)
        if not project:
            logger.error(f"Project {project_id} not found for publishing job")
            return

        publisher = WordPressPublisher(db)
        try:
            result = publisher.publish_article(project)
            if result:
                logger.info(f"Scheduled publish completed: {result['wp_post_url']}")
            else:
                logger.info(f"No articles to publish for {project_id}")
        except Exception as e:
            logger.error(f"Scheduled publishing failed for {project_id}: {e}")


def get_job_status():
    """Get status of all scheduler jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': str(job.next_run_time) if job.next_run_time else 'paused',
            'trigger': str(job.trigger),
        })
    return jobs
