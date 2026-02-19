import logging

from models.content import (
    add_keywords, get_random_keyword, mark_keyword_title_generated,
    add_blog_titles, add_ads_titles, get_random_blog_title, mark_blog_title_generated,
    get_random_ads_title, mark_ads_title_generated,
    create_article, create_ads_content,
    add_bein_paragraphs, add_info_blocks, add_bullet_items,
)
from services.ai_provider import ProviderRegistry, find_active_provider

logger = logging.getLogger(__name__)


class ContentGenerator:
    def __init__(self, db, fernet):
        self.db = db
        self.fernet = fernet

    def _get_provider(self):
        provider = find_active_provider(self.db, self.fernet)
        if not provider:
            raise RuntimeError("No active AI provider with valid API keys found.")
        return provider

    def _ai(self, prompt, system_prompt=''):
        provider = self._get_provider()
        return ProviderRegistry.generate(self.db, self.fernet, provider, prompt, system_prompt)

    def _ai_json(self, prompt, system_prompt=''):
        provider = self._get_provider()
        return ProviderRegistry.generate_json(self.db, self.fernet, provider, prompt, system_prompt)

    # --- Step 1: Keyword Generation ---
    def generate_keywords(self, project):
        pid = str(project['_id'])

        # First, insert seed keywords from project config
        seed = project.get('keyword', '')
        if seed:
            seeds = [k.strip() for k in seed.split('-') if k.strip()]
            if seeds:
                add_keywords(self.db, pid, seeds)
                logger.info(f"Added {len(seeds)} seed keywords for project {pid}")

        # Then generate AI keywords
        num_kw = project['content_settings']['number_of_keyword'] // 4
        prompt = f"""اطلاعات کسب‌وکار:
نام برند: {project['company_name']}
محصولات یا خدمات اصلی: {project['services_products']}
حوزه کاری: {project['business_field']}
بر اساس اطلاعات فوق، لطفاً دقیقاً {num_kw} کلمه کلیدی سئو شده و هدفمند پیشنهاد کن که:
- ترکیبی از کلمات کوتاه، میان‌رده و بلند باشند.
- شامل کلمات مرتبط با حوزه کاری و نیاز مشتریان باشند.
- قابلیت رتبه‌گیری بالا در موتورهای جستجو را داشته باشند.
- از عبارات جذاب، پرسرچ و با نیت جستجوی مشخص (اطلاعاتی، تراکنشی، ناوبری) استفاده شود.
هر کلمه را در یک خروجی زیر هم بده
به زبان {project['lang']} بنویس

هر آیتم را با ============== جدا کن"""

        sys_prompt = """شما یک کارشناس ارشد سئو، تحقیق کلمات کلیدی و بازاریابی محتوایی هستید.
هیچ چیز اضافی ننویس فقط کلمه ها رو خروجی بده"""

        result = self._ai(prompt, sys_prompt)
        keywords = [k.strip() for k in result.split('==============') if k.strip()]
        count = add_keywords(self.db, pid, keywords)
        logger.info(f"Generated {count} AI keywords for project {pid}")
        return count

    # --- Step 2: Title Generation ---
    def generate_titles(self, project):
        pid = str(project['_id'])
        kw = get_random_keyword(self.db, pid, title_generated=False)
        if not kw:
            logger.warning(f"No unused keywords for project {pid}")
            return 0, 0

        num_content = project['content_settings']['number_of_content']
        num_kw = project['content_settings']['number_of_keyword']
        num_ads = project['content_settings']['number_of_ads']
        blog_count = int(num_content * 1.2 / max(num_kw, 1))
        ads_count = int(num_ads * 1.2 / max(num_kw, 1))

        prompt = f"""You are an expert SEO content strategist specialized in generating high-converting article titles.

Business Information:
Brand Name: {project['company_name']}
Main Products or Services: {project['services_products']}
Business Field: {project['business_field']}

Your task is to produce two categories of fully SEO-optimized and highly engaging titles in Persian:
1. {blog_count} content titles (Blog Titles)
2. {ads_count} advertising titles (Advertising Titles)

Follow these rules:
- Keyword must appear exactly once in each title, near beginning or middle.
- Length: 55-65 characters each.
- SEO optimized with E-E-A-T principles.
- Topic variety: educational guides, listicles, comparisons, tips & tricks, etc.

Output Format: JSON with two fields:
- "blog": string with titles separated by newlines
- "ads": string with titles separated by newlines

Write in {project['lang']}
Keyword: {kw['text']}"""

        sys_prompt = "You are a helpful assistant. Only output the titles, nothing extra."

        data = self._ai_json(prompt, sys_prompt)
        blog_titles = [t for t in data.get('blog', '').split('\n') if t.strip()]
        ads_titles = [t for t in data.get('ads', '').split('\n') if t.strip()]

        b_count = add_blog_titles(self.db, pid, blog_titles, kw['text'])
        a_count = add_ads_titles(self.db, pid, ads_titles, kw['text'])
        mark_keyword_title_generated(self.db, kw['_id'])

        logger.info(f"Generated {b_count} blog titles, {a_count} ads titles for project {pid}")
        return b_count, a_count

    # --- Step 3: Article Generation ---
    def generate_article(self, project):
        pid = str(project['_id'])
        title_doc = get_random_blog_title(self.db, pid, generated=False)
        if not title_doc:
            logger.warning(f"No unused blog titles for project {pid}")
            return None

        word_count = project['content_settings']['article_word_count']
        chapters = project['content_settings']['article_chapters']
        per_chapter = word_count // chapters

        prompt = f"""Write a fully SEO-optimized, human-written article in Persian.

Title: {title_doc['content']}
Keyword: {title_doc['keyword']}

Business Information:
Brand Name: {project['company_name']}
Main Products or Services: {project['services_products']}
Business Field: {project['business_field']}
About: {project['about_company']}

Content Rules:
- Follow E-E-A-T principles.
- Word count: {word_count}
- Use the keyword naturally (density < 2%).
- Use synonyms where needed.
- Use <br> tags for line breaks in text.

Structure:
- Create {chapters} chapters inside a JSON array field called "chapters".
- Each chapter has "title" and "content" fields.
- Each chapter length ≈ {per_chapter} words.
- Add a relevant emoji at the start of each chapter title.
- Do NOT use "Chapter 1", "Chapter 2", etc.
- Don't use colons in titles.
- Add 2 random HTML tables (class "my_table") in random chapters.
- Enclose all HTML attributes in double quotes.

Output JSON format:
{{
  "chapters": [
    {{ "title": "string", "content": "string" }}
  ],
  "refrence": "string",
  "faq": "string",
  "slug": "string"
}}

Additional:
- Create 10 FAQ items as an HTML table with class "my_table" inside field "faq".
- Translate the title to English in field "slug".
- Write in {project['lang']} language."""

        sys_prompt = "You are a senior SEO content writer. Output valid JSON only."

        data = self._ai_json(prompt, sys_prompt)
        article_id = create_article(self.db, pid, {
            'article_title': title_doc['content'],
            'slug': data.get('slug', ''),
            'tag': title_doc['keyword'],
            'chapters': data.get('chapters', []),
            'faq': data.get('faq', ''),
            'reference': data.get('refrence', data.get('reference', '')),
        })
        mark_blog_title_generated(self.db, title_doc['_id'])
        logger.info(f"Generated article {article_id} for project {pid}")
        return article_id

    # --- Step 4: Ads Content Generation ---
    def generate_ads_content(self, project):
        pid = str(project['_id'])
        title_doc = get_random_ads_title(self.db, pid, generated=False)
        if not title_doc:
            logger.warning(f"No unused ads titles for project {pid}")
            return None

        prompt = f"""Write a persuasive, SEO-optimized promotional article (2000 characters max).

Title: {title_doc['content']}
Keyword: {title_doc['keyword']}

Company: {project['company_name']}
Business field: {project['business_field']}
Services: {project['services_products']}
About: {project['about_company']}
Language: {project['lang']}

Structure:
1. Hook (1-2 sentences) - emotional opener
2. Introduction (80-100 words) - what the company offers
3. Problem Section - pain points
4. Solution Section - present services as the solution
5. Call to Action with urgency
Contact: {project['address']}, {project['mobile_phone']}
6. Why choose this company

Write in {project['lang']}. Output only the article text."""

        result = self._ai(prompt)
        create_ads_content(self.db, pid, title_doc['content'], result)
        mark_ads_title_generated(self.db, title_doc['_id'])
        logger.info(f"Generated ads content for project {pid}")
        return True

    # --- Step 5: Supplementary Content ---
    def generate_bein_paragraphs(self, project):
        pid = str(project['_id'])
        prompt = f"""For the company {project['company_name']} that provides {project['services_products']}, create 50 unique advertising texts.

Each text must:
- Start with a question or engaging hook.
- Present the solution or benefit.
- List 2-3 advantages with ✅ symbol.
- End with a short call-to-action.
- Be 350-500 characters total.
- Include the company name.

Write in {project['lang']}
Separate each item with =============="""

        sys_prompt = "You are a helpful assistant. Don't use quotes in content."

        result = self._ai(prompt, sys_prompt)
        texts = [t.strip() for t in result.split('==============') if t.strip()]
        count = add_bein_paragraphs(self.db, pid, texts)
        logger.info(f"Generated {count} bein paragraphs for project {pid}")
        return count

    def generate_info_blocks(self, project):
        pid = str(project['_id'])
        prompt = f"""For the company {project['company_name']} that provides {project['services_products']}, create 50 unique promotional texts.

Each text must:
- Start with a hook.
- Describe one specific service/benefit.
- Add 1 check mark (✅) with a feature.

Include contact info in HTML:
✉️ <a href="mailto:{project['email']}">{project['email']}</a><br>
📱 <a href="tel:{project['mobile_phone']}">{project['mobile_phone']}</a><br>
📞 <a href="tel:{project['phone']}">{project['phone']}</a><br>

Write in {project['lang']}
Separate each item with ==============

Return in json field "info" """

        sys_prompt = "You are a helpful assistant. Don't use quotes in content."

        data = self._ai_json(prompt, sys_prompt)
        info_text = data.get('info', '')
        texts = [t.strip() for t in info_text.split('==============') if t.strip()]
        count = add_info_blocks(self.db, pid, texts)
        logger.info(f"Generated {count} info blocks for project {pid}")
        return count

    def generate_bullet_items(self, project):
        pid = str(project['_id'])
        prompt = f"""For the company {project['company_name']} whose services include {project['services_products']}, produce a list of 250 different, realistic, and industry-relevant services.

Use this format for each entry:
{project.get('bullet1', '')}
[Service 1]
[Service 2]
[Service 3]
[Service 4]
[Service 5]
{project.get('bullet2', '')}
{project.get('bullet3', '')}

Provide only five new services per entry.
All services must relate to {project['business_field']}.

Write in {project['lang']}
Separate each item with ==============

Return in json field "bullet" """

        sys_prompt = "You are a helpful assistant. Don't use quotes in content."

        data = self._ai_json(prompt, sys_prompt)
        bullet_text = data.get('bullet', '')
        texts = [t.strip() for t in bullet_text.split('==============') if t.strip()]
        count = add_bullet_items(self.db, pid, texts)
        logger.info(f"Generated {count} bullet items for project {pid}")
        return count

    # --- Full Pipeline ---
    def run_full_pipeline(self, project):
        """Run the complete content generation pipeline for a project."""
        pid = str(project['_id'])
        results = {}

        try:
            results['keywords'] = self.generate_keywords(project)
        except Exception as e:
            logger.error(f"Keyword generation failed for {pid}: {e}")
            results['keywords'] = f"Error: {e}"

        try:
            results['titles'] = self.generate_titles(project)
        except Exception as e:
            logger.error(f"Title generation failed for {pid}: {e}")
            results['titles'] = f"Error: {e}"

        try:
            results['article'] = self.generate_article(project)
        except Exception as e:
            logger.error(f"Article generation failed for {pid}: {e}")
            results['article'] = f"Error: {e}"

        try:
            results['ads'] = self.generate_ads_content(project)
        except Exception as e:
            logger.error(f"Ads generation failed for {pid}: {e}")
            results['ads'] = f"Error: {e}"

        try:
            results['bein'] = self.generate_bein_paragraphs(project)
        except Exception as e:
            logger.error(f"Bein paragraph generation failed for {pid}: {e}")
            results['bein'] = f"Error: {e}"

        try:
            results['info'] = self.generate_info_blocks(project)
        except Exception as e:
            logger.error(f"Info block generation failed for {pid}: {e}")
            results['info'] = f"Error: {e}"

        try:
            results['bullets'] = self.generate_bullet_items(project)
        except Exception as e:
            logger.error(f"Bullet generation failed for {pid}: {e}")
            results['bullets'] = f"Error: {e}"

        return results
