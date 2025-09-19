import json
from sqlalchemy.orm import Session
from models import Base, Job, engine, SessionLocal
from utils import extract_skills

def seed_real_jobs():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing jobs
        db.query(Job).delete()
        db.commit()
        
        real_jobs = [
            {
                "title": "Senior Python Developer",
                "description": "We are seeking a Senior Python Developer to design and implement robust backend systems. Responsibilities include writing clean code, optimizing APIs, and collaborating with front-end teams. Experience with Django, RESTful services, and cloud platforms like AWS is required.",
                "location": "Bangalore, India",
                "company": "InnovateTech"
            },
            {
                "title": "Data Analyst",
                "description": "Join our team as a Data Analyst to analyze large datasets and provide actionable insights. Requires proficiency in SQL, Excel, and data visualization tools like Tableau. Strong problem-solving and communication skills are essential.",
                "location": "Mumbai, India",
                "company": "DataVision"
            },
            {
                "title": "Project Manager",
                "description": "Lead complex projects from initiation to completion. Responsibilities include team coordination, risk management, and stakeholder communication. PMP certification and experience with Agile methodologies are preferred.",
                "location": "Delhi, India",
                "company": "BuildMasters"
            },
            {
                "title": "Frontend Developer",
                "description": "Create responsive and engaging user interfaces using React and JavaScript. Collaborate with designers and backend developers to deliver high-quality web applications. Knowledge of CSS frameworks like Tailwind is a plus.",
                "location": "Hyderabad, India",
                "company": "WebCrafters"
            },
            {
                "title": "Machine Learning Engineer",
                "description": "Develop and deploy machine learning models to solve real-world problems. Requires expertise in Python, TensorFlow, and data preprocessing. Experience with NLP or computer vision is advantageous.",
                "location": "Chennai, India",
                "company": "AI Solutions"
            }
        ]
        
        seeded_count = 0
        for job_data in real_jobs:
            existing = db.query(Job).filter_by(title=job_data["title"]).first()
            if not existing:
                job = Job(
                    title=job_data["title"],
                    description=job_data["description"],
                    location=job_data["location"],
                    company=job_data["company"],
                    skills_json=json.dumps([])  # Initial empty
                )
                db.add(job)
                seeded_count += 1
        
        db.commit()
        print(f"Seeded {seeded_count} realistic jobs. Total in DB: {db.query(Job).count()}")
        
        sample = db.query(Job).first()
        if sample:
            print(f"Sample job: {sample.title} | Location: {sample.location} | Company: {sample.company}")
    
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_jobs()