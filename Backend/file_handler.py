import csv
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "candidates.csv"
UPLOAD_DIR = BASE_DIR / "uploads"
CSV_FIELDS = [
    "fullname",
    "email",
    "mobile",
    "position",
    "qualification",
    "experience", 
    "yearOfPassing",
    "percentage",
    "college",
    "primarySkills",
    "secondarySkills",
    "languagesKnown",
    "resume",
    "applied_date",
]


def save_resume_file(resume_file: UploadFile) -> str:
    
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    original_name = resume_file.filename or "resume.pdf"
    safe_name = "".join(ch for ch in original_name if ch.isalnum() or ch in ("-", "_", "."))
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_name = f"{timestamp}_{safe_name}"
    file_path = UPLOAD_DIR / saved_name

    with file_path.open("wb") as target_file:
        shutil.copyfileobj(resume_file.file, target_file)

    return saved_name


