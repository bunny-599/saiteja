# Sky-Scrapper: AI-Powered Competitor Intelligence Platform

Sky-Scrapper is a production-ready competitor intelligence system that scans the public web in real-time. It executes multi-vector scraping pipelines (crawling homepages, Trustpilot reviews, Meta Ads Library, Google News, and financial indices), compiles the data, feeds it to Claude 3.5 Sonnet, and generates interactive SWOT grids, sentiment donut charts, and downloadable ReportLab PDF summaries.

---

## 🏗️ ARCHITECTURE FLOW

```ascii
                     +---------------------------------------+
                     |         React Dashboard (Vite)        |
                     +-------------------+-------------------+
                                         | (REST API / Polling)
                                         v
                     +-------------------+-------------------+
                     |       FastAPI Application Engine      |
                     +-------------------+-------------------+
                                         |
                       +-----------------+-----------------+
                       | (Background Tasks Orchestration)  |
                       v                                   v
             +---------+----------+              +---------+----------+
             |  SQLite cache / DB |              | Real-time Scrapers |
             +--------------------+              +---------+----------+
                                                           |
  +------------------+-----------------+-------------------+------------------+------------------+
  |                  |                 |                   |                  |                  |
  v                  v                 v                   v                  v                  v
[Website]       [Trustpilot]      [Meta Ads]         [Google News]         [Growjo]           [Socials]
Crawls taglines  Scrapes reviews  Extracts active    Aggregates Google     Pulls revenues,    Pulls LinkedIn,
& tech stacks.   via ScraperAPI.  ad copy/CTAs.      News & TechCrunch.    funding & staff.   Twitter, Insta.
  |                  |                 |                   |                  |                  |
  +------------------+-----------------+-------------------+------------------+------------------+
                                         |
                                         v (Clean Plain Text)
                     +-------------------+-------------------+
                     |       Claude Sonnet (Anthropic API)   |
                     | - Competitor Profiles  - SWOT Matrix  |
                     | - Sentiment Analysis   - Opportunities |
                     +-------------------+-------------------+
                                         |
                                         v
                     +-------------------+-------------------+
                     |       ReportLab PDF / JSON Package    |
                     +---------------------------------------+
```

---

## 🛠️ TECH STACK

- **Backend**: Python 3.11+, FastAPI, Playwright (Stealth), BeautifulSoup4, HTTPX, SQLAlchemy (Async)
- **Database**: SQLite via `aiosqlite`
- **AI Integration**: Anthropic Python SDK (`claude-3-5-sonnet-20241022`)
- **PDF Core**: ReportLab PDF document builder
- **Frontend**: React (Vite), TailwindCSS, Recharts, TanStack React Query

---

## 🚀 GETTING STARTED

### 1. Prerequisites
- Python 3.11 or higher installed.
- Node.js v18+ and npm installed.

### 2. Installation
Clone the workspace and run the build:
```bash
# Install Python packages and Node packages
make install

# Install Playwright Chromium headless binaries
make playwright
```

### 3. Environment Setup
Create a `.env` file in the root directory (based on `.env.example`):
```ini
ANTHROPIC_API_KEY=your-anthropic-api-key
SERPER_API_KEY=your-serper-api-key
SCRAPERAPI_KEY=your-scraper-api-key
```

### 4. Running the Platform
Launch the FastAPI server (port 8000) and the React development server (port 5173) concurrently:
```bash
make dev
```
Open `http://localhost:5173` in your browser.

---

## 📡 API REFERENCE

### 1. Submit a Research Job
Submit a request to queue a target company analysis:
```bash
curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"company_name": "OpenAI", "industry": "Artificial Intelligence", "depth": "standard"}'
```
**Response:**
```json
{"job_id": "8a09f8d9-29ef-4bfd-a19c-3665a120bd70", "status": "pending"}
```

### 2. Poll Status & Logs
Fetch the live progress state and running console text logs of the job:
```bash
curl -X GET "http://localhost:8000/api/status/8a09f8d9-29ef-4bfd-a19c-3665a120bd70"
```
**Response:**
```json
{
  "job_id": "8a09f8d9-29ef-4bfd-a19c-3665a120bd70",
  "company_name": "OpenAI",
  "industry": "Artificial Intelligence",
  "status": "scraping",
  "progress": 40,
  "logs": [
    {"time": "2026-05-19 22:30:15", "message": "Initializing analysis job..."},
    {"time": "2026-05-19 22:30:17", "message": "Discovering competitors for 'OpenAI' in 'Artificial Intelligence'..."},
    {"time": "2026-05-19 22:30:20", "message": "✓ Discovered 5 competitors: Anthropic, Cohere, AI21 Labs..."},
    {"time": "2026-05-19 22:30:21", "message": "Starting scraping pipeline for Target..."}
  ],
  "error_log": "",
  "created_at": "2026-05-19T22:30:15"
}
```

### 3. Fetch Finished Report JSON
Retrieve the compiled competitor data and Claude analysis matrices:
```bash
curl -X GET "http://localhost:8000/api/report/8a09f8d9-29ef-4bfd-a19c-3665a120bd70"
```

### 4. Export Report Lab PDF
Download the professionally compiled multi-page PDF summary:
```bash
curl -X GET "http://localhost:8000/api/export/pdf/8a09f8d9-29ef-4bfd-a19c-3665a120bd70" --output report.pdf
```
