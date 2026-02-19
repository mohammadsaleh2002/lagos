import logging
import random
import requests
from requests.auth import HTTPBasicAuth

from config import Config
from models.content import (
    get_random_unpublished_article, mark_article_published,
    get_random_bein, get_random_info, get_random_bullet,
)

logger = logging.getLogger(__name__)


class WordPressPublisher:
    def __init__(self, db):
        self.db = db

    def _assemble_html(self, article, project):
        """Assemble the final HTML content from article chapters and supplementary content."""
        pid = str(project['_id'])
        chapters = article.get('chapters', [])
        beins = get_random_bein(self.db, pid, count=3)
        info = get_random_info(self.db, pid)
        bullet = get_random_bullet(self.db, pid)

        colors = random.sample(Config.HEADING_COLORS, min(len(Config.HEADING_COLORS), 10))
        heading_tags = ['h2', 'h3', 'h2', 'h3', 'h2', 'h4', 'h3', 'h2', 'h3', 'h3']

        html_parts = []

        for i, chapter in enumerate(chapters):
            if i >= 10:
                break

            tag = heading_tags[i] if i < len(heading_tags) else 'h3'
            color = colors[i % len(colors)]
            title = chapter.get('title', '')
            content = chapter.get('content', '')

            html_parts.append(f'<{tag} style="color:{color}">{title}</{tag}>')
            html_parts.append(content)

            # Insert bein paragraphs after chapters 2, 5, 9
            if i == 1 and len(beins) > 0:
                html_parts.append(f'<blockquote>{beins[0]["text"]}</blockquote>')
            elif i == 4 and len(beins) > 1:
                html_parts.append(f'<blockquote>{beins[1]["text"]}</blockquote>')
            elif i == 8 and len(beins) > 2:
                html_parts.append(f'<blockquote>{beins[2]["text"]}</blockquote>')

        # Append FAQ
        if article.get('faq'):
            html_parts.append(article['faq'])

        # Append bullet
        if bullet:
            html_parts.append(f'<strong>{bullet["text"]}</strong>')

        # Append info
        if info:
            html_parts.append(info['text'])

        return '\n'.join(html_parts)

    def publish_article(self, project, article_id=None):
        """Publish an article to WordPress."""
        pid = str(project['_id'])
        wp = project.get('wordpress', {})

        if not wp.get('url') or not wp.get('username') or not wp.get('app_password'):
            raise ValueError("WordPress credentials not configured for this project.")

        # Get article
        if article_id:
            from models.content import get_article
            article = get_article(self.db, article_id)
        else:
            article = get_random_unpublished_article(self.db, pid)

        if not article:
            logger.info(f"No unpublished articles for project {pid}")
            return None

        # Assemble HTML
        html_content = self._assemble_html(article, project)

        # Create WordPress post
        wp_url = wp['url'].rstrip('/')
        api_url = f"{wp_url}/wp-json/wp/v2/posts"
        auth = HTTPBasicAuth(wp['username'], wp['app_password'])

        post_data = {
            'title': article['article_title'],
            'content': html_content,
            'slug': article.get('slug', ''),
            'status': 'publish',
            'ping_status': 'open',
        }

        if wp.get('category_id'):
            post_data['categories'] = [wp['category_id']]

        response = requests.post(api_url, json=post_data, auth=auth, timeout=30)
        response.raise_for_status()
        wp_post = response.json()

        wp_post_id = wp_post.get('id')
        wp_post_url = wp_post.get('link', '')

        # Mark as published
        mark_article_published(self.db, str(article['_id']), wp_post_id, wp_post_url)

        logger.info(f"Published article to WP: {wp_post_url}")
        return {
            'wp_post_id': wp_post_id,
            'wp_post_url': wp_post_url,
            'article_title': article['article_title'],
        }
