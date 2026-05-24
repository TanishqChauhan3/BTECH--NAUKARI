# 🎓 CareerBridge — Job Aggregator for B.Tech CS Graduates

A full-stack job aggregation portal that scrapes private sector, government, and PSU job listings from 18+ sources, deduplicates them, and presents them in a clean, filterable React UI.

---

## 🏗️ Architecture Overview

```
Data Sources (RSS / Web)
        ↓
Scraper Pipeline (feedparser + Playwright + BS4)
        ↓
Normaliser + Deduplicator (SHA-256 fingerprint)
        ↓
PostgreSQL (via SQLAlchemy async)
        ↓
FastAPI REST API (with Redis cache)
        ↓
React + Vite Frontend
```

---

## 📁 Project Structure

```
careerbridge/
├── backend/
│   ├── main.py            # FastAPI app entry point
│   ├── database.py        # Async SQLAlchemy engine + session
│   ├── models.py          # ORM models (Job, Source)
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── crud.py            # All database operations
│   ├── routers/
│   │   ├── jobs.py        # GET /jobs, GET /jobs/{id}, POST /jobs/refresh
│   │   ├── search.py      # GET /search?q=...
│   │   └── sources.py     # GET /sources
│   └── Dockerfile
│
├── scraper/
│   ├── rss_fetcher.py     # feedparser-based async RSS fetcher
│   ├── web_scraper.py     # Playwright + BeautifulSoup scrapers
│   ├── normalizer.py      # Field normalisation + SHA-256 dedup
│   ├── scheduler.py       # APScheduler pipeline orchestrator
│   └── Dockerfile
│
├── frontend/              # React + Vite application
│   ├── src/
│   │   ├── App.jsx        # Main component (search, filter, cards, modal)
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml     # Full stack: DB + Redis + API + Scraper + Frontend
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🚀 Quick Start (Docker — Recommended)

### Prerequisites
- Docker Desktop installed and running
- Git

### 1. Clone and start

```bash
git clone https://github.com/youruser/careerbridge.git
cd careerbridge
docker-compose up --build
```

This starts:
| Service   | URL                            |
|-----------|--------------------------------|
| Frontend  | http://localhost:5173          |
| API       | http://localhost:8000          |
| API Docs  | http://localhost:8000/docs     |
| PostgreSQL| localhost:5432                 |
| Redis     | localhost:6379                 |

The scraper will run immediately on startup, then every 30 minutes automatically.

---

## 🛠️ Manual Setup (Without Docker)

### Backend

```bash
# 1. Create virtualenv
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Set environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/careerbridge"
export REDIS_URL="redis://localhost:6379/0"

# 5. Run DB migrations
cd backend
alembic upgrade head

# 6. Start API server
uvicorn main:app --reload --port 8000
```

### Scraper

```bash
cd scraper
python scheduler.py   # runs immediately + every 30 min
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 API Reference

| Method | Endpoint                  | Description                         |
|--------|---------------------------|-------------------------------------|
| GET    | `/api/v1/jobs`            | List jobs (filter by type/location) |
| GET    | `/api/v1/jobs/{id}`       | Get single job with full details    |
| POST   | `/api/v1/jobs/refresh`    | Trigger manual scrape               |
| GET    | `/api/v1/search?q=python` | Full-text keyword search            |
| GET    | `/api/v1/sources`         | List all active scrape sources      |
| GET    | `/health`                 | Health check                        |

### Query parameters for `/api/v1/jobs`

| Param       | Type   | Example          |
|-------------|--------|------------------|
| `job_type`  | string | `Govt`, `Private`, `PSU` |
| `location`  | string | `Bangalore`      |
| `experience`| string | `Fresher`        |
| `page`      | int    | `1`              |
| `page_size` | int    | `20` (max 100)   |

---

## 🕷️ Scraper Architecture

### RSS Sources (feedparser)
- TimesJobs CS jobs feed
- Shine.com IT fresher feed
- Freshersworld CS feed
- GovtJobsAlert RSS

### Playwright Scrapers (JS-heavy sites)
- **Internshala** — Paginated React app, 3 pages
- **NIC Recruitment Portal** — Govt tables

### Anti-bot Mitigations
- Rotating User-Agent strings from a pool of 4
- `navigator.webdriver` property hidden
- Random delays between requests (1.5–4s)
- Max 2 concurrent browser contexts

### Deduplication
Jobs are fingerprinted using SHA-256:
```python
fingerprint = SHA256(title.lower() + "|" + company.lower() + "|" + location.lower())
```
Duplicates from different sources are automatically skipped.

---

## 🗄️ Database Schema

```sql
-- sources
id, name, url, feed_type (rss|scrape), is_active, last_fetched, created_at

-- jobs
id, title, company, location, job_type (Private|Govt|PSU),
experience, salary, description, apply_url, tags (text[]),
posted_at, scraped_at, is_active, fingerprint (SHA-256, UNIQUE),
source_id (FK), search_vector (TSVECTOR for FTS)

Indexes: job_type, location, posted_at, GIN(search_vector), fingerprint
```

---

## ⚙️ Environment Variables

| Variable       | Default                                         | Description             |
|----------------|-------------------------------------------------|-------------------------|
| `DATABASE_URL` | `postgresql+asyncpg://careerbridge:secret@localhost:5432/careerbridge` | Postgres connection |
| `REDIS_URL`    | `redis://localhost:6379/0`                      | Redis connection        |
| `VITE_API_URL` | `http://localhost:8000/api/v1`                  | Frontend API base URL   |

---

## 📦 Tech Stack

| Layer     | Technology                              |
|-----------|-----------------------------------------|
| Frontend  | React 18, Vite, CSS-in-JS               |
| Backend   | FastAPI, SQLAlchemy (async), Alembic    |
| Database  | PostgreSQL 16 (full-text search)        |
| Cache     | Redis 7                                 |
| Scraping  | feedparser, Playwright, BeautifulSoup4  |
| Scheduler | APScheduler 3.x                         |
| Deploy    | Docker Compose, Nginx (prod)            |

---

## 🚢 Production Deployment

1. Replace `docker-compose.yml` dev commands with production ones (no `--reload`)
2. Set strong passwords in environment variables or use Docker Secrets
3. Add an Nginx reverse proxy in front of API and Frontend
4. Enable SSL via Let's Encrypt / Certbot
5. Deploy to any VPS (DigitalOcean, AWS EC2, Hetzner) or use Railway/Render for managed hosting

---

## 🤝 Contributing

Pull requests welcome! To add a new scraper:
1. Add a new async function in `scraper/web_scraper.py`
2. Register it in `run_all_scrapers()`
3. Add the source to the `sources` table via Alembic migration

---

## 📄 License

MIT © 2025 CareerBridge
