import json
import os
from typing import List, Set, Tuple
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import re
from dotenv import load_dotenv

load_dotenv()

# Load local model and tokenizer with cache_dir
model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./models", local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir="./models", local_files_only=True)
text_generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

def extract_skills(text: str) -> List[str]:
    """Extract skills using local flan-t5-small model with simpler prompt."""
    prompt = f"Identify skills from this job description: {text[:1000]}. Return a comma-separated list of up to 10 skills (e.g., python, django, aws)."
    try:
        response = text_generator(prompt, max_new_tokens=100, num_return_sequences=1)
        generated_text = response[0]['generated_text'].strip() if response else ""
    except Exception as e:
        print(f"Local model error: {e}. Using mock fallback.")
        generated_text = ""
    
    # Clean and process
    skills_str = re.sub(r'[^\w\s,]', '', generated_text).strip()
    skills = [s.strip().lower() for s in skills_str.split(',') if s.strip() and len(s) <= 20]
    if not skills or any(len(s) > 20 for s in skills):  # Detect garbage or empty
        print("No valid skills extracted. Using mock skills.")
        skills = ["python", "sql", "leadership", "communication", "management", "javascript", "aws", "react", "data analysis", "project management"][:5]
    return list(set(skills))[:10]  # Unique, limit to 10

def compute_match(cand_skills: Set[str], job_skills: Set[str]) -> Tuple[float, List[str], List[str], str]:
    """Compute match score and details using Jaccard + simple explanation."""
    if not job_skills:
        return 0.0, [], [], "No job skills defined."
    
    intersect = cand_skills & job_skills
    overlap = len(intersect) / len(job_skills)
    score = min(overlap * 100, 100)
    
    matching = sorted(list(intersect))[:3]
    missing = sorted(list(job_skills - cand_skills))[:3]
    
    explanation = f"Matches on {len(matching)} skills (e.g., {', '.join(matching[:2])}). Consider adding {', '.join(missing)}."
    return score, matching, missing, explanation

def get_db_session():
    from models import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()