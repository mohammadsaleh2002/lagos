from flask import Flask, current_app, session, request, redirect, url_for
from flask_login import LoginManager
from pymongo import MongoClient
from cryptography.fernet import Fernet

from config import Config
from translations import get_text

login_manager = LoginManager()

SUPPORTED_LANGS = ['en', 'fa']
DEFAULT_LANG = 'fa'


def get_db():
    """Get MongoDB database from current Flask app context."""
    return current_app.extensions['mongo_db']


def get_fernet():
    """Get Fernet instance from current Flask app context."""
    return current_app.extensions['fernet']


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # MongoDB
    mongo_client = MongoClient(app.config['MONGO_URI'], serverSelectionTimeoutMS=5000)
    db = mongo_client[app.config['MONGO_DB']]

    # Store on app so it survives debug reloader
    app.extensions['mongo_client'] = mongo_client
    app.extensions['mongo_db'] = db

    # Create indexes (deferred - only runs when MongoDB is available)
    def _ensure_indexes():
        try:
            db.users.create_index('username', unique=True)
            db.projects.create_index('db_key', unique=True)
            db.api_keys.create_index('provider')
            db.keywords.create_index('project_id')
            db.blog_titles.create_index('project_id')
            db.ads_titles.create_index('project_id')
            db.articles.create_index('project_id')
            db.articles.create_index([('project_id', 1), ('is_published', 1)])
        except Exception as e:
            print(f"[WARN] Could not create indexes: {e}")

    _ensure_indexes()

    # Fernet encryption for API keys
    fernet_key = app.config['FERNET_KEY']
    if not fernet_key:
        fernet_key = Fernet.generate_key().decode()
        print(f"[WARN] No FERNET_KEY set. Generated: {fernet_key}")
        print("       Add FERNET_KEY to your .env file to persist encryption across restarts.")
    fernet_instance = Fernet(fernet_key.encode() if isinstance(fernet_key, str) else fernet_key)
    app.extensions['fernet'] = fernet_instance

    # Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    from models.user import load_user_by_id
    login_manager.user_loader(load_user_by_id)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.projects import projects_bp
    from routes.api_keys import api_keys_bp
    from routes.content import content_bp
    from routes.publishing import publishing_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(api_keys_bp, url_prefix='/api-keys')
    app.register_blueprint(content_bp, url_prefix='/content')
    app.register_blueprint(publishing_bp, url_prefix='/publishing')

    # Language context processor
    @app.context_processor
    def inject_i18n():
        lang = session.get('lang', DEFAULT_LANG)
        def t(key, **kwargs):
            return get_text(key, lang, **kwargs)
        return dict(t=t, current_lang=lang, is_rtl=(lang == 'fa'))

    # Language switch route
    @app.route('/set-lang/<lang>')
    def set_lang(lang):
        if lang in SUPPORTED_LANGS:
            session['lang'] = lang
        return redirect(request.referrer or url_for('dashboard.index'))

    # Scheduler
    from services.scheduler import init_scheduler
    init_scheduler(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=9595)
