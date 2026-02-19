from datetime import datetime, timezone
from bson import ObjectId


def default_project():
    return {
        'name': '',
        'db_key': '',
        'company_name': '',
        'business_field': '',
        'services_products': '',
        'about_company': '',
        'lang': 'fa',
        'address': '',
        'phone': '',
        'mobile_phone': '',
        'email': '',
        'keyword': '',
        'bullet1': '',
        'bullet2': '',
        'bullet3': '',
        'wordpress': {
            'url': '',
            'username': '',
            'app_password': '',
            'category_id': 0,
        },
        'telegram': {
            'bot_token': '',
            'chat_id': '',
        },
        'schedule': {
            'creation_enabled': False,
            'creation_interval_minutes': 60,
            'publish_enabled': False,
            'publish_interval_minutes': 20,
        },
        'content_settings': {
            'number_of_content': 100,
            'number_of_keyword': 20,
            'number_of_ads': 50,
            'article_word_count': 3500,
            'article_chapters': 10,
            'ads_word_count': 800,
        },
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
    }


def create_project(db, data):
    project = default_project()
    project.update(data)
    project['created_at'] = datetime.now(timezone.utc)
    project['updated_at'] = datetime.now(timezone.utc)
    result = db.projects.insert_one(project)
    return str(result.inserted_id)


def get_project(db, project_id):
    return db.projects.find_one({'_id': ObjectId(project_id)})


def get_all_projects(db):
    return list(db.projects.find().sort('created_at', -1))


def update_project(db, project_id, data):
    data['updated_at'] = datetime.now(timezone.utc)
    db.projects.update_one({'_id': ObjectId(project_id)}, {'$set': data})


def delete_project(db, project_id):
    oid = ObjectId(project_id)
    db.projects.delete_one({'_id': oid})
    # Clean up related content
    for col in ['keywords', 'blog_titles', 'ads_titles', 'articles',
                'ads_content', 'bein_paragraphs', 'info_blocks', 'bullet_items']:
        db[col].delete_many({'project_id': str(oid)})
