# ResumeIQ

**AI-powered resume screening built entirely on free-tier tools.**

ResumeIQ lets you upload up to 5 PDF resumes alongside a job description and automatically ranks candidates by skill fit — no paid APIs, no cloud, no data leaving your machine (except the LLM call to OpenRouter).

---

## What It Does

1. **Parses** uploaded PDF resumes with PyMuPDF
2. **Extracts skills** from both the job description and each resume using Llama 3.3-70B (via OpenRouter free tier)
3. **Falls back** to a curated 600+ skill YAML taxonomy (semantic search with FAISS) if the LLM returns nothing
4. **Embeds** all skill sets locally using `all-MiniLM-L6-v2` (no external calls)
5. **Ranks** candidates by cosine similarity between their embedded skills and the job description's skill embedding
6. **Displays** results in a Streamlit dashboard — score ranking chart, candidate cards with matched/missing skills, skill matrix table, and CSV export

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit + custom HTML/CSS components |
| **Backend API** | FastAPI + Uvicorn |
| **LLM orchestration** | LangGraph (3-node pipeline: extract → embed → rank) |
| **LLM** | Llama 3.3-70B Instruct via [OpenRouter](https://openrouter.ai) (free tier) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (local, offline) |
| **Vector search** | FAISS (CPU) |
| **PDF parsing** | PyMuPDF (`fitz`) |
| **Observability** | LangSmith (optional tracing) + structlog |
| **Config** | Pydantic Settings + `python-dotenv` |

---

## Installation

### Prerequisites

- Python 3.10+
- A free [OpenRouter account](https://openrouter.ai) — get your API key at `openrouter.ai/keys`

### Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd resume-screening

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and fill in your keys (see Environment Variables below)
```

---

## Environment Variables

Copy `.env.example` to `.env` and set the following:

```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free

# Local embedding model (no key needed — downloads automatically on first run)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Optional — LangSmith tracing (leave blank to disable)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=resume-screener

# Logging level
LOG_LEVEL=INFO
```

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | ✅ Yes | Free key from openrouter.ai/keys |
| `OPENROUTER_BASE_URL` | ✅ Yes | Keep as default |
| `LLM_MODEL` | ✅ Yes | Free model — do not change unless upgrading |
| `EMBEDDING_MODEL` | ✅ Yes | Downloaded locally on first run (~90 MB) |
| `LANGCHAIN_API_KEY` | ❌ Optional | Enables LangSmith trace dashboard |
| `LANGCHAIN_PROJECT` | ❌ Optional | LangSmith project name |
| `LOG_LEVEL` | ❌ Optional | `DEBUG`, `INFO`, `WARNING` |

---

## How to Run

ResumeIQ runs as **two separate processes** — the FastAPI backend and the Streamlit frontend. Open two terminal windows in the project root.

### Terminal 1 — Start the Backend API

```bash
python -m api.main
```

The API starts at `http://localhost:8000`.
You can verify it's running by visiting `http://localhost:8000/docs`.

### Terminal 2 — Start the Frontend

```bash
streamlit run ui/app.py
```

The app opens at `http://localhost:8501`.

> **Note:** Both processes must be running at the same time. The frontend calls the backend at `http://localhost:8000/api/v1/screen`.

---

## How to Use

1. **Open** `http://localhost:8501` in your browser
2. **Paste** a job description into the left sidebar text area — include required skills, nice-to-haves, and context for best results
3. **Upload** 1–5 PDF resumes using the file uploader (drag-and-drop or click)
4. **Click** "Screen Candidates" — the sidebar shows an animated pulse while processing
5. **Review** results across three tabs:
   - **Overview** — Score ranking bar chart + heatmap of common missing skills
   - **Candidate cards** — Per-candidate score badge, verdict, skill fit bar, matched/missing skill pills
   - **Skill matrix** — Table of all JD skills vs. all candidates with Yes/No coverage and % footer
6. **Export** results via "Download results as CSV" in the Skill matrix tab

---

## Project Structure

```
resume-screening/
│
├── api/                        # FastAPI backend
│   ├── main.py                 # Uvicorn server entry point
│   ├── router.py               # POST /api/v1/screen endpoint
│   └── schemas.py              # Pydantic request/response models
│
├── agents/                     # LangGraph pipeline
│   ├── graph.py                # Compiled graph definition
│   ├── nodes.py                # Node functions: extract_skills, embed, rank
│   └── state.py                # ScreenerState TypedDict
│
├── core/                       # Shared processing logic
│   ├── pdf_parser.py           # PyMuPDF text extraction
│   ├── skill_extractor.py      # LLM skill extraction via OpenRouter
│   └── embedder.py             # Local sentence-transformer embedding + FAISS
│
├── skills/
│   └── global_skills.yaml      # 600+ skill taxonomy fallback (grouped by role)
│
├── ui/                         # Streamlit frontend
│   ├── app.py                  # Main app — sidebar, API call, results routing
│   ├── theme.py                # CSS injection (apply_theme function)
│   ├── html_components.py      # HTML builders: cards, charts, matrix, metrics
│   └── components.py           # Legacy Plotly chart helpers
│
├── observability/
│   ├── logger.py               # structlog configuration
│   └── langsmith_setup.py      # LangSmith tracing setup
│
├── .streamlit/
│   └── config.toml             # Streamlit theme (light mode, Inter font, accent color)
│
├── config.py                   # Pydantic Settings — loads all env vars
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
└── README.md
```

---

## Known Limitations

### OpenRouter Free Tier Rate Limits

The free `meta-llama/llama-3.3-70b-instruct:free` model has strict rate limits:

| Limit | Value |
|---|---|
| Requests per minute | ~20 RPM |
| Requests per day | ~200 RPD |
| Context window | 128K tokens |

**Impact on this app:**
- Each screening job makes **N + 1 LLM calls** (1 for the JD + 1 per resume)
- Processing 5 resumes = 6 LLM calls in sequence
- If you hit a 429 rate-limit error, the app automatically waits 60 seconds and retries once
- If the retry also fails, skill extraction returns an empty list and FAISS similarity scoring will reflect missing skills

**Workarounds:**
- Spread large batches across multiple runs with a few minutes between them
- Upgrade to a paid OpenRouter model by changing `LLM_MODEL` in `.env`
- The FAISS semantic fallback against `skills/global_skills.yaml` activates automatically if the LLM returns no skills

### Other Limitations

- **Max 5 resumes per run** — enforced at both the API and UI layer
- **PDF only** — scanned image PDFs without embedded text will extract as empty and return a zero score
- **Candidate name = filename** — names are derived from the PDF filename, not parsed from content
- **Embedding model download** — `all-MiniLM-L6-v2` (~90 MB) downloads on first run; requires internet once
- **No persistence** — results are stored in Streamlit session state only; refreshing the page clears them
- **Single-user** — no auth, no multi-tenancy; designed for local personal use

---

## API Reference

### `POST /api/v1/screen`

Screens a batch of resumes against a job description.

**Request** (`multipart/form-data`):

| Field | Type | Description |
|---|---|---|
| `jd_text` | `string` (form) | Full job description text |
| `resumes` | `file[]` (PDF) | 1–5 PDF files |

**Response** (`application/json`):

```json
{
  "results": [
    {
      "candidate_name": "john_doe.pdf",
      "score": 0.847,
      "matched_skills": ["Python", "Docker", "FastAPI"],
      "missing_skills": ["Kubernetes", "Terraform"],
      "rank": 1
    }
  ],
  "jd_skills": ["Python", "Docker", "FastAPI", "Kubernetes", "Terraform"],
  "total_candidates": 1,
  "processing_time_seconds": 12.4
}
```

Interactive docs available at `http://localhost:8000/docs` when the backend is running.
