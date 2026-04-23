# ResumeIQ — Architecture & Code Reference

A file-by-file explanation of every folder and module in the project.

---

## How the System Fits Together

```
Browser (Streamlit UI)
        │
        │  HTTP POST /api/v1/screen
        ▼
FastAPI Backend  ──►  LangGraph Pipeline
   api/              agents/
   ├── main.py        ├── graph.py      (wires the 3 nodes)
   ├── router.py      ├── nodes.py      (extract → embed → rank)
   └── schemas.py     └── state.py      (shared data bag)
        │
        ├── core/pdf_parser.py          (PDF → text)
        ├── core/skill_extractor.py     (text → skills via LLM)
        └── core/embedder.py            (skills → vectors via FAISS)
                                             ▲
                                    sentence-transformers
                                    (all-MiniLM-L6-v2, local)
```

Data flows in one direction: `PDF bytes → raw text → skills list → embedding vector → cosine score → ranked result → JSON response → UI`.

---

## Root-Level Files

### `config.py`
Central configuration loader. Uses **Pydantic Settings** to read all environment variables from `.env` and expose them as a typed `settings` singleton used throughout the app.

```python
from config import settings
settings.OPENROUTER_API_KEY   # type: str
settings.LLM_MODEL            # type: str
settings.EMBEDDING_MODEL      # type: str
```

Any module that needs a config value imports `settings` from here — nothing reads `os.environ` directly.

---

### `requirements.txt`
All Python dependencies. Install with `pip install -r requirements.txt`.

| Package | Purpose |
|---|---|
| `fastapi` + `uvicorn` | Backend HTTP server |
| `streamlit` | Frontend UI framework |
| `langchain` + `langgraph` + `langsmith` | LLM orchestration + tracing |
| `langchain-openai` | OpenAI-compatible client (used for OpenRouter) |
| `faiss-cpu` | Vector similarity search |
| `sentence-transformers` | Local embedding model |
| `pymupdf` | PDF text extraction (`fitz`) |
| `httpx` | Async HTTP client used by the Streamlit frontend to call the backend |
| `pydantic-settings` | Typed env var loading |
| `python-multipart` | Enables FastAPI to receive file uploads |
| `structlog` | Structured JSON/console logging |
| `pyyaml` | Loads the `skills/global_skills.yaml` taxonomy |

---

### `.env` / `.env.example`
`.env` holds all secrets and is **never committed** (listed in `.gitignore`).  
`.env.example` is the committed template showing every required variable without real values.

---

### `.gitignore`
Excludes `venv/`, `__pycache__/`, `.pyc` files, `.env`, model weight files (`*.bin`, `*.safetensors`), FAISS indexes, uploaded PDFs, and IDE folders from version control.

---

### `README.md`
User-facing documentation: what the app does, installation steps, how to run both processes, how to use the UI, the full API reference, and known limitations.

---

### `ARCHITECTURE.md` *(this file)*
Developer-facing documentation: explains every folder and file in detail.

---

## `api/` — FastAPI Backend

The HTTP layer. Receives requests from the Streamlit frontend, validates inputs, drives the LangGraph pipeline, and returns structured JSON.

### `api/main.py`
**Entry point** for the backend server.

- Creates the `FastAPI` application instance
- Registers CORS middleware (wide open for local dev — lock down in production)
- Mounts the business-logic router at `/api/v1`
- Exposes `GET /health` → `{"status": "ok"}` for liveness checks
- When run as `python -m api.main`, starts Uvicorn with `reload=True` (hot-reloads on file changes)

### `api/router.py`
**The only real endpoint**: `POST /api/v1/screen`

What it does step by step:
1. Validates 1–5 uploaded files are PDFs
2. Calls `pdf_parser.extract_text_from_pdf()` on each file → dict of `{filename: text}`
3. Passes texts + JD to `agents.graph.run_screening()` (the LangGraph pipeline)
4. Assembles the ranked results into a `ScreeningResponse` and returns it

Handles errors explicitly: HTTP 400 for bad inputs, 422 for pipeline errors, 500 for unexpected crashes.

### `api/schemas.py`
**Pydantic models** for request validation and response serialization.

| Model | Fields |
|---|---|
| `RankingResult` | `candidate_name`, `score` (0–1), `matched_skills`, `missing_skills`, `rank` |
| `ScreeningResponse` | `results: list[RankingResult]`, `jd_skills`, `total_candidates`, `processing_time_seconds` |
| `ErrorResponse` | `detail: str` |

---

## `agents/` — LangGraph Pipeline

The AI orchestration layer. A three-node directed acyclic graph built with **LangGraph**. Each node is a pure function that receives the state dict and returns a partial update.

### `agents/state.py`
**Defines `ScreenerState`** — the shared data bag that flows through every node.

```
resume_texts       {filename: raw_text}          Input: PDF text per candidate
jd_text            str                            Input: job description text
extracted_skills   {filename: [skill, ...]}       After node_extract_skills
jd_skills          [skill, ...]                   After node_extract_skills
embeddings         {filename: [float, ...]}        After node_embed (384-dim vectors)
jd_embedding       [float, ...]                   After node_embed
scores             {filename: float}              After node_rank (cosine similarity)
missing_skills     {filename: [skill, ...]}        After node_rank
error              str | None                     Set by any node on failure
```

`default_state()` returns a fresh zeroed-out state dict before each pipeline run.

### `agents/graph.py`
**Wires the pipeline together** and exposes `run_screening()`.

Graph topology:
```
extract_skills  ──►  embed  ──►  rank
```

`run_screening(resume_texts, jd_text)`:
1. Initialises a fresh `default_state()`
2. Injects the inputs
3. Calls `app.invoke(state)` — LangGraph runs all three nodes in sequence
4. Returns the final populated state (LangSmith auto-traces this if `LANGCHAIN_API_KEY` is set)

### `agents/nodes.py`
**The three node functions** — all stateless, all return partial state updates.

#### `node_extract_skills(state)`
- Calls `core.skill_extractor.extract_skills()` on the JD text → `jd_skills`
- If the LLM returns zero JD skills, falls back: embeds the JD text, searches `skills/global_skills.yaml` by role similarity, and substitutes the best-matched role's skill list
- Concurrently calls `extract_skills()` on all resumes using a `ThreadPoolExecutor` (max 5 workers)
- Returns `{extracted_skills, jd_skills}`

#### `node_embed(state)`
- Joins each candidate's skill list into a comma-separated string and embeds it locally
- Embeds the JD skill list similarly
- Inserts a 2-second sleep between JD and resume embeddings to avoid any rate-limit bursts
- Returns `{embeddings, jd_embedding}`

#### `node_rank(state)`
- Builds a FAISS index from all resume embedding vectors
- Searches it with the JD embedding → cosine similarity scores
- Computes `missing_skills` as `set(jd_skills) − set(resume_skills)` for each candidate
- Returns `{scores, missing_skills}`

---

## `core/` — Shared Processing Logic

Stateless utility modules. No HTTP, no LangGraph — just pure functions used by the agent nodes.

### `core/pdf_parser.py`
**PDF → clean text string** using PyMuPDF (`fitz`).

- Opens the PDF from raw bytes (no temp files written to disk)
- Iterates every page calling `page.get_text()`
- Strips excessive whitespace by splitting and re-joining on spaces
- Raises `ValueError` if the result is under 50 characters (catches scanned/image-only PDFs early)
- Includes a self-test block runnable with `python core/pdf_parser.py`

### `core/skill_extractor.py`
**Text → skill list** via the OpenRouter LLM API.

- Sends a zero-temperature chat completion request to `settings.LLM_MODEL`
- System prompt instructs the model to return **only** a JSON array of strings (no markdown, no explanation)
- Handles `HTTP 429` rate-limit errors by sleeping 60 seconds and retrying once
- Strips markdown fences (` ```json `) from the response before JSON parsing
- Returns `[]` on any error — never crashes the pipeline
- Includes a standalone test block runnable with `python core/skill_extractor.py`

### `core/embedder.py`
**Skills → 384-dimension vectors** using a local sentence-transformer, plus FAISS index operations.

Loads `all-MiniLM-L6-v2` once at module import time (downloads ~90 MB to `~/.cache` on first run, subsequent loads are instant).

| Function | What it does |
|---|---|
| `embed_texts(texts)` | Encodes a list of strings into L2-normalised 384-dim vectors. Returns `list[list[float]]` |
| `build_faiss_index(embeddings)` | Builds an `IndexFlatIP` (inner product = cosine similarity on normalised vectors). Dimension fixed at 384 |
| `search_index(index, query, k)` | Reshapes query to `(1, 384)`, searches index, returns `list[(idx, score)]` sorted descending |

---

## `skills/`

### `skills/global_skills.yaml`
A curated taxonomy of 600+ technical skills grouped by job role (e.g. `backend_engineer`, `data_scientist`, `devops_engineer`, etc.).

**Used only as a fallback** in `node_extract_skills()`: if the LLM returns zero skills for a JD (e.g. on rate-limit failure or vague text), the system embeds the JD and finds the closest role in this file semantically, then borrows that role's skill list.

Structure:
```yaml
job_roles:
  backend_engineer:
    skills: [Python, FastAPI, PostgreSQL, Docker, ...]
  data_scientist:
    skills: [Python, PyTorch, scikit-learn, SQL, ...]
```

---

## `ui/` — Streamlit Frontend

The browser-facing application. Runs as a separate process from the backend and communicates via HTTP.

### `ui/app.py`
**Main application file** — the only Streamlit entrypoint.

Sections (top to bottom):

| Section | What it does |
|---|---|
| Session state init | Sets defaults for `results`, `jd_skills`, `screening`, `proc_time` |
| Theme | Calls `apply_theme(dark=False)` to inject all CSS |
| Sidebar (`with st.sidebar:`) | Logo, JD text area, file uploader, file count badge, spinner, screen button |
| Button click handler | Sets `session_state["screening"] = True` and calls `st.rerun()` to show the spinner |
| API call block | When `screening=True`, POSTs to `/api/v1/screen`, stores results, clears flag, reruns |
| Results display | Renders metrics, tabs (Overview / Candidate cards / Skill matrix), and CSV download |
| Empty state | Shows a centred SVG illustration when no results exist yet |

### `ui/theme.py`
**CSS injection module.** Contains a single `apply_theme(dark: bool)` function that calls `st.markdown()` with a `<style>` block.

Covers:
- CSS custom properties (design tokens: `--bg`, `--text`, `--accent`, etc.) for light + dark modes
- Sidebar layout, typography, textarea, divider styling
- File uploader dropzone (hides Streamlit's default instructions, styles the drag-and-drop zone)
- Primary and secondary button styles
- Metric cards, tabs, expanders, alerts, scrollbar, spinner

### `ui/html_components.py`
**Pure HTML string builders** — returns raw HTML strings rendered via `st.html()`.

| Function | Output |
|---|---|
| `get_colors(dark)` | Returns a dict of hex color values for the current theme |
| `score_color(score, c)` | Maps score to `(text_color, bg_color)` tuple — green ≥0.7, amber ≥0.4, red <0.4 |
| `verdict_label(score)` | Returns `"Shortlist"`, `"Maybe"`, or `"Reject"` |
| `build_metrics_html(results, jd_skills, dark)` | 4-column KPI bar: Top Score, Avg Score, Shortlisted count, JD Skills found |
| `build_candidate_card_html(result, rank, jd_skills, dark)` | Full candidate card with avatar initials, score badge, skill fit progress bar, matched/missing skill pills, and stat grid |
| `build_ranking_chart_html(results, dark)` | Horizontal bar chart of all candidates ranked by score, with a 70% threshold dashed line and colour-coded bars |
| `build_skill_matrix_html(results, jd_skills, dark)` | HTML table: rows = JD skills, columns = candidates, cells = Yes/No pill, footer = coverage % |

### `ui/components.py`
Legacy Plotly-based chart helpers from an earlier version of the UI. Kept for reference but not actively used by `app.py` — `html_components.py` replaced these with pure HTML/CSS equivalents.

---

## `observability/` — Logging & Tracing

### `observability/logger.py`
**Structured logging** via `structlog`.

- Configures `structlog` once on module import
- In `DEBUG` mode: pretty console output with colours
- In any other mode: JSON-formatted lines (suitable for log aggregators)
- `get_logger(name)` returns a bound logger pre-tagged with `service="resume-screener"`
- `log_screening_run(...)` emits a structured event with `n_resumes`, `processing_time`, `top_score`

### `observability/langsmith_setup.py`
**LangSmith tracing** (optional).

- `configure_langsmith()` sets the `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, and `LANGCHAIN_PROJECT` env vars at runtime if a key is present — this is all LangGraph needs to start sending traces
- `create_eval_dataset_entry(...)` creates structured JSONL-compatible entries that can be manually uploaded to LangSmith as evaluation datasets for future automated eval runs

---

## `.streamlit/`

### `.streamlit/config.toml`
Streamlit's built-in theming config. Sets the app to **light mode** with the accent colour, background colours, and font family to match the custom CSS.

```toml
[theme]
base                  = "light"
primaryColor          = "#534AB7"
backgroundColor       = "#ffffff"
secondaryBackgroundColor = "#f8f8f6"
textColor             = "#111110"
font                  = "sans serif"
```

This eliminates Streamlit's native dark/light toggle flash and ensures the base theme is consistent before the custom CSS injection runs.

---

## Data Flow Summary

```
User uploads PDF(s) + pastes JD
           │
           ▼
  ui/app.py  ──POST──►  api/router.py
                              │
                    core/pdf_parser.py
                    (bytes → clean text)
                              │
                    agents/graph.py
                    run_screening()
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         node_extract     node_embed      node_rank
         _skills()         ()              ()
              │               │               │
    skill_extractor.py  embedder.py     embedder.py
    (LLM via OpenRouter) (MiniLM local)  (FAISS search)
              │               │               │
              └───────────────┴───────────────┘
                              │
                   ScreeningResponse (JSON)
                              │
                   ui/app.py receives it
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      html_components  html_components  html_components
      build_metrics    build_ranking    build_skill
      _html()          _chart_html()    _matrix_html()
```
