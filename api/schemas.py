from pydantic import BaseModel, Field

class RankingResult(BaseModel):
    candidate_name: str
    score: float = Field(ge=0.0, le=1.0, description="Similarity score between 0 and 1")
    matched_skills: list[str]
    missing_skills: list[str]
    rank: int = Field(ge=1, description="Ranking position (1 is the best)")

class ScreeningResponse(BaseModel):
    results: list[RankingResult]
    jd_skills: list[str]
    total_candidates: int
    processing_time_seconds: float

class ErrorResponse(BaseModel):
    detail: str

# Defines Pydantic response models for the screening API: `RankingResult` for individual candidate scores and skills, `ScreeningResponse` for the full screening output, and `ErrorResponse` for error payloads.
