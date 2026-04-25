import time
import logging

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from api.schemas import ScreeningResponse, RankingResult
from core.pdf_parser import extract_text_from_pdf
from agents.graph import run_screening

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/screen", response_model=ScreeningResponse)
async def screen_resumes(
    jd_text: str = Form(...),
    resumes: list[UploadFile] = File(...)
):
    start_time = time.perf_counter()
    logger.info(f"Starting screening process for {len(resumes)} resumes.")

    try:
        if not (1 <= len(resumes) <= 5):
            raise HTTPException(status_code=400, detail="Must provide between 1 and 5 resumes.")

        resume_texts = {}
        for resume in resumes:
            if resume.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail=f"File {resume.filename} is not a PDF.")
            
            file_bytes = await resume.read()
            try:
                text = extract_text_from_pdf(file_bytes)
                resume_texts[resume.filename] = text
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Error parsing PDF {resume.filename}: {e}")

        state = run_screening(resume_texts, jd_text)

        if state.get("error"):
            raise HTTPException(status_code=422, detail=state["error"])

        extracted_skills = state.get("extracted_skills", {})
        jd_skills = state.get("jd_skills", [])
        scores = state.get("scores", {})
        missing_skills_map = state.get("missing_skills", {})

        jd_skills_set = set(jd_skills)
        raw_results = []

        for candidate_filename in resume_texts.keys():
            score = scores.get(candidate_filename, 0.0)
            resume_skills = set(extracted_skills.get(candidate_filename, []))
            
            matched_skills = list(jd_skills_set & resume_skills)
            
            missing_skills = missing_skills_map.get(candidate_filename, list(jd_skills_set - resume_skills))

            raw_results.append({
                "candidate_name": candidate_filename,
                "score": score,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills
            })

        raw_results.sort(key=lambda x: x["score"], reverse=True)

        final_results = []
        for rank_idx, r in enumerate(raw_results, start=1):
            final_results.append(
                RankingResult(
                    candidate_name=r["candidate_name"],
                    score=r["score"],
                    matched_skills=r["matched_skills"],
                    missing_skills=r["missing_skills"],
                    rank=rank_idx
                )
            )

        processing_time = time.perf_counter() - start_time
        logger.info(f"Screening complete for {len(resumes)} resumes. Tracked latency: {processing_time:.2f} seconds.")

        return ScreeningResponse(
            results=final_results,
            jd_skills=jd_skills,
            total_candidates=len(final_results),
            processing_time_seconds=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating or processing route: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected internal server error processing the resumes.")

# Defines the POST /screen endpoint that accepts a job description and up to 5 PDF resumes, parses them, runs the LangGraph screening pipeline, and returns ranked candidates with matched/missing skills and processing time.
