from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from models import Base, Job, Candidate, Match, engine, SessionLocal
from utils import extract_skills, compute_match, get_db_session
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Load .env file
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
Base.metadata.create_all(bind=engine)

@app.get("/jobs")
def get_jobs(q: str = None, location: str = None, company: str = None, db: Session = Depends(get_db_session)):
    query = db.query(Job)
    if q:
        query = query.filter(Job.title.ilike(f"%{q}%"))
    if location:
        query = query.filter(Job.location == location)
    if company:
        query = query.filter(Job.company == company)
    jobs = query.all()
    return {"jobs": [{"id": j.id, "title": j.title, "description": j.description[:200], "location": j.location, "company": j.company, "skills": json.loads(j.skills_json) if j.skills_json else []} for j in jobs]}

@app.post("/candidates/upload")
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db_session)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    try:
        contents = file.file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        skills = extract_skills(text)
        candidate = Candidate(resume_text=text, skills_json=json.dumps(skills))
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return {"candidate_id": candidate.id, "resume_text": text[:500] + "..." if len(text) > 500 else text, "skills": skills}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/matches/generate")
def generate_matches(candidate_id: int, db: Session = Depends(get_db_session)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    cand_skills = json.loads(candidate.skills_json)
    jobs = db.query(Job).all()
    matches = []
    for job in jobs:
        job_skills = json.loads(job.skills_json)
        score, matching_skills, missing_skills, explanation = compute_match(set(cand_skills), set(job_skills))
        match = Match(
            candidate_id=candidate_id,
            job_id=job.id,
            score=score,
            matching_skills_json=json.dumps(matching_skills),
            missing_skills_json=json.dumps(missing_skills),
            explanation=explanation
        )
        db.add(match)
        db.commit()
        matches.append({
            "job": {"id": job.id, "title": job.title, "location": job.location, "company": job.company},
            "score": score,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "explanation": explanation
        })
    return {"matches": matches}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)