# Lagos - Blog Creation & WordPress Publishing Platform

## Overview
Python Flask application that automates SEO blog content creation using AI and publishes to WordPress. Supports multiple projects, API key rotation, and a web dashboard.

## Tech Stack
- **Backend**: Python Flask + Jinja2 (Bootstrap 5 + custom dark design system)
- **Database**: MongoDB (pymongo)
- **Scheduler**: APScheduler (background jobs)
- **AI Providers**: Pluggable system - Gemini, OpenAI, Claude (extensible)
- **WordPress**: REST API via requests
- **Auth**: Flask-Login with password hashing
- **Encryption**: Fernet (cryptography) for API key storage
- **Fonts**: Inter (LTR) + Vazirmatn (RTL/Persian) via Google Fonts

## Project Structure
```
Lagos/
├── app.py                          # Flask app factory, MongoDB init, blueprint registration
├── config.py                       # Config class (env vars, color palette)
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (MONGO_URI, FERNET_KEY, etc.)
│
├── models/                         # MongoDB document models
│   ├── user.py                     # User auth (create, find, verify password)
│   ├── project.py                  # Project CRUD (business info, WP creds, schedules)
│   ├── api_key.py                  # API key CRUD, encryption, round-robin rotation
│   └── content.py                  # Keywords, titles, articles, ads, supplementary content, stats
│
├── services/                       # Business logic
│   ├── ai_provider.py              # AIProvider base class, ProviderRegistry, key rotation
│   ├── providers/
│   │   ├── gemini.py               # Google Gemini (gemini-2.0-flash)
│   │   ├── openai_provider.py      # OpenAI (gpt-4o-mini)
│   │   └── claude.py               # Anthropic Claude (claude-sonnet-4-20250514)
│   ├── content_generator.py        # Full pipeline: keywords → titles → articles → ads → supplementary
│   ├── wordpress_publisher.py      # HTML assembly + WP REST API publishing
│   └── scheduler.py                # APScheduler: per-project creation & publish jobs
│
├── routes/                         # Flask blueprints (6 total, 21 routes)
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
    ├── css/style.css               # Full custom dark UI system (glassmorphism, gradients, animations)
    └── js/app.js                   # Sidebar toggle (localStorage), toast auto-dismiss, count-up animation
```

## UI Design System
Custom dark design built on top of Bootstrap 5 (NOT plain Bootstrap).

Key CSS classes defined in `style.css`:
- `stat-card stat-{primary|success|info|warning}` — dashboard stat cards with gradient border, colored glow bg, and icon with drop shadow
- `mini-stat` / `mini-stat-label` / `mini-stat-value` — compact stat boxes (content overview)
- `section-header` — form section titles with icon and bottom border
- `animate-in` / `animate-in-delay-{1-4}` — fadeInUp entrance animation
- `empty-state` / `empty-icon` — zero-state placeholder with large icon
- `glass-card` — glassmorphism card
- `auth-wrapper` / `auth-card` — centered login/setup layout with decorative gradient blobs
- `toast-modern toast-{success|danger|warning|info}` — slide-in toast notification
- `sidebar` / `sidebar-brand` / `sidebar-toggle` / `sidebar-footer` — collapsible sidebar

Sidebar collapses to icon-only mode (`width: 72px`), state saved in `localStorage['sidebarCollapsed']`.
Stat values use `data-count` attribute for animated count-up on page load.

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
- Round-robin: picks least-recently-used active key per provider
- On error: increments error count, retries with next key
- Auto-disable: key disabled after 5 consecutive failures
- Manual reset from dashboard

## Running
```bash
pip install -r requirements.txt
python app.py
# Visit localhost:9595/setup to create admin account
# Port is set to 9595 in app.py
```

## Environment Variables (.env)
- `SECRET_KEY` - Flask session secret
- `MONGO_URI` - MongoDB connection string with auth
- `MONGO_DB` - Database name (default: lagos)
- `FERNET_KEY` - Encryption key for API keys (auto-generated if empty, save it!)

## Key Design Decisions
- No image system (excluded for now, can be added later)
- Prompts derived from the original n8n workflows (creation.json, uploadtowp.json)
- Colors for headings come from a predefined palette in config.py (no DB table)
- Each project is fully independent with its own content and schedule
- Scheduler jobs are synced on project create/update
- MongoDB accessed via `current_app.extensions['mongo_db']` pattern (survives debug reloader)
- Multilingual: EN + FA (Persian), RTL layout auto-applied when lang=fa; Bootstrap RTL CSS loaded conditionally

## Maintenance Rules
- **After every change to the project: update CLAUDE.md AND TODO.md**
