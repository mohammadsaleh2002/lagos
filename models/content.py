from datetime import datetime, timezone
from bson import ObjectId


# --- Keywords ---
def add_keywords(db, project_id, keywords):
    docs = [{
        'project_id': project_id,
        'text': kw.strip(),
        'is_title_generated': False,
        'created_at': datetime.now(timezone.utc),
    } for kw in keywords if kw.strip()]
    if docs:
        db.keywords.insert_many(docs)
    return len(docs)


def get_random_keyword(db, project_id, title_generated=False):
    pipeline = [
        {'$match': {'project_id': project_id, 'is_title_generated': title_generated}},
        {'$sample': {'size': 1}}
    ]
    results = list(db.keywords.aggregate(pipeline))
    return results[0] if results else None


def mark_keyword_title_generated(db, keyword_id):
    db.keywords.update_one(
        {'_id': ObjectId(keyword_id)},
        {'$set': {'is_title_generated': True}}
    )


# --- Blog Titles ---
def add_blog_titles(db, project_id, titles, keyword):
    docs = [{
        'project_id': project_id,
        'content': t.strip(),
        'keyword': keyword,
        'is_article_generated': False,
        'created_at': datetime.now(timezone.utc),
    } for t in titles if t.strip()]
    if docs:
        db.blog_titles.insert_many(docs)
    return len(docs)


def get_random_blog_title(db, project_id, generated=False):
    pipeline = [
        {'$match': {'project_id': project_id, 'is_article_generated': generated}},
        {'$sample': {'size': 1}}
    ]
    results = list(db.blog_titles.aggregate(pipeline))
    return results[0] if results else None


def mark_blog_title_generated(db, title_id):
    db.blog_titles.update_one(
        {'_id': ObjectId(title_id)},
        {'$set': {'is_article_generated': True}}
    )


# --- Ads Titles ---
def add_ads_titles(db, project_id, titles, keyword):
    docs = [{
        'project_id': project_id,
        'content': t.strip(),
        'keyword': keyword,
        'is_generated': False,
        'created_at': datetime.now(timezone.utc),
    } for t in titles if t.strip()]
    if docs:
        db.ads_titles.insert_many(docs)
    return len(docs)


def get_random_ads_title(db, project_id, generated=False):
    pipeline = [
        {'$match': {'project_id': project_id, 'is_generated': generated}},
        {'$sample': {'size': 1}}
    ]
    results = list(db.ads_titles.aggregate(pipeline))
    return results[0] if results else None


def mark_ads_title_generated(db, title_id):
    db.ads_titles.update_one(
        {'_id': ObjectId(title_id)},
        {'$set': {'is_generated': True}}
    )


# --- Articles ---
def create_article(db, project_id, data):
    doc = {
        'project_id': project_id,
        'article_title': data.get('article_title', ''),
        'slug': data.get('slug', ''),
        'tag': data.get('tag', ''),
        'chapters': data.get('chapters', []),
        'faq': data.get('faq', ''),
        'reference': data.get('reference', ''),
        'is_published': False,
        'wp_post_id': None,
        'wp_post_url': None,
        'published_at': None,
        'created_at': datetime.now(timezone.utc),
    }
    result = db.articles.insert_one(doc)
    return str(result.inserted_id)


def get_random_unpublished_article(db, project_id):
    pipeline = [
        {'$match': {'project_id': project_id, 'is_published': False}},
        {'$sample': {'size': 1}}
    ]
    results = list(db.articles.aggregate(pipeline))
    return results[0] if results else None


def mark_article_published(db, article_id, wp_post_id, wp_post_url):
    db.articles.update_one(
        {'_id': ObjectId(article_id)},
        {'$set': {
            'is_published': True,
            'wp_post_id': wp_post_id,
            'wp_post_url': wp_post_url,
            'published_at': datetime.now(timezone.utc),
        }}
    )


def get_articles(db, project_id, published=None, limit=50):
    query = {'project_id': project_id}
    if published is not None:
        query['is_published'] = published
    return list(db.articles.find(query).sort('created_at', -1).limit(limit))


def get_article(db, article_id):
    return db.articles.find_one({'_id': ObjectId(article_id)})


# --- Ads Content ---
def create_ads_content(db, project_id, title, text):
    doc = {
        'project_id': project_id,
        'title': title,
        'text': text,
        'created_at': datetime.now(timezone.utc),
    }
    db.ads_content.insert_one(doc)


# --- Supplementary content ---
def add_bein_paragraphs(db, project_id, texts):
    docs = [{
        'project_id': project_id,
        'text': t.strip(),
        'created_at': datetime.now(timezone.utc),
    } for t in texts if t.strip()]
    if docs:
        db.bein_paragraphs.insert_many(docs)
    return len(docs)


def get_random_bein(db, project_id, count=3):
    pipeline = [
        {'$match': {'project_id': project_id}},
        {'$sample': {'size': count}}
    ]
    return list(db.bein_paragraphs.aggregate(pipeline))


def add_info_blocks(db, project_id, texts):
    docs = [{
        'project_id': project_id,
        'text': t.strip(),
        'created_at': datetime.now(timezone.utc),
    } for t in texts if t.strip()]
    if docs:
        db.info_blocks.insert_many(docs)
    return len(docs)


def get_random_info(db, project_id):
    pipeline = [
        {'$match': {'project_id': project_id}},
        {'$sample': {'size': 1}}
    ]
    results = list(db.info_blocks.aggregate(pipeline))
    return results[0] if results else None


def add_bullet_items(db, project_id, texts):
    docs = [{
        'project_id': project_id,
        'text': t.strip(),
        'created_at': datetime.now(timezone.utc),
    } for t in texts if t.strip()]
    if docs:
        db.bullet_items.insert_many(docs)
    return len(docs)


def get_random_bullet(db, project_id):
    pipeline = [
        {'$match': {'project_id': project_id}},
        {'$sample': {'size': 1}}
    ]
    results = list(db.bullet_items.aggregate(pipeline))
    return results[0] if results else None


# --- Stats ---
def get_project_stats(db, project_id):
    return {
        'keywords': db.keywords.count_documents({'project_id': project_id}),
        'blog_titles': db.blog_titles.count_documents({'project_id': project_id}),
        'blog_titles_unused': db.blog_titles.count_documents({'project_id': project_id, 'is_article_generated': False}),
        'ads_titles': db.ads_titles.count_documents({'project_id': project_id}),
        'articles_total': db.articles.count_documents({'project_id': project_id}),
        'articles_published': db.articles.count_documents({'project_id': project_id, 'is_published': True}),
        'articles_unpublished': db.articles.count_documents({'project_id': project_id, 'is_published': False}),
        'bein_paragraphs': db.bein_paragraphs.count_documents({'project_id': project_id}),
        'info_blocks': db.info_blocks.count_documents({'project_id': project_id}),
        'bullet_items': db.bullet_items.count_documents({'project_id': project_id}),
    }
