from typing import TypedDict

class ScreenerState(TypedDict):
    resume_texts: dict[str, str]
    jd_text: str
    extracted_skills: dict[str, list[str]]
    jd_skills: list[str]
    embeddings: dict[str, list[float]]
    jd_embedding: list[float]
    scores: dict[str, float]
    missing_skills: dict[str, list[str]]
    error: str | None

def default_state() -> ScreenerState:
    """Returns a fresh default initialized state dictionary."""
    return {
        "resume_texts": {},
        "jd_text": "",
        "extracted_skills": {},
        "jd_skills": [],
        "embeddings": {},
        "jd_embedding": [],
        "scores": {},
        "missing_skills": {},
        "error": None
    }

# Defines the `ScreenerState` TypedDict used as the shared state schema across all LangGraph nodes, and provides a `default_state()` factory to initialize it with empty defaults.
