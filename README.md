# Lagos - AI-Powered Blog Creation & WordPress Publishing Platform

## Overview

Lagos is a Python Flask web application that automates SEO-optimized blog content creation using AI and publishes articles directly to WordPress. It supports multiple projects, AI provider key rotation, scheduled content generation, and a comprehensive web dashboard.

## Features

- 🤖 **Multi-AI Provider Support**: Gemini, OpenAI, and Claude with automatic failover
- 🔄 **API Key Rotation**: Round-robin key selection with automatic error handling
- 📝 **Complete Content Pipeline**: Keywords → Titles → Articles → Ads → Supplementary Content
- 📅 **Scheduled Automation**: APScheduler for automated content creation and publishing
- 🌐 **Bilingual UI**: English and Persian (RTL) support
- 🔐 **Secure Storage**: Fernet encryption for API keys
- 📊 **Project Management**: Multiple independent projects with separate content and schedules
- 🎨 **WordPress Integration**: Direct publishing via WordPress REST API
- 📈 **Content Statistics**: Track keywords, titles, articles, and publishing status

## Tech Stack

- **Backend**: Python Flask 3.1.0 + Jinja2 templates
- **Database**: MongoDB (pymongo 4.11.3)
- **Scheduler**: APScheduler 3.10.4
- **AI Providers**: 
  - Google Gemini (gemini-2.0-flash)
  - OpenAI (gpt-4o-mini)
  - Anthropic Claude (claude-sonnet-4-20250514)
- **WordPress**: REST API via requests
- **Authentication**: Flask-Login with password hashing
- **Encryption**: Fernet (cryptography) for API key storage
- **UI**: Bootstrap 5 dark theme with RTL support

## Project Structure

```
Lagos/
├── app.py                          # Flask app factory, MongoDB init, blueprint registration
├── config.py                       # Config class (env vars, color palette)
├── requirements.txt                # Python dependencies
├── translations.py                 # Bilingual translation system
├── .env                            # Environment variables (not in repo)
│
├── models/                         # MongoDB document models
│   ├── __init__.py
│   ├── user.py                     # User authentication (create, find, verify password)
│   ├── project.py                  # Project CRUD (business info, WP creds, schedules)
│   ├── api_key.py                  # API key CRUD, encryption, round-robin rotation
│   └── content.py                  # Keywords, titles, articles, ads, supplementary content, stats
│
├── services/                       # Business logic
│   ├── __init__.py
│   ├── ai_provider.py              # AIProvider base class, ProviderRegistry, key rotation
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── gemini.py               # Google Gemini provider
│   │   ├── openai_provider.py      # OpenAI provider
│   │   └── claude.py               # Anthropic Claude provider
│   ├── content_generator.py        # Full pipeline: keywords → titles → articles → ads → supplementary
│   ├── wordpress_publisher.py      # HTML assembly + WP REST API publishing
│   └── scheduler.py                # APScheduler: per-project creation & publish jobs
│
├── routes/                         # Flask blueprints (6 total, 21 routes)
│   ├── __init__.py
│   ├── auth.py                     # /login, /logout, /setup
│   ├── dashboard.py                # / (overview stats)
│   ├── projects.py                 # /projects/* (CRUD)
│   ├── api_keys.py                 # /api-keys/* (add, toggle, delete, reset errors)
│   ├── content.py                  # /content/* (overview, articles, keywords, generate actions)
│   └── publishing.py               # /publishing/* (queue, manual publish, settings)
│
├── templates/                      # Jinja2 templates (Bootstrap 5 dark, sidebar nav)
│   ├── base.html                   # Layout with sidebar
│   ├── auth/                       # login.html, setup.html
│   ├── dashboard/                  # index.html (stats cards, project table, jobs)
│   ├── projects/                   # list.html, create.html, edit.html, _form.html
│   ├── api_keys/                   # list.html (add form + table)
│   ├── content/                    # overview.html, articles.html, article_detail.html, keywords.html
│   └── publishing/                 # queue.html, settings.html
│
└── static/
    ├── css/style.css               # Sidebar styles
    └── js/app.js                   # Auto-dismiss alerts
```

## MongoDB Collections

- `users` - Dashboard user accounts
- `projects` - Business profiles with WP credentials, schedules, content settings
- `api_keys` - Encrypted AI provider keys with usage tracking
- `keywords` - SEO keywords per project
- `blog_titles` - Generated blog titles per project
- `ads_titles` - Generated advertising titles per project
- `articles` - Full articles (10 chapters, FAQ, slug, publish status)
- `ads_content` - Generated ad copy
- `bein_paragraphs` - Inter-paragraph promotional texts
- `info_blocks` - Contact/promo blocks
- `bullet_items` - Service bullet points

## Content Generation Pipeline

1. **Keywords**: AI generates SEO keywords from business info + seed keywords
2. **Titles**: Picks random keyword → generates blog + ads titles via AI
3. **Articles**: Picks random unused title → generates 10-chapter article with FAQ
4. **Ads**: Picks random ads title → generates promotional article
5. **Supplementary**: Generates bein_paragraphs (50), info_blocks (50), bullet_items (250)

## WordPress Publishing Flow

1. Picks random unpublished article
2. Assembles HTML: chapters with colored headings + blockquotes + FAQ + bullets + info
3. Posts via WP REST API (title, content, slug, category, status=publish)
4. Marks article as published with WP post ID and URL

## API Key Rotation

- **Round-robin**: Picks least-recently-used active key per provider
- **On error**: Increments error count, retries with next key
- **Auto-disable**: Key disabled after 5 consecutive failures
- **Manual reset**: Reset error count from dashboard

## Installation

1. **Clone the repository**
   ```bash
   cd /home/mohammad-saleh/Desktop/RASAWEB/Lagos
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB=lagos
   FERNET_KEY=your-fernet-key-here  # Optional, auto-generated if empty
   ```

5. **Start MongoDB**
   Ensure MongoDB is running on your system.

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Initial setup**
   - Visit `http://localhost:9595/setup` to create the first admin account
   - Login at `http://localhost:9595/login`

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask session secret | `lagos-secret-key-change-in-production` | Yes (change in production) |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/` | Yes |
| `MONGO_DB` | Database name | `lagos` | No |
| `FERNET_KEY` | Encryption key for API keys | Auto-generated if empty | No (but recommended) |

**Note**: If `FERNET_KEY` is not set, a new key will be generated on startup. Save this key to your `.env` file to persist encryption across restarts.

## Usage

### 1. Add API Keys
- Navigate to **API Keys** in the sidebar
- Add API keys for at least one provider (Gemini, OpenAI, or Claude)
- Keys are encrypted and stored securely

### 2. Create a Project
- Go to **Projects** → **Create Project**
- Fill in business information:
  - Company name, business field, services/products
  - Contact information
  - WordPress credentials (URL, username, app password, category ID)
  - Content settings (word count, chapters, etc.)
  - Schedule settings (auto-creation and auto-publishing intervals)

### 3. Generate Content
- Go to **Content** → Select your project
- Use the generation buttons:
  - **Keywords**: Generate SEO keywords
  - **Titles**: Generate blog and ads titles
  - **Generate Article**: Create a full article
  - **Ads**: Generate promotional content
  - **Supplementary**: Generate bein paragraphs, info blocks, and bullet items
  - **Full Pipeline**: Run all steps sequentially

### 4. Publish to WordPress
- Go to **Publishing** → **Queue**
- View unpublished articles
- Click **Publish Next** to publish a random article
- Or manually select an article to publish

### 5. Schedule Automation
- Edit project settings
- Enable **Auto Content Creation** and set interval (minutes)
- Enable **Auto Publishing** and set interval (minutes)
- Jobs will run automatically in the background

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout
- `GET/POST /setup` - Initial admin account creation

### Dashboard
- `GET /` - Dashboard overview with stats

### Projects
- `GET /projects/` - List all projects
- `GET /projects/create` - Create project form
- `POST /projects/create` - Create project
- `GET /projects/<id>/edit` - Edit project form
- `POST /projects/<id>/edit` - Update project
- `POST /projects/<id>/delete` - Delete project

### API Keys
- `GET /api-keys/` - List all API keys
- `POST /api-keys/add` - Add new API key
- `POST /api-keys/<id>/toggle` - Toggle key active status
- `POST /api-keys/<id>/reset-errors` - Reset error count
- `POST /api-keys/<id>/delete` - Delete API key

### Content
- `GET /content/` - Content overview for all projects
- `GET /content/<project_id>/articles` - List articles
- `GET /content/<project_id>/articles/<article_id>` - Article detail
- `GET /content/<project_id>/keywords` - View keywords and titles
- `POST /content/<project_id>/generate` - Generate content (action: keywords, titles, article, ads, supplementary, full)

### Publishing
- `GET /publishing/` - Publishing queue
- `POST /publishing/<project_id>/publish` - Publish article
- `GET /publishing/settings` - Scheduler settings

## Key Design Decisions

- **No image system**: Excluded for now, can be added later
- **Prompts**: Derived from original n8n workflows (creation.json, uploadtowp.json)
- **Colors**: Heading colors come from predefined palette in config.py (no DB table)
- **Project independence**: Each project is fully independent with its own content and schedule
- **Scheduler sync**: Jobs are synced on project create/update
- **Bilingual support**: Full English/Persian translation system with RTL support

## Security Considerations

- API keys are encrypted using Fernet before storage
- Passwords are hashed using Werkzeug's password hashing
- Flask-Login handles session management
- All routes (except auth) require login
- MongoDB indexes ensure data integrity

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running: `sudo systemctl status mongod`
- Check `MONGO_URI` in `.env` file
- Verify network connectivity to MongoDB server

### API Key Errors
- Check API key validity in provider dashboard
- Review error count in API Keys page
- Reset errors if key is valid but marked as failed
- Ensure at least one active key exists per provider

### Scheduler Not Running
- Check job status in Dashboard
- Verify project schedule settings are enabled
- Review application logs for scheduler errors

### WordPress Publishing Fails
- Verify WordPress credentials (URL, username, app password)
- Check WordPress REST API is enabled
- Ensure category ID exists in WordPress
- Review network connectivity to WordPress site

## Development

### Running in Debug Mode
The application runs in debug mode by default:
```python
app.run(debug=True, port=9595)
```

### Adding New AI Providers
1. Create a new provider class in `services/providers/`
2. Inherit from `AIProvider` base class
3. Implement `generate()` and `generate_json()` methods
4. Register with `@ProviderRegistry.register` decorator
5. Add provider name to `PROVIDERS` list in `models/api_key.py`

### Adding Translations
Edit `translations.py` and add new keys to the `TRANSLATIONS` dictionary:
```python
'new_key': {'en': 'English text', 'fa': 'متن فارسی'}
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support information here]

