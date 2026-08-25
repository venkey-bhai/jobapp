import io
import os
from typing import Optional
# from Backend.schemas import CandidateVoiceSchema
# import speech_recognition as sr

# import openai
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile
)

from database import get_db
from models import Candidate
# from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from file_handler import save_resume_file

# load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Code AI Careers"),
    version=os.getenv("APP_VERSION", "1.0.0"),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Job Application API is Running",
        "status": os.getenv("RECRUITMENT_STATUS", "active"),
    }


 


@app.post("/candidates")
def add_candidate(
    fullname: str = Form(...),
    gender: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    position: str = Form(""),
    qualification: str = Form(""),
    experience: str = Form(""),
    yearOfPassing: str = Form(""),
    percentage: str = Form(""),
    college: str = Form(""),
    primarySkills: str = Form(""),
    secondarySkills: str = Form(""),
    languagesKnown: str = Form(""),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not fullname.strip():
        raise HTTPException(
            status_code=400,
            detail="Full name is required."
        )
    if not gender.strip():
        raise HTTPException(
            status_code=400,
            detail="Gender is required."
        )

    if not email.strip():
        raise HTTPException(
            status_code=400,
            detail="Email is required."
        )

    if not mobile.strip():
        raise HTTPException(
            status_code=400,
            detail="Mobile number is required."
        )

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required."
        )

    allowed_extensions = {
        ".pdf",
        ".doc",
        ".docx"
    }

    file_extension = os.path.splitext(
        resume.filename
    )[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC, and DOCX files are allowed."
        )

    # Save uploaded file
    resume_name = save_resume_file(resume)

    # Save candidate information
    db_candidate = Candidate(
        fullname=fullname,
        gender=gender,
        email=email,
        mobile=mobile,
        position=position,
        qualification=qualification,
        experience=experience,
        yearOfPassing=yearOfPassing,
        percentage=percentage,
        college=college,
        primarySkills=primarySkills,
        secondarySkills=secondarySkills,
        languagesKnown=languagesKnown,
        resume=resume_name
    )

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    return {
        "success": True,
        "message": "Application submitted successfully.",
        "candidate": db_candidate
    }


@app.get("/candidates")
def get_candidates(db: Session = Depends(get_db)):
    return {
        "candidates": db.query(Candidate).all()
    }


@app.get("/candidates/search")
def search_candidates(
    name: str,
    db: Session = Depends(get_db)
):

    if not name or not name.strip():
        raise HTTPException(
            status_code=400,
            detail="Candidate name is required."
        )

    candidates = (
        db.query(Candidate)
        .filter(
            Candidate.fullname.ilike(
                f"%{name.strip()}%"
            )
        )
        .order_by(Candidate.id.asc())
        .all()
    )

    return {
        "candidates": candidates
    }





# @app.get("/candidates")
# def get_candidates(db: Session = Depends(get_db)):
#     return {"candidates": db.query(Candidate).all()}


# @app.get("/candidates/search")
# def search_candidates(name: str, db: Session = Depends(get_db)):
#     if not name or not name.strip():
#         raise HTTPException(status_code=400, detail="Candidate name is required.")

#     candidates = (
#         db.query(Candidate)
#         .filter(Candidate.fullname.ilike(f"%{name.strip()}%"))
#         .order_by(Candidate.id.asc())
#         .all()
#     )

#     return {"candidates": candidates}


@app.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully."}


@app.put("/candidates/{id}")
def update_candidate(
    id: int,
    status: str = Form(""), 
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    # Update candidate information
    
    candidate.status = status

    
        
    db.commit()
    db.refresh(candidate)   
    
    return {
        "success": True,
        "message": "Candidate updated successfully.",
        "candidate": candidate
    }   

