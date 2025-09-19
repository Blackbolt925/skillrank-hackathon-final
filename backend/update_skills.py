import json
from sqlalchemy.orm import Session
from models import Base, Job, engine, SessionLocal
from utils import extract_skills

def update_job_skills():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        jobs = db.query(Job).all()
        updated = 0
        for job in jobs:
            if job.skills_json == "[]":
                skills = extract_skills(job.description)
                job.skills_json = json.dumps(skills)
                updated += 1
                print(f"Updated job '{job.title[:50]}...': Skills = {skills}")
        
        db.commit()
        print(f"Updated {updated} jobs with skills.")
        
        sample = db.query(Job).first()
        if sample:
            print(f"Sample job after update: {sample.title[:50]}... | Skills: {sample.skills_json}")
    
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_job_skills()