import time
from typing import Any
import concurrent.futures
import yaml

from langchain_openai import ChatOpenAI

from config import settings
from core.skill_extractor import extract_skills
from core.embedder import embed_texts, build_faiss_index, search_index
from agents.state import ScreenerState


def node_extract_skills(state: ScreenerState) -> dict[str, Any]:
    try:
        if state.get("error"):
            return {}

        resume_texts = state.get("resume_texts", {})
        jd_text = state.get("jd_text", "")
        
        extracted_skills = {}
        jd_skills = []

        if jd_text:
            jd_skills = extract_skills(jd_text)
            
        if len(jd_skills) == 0:
            try:
                with open("skills/global_skills.yaml", "r", encoding="utf-8") as f:
                    taxonomy = yaml.safe_load(f)
                    
                roles = list(taxonomy.get("job_roles", {}).keys())
                if roles:
                    role_embeddings = embed_texts(roles)
                    jd_text_embedding = embed_texts([jd_text])[0]
                    
                    index = build_faiss_index(role_embeddings)
                    results = search_index(index, jd_text_embedding, k=1)
                    if results:
                        best_match_idx = results[0][0]
                        matched_role = roles[best_match_idx]
                        fallback_skills = taxonomy["job_roles"][matched_role]["skills"]
                        jd_skills.extend(fallback_skills)
                        jd_skills = list(set(jd_skills))
            except Exception as fe:
                print(f"Fallback taxonomy load failed: {fe}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_name = {executor.submit(extract_skills, text): name for name, text in resume_texts.items()}
            for future in concurrent.futures.as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    extracted_skills[name] = future.result()
                except Exception as exc:
                    print(f'{name} generated an exception: {exc}')
                    extracted_skills[name] = []

        return {
            "extracted_skills": extracted_skills,
            "jd_skills": jd_skills
        }
    except Exception as e:
        return {"error": f"Error in node_extract_skills: {e}"}

def node_embed(state: ScreenerState) -> dict[str, Any]:
    try:
        if state.get("error"):
            return {}

        extracted_skills = state.get("extracted_skills", {})
        jd_skills = state.get("jd_skills", [])
        
        embeddings = {}
        jd_embedding = []

        jd_skills_str = ", ".join(jd_skills)
        if jd_skills_str:
            jd_embedding_res = embed_texts([jd_skills_str])
            if jd_embedding_res:
                jd_embedding = jd_embedding_res[0]
                
        time.sleep(2)

        resume_names = list(extracted_skills.keys())
        if resume_names:
            resume_skill_strings = [", ".join(extracted_skills[name]) for name in resume_names]
            resume_embeddings = embed_texts(resume_skill_strings)
            
            for name, emb in zip(resume_names, resume_embeddings):
                embeddings[name] = emb

        return {
            "embeddings": embeddings,
            "jd_embedding": jd_embedding
        }
    except Exception as e:
        return {"error": f"Error in node_embed: {e}"}

def node_rank(state: ScreenerState) -> dict[str, Any]:
    try:
        if state.get("error"):
            return {}

        embeddings = state.get("embeddings", {})
        jd_embedding = state.get("jd_embedding", [])
        jd_skills = state.get("jd_skills", [])
        extracted_skills = state.get("extracted_skills", {})

        if not embeddings or not jd_embedding:
            return {"scores": {}, "missing_skills": {}}

        resume_names = list(embeddings.keys())
        resume_embs_list = [embeddings[name] for name in resume_names]

        index = build_faiss_index(resume_embs_list)
        k = len(resume_names)
        results = search_index(index, jd_embedding, k)

        scores = {}
        for idx, score in results:
            name = resume_names[idx]
            scores[name] = score

        missing_skills = {}
        jd_skills_set = set(jd_skills)
        for name in resume_names:
            resume_skills_set = set(extracted_skills.get(name, []))
            missing = jd_skills_set - resume_skills_set
            missing_skills[name] = list(missing)

        return {
            "scores": scores,
            "missing_skills": missing_skills
        }
    except Exception as e:
        return {"error": f"Error in node_rank: {e}"}

# Implements three LangGraph node functions: `node_extract_skills` extracts skills from JD and resumes (with taxonomy fallback), `node_embed` generates FAISS-compatible embeddings, and `node_rank` scores and ranks candidates by similarity while computing missing skills.
